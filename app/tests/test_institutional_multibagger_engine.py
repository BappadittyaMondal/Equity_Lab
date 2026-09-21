import pytest
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine


def test_institutional_multibagger_scoring_universe():
    """Verify ranking universe returns candidate scorecards, archetypes, and thesis criteria."""
    rankings = InstitutionalMultibaggerEngine.rank_universe(min_score=50.0)
    assert len(rankings) > 0

    first = rankings[0]
    assert "symbol" in first
    assert "overall_score" in first
    assert "confidence_score" in first
    assert "archetype" in first
    assert "engine_breakdown" in first
    assert "causal_chain_steps" in first
    assert "positive_drivers" in first
    assert "invalidation_criteria" in first

    # Check score ranges
    assert 50.0 <= first["overall_score"] <= 100.0
    assert 0.0 <= first["confidence_score"] <= 100.0


def test_institutional_multibagger_archetype_assignment():
    """Test evaluating individual stock profiles for proper archetype assignments."""
    test_comp = {
        "symbol": "TEST.NS",
        "company_name": "Test Multibagger Inc.",
        "market_cap": 12000.0,
        "current_price": 1500.0,
        "high_52w": 1600.0,
        "low_52w": 800.0,
        "volume": 200000,
        "vol_1w_avg": 180000,
        "vol_1y_avg": 50000,
        "roe_3yr": 22.0,
        "roe_latest": 26.0,
        "roce_3yr": 24.0,
        "roce_latest": 28.0,
        "opm_5yr": 25.0,
        "opm_latest": 32.0,
        "op_growth": 35.0,
        "pat_growth_3yr": 38.0,
        "pat_growth_latest": 42.0,
        "sales_growth_3yr": 28.0,
        "sales_growth_latest": 32.0,
        "eps_growth_3yr": 36.0,
        "eps_latest": 45.0,
        "cfo_3yr": 500.0,
        "cfo_last_year": 220.0,
        "net_profit_last_year": 180.0,
        "net_block": 800.0,
        "net_block_3yr_back": 400.0,
        "net_block_preceding_year": 650.0,
        "cwip": 200.0,
        "cwip_preceding_year": 100.0,
        "piotroski_score": 8.0,
        "promoter_holding": 55.0,
        "pledged_pct": 0.0,
        "debt_to_equity": 0.25,
        "interest_coverage": 12.0,
        "peg_ratio": 0.95
    }

    result = InstitutionalMultibaggerEngine.evaluate_company(test_comp)
    assert result["overall_score"] >= 80.0
    assert result["archetype"] in ["Early Multibagger", "Emerging Compounder", "Capex Expansion"]
    assert len(result["causal_chain_steps"]) >= 4
    assert len(result["positive_drivers"]) >= 3


def test_institutional_risk_penalty_detection():
    """Verify risk penalties trigger on high pledge or poor cash conversion."""
    risky_comp = {
        "symbol": "RISK.NS",
        "company_name": "Risky Business Ltd.",
        "market_cap": 2000.0,
        "current_price": 100.0,
        "high_52w": 200.0,
        "low_52w": 80.0,
        "volume": 50000,
        "vol_1w_avg": 40000,
        "vol_1y_avg": 30000,
        "roe_3yr": 8.0,
        "roe_latest": 6.0,
        "roce_3yr": 9.0,
        "roce_latest": 7.0,
        "opm_5yr": 12.0,
        "opm_latest": 8.0,
        "op_growth": 2.0,
        "pat_growth_3yr": 3.0,
        "pat_growth_latest": 1.0,
        "sales_growth_3yr": 4.0,
        "sales_growth_latest": 2.0,
        "eps_growth_3yr": 2.0,
        "eps_latest": 5.0,
        "cfo_3yr": 10.0,
        "cfo_last_year": 20.0,
        "net_profit_last_year": 80.0,  # CFO << PAT!
        "net_block": 100.0,
        "net_block_3yr_back": 95.0,
        "net_block_preceding_year": 98.0,
        "cwip": 10.0,
        "cwip_preceding_year": 10.0,
        "piotroski_score": 3.0,
        "promoter_holding": 30.0,
        "pledged_pct": 25.0,  # High pledge!
        "debt_to_equity": 1.8,  # High debt!
        "interest_coverage": 1.5,  # Weak coverage!
        "peg_ratio": 3.5
    }

    result = InstitutionalMultibaggerEngine.evaluate_company(risky_comp)
    assert result["engine_breakdown"]["risk_penalties"] <= -20.0
    assert result["archetype"] == "Value Trap"
    assert len(result["risk_flags"]) >= 3


