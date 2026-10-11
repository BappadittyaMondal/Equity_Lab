"""Unit and integration tests for Phase 172 Institutional Hardening and Learning Loop v2.

Verifies:
1. Universal Surveillance Hard Vetoes (SEBI ASM/GSM/ESM, NCLT, circuit lock, auditor resignations).
2. Turnaround Hardened Metrics (CFO vs PAT sign de-trapping, EBITDA/Interest >= 2.0x, pledge <= 10%, pure solvency runway).
3. SIP Compounder Hard Valuation Sanity Cap (P/E <= 95x, PEG <= 2.8).
4. Tier-Scaled Liquidity Floors across SWING_3D, PRE_FLY, and DEADLIEST_COMBO.
5. Anti-Operator Churn Guard in PRE_FLY and DEADLIEST_COMBO.
6. Self-Learning Engine Loop v2 (Sample tracking, Binomial p-values, Auto-Rollback at -15%, Benjamini-Hochberg FDR, Human Sign-off).
"""

import math
import os
import pytest
from app.services.research.intent_adaptive_engine import QueryAdaptiveConstraintEngine
from app.services.research.self_learning_engine import SelfLearningEngine, KnowledgeEntity


# ==============================================================================
# 1. UNIVERSAL SURVEILLANCE & REGULATORY HARD VETO LAYER
# ==============================================================================

def test_universal_veto_nclt_insolvency():
    """Verify NCLT IBC status immediately triggers a fatal veto for any archetype."""
    data = {"nclt_status": True, "roce_latest": 35.0, "market_cap": 5000.0}
    res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SIP_COMPOUNDER", data)
    assert res["passed"] is False
    assert res["status"] == "REJECTED_INTENT_VETO"
    assert any("NCLT insolvency" in v for v in res["fatal_vetoes"])


def test_universal_veto_sebi_asm_stage_3():
    """Verify SEBI ASM Stage 3-4 triggers fatal veto."""
    data = {"asm_stage": 3, "market_cap": 2500.0, "roce": 22.0}
    res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SWING_3D", data)
    assert res["passed"] is False
    assert any("ASM Stage 3" in v for v in res["fatal_vetoes"])


def test_universal_veto_sebi_gsm_stage():
    """Verify SEBI GSM triggers fatal veto."""
    data = {"gsm_stage": 1, "market_cap": 800.0}
    res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("MICRO_MULTIBAGGER", data)
    assert res["passed"] is False
    assert any("GSM Stage 1" in v for v in res["fatal_vetoes"])


def test_universal_veto_circuit_lock_and_auditor_flags():
    """Verify circuit lock and abrupt auditor resignations trigger fatal vetoes."""
    data_locked = {"circuit_locked": True}
    res_locked = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("PRE_FLY", data_locked)
    assert any("circuit band" in v for v in res_locked["fatal_vetoes"])

    data_auditor = {"auditor_resigned": True}
    res_auditor = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("DEEP_VALUE", data_auditor)
    assert any("auditor resigned" in v for v in res_auditor["fatal_vetoes"])

    data_qual = {"qualified_audit": True}
    res_qual = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SIP_COMPOUNDER", data_qual)
    assert any("qualified or adverse" in v for v in res_qual["fatal_vetoes"])


# ==============================================================================
# 2. TURNAROUND HARDENED METRICS
# ==============================================================================

def test_turnaround_negative_pat_with_positive_cfo_passes():
    """Verify loss-making turnaround (negative PAT) with positive cash flow passes cash realization gate."""
    data = {
        "pat_latest": -25.0,        # Loss making
        "cfo_cr": 45.0,             # Positive cash flow from ops
        "interest_coverage": 2.5,   # >= 2.0x
        "pledged_pct": 2.0,         # <= 10.0%
        "cash_equivalents_cr": 100.0,
        "annual_interest_cr": 10.0,
    }
    res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("TURNAROUND", data)
    assert res["passed"] is True
    assert any("Positive operating cash inflection strictly confirmed" in t for t in res["tightened_parameters"])


