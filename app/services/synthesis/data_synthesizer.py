"""Data Synthesis Layer – actual implementation.

This module implements the missing `DataSynthesizer` required by the arbiter.
It reconciles market data from one or multiple providers, flags anomalies, and
produces a `SynthesizedEquitySnapshot` that includes a `data_confidence_score`
(0‑1) used by the decision brain.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.schemas import SynthesizedEquitySnapshot, MetaHeader
from app.core.config import settings
from app.services.market_data import get_quote, get_ist_now_str

logger = logging.getLogger(__name__)


class DataSynthesizer:
    """Reconciles raw provider responses into a unified snapshot."""

    def __init__(self, **_: Any) -> None:
        logger.debug("DataSynthesizer initialized with default parameters.")

    def _fetch_market_data(self, symbol: str, as_of: Optional[datetime] = None) -> Dict[str, Any]:
        """Fetch a market quote for *symbol* and return a minimal dict."""
        try:
            quote = get_quote(symbol, as_of=as_of)
            if isinstance(quote, dict):
                return {
                    "price": quote.get("price"),
                    "pe_ratio": quote.get("pe_ratio"),
                    "symbol": quote.get("symbol", symbol),
                    "is_mock": quote.get("is_mock", False),
                    "data_mode": quote.get("meta", {}).get("data_mode") if isinstance(quote.get("meta"), dict) else None,
                }
            return {
                "price": getattr(quote, "price", None),
                "pe_ratio": getattr(quote, "pe_ratio", None),
                "symbol": getattr(quote, "symbol", symbol),
                "is_mock": getattr(quote, "is_mock", False),
                "data_mode": getattr(getattr(quote, "meta", None), "data_mode", None),
            }
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to fetch market data for %s: %s", symbol, exc)
            return {}

    def synthesize(self, raw_provider_responses: Any, as_of: Optional[datetime] = None) -> SynthesizedEquitySnapshot:
        """Create a :class:`SynthesizedEquitySnapshot` from raw provider data."""
        if isinstance(raw_provider_responses, str):
            provider_data = {"primary": self._fetch_market_data(raw_provider_responses, as_of=as_of)}
            symbol = raw_provider_responses.upper()
        elif isinstance(raw_provider_responses, dict):
            provider_data = raw_provider_responses
            symbol = None
            for payload in provider_data.values():
                if isinstance(payload, dict) and "symbol" in payload:
                    symbol = str(payload["symbol"]).upper()
                    break
            if symbol is None:
                symbol = "UNKNOWN"
        else:
            logger.error("Unsupported raw_provider_responses type: %s", type(raw_provider_responses))
            provider_data = {}
            symbol = "UNKNOWN"

        prices: List[float] = []
        pe_ratios: List[float] = []
        for payload in provider_data.values():
            if not isinstance(payload, dict):
                continue
            price = payload.get("price")
            pe = payload.get("pe_ratio")
            if isinstance(price, (int, float)):
                prices.append(float(price))
            if isinstance(pe, (int, float)):
                pe_ratios.append(float(pe))

        consensus_price = sum(prices) / len(prices) if prices else None
        consensus_pe = sum(pe_ratios) / len(pe_ratios) if pe_ratios else None

        anomaly_flags: List[str] = []
        tolerance = getattr(settings, "PRICE_CONFLICT_TOLERANCE_PCT", 5.0) / 100.0
        if prices:
            avg_price = consensus_price or 0.0
            for p in prices:
                if avg_price > 0 and abs(p - avg_price) / avg_price > tolerance:
                    anomaly_flags.append("price_conflict")
                    break

        # Compute confidence from actual data availability in ResearchDataStore and live quote presence
        has_quote = 1.0 if (consensus_price is not None and consensus_price > 0) else 0.0
        fin_count = 0
        has_ownership = 0.0
        try:
            from app.services.research_data import ResearchDataStore
            store = ResearchDataStore()
            if symbol and symbol != "UNKNOWN":
                company, financials, events, corp_actions, ownership, documents = store.get_timeline(symbol, as_of=as_of)
                fin_count = len(financials)
                has_ownership = 1.0 if len(ownership) > 0 else 0.0
        except Exception:
            pass

        fin_score = min(1.0, fin_count / 8.0)
        data_confidence_score = round((0.3 * has_quote) + (0.5 * fin_score) + (0.2 * has_ownership), 2)

        # Determine truthful market_data_type without hardcoded "synthetic" label
        is_mock_any = any(payload.get("is_mock") for payload in provider_data.values() if isinstance(payload, dict))
        data_modes = [payload.get("data_mode") for payload in provider_data.values() if isinstance(payload, dict)]
        if "PIT_HISTORICAL" in data_modes:
            market_data_type = "PIT_HISTORICAL"
        elif is_mock_any or "MOCK" in data_modes:
            market_data_type = "SIMULATED"
        elif consensus_price is not None:
            market_data_type = "OBSERVED"
        else:
            market_data_type = "DATA_UNAVAILABLE"

        now_str = get_ist_now_str()
        as_of_str = as_of.isoformat() if as_of else now_str
        meta = MetaHeader(
            source="DataSynthesizer",
            as_of=as_of_str,
            retrieved_at=now_str,
            market_data_type=market_data_type,
            stale=False,
            limitations=["basic reconciliation"],
        )

        snapshot = SynthesizedEquitySnapshot(
            symbol=symbol,
            consensus_price=consensus_price,
            consensus_pe=consensus_pe,
            adjusted_price=None,
            adjusted_pe=None,
            anomaly_flags=anomaly_flags,
            corporate_action_adjusted=False,
            data_confidence_score=data_confidence_score,
            meta=meta,
        )
        return snapshot