def test_institutional_pledge_missing_fail_closed_in_production(monkeypatch):
    """Verify that if pledged_pct is missing when OFFLINE_TEST_MODE is false (production), gate fails closed."""
    monkeypatch.setenv("OFFLINE_TEST_MODE", "false")
    item = {
        "symbol": "PROD_AUDIT.NS",
        "company_name": "Prod Audit Corp",
        "market_cap": 5000.0,
        "current_price": 500.0,
        "debt_to_equity": 0.5,
    }
    # In production without pledged_pct: Hard gate must disqualify
    gate = InstitutionalMultibaggerEngine.evaluate_hard_risk_gate(item)
    assert not gate["passed"]
    assert any("Promoter Pledge Data Missing" in d for d in gate["disqualifications"])

    # In production without pledged_pct: Score evaluation must penalize and flag
    eval_res = InstitutionalMultibaggerEngine.evaluate_company(item)
    assert any("Promoter Pledge Data Missing" in f for f in eval_res["risk_flags"])
    assert eval_res["engine_breakdown"]["risk_penalties"] <= -15.0


def test_institutional_missing_debt_and_coverage_fail_closed_in_production(monkeypatch):
    """Verify that unobserved debt_to_equity and interest_coverage receive 0 safety score and risk penalties."""
    monkeypatch.setenv("OFFLINE_TEST_MODE", "false")
    item = {
        "symbol": "NODEBT.NS",
        "company_name": "No Debt Provided Corp",
        "market_cap": 3000.0,
        "current_price": 200.0,
        "promoter_holding": 60.0,
        "pledged_pct": 0.0,
        # debt_to_equity and interest_coverage unobserved
    }
    eval_res = InstitutionalMultibaggerEngine.evaluate_company(item)
    assert eval_res["engine_breakdown"]["balance_sheet_safety"] == 0.0
    assert any("Debt-to-Equity Data Missing/Unverified" in f for f in eval_res["risk_flags"])
    assert any("Interest Coverage Data Missing/Unverified" in f for f in eval_res["risk_flags"])
    assert eval_res["engine_breakdown"]["risk_penalties"] <= -20.0


def test_multibagger_lifecycle_stage_classification():
    """Verify classification of M0 through M4 lifecycle progression stages."""
    # M0: Incomplete data or microcap ceiling
    m0 = InstitutionalMultibaggerEngine.classify_multibagger_lifecycle_stage({"market_cap": 25.0, "data_completeness_pct": 50.0})
    assert m0["stage"] == "M0_UNVERIFIED"

    # M1: Base stabilizing (positive cash, stabilizing margins)
    m1 = InstitutionalMultibaggerEngine.classify_multibagger_lifecycle_stage({
        "market_cap": 500.0, "cfo_last_year": 50.0, "net_profit_last_year": 30.0, "data_completeness_pct": 100.0
    })
    assert m1["stage"] == "M1_BASE_STABILIZING"

    # M2: Operating inflection (CWIP / Net Block >= 25% or margin expansion)
    m2 = InstitutionalMultibaggerEngine.classify_multibagger_lifecycle_stage({
        "market_cap": 1500.0, "net_block": 200.0, "cwip": 80.0, "sales_growth_latest": 18.0, "data_completeness_pct": 100.0
    })
    assert m2["stage"] == "M2_OPERATING_INFLECTION"
    assert m2["cwip_to_block_ratio"] == 0.4

    # M3: Institutional scaling (incremental ROIC >= 22% or institutional accumulation)
    m3 = InstitutionalMultibaggerEngine.classify_multibagger_lifecycle_stage({
        "market_cap": 4000.0, "incremental_roic": 25.0, "institutional_holding": 12.0, "sales_growth_latest": 24.0, "data_completeness_pct": 100.0
    })
    assert m3["stage"] == "M3_INSTITUTIONAL_SCALING"

    # M4: Mature compounder (market_cap >= 10000 Cr, high ROIC, sales growth)
    m4 = InstitutionalMultibaggerEngine.classify_multibagger_lifecycle_stage({
        "market_cap": 25000.0, "sales_growth_latest": 15.0, "incremental_roic": 20.0, "data_completeness_pct": 100.0
    })
    assert m4["stage"] == "M4_MATURE_COMPOUNDER"