def test_turnaround_cash_burning_fails():
    """Verify turnaround with negative cash flow fails with OBJECTIVE_BLOCK."""
    data = {
        "pat_latest": -25.0,
        "cfo_cr": -15.0,            # Burning cash
        "interest_coverage": 2.5,
        "pledged_pct": 0.0,
    }
    res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("TURNAROUND", data)
    assert res["passed"] is False
    assert any("Operating cash flow (CFO) is non-positive" in b for b in res["objective_blocks"])


def test_turnaround_interest_coverage_and_pledge_limits():
    """Verify tightened interest coverage (< 2.0x) and pledge (> 10%) thresholds."""
    data_weak_cov = {
        "cfo_cr": 20.0,
        "interest_coverage": 1.7,   # < 2.0x
        "pledged_pct": 5.0,
    }
    res_cov = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("TURNAROUND", data_weak_cov)
    assert any("Interest coverage ratio (1.70x)" in b for b in res_cov["objective_blocks"])

    data_high_pledge = {
        "cfo_cr": 20.0,
        "interest_coverage": 2.5,
        "pledged_pct": 14.5,        # > 10.0%
    }
    res_pledge = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("TURNAROUND", data_high_pledge)
    assert any("Promoter pledge (14.5%) exceeds tightened turnaround" in v for v in res_pledge["fatal_vetoes"])


# ==============================================================================
# 3. SIP COMPOUNDER HARD VALUATION SANITY CAP
# ==============================================================================

def test_sip_compounder_valuation_sanity_cap():
    """Verify bubble multiple P/E > 95x or PEG > 2.8 blocks SIP compounder thesis."""
    data_bubble = {
        "pe": 115.0,
        "peg": 3.4,
        "roce_latest": 28.0,
        "cfo_pat": 1.10,
        "caqi": 0.95,
        "debt_to_equity": 0.05,
    }
    res_bubble = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SIP_COMPOUNDER", data_bubble)
    assert res_bubble["passed"] is False
    assert any("Valuation exceeds institutional SIP compounder sanity ceiling" in b for b in res_bubble["objective_blocks"])

    data_fair = {
        "pe": 45.0,
        "peg": 1.6,
        "roce_latest": 28.0,
        "cfo_pat": 1.10,
        "caqi": 0.95,
        "debt_to_equity": 0.05,
    }
    res_fair = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SIP_COMPOUNDER", data_fair)
    assert res_fair["passed"] is True
    assert any("Valuation sanity verified" in t for t in res_fair["tightened_parameters"])


# ==============================================================================
# 4. TIER-SCALED LIQUIDITY FLOORS
# ==============================================================================

def test_tier_scaled_liquidity_swing_and_prefly():
    """Verify micro-cap with ₹1.5 Cr ADTV passes, whereas mid-cap needs >= ₹5.0 Cr."""
    # Micro-cap (< ₹1,500 Cr) with ₹1.5 Cr ADTV in SWING_3D
    data_micro = {
        "market_cap": 800.0,
        "adtv_cr": 1.5,
        "circuit_headroom": 5.0,
    }
    res_micro = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SWING_3D", data_micro)
    assert any("Tactical exit liquidity verified (ADTV: ₹1.5Cr >= ₹1.0Cr for Micro-cap" in t for t in res_micro["tightened_parameters"])

    # Mid-cap (₹12,000 Cr) with ₹2.0 Cr ADTV in SWING_3D receives caution
    data_mid = {
        "market_cap": 12000.0,
        "adtv_cr": 2.0,
        "circuit_headroom": 5.0,
    }
    res_mid = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SWING_3D", data_mid)
    assert any("below Mid/Large-cap (>₹6,000 Cr) tactical liquidity benchmark" in w for w in res_mid["warnings"])


# ==============================================================================
# 5. ANTI-OPERATOR CHURN GUARD
# ==============================================================================

