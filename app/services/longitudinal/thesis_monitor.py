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
        prior_probability: float = 0.50
    ) -> ThesisMonitor:
        """Evaluate and update investment thesis state based on Bayesian evidence updating.

        Bayesian Update Formula (Section 28):
        P(Thesis | Evidence) = [ Likelihood_Ratio * Prior ] / [ Likelihood_Ratio * Prior + (1 - Prior) ]
        """
        from app.services.market_data import normalize_symbol
        normalized = normalize_symbol(symbol)
        existing = self.get_thesis(normalized)

        # 1. Compute Likelihood Ratio L = P(Evidence|Thesis) / P(Evidence|Not Thesis)
        if conviction_score >= 80 and not contradictions:
            likelihood_ratio = 3.5  # Strong confirming evidence
        elif conviction_score >= 60 and len(contradictions) <= 1:
            likelihood_ratio = 1.8  # Moderate positive evidence
        elif verdict == "Avoid" or conviction_score < 30:
            likelihood_ratio = 0.15  # Strongly disconfirming evidence
        elif contradictions or conviction_score < 50:
            likelihood_ratio = 0.45  # Negative evidence
        else:
            likelihood_ratio = 1.0  # Neutral evidence

        # 2. Compute Posterior Probability
        prior = max(0.01, min(0.99, prior_probability))
        posterior_num = likelihood_ratio * prior
        posterior_den = posterior_num + (1.0 - prior)
        posterior_prob = round(posterior_num / posterior_den, 3)

        # 3. Map Posterior Probability to Thesis State Taxonomy (§28 & §29)
        if posterior_prob >= 0.75:
            thesis_state = "STRENGTHENING"
        elif posterior_prob >= 0.50:
            thesis_state = "STABLE"
        elif posterior_prob >= 0.25:
            thesis_state = "WEAKENING"
        else:
            thesis_state = "BROKEN"

        # Parameter Assembly
        why_buy = primary_thesis if primary_thesis else f"Investment thesis for {normalized} based on quant signals."
        growth_drivers = [
            f"Conviction score: {conviction_score}/100",
            f"Verdict: {verdict}",
            f"Bayesian Thesis Probability: {posterior_prob*100:.1f}% (Likelihood Ratio: {likelihood_ratio:.2f}x)"
        ]
        catalysts = ["Quarterly earnings acceleration", "Institutional re-rating"]
        risks = [f"Contradicting engines: {', '.join(contradictions)}"] if contradictions else ["Macro slowdown"]
        thesis_conditions = ["Conviction score >= 50", "Bayesian probability >= 50%", "No governance veto"]
        invalidation_conditions = ["Conviction score < 30", "Bayesian probability < 25%", "Governance grade POOR/UNKNOWN"]

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
