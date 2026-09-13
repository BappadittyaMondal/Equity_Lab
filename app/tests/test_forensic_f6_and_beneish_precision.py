"""Unit tests for Phase 93-96 Institutional Hardening & Forensic Precision."""

from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

from app.services.strategies.forensic_engine import compute_beneish_mscore, compute_piotroski_fscore
from app.services.research.multimodal_chart_reconciliation import MultimodalChartReconciliationEngine
from app.services.research.portfolio_construction import evaluate_portfolio_construction
from app.services.strategies.swing_alerts_service import get_swing_trade_alerts


def _make_obs(metric: str, period: str, value: float):
    obs = MagicMock()
    obs.metric = metric
    obs.period_end = period
    obs.value = value
    obs.confidence = 0.90
    return obs


def test_piotroski_f6_current_ratio_observed_improvement():
    """Verify F6 awards 1 point when Current Ratio strictly improves YoY."""
    financials = [
        _make_obs("revenue", "2023-03-31", 1000.0),
        _make_obs("revenue", "2024-03-31", 1200.0),
        _make_obs("net_income", "2023-03-31", 100.0),
        _make_obs("net_income", "2024-03-31", 150.0),
        _make_obs("operating_cash_flow", "2023-03-31", 120.0),
        _make_obs("operating_cash_flow", "2024-03-31", 180.0),
        _make_obs("total_assets", "2023-03-31", 2000.0),
        _make_obs("total_assets", "2024-03-31", 2200.0),
        _make_obs("total_debt", "2023-03-31", 500.0),
        _make_obs("total_debt", "2024-03-31", 400.0),
        _make_obs("gross_profit", "2023-03-31", 400.0),
        _make_obs("gross_profit", "2024-03-31", 500.0),
        # Current Assets & Liabilities: CR improves from 1.50 to 2.00
        _make_obs("current_assets", "2023-03-31", 300.0),
        _make_obs("current_assets", "2024-03-31", 400.0),
        _make_obs("current_liabilities", "2023-03-31", 200.0),
        _make_obs("current_liabilities", "2024-03-31", 200.0),
    ]
    res = compute_piotroski_fscore(financials)
    assert res["component_scores"]["F6"] == 1
    assert any("Current ratio improved (1.50 → 2.00)" in e for e in res["evidence"])


def test_piotroski_f6_current_ratio_observed_deterioration():
    """Verify F6 awards 0 points when Current Ratio declines YoY."""
    financials = [
        _make_obs("revenue", "2023-03-31", 1000.0),
        _make_obs("revenue", "2024-03-31", 1200.0),
        _make_obs("net_income", "2023-03-31", 100.0),
        _make_obs("net_income", "2024-03-31", 150.0),
        _make_obs("operating_cash_flow", "2023-03-31", 120.0),
        _make_obs("operating_cash_flow", "2024-03-31", 180.0),
        _make_obs("total_assets", "2023-03-31", 2000.0),
        _make_obs("total_assets", "2024-03-31", 2200.0),
        _make_obs("total_debt", "2023-03-31", 500.0),
        _make_obs("total_debt", "2024-03-31", 400.0),
        _make_obs("gross_profit", "2023-03-31", 400.0),
        _make_obs("gross_profit", "2024-03-31", 500.0),
        # Current Assets & Liabilities: CR declines from 2.00 to 1.50
        _make_obs("current_assets", "2023-03-31", 400.0),
        _make_obs("current_assets", "2024-03-31", 300.0),
        _make_obs("current_liabilities", "2023-03-31", 200.0),
        _make_obs("current_liabilities", "2024-03-31", 200.0),
    ]
    res = compute_piotroski_fscore(financials)
    assert res["component_scores"]["F6"] == 0
    assert any("Current ratio declined/stable (2.00 → 1.50)" in e for e in res["evidence"])


def test_piotroski_f6_unobserved_zero_trust_fail_closed():
    """Verify F6 awards 0 points under zero-trust when current assets/liabilities are unobserved."""
    financials = [
        _make_obs("revenue", "2023-03-31", 1000.0),
        _make_obs("revenue", "2024-03-31", 1200.0),
        _make_obs("net_income", "2023-03-31", 100.0),
        _make_obs("net_income", "2024-03-31", 150.0),
        _make_obs("operating_cash_flow", "2023-03-31", 120.0),
        _make_obs("operating_cash_flow", "2024-03-31", 180.0),
        _make_obs("total_assets", "2023-03-31", 2000.0),
        _make_obs("total_assets", "2024-03-31", 2200.0),
        _make_obs("gross_profit", "2023-03-31", 400.0),
        _make_obs("gross_profit", "2024-03-31", 500.0),
    ]
    res = compute_piotroski_fscore(financials)
    assert res["component_scores"]["F6"] == 0
    assert any("F6 Liquidity: current assets/liabilities unobserved" in e for e in res["evidence"])


def test_beneish_dsri_audited_receivables_calculation():
    """Verify Beneish calculates DSRI from audited receivables and detects manipulation if DSRI > 1.25."""
    financials = [
        _make_obs("revenue", "2023-03-31", 1000.0),
        _make_obs("revenue", "2024-03-31", 1100.0),  # +10% revenue
        _make_obs("gross_profit", "2023-03-31", 400.0),
        _make_obs("gross_profit", "2024-03-31", 440.0),
        _make_obs("total_assets", "2023-03-31", 2000.0),
        _make_obs("total_assets", "2024-03-31", 2200.0),
        _make_obs("operating_cash_flow", "2023-03-31", 150.0),
        _make_obs("operating_cash_flow", "2024-03-31", 160.0),
        _make_obs("net_income", "2023-03-31", 100.0),
        _make_obs("net_income", "2024-03-31", 110.0),
        # Receivables grew from 100 to 200 (+100%, vs +10% revenue) -> DSRI = (200/1100) / (100/1000) = 1.818
        _make_obs("trade_receivables", "2023-03-31", 100.0),
        _make_obs("trade_receivables", "2024-03-31", 200.0),
    ]
    res = compute_beneish_mscore(financials)
    assert res["dsri_status"] == "AUDITED_RECEIVABLES_OBSERVED"
    assert res["dsri"] == pytest.approx(1.8182, rel=1e-3)
    assert res["model_variant"] == "BENEISH_M_AUDITED_RECEIVABLES"
    assert any("DSRI=1.82 > 1.25: Receivables growing much faster than sales" in e for e in res["evidence"])


