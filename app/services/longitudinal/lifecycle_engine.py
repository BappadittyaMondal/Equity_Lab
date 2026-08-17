"""Deterministic Lifecycle State Machine Engine.

Consumes existing strategy outputs (Turnaround, Growth Inflection, Multibagger, Growth Arbitrage, Technicals)
and computes the current company lifecycle stage, tracking stage transitions over time.
"""

import json
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.models.schemas import LifecycleState
from app.services.db import get_connection


class LifecycleEngine:
    """Computes and persists deterministic company lifecycle state transitions."""

    VALID_STAGES = {
        "DISCOVERY",
        "EARLY_IMPROVEMENT",
        "GROWTH_INFLECTION",
        "EARNINGS_ACCELERATION",
        "RECOGNITION",
        "RERATING",
        "MATURE_GROWTH",
        "DECELERATION",
        "BREAKDOWN",
        "TURNAROUND",
        "RECOVERY",
    }

    def __init__(self, db: Optional[sqlite3.Connection] = None):
        self.db = db or get_connection()

    def get_latest_lifecycle(self, symbol: str) -> Optional[LifecycleState]:
        """Fetch the most recent persisted lifecycle state for a symbol."""
        row = self.db.execute(
            "SELECT * FROM lifecycle_transitions WHERE symbol = ? ORDER BY id DESC LIMIT 1",
            (symbol.upper(),),
        ).fetchone()
        if not row:
            return None
        row_dict = dict(row)
        evidence = []
        if row_dict.get("supporting_evidence"):
            try:
                evidence = json.loads(row_dict["supporting_evidence"])
            except Exception:
                evidence = []
        return LifecycleState(
            symbol=row_dict["symbol"],
            previous_stage=row_dict["previous_stage"],
            current_stage=row_dict["current_stage"],
            transition_date=row_dict["created_at"],
            transition_reason=row_dict["transition_reason"],
            confidence=row_dict["confidence"],
            supporting_evidence=evidence,
        )

    def evaluate_lifecycle(
        self,
        symbol: str,
        engine_outputs: List[Dict[str, Any]],
        conviction_score: int,
    ) -> LifecycleState:
        """Evaluate deterministic lifecycle stage from strategy engine signals."""
        from app.services.market_data import normalize_symbol
        normalized = normalize_symbol(symbol)

        # Extract flags from strategy run outputs
        engine_map = {out["engine_id"]: out for out in engine_outputs}

        turnaround_out = engine_map.get("E2", {})
        growth_inflection_out = engine_map.get("E1", {})
        multibagger_out = engine_map.get("E4", {})
        ath_breakout_out = engine_map.get("D15", {})

        is_turnaround = turnaround_out.get("verdict") == "Buy" or getattr(turnaround_out.get("raw"), "passed_gates", False)
        is_growth_inflection = growth_inflection_out.get("verdict") == "Buy" or getattr(growth_inflection_out.get("raw"), "passed_gates", False)
        is_multibagger = multibagger_out.get("verdict") == "Buy" or getattr(multibagger_out.get("raw"), "passed_gates", False)
        is_breakout = ath_breakout_out.get("verdict") == "Buy" or getattr(ath_breakout_out.get("raw"), "passed_gates", False)

        evidence: List[str] = []
        previous = self.get_latest_lifecycle(normalized)
        prev_stage = previous.current_stage if previous else None

        # Determine stage via deterministic rules
        if is_turnaround:
            if prev_stage == "TURNAROUND":
                current_stage = "RECOVERY"
                reason = "Turnaround confirmed by operational recovery metrics."
            else:
                current_stage = "TURNAROUND"
                reason = "Turnaround stage detected by margin stabilization and debt reduction."
            evidence.append("Turnaround engine E2 passed.")
        elif is_growth_inflection and is_breakout:
            current_stage = "EARNINGS_ACCELERATION"
            reason = "Earnings inflection coupled with technical ATH breakout."
            evidence.append("Growth inflection E1 and Breakout D15 passed.")
        elif is_growth_inflection:
            current_stage = "GROWTH_INFLECTION"
            reason = "Quarterly revenue and PAT growth acceleration detected."
            evidence.append("Growth inflection E1 passed.")
        elif is_multibagger and conviction_score >= 80:
            current_stage = "RERATING"
            reason = "High conviction score (>=80) with top multibagger quality metrics."
            evidence.append("Multibagger screener E4 passed with high score.")
        elif is_multibagger:
            current_stage = "RECOGNITION"
            reason = "Multibagger quality screener passed initial thresholds."
            evidence.append("Multibagger screener E4 passed.")
        elif conviction_score >= 60:
            current_stage = "EARLY_IMPROVEMENT"
            reason = "Moderate conviction score showing initial fundamental improvement."
            evidence.append("Conviction score >= 60.")
        elif conviction_score < 30:
            current_stage = "BREAKDOWN"
            reason = "Low conviction score (<30) indicating deteriorating fundamentals or governance veto."
            evidence.append("Conviction score < 30.")
        else:
            current_stage = "DISCOVERY"
            reason = "Baseline stage; monitoring for fundamental signals."
            evidence.append("Baseline assessment.")

        state = LifecycleState(
            symbol=normalized,
            previous_stage=prev_stage,
            current_stage=current_stage,
            transition_date=datetime.now(timezone.utc).isoformat(),
            transition_reason=reason,
            confidence=0.85 if evidence else 0.70,
            supporting_evidence=evidence,
        )

        # Persist if stage changed or no previous record exists
        if not previous or previous.current_stage != current_stage:
            self._persist(state)

        return state

    def _persist(self, state: LifecycleState) -> None:
        self.db.execute(
            """
            INSERT INTO lifecycle_transitions (symbol, previous_stage, current_stage, transition_reason, confidence, supporting_evidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                state.symbol,
                state.previous_stage,
                state.current_stage,
                state.transition_reason,
                state.confidence,
                json.dumps(state.supporting_evidence),
                state.transition_date,
            ),
        )
        self.db.commit()
