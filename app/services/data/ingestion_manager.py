"""Ingestion Manager for Equity Lab Data Pipelines.

Handles ingestion, normalization, rate limiting, and point-in-time database storage for
Indian Equities (BSE/NSE filings, quarterly statements, promoter holdings, price-volume history).
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from app.services.db import get_connection

logger = logging.getLogger(__name__)


class IngestionManager:
    """Manages multi-source data ingestion and point-in-time database persistence."""

    def normalize_symbol(self, symbol: str) -> str:
        """Ensure symbol has standard Indian exchange ticker suffix (.NS or .BO)."""
        sym = symbol.strip().upper()
        if not (sym.endswith(".NS") or sym.endswith(".BO")):
            sym = f"{sym}.NS"
        return sym

    def ingest_quarterly_financials(self, records: List[Dict[str, Any]]) -> int:
        """Insert or update quarterly financial records in the point-in-time store.

        Each record expected to contain:
        - symbol, period_ended, revenue, operating_profit, net_profit, eps,
          operating_margin_pct, net_margin_pct, roce_pct, roe_pct, as_of_date, source
        """
        conn = get_connection()
        inserted_count = 0
        now_str = datetime.now(timezone.utc).isoformat()

        try:
            for rec in records:
                sym = self.normalize_symbol(rec["symbol"])
                as_of = rec.get("as_of_date", now_str)
                source = rec.get("source", "automated_ingestion")

                conn.execute(
                    """
                    INSERT INTO quarterly_financials (
                        symbol, period_ended, revenue, operating_profit, net_profit, eps,
                        operating_margin_pct, net_margin_pct, roce_pct, roe_pct, as_of_date, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(symbol, period_ended) DO UPDATE SET
                        revenue = excluded.revenue,
                        operating_profit = excluded.operating_profit,
                        net_profit = excluded.net_profit,
                        eps = excluded.eps,
                        operating_margin_pct = excluded.operating_margin_pct,
                        net_margin_pct = excluded.net_margin_pct,
                        roce_pct = excluded.roce_pct,
                        roe_pct = excluded.roe_pct,
                        as_of_date = excluded.as_of_date,
                        source = excluded.source
                    """,
                    (
                        sym,
                        rec["period_ended"],
                        rec.get("revenue"),
                        rec.get("operating_profit"),
                        rec.get("net_profit"),
                        rec.get("eps"),
                        rec.get("operating_margin_pct"),
                        rec.get("net_margin_pct"),
                        rec.get("roce_pct"),
                        rec.get("roe_pct"),
                        as_of,
                        source,
                    ),
                )
                inserted_count += 1

            conn.commit()
            return inserted_count
        except Exception as e:
            conn.rollback()
            logger.error("Failed to ingest quarterly financials: %s", e)
            raise e
        finally:
            conn.close()

    def ingest_promoter_shareholding(self, records: List[Dict[str, Any]]) -> int:
        """Insert or update promoter shareholding data."""
        conn = get_connection()
        inserted_count = 0
        now_str = datetime.now(timezone.utc).isoformat()

        try:
            for rec in records:
                sym = self.normalize_symbol(rec["symbol"])
                as_of = rec.get("as_of_date", now_str)
                source = rec.get("source", "automated_ingestion")

                conn.execute(
                    """
                    INSERT INTO promoter_shareholding (
                        symbol, period_ended, promoter_holding_pct, pledged_pct,
                        institutional_holding_pct, as_of_date, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(symbol, period_ended) DO UPDATE SET
                        promoter_holding_pct = excluded.promoter_holding_pct,
                        pledged_pct = excluded.pledged_pct,
                        institutional_holding_pct = excluded.institutional_holding_pct,
                        as_of_date = excluded.as_of_date,
                        source = excluded.source
                    """,
                    (
                        sym,
                        rec["period_ended"],
                        rec["promoter_holding_pct"],
                        rec.get("pledged_pct", 0.0),
                        rec.get("institutional_holding_pct", 0.0),
                        as_of,
                        source,
                    ),
                )
                inserted_count += 1

            conn.commit()
            return inserted_count
        except Exception as e:
            conn.rollback()
            logger.error("Failed to ingest promoter shareholding: %s", e)
            raise e
        finally:
            conn.close()

    def ingest_historical_prices(self, records: List[Dict[str, Any]]) -> int:
        """Insert or update historical daily price-volume records."""
        conn = get_connection()
        inserted_count = 0
        now_str = datetime.now(timezone.utc).isoformat()

        try:
            for rec in records:
                sym = self.normalize_symbol(rec["symbol"])
                as_of = rec.get("as_of_date", now_str)

                conn.execute(
                    """
                    INSERT INTO historical_prices (
                        symbol, date, open, high, low, close, volume, adjusted_close, as_of_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(symbol, date) DO UPDATE SET
                        open = excluded.open,
                        high = excluded.high,
                        low = excluded.low,
                        close = excluded.close,
                        volume = excluded.volume,
                        adjusted_close = excluded.adjusted_close,
                        as_of_date = excluded.as_of_date
                    """,
                    (
                        sym,
                        rec["date"],
                        rec["open"],
                        rec["high"],
                        rec["low"],
                        rec["close"],
                        rec["volume"],
                        rec.get("adjusted_close", rec["close"]),
                        as_of,
                    ),
                )
                inserted_count += 1

            conn.commit()
            return inserted_count
        except Exception as e:
            conn.rollback()
            logger.error("Failed to ingest historical prices: %s", e)
            raise e
        finally:
            conn.close()

    def get_latest_financials(self, symbol: str, as_of_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve quarterly financials respecting point-in-time publication date."""
        conn = get_connection()
        sym = self.normalize_symbol(symbol)
        try:
            if as_of_date:
                rows = conn.execute(
                    """
                    SELECT * FROM quarterly_financials
                    WHERE symbol = ? AND as_of_date <= ?
                    ORDER BY period_ended DESC
                    """,
                    (sym, as_of_date),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM quarterly_financials
                    WHERE symbol = ?
                    ORDER BY period_ended DESC
                    """,
                    (sym,),
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
