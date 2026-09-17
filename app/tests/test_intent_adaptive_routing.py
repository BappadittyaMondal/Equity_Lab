"""Unit tests for Query-Intent Adaptive Dynamic Parameter Routing Engine (§Master Control Plane)."""

import pytest
from app.services.research.intent_adaptive_engine import (
    QueryAdaptiveConstraintEngine,
    ARCHETYPE_WEIGHT_PROFILES
)
from app.services.research.multi_horizon_matrix_engine import MultiHorizonMatrixEngine


def test_intent_detection():
    """Verify natural language query intent detection across 6 strategic archetypes."""
    assert QueryAdaptiveConstraintEngine.detect_query_intent("Find turnaround stocks recovering from loss") == "TURNAROUND"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("Graham deep value net-net buying") == "VALUE_BUYING"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("Best SIP compounder for 10 year horizon") == "SIP_COMPOUNDER"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("10 day swing trade breakout setup") == "SWING_POSITIONAL"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("Early stage 100cr microcap multibagger runway") == "EARLY_MICROCAP"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("Compare Tata Motors vs Mahindra") == "PEER_COMPARE"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("Analyze Reliance Industries") == "GENERAL"


def test_turnaround_constraint_relaxation_and_tightening():
    """Verify that turnaround intent relaxes historical CAGR but strictly enforces cash flow inflection."""
    # 1. Genuine turnaround: negative historical CAGR, but positive cash turn and solid interest coverage
    good_turnaround = {
        "pat_growth_3yr": -15.0,
        "sales_growth_3yr": -8.0,
        "roce_latest": 6.5,
        "cfo_pat_ratio": 1.25,
        "debt_to_equity": 0.45,
        "interest_coverage": 2.8,
        "pledged_pct": 0.0,
    }
    res1 = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("TURNAROUND", good_turnaround)
    assert res1["passed"] is True
    assert len(res1["relaxed_parameters"]) > 0
    assert any("growth" in r.lower() for r in res1["relaxed_parameters"])
    assert any("interest coverage" in t.lower() for t in res1["tightened_parameters"])

    # 2. Fake turnaround: insolvent with interest coverage < 1.5x
    bad_turnaround = {
        "pat_growth_3yr": -25.0,
        "sales_growth_3yr": -12.0,
        "roce_latest": 2.0,
        "cfo_pat_ratio": -0.5,
        "debt_to_equity": 1.8,
        "interest_coverage": 0.9,
        "pledged_pct": 25.0,
    }
    res2 = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("TURNAROUND", bad_turnaround)
    assert res2["passed"] is False
    assert len(res2["vetoes"]) >= 2
    assert any("interest coverage" in v.lower() for v in res2["vetoes"])


def test_sip_compounder_constraint_relaxation_and_tightening():
    """Verify that SIP compounder intent relaxes technicals but strictly enforces ROCE and cash flow."""
    # 1. High-grade compounder
    clean_compounder = {
        "roce_latest": 27.5,
        "cfo_pat_ratio": 0.92,
        "debt_to_equity": 0.05,
        "pledged_pct": 0.0,
    }
    res1 = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SIP_COMPOUNDER", clean_compounder)
    assert res1["passed"] is True
    assert any("technical" in r.lower() for r in res1["relaxed_parameters"])
    assert any("roce" in t.lower() for t in res1["tightened_parameters"])

    # 2. Deficient cash realization compounder (accounting earnings without cash)
    weak_cash_compounder = {
        "roce_latest": 22.0,
        "cfo_pat_ratio": 0.55,  # Fails 0.80 standard
        "debt_to_equity": 0.10,
        "pledged_pct": 0.0,
    }
    res2 = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SIP_COMPOUNDER", weak_cash_compounder)
    assert res2["passed"] is False
    assert any("cfo/pat" in v.lower() for v in res2["vetoes"])


def test_multi_horizon_dso_haircut():
    """Verify that MultiHorizonMatrixEngine applies mathematical haircut when DSO is high."""
    clean_company = {
        "company_name": "Clean Compounder",
        "current_price": 1000.0,
        "market_cap": 5000.0,
        "pat_growth_3yr": 35.0,
        "sales_growth_3yr": 30.0,
        "roce_latest": 25.0,
        "cfo_pat_ratio": 0.90,
        "debt_to_equity": 0.02,
        "dso": 75.0,  # Below 120 threshold
    }
    mh_clean = MultiHorizonMatrixEngine.calculate_single_symbol_matrix("CLEAN.NS", override_data=clean_company)

    stretched_company = {
        "company_name": "Stretched Receivables Co",
        "current_price": 1000.0,
        "market_cap": 5000.0,
        "pat_growth_3yr": 35.0,
        "sales_growth_3yr": 30.0,
        "roce_latest": 25.0,
        "cfo_pat_ratio": 0.40,  # Low cash conversion
        "debt_to_equity": 0.35,
        "dso": 210.0,  # Stretched receivables > 120 days
    }
    mh_stretched = MultiHorizonMatrixEngine.calculate_single_symbol_matrix("STRETCH.NS", override_data=stretched_company)

    # Stretched company must receive mathematical CAGR penalty
    assert mh_stretched.cagr_3y_pct < mh_clean.cagr_3y_pct
    assert any("Working capital stretch" in r for r in mh_stretched.forensic_invalidation_rules)


