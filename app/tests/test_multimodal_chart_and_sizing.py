"""Unit tests for Multimodal Chart Reconciliation & Risk-Budget Sizing Engine (§Master Control Plane)."""

import pandas as pd
import numpy as np
import pytest
from app.services.research.multimodal_chart_reconciliation import MultimodalChartReconciliationEngine
from app.services.research.portfolio_construction import evaluate_portfolio_construction


def _create_mock_ohlcv(latest_close=100.0, latest_vol=100000.0, avg_vol=100000.0):
    dates = pd.date_range("2026-01-01", periods=30)
    closes = np.full(30, latest_close)
    volumes = np.full(30, avg_vol)
    volumes[-1] = latest_vol
    return pd.DataFrame({
        "open": closes * 0.99,
        "high": closes * 1.01,
        "low": closes * 0.98,
        "close": closes,
        "volume": volumes
    }, index=dates)


def test_multimodal_chart_reconciliation_bull_trap():
    """Verify that a breakout on chart image lacking volume confirmation is flagged as a bull trap."""
    # Breakout price was 95.0, current price is 100.0, but volume is only 0.7x ADTV
    df = _create_mock_ohlcv(latest_close=100.0, latest_vol=70000.0, avg_vol=100000.0)
    visual_features = {
        "visual_price": 100.0,
        "visual_breakout_level": 95.0,
        "visual_pattern": "VCP_BREAKOUT"
    }
    res = MultimodalChartReconciliationEngine.reconcile_chart_features("TEST.NS", visual_features, df)
    assert res["status"] == "SUCCESS"
    assert res["is_breakout_confirmed"] is False
    assert res["alignment_verdict"] == "BULL_TRAP_LOW_VOLUME"
    assert res["actionable_signal"] == "AVOID_BULL_TRAP"
    assert len(res["discrepancies"]) > 0


def test_multimodal_chart_reconciliation_confirmed_breakout():
    """Verify that a breakout supported by high volume is confirmed for execution."""
    # Breakout price 95.0, current close 100.0, volume 2.5x ADTV
    df = _create_mock_ohlcv(latest_close=100.0, latest_vol=250000.0, avg_vol=100000.0)
    visual_features = {
        "visual_price": 100.0,
        "visual_breakout_level": 95.0,
        "visual_pattern": "VCP_BREAKOUT"
    }
    res = MultimodalChartReconciliationEngine.reconcile_chart_features("TEST.NS", visual_features, df)
    assert res["status"] == "SUCCESS"
    assert res["is_breakout_confirmed"] is True
    assert res["alignment_verdict"] == "CONFIRMED_HIGH_VOLUME_BREAKOUT"
    assert res["actionable_signal"] == "EXECUTE_ENTRY"
    assert res["alignment_score_0_100"] >= 90.0


def test_multimodal_chart_pixel_discrepancy():
    """Verify that visual pixel hallucination/drift is detected and numeric close is enforced."""
    df = _create_mock_ohlcv(latest_close=100.0, latest_vol=100000.0, avg_vol=100000.0)
    visual_features = {
        "visual_price": 115.0,  # 15% discrepancy
        "visual_breakout_level": 110.0
    }
    res = MultimodalChartReconciliationEngine.reconcile_chart_features("TEST.NS", visual_features, df)
    assert res["price_discrepancy_pct"] > 10.0
    assert any("diverges" in d for d in res["discrepancies"])
    assert res["numerical_close"] == 100.0


def test_risk_budget_sizing_stop_loss_scaling():
    """Verify that wider stop-loss scales down position size to preserve the 1.5% max risk budget."""
    # Sizing with tight 5% stop
    tight_inputs = {"stop_loss_pct": 5.0, "max_risk_budget_pct": 1.5, "fund_aum_cr": 50.0, "adtv_cr": 50.0, "thesis_maturity": {"confirmed_quarters": 2}}
    res_tight = evaluate_portfolio_construction("TRENT", mivs_score=85.0, portfolio_inputs=tight_inputs)

    # Sizing with wide 25% stop (1.5% / 0.25 = 6.0% size)
    wide_inputs = {"stop_loss_pct": 25.0, "max_risk_budget_pct": 1.5, "fund_aum_cr": 50.0, "adtv_cr": 50.0, "thesis_maturity": {"confirmed_quarters": 2}}
    res_wide = evaluate_portfolio_construction("TRENT", mivs_score=85.0, portfolio_inputs=wide_inputs)

    # Wide stop position size must be strictly smaller to keep portfolio risk capped at 1.5%
    assert res_wide["recommended_position_pct"] < res_tight["recommended_position_pct"]
    assert res_wide["recommended_position_pct"] <= 7.5


