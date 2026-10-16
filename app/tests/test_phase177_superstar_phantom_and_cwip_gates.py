"""Phase 177 Unit & Integration Certification Test Suite.

Verifies:
1. SelfLearningEngine.record_empirical_rule preserves target_symbol in bayesian_prior_modifier.
2. SelfLearningEngine.record_superstar_exit registers 1-step certified exit rules into dynamic memory.
3. Stage 0 Dynamic Memory Recall in deadliest_combo_pipeline intercepts target_symbol correctly.
4. detect_phantom_superstar_status identifies exited/sub-1% superstars and prevents narrative traps.
5. _calculate_operating_leverage_convexity rewards CWIP/Net Block >= 25% capacity expansion without breaching 2.50 ceiling.
"""

import pytest
from app.services.research.self_learning_engine import SelfLearningEngine
from app.services.strategies.shareholding_pattern import (
    detect_phantom_superstar_status,
    match_smart_money_entity,
    TRACKED_SMART_MONEY_PATTERNS,
)
from app.services.research.deadliest_combo_pipeline import (
    _calculate_operating_leverage_convexity,
    run_deadliest_combo_pipeline,
)


def test_record_empirical_rule_preserves_target_symbol():
    """Verify target_symbol is cleanly stored in bayesian_prior_modifier."""
    sle = SelfLearningEngine()
    ent = sle.record_empirical_rule(
        rule_name="TEST_EMPIRICAL_TARGET_RULE",
        category="HARD_GATE_DISQUALIFICATION",
        confidence=0.90,
        logic_statement="Test rule for target symbol preservation",
        target_symbol="TESTXYZ.NS",
    )
    assert ent.bayesian_prior_modifier.get("target_symbol") == "TESTXYZ"
    
    # Query back
    priors = sle.query_learned_priors(category="HARD_GATE_DISQUALIFICATION")
    matched = [p for p in priors if p.get("bayesian_prior_modifier", {}).get("target_symbol") == "TESTXYZ"]
    assert len(matched) >= 1
    assert matched[0]["canonical_name"] == "TEST_EMPIRICAL_TARGET_RULE"


def test_record_superstar_exit_registers_in_dynamic_memory():
    """Verify 1-step conversational superstar exit helper."""
    sle = SelfLearningEngine()
    ent = sle.record_superstar_exit(
        symbol="RAGHAV",
        superstar_name="Rekha Jhunjhunwala",
        exit_quarter="Q4 FY25",
        reason="Stake trimmed below 1.0% SEBI disclosure threshold",
    )
    assert ent.category == "HARD_GATE_DISQUALIFICATION"
    assert ent.confidence_score == 0.95
    assert ent.verification_status == "CERTIFIED_FACT"
    assert ent.bayesian_prior_modifier.get("target_symbol") == "RAGHAV"
    assert ent.bayesian_prior_modifier.get("superstar") == "Rekha Jhunjhunwala"
    assert "Q4 FY25" in ent.description


def test_stage0_dynamic_memory_recall_intercepts_target_symbol():
    """Verify Stage 0 pipeline recall halts candidate when target_symbol rule exists."""
    sle = SelfLearningEngine()
    sle.record_empirical_rule(
        rule_name="DISQUALIFY_STAGE0_TARGET_STOCK",
        category="HARD_GATE_DISQUALIFICATION",
        confidence=0.95,
        logic_statement="Simulated fraudulent accounting veto",
        target_symbol="STAGE0BAD",
    )

    results = run_deadliest_combo_pipeline(["STAGE0BAD"], fetch_live=False)
    assert len(results) == 0  # Disqualified, not returned in passed list


def test_detect_phantom_superstar_status_with_historical_exit():
    """Verify detection when superstar is present historically but missing from current filings."""
    historical = [
        {"holder_name": "Ashish Kacholia", "holding_pct": 2.02, "quarter": "Dec 2022"},
        {"holder_name": "Mukul Mahavir Agrawal", "holding_pct": 1.55, "quarter": "Dec 2022"},
    ]
    current = [
        {"holder_name": "General Public Retail", "holding_pct": 0.50},
    ]

    res = detect_phantom_superstar_status(
        symbol="RAGHAV",
        current_holders=current,
        historical_holders=historical,
    )
    assert res["is_phantom_detected"] is True
    assert res["phantom_superstars_count"] == 2
    assert res["conviction_haircut_pts"] == 25.0
    assert res["verdict_label"] == "PHANTOM_EXIT_DISTRIBUTION_TRAP"
    
    entities = [e["superstar_entity"] for e in res["exited_superstars"]]
    assert "ASHISH_KACHOLIA" in entities
    assert "MUKUL_AGRAWAL" in entities


def test_detect_phantom_superstar_status_queried_superstar_absent():
    """Verify detection when user queries a superstar who does not hold >= 1%."""
    current = [
        {"holder_name": "Unrelated Individual", "holding_pct": 1.50},
    ]

    res = detect_phantom_superstar_status(
        symbol="NAZARA",
        current_holders=current,
        queried_superstar="Rekha Jhunjhunwala",
    )
    assert res["is_phantom_detected"] is True
    assert res["verdict_label"] == "PHANTOM_EXIT_DISTRIBUTION_TRAP"
    assert res["exited_superstars"][0]["superstar_entity"] == "REKHA_JHUNJHUNWALA"


def test_detect_phantom_superstar_status_active_cluster():
    """Verify detection when 2+ superstars are verified active >= 1.0%."""
    current = [
        {"holder_name": "Ashish Kacholia", "holding_pct": 1.83},
        {"holder_name": "Kedia Securities Pvt Ltd", "holding_pct": 1.14},
    ]

    res = detect_phantom_superstar_status(
        symbol="ADVAIT",
        current_holders=current,
    )
    assert res["is_phantom_detected"] is False
    assert res["active_superstars_count"] == 2
    assert res["conviction_haircut_pts"] == 0.0
    assert res["verdict_label"] == "HIGH_CONVICTION_ACTIVE_CLUSTER"


def test_cwip_operating_leverage_convexity_boost():
    """Verify CWIP >= 25% of Net Block boosts Omega convexity within [1.0, 2.5] bounds."""
    # Baseline without CWIP
    data_no_cwip = {
        "pat_growth_latest": 30.0,
        "sales_growth_latest": 20.0,
        "cwip": 0.0,
        "net_block": 100.0,
    }
    omega_baseline = _calculate_operating_leverage_convexity(data_no_cwip)
    assert omega_baseline == round(30.0 / 20.0, 3)  # 1.50

    # With CWIP = 50 Cr on Net Block = 100 Cr (50% expansion)
    data_with_cwip = {
        "pat_growth_latest": 30.0,
        "sales_growth_latest": 20.0,
        "cwip": 50.0,
        "net_block": 100.0,
    }
    omega_boosted = _calculate_operating_leverage_convexity(data_with_cwip)
    assert omega_boosted > omega_baseline
    assert omega_boosted <= 2.50

    # Cap test: Excessive growth + CWIP cannot exceed 2.50 ceiling
    data_extreme = {
        "pat_growth_latest": 100.0,
        "sales_growth_latest": 10.0,
        "cwip": 80.0,
        "net_block": 100.0,
    }
    omega_extreme = _calculate_operating_leverage_convexity(data_extreme)
    assert omega_extreme == 2.50