def test_multibagger_economic_feasibility_hurdles():
    """Verify 7-year 5x (25.85% CAGR) and 10x (38.92% CAGR) mathematical feasibility calculations."""
    # Healthy company at reasonable valuation
    fair_comp = {
        "symbol": "FAIR.NS",
        "current_price": 200.0,
        "eps_latest": 10.0,  # PE = 20x
        "market_cap": 3000.0
    }
    feas_fair = InstitutionalMultibaggerEngine.evaluate_multibagger_economic_feasibility(fair_comp)
    assert feas_fair["entry_pe"] == 20.0
    assert feas_fair["cagr_5x_price_pct"] == 25.85
    assert feas_fair["cagr_10x_price_pct"] == 38.95
    assert feas_fair["earnings_cagr_required_5x_pct"] == 25.85
    assert feas_fair["hurdle_status"] == "REALISTIC_HURDLE"
    assert feas_fair["is_feasible"] is True
    assert feas_fair["is_haircut_applied"] is False

    # Stretched company at extreme valuation (PE = 85x)
    extreme_comp = {
        "symbol": "EXPENSIVE.NS",
        "current_price": 850.0,
        "eps_latest": 10.0,  # PE = 85x
        "market_cap": 5000.0
    }
    feas_extreme = InstitutionalMultibaggerEngine.evaluate_multibagger_economic_feasibility(extreme_comp)
    assert feas_extreme["entry_pe"] == 85.0
    assert feas_extreme["hurdle_status"] == "EXTREME_HURDLE"
    assert feas_extreme["is_feasible"] is False
    assert feas_extreme["is_haircut_applied"] is True
    assert feas_extreme["haircut_points"] == 10.0
    assert len(feas_extreme["risk_flags"]) >= 1

    # Check that evaluate_company includes lifecycle_stage and economic_feasibility
    eval_res = InstitutionalMultibaggerEngine.evaluate_company(fair_comp)
    assert "lifecycle_stage" in eval_res
    assert "economic_feasibility" in eval_res
    assert eval_res["economic_feasibility"]["hurdle_status"] == "REALISTIC_HURDLE"


def test_multibagger_sector_tam_ceiling():
    """Verify Sector TAM Ceiling detects domestic market saturation unless export transition is active."""
    # Saturated domestic company (Rev = ₹5,000 Cr, TAM = ₹20,000 Cr -> 5x growth requires ₹25,000 Cr > 100% TAM)
    saturated_comp = {
        "symbol": "SATURATED.NS",
        "current_price": 200.0,
        "eps_latest": 10.0,  # PE = 20x
        "market_cap": 15000.0,
        "revenue_cr": 5000.0,
        "sector_tam_cr": 20000.0,
        "export_transition": False
    }
    res_sat = InstitutionalMultibaggerEngine.evaluate_multibagger_economic_feasibility(saturated_comp)
    assert res_sat["tam_ceiling_breach"] is True
    assert res_sat["is_feasible"] is False
    assert res_sat["is_haircut_applied"] is True
    assert res_sat["haircut_points"] == 10.0
    assert res_sat["hurdle_status"] == "SECTOR_TAM_CEILING_BREACH"
    assert any("Sector TAM Ceiling Breach" in flag for flag in res_sat["risk_flags"])

    # Same company with active global export transition: domestic TAM ceiling is waived
    exporting_comp = dict(saturated_comp)
    exporting_comp["export_transition"] = True
    res_exp = InstitutionalMultibaggerEngine.evaluate_multibagger_economic_feasibility(exporting_comp)
    assert res_exp["tam_ceiling_breach"] is False
    assert res_exp["is_feasible"] is True
    assert res_exp["is_haircut_applied"] is False
    assert res_exp["haircut_points"] == 0.0
    assert res_exp["hurdle_status"] == "REALISTIC_HURDLE"


