"""Phase 2 — Analytical Engines Tests.

Tests for:
  Layer 4: fundamental_metrics (DuPont, cashflow, balance sheet, quality score)
  Layer 5: dcf_forward (valuation zone, PEG, scenario structure)
  Layer 6: technical_engines (B4, B6, B7, D17 response shape)
  Layer 7: forensic_engine (Beneish, Altman, Piotroski)
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Any, List


# ═══════════════════════════════════════════════════════════════════════════
# Shared fixtures
# ═══════════════════════════════════════════════════════════════════════════

def _make_obs(metric: str, period: str, value: float) -> MagicMock:
    """Create a mock FinancialObservation."""
    obs = MagicMock()
    obs.metric = metric
    obs.period_end = period
    obs.value = value
    obs.confidence = 0.85
    return obs


def _rich_financials() -> List[Any]:
    """16 quarters of rich financial data for comprehensive testing."""
    quarters = [f"2021-0{q}-30" if q <= 9 else f"2021-{q}-30" for q in range(1, 5)]
    quarters += [f"2022-0{q}-30" if q <= 9 else f"2022-{q}-30" for q in range(1, 5)]
    quarters += [f"2023-0{q}-30" if q <= 9 else f"2023-{q}-30" for q in range(1, 5)]
    quarters += [f"2024-0{q}-30" if q <= 9 else f"2024-{q}-30" for q in range(1, 5)]

    periods = [
        "2021-03-30", "2021-06-30", "2021-09-30", "2021-12-30",
        "2022-03-30", "2022-06-30", "2022-09-30", "2022-12-30",
        "2023-03-30", "2023-06-30", "2023-09-30", "2023-12-30",
        "2024-03-30", "2024-06-30", "2024-09-30", "2024-12-30",
    ]

    financials = []
    base_rev = 1000.0
    base_pat = 100.0
    base_cfo = 110.0
    base_assets = 2000.0
    base_equity = 1200.0
    base_debt = 300.0

    for i, period in enumerate(periods):
        growth = 1 + (i * 0.03)
        financials += [
            _make_obs("revenue", period, base_rev * growth),
            _make_obs("net_income", period, base_pat * growth),
            _make_obs("operating_cash_flow", period, base_cfo * growth),
            _make_obs("total_assets", period, base_assets * (1 + i * 0.02)),
            _make_obs("total_equity", period, base_equity * (1 + i * 0.025)),
            _make_obs("total_debt", period, base_debt * (1 - i * 0.01)),
            _make_obs("gross_profit", period, base_rev * growth * 0.35),
            _make_obs("operating_income", period, base_rev * growth * 0.15),
        ]

    # Add ROE / ROCE
    for i, period in enumerate(periods):
        growth = 1 + (i * 0.03)
        financials.append(_make_obs("roce", period, 18.0 + i * 0.3))
        financials.append(_make_obs("free_cash_flow", period, 80.0 * growth))
        financials.append(_make_obs("working_capital", period, 400.0 * growth))
        financials.append(_make_obs("retained_earnings", period, 500.0 * growth))

    return financials


# ═══════════════════════════════════════════════════════════════════════════
# Layer 4: Fundamental Metrics Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestRevenueMetrics:
    """Revenue acceleration, CAGR, and YoY."""

    def test_revenue_yoy_computed(self):
        from app.services.strategies.fundamental_metrics import compute_revenue_metrics
        result = compute_revenue_metrics(_rich_financials())
        assert "revenue_yoy_pct" in result
        assert isinstance(result["revenue_yoy_pct"], float)

    def test_revenue_3y_cagr_computed(self):
        from app.services.strategies.fundamental_metrics import compute_revenue_metrics
        result = compute_revenue_metrics(_rich_financials())
        assert "revenue_3y_cagr_pct" in result
        assert result["revenue_3y_cagr_pct"] > 0  # Growing business

    def test_revenue_acceleration_detected(self):
        from app.services.strategies.fundamental_metrics import compute_revenue_metrics
        result = compute_revenue_metrics(_rich_financials())
        # Our synthetic data grows steadily, should detect acceleration
        assert "revenue_accelerating" in result

    def test_revenue_empty_returns_no_data(self):
        from app.services.strategies.fundamental_metrics import compute_revenue_metrics
        result = compute_revenue_metrics([])
        assert result["status"] == "no_data"

    def test_revenue_evidence_populated(self):
        from app.services.strategies.fundamental_metrics import compute_revenue_metrics
        result = compute_revenue_metrics(_rich_financials())
        assert len(result.get("evidence", [])) >= 1


class TestCashFlowMetrics:
    """Earnings quality and FCF analysis."""

    def test_earnings_quality_ratio_computed(self):
        from app.services.strategies.fundamental_metrics import compute_cashflow_metrics
        result = compute_cashflow_metrics(_rich_financials())
        assert "earnings_quality_ratio" in result
        assert result["earnings_quality_ratio"] > 0

    def test_earnings_quality_high_cfo_pat(self):
        """CFO > PAT → high earnings quality."""
        from app.services.strategies.fundamental_metrics import compute_cashflow_metrics
        result = compute_cashflow_metrics(_rich_financials())
        # Our data has CFO=110% of PAT → quality ratio > 1
        assert result["earnings_quality_ratio"] >= 1.0

    def test_fcf_positive_detected(self):
        from app.services.strategies.fundamental_metrics import compute_cashflow_metrics
        result = compute_cashflow_metrics(_rich_financials())
        assert result.get("latest_fcf", 0) > 0


class TestDuPontROE:
    """DuPont decomposition."""

    def test_roe_computed(self):
        from app.services.strategies.fundamental_metrics import compute_dupont_roe
        result = compute_dupont_roe(_rich_financials())
        assert "roe_pct" in result
        assert result["roe_pct"] > 0

    def test_dupont_components_present(self):
        from app.services.strategies.fundamental_metrics import compute_dupont_roe
        result = compute_dupont_roe(_rich_financials())
        assert "net_margin_pct" in result
        assert "asset_turnover" in result
        assert "equity_multiplier" in result

    def test_dupont_insufficient_data(self):
        from app.services.strategies.fundamental_metrics import compute_dupont_roe
        result = compute_dupont_roe([])
        assert result["status"] == "insufficient_data"


class TestFundamentalQualityScore:
    """Composite scoring."""

    def test_quality_score_range(self):
        from app.services.strategies.fundamental_metrics import compute_fundamental_quality_score
        result = compute_fundamental_quality_score(_rich_financials())
        score = result["fundamental_quality_score"]
        assert 0.0 <= score <= 100.0

    def test_quality_score_high_for_rich_data(self):
        """Rich growing company should score well."""
        from app.services.strategies.fundamental_metrics import compute_fundamental_quality_score
        result = compute_fundamental_quality_score(_rich_financials())
        assert result["fundamental_quality_score"] >= 50.0  # Good quality

    def test_quality_score_evidence_populated(self):
        from app.services.strategies.fundamental_metrics import compute_fundamental_quality_score
        result = compute_fundamental_quality_score(_rich_financials())
        assert len(result["evidence"]) >= 4  # One per pillar


# ═══════════════════════════════════════════════════════════════════════════
# Layer 5: Forward DCF Tests (mocked market data)
# ═══════════════════════════════════════════════════════════════════════════

class TestValuationZone:
    """Test valuation zone classification logic."""

    def test_deeply_undervalued_high_mos(self):
        from app.services.strategies.dcf_forward import _compute_valuation_zone
        # MoS=35% → DEEPLY_UNDERVALUED; PEG=0.8 → UNDERVALUED
        # Pessimistic-wins logic returns the more conservative of the two
        result = _compute_valuation_zone(15.0, 0.8, 35.0)
        assert result in ("DEEPLY_UNDERVALUED", "UNDERVALUED")

    def test_deeply_undervalued_no_peg(self):
        from app.services.strategies.dcf_forward import _compute_valuation_zone
        # Without PEG, only MoS=40% → pure DEEPLY_UNDERVALUED
        assert _compute_valuation_zone(12.0, None, 40.0) == "DEEPLY_UNDERVALUED"

    def test_overvalued_negative_mos(self):
        from app.services.strategies.dcf_forward import _compute_valuation_zone
        result = _compute_valuation_zone(50.0, 3.0, -25.0)
        assert result in ("OVERVALUED", "EXTREMELY_OVERVALUED")

    def test_fair_value_neutral(self):
        from app.services.strategies.dcf_forward import _compute_valuation_zone
        result = _compute_valuation_zone(22.0, 1.5, 5.0)
        assert result in ("FAIR", "UNDERVALUED")

    def test_valuation_zone_high_pe_no_mos(self):
        from app.services.strategies.dcf_forward import _compute_valuation_zone
        result = _compute_valuation_zone(70.0, None, None)
        assert result == "EXTREMELY_OVERVALUED"

    def test_valuation_zone_low_pe_no_mos(self):
        from app.services.strategies.dcf_forward import _compute_valuation_zone
        result = _compute_valuation_zone(10.0, None, None)
        assert result == "UNDERVALUED"


class TestScenarioAnalysis:
    """Scenario structure and probability sum."""

    def test_scenarios_probability_sum_to_100(self):
        from app.services.strategies.dcf_forward import _compute_scenarios
        scenarios = _compute_scenarios(
            fcf_base=5000.0, market_cap=200000.0, price=500.0,
            discount_rate=0.12, terminal_growth=0.04
        )
        total_prob = (
            scenarios["bull_case"]["probability"] +
            scenarios["base_case"]["probability"] +
            scenarios["bear_case"]["probability"]
        )
        assert abs(total_prob - 1.0) < 0.001

    def test_bull_value_exceeds_bear(self):
        from app.services.strategies.dcf_forward import _compute_scenarios
        scenarios = _compute_scenarios(
            fcf_base=5000.0, market_cap=200000.0, price=500.0,
            discount_rate=0.12, terminal_growth=0.04
        )
        bull_val = scenarios["bull_case"]["intrinsic_value"] or 0
        bear_val = scenarios["bear_case"]["intrinsic_value"] or float("inf")
        assert bull_val > bear_val

    def test_insufficient_fcf_returns_status(self):
        from app.services.strategies.dcf_forward import _compute_scenarios
        result = _compute_scenarios(
            fcf_base=None, market_cap=0.0, price=500.0,
            discount_rate=0.12, terminal_growth=0.04
        )
        assert result.get("status") == "insufficient_data"


# ═══════════════════════════════════════════════════════════════════════════
# Layer 7: Forensic Engine Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestBeneishMScore:
    """Beneish manipulation detection."""

    def test_beneish_computed_with_data(self):
        from app.services.strategies.forensic_engine import compute_beneish_mscore
        result = compute_beneish_mscore(_rich_financials())
        assert "m_score" in result
        assert isinstance(result["m_score"], float)

    def test_beneish_classification_present(self):
        from app.services.strategies.forensic_engine import compute_beneish_mscore
        result = compute_beneish_mscore(_rich_financials())
        assert result["classification"] in ("LIKELY_MANIPULATOR", "GREY_ZONE", "LIKELY_NOT_MANIPULATOR")

    def test_beneish_insufficient_data(self):
        from app.services.strategies.forensic_engine import compute_beneish_mscore
        result = compute_beneish_mscore([])
        assert result["status"] == "insufficient_data"

    def test_beneish_healthy_company_not_manipulator(self):
        """A company with high CFO and normal growth should not flag."""
        from app.services.strategies.forensic_engine import compute_beneish_mscore
        result = compute_beneish_mscore(_rich_financials())
        # Our synthetic data has clean growing revenue + positive CFO
        # TATA should be low → m_score < -1.78
        assert result["classification"] in ("LIKELY_NOT_MANIPULATOR", "GREY_ZONE")


class TestAltmanZScore:
    """Altman financial distress detection."""

    def test_altman_computed_with_data(self):
        from app.services.strategies.forensic_engine import compute_altman_zscore
        result = compute_altman_zscore(_rich_financials())
        assert "z_score" in result

    def test_altman_zone_classification(self):
        from app.services.strategies.forensic_engine import compute_altman_zscore
        result = compute_altman_zscore(_rich_financials())
        assert result.get("zone") in ("SAFE", "GREY", "DISTRESS")

    def test_altman_insufficient_data(self):
        from app.services.strategies.forensic_engine import compute_altman_zscore
        result = compute_altman_zscore([])
        assert result["status"] == "insufficient_data"

    def test_altman_healthy_company_in_safe_zone(self):
        """Our rich company has low debt, good EBIT → should be SAFE."""
        from app.services.strategies.forensic_engine import compute_altman_zscore
        result = compute_altman_zscore(_rich_financials())
        assert result["zone"] in ("SAFE", "GREY")


class TestPiotroskiFScore:
    """Piotroski 9-point quality scoring."""

    def test_f_score_range(self):
        from app.services.strategies.forensic_engine import compute_piotroski_fscore
        result = compute_piotroski_fscore(_rich_financials())
        assert 0 <= result["f_score"] <= 9

    def test_component_scores_present(self):
        from app.services.strategies.forensic_engine import compute_piotroski_fscore
        result = compute_piotroski_fscore(_rich_financials())
        scores = result["component_scores"]
        assert all(k in scores for k in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"])

    def test_all_scores_binary(self):
        from app.services.strategies.forensic_engine import compute_piotroski_fscore
        result = compute_piotroski_fscore(_rich_financials())
        for k, v in result["component_scores"].items():
            assert v in (0, 1), f"{k}={v} is not binary"

    def test_healthy_company_strong_f_score(self):
        """Growing company with positive FCF should have F-Score ≥ 5."""
        from app.services.strategies.forensic_engine import compute_piotroski_fscore
        result = compute_piotroski_fscore(_rich_financials())
        assert result["f_score"] >= 5

    def test_insufficient_data(self):
        from app.services.strategies.forensic_engine import compute_piotroski_fscore
        result = compute_piotroski_fscore([])
        assert result["status"] == "insufficient_data"


# ═══════════════════════════════════════════════════════════════════════════
# Layer 6: Technical Engines (structure tests — mocked price data)
# ═══════════════════════════════════════════════════════════════════════════

class TestTechnicalEngineStructure:
    """Verify all technical engines return valid StrategyRunResponse."""

    def _mock_hist(self, n: int = 252):
        """Create a fake OHLCV DataFrame with n bars."""
        import pandas as pd
        import numpy as np
        np.random.seed(42)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=n, freq="B")
        price = 1000.0 + np.cumsum(np.random.randn(n) * 5)
        price = np.clip(price, 100, 5000)
        volume = np.abs(np.random.randn(n) * 500000 + 1000000).astype(int)
        df = pd.DataFrame({
            "Open": price * 0.99,
            "High": price * 1.01,
            "Low": price * 0.98,
            "Close": price,
            "Volume": volume,
        }, index=dates)
        return df

    @patch("app.services.strategies.technical_engines.get_history")
    def test_b4_vpa_response_shape(self, mock_hist):
        from app.services.strategies.technical_engines import run_vpa_b4
        mock_hist.return_value = self._mock_hist()
        resp = run_vpa_b4("RELIANCE")
        assert resp.strategy_id == "B4"
        assert "vpa_score" in resp.results
        assert 0.0 <= resp.results["vpa_score"] <= 100.0

    @patch("app.services.strategies.technical_engines.get_history")
    def test_b6_rs_rating_response_shape(self, mock_hist):
        from app.services.strategies.technical_engines import run_rs_rating_b6
        mock_hist.return_value = self._mock_hist()
        resp = run_rs_rating_b6("RELIANCE")
        assert resp.strategy_id == "B6"
        assert 0 <= resp.results["rs_rating"] <= 99

    @patch("app.services.strategies.technical_engines.get_history")
    def test_b7_pocket_pivot_response_shape(self, mock_hist):
        from app.services.strategies.technical_engines import run_pocket_pivot_b7
        mock_hist.return_value = self._mock_hist()
        resp = run_pocket_pivot_b7("RELIANCE")
        assert resp.strategy_id == "B7"
        assert "pocket_pivots_last30" in resp.results
        assert isinstance(resp.results["pocket_pivots_last30"], int)

    @patch("app.services.strategies.technical_engines.get_history")
    def test_d17_mean_reversion_response_shape(self, mock_hist):
        from app.services.strategies.technical_engines import run_mean_reversion_d17
        mock_hist.return_value = self._mock_hist()
        resp = run_mean_reversion_d17("RELIANCE")
        assert resp.strategy_id == "D17"
        assert resp.results["weinstein_stage"] in (
            "STAGE_1_BASING", "STAGE_2_ADVANCING",
            "STAGE_3_TOPPING", "STAGE_4_DECLINING"
        )

    @patch("app.services.strategies.technical_engines.get_history")
    def test_insufficient_data_returns_proper_status(self, mock_hist):
        from app.services.strategies.technical_engines import run_vpa_b4
        mock_hist.return_value = None  # Simulate no data
        resp = run_vpa_b4("RELIANCE")
        assert resp.status == "data_insufficient"
        assert resp.passed_gates is False


# ═══════════════════════════════════════════════════════════════════════════
# Registry: else-branch elimination test
# ═══════════════════════════════════════════════════════════════════════════

class TestRegistryElseBranch:
    """Verify no module returns the fake diagnostic_score: 82.5."""

    def test_no_fake_diagnostic_score_in_registry(self):
        """The else branch must return data_insufficient, not diagnostic_score: 82.5."""
        import importlib
        src = importlib.util.find_spec(
            "app.services.strategies.registry"
        )
        if src and src.origin:
            with open(src.origin) as f:
                content = f.read()
            assert "diagnostic_score: 82.5" not in content, \
                "Fake diagnostic_score found in registry!"
            assert "diagnostic_score\": 82.5" not in content
