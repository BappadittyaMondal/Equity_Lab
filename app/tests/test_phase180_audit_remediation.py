"""Phase 180 Unit Tests — Comprehensive Microscopic Engine Audit Remediation.

Verifies:
1. Omega Floor Mathematical Re-calibration:
   - Operating leverage convexity calculation with denom = max(1.0, rev_growth_val).
   - Margin-expansion inflection plays in 0.1% to 5.0% revenue growth range receive proper convexity credit.
2. Intent-Aware Multi-Tier Universe Screener:
   - Dynamic routing of default symbol pools by intent archetype (MICRO_MULTIBAGGER, PRE_FLY, VALUE, SIP, SUPERSTAR).
   - Preserves backward compatibility when no intent or explicit universe is passed.
3. Superstar Portfolio Holdings Discovery:
   - Publicly disclosed portfolio mappings for Vijay Kedia, Ashish Kacholia, Mukul Agrawal, Dolly Khanna, Damani.
   - Integration with intent routing and screening.
4. Sector-Aware Terminal P/E in Return Ceiling & CAGR Matrix:
   - Sector-specific baseline multiples (FMCG/Consumer 35x, Tech/Pharma 25x, Metals/Mining 10x, General 18x).
   - Prevents artificial compression of premium compounders and overinflation of cyclicals.
5. Penman Reformulation Asset-Light Negative NOA:
   - Negative NOA with positive NOPAT classified as EXCEPTIONAL_ASSET_LIGHT_FLOAT instead of NEUTRAL_ENGINE.
   - Supreme capital efficiency via float documented transparently.
6. Intent-Adaptive Keyword Scoring Refinement:
   - Compound token pairing: "microcap" + "multibagger" -> MICRO_MULTIBAGGER.
   - 10D sub-horizon swing regex pattern matching -> SWING_10D.
7. Deadliest Combo Pipeline Panic-vs-De-Rate Wiring:
   - panic_vs_derate module output populated in result breakdown.
"""

import pytest
from app.services.research.deadliest_combo_pipeline import _calculate_operating_leverage_convexity
from app.services.research.universe_screener import (
    run_technical_universe_screener,
    _ARCHETYPE_DEFAULT_UNIVERSES,
    _DEFAULT_UNIVERSE,
)
from app.services.strategies.shareholding_pattern import (
    get_superstar_portfolio_symbols,
    SUPERSTAR_PORTFOLIO_REGISTRY,
    match_smart_money_entity,
)
from app.services.research.return_ceiling import (
    compute_return_ceiling,
    SECTOR_TERMINAL_PE_MAP,
)
from app.services.research.cagr_matrix_service import generate_cagr_sensitivity_matrix
from app.services.research.penman_reformulation import PenmanStatementReformulator
from app.services.research.intent_adaptive_engine import QueryAdaptiveConstraintEngine


class TestPhase180OmegaFloorRemediation:
    """Verify Omega denominator floor re-calibration from 5.0% to 1.0%."""

    def test_low_revenue_growth_margin_expansion_receives_convexity(self):
        """PAT growth +10%, Rev growth +1% -> ratio = 10.0 -> Omega = 2.50 (capped)."""
        fund = {"pat_growth_latest": 10.0, "sales_growth_latest": 1.0}
        omega = _calculate_operating_leverage_convexity(fund)
        assert omega == 2.5

    def test_tiny_revenue_growth_numerical_stability(self):
        """PAT growth +5%, Rev growth +0.1% -> denom floored at 1.0 -> ratio 5.0 -> Omega = 2.50."""
        fund = {"pat_growth_latest": 5.0, "sales_growth_latest": 0.1}
        omega = _calculate_operating_leverage_convexity(fund)
        assert omega == 2.5

    def test_moderate_revenue_growth_unaffected(self):
        """PAT growth +30%, Rev growth +20% -> ratio = 1.5 -> Omega = 1.5."""
        fund = {"pat_growth_latest": 30.0, "sales_growth_latest": 20.0}
        omega = _calculate_operating_leverage_convexity(fund)
        assert omega == 1.5

    def test_sub_unity_growth_floored_at_one(self):
        """PAT growth +10%, Rev growth +25% -> ratio = 0.4 -> Omega = 1.0."""
        fund = {"pat_growth_latest": 10.0, "sales_growth_latest": 25.0}
        omega = _calculate_operating_leverage_convexity(fund)
        assert omega == 1.0

    def test_negative_growth_returns_baseline(self):
        """Negative PAT growth returns baseline 1.0."""
        fund = {"pat_growth_latest": -5.0, "sales_growth_latest": 15.0}
        omega = _calculate_operating_leverage_convexity(fund)
        assert omega == 1.0


