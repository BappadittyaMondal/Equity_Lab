"""Phase 164 Unit Tests — University-Level Fundamental & Capital Allocation Master Engine.

Verifies:
1. Stephen Penman Statement Reformulator:
   - Operating RNOA vs Financial Leverage decomposition: ROE = RNOA + FLEV * (RNOA - NBC).
   - Detection of Debt-Inflated ROE illusions and Negative Operating Spreads.
2. Edward Chancellor Capital Cycle Detector:
   - Capex / D&A < 0.80 indicates capital starvation & supply contraction (turnaround catalyst).
   - Capex / D&A > 2.20 detects capex glut and overinvestment risk.
3. William Thorndike Outsiders Capital Allocation Scorer:
   - Incremental ROIC (Delta NOPAT / Reinvestment) compounding scoring.
   - Dilution penalty and accretive buyback bonuses.
4. Aswath Damodaran Corporate Life Cycle Classifier:
   - Stage mapping (Startup, High Growth, Mature Growth, Cash Cow, Decline).
   - WACC and terminal growth ceiling constraints.
5. Michael Mauboussin Base Rate Filter:
   - Reverse-DCF implied growth cross-referenced against historical Indian market empirical base rates.
6. Return Ceiling Integration:
   - Seamless output of base_rate_assessment and backwards compatibility.
7. Self-Learning Knowledge Base:
   - Verification of Phase 164 candidate patterns and certified facts in registry.
"""

import pytest
from app.services.research.penman_reformulation import (
    PenmanStatementReformulator,
    ChancellorCapitalCycleDetector,
    ThorndikeCapitalAllocationScorer,
    DamodaranLifeCycleClassifier,
    MauboussinBaseRateFilter,
)
from app.services.research.return_ceiling import compute_return_ceiling
from app.services.research.self_learning_engine import SelfLearningEngine


# ----------------------------------------------------------------------
# 1. Stephen Penman Statement Reformulator Tests
# ----------------------------------------------------------------------

def test_penman_pure_operating_compounder():
    """Verify high-RNOA, zero/low-debt company is classified as exceptional core engine."""
    res = PenmanStatementReformulator.reformulate(
        operating_assets=1000.0,
        operating_liabilities=200.0,
        financial_obligations=50.0,
        financial_assets=150.0,
        ebit=240.0,
        net_interest_expense=0.0,
        tax_rate_pct=25.0,
        sales=2000.0,
    )
    # NOA = 1000 - 200 = 800
    # NFO = 50 - 150 = -100 (Net cash)
    # CSE = 800 - (-100) = 900
    # NOPAT = 240 * 0.75 = 180
    # RNOA = 180 / 800 = 22.5%
    assert res["noa"] == 800.0
    assert res["nfo"] == -100.0
    assert res["rnoa_pct"] == 22.5
    assert res["debt_inflated_roe_trap"] is False
    assert res["engine_quality"] in ["STRONG_OPERATING_ENGINE", "EXCEPTIONAL_CORE_ENGINE"]


def test_penman_debt_inflated_roe_trap():
    """Verify high reported ROE driven purely by heavy financial leverage is flagged as a trap."""
    res = PenmanStatementReformulator.reformulate(
        operating_assets=2500.0,
        operating_liabilities=500.0,
        financial_obligations=1600.0,
        financial_assets=100.0,
        ebit=180.0,
        net_interest_expense=90.0,
        tax_rate_pct=25.0,
        reported_equity=500.0,
        reported_pat=110.0,
    )
    # Reported ROE = 110 / 500 = 22.0%
    # NOA = 2000, NFO = 1500, CSE = 500
    # FLEV = 1500 / 500 = 3.0 (high leverage)
    # NOPAT = 180 * 0.75 = 135 -> RNOA = 135 / 2000 = 6.75% (< 10%)
    assert res["reported_roe_pct"] == 22.0
    assert res["rnoa_pct"] < 10.0
    assert res["flev"] >= 1.2
    assert res["debt_inflated_roe_trap"] is True
    assert res["engine_quality"] == "FINANCIAL_ENGINEERING_TRAP"
    assert "High ROE" in res["trap_reason"]