def test_quarterly_invalidation_milestones():
    """Verify quarterly invalidation milestone tracker validates compounding invariants and flags thesis degradation."""
    # 1. Pristine compounder passing all 4 operational milestones
    healthy_comp = {
        "symbol": "COMPOUNDER.NS",
        "sales_growth_latest": 24.5,
        "incremental_roic": 26.0,
        "opm_latest": 28.0,
        "opm_5yr": 27.0,
        "audit_qualification": False,
        "pledged_pct": 0.0,
    }
    res_healthy = InstitutionalMultibaggerEngine.evaluate_quarterly_invalidation_milestones(healthy_comp)
    assert res_healthy["thesis_health"] == "HEALTHY_COMPOUNDING"
    assert res_healthy["is_thesis_healthy"] is True
    assert res_healthy["milestones_passed_count"] == 4
    assert len(res_healthy["breached_milestones"]) == 0

    # 2. Degraded compounder failing revenue growth, incremental ROIC, and margin stability
    degraded_comp = {
        "symbol": "DEGRADED.NS",
        "sales_growth_latest": 8.0,      # < 20%
        "incremental_roic": 14.0,        # < 22%
        "opm_latest": 15.0,              # 15.0 < 22.0 - 2.0 (breach > 200 bps)
        "opm_5yr": 22.0,
        "audit_qualification": False,
        "pledged_pct": 0.0,
    }
    res_degraded = InstitutionalMultibaggerEngine.evaluate_quarterly_invalidation_milestones(degraded_comp)
    assert res_degraded["thesis_health"] == "THESIS_DEGRADATION_ALERT"
    assert res_degraded["is_thesis_healthy"] is False
    assert res_degraded["milestones_passed_count"] == 1  # Only governance passed
    assert len(res_degraded["breached_milestones"]) == 3

    # 3. Governance breach (Auditor qualification) immediately forces THESIS_DEGRADATION_ALERT
    audit_flagged_comp = dict(healthy_comp, audit_qualification=True)
    res_audit = InstitutionalMultibaggerEngine.evaluate_quarterly_invalidation_milestones(audit_flagged_comp)
    assert res_audit["thesis_health"] == "THESIS_DEGRADATION_ALERT"
    assert res_audit["is_thesis_healthy"] is False
    assert any("Auditor qualification" in b for b in res_audit["breached_milestones"])


def test_capacity_feasibility_ratio_stress_and_mitigation():
    """Verify Capacity Feasibility Ratio (CFR) flags execution stress for massive order books lacking physical net block/CWIP."""
    # 1. Feasible company: Order book well within operational turnover
    feasible_comp = {
        "symbol": "FEASIBLE.NS",
        "unexecuted_order_book": 600.0,
        "net_block": 500.0,
        "sector_asset_turnover_benchmark": 2.0,
        "cwip": 50.0
    }
    cfr_feas = InstitutionalMultibaggerEngine.evaluate_capacity_feasibility_ratio(feasible_comp)
    assert cfr_feas["capacity_feasibility_ratio"] == 0.60
    assert cfr_feas["is_capacity_stressed"] is False
    assert cfr_feas["status"] == "CAPACITY_FEASIBLE"
    assert cfr_feas["haircut_points"] == 0.0

    # 2. Execution capacity stress: Order book is 12.5x turnover capacity with negligible CWIP (< 20%)
    stressed_comp = {
        "symbol": "PHANTOM_ORDERS.NS",
        "unexecuted_order_book": 5000.0,
        "net_block": 200.0,
        "sector_asset_turnover_benchmark": 2.0,
        "cwip": 10.0,  # CWIP / Net Block = 0.05 < 0.20
        "sales_growth_3yr": 25.0,
        "pat_growth_3yr": 30.0,
        "roce_latest": 20.0,
        "cfo_last_year": 100.0,
        "net_profit_last_year": 80.0
    }
    cfr_stress = InstitutionalMultibaggerEngine.evaluate_capacity_feasibility_ratio(stressed_comp)
    assert cfr_stress["capacity_feasibility_ratio"] == 12.50
    assert cfr_stress["is_capacity_stressed"] is True
    assert cfr_stress["status"] == "EXECUTION_CAPACITY_STRESS"
    assert cfr_stress["haircut_points"] == 10.0
    assert "EXECUTION_CAPACITY_STRESS" in cfr_stress["stress_flag"]

    # Verify integration into evaluate_company
    eval_res = InstitutionalMultibaggerEngine.evaluate_company(stressed_comp)
    assert eval_res["capacity_feasibility"]["is_capacity_stressed"] is True
    assert any("EXECUTION_CAPACITY_STRESS" in rf for rf in eval_res["risk_flags"])
    assert eval_res["is_investable"] is False

    # 3. Mitigated company: Same huge order book, but active major CWIP (CWIP / Net Block = 0.50 >= 0.20)
    mitigated_comp = dict(stressed_comp)
    mitigated_comp["cwip"] = 100.0  # 50% CWIP/Net Block underway
    cfr_mitigated = InstitutionalMultibaggerEngine.evaluate_capacity_feasibility_ratio(mitigated_comp)
    assert cfr_mitigated["capacity_feasibility_ratio"] == 12.50
    assert cfr_mitigated["is_capacity_stressed"] is False
    assert cfr_mitigated["status"] == "CAPACITY_FEASIBLE"
    assert cfr_mitigated["haircut_points"] == 0.0