def test_algorithmic_geometric_pattern_detector():
    """Verify Minervini VCP, Cup & Handle, and Gaussian KDE calculations directly on OHLCV."""
    from app.services.research.multimodal_chart_reconciliation import GeometricPatternDetector

    # Create 60 days of bars exhibiting contraction (VCP setup)
    dates = pd.date_range("2026-01-01", periods=60)
    # 3 progressive contractions: 100->80, 100->90, 100->96
    closes = np.concatenate([
        np.linspace(95, 80, 15),
        np.linspace(80, 100, 15),
        np.linspace(100, 92, 15),
        np.linspace(92, 98, 15),
    ])
    highs = closes * 1.02
    lows = closes * 0.98
    vols = np.concatenate([
        np.full(30, 100000.0),
        np.full(15, 60000.0),
        np.full(15, 30000.0),  # Volume dry-up at pivot
    ])
    df = pd.DataFrame({"open": closes, "high": highs, "low": lows, "close": closes, "volume": vols}, index=dates)

    # 1. Test KDE Support / Resistance
    kde_res = GeometricPatternDetector.detect_kde_support_resistance(df)
    assert kde_res["status"] == "SUCCESS"
    assert len(kde_res["support_levels"]) > 0 or len(kde_res["resistance_levels"]) > 0

    # 2. Test VCP Pattern Detection
    vcp_res = GeometricPatternDetector.detect_vcp_pattern(df)
    assert "is_vcp_detected" in vcp_res
    assert "contraction_depths_pct" in vcp_res
    assert vcp_res["volume_dryup_confirmed"] is True

    # 3. Test Full Geometric Analysis & Vision Anchor Verification
    full_res = MultimodalChartReconciliationEngine.analyze_geometric_chart_patterns(
        "DIXON",
        df,
        visual_features={"visual_breakout_level": float(vcp_res["pivot_resistance"])}
    )
    assert full_res["status"] == "SUCCESS"
    assert full_res["pattern_type"] == "GEOMETRIC_OHLCV_VERIFIED"
    assert full_res["visual_anchor_verified"] is True
    assert full_res["data_authority"] == "NUMERIC_EXCHANGE_OHLCV_AUTHORITATIVE"


def test_portfolio_construction_event_proximity_multiplier_haircut():
    """Verify that an active event proximity haircut (0.50x) scales down recommended position size."""
    base_inputs = {
        "stop_loss_pct": 5.0,
        "max_risk_budget_pct": 1.5,
        "fund_aum_cr": 50.0,
        "adtv_cr": 50.0,
        "thesis_maturity": {"confirmed_quarters": 2}
    }
    # Standard sizing without event risk (multiplier 1.0)
    res_normal = evaluate_portfolio_construction("TRENT", mivs_score=85.0, portfolio_inputs=base_inputs)
    assert res_normal["event_proximity_multiplier"] == 1.0

    # Binary catalyst risk active (multiplier 0.50)
    event_inputs = dict(base_inputs, position_sizing_multiplier=0.50)
    res_haircut = evaluate_portfolio_construction("TRENT", mivs_score=85.0, portfolio_inputs=event_inputs)

    assert res_haircut["event_proximity_multiplier"] == 0.50
    assert res_haircut["base_recommended_position_pct"] == res_normal["recommended_position_pct"]
    assert res_haircut["recommended_position_pct"] == round(res_normal["recommended_position_pct"] * 0.50, 1)
    assert any("Event Proximity Haircut Applied: 0.50x" in ev for ev in res_haircut["evidence"])
    assert res_haircut["portfolio_signal"]["event_proximity_multiplier"] == 0.50