def test_penman_negative_spread_value_destruction():
    """Verify negative spread (NBC > RNOA) with leverage triggers trap warning."""
    res = PenmanStatementReformulator.reformulate(
        operating_assets=1200.0,
        operating_liabilities=200.0,
        financial_obligations=800.0,
        financial_assets=50.0,
        ebit=90.0,
        net_interest_expense=120.0,
        tax_rate_pct=25.0,
    )
    # NOA = 1000, NFO = 750, CSE = 250, FLEV = 3.0
    # NOPAT = 90 * 0.75 = 67.5 -> RNOA = 6.75%
    # NFE = 120 * 0.75 = 90 -> NBC = 90 / 750 = 12.0%
    # Spread = 6.75 - 12.0 = -5.25%
    assert res["spread_pct"] < 0
    assert res["debt_inflated_roe_trap"] is True


def test_penman_margin_and_asset_turnover_decomposition():
    """Verify DuPont-style decomposition of RNOA into Profit Margin and Asset Turnover."""
    res = PenmanStatementReformulator.reformulate(
        operating_assets=1500.0,
        operating_liabilities=500.0,
        financial_obligations=200.0,
        financial_assets=100.0,
        ebit=200.0,
        net_interest_expense=10.0,
        sales=3000.0,
    )
    # NOA = 1000, Sales = 3000 -> ATO = 3.0
    # NOPAT = 150 -> PM = 150 / 3000 = 5.0%
    # RNOA = PM * ATO = 5.0% * 3.0 = 15.0%
    assert res["asset_turnover"] == 3.0
    assert res["operating_profit_margin_pct"] == 5.0
    assert res["rnoa_pct"] == 15.0


def test_penman_graceful_fallbacks_and_zero_crash():
    """Verify engine handles zeros or negative book values cleanly without throwing exceptions."""
    res = PenmanStatementReformulator.reformulate(
        operating_assets=0.0,
        operating_liabilities=0.0,
        financial_obligations=0.0,
        financial_assets=0.0,
        ebit=0.0,
        net_interest_expense=0.0,
    )
    assert res["noa"] == 0.0
    assert res["rnoa_pct"] == 0.0
    assert res["debt_inflated_roe_trap"] is False


# ----------------------------------------------------------------------
# 2. Edward Chancellor Capital Cycle Detector Tests
# ----------------------------------------------------------------------

def test_chancellor_capital_starvation_supply_contraction():
    """Verify capex/D&A < 0.80 correctly identifies capital starvation and supply contraction."""
    res = ChancellorCapitalCycleDetector.detect_capital_cycle(
        capex_cr=35.0,
        da_cr=70.0,
        cfo_cr=45.0,
        pat_cr=20.0,
    )
    assert res["capex_to_da_ratio"] == 0.50
    assert res["capital_starvation"] is True
    assert res["capex_glut_risk"] is False
    assert res["capital_cycle_phase"] == "CAPITAL_STARVATION_SUPPLY_CONTRACTION"
    assert res["turnaround_supply_catalyst"] is True


def test_chancellor_capex_glut_overinvestment():
    """Verify capex/D&A > 2.20 flags overinvestment and future glut risk."""
    res = ChancellorCapitalCycleDetector.detect_capital_cycle(
        capex_cr=300.0,
        da_cr=90.0,
        asset_growth_pct=35.0,
        pat_cr=-10.0,
    )
    assert res["capex_to_da_ratio"] == 3.33
    assert res["capex_glut_risk"] is True
    assert res["capital_starvation"] is False
    assert res["capital_cycle_phase"] == "CAPITAL_EXPANSION_GLUT_RISK"
    assert res["asset_growth_anomaly_risk"] is True