def test_sector_specific_asset_turnover_matrix_and_accumulator():
    """Verify sector turnover benchmark resolution and automated order-book accumulation."""
    # 1. Defense Electronics: High IP/testing turnover benchmark (3.5x)
    defense_comp = {
        "symbol": "DEFENSE_TECH.NS",
        "sector": "DEFENSE_ELECTRONICS",
        "unexecuted_order_book": 700.0,
        "net_block": 200.0,  # Denom = 200 * 3.5 = 700 -> CFR = 1.0x
        "cwip": 10.0
    }
    cfr_def = InstitutionalMultibaggerEngine.evaluate_capacity_feasibility_ratio(defense_comp)
    assert cfr_def["sector_asset_turnover_benchmark"] == 3.5
    assert cfr_def["capacity_feasibility_ratio"] == 1.0
    assert cfr_def["is_capacity_stressed"] is False

    # 2. Civil Construction: Heavy asset-intensive turnover benchmark (1.2x)
    civil_comp = {
        "symbol": "CIVIL_INFRA.NS",
        "sector": "CIVIL_CONSTRUCTION",
        "unexecuted_order_book": 1200.0,
        "net_block": 200.0,  # Denom = 200 * 1.2 = 240 -> CFR = 5.0x > 3.5x
        "cwip": 10.0         # CWIP / Net Block = 0.05 < 0.20
    }
    cfr_civil = InstitutionalMultibaggerEngine.evaluate_capacity_feasibility_ratio(civil_comp)
    assert cfr_civil["sector_asset_turnover_benchmark"] == 1.2
    assert cfr_civil["capacity_feasibility_ratio"] == 5.0
    assert cfr_civil["is_capacity_stressed"] is True
    assert cfr_civil["status"] == "EXECUTION_CAPACITY_STRESS"

    # 3. Headless screening order-book fallback: order_wins_value_cr populated from announcements
    headless_comp = {
        "symbol": "AUTO_ACCUM.NS",
        "sector": "CAPITAL_GOODS",
        "order_wins_value_cr": 440.0,  # Auto-accumulated proxy
        "net_block": 100.0,            # Denom = 100 * 2.2 = 220 -> CFR = 2.0x <= 3.5x
        "cwip": 20.0
    }
    cfr_headless = InstitutionalMultibaggerEngine.evaluate_capacity_feasibility_ratio(headless_comp)
    assert cfr_headless["sector_asset_turnover_benchmark"] == 2.2
    assert cfr_headless["unexecuted_order_book_cr"] == 440.0
    assert cfr_headless["capacity_feasibility_ratio"] == 2.0
    assert cfr_headless["is_capacity_stressed"] is False

    # 4. Asset-light IT/Software and token boundary protection
    assert InstitutionalMultibaggerEngine.resolve_sector_asset_turnover("IT_SERVICES") == 8.0
    assert InstitutionalMultibaggerEngine.resolve_sector_asset_turnover("SOFTWARE") == 8.0
    assert InstitutionalMultibaggerEngine.resolve_sector_asset_turnover("DEFENSE") == 3.0
    assert InstitutionalMultibaggerEngine.resolve_sector_asset_turnover("DEFENSE_ELECTRONICS") == 3.5
    assert InstitutionalMultibaggerEngine.resolve_sector_asset_turnover("POWER") == 1.5
    assert InstitutionalMultibaggerEngine.resolve_sector_asset_turnover("POWER_EQUIPMENT") == 1.8
    assert InstitutionalMultibaggerEngine.resolve_sector_asset_turnover("CAPITAL_GOODS") == 2.2



