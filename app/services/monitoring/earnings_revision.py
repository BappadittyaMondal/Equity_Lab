"""Earnings Revision Tracking Service (`RevisionTracker`).

Tracks consensus and internal EPS/revenue estimates over time and calculates
revision direction (UP/DOWN/FLAT) and magnitude percentage.

**Data Feed Note:**
No automated live consensus analyst feed is currently wired into the ingestion layer.
Populating the `earnings_estimates` table requires either the manual/CSV ingestion script
(`scripts/ingest_earnings_estimates.py`) or a future paid market data API integration.
"""

import sqlite3
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger(__name__)


class RevisionTracker:
    """Computes estimate revisions and trends from `earnings_estimates` table."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATA_STORE_PATH

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_estimate(
        self,
        symbol: str,
        fiscal_period: str,
        estimate_value: float,
        estimate_type: str = "consensus_eps",
        as_of_date: Optional[str] = None,
        source: str = "MANUAL_INPUT",
        revision_of: Optional[int] = None
    ) -> int:
        """Insert an estimate row into `earnings_estimates` table."""
        symbol_clean = symbol.upper().strip()
        as_of = as_of_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO earnings_estimates 
            (symbol, fiscal_period, estimate_type, estimate_value, as_of_date, source, revision_of)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (symbol_clean, fiscal_period, estimate_type, float(estimate_value), as_of, source, revision_of)
        )
        estimate_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return estimate_id

    def get_estimates(
        self,
        symbol: str,
        fiscal_period: Optional[str] = None,
        estimate_type: str = "consensus_eps"
    ) -> List[Dict[str, Any]]:
        """Fetch estimate rows for a symbol sorted chronologically."""
        symbol_clean = symbol.upper().strip()
        conn = self._get_connection()

        if fiscal_period:
            rows = conn.execute(
                """
                SELECT * FROM earnings_estimates 
                WHERE symbol = ? AND fiscal_period = ? AND estimate_type = ?
                ORDER BY as_of_date ASC, id ASC
                """,
                (symbol_clean, fiscal_period, estimate_type)
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM earnings_estimates 
                WHERE symbol = ? AND estimate_type = ?
                ORDER BY fiscal_period ASC, as_of_date ASC, id ASC
                """,
                (symbol_clean, estimate_type)
            ).fetchall()

        conn.close()
        return [dict(r) for r in rows]

    def compute_revision(
        self,
        symbol: str,
        fiscal_period: str,
        estimate_type: str = "consensus_eps"
    ) -> Dict[str, Any]:
        """Compute revision direction and percentage magnitude given estimate chain."""
        estimates = self.get_estimates(symbol, fiscal_period, estimate_type)

        if not estimates:
            return {
                "symbol": symbol.upper().strip(),
                "fiscal_period": fiscal_period,
                "estimate_type": estimate_type,
                "has_revision": False,
                "revision_direction": "NO_DATA",
                "revision_magnitude_pct": 0.0,
                "initial_estimate": None,
                "latest_estimate": None,
                "estimate_count": 0,
                "notice": "No earnings estimates found for ticker/period. Populating table requires scripts/ingest_earnings_estimates.py."
            }

        if len(estimates) == 1:
            val = estimates[0]["estimate_value"]
            return {
                "symbol": symbol.upper().strip(),
                "fiscal_period": fiscal_period,
                "estimate_type": estimate_type,
                "has_revision": False,
                "revision_direction": "NO_REVISION",
                "revision_magnitude_pct": 0.0,
                "initial_estimate": val,
                "latest_estimate": val,
                "estimate_count": 1,
                "as_of_date": estimates[0]["as_of_date"]
            }

        initial_val = estimates[0]["estimate_value"]
        latest_val = estimates[-1]["estimate_value"]
        prev_val = estimates[-2]["estimate_value"]

        delta = latest_val - prev_val
        if prev_val != 0:
            magnitude_pct = round((delta / abs(prev_val)) * 100.0, 2)
        else:
            magnitude_pct = 0.0

        if delta > 0:
            direction = "UP"
        elif delta < 0:
            direction = "DOWN"
        else:
            direction = "FLAT"

        cumulative_delta = latest_val - initial_val
        cumulative_magnitude_pct = round((cumulative_delta / abs(initial_val)) * 100.0, 2) if initial_val != 0 else 0.0

        return {
            "symbol": symbol.upper().strip(),
            "fiscal_period": fiscal_period,
            "estimate_type": estimate_type,
            "has_revision": True,
            "revision_direction": direction,
            "revision_magnitude_pct": magnitude_pct,
            "cumulative_revision_pct": cumulative_magnitude_pct,
            "initial_estimate": initial_val,
            "previous_estimate": prev_val,
            "latest_estimate": latest_val,
            "estimate_count": len(estimates),
            "latest_as_of_date": estimates[-1]["as_of_date"]
        }

    def compute_revision_breadth_and_momentum(
        self,
        symbol: str,
        estimate_type: str = "consensus_eps"
    ) -> Dict[str, Any]:
        """Compute Revision Breadth and Revision Momentum across all fiscal periods for symbol.

        Formulas:
        Revision Breadth = (Up Revisions - Down Revisions) / Total Revisions
        Revision Momentum = Revision Breadth * Average Revision Magnitude (%)
        """
        symbol_clean = symbol.upper().strip()
        estimates = self.get_estimates(symbol_clean, estimate_type=estimate_type)

        if not estimates or len(estimates) < 2:
            return {
                "symbol": symbol_clean,
                "revision_breadth": 0.0,
                "revision_momentum": 0.0,
                "up_revisions": 0,
                "down_revisions": 0,
                "flat_revisions": 0,
                "total_revisions": 0,
                "avg_magnitude_pct": 0.0,
                "status": "DATA_UNAVAILABLE"
            }

        up_count = 0
        down_count = 0
        flat_count = 0
        magnitudes = []

        for i in range(1, len(estimates)):
            prev_val = estimates[i - 1]["estimate_value"]
            curr_val = estimates[i]["estimate_value"]
            delta = curr_val - prev_val
            mag = (delta / abs(prev_val)) * 100.0 if prev_val != 0 else 0.0
            magnitudes.append(mag)

            if delta > 0:
                up_count += 1
            elif delta < 0:
                down_count += 1
            else:
                flat_count += 1

        total = up_count + down_count + flat_count
        if total == 0:
            breadth = 0.0
            momentum = 0.0
            avg_mag = 0.0
        else:
            breadth = round((up_count - down_count) / float(total), 3)
            avg_mag = round(sum(magnitudes) / float(len(magnitudes)), 2)
            momentum = round(breadth * avg_mag, 2)

        return {
            "symbol": symbol_clean,
            "revision_breadth": breadth,
            "revision_momentum": momentum,
            "up_revisions": up_count,
            "down_revisions": down_count,
            "flat_revisions": flat_count,
            "total_revisions": total,
            "avg_magnitude_pct": avg_mag,
            "status": "PRODUCTION"
        }