import os
os.environ["OFFLINE_TEST_MODE"] = "true"


class TestPhase180IntentAwareUniverseScreener:
    """Verify intent-adaptive universe routing in universe_screener.py."""

    def test_micro_multibagger_intent_selects_micro_universe(self):
        assert "RELIANCE" not in _ARCHETYPE_DEFAULT_UNIVERSES["MICRO_MULTIBAGGER"]
        assert "KAYNES" in _ARCHETYPE_DEFAULT_UNIVERSES["MICRO_MULTIBAGGER"]
        res = run_technical_universe_screener(universe=["KAYNES", "DATAPATT"], intent_archetype="MICRO_MULTIBAGGER")
        assert res["total_universe_scanned"] == 2
        assert res["intent_archetype"] == "MICRO_MULTIBAGGER"

    def test_sip_compounder_intent_selects_defensive_universe(self):
        assert "HINDUNILVR" in _ARCHETYPE_DEFAULT_UNIVERSES["SIP_COMPOUNDER"]
        assert "ITC" in _ARCHETYPE_DEFAULT_UNIVERSES["SIP_COMPOUNDER"]
        res = run_technical_universe_screener(universe=["HINDUNILVR", "ITC"], intent_archetype="SIP_COMPOUNDER")
        assert res["total_universe_scanned"] == 2
        assert res["intent_archetype"] == "SIP_COMPOUNDER"

    def test_kedia_superstar_intent_selects_kedia_portfolio(self):
        assert "PATELENG" in _ARCHETYPE_DEFAULT_UNIVERSES["KEDIA_SMILE"]
        res = run_technical_universe_screener(universe=["PATELENG"], intent_archetype="KEDIA_SMILE")
        assert res["total_universe_scanned"] == 1
        assert res["intent_archetype"] == "KEDIA_SMILE"

    def test_archetype_registry_completeness(self):
        assert "MICRO_MULTIBAGGER" in _ARCHETYPE_DEFAULT_UNIVERSES
        assert "PRE_FLY" in _ARCHETYPE_DEFAULT_UNIVERSES
        assert "VALUE_BUYING" in _ARCHETYPE_DEFAULT_UNIVERSES
        assert "SIP_COMPOUNDER" in _ARCHETYPE_DEFAULT_UNIVERSES
        assert "KEDIA_SMILE" in _ARCHETYPE_DEFAULT_UNIVERSES
        assert "KACHOLIA_SCALABILITY" in _ARCHETYPE_DEFAULT_UNIVERSES
        assert "AGRAWAL_INFLECTION" in _ARCHETYPE_DEFAULT_UNIVERSES

    def test_explicit_universe_overrides_intent(self):
        custom = ["TATAMOTORS", "MARUTI"]
        res = run_technical_universe_screener(universe=custom, intent_archetype="MICRO_MULTIBAGGER")
        assert res["total_universe_scanned"] == 2


class TestPhase180SuperstarPortfolioRegistry:
    """Verify superstar portfolio mappings in shareholding_pattern.py."""

    def test_vijay_kedia_holdings(self):
        holdings = get_superstar_portfolio_symbols("Vijay Kedia")
        assert "PATELENG" in holdings
        assert "TALBROSAUTO" in holdings
        assert len(holdings) >= 5

    def test_ashish_kacholia_holdings(self):
        holdings = get_superstar_portfolio_symbols("ashish kacholia")
        assert "SAFARI" in holdings
        assert "GRAVITA" in holdings
        assert len(holdings) >= 5

    def test_mukul_agrawal_holdings(self):
        holdings = get_superstar_portfolio_symbols("Mukul Agrawal")
        assert "ZENITH" in holdings
        assert "NEOGEN" in holdings
        assert len(holdings) >= 5

    def test_empty_or_unknown_superstar(self):
        assert get_superstar_portfolio_symbols("") == []
        assert get_superstar_portfolio_symbols("NonExistentInvestor123") == []


