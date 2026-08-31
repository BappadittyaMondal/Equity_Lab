"""
2-Layer Turnaround Probability & Relapse Classifier Model.

Computes Layer 1 (Fundamental Recovery Probability P_Recovery),
Relapse Classifier (P_Relapse), Value Trap Risk, and Layer 2 (Stock Outperformance Probability).
"""

import math
from typing import Any, Dict


def sigmoid(x: float) -> float:
    """Standard sigmoid activation with numerical stability."""
    if x < -45.0:
        return 0.0
    if x > 45.0:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def predict_turnaround_probabilities(features: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate 2-layer calibrated probability scores."""
    if features.get("status") != "production":
        return {
            "status": "data_insufficient",
            "p_recovery": 0.0,
            "p_relapse": 0.0,
            "p_outperformance": 0.0,
            "value_trap_risk_score": 50.0,
        }

    fund_score = float(features.get("fundamental_recovery_score", 0.0))
    cash_score = float(features.get("cash_score", 0.0))
    frmr_gap = float(features.get("frmr_gap_score", 0.0))
    cfo_pat = float(features.get("cfo_to_pat", 0.0))
    opm_damage = float(features.get("opm_damage_gap", 0.0))
    improving_q = float(features.get("improving_quarters", 0.0))

    # Layer 1: Fundamental Recovery Probability P_Recovery
    # Logit calculation: fund_score baseline + improving quarters boost
    logit_recovery = (fund_score - 50.0) * 0.06 + (improving_q * 0.25) + (cash_score - 50.0) * 0.03
    p_recovery = round(sigmoid(logit_recovery), 4)

    # Relapse Classifier P_Relapse (PAT growing but CFO falling or low CFO/PAT)
    logit_relapse = (0.8 - cfo_pat) * 2.5 + (opm_damage * 0.1) - (improving_q * 0.3)
    p_relapse = round(sigmoid(logit_relapse), 4)

    # Value Trap Risk (0 - 100)
    value_trap_risk = round(min(100.0, max(0.0, (1.0 - p_recovery) * 50.0 + p_relapse * 50.0)), 2)

    # Layer 2: Stock Outperformance Probability P_Outperformance | Recovery
    # Combined with Expectation Gap (FRMR)
    logit_outperform = (p_recovery - 0.5) * 3.0 + (frmr_gap * 0.04) - (p_relapse * 1.5)
    p_outperformance = round(sigmoid(logit_outperform), 4)

    # Composite Turnaround Score (0 - 100)
    turnaround_score = round(min(100.0, max(0.0, p_recovery * 60.0 + (1.0 - p_relapse) * 20.0 + min(20.0, max(0.0, frmr_gap * 0.4)))), 2)

    return {
        "status": "production",
        "turnaround_score": turnaround_score,
        "p_recovery": p_recovery,
        "p_relapse": p_relapse,
        "p_outperformance": p_outperformance,
        "value_trap_risk_score": value_trap_risk,
        "confidence_tier": "HIGH" if p_recovery >= 0.7 else ("MEDIUM" if p_recovery >= 0.4 else "LOW"),
    }
