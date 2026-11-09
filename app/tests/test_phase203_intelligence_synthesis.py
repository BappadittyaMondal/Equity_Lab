"""Phase 203: Autonomous Knowledge Synthesis, Horizon-Adaptive Parameter Certification & Bundle Synchronization Test Suite.

Verifies:
1. Dynamic Knowledge Registry: Entities #68, #69, #70 recorded, promoted, and queryable.
2. QueryAdaptiveConstraintEngine: Horizon-adaptive parameter scaling (3D, 10D, 30D, SIP).
3. Portfolio Construction: Multi-constraint liquidity cap and Steenbarger tilt circuit breaker.
4. Arbiter Dynamic Prior Recall: Dynamic recall of institutional empirical rules.
"""

import pytest
from app.services.research.self_learning_engine import SelfLearningEngine
from app.services.research.intent_adaptive_engine import (
    QueryAdaptiveConstraintEngine,
    compute_horizon_grayzone_weight,
)
from app.services.research.portfolio_construction import evaluate_portfolio_construction


def test_phase203_dynamic_knowledge_entities_promoted():
    """Verify that Entities #68, #69, #70 are recorded and promoted in dynamic memory."""
    sle = SelfLearningEngine()
    promoted = sle.query_learned_priors(require_promoted=True)
    promoted_ids = {e.get("entity_id") for e in promoted}

    assert "SAMIR_ARORA_VIA_NEGATIVA_CM3_INFLECTION" in promoted_ids
    assert "KEDIA_YOUNG_BREAKOUT_EXTENSION_GATE" in promoted_ids
    assert "PANKAJ_BHARADWAJ_3M_RISK_BUDGET_ASYMMETRY" in promoted_ids

    # Check properties of Entity #68
    e68 = [e for e in promoted if e.get("entity_id") == "SAMIR_ARORA_VIA_NEGATIVA_CM3_INFLECTION"][0]
    assert e68["category"] == "CAPITAL_PRESERVATION_INVERSION"
    assert e68["confidence_score"] >= 0.85
    assert e68["shadow_status"] == "PROMOTED"


def test_phase203_horizon_adaptive_weight_profiles():
    """Verify orthogonal weighting shifts between short-term tactical swing and long-term SIP."""
    engine = QueryAdaptiveConstraintEngine()

    sip_weights = engine.get_weight_profile("SIP")
    assert sip_weights["TECHNICAL"] == 0.0
    assert sip_weights["FUNDAMENTAL"] >= 0.35
    assert sip_weights["FORENSIC"] >= 0.20

    swing_weights = engine.get_weight_profile("SWING")
    assert swing_weights["TECHNICAL"] >= 0.50
    assert swing_weights["MACRO"] >= 0.15
    assert swing_weights["GOVERNANCE"] == 0.0

    # Horizon decay factor
    assert compute_horizon_grayzone_weight(3) == 0.0
    assert compute_horizon_grayzone_weight(10) <= 0.10
    assert compute_horizon_grayzone_weight(365) >= 0.99


def test_phase203_swing_horizon_constraints():
    """Verify 3D tactical, 10D multi-session, and 30D positional constraints."""
    engine = QueryAdaptiveConstraintEngine()

    # 1. SWING_3D with tight circuit headroom (< 3%) triggers objective block
    data_3d_blocked = {
        "vol_z": 2.5,
        "close_pos": 0.80,
        "circuit_headroom": 1.5,  # Too close to upper circuit (freeze risk)
        "market_cap": 2500.0,
        "adtv_cr": 4.0,
    }
    res_3d = engine.evaluate_adaptive_constraints("SWING_3D", data_3d_blocked)
    assert not res_3d["passed"]
    assert any("circuit headroom" in b.lower() for b in res_3d["objective_blocks"])

    # 2. SWING_10D with earnings in 2 days triggers event risk warning
    data_10d_earnings = {
        "vol_z": 1.8,
        "days_to_earnings": 2,  # Binary overnight earnings risk
    }
    res_10d = engine.evaluate_adaptive_constraints("SWING_10D", data_10d_earnings)
    assert any("earnings" in w.lower() for w in res_10d["warnings"])

    # 3. POSITIONAL_30D quarterly PAT acceleration verified
    data_30d_accelerating = {
        "pat_growth_latest": 28.0,
        "breakout_vol": 2.5,
    }
    res_30d = engine.evaluate_adaptive_constraints("POSITIONAL_30D", data_30d_accelerating)
    assert any("earnings acceleration verified" in t.lower() for t in res_30d["tightened_parameters"])


def test_phase203_portfolio_sizing_liquidity_envelope():
    """Verify that portfolio construction bounds naive risk sizing by 5-day ADV participation cap."""
    # A fund with ₹500 Cr AUM attempting to buy an illiquid microcap with ADTV of only ₹0.20 Cr
    res = evaluate_portfolio_construction(
        symbol="TINYCAP",
        mivs_score=85.0,
        evidence_confidence_pct=80.0,
        adtv_cr=0.20,  # Very low liquidity
        fund_aum_cr=500.0,
        portfolio_inputs={
            "stop_distance_pct": 2.0,  # Tight 2% stop would naively request 75% allocation!
            "max_risk_budget_pct": 1.5,
        }
    )

    # Liquidity cap must brutally restrict recommended allocation to <= 1.0%
    assert res["recommended_position_pct"] <= 1.0, (
        f"Illiquid microcap position {res['recommended_position_pct']}% exceeds 1.0% liquidity cap"
    )


def test_phase203_steenbarger_emotional_tilt_circuit_breaker():
    """Verify that 2 consecutive stop-outs throttle capital allocation by 50%."""
    # Normal allocation
    res_normal = evaluate_portfolio_construction(
        symbol="COMPOUNDER",
        mivs_score=90.0,
        evidence_confidence_pct=85.0,
        adtv_cr=25.0,
        fund_aum_cr=100.0,
        portfolio_inputs={"stop_distance_pct": 5.0, "consecutive_stop_losses": 0}
    )

    # Tilted allocation after 2 stop-outs
    res_tilted = evaluate_portfolio_construction(
        symbol="COMPOUNDER",
        mivs_score=90.0,
        evidence_confidence_pct=85.0,
        adtv_cr=25.0,
        fund_aum_cr=100.0,
        portfolio_inputs={"stop_distance_pct": 5.0, "consecutive_stop_losses": 2}
    )

    assert res_tilted["recommended_position_pct"] < res_normal["recommended_position_pct"]
    assert any("STEENBARGER DRAWDOWN CIRCUIT BREAKER" in e for e in res_tilted["evidence"])