# ===== Phase 35-38: Launchpad Discovery Engine Tests =====

def test_launchpad_candidate_lifecycle_stage():
    """Phase 35 (C3): Verify LAUNCHPAD_CANDIDATE stage triggers for sub-Rs.500 Cr stock
    meeting all 5 quality gates. Previously these stocks were M0_UNVERIFIED — this was
    the exact reason all 14 historical multibaggers would have been rejected at entry price."""
    # 1. Sub-Rs.500 Cr stock passing all 5 gates → must be LAUNCHPAD_CANDIDATE
    launchpad_comp = {
        "market_cap": 280.0,           # Sub-Rs.500 Cr
        "piotroski_score": 8.0,        # >= 7
        "promoter_holding": 62.0,      # >= 50%
        "pledged_pct": 0.0,            # <= 5%
        "order_book_cr": 750.0,        # OB/MCap = 750/280 = 2.68x >= 1.5x
        "cfo_last_year": 30.0,         # CFO > 0
        "opm_latest": 14.0,
        "opm_5yr": 10.0,
        "data_completeness_pct": 100.0
    }
    lc = InstitutionalMultibaggerEngine.classify_multibagger_lifecycle_stage(launchpad_comp)
    assert lc["stage"] == "LAUNCHPAD_CANDIDATE", f"Expected LAUNCHPAD_CANDIDATE, got {lc['stage']}"
    assert lc["is_launchpad_candidate"] is True
    assert lc["ob_to_mcap_ratio"] >= 1.5
    assert "launchpad" in lc["description"].lower()

    # 2. Extreme microcap < Rs.50 Cr still M0_UNVERIFIED (data reliability floor preserved)
    extreme_micro = dict(launchpad_comp, market_cap=30.0)
    lc_micro = InstitutionalMultibaggerEngine.classify_multibagger_lifecycle_stage(extreme_micro)
    assert lc_micro["stage"] == "M0_UNVERIFIED"
    assert lc_micro["is_launchpad_candidate"] is False

    # 3. Sub-Rs.500 Cr BUT failing OB:MCap gate → not launchpad (falls through to M1)
    low_ob = dict(launchpad_comp, order_book_cr=100.0)  # OB/MCap = 0.36x < 1.5x
    lc_low = InstitutionalMultibaggerEngine.classify_multibagger_lifecycle_stage(low_ob)
    assert lc_low["stage"] in ["M1_BASE_STABILIZING", "M0_UNVERIFIED"]
    assert lc_low["is_launchpad_candidate"] is False

    # 4. Sub-Rs.500 Cr BUT high pledge → not launchpad
    high_pledge = dict(launchpad_comp, pledged_pct=20.0)
    lc_pledge = InstitutionalMultibaggerEngine.classify_multibagger_lifecycle_stage(high_pledge)
    assert lc_pledge["stage"] != "LAUNCHPAD_CANDIDATE"

    # 5. Legacy M1/M2/M3/M4 stages still work correctly after Phase 35 change
    m4_comp = {"market_cap": 25000.0, "sales_growth_latest": 15.0, "incremental_roic": 20.0, "data_completeness_pct": 100.0}
    assert InstitutionalMultibaggerEngine.classify_multibagger_lifecycle_stage(m4_comp)["stage"] == "M4_MATURE_COMPOUNDER"