def test_decision_query_intent_dynamic_routing():
    """Verify that arbitrate and /api/v1/decision dynamically resolve intent from free-text query."""
    from app.services.decision_brain.arbiter import Arbiter
    from fastapi.testclient import TestClient
    from app.main import app

    # 1. Direct Arbiter test with query
    arbiter = Arbiter()
    call = arbiter.arbitrate("RELIANCE", query="10 day swing breakout setup")
    assert call is not None
    assert call.symbol in ("RELIANCE", "RELIANCE.NS")
    assert call.catalyst_timing in ("1-5 Days", "1-3 Weeks")

    call_turnaround = arbiter.arbitrate("RELIANCE", query="turnaround recovery candidate")
    assert call_turnaround.catalyst_timing == "6-18 Months"

    # 2. REST API endpoint with query parameter
    client = TestClient(app)
    resp = client.get("/api/v1/decision/RELIANCE?query=find%20turnaround%20recovery")
    assert resp.status_code == 200
    data = resp.json()
    assert "verdict" in data
    assert "conviction_score" in data


def test_dynamic_parameter_strictness_surfacing_in_manifest():
    """Verify Arbiter decision_manifest explicitly surfaces dynamic_parameter_adjustments with relaxed/tightened params."""
    from app.services.decision_brain.arbiter import Arbiter
    arbiter = Arbiter()
    call = arbiter.arbitrate("RELIANCE", query="10 day swing breakout setup")
    manifest = call.decision_manifest
    assert manifest is not None
    assert "dynamic_parameter_adjustments" in manifest
    dpa = manifest["dynamic_parameter_adjustments"]
    assert dpa["intent"] == "SWING_POSITIONAL"
    assert len(dpa["relaxed_parameters"]) > 0
    assert len(dpa["tightened_parameters"]) > 0
    assert "strictness_summary" in dpa
    assert "Intent SWING_POSITIONAL" in dpa["strictness_summary"]


def test_intent_adaptive_all_archetypes_strictness_coverage():
    """Verify IntentAdaptiveEngine yields relaxed & tightened parameters across all intents and aliases."""
    from app.services.research.intent_adaptive_engine import IntentAdaptiveEngine
    mock_data = {
        "sales_growth_3yr": 12.0,
        "pat_growth_3yr": 15.0,
        "roce_latest": 22.0,
        "debt_to_equity": 0.2,
        "cfo_pat_ratio": 0.85,
        "interest_coverage": 4.5,
        "promoter_holding": 55.0,
        "pledged_pct": 0.0,
    }
    intents = ["TURNAROUND", "VALUE_BUYING", "VALUE", "SIP_COMPOUNDER", "SIP", "SWING_POSITIONAL", "SWING", "EARLY_MICROCAP", "MULTIBAGGER", "PEER_COMPARE", "GENERAL"]
    for intent in intents:
        verdict = IntentAdaptiveEngine.synthesize_intent_verdict(intent, mock_data)
        assert len(verdict["relaxed_parameters"]) > 0, f"Intent {intent} missing relaxed parameters"
        assert len(verdict["tightened_parameters"]) > 0, f"Intent {intent} missing tightened parameters"
        assert "strictness_summary" in verdict
        assert verdict["status"] in ("APPROVED", "REJECTED_INTENT_VETO")


def test_arbiter_synthesize_intent_verdict():
    """Verify Arbiter.synthesize_intent_verdict produces consolidated intent-conditioned decision."""
    from app.services.decision_brain.arbiter import Arbiter
    arbiter = Arbiter()
    res = arbiter.synthesize_intent_verdict("TCS", intent="SIP_COMPOUNDER")
    assert res["symbol"] == "TCS"
    assert res["intent"] == "SIP_COMPOUNDER"
    assert "verdict" in res
    assert "dynamic_parameter_adjustments" in res
    assert res["dynamic_parameter_adjustments"]["intent"] == "SIP_COMPOUNDER"
    assert len(res["dynamic_parameter_adjustments"]["tightened_parameters"]) > 0