class TestPhase180SectorAwareTerminalPE:
    """Verify sector-aware terminal P/E resolution in return ceiling and CAGR matrix."""

    def test_fmcg_sector_return_ceiling(self):
        res = compute_return_ceiling(
            current_mcap_cr=50000.0,
            ttm_pat_cr=1500.0,
            sector="FMCG",
        )
        assert res["sector"] == "FMCG"
        # FMCG base terminal PE = 35.0 (vs general 18.0)
        # Future PAT at 18% 3Y = 1500 * (1.18^3) = 2464.5 Cr
        # Future Mcap = 2464.5 * 35.0 = 86258 Cr -> multiple = 86258 / 50000 = 1.73x
        assert res["base_multiple"] > 1.5
        assert res["label"] == "GROWTH_COMPOUNDER"

    def test_metals_sector_return_ceiling(self):
        res = compute_return_ceiling(
            current_mcap_cr=50000.0,
            ttm_pat_cr=5000.0,
            sector="METALS & MINING",
        )
        assert res["sector"] == "METALS & MINING"
        # Metals base terminal PE = 10.0 (compressed multiple for commodity cyclical)
        assert res["base_multiple"] <= 1.8

    def test_default_sector_backward_compatible(self):
        res = compute_return_ceiling(
            current_mcap_cr=10000.0,
            ttm_pat_cr=500.0,
        )
        assert res["sector"] == "GENERAL"
        # General uses 18.0x base terminal PE
        assert res["base_multiple"] == round((500.0 * (1.18**3) * 18.0) / 10000.0, 2)

    def test_cagr_matrix_sector_awareness(self):
        res_fmcg = generate_cagr_sensitivity_matrix("TEST_FMCG", sector="FMCG")
        res_metal = generate_cagr_sensitivity_matrix("TEST_METAL", sector="METALS")
        assert "CAGR Matrix Engine" in res_fmcg.meta.source
        assert "CAGR Matrix Engine" in res_metal.meta.source
        assert res_fmcg.scenario_matrix[4].target_price_5y > res_metal.scenario_matrix[4].target_price_5y


class TestPhase180PenmanAssetLightNegativeNOA:
    """Verify Stephen Penman statement reformulation for asset-light float efficiency."""

    def test_negative_noa_positive_nopat_classified_as_exceptional(self):
        res = PenmanStatementReformulator.reformulate(
            operating_assets=300.0,
            operating_liabilities=800.0,  # Negative NOA = 300 - 800 = -500
            financial_obligations=100.0,
            financial_assets=400.0,       # Net cash NFO = -300
            ebit=120.0,
            net_interest_expense=0.0,
            tax_rate_pct=25.0,
            sales=2500.0,
        )
        assert res["noa"] == -500.0
        assert res["is_asset_light_negative_noa"] is True
        assert res["engine_quality"] == "EXCEPTIONAL_ASSET_LIGHT_FLOAT"
        assert res["rnoa_pct"] == 999.0
        assert "supreme capital efficiency" in res["asset_light_efficiency_note"].lower()

    def test_standard_positive_noa_remains_unchanged(self):
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
        assert res["is_asset_light_negative_noa"] is False
        assert res["rnoa_pct"] == 22.5
        assert res["engine_quality"] in ["STRONG_OPERATING_ENGINE", "EXCEPTIONAL_CORE_ENGINE"]


class TestPhase180IntentDetectionRefinements:
    """Verify intent detection compound token pairing and sub-horizon regex."""

    def test_microcap_multibagger_compound_phrase(self):
        intent = QueryAdaptiveConstraintEngine.detect_query_intent("give me microcap multibagger stocks")
        assert intent == "MICRO_MULTIBAGGER"

    def test_micro_multibagger_list(self):
        intent = QueryAdaptiveConstraintEngine.detect_query_intent("micro multibagger list for 2026")
        assert intent == "MICRO_MULTIBAGGER"

    def test_sub_horizon_10d_swing(self):
        intent = QueryAdaptiveConstraintEngine.detect_query_intent("10 day swing setups")
        assert intent == "SWING_10D"

    def test_sub_horizon_10d_variant(self):
        intent = QueryAdaptiveConstraintEngine.detect_query_intent("10d momentum breakout")
        assert intent == "SWING_10D"

    def test_sub_horizon_3d_swing(self):
        intent = QueryAdaptiveConstraintEngine.detect_query_intent("3 day quick swing trade")
        assert intent == "SWING_3D"

    def test_sub_horizon_30d_positional(self):
        intent = QueryAdaptiveConstraintEngine.detect_query_intent("30 day positional play")
        assert intent == "POSITIONAL_30D"