def test_revenue_quality_composition_tracker():
    """Phase 36 (C1): Revenue quality composition tracker detects revenue CHARACTER change.
    Tests: export shift, recurring shift, ticket size jump, gross margin proxy."""
    # 1. Strong revenue quality shift via export + gross margin
    export_shift_comp = {
        "export_revenue_pct": 28.0,
        "export_revenue_pct_prev_year": 8.0,    # +20ppt export shift
        "opm_latest": 18.0,
        "opm_5yr": 10.0,                         # +800bps gross margin
        "gross_margin_pct": 18.0,
        "gross_margin_pct_prev": 10.0
    }
    rq = InstitutionalMultibaggerEngine.evaluate_revenue_quality_composition(export_shift_comp)
    assert rq["has_revenue_quality_shift"] is True
    assert rq["revenue_quality_score"] >= 20.0
    assert rq["export_rev_delta_ppt"] == 20.0
    assert len(rq["transformation_signals"]) >= 1

    # 2. Ticket size jump (JSLL / Kovai Medical pattern)
    ticket_comp = {
        "avg_ticket_size_rs": 40000.0,
        "avg_ticket_size_rs_prev": 500.0,     # 80x ticket size jump
    }
    rq2 = InstitutionalMultibaggerEngine.evaluate_revenue_quality_composition(ticket_comp)
    assert rq2["revenue_quality_score"] >= 20.0
    assert any("Ticket" in s for s in rq2["transformation_signals"])

    # 3. No data available — fallback to OPM proxy
    no_data_comp = {"opm_latest": 15.0, "opm_5yr": 8.0}
    rq3 = InstitutionalMultibaggerEngine.evaluate_revenue_quality_composition(no_data_comp)
    assert rq3["data_available"] is False
    assert rq3["revenue_quality_score"] >= 0.0  # Graceful fallback

    # 4. No quality shift → score < 20
    flat_comp = {"opm_latest": 10.0, "opm_5yr": 10.0}
    rq4 = InstitutionalMultibaggerEngine.evaluate_revenue_quality_composition(flat_comp)
    assert rq4["has_revenue_quality_shift"] is False


def test_regulatory_discovery_lag_score():
    """Phase 37 (C2): Pre-event regulatory trigger time-lag scorer.
    Tests: undiscovered window, analyst/institutional coverage, category benchmarks."""
    # 1. Fresh RDSS scheme trigger 30 days ago (Genus Power pattern) — within 150d window
    fresh_trigger_comp = {
        "days_since_trigger": 30,
        "regulatory_category": "RDSS_SCHEME",
        "analyst_coverage_count": 1,   # Undiscovered
        "fii_dii_holding": 1.5,        # < 2% — zero institutional
    }
    lag = InstitutionalMultibaggerEngine.compute_regulatory_discovery_lag_score(fresh_trigger_comp)
    assert lag["regulatory_lag_score"] >= 60.0
    assert lag["undiscovered_alpha_probability"] >= 0.60
    assert lag["is_within_undiscovered_window"] is True
    assert lag["regulatory_category"] == "RDSS_SCHEME"

    # 2. Past window (200d, typical = 150d) — partial alpha
    past_window_comp = {
        "days_since_trigger": 200,
        "regulatory_category": "RDSS_SCHEME",
        "analyst_coverage_count": 8,
        "fii_dii_holding": 12.0,
    }
    lag2 = InstitutionalMultibaggerEngine.compute_regulatory_discovery_lag_score(past_window_comp)
    assert lag2["is_within_undiscovered_window"] is False
    assert lag2["regulatory_lag_score"] < lag["regulatory_lag_score"]

    # 3. No trigger date — score still works (zero lag contribution but coverage scores)
    no_trigger = {
        "analyst_coverage_count": 2,
        "fii_dii_holding": 3.0,
    }
    lag3 = InstitutionalMultibaggerEngine.compute_regulatory_discovery_lag_score(no_trigger)
    assert "regulatory_lag_score" in lag3
    assert lag3["lag_days_since_trigger"] == 0