def test_bfsi_subsector_branching_lending_vs_asset_light_vs_insurance():
    """Verify granular sub-sector routing under SIP_COMPOUNDER intent."""
    # 1. BFSI Asset-Light (AMC / Depository / Exchange)
    amc_data = {
        "sector": "Financial Services",
        "sub_sector": "Asset Management (AMC)",
        "roce_latest": 34.0,
        "operating_margin": 42.0,
        "debt_to_equity": 0.0,
        "pledged_pct": 0.0,
    }
    res_amc = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SIP_COMPOUNDER", amc_data)
    assert res_amc["passed"] is True
    assert any("asset-light financial platform" in r for r in res_amc["relaxed_parameters"])
    assert any("ROCE (34.0% >= 25.0%)" in t for t in res_amc["tightened_parameters"])
    assert any("Operating Margin (42.0% >= 35.0%)" in t for t in res_amc["tightened_parameters"])

    # 2. BFSI Insurance (Checks solvency ratio >= 1.50)
    insurance_data_pass = {
        "sector": "Financial Services",
        "sub_sector": "Life Insurance",
        "solvency_ratio": 1.85,
        "pledged_pct": 0.0,
    }
    res_ins = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SIP_COMPOUNDER", insurance_data_pass)
    assert res_ins["passed"] is True
    assert any("Solvency ratio (1.85 >= 1.50)" in t for t in res_ins["tightened_parameters"])

    insurance_data_fail = {
        "sector": "Financial Services",
        "sub_sector": "Life Insurance",
        "solvency_ratio": 1.20,  # Below 1.50
        "pledged_pct": 0.0,
    }
    res_ins_fail = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SIP_COMPOUNDER", insurance_data_fail)
    assert res_ins_fail["passed"] is False
    assert any("solvency ratio" in v.lower() for v in res_ins_fail["vetoes"])

    # 3. BFSI Lending (Bank with high NPA veto)
    bank_data_fail = {
        "sector": "Banking",
        "sub_sector": "Commercial Banks",
        "roe": 16.0,
        "gross_npa": 4.2,  # > 3.5% veto
        "pledged_pct": 0.0,
    }
    res_bank_fail = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SIP_COMPOUNDER", bank_data_fail)
    assert res_bank_fail["passed"] is False
    assert any("gross npa" in v.lower() for v in res_bank_fail["vetoes"])


def test_sub_horizon_swing_and_positional_routing():
    """Verify granular sub-horizon intent detection, weight profiling, and adaptive constraint logic."""
    # 1. Intent detection
    assert QueryAdaptiveConstraintEngine.detect_query_intent("3 day tactical momentum breakout") == "SWING_3D"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("30 day monthly positional trade") == "POSITIONAL_30D"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("3d quick scalp setup") == "SWING_3D"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("30d base breakout setup") == "POSITIONAL_30D"

    # 2. Weight profiles
    w_3d = QueryAdaptiveConstraintEngine.get_weight_profile("SWING_3D")
    assert w_3d["TECHNICAL"] == 0.65
    assert w_3d["VALUATION"] == 0.00

    w_10d = QueryAdaptiveConstraintEngine.get_weight_profile("SWING_10D")
    assert w_10d["TECHNICAL"] == 0.55
    assert w_10d["VALUATION"] == 0.00

    w_30d = QueryAdaptiveConstraintEngine.get_weight_profile("POSITIONAL_30D")
    assert w_30d["TECHNICAL"] == 0.45
    assert w_30d["FUNDAMENTAL"] == 0.30

    # 3. SWING_3D circuit headroom test
    pass_3d = {
        "volume_z_score": 2.8,
        "close_position": 0.82,
        "circuit_headroom": 5.2,
        "adtv_cr": 12.0
    }
    res_3d_pass = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SWING_3D", pass_3d)
    assert res_3d_pass["passed"] is True
    assert any("circuit headroom" in t.lower() for t in res_3d_pass["tightened_parameters"])

    fail_3d = {
        "volume_z_score": 2.8,
        "close_position": 0.82,
        "circuit_headroom": 1.2,  # < 3.0% headroom
        "adtv_cr": 12.0
    }
    res_3d_fail = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SWING_3D", fail_3d)
    assert res_3d_fail["passed"] is False
    assert any("circuit headroom" in v.lower() for v in res_3d_fail["vetoes"])

    # 4. SWING_10D earnings binary gap risk
    warn_10d = {
        "volume_z_score": 2.1,
        "days_to_earnings": 3  # Binary event risk within 5 sessions
    }
    res_10d = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SWING_10D", warn_10d)
    assert res_10d["passed"] is True
    assert any("earnings announcement" in w.lower() for w in res_10d["warnings"])

    # 5. POSITIONAL_30D PAT acceleration
    pass_30d = {
        "pat_growth_latest": 26.5,
        "breakout_volume_mult": 2.4
    }
    res_30d = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("POSITIONAL_30D", pass_30d)
    assert res_30d["passed"] is True
    assert any("quarterly earnings acceleration" in t.lower() for t in res_30d["tightened_parameters"])


