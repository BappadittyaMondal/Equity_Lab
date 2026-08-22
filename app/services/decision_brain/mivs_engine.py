"""Institutional Multi-Factor Investment Vector Score (MIVS) Engine.

Composes underlying analytical engines (Incremental ROIC, Moat Engine, Unit Economics,
Expectation Gap / Revision Breadth, Forensic Scores, Technical Scores) into a gated,
100-point composite investment vector score with explicit hard-gate veto checks.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MIVSDimensionScore(BaseModel):
    name: str
    weight: float
    raw_score: float  # 0.0 to 100.0
    weighted_score: float  # raw_score * weight
    details: Dict[str, Any] = Field(default_factory=dict)


class MIVSScoreResult(BaseModel):
    symbol: str
    mivs_score: float  # 0.0 to 100.0
    verdict: str  # Strong Buy / Buy / Accumulate / Watch / Avoid
    passed_hard_gates: bool
    gate_reasons: List[str] = Field(default_factory=list)
    dimension_scores: Dict[str, MIVSDimensionScore] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MIVSEngine:
    """Multi-Factor Investment Vector Score (MIVS) calculator."""

    HARD_GATE_VETO_CAP = 30.0

    DIMENSION_WEIGHTS = {
        "BUSINESS_QUALITY_MOAT": 0.25,
        "CAPITAL_ALLOCATION_ROIC": 0.20,
        "VALUATION_EXPECTATION_GAP": 0.20,
        "EARNINGS_REVISION_MOMENTUM": 0.15,
        "TECHNICAL_TREND_VECTOR": 0.10,
        "GOVERNANCE_FORENSIC_SAFETY": 0.10,
    }

    def compute_mivs(
        self,
        symbol: str,
        engine_outputs: List[Dict[str, Any]],
        financial_snapshot: Optional[Any] = None,
    ) -> MIVSScoreResult:
        """Computes the 100-point MIVS vector score across 6 weighted dimensions.

        Evaluates 4 Hard Gates before final score aggregation:
          1. Beneish M-Score Veto (> -1.78 or CRITICAL risk)
          2. Altman Z-Score Veto (< 1.81 distress)
          3. High Promoter Pledge Veto (> 40%)
          4. Governance Quality Veto (POOR grade)
        """
        norm_symbol = symbol.upper()
        gate_reasons = []

        # ── 1. Evaluate Hard Gates ──────────────────────────────────────────────
        for out in engine_outputs:
            raw = out.get("raw")
            if not raw:
                continue

            results = getattr(raw, "results", {}) or {}
            metrics = getattr(raw, "metrics", {}) or {}

            # Beneish M-Score check
            beneish_score = results.get("beneish_m_score") or metrics.get("beneish_m_score")
            forensic_risk = results.get("forensic_risk") or metrics.get("forensic_risk")
            if (beneish_score is not None and isinstance(beneish_score, (int, float)) and beneish_score > -1.78) or forensic_risk == "CRITICAL":
                gate_reasons.append(f"Beneish M-Score / Forensic Veto (Score={beneish_score}, Risk={forensic_risk})")

            # Altman Z-Score check
            altman_z = results.get("altman_z_score") or metrics.get("altman_z_score")
            if altman_z is not None and isinstance(altman_z, (int, float)) and altman_z < 1.81:
                gate_reasons.append(f"Altman Z-Score Distress Veto (Z-Score={altman_z:.2f} < 1.81)")

            # Promoter Pledge check
            pledge = results.get("promoter_pledge_pct") or metrics.get("promoter_pledge_pct")
            if pledge is not None and isinstance(pledge, (int, float)) and pledge > 40.0:
                gate_reasons.append(f"High Promoter Pledge Veto (Pledge={pledge:.1f}% > 40%)")

            # Governance Grade check
            if out.get("engine_id") == "C13":
                gov_grade = results.get("governance_grade")
                if gov_grade == "POOR":
                    gate_reasons.append("Governance Quality Veto (Grade=POOR)")

        passed_hard_gates = len(gate_reasons) == 0

        # ── 2. Dimension Scoring ───────────────────────────────────────────────
        dimension_map: Dict[str, List[float]] = {k: [] for k in self.DIMENSION_WEIGHTS}
        details_map: Dict[str, Dict[str, Any]] = {k: {} for k in self.DIMENSION_WEIGHTS}

        for out in engine_outputs:
            eng_id = out.get("engine_id", "")
            confidence = float(out.get("confidence", 70))
            passed = out.get("verdict") == "Buy"
            raw = out.get("raw")
            results = getattr(raw, "results", {}) or {} if raw else {}
            score_0_100 = getattr(raw, "score_0_100", None) or (confidence if passed else 30.0)

            # Map engine to dimension
            if eng_id in ("E1", "E6", "E13", "MOAT"):
                dimension_map["BUSINESS_QUALITY_MOAT"].append(score_0_100)
                details_map["BUSINESS_QUALITY_MOAT"][eng_id] = score_0_100
            elif eng_id in ("E7", "E8", "UNIT_ECONOMICS"):
                dimension_map["CAPITAL_ALLOCATION_ROIC"].append(score_0_100)
                details_map["CAPITAL_ALLOCATION_ROIC"][eng_id] = score_0_100
            elif eng_id in ("E2", "C9", "GROWTH_ARBITRAGE"):
                dimension_map["VALUATION_EXPECTATION_GAP"].append(score_0_100)
                details_map["VALUATION_EXPECTATION_GAP"][eng_id] = score_0_100
            elif eng_id in ("E21", "E24", "EARNINGS_REVISION"):
                dimension_map["EARNINGS_REVISION_MOMENTUM"].append(score_0_100)
                details_map["EARNINGS_REVISION_MOMENTUM"][eng_id] = score_0_100
            elif eng_id in ("B5", "B8", "D15", "TECHNICAL"):
                dimension_map["TECHNICAL_TREND_VECTOR"].append(score_0_100)
                details_map["TECHNICAL_TREND_VECTOR"][eng_id] = score_0_100
            elif eng_id in ("C11", "C12", "C13", "FORENSIC"):
                dimension_map["GOVERNANCE_FORENSIC_SAFETY"].append(score_0_100)
                details_map["GOVERNANCE_FORENSIC_SAFETY"][eng_id] = score_0_100

        # ── 3. Aggregate Dimension & Composite Score ───────────────────────────
        dimension_scores: Dict[str, MIVSDimensionScore] = {}
        weighted_sum = 0.0

        for dim_key, weight in self.DIMENSION_WEIGHTS.items():
            scores = dimension_map[dim_key]
            if scores:
                raw_score = sum(scores) / len(scores)
            else:
                raw_score = 50.0  # neutral fallback if no specific engine ran for dim
            
            w_score = raw_score * weight
            weighted_sum += w_score

            dimension_scores[dim_key] = MIVSDimensionScore(
                name=dim_key,
                weight=weight,
                raw_score=round(raw_score, 1),
                weighted_score=round(w_score, 1),
                details=details_map[dim_key],
            )

        if not passed_hard_gates:
            final_mivs = min(weighted_sum, self.HARD_GATE_VETO_CAP)
            verdict = "Avoid"
        else:
            final_mivs = weighted_sum
            if final_mivs >= 85.0:
                verdict = "Strong Buy"
            elif final_mivs >= 70.0:
                verdict = "Buy"
            elif final_mivs >= 55.0:
                verdict = "Accumulate"
            elif final_mivs >= 40.0:
                verdict = "Watch"
            else:
                verdict = "Avoid"

        return MIVSScoreResult(
            symbol=norm_symbol,
            mivs_score=round(final_mivs, 1),
            verdict=verdict,
            passed_hard_gates=passed_hard_gates,
            gate_reasons=gate_reasons,
            dimension_scores=dimension_scores,
            metadata={"dimension_count": len(dimension_scores), "hard_gates_checked": 4},
        )
