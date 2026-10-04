"""Phase 156 Tests — Institutional-Grade Multiplicative Pipeline Refinements.

Verifies:
  T1: Segmented MCap gates (₹150 Cr minimum, ₹15,000 Cr maximum).
  T2: Continuous Quality Multiplier Q in [0.50, 1.00].
  T3: Operating Leverage Convexity Omega in [1.0, 2.5].
  T4: Order-book conversion burn rate kappa >= 0.20 guard.
  T5: Segmented threshold tapering across Micro, Small, and Mid cap tiers.
  T6: Segment-relative headroom scaling and delivery benchmark.
  T7: Multiplicative cross-product formula calculation and power weights.
  T8: Portfolio construction sector concentration cap enforcement.
"""

import pytest
from unittest.mock import patch
from app.services.research.deadliest_combo_pipeline import (
    _check_hard_gates,
    _calculate_continuous_q,
    _calculate_operating_leverage_convexity,
    _calculate_order_book_burn_rate,
    _get_segmented_thresholds,
    _calculate_headroom_and_delivery,
    run_deadliest_combo_pipeline,
    format_pipeline_report,
    SCORING_POWERS,
)


class TestPhase156InstitutionalGates:
    """Verify Phase 156 boundary conditions and segmented hard gates."""

    def test_mcap_below_150cr_rejected(self):
        fund = {"market_cap": 140.0, "debt_to_equity": 0.05, "pledged_pct": 0.0}
        reason = _check_hard_gates(fund)
        assert reason is not None
        assert "150 Cr minimum" in reason

    def test_mcap_150cr_accepted(self):
        fund = {"market_cap": 150.0, "debt_to_equity": 0.05, "pledged_pct": 0.0}
        assert _check_hard_gates(fund) is None

    def test_mcap_15000cr_accepted(self):
        fund = {"market_cap": 15000.0, "debt_to_equity": 0.05, "pledged_pct": 0.0}
        assert _check_hard_gates(fund) is None

    def test_mcap_above_15000cr_rejected(self):
        fund = {"market_cap": 15050.0, "debt_to_equity": 0.05, "pledged_pct": 0.0}
        reason = _check_hard_gates(fund)
        assert reason is not None
        assert "15,000 Cr maximum" in reason


class TestPhase156ContinuousQualityMultiplier:
    """Verify continuous quality multiplier Q in [0.50, 1.00]."""

    def test_pristine_company_high_q(self):
        fund = {"cfo_pat": 1.3, "pledged_pct": 0.0, "debt_to_equity": 0.02}
        q = _calculate_continuous_q(fund)
        # 0.40 * 1.0 + 0.30 * 1.0 + 0.30 * (1.0 - 0.04) = 0.40 + 0.30 + 0.288 = 0.988
        assert q >= 0.95
        assert q <= 1.00

    def test_strained_company_bounded_q(self):
        fund = {"cfo_pat": 0.1, "pledged_pct": 4.5, "debt_to_equity": 0.32}
        q = _calculate_continuous_q(fund)
        assert q >= 0.50
        assert q <= 0.65

    def test_worst_case_clamped_to_floor(self):
        fund = {"cfo_pat": 0.0, "pledged_pct": 10.0, "debt_to_equity": 0.50}
        q = _calculate_continuous_q(fund)
        assert q == 0.50


class TestPhase156OperatingLeverageConvexity:
    """Verify Omega calculation in [1.0, 2.5]."""

    def test_high_operating_leverage(self):
        fund = {"pat_growth_latest": 75.0, "sales_growth_latest": 25.0}
        omega = _calculate_operating_leverage_convexity(fund)
        # 75 / 25 = 3.0 -> capped at 2.5
        assert omega == 2.5

    def test_moderate_operating_leverage(self):
        fund = {"pat_growth_latest": 30.0, "sales_growth_latest": 20.0}
        omega = _calculate_operating_leverage_convexity(fund)
        # 30 / 20 = 1.5
        assert omega == 1.5

    def test_sub_unity_floored_at_one(self):
        fund = {"pat_growth_latest": 10.0, "sales_growth_latest": 25.0}
        omega = _calculate_operating_leverage_convexity(fund)
        assert omega == 1.0