# ----------------------------------------------------------------------
# 3. William Thorndike Capital Allocation Scorer Tests
# ----------------------------------------------------------------------

def test_thorndike_incremental_roic_outsider_excellence():
    """Verify high incremental ROIC earns OUTSIDER_EXCELLENCE rating."""
    res = ThorndikeCapitalAllocationScorer.score_capital_allocation(
        nopat_start_cr=100.0,
        nopat_end_cr=260.0,
        reinvestment_cr=400.0,
        share_dilution_cagr_pct=0.0,
        fcf_to_nopat_ratio=0.95,
        buyback_yield_pct=1.5,
    )
    # Delta NOPAT = 160 on 400 reinvestment = 40.0% incremental ROIC
    assert res["incremental_roic_pct"] == 40.0
    assert res["capital_allocation_score"] >= 85.0
    assert res["allocation_rating"] == "OUTSIDER_EXCELLENCE"
    assert res["buyback_accretion_applied"] is True


def test_thorndike_dilution_penalty_and_value_destruction():
    """Verify excessive dilution and negative incremental earnings penalize score."""
    res = ThorndikeCapitalAllocationScorer.score_capital_allocation(
        nopat_start_cr=120.0,
        nopat_end_cr=130.0,
        reinvestment_cr=500.0,
        share_dilution_cagr_pct=6.5,
        fcf_to_nopat_ratio=0.30,
        buyback_yield_pct=0.0,
    )
    # Delta NOPAT = 10 on 500 reinvestment = 2.0% incremental ROIC
    assert res["incremental_roic_pct"] == 2.0
    assert res["dilution_penalized"] is True
    assert res["capital_allocation_score"] < 50.0
    assert res["allocation_rating"] == "VALUE_DESTROYER"


# ----------------------------------------------------------------------
# 4. Aswath Damodaran Corporate Life Cycle Classifier Tests
# ----------------------------------------------------------------------

def test_damodaran_startup_early_stage():
    """Verify early stage startup classification with elevated WACC hurdle."""
    res = DamodaranLifeCycleClassifier.classify_life_cycle(
        sales_cagr_pct=45.0,
        operating_margin_pct=-12.0,
        age_years=3,
        fcf_positive=False,
    )
    assert res["life_cycle_stage"] == "STARTUP_EARLY"
    assert res["recommended_wacc_range_pct"] == [18.0, 24.0]
    assert res["primary_stage_risk"] == "HIGH_SURVIVAL_RUNWAY_RISK"


def test_damodaran_mature_cash_cow():
    """Verify mature cash cow stage with steady margins and moderate growth."""
    res = DamodaranLifeCycleClassifier.classify_life_cycle(
        sales_cagr_pct=6.0,
        operating_margin_pct=22.0,
        age_years=25,
        fcf_positive=True,
    )
    assert res["life_cycle_stage"] == "MATURE_CASH_COW"
    assert res["recommended_wacc_range_pct"] == [12.0, 14.0]
    assert res["terminal_growth_ceiling_pct"] <= 6.0


# ----------------------------------------------------------------------
# 5. Michael Mauboussin Base Rate Filter Tests
# ----------------------------------------------------------------------

def test_mauboussin_base_rate_filter_plausibility():
    """Verify empirical base rate frequency grading."""
    # 45% CAGR is statistically rare (< 1% of firms over 5 years)
    res_high = MauboussinBaseRateFilter.evaluate_growth_base_rate(implied_5y_cagr_pct=45.0)
    assert res_high["empirical_base_rate_frequency_pct"] < 1.0
    assert res_high["plausibility_grade"] == "STATISTICALLY_IMPLAUSIBLE_TRAP"
    assert res_high["base_rate_penalty_score"] >= 0.80

    # 14% CAGR is within historical median achievability (> 50%)
    res_moderate = MauboussinBaseRateFilter.evaluate_growth_base_rate(implied_5y_cagr_pct=14.0)
    assert res_moderate["empirical_base_rate_frequency_pct"] >= 50.0
    assert res_moderate["plausibility_grade"] == "HIGHLY_PLAUSIBLE"
    assert res_moderate["base_rate_penalty_score"] == 0.0


