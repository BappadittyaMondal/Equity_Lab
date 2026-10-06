"""Unit tests for Phase 159: Interval Bounds Q Model, Stage 9 Consumer Sorting Safety, and CADR Per-Action Corporate Action Step Tests."""

import pytest
from unittest.mock import patch, MagicMock
from app.services.research.deadliest_combo_pipeline import (
    calculate_continuous_q_bounds,
    _calculate_continuous_q,
    run_deadliest_combo_pipeline,
    run_deadliest_combo_pipeline_with_audit,
    DeadliestComboResult,
)
from app.services.research.forensic_auditor import compute_cadr, CADRResult


# ─────────────────────────────────────────────────────────────────────────────
# 1. Continuous Q Interval Bounds Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestContinuousQIntervalBounds:
    """Verify Q calculation under interval bounds [Q_min, Q_max]."""

    def test_observed_cfo_produces_identical_point_and_bounds(self):
        fund = {"cfo_pat": 1.20, "pledged_pct": 0.0, "debt_to_equity": 0.02}
        q, q_min, q_max, state = calculate_continuous_q_bounds(fund)
        assert state == "OBSERVED"
        assert q == q_min == q_max
        assert q >= 0.95
        assert q <= 1.00

    def test_unobserved_cfo_produces_distinct_bounds(self):
        fund = {"cfo_pat": None, "pledged_pct": 0.0, "debt_to_equity": 0.10}
        q_eff, q_min, q_max, state = calculate_continuous_q_bounds(fund)
        assert state == "UNKNOWN"
        # q_min uses tc=0.0, q_max uses tc=1.0 -> difference must be 0.40
        assert q_max > q_min
        assert q_max - q_min == pytest.approx(0.40, abs=1e-3)
        assert q_min >= 0.50

    def test_negative_cfo_clamped_not_negative(self):
        fund = {"cfo_pat": -3.5, "pledged_pct": 0.0, "debt_to_equity": 0.10}
        q, q_min, q_max, state = calculate_continuous_q_bounds(fund)
        assert state == "OBSERVED"
        # tc must be clamped to 0.0; Q must be >= 0.50 floor
        assert q >= 0.50
        assert q == q_min == q_max

    def test_high_pledge_clamped_to_zero(self):
        fund = {"cfo_pat": 0.80, "pledged_pct": 35.0, "debt_to_equity": 0.0}
        q, q_min, q_max, state = calculate_continuous_q_bounds(fund)
        assert state == "OBSERVED"
        # tp must be clamped to 0.0 (not negative)
        # raw = 0.40 * 1.0 + 0.30 * 0.0 + 0.30 * 1.0 = 0.70
        assert q == pytest.approx(0.70, abs=1e-3)

    def test_high_de_clamped_to_zero(self):
        fund = {"cfo_pat": 0.80, "pledged_pct": 0.0, "debt_to_equity": 1.80}
        q, q_min, q_max, state = calculate_continuous_q_bounds(fund)
        assert state == "OBSERVED"
        # td must be clamped to 0.0 (not negative)
        # raw = 0.40 * 1.0 + 0.30 * 1.0 + 0.30 * 0.0 = 0.70
        assert q == pytest.approx(0.70, abs=1e-3)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Pipeline Interval Bounds & Stage 9 Safety Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestPipelineBoundsRouting:
    """Verify Deadliest Combo pipeline routing under unknown CFO and sorting safety."""

    @patch("app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher.fetch_and_store")
    def test_unobserved_cfo_q_max_deficit_fails_definitively(self, mock_fetch):
        # Stock with mediocre potential where even Q_max cannot reach 70
        mock_stock = {
            "symbol": "WEAK.NS",
            "company_name": "Weak Growth Ltd",
            "market_cap": 2500.0,
            "current_price": 100.0,
            "high_52w": 200.0,
            "low_52w": 80.0,
            "volume": 20000,
            "debt_to_equity": 0.30,
            "pledged_pct": 4.5,
            "cfo_pat": None,  # UNKNOWN
            "net_profit_last_year": 20.0,
            "shares_count": 10000000,
            "shares_count_10yr_back": 10000000,
        }
        mock_fetch.return_value = mock_stock

        results, disqualified = run_deadliest_combo_pipeline_with_audit(["WEAK.NS"], top_n=5)
        # Stock cannot pass 70 hurdle -> must be in disqualified with Q_MAX_DEFICIT
        assert len(results) == 0
        assert len(disqualified) == 1
        dq = disqualified[0]
        assert "Q_MAX_DEFICIT" in dq.disqualification_reason or "DATA_INCOMPLETE" in dq.disqualification_reason
        assert dq.cfo_state == "UNKNOWN"
        assert dq.score_range is not None

    @patch("app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher.fetch_and_store")
    def test_unobserved_cfo_straddles_marked_data_incomplete(self, mock_fetch):
        # Stock with top-tier technicals & multibagger potential where Q_max >= 70, but CFO is unknown
        mock_stock = {
            "symbol": "SOLID.NS",
            "company_name": "Solid Growth Ltd",
            "market_cap": 3000.0,
            "current_price": 500.0,
            "high_52w": 510.0,
            "low_52w": 200.0,
            "dma_50": 480.0,
            "dma_200": 350.0,
            "volume": 500000,
            "vol_1w_avg": 400000,
            "vol_1y_avg": 200000,
            "debt_to_equity": 0.05,
            "pledged_pct": 0.0,
            "roce_annualized": 32.0,
            "roe_annualized": 28.0,
            "pat_growth_latest": 65.0,
            "sales_growth_latest": 35.0,
            "cfo_pat": None,  # UNKNOWN
            "net_profit_last_year": 300.0,
            "shares_count": 10000000,
            "shares_count_10yr_back": 10000000,
        }
        mock_fetch.return_value = mock_stock

        results, disqualified = run_deadliest_combo_pipeline_with_audit(["SOLID.NS"], top_n=5)
        # Cannot be certified without cash flow -> held from ranked results
        assert len(results) == 0
        assert len(disqualified) == 1
        dq = disqualified[0]
        assert "DATA_INCOMPLETE" in dq.disqualification_reason or "Q_MAX_DEFICIT" in dq.disqualification_reason
        assert dq.cfo_state == "UNKNOWN"

    @patch("app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher.fetch_and_store")
    def test_observed_cfo_passes_and_ranks_cleanly(self, mock_fetch):
        # Pristine stock with observed cash flow
        mock_stock = {
            "symbol": "CHAMP.NS",
            "company_name": "Champion Ltd",
            "market_cap": 3000.0,
            "current_price": 500.0,
            "high_52w": 510.0,
            "low_52w": 200.0,
            "dma_50": 480.0,
            "dma_200": 350.0,
            "volume": 500000,
            "vol_1w_avg": 400000,
            "vol_1y_avg": 200000,
            "debt_to_equity": 0.02,
            "pledged_pct": 0.0,
            "roce_annualized": 35.0,
            "roe_annualized": 30.0,
            "pat_growth_latest": 70.0,
            "sales_growth_latest": 40.0,
            "cfo_pat": 1.10,  # OBSERVED
            "net_profit_last_year": 350.0,
            "shares_count": 10000000,
            "shares_count_10yr_back": 10000000,
        }
        mock_fetch.return_value = mock_stock

        results = run_deadliest_combo_pipeline(["CHAMP.NS"], top_n=5)
        assert len(results) == 1
        r = results[0]
        assert r.cfo_state == "OBSERVED"
        assert r.hard_gate_pass is True
        assert r.composite_score > 0.0