def test_beneish_dsri_unobserved_warning():
    """Verify Beneish flags unobserved receivables with explicit warning disclosure."""
    financials = [
        _make_obs("revenue", "2023-03-31", 1000.0),
        _make_obs("revenue", "2024-03-31", 1100.0),
        _make_obs("gross_profit", "2023-03-31", 400.0),
        _make_obs("gross_profit", "2024-03-31", 440.0),
        _make_obs("total_assets", "2023-03-31", 2000.0),
        _make_obs("total_assets", "2024-03-31", 2200.0),
        _make_obs("operating_cash_flow", "2023-03-31", 150.0),
        _make_obs("operating_cash_flow", "2024-03-31", 160.0),
        _make_obs("net_income", "2023-03-31", 100.0),
        _make_obs("net_income", "2024-03-31", 110.0),
    ]
    res = compute_beneish_mscore(financials)
    assert res["dsri_status"] == "RECEIVABLES_UNOBSERVED"
    assert res["model_variant"] == "BENEISH_M_PARTIAL_PROXIED"
    assert "RECEIVABLES_UNOBSERVED" in res["data_gap_warning"]


def test_multimodal_chart_pixel_discrepancy_forces_abstain():
    """Verify that a visual pixel discrepancy > 2% forces actionable_signal = ABSTAIN_DATA_MISMATCH."""
    dates = pd.date_range("2026-01-01", periods=30)
    df = pd.DataFrame({
        "open": [100.0] * 30,
        "high": [101.0] * 30,
        "low": [99.0] * 30,
        "close": [100.0] * 30,
        "volume": [250000.0] * 30,  # 2.5x volume
    }, index=dates)

    visual_features = {
        "visual_price": 115.0,  # 15% discrepancy
        "visual_breakout_level": 95.0,
        "visual_pattern": "VCP_BREAKOUT",
    }
    res = MultimodalChartReconciliationEngine.reconcile_chart_features("TEST.NS", visual_features, df)
    assert res["pixel_discrepancy_overridden"] is True
    assert res["actionable_signal"] == "ABSTAIN_DATA_MISMATCH"


def test_swing_alerts_filter_sub_1_5_rrr():
    """Verify swing alerts discard setups where RRR < 1.50."""
    dates = pd.date_range("2024-01-01", periods=20, freq="D")
    synthetic_df = pd.DataFrame({
        "open": [100.0] * 20,
        "high": [105.0] * 20,
        "low": [95.0] * 20,
        "close": [100.0] * 20,
        "volume": [100000] * 20,
    }, index=dates)

    mock_d17 = MagicMock()
    mock_d17.metrics = {"weinstein_stage": "STAGE_2_ADVANCING"}
    mock_pp = MagicMock()
    mock_pp.metrics = {"pocket_pivot_count": 2}
    mock_rs = MagicMock()
    mock_rs.metrics = {"rs_rating_0_99": 80}
    mock_vpa = MagicMock()
    mock_vpa.metrics = {"vpa_score": 75.0}
    mock_vpa.results = {"accumulation_signal": "STRONG"}

    mock_quote = MagicMock()
    mock_quote.price = 200.0

    # Test passing setup (RRR = 2.0 >= 1.50)
    with patch("app.services.strategies.swing_alerts_service.run_mean_reversion_d17", return_value=mock_d17), \
         patch("app.services.strategies.swing_alerts_service.run_pocket_pivot_b7", return_value=mock_pp), \
         patch("app.services.strategies.swing_alerts_service.run_rs_rating_b6", return_value=mock_rs), \
         patch("app.services.strategies.swing_alerts_service.run_vpa_b4", return_value=mock_vpa), \
         patch("app.services.strategies.swing_alerts_service.get_quote", return_value=mock_quote), \
         patch("app.services.strategies.swing_alerts_service.get_history", return_value=synthetic_df):

        res = get_swing_trade_alerts(["TEST_PASSING"])
        assert len(res.alerts) == 1
        assert res.alerts[0].risk_reward_ratio >= 1.50


def test_portfolio_construction_confidence_transparency():
    """Verify unobserved confidence applies conservative 70% baseline with evidence notice."""
    res = evaluate_portfolio_construction("TRENT", mivs_score=85.0)
    assert res["recommended_position_pct"] > 0.0
    assert any("Evidence confidence unobserved: using conservative baseline 70.0%" in e for e in res["evidence"])


def test_short_term_prediction_fetches_real_outcome_residuals():
    """Verify ShortTermPredictionEngine._fetch_outcome_ledger_residuals successfully queries outcome_ledger."""
    from app.services.strategies.short_term_prediction_engine import ShortTermPredictionEngine
    res_30 = ShortTermPredictionEngine._fetch_outcome_ledger_residuals(30)
    assert isinstance(res_30, list)
    if len(res_30) > 0:
        assert len(res_30) >= 20
        assert all(isinstance(x, float) for x in res_30)

