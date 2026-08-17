"""Daily Price Ingester — Stores OHLCV into market_daily_snapshots.

Fetches daily OHLCV data from yfinance and stores it in the
ResearchDataStore's market_daily_snapshots table for use by
technical analysis engines.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.research_data import ResearchDataStore
from app.services.market_data import normalize_symbol, get_history

logger = logging.getLogger(__name__)


class DailyPriceIngester:
    """Ingests daily OHLCV price data into market_daily_snapshots."""

    def __init__(self, store: Optional[ResearchDataStore] = None):
        self.store = store or ResearchDataStore()

    def ingest_symbol(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Ingest daily price data for a symbol over given period.

        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
            period: Data period (e.g., "1y", "2y", "5y")

        Returns:
            Summary dict with ingestion counts.
        """
        norm = normalize_symbol(symbol)
        ticker_str = norm if norm.endswith(".NS") else norm + ".NS"

        result = {
            "symbol": ticker_str.replace(".NS", ""),
            "snapshots_ingested": 0,
            "errors": [],
        }

        # Ensure company record exists
        try:
            self.store.upsert_company({
                "symbol": ticker_str,
                "company_name": ticker_str.replace(".NS", ""),
                "legal_name": ticker_str.replace(".NS", ""),
                "sector": "",
            })
        except Exception:
            pass

        try:
            hist = get_history(norm, period=period, interval="1d")
            if hist is None or hist.empty:
                result["errors"].append(f"No historical data returned for {norm}")
                return result
        except Exception as e:
            result["errors"].append(f"History fetch failed: {e}")
            return result

        now_iso = datetime.now(timezone.utc).isoformat()

        for idx, row in hist.iterrows():
            try:
                trading_date = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)[:10]
                self.store.add_market_daily_snapshot({
                    "symbol": ticker_str,
                    "trading_date": trading_date,
                    "open_price": float(row.get("Open", 0)),
                    "high_price": float(row.get("High", 0)),
                    "low_price": float(row.get("Low", 0)),
                    "close_price": float(row.get("Close", 0)),
                    "volume": int(row.get("Volume", 0)),
                    "delivery_volume": None,
                    "delivery_pct": None,
                    "market_cap": None,
                    "published_at": now_iso,
                    "source_name": "yfinance",
                    "source_url": f"https://finance.yahoo.com/quote/{norm}/history/",
                })
                result["snapshots_ingested"] += 1
            except Exception as e:
                logger.debug("Daily snapshot store error for %s on %s: %s", norm, idx, e)

        logger.info("Ingested %d daily snapshots for %s", result["snapshots_ingested"], norm)
        return result
