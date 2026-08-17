"""Investment Thesis Monitoring Engine.

Maintains structural investment thesis records (WHY BUY, GROWTH DRIVERS, CATALYSTS, RISKS,
THESIS CONDITIONS, INVALIDATION CONDITIONS) and evaluates thesis state (STRENGTHENING, STABLE, WEAKENING, BROKEN).
"""

import json
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.models.schemas import ThesisMonitor
from app.services.db import get_connection


class ThesisMonitorEngine:
    """Evaluates and persists investment thesis state changes."""

    def __init__(self, db: Optional[sqlite3.Connection] = None):
        self.db = db or get_connection()

    def get_thesis(self, symbol: str) -> Optional[ThesisMonitor]:
        """Fetch current investment thesis record for a symbol."""
        row = self.db.execute(
            "SELECT * FROM thesis_records WHERE symbol = ?",
            (symbol.upper(),),
        ).fetchone()
        if not row:
            return None
        row_dict = dict(row)
        return ThesisMonitor(
            symbol=row_dict["symbol"],
            why_buy=row_dict["why_buy"],
            growth_drivers=json.loads(row_dict.get("growth_drivers") or "[]"),
            catalysts=json.loads(row_dict.get("catalysts") or "[]"),
            risks=json.loads(row_dict.get("risks") or "[]"),
            thesis_conditions=json.loads(row_dict.get("thesis_conditions") or "[]"),
            invalidation_conditions=json.loads(row_dict.get("invalidation_conditions") or "[]"),
            thesis_state=row_dict["thesis_state"],
            updated_at=row_dict["updated_at"],
        )

    def evaluate_thesis_state(
        self,
        symbol: str,
        conviction_score: int,
        verdict: str,
        contradictions: List[str],
        primary_thesis: str,
    ) -> ThesisMonitor:
        """Evaluate and update investment thesis state based on fresh evidence."""
        from app.services.market_data import normalize_symbol
        normalized = normalize_symbol(symbol)
        existing = self.get_thesis(normalized)

        # Default thesis parameters if none exists
        why_buy = primary_thesis if primary_thesis else f"Investment thesis for {normalized} based on quant signals."
        growth_drivers = [f"Conviction score: {conviction_score}/100", f"Verdict: {verdict}"]
        catalysts = ["Quarterly earnings acceleration", "Institutional re-rating"]
        risks = [f"Contradicting engines: {', '.join(contradictions)}"] if contradictions else ["Macro slowdown"]
        thesis_conditions = ["Conviction score >= 50", "No governance veto"]
        invalidation_conditions = ["Conviction score < 30", "Governance grade POOR/UNKNOWN", "PAT margin breakdown"]

        # Determine state trajectory
        if conviction_score >= 80 and not contradictions:
            thesis_state = "STRENGTHENING"
        elif verdict == "Avoid" or conviction_score < 30:
            thesis_state = "BROKEN"
        elif contradictions or conviction_score < 50:
            thesis_state = "WEAKENING"
        else:
            thesis_state = "STABLE"

        thesis = ThesisMonitor(
            symbol=normalized,
            why_buy=why_buy,
            growth_drivers=growth_drivers,
            catalysts=catalysts,
            risks=risks,
            thesis_conditions=thesis_conditions,
            invalidation_conditions=invalidation_conditions,
            thesis_state=thesis_state,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

        self._upsert_thesis(thesis)
        return thesis

    def _upsert_thesis(self, thesis: ThesisMonitor) -> None:
        self.db.execute(
            """
            INSERT INTO thesis_records (
                symbol, why_buy, growth_drivers, catalysts, risks,
                thesis_conditions, invalidation_conditions, thesis_state, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                why_buy=excluded.why_buy,
                growth_drivers=excluded.growth_drivers,
                catalysts=excluded.catalysts,
                risks=excluded.risks,
                thesis_conditions=excluded.thesis_conditions,
                invalidation_conditions=excluded.invalidation_conditions,
                thesis_state=excluded.thesis_state,
                updated_at=excluded.updated_at
            """,
            (
                thesis.symbol,
                thesis.why_buy,
                json.dumps(thesis.growth_drivers),
                json.dumps(thesis.catalysts),
                json.dumps(thesis.risks),
                json.dumps(thesis.thesis_conditions),
                json.dumps(thesis.invalidation_conditions),
                thesis.thesis_state,
                thesis.updated_at,
            ),
        )
        self.db.commit()
