"""
Multi-Stage Turnaround Label Engine.

Defines target classifications distinguishing sustained fundamental turnaround
from temporary bounces, false recoveries, and relapses.
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class TurnaroundLabel(str, Enum):
    NO_RECOVERY = "NO_RECOVERY"
    TEMPORARY_RECOVERY = "TEMPORARY_RECOVERY"
    EMERGING_TURNAROUND = "EMERGING_TURNAROUND"
    SUSTAINED_TURNAROUND = "SUSTAINED_TURNAROUND"
    RECOVERY_THEN_RELAPSE = "RECOVERY_THEN_RELAPSE"


def evaluate_historical_damage(financials: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluate whether historical damage condition T0 is present.
    
    Condition T0 requires at least 2 of the following historical damage indicators:
    1. Revenue growth deterioration (YoY decline or <0% CAGR)
    2. EBITDA / OPM peak-to-trough compression (>300 bps drop)
    3. ROCE / ROIC compression (>400 bps drop from peak)
    4. Net Debt / EBITDA leverage spike (>3.0x or debt doubling)
    5. FCF / PAT cash flow deterioration
    """
    if not financials or len(financials) < 2:
        return {"damage_state": False, "damage_score": 0.0, "damage_reasons": ["Insufficient historical data"]}

    damage_points = 0
    reasons = []

    # Extract historical metrics
    revs = [f.get("revenue_inr", f.get("sales", 0.0)) for f in financials]
    opms = [f.get("opm_pct", f.get("ebitda_margin_pct", 0.0)) for f in financials]
    roces = [f.get("roce_pct", 0.0) for f in financials]
    debts = [f.get("debt_inr", f.get("total_debt", 0.0)) for f in financials]

    # 1. Revenue deterioration
    if len(revs) >= 4 and revs[-1] < revs[0]:
        damage_points += 1
        reasons.append("Historical revenue decline detected across multi-period horizon.")

    # 2. OPM compression
    peak_opm = max(opms) if opms else 0.0
    curr_opm = opms[-1] if opms else 0.0
    if peak_opm - curr_opm >= 3.0:
        damage_points += 1
        reasons.append(f"Operating margin compressed by {peak_opm - curr_opm:.1f}% from peak.")

    # 3. ROCE compression
    peak_roce = max(roces) if roces else 0.0
    curr_roce = roces[-1] if roces else 0.0
    if peak_roce - curr_roce >= 4.0:
        damage_points += 1
        reasons.append(f"ROCE compressed by {peak_roce - curr_roce:.1f}% from historical peak.")

    # 4. Debt expansion
    if len(debts) >= 2 and debts[-1] > debts[0] * 1.5 and debts[-1] > 0:
        damage_points += 1
        reasons.append("Debt levels expanded significantly during stress period.")

    damage_state = damage_points >= 2
    damage_score = min(100.0, (damage_points / 4.0) * 100.0)

    return {
        "damage_state": damage_state,
        "damage_score": damage_score,
        "damage_points": damage_points,
        "damage_reasons": reasons if reasons else ["No severe historical damage detected."]
    }


def classify_turnaround_stage(
    historical_damage: bool,
    improving_quarters: int,
    cfo_pat_ratio: float,
    relapse_flags: int
) -> TurnaroundLabel:
    """Classify company into multi-stage turnaround label based on trajectory features."""
    if not historical_damage:
        return TurnaroundLabel.NO_RECOVERY

    if improving_quarters == 0:
        return TurnaroundLabel.NO_RECOVERY

    if relapse_flags >= 2:
        return TurnaroundLabel.RECOVERY_THEN_RELAPSE

    if improving_quarters == 1:
        return TurnaroundLabel.TEMPORARY_RECOVERY

    if improving_quarters in (2, 3):
        if cfo_pat_ratio >= 0.8:
            return TurnaroundLabel.EMERGING_TURNAROUND
        return TurnaroundLabel.TEMPORARY_RECOVERY

    if improving_quarters >= 4:
        if cfo_pat_ratio >= 0.8 and relapse_flags == 0:
            return TurnaroundLabel.SUSTAINED_TURNAROUND
        elif relapse_flags >= 1:
            return TurnaroundLabel.RECOVERY_THEN_RELAPSE
        return TurnaroundLabel.EMERGING_TURNAROUND

    return TurnaroundLabel.NO_RECOVERY