# ----------------------------------------------------------------------
# 6. Return Ceiling Integration Tests
# ----------------------------------------------------------------------

def test_return_ceiling_phase164_mauboussin_integration():
    """Verify compute_return_ceiling includes base_rate_assessment seamlessly."""
    res = compute_return_ceiling(
        current_mcap_cr=2500.0,
        ttm_pat_cr=120.0,
        sovereign_yield_pct=7.1,
    )
    assert "base_rate_assessment" in res
    assert "base_rate_plausibility_grade" in res
    assert res["base_rate_plausibility_grade"] in [
        "HIGHLY_PLAUSIBLE", "MODERATE_PLAUSIBILITY", "CHALLENGING_HIGH_GROWTH"
    ]
    # Backwards compatibility check
    assert res["multibagger_eligible"] is not None
    assert res["horizon_years"] == 3


# ----------------------------------------------------------------------
# 7. Self-Learning Knowledge Base Tests
# ----------------------------------------------------------------------

def test_self_learning_phase164_patterns_and_facts():
    """Verify candidate pattern matching and registry persistence."""
    engine = SelfLearningEngine()
    
    # 1. Penman detection
    text_penman = "Stephen Penman reformulated balance sheet and RNOA decomposition shows high FLEV debt-inflated ROE."
    gaps_penman = engine.detect_knowledge_gaps(text_penman)
    entity_ids = [g["entity_id"] for g in gaps_penman]
    assert "PENMAN_RNOA_DECOMPOSITION" in entity_ids

    # 2. Chancellor capital cycle detection
    text_chancellor = "Edward Chancellor capital cycle analysis indicates severe capex starvation and supply side consolidation."
    gaps_chancellor = engine.detect_knowledge_gaps(text_chancellor)
    assert any(g["entity_id"] == "CAPITAL_CYCLE_STARVATION" for g in gaps_chancellor)

    # 3. Mauboussin base rate detection
    text_mauboussin = "Michael Mauboussin expectations investing and base rate analysis for reverse DCF."
    gaps_mauboussin = engine.detect_knowledge_gaps(text_mauboussin)
    assert any(g["entity_id"] == "MAUBOUSSIN_BASE_RATE_PLAUSIBILITY" for g in gaps_mauboussin)

    # 4. Thorndike outsiders detection
    text_thorndike = "William Thorndike Outsiders capital allocation with high incremental ROIC and buyback accretion."
    gaps_thorndike = engine.detect_knowledge_gaps(text_thorndike)
    assert any(g["entity_id"] == "THORNDIKE_INCREMENTAL_ROIC" for g in gaps_thorndike)

    # 5. Damodaran life cycle detection
    text_damodaran = "Aswath Damodaran corporate life cycle model with cost of capital and WACC."
    gaps_damodaran = engine.detect_knowledge_gaps(text_damodaran)
    assert any(g["entity_id"] == "DAMODARAN_LIFE_CYCLE" for g in gaps_damodaran)

    # 6. Verify registered facts in registry
    reg = engine._read_registry()
    entities = reg.get("entities", {})
    for expected_id in [
        "PENMAN_RNOA_DECOMPOSITION",
        "CAPITAL_CYCLE_STARVATION",
        "MAUBOUSSIN_BASE_RATE_PLAUSIBILITY",
        "THORNDIKE_INCREMENTAL_ROIC",
        "DAMODARAN_LIFE_CYCLE",
    ]:
        assert expected_id in entities, f"Missing entity {expected_id} in registry"
        assert entities[expected_id]["verification_status"] == "CERTIFIED_FACT"