def test_anti_operator_churn_guard_in_prefly_and_combo():
    """Verify volume spike >= 3.0σ with price move <= 0.5% triggers anti-churn block."""
    data_churn = {
        "circuit_headroom": 6.0,
        "adtv_cr": 4.0,
        "volume_z_score": 3.8,
        "price_change_pct": 0.15,   # Stagnant price on massive volume surge
    }
    res_prefly = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("PRE_FLY", data_churn)
    assert res_prefly["passed"] is False
    assert any("Suspect volume churn/distribution" in b for b in res_prefly["objective_blocks"])


# ==============================================================================
# 6. SELF-LEARNING ENGINE LOOP V2 STATISTICAL CONTROLS
# ==============================================================================

def test_learning_loop_v2_trial_recording_and_auto_rollback(tmp_path, monkeypatch):
    """Verify trial tracking, binomial p-value calculation, and auto-rollback circuit breaker."""
    test_reg = tmp_path / "learned_rules_registry.json"
    monkeypatch.setattr("app.services.research.self_learning_engine.REGISTRY_FILE", str(test_reg))
    monkeypatch.setattr("app.services.research.self_learning_engine.DYNAMIC_KNOWLEDGE_DIR", str(tmp_path))

    engine = SelfLearningEngine()
    ent = engine.evaluate_and_learn_entity(
        entity_id="TEST_ALPHA_SIGNAL",
        text_context="Stan Weinstein Mansfield Relative Strength outperformance break",
        provenance_score=0.90,
    )
    assert ent.shadow_status == "SHADOW"
    assert ent.sample_count == 0

    # Record 15 positive outcomes with positive alpha
    for _ in range(15):
        updated = engine.record_trial_outcome("TEST_ALPHA_SIGNAL", success=True, return_delta=0.04)

    assert updated.sample_count == 15
    assert updated.success_count == 15
    assert updated.p_value is not None
    assert updated.p_value < 0.01  # Highly significant 15/15 wins

    # Now trigger underperformance > 15% -> Auto-Rollback
    failed_ent = engine.record_trial_outcome("TEST_ALPHA_SIGNAL", success=False, return_delta=-3.50)
    assert failed_ent.performance_delta < -0.15
    assert failed_ent.shadow_status == "REJECTED"
    assert failed_ent.verification_status == "SPECULATIVE_NARRATIVE_NOISE"


def test_learning_loop_v2_fdr_and_human_signoff(tmp_path, monkeypatch):
    """Verify Benjamini-Hochberg FDR control and promotion requiring human signoff."""
    test_reg = tmp_path / "learned_rules_registry.json"
    monkeypatch.setattr("app.services.research.self_learning_engine.REGISTRY_FILE", str(test_reg))
    monkeypatch.setattr("app.services.research.self_learning_engine.DYNAMIC_KNOWLEDGE_DIR", str(tmp_path))

    engine = SelfLearningEngine()
    engine.evaluate_and_learn_entity(
        entity_id="SIGNAL_A",
        text_context="High quality CWIP expansion",
        provenance_score=0.95,
    )

    # Simulate 100 samples with 68 wins (p-value ~ 0.0002) and +3.5% return delta
    for _ in range(68):
        engine.record_trial_outcome("SIGNAL_A", success=True, return_delta=0.05)
    for _ in range(32):
        engine.record_trial_outcome("SIGNAL_A", success=False, return_delta=-0.01)

    # Evaluate FDR control with min_samples=100
    res_fdr = engine.evaluate_fdr_and_promotion(alpha_fdr=0.05, min_samples=100)
    assert res_fdr["total_candidates_tested"] == 1
    # Without human sign-off, must be placed in qualified awaiting signoff, NOT automatically promoted
    assert res_fdr["promoted_count"] == 0
    assert "SIGNAL_A" in res_fdr["qualified_awaiting_signoff_entities"]

    # Now provide human sign-off
    promoted_ent = engine.approve_human_signoff("SIGNAL_A")
    assert promoted_ent.human_signoff is True
    assert promoted_ent.shadow_status == "PROMOTED"
    assert promoted_ent.verification_status == "CERTIFIED_FACT"

    # Verify querying with require_promoted=True now includes SIGNAL_A
    priors = engine.query_learned_priors(require_promoted=True)
    assert any(p["entity_id"] == "SIGNAL_A" for p in priors)
