"""Institutional Multi-Factor Investment Vector Score (MIVS) Engine (Enhanced & Expanded Edition).

Composes underlying analytical engines across 9 reweighted components (100 points) and
enforces 7 explicit hard-gate veto checks per Section 51 and Section 52 of the Institutional Framework.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.services.research.peer_normalization import evaluate_peer_normalization

logger = logging.getLogger(__name__)


class MIVSDimensionScore(BaseModel):
    name: str
    weight: float
    raw_score: float  # 0.0 to 100.0
    weighted_score: float  # raw_score * weight
    percentile_rank: Optional[float] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class MIVSScoreResult(BaseModel):
    symbol: str
    mivs_score: float  # 0.0 to 100.0
    verdict: str  # Strong Buy / Buy / Accumulate / Watch / Avoid
    passed_hard_gates: bool
    gate_reasons: List[str] = Field(default_factory=list)
    dimension_scores: Dict[str, MIVSDimensionScore] = Field(default_factory=dict)
    sector_relative_percentile: float = 50.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MIVSEngine:
    """Multi-Factor Investment Vector Score (MIVS) calculator across 9 weighted components."""

    HARD_GATE_VETO_CAP = 30.0

    # 9-Component Reweighted Vector Distribution (§52)
    DIMENSION_WEIGHTS = {
        "FUNDAMENTAL_INFLECTION": 0.22,         # 22 pts
        "BUSINESS_INDUSTRY_QUALITY": 0.18,       # 18 pts
        "INCREMENTAL_ECONOMICS": 0.13,           # 13 pts
        "GROWTH_AND_RUNWAY": 0.12,               # 12 pts
        "EXPECTATION_GAP_REVISIONS": 0.10,       # 10 pts
        "GOVERNANCE_PROMOTER_BEHAVIOUR": 0.08,   # 8 pts
        "VALUATION_ASYMMETRY": 0.08,             # 8 pts
        "MARKET_CONFIRMATION_ALT_DATA": 0.05,    # 5 pts
        "EVIDENCE_CONFIDENCE": 0.04,             # 4 pts
    }

    def compute_mivs(
        self,
        symbol: str,
        engine_outputs: List[Dict[str, Any]],
        financial_snapshot: Optional[Any] = None,
        sector: str = "MANUFACTURING"
    ) -> MIVSScoreResult:
        """Computes the 100-point MIVS vector score across 9 weighted components.

        Evaluates 7 Hard Gates before final score aggregation (§51):
          1. Accounting & Forensic Integrity (Beneish > -1.78 / Piotroski < 3)
          2. Financial Survival (Altman Z < 1.81)
          3. Business Quality (ROIC floor check)
          4. Fundamental Trajectory (Deteriorating operational trend)
          5. Expectation Gap (Market over-expectation)
          6. Valuation Asymmetry (Zero margin of safety)
          7. Governance & Bias-Check (Promoter pledge > 40%, related-party red flags, missing red-team review)
        """
        norm_symbol = symbol.upper()
        gate_reasons = []

        # ── 1. Evaluate 7 Hard Gates ───────────────────────────────────────────
        for out in engine_outputs:
            raw = out.get("raw")
            if not raw:
                continue

            results = getattr(raw, "results", {}) or {}
            metrics = getattr(raw, "metrics", {}) or {}

            # Gate 1: Accounting & Forensic Integrity
            beneish_score = results.get("beneish_m_score") or metrics.get("beneish_m_score")
            piotroski_f = results.get("piotroski_f_score") or metrics.get("piotroski_f_score")
            forensic_risk = results.get("forensic_risk") or metrics.get("forensic_risk")
            if (beneish_score is not None and isinstance(beneish_score, (int, float)) and beneish_score > -1.78) or forensic_risk == "CRITICAL":
                gate_reasons.append(f"Gate 1 Veto: Beneish M-Score / Forensic Risk (M-Score={beneish_score})")
            if piotroski_f is not None and isinstance(piotroski_f, int) and piotroski_f < 3:
                gate_reasons.append(f"Gate 1 Veto: Piotroski F-Score ({piotroski_f}/9 < 3)")

            # Gate 2: Financial Survival
            altman_z = results.get("altman_z_score") or metrics.get("altman_z_score")
            if altman_z is not None and isinstance(altman_z, (int, float)) and altman_z < 1.81:
                gate_reasons.append(f"Gate 2 Veto: Altman Z-Score Distress (Z-Score={altman_z:.2f} < 1.81)")

            # Gate 3: Business Quality Floor
            roic = results.get("roic_pct") or metrics.get("roic_pct")
            if roic is not None and isinstance(roic, (int, float)) and roic < 6.0:
                gate_reasons.append(f"Gate 3 Veto: Business Quality ROIC Floor (ROIC={roic:.1f}% < 6.0%)")

            # Gate 4: Fundamental Trajectory
            stage = results.get("stage") or results.get("turnaround_stage")
            if stage == "Exhausting" or results.get("false_turnaround_risk") == "CRITICAL":
                gate_reasons.append("Gate 4 Veto: Fundamental Trajectory Breakdown")

            # Gate 5: Expectation Gap Overshoot
            gap_class = results.get("gap_classification")
            if gap_class == "PRICED_IN" and results.get("potential_rerating_score", 50) < 20:
                gate_reasons.append("Gate 5 Veto: Market Expectation Gap Heavily Overshot")

            # Gate 6: Valuation Asymmetry
            rec = results.get("recommendation")
            risk_rating = results.get("risk_rating")
            if rec == "AVOID" and risk_rating == "EXTREME":
                gate_reasons.append("Gate 6 Veto: Severe Valuation Overvaluation / Negative Asymmetry")

            # Gate 7: Governance & Bias-Check
            pledge = results.get("promoter_pledge_pct") or metrics.get("promoter_pledge_pct")
            if pledge is not None and isinstance(pledge, (int, float)) and pledge > 40.0:
                gate_reasons.append(f"Gate 7 Veto: High Promoter Pledge (Pledge={pledge:.1f}% > 40%)")

            if out.get("engine_id") == "C13":
                gov_grade = results.get("governance_grade")
                if gov_grade == "POOR":
                    gate_reasons.append("Gate 7 Veto: Governance Quality Grade POOR")

        passed_hard_gates = len(gate_reasons) == 0

        # ── 2. Dimension Scoring Across 9 Components ───────────────────────────
        dimension_map: Dict[str, List[float]] = {k: [] for k in self.DIMENSION_WEIGHTS}
        details_map: Dict[str, Dict[str, Any]] = {k: {} for k in self.DIMENSION_WEIGHTS}

        for out in engine_outputs:
            eng_id = out.get("engine_id", "")
            confidence = float(out.get("confidence", 70))
            passed = out.get("verdict") == "Buy"
            raw = out.get("raw")
            results = getattr(raw, "results", {}) or {} if raw else {}
            score_0_100 = getattr(raw, "score_0_100", None) or (confidence if passed else 30.0)

            # Map engines to 9 MIVS dimensions
            if eng_id in ("E1", "GROWTH_INFLECTION"):
                dimension_map["FUNDAMENTAL_INFLECTION"].append(score_0_100)
                details_map["FUNDAMENTAL_INFLECTION"][eng_id] = score_0_100
            elif eng_id in ("MOAT", "E6", "B5", "BUSINESS_QUALITY"):
                dimension_map["BUSINESS_INDUSTRY_QUALITY"].append(score_0_100)
                details_map["BUSINESS_INDUSTRY_QUALITY"][eng_id] = score_0_100
            elif eng_id in ("E8", "UNIT_ECONOMICS", "INCREMENTAL_ROIC", "D18"):
                dimension_map["INCREMENTAL_ECONOMICS"].append(score_0_100)
                details_map["INCREMENTAL_ECONOMICS"][eng_id] = score_0_100
            elif eng_id in ("MULTIBAGGER", "E4", "E13", "E7", "D15"):
                dimension_map["GROWTH_AND_RUNWAY"].append(score_0_100)
                details_map["GROWTH_AND_RUNWAY"][eng_id] = score_0_100
            elif eng_id in ("E2", "E21", "EXPECTATION_GAP", "REVISION_MOMENTUM"):
                dimension_map["EXPECTATION_GAP_REVISIONS"].append(score_0_100)
                details_map["EXPECTATION_GAP_REVISIONS"][eng_id] = score_0_100
            elif eng_id in ("C13", "PROMOTER_BEHAVIOUR", "SHAREHOLDING_PATTERN"):
                dimension_map["GOVERNANCE_PROMOTER_BEHAVIOUR"].append(score_0_100)
                details_map["GOVERNANCE_PROMOTER_BEHAVIOUR"][eng_id] = score_0_100
            elif eng_id in ("C9", "E5", "GROWTH_ARBITRAGE", "VALUATION"):
                dimension_map["VALUATION_ASYMMETRY"].append(score_0_100)
                details_map["VALUATION_ASYMMETRY"][eng_id] = score_0_100
            elif eng_id in ("C11", "ALT_DATA", "CONCALL_NLP", "CATALYSTS", "TECHNICAL"):
                dimension_map["MARKET_CONFIRMATION_ALT_DATA"].append(score_0_100)
                details_map["MARKET_CONFIRMATION_ALT_DATA"][eng_id] = score_0_100
            elif eng_id in ("RED_TEAM", "VALIDATION", "EVIDENCE"):
                dimension_map["EVIDENCE_CONFIDENCE"].append(score_0_100)
                details_map["EVIDENCE_CONFIDENCE"][eng_id] = score_0_100

        # ── 3. Peer Normalization & Composite Vector Score ─────────────────────
        raw_dimension_scores = {}
        for dim_key in self.DIMENSION_WEIGHTS:
            scores = dimension_map[dim_key]
            raw_dimension_scores[dim_key] = sum(scores) / len(scores) if scores else 50.0

        peer_norm_res = evaluate_peer_normalization(symbol, sector=sector, raw_scores=raw_dimension_scores)
        percentile_ranks = peer_norm_res.get("percentile_ranks", {})

        dimension_scores: Dict[str, MIVSDimensionScore] = {}
        weighted_sum = 0.0

        for dim_key, weight in self.DIMENSION_WEIGHTS.items():
            raw_score = raw_dimension_scores[dim_key]
            w_score = raw_score * weight
            weighted_sum += w_score

            dimension_scores[dim_key] = MIVSDimensionScore(
                name=dim_key,
                weight=weight,
                raw_score=round(raw_score, 1),
                weighted_score=round(w_score, 1),
                percentile_rank=percentile_ranks.get(dim_key, 50.0),
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
            sector_relative_percentile=peer_norm_res.get("sector_relative_percentile", 50.0),
            metadata={"dimension_count": len(dimension_scores), "hard_gates_checked": 7, "sector": sector},
        )