def test_jaw_effect_predictor():
    """Phase 38a (I1): Jaw Effect Pre-Indicator scores the setup for OPM explosion
    BEFORE it materializes. Tests: high fixed cost ratio + OB utilization headroom."""
    # 1. Classic jaw effect setup (all 14 historical stocks pattern)
    jaw_comp = {
        "revenue_cr": 120.0,
        "order_book_cr": 480.0,          # OB = 4x revenue; implied annual = 320 Cr = 2.67x
        "opm_latest": 10.0,              # OPM 10% → estimated fixed cost ratio = 90%
        "net_profit_last_year": 12.0,
        "cfo_last_year": 15.0,
    }
    jaw = InstitutionalMultibaggerEngine.evaluate_jaw_effect_predictor(jaw_comp)
    assert jaw["jaw_effect_score"] >= 40.0
    assert jaw["has_jaw_effect_setup"] is True
    assert jaw["jaw_effect_probability"] >= 0.40
    assert len(jaw["predictor_signals"]) >= 2

    # 2. No jaw effect (low OB, moderate margins, no fixed cost leverage)
    no_jaw_comp = {
        "revenue_cr": 500.0,
        "order_book_cr": 100.0,   # OB < revenue
        "opm_latest": 22.0,       # Low fixed cost ratio (~78%)... but below 70% after calc
        "net_profit_last_year": 80.0,
        "cfo_last_year": 70.0,
    }
    jaw2 = InstitutionalMultibaggerEngine.evaluate_jaw_effect_predictor(no_jaw_comp)
    # With OPM=22%, fixed_cost_ratio=0.78 still >= 0.70 → some score
    assert "jaw_effect_score" in jaw2

    # 3. Result dict has required keys
    assert "fixed_cost_ratio_estimated" in jaw
    assert "methodology_note" in jaw


def test_launchpad_readiness_composite_score():
    """Phase 38b (I2): Composite Launchpad Readiness Score synthesizes 5 signals.
    Tests: HIGH_CONVICTION, MODERATE_CONVICTION, INSUFFICIENT_SIGNAL tiers."""
    # 1. HIGH_CONVICTION — all 5 components firing (historically maps to 14-stock launchpad pattern)
    hc_comp = {
        "market_cap": 250.0,
        "order_book_cr": 750.0,          # OB/MCap = 3.0x → Component 1: +20
        "promoter_holding": 62.0,        # >= 50% + no dilution → Component 2: +20
        "pledged_pct": 0.0,
        "recent_equity_dilution": False,
        "piotroski_score": 8.0,          # For LAUNCHPAD_CANDIDATE → Component 3: +25
        "cfo_last_year": 20.0,
        "opm_latest": 10.0,
        "opm_5yr": 8.0,
        "data_completeness_pct": 100.0,
        "revenue_cr": 100.0,             # OB = 7.5x revenue → jaw effect → Component 4
        "net_profit_last_year": 8.0,
        "export_revenue_pct": 25.0,      # Revenue quality → Component 5
        "export_revenue_pct_prev_year": 5.0,
    }
    lr = InstitutionalMultibaggerEngine.evaluate_launchpad_readiness_score(hc_comp)
    assert lr["launchpad_readiness_score"] >= 70.0, f"Expected >= 70, got {lr['launchpad_readiness_score']}"
    assert lr["conviction_tier"] == "HIGH_CONVICTION_LAUNCHPAD"
    assert "component_scores" in lr
    assert lr["component_scores"]["lifecycle_stage"]["stage"] == "LAUNCHPAD_CANDIDATE"

    # 2. INSUFFICIENT_SIGNAL — large cap, low OB, no special signals
    ins_comp = {
        "market_cap": 15000.0,
        "order_book_cr": 500.0,    # OB/MCap = 0.03x
        "promoter_holding": 25.0,
        "pledged_pct": 15.0,
    }
    lr2 = InstitutionalMultibaggerEngine.evaluate_launchpad_readiness_score(ins_comp)
    assert lr2["conviction_tier"] in ["INSUFFICIENT_SIGNAL", "EARLY_SIGNAL_WATCH"]

    # 3. Methodology note present and non-empty
    assert len(lr["methodology_note"]) > 50

    # 4. evaluate_company includes all 4 new launchpad fields
    from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine as IME
    result = IME.evaluate_company(hc_comp)
    assert "revenue_quality_composition" in result
    assert "regulatory_discovery_lag" in result
    assert "jaw_effect_predictor" in result
    assert "launchpad_readiness" in result
    assert result["lifecycle_stage"]["is_launchpad_candidate"] is True