class TestPhase156OrderBookAndTapering:
    """Verify order book burn rate and segmented threshold tapering."""

    def test_order_book_burn_rate(self):
        fund_good = {"total_revenue": 400.0, "order_book": 1000.0}
        kappa = _calculate_order_book_burn_rate(fund_good)
        assert kappa == 0.40
        assert kappa >= 0.20

        fund_slow = {"total_revenue": 100.0, "order_book": 1000.0}
        kappa_slow = _calculate_order_book_burn_rate(fund_slow)
        assert kappa_slow == 0.10
        assert kappa_slow < 0.20

    def test_segmented_threshold_tapering(self):
        micro = _get_segmented_thresholds(800.0)
        assert micro["tier"] == "MICRO"
        assert micro["cwip_pct_min"] == 15.0
        assert micro["inc_roic_min"] == 22.0

        small = _get_segmented_thresholds(3500.0)
        assert small["tier"] == "SMALL"
        assert small["cwip_pct_min"] == 12.0
        assert small["inc_roic_min"] == 20.0

        mid = _get_segmented_thresholds(11000.0)
        assert mid["tier"] == "MID"
        assert mid["cwip_pct_min"] == 8.0
        assert mid["inc_roic_min"] == 16.0

    def test_headroom_and_delivery(self):
        res_5pct = _calculate_headroom_and_delivery({"price_band_pct": 5.0})
        assert res_5pct["headroom_cap_pct"] == 3.0  # min(3.0, 0.75 * 5.0) = 3.0

        res_2pct = _calculate_headroom_and_delivery({"price_band_pct": 2.0})
        assert res_2pct["headroom_cap_pct"] == 1.5  # min(3.0, 0.75 * 2.0) = 1.5


class TestPhase156MultiplicativePipelineAndPortfolio:
    """Verify multiplicative scoring execution and portfolio concentration constraints."""

    @patch("app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher.fetch_and_store")
    def test_portfolio_sector_concentration_cap(self, mock_fetch):
        # 4 stocks: 3 in POWER sector, 1 in PHARMA
        s_p1 = {
            "symbol": "PWR1.NS", "company_name": "Power 1 Ltd", "sector": "POWER",
            "market_cap": 2000.0, "current_price": 100.0, "high_52w": 110.0, "low_52w": 60.0,
            "debt_to_equity": 0.05, "pledged_pct": 0.0, "cfo_pat": 1.2, "roce_annualized": 30.0,
            "net_profit_last_year": 100.0, "pat_growth_latest": 40.0, "sales_growth_latest": 20.0,
            "pat_quality_flag": "OPERATING", "shares_count": 10000000, "shares_count_10yr_back": 10000000,
        }
        s_p2 = {
            "symbol": "PWR2.NS", "company_name": "Power 2 Ltd", "sector": "POWER",
            "market_cap": 2500.0, "current_price": 200.0, "high_52w": 220.0, "low_52w": 120.0,
            "debt_to_equity": 0.10, "pledged_pct": 0.0, "cfo_pat": 1.1, "roce_annualized": 28.0,
            "net_profit_last_year": 120.0, "pat_growth_latest": 35.0, "sales_growth_latest": 18.0,
            "pat_quality_flag": "OPERATING", "shares_count": 10000000, "shares_count_10yr_back": 10000000,
        }
        s_p3 = {
            "symbol": "PWR3.NS", "company_name": "Power 3 Ltd", "sector": "POWER",
            "market_cap": 3000.0, "current_price": 150.0, "high_52w": 160.0, "low_52w": 90.0,
            "debt_to_equity": 0.12, "pledged_pct": 0.0, "cfo_pat": 1.0, "roce_annualized": 26.0,
            "net_profit_last_year": 130.0, "pat_growth_latest": 30.0, "sales_growth_latest": 15.0,
            "pat_quality_flag": "OPERATING", "shares_count": 10000000, "shares_count_10yr_back": 10000000,
        }
        s_ph1 = {
            "symbol": "PHAR1.NS", "company_name": "Pharma 1 Ltd", "sector": "PHARMA",
            "market_cap": 4000.0, "current_price": 300.0, "high_52w": 320.0, "low_52w": 180.0,
            "debt_to_equity": 0.08, "pledged_pct": 0.0, "cfo_pat": 1.15, "roce_annualized": 25.0,
            "net_profit_last_year": 140.0, "pat_growth_latest": 28.0, "sales_growth_latest": 16.0,
            "pat_quality_flag": "OPERATING", "shares_count": 10000000, "shares_count_10yr_back": 10000000,
        }

        mock_fetch.side_effect = lambda sym: {
            "PWR1.NS": s_p1, "PWR2.NS": s_p2, "PWR3.NS": s_p3, "PHAR1.NS": s_ph1
        }.get(sym)

        # Enforce max sector concentration: 30% of top 3 is ~1 per sector
        results = run_deadliest_combo_pipeline(
            ["PWR1.NS", "PWR2.NS", "PWR3.NS", "PHAR1.NS"],
            top_n=3,
            enforce_portfolio_constraints=True,
            max_sector_exposure=0.30,
        )

        assert len(results) == 3
        # First 2 should contain diversified sectors (e.g. POWER and PHARMA represented)
        sectors_in_top2 = {results[0].sector, results[1].sector}
        assert "PHARMA" in sectors_in_top2
        assert "POWER" in sectors_in_top2

        # Verify multiplicative breakdown fields
        r0 = results[0]
        assert "continuous_q" in r0.breakdown
        assert "operating_leverage_convexity_omega" in r0.breakdown
        assert "segmented_tier" in r0.breakdown
        assert r0.breakdown["scoring_model"] == "multiplicative_cross_product_v2"
        assert r0.breakdown["powers"] == SCORING_POWERS