# ─────────────────────────────────────────────────────────────────────────────
# 3. CADR Per-Action Corporate Action Step Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestCADRPerActionStepTest:
    """Verify CADR per-action basis discrimination and annualized/cumulative output."""

    def test_cadr_unadjusted_series_with_step(self):
        """Pre=10M, Post=20M, Step=2.0 ≈ Factor=2.0 -> AS_REPORTED basis, 0% CADR."""
        res = compute_cadr(
            shares_latest=20_000_000,
            shares_3y_ago=10_000_000,
            split_adjustment_factor=2.0,
            series_basis="UNKNOWN",
            shares_before_action=10_000_000,
            shares_after_action=20_000_000,
        )
        assert res.severity == "CLEAN"
        assert res.cadr == pytest.approx(0.0, abs=1e-4)
        assert res.cadr_cumulative == pytest.approx(0.0, abs=1e-4)
        assert res.series_basis == "AS_REPORTED"

    def test_cadr_already_adjusted_vendor_series_with_step(self):
        """Pre=20M, Post=20M, Step=1.0 ≈ 1.0 -> VENDOR_ADJUSTED basis, factor=1.0, 0% CADR."""
        res = compute_cadr(
            shares_latest=20_000_000,
            shares_3y_ago=20_000_000,
            split_adjustment_factor=2.0,
            series_basis="UNKNOWN",
            shares_before_action=20_000_000,
            shares_after_action=20_000_000,
        )
        assert res.severity == "CLEAN"
        assert res.cadr == pytest.approx(0.0, abs=1e-4)
        assert res.cadr_cumulative == pytest.approx(0.0, abs=1e-4)
        assert res.series_basis == "VENDOR_ADJUSTED"

    def test_cadr_bonus_plus_15_percent_warrants(self):
        """1:1 bonus (Factor 2.0) + 15% genuine preferential warrants (23M shares)."""
        res = compute_cadr(
            shares_latest=23_000_000,
            shares_3y_ago=10_000_000,
            dilution_instrument_hint="warrants",
            archetype="EARLY_MICROCAP",
            split_adjustment_factor=2.0,
            series_basis="AS_REPORTED",
        )
        # Cumulative = 23M / 20M - 1 = +15.0%
        # Annualized = (1.15)^(1/3) - 1 = 4.77% p.a. (below 5% warrant ceiling)
        assert res.cadr_cumulative == pytest.approx(0.15, abs=1e-3)
        assert res.cadr_annualized == pytest.approx(0.0477, abs=1e-3)
        assert res.severity == "CLEAN"

    def test_cadr_warrant_threshold_breached_surfaces_both_metrics(self):
        """Genuine warrant dilution of 20% cumulative (>5% p.a.)."""
        res = compute_cadr(
            shares_latest=24_000_000,
            shares_3y_ago=10_000_000,
            dilution_instrument_hint="preferential warrants",
            archetype="EARLY_MICROCAP",
            split_adjustment_factor=2.0,
            series_basis="AS_REPORTED",
        )
        # Cumulative = 24M / 20M - 1 = +20.0%
        # Annualized = (1.20)^(1/3) - 1 = 6.27% p.a. (> 5% ceiling)
        assert res.severity == "TIER2_OBJECTIVE_BLOCK"
        assert res.cadr_annualized == pytest.approx(0.0627, abs=1e-3)
        assert res.cadr_cumulative == pytest.approx(0.20, abs=1e-3)
        assert "p.a." in res.flag_message
        assert "cumulative" in res.flag_message

    def test_unexplained_negative_dilution_flags_caution(self):
        """Shares decrease by 20% without buyback -> TIER3 caution."""
        res = compute_cadr(
            shares_latest=8_000_000,
            shares_3y_ago=10_000_000,
            split_adjustment_factor=1.0,
            series_basis="AS_REPORTED",
            buyback_explains=False,
        )
        assert res.severity == "TIER3_CONTEXTUAL_CAUTION"
        assert res.cadr_cumulative == pytest.approx(-0.20, abs=1e-3)
        assert "Unexplained negative dilution" in res.flag_message
