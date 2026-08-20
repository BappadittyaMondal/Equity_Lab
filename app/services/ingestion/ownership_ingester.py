"""Ownership Data Ingester — Fetches shareholding pattern and promoter pledge data.

Follows the same pattern as FinancialIngester and DailyPriceIngester.
Ingests quarterly ownership snapshots into ResearchDataStore via add_ownership_snapshot().
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.services.research_data import ResearchDataStore
from app.services.market_data import normalize_symbol

logger = logging.getLogger(__name__)

_SOURCE_NAME = "bse_nse_filings"
_SOURCE_CONFIDENCE = 0.90


class OwnershipIngester:
    """Ingests quarterly shareholding patterns and promoter pledge data into ResearchDataStore."""

    def __init__(self, store: Optional[ResearchDataStore] = None):
        self.store = store or ResearchDataStore()

    def fetch_ownership_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch official shareholding pattern and promoter pledge data for a symbol.

        DEFERRAL SCOPE NOTE (Release Pass): Live exchange APIs for shareholding patterns
        (BSE/NSE XBRL filings) are deliberately deferred to a post-v0.3 release cycle.
        Returning None guarantees that missing ownership data gracefully reduces the
        Synthesizer data_confidence_score (has_ownership=0.0) without fabricating numbers.
        """
        logger.warning("Ownership data source not yet connected for %s", symbol)
        return None

    def ingest_symbol(self, symbol: str) -> Dict[str, Any]:
        """Ingest ownership snapshot for a given symbol if data source is available.

        Returns a summary dict with counts of snapshots ingested.
        """
        norm = normalize_symbol(symbol)
        ticker_str_clean = norm.replace(".NS", "")

        result = {
            "symbol": ticker_str_clean,
            "snapshots_ingested": 0,
            "errors": [],
        }

        raw_data = self.fetch_ownership_data(ticker_str_clean)
        if raw_data is None:
            result["errors"].append(
                f"No ownership data available: live source not yet connected for {ticker_str_clean}"
            )
            return result

        try:
            # Ensure snapshot fields conform to OwnershipSnapshotIn schema before calling add_ownership_snapshot
            snapshot_payload = {
                "symbol": norm,
                "period_end": raw_data.get("period_end", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
                "promoter_pct": float(raw_data.get("promoter_pct", 0.0)),
                "fii_pct": float(raw_data.get("fii_pct", 0.0)),
                "dii_pct": float(raw_data.get("dii_pct", 0.0)),
                "mutual_fund_pct": raw_data.get("mutual_fund_pct"),
                "insurance_pct": raw_data.get("insurance_pct"),
                "public_pct": float(raw_data.get("public_pct", 100.0)),
                "aif_pct": raw_data.get("aif_pct"),
                "promoter_pledge_pct": raw_data.get("promoter_pledge_pct"),
                "published_at": raw_data.get("published_at", datetime.now(timezone.utc).isoformat()),
                "source_name": raw_data.get("source_name", _SOURCE_NAME),
                "source_url": raw_data.get("source_url", f"https://www.nseindia.com/get-quotes/equity?symbol={ticker_str_clean}"),
                "confidence": float(raw_data.get("confidence", _SOURCE_CONFIDENCE)),
            }

            self.store.add_ownership_snapshot(snapshot_payload)
            result["snapshots_ingested"] = 1
            logger.info("Successfully ingested ownership snapshot for %s", ticker_str_clean)
        except Exception as e:
            logger.error("Failed to store ownership snapshot for %s: %s", ticker_str_clean, e)
            result["errors"].append(f"Storage error for {ticker_str_clean}: {e}")

        return result
