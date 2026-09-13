"""Unit tests for Phases 99, 100, and 101:
- Phase 99: Tactical Swing Market Regime Filter & Nifty 50-EMA Conditioning
- Phase 100: Micro-Cap ADV Participation Cap in Portfolio Position Sizing
- Phase 101: Executive 3-Bullet Decision Card in Decision Arbiter
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from app.services.strategies.swing_alerts_service import get_swing_trade_alerts
from app.models.schemas import SwingTradeAlertsResponse, MarketRegimeClassification, ExecutiveDecisionCard
from app.services.research.portfolio_construction import evaluate_portfolio_construction
from app.services.decision_brain.arbiter import Arbiter


def test_swing_alerts_macro_regime_unfavorable_discount():
    """Phase 99: Verify swing alerts receive macro haircut when market regime is in bear trend or panic."""
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

    mock_bear_regime = MarketRegimeClassification(
        regime_code="R4_BEAR_TREND",
        description="Bear Trend — Benchmark below long-term trend",
        market_stress_level="HIGH"
    )

    with patch("app.services.strategies.swing_alerts_service.run_mean_reversion_d17", return_value=mock_d17), \
         patch("app.services.strategies.swing_alerts_service.run_pocket_pivot_b7", return_value=mock_pp), \
         patch("app.services.strategies.swing_alerts_service.run_rs_rating_b6", return_value=mock_rs), \
         patch("app.services.strategies.swing_alerts_service.run_vpa_b4", return_value=mock_vpa), \
         patch("app.services.strategies.swing_alerts_service.get_quote", return_value=mock_quote), \
         patch("app.services.strategies.swing_alerts_service.get_history", return_value=synthetic_df), \
         patch("app.services.strategies.swing_alerts_service.classify_market_regime", return_value=mock_bear_regime):

        res = get_swing_trade_alerts(["TEST_TICKER"])
        assert isinstance(res, SwingTradeAlertsResponse)
        assert res.market_regime == "R4_BEAR_TREND"
        assert res.market_regime_favorable is False
        assert len(res.alerts) == 1
        alert = res.alerts[0]
        assert alert.market_regime == "R4_BEAR_TREND"
        assert alert.market_regime_favorable is False
        # Base setup_score was 95.0; 15% macro haircut = 80.8
        assert alert.swing_setup_score == pytest.approx(80.8, rel=1e-2)


def test_portfolio_construction_microcap_adv_cap():
    """Phase 100: Verify that illiquid micro-caps are not artificially clamped to 1.0% of fund AUM."""
    # Low ADTV: Rs 0.20 Cr (20 Lakhs) with Rs 500 Cr Fund AUM
    res_illiquid = evaluate_portfolio_construction(
        "MICRO_CAP",
        mivs_score=85.0,
        adtv_cr=0.20,
        fund_aum_cr=500.0
    )
    # 0.20 * 5.0 * 0.15 / 500.0 * 100.0 = 0.03%, bounded by min floor 0.1%
    assert res_illiquid["portfolio_signal"]["liquidity_cap_pct"] == 0.1
    assert res_illiquid["recommended_position_pct"] == 0.1
    assert any("Micro-Cap Liquidity Constraint" in e for e in res_illiquid["evidence"])

    # Normal liquid scrip: Rs 12.5 Cr ADTV with Rs 500 Cr AUM
    res_liquid = evaluate_portfolio_construction(
        "LIQUID_STOCK",
        mivs_score=85.0,
        adtv_cr=12.5,
        fund_aum_cr=500.0
    )
    # 12.5 * 5.0 * 0.15 / 500.0 * 100.0 = 1.875% -> 1.9%
    assert res_liquid["portfolio_signal"]["liquidity_cap_pct"] == 1.9
    assert res_liquid["recommended_position_pct"] > 0.5


def test_arbiter_generates_executive_decision_card():
    """Phase 101: Verify Arbiter generates and attaches ExecutiveDecisionCard to ConvictionCall."""
    arb = Arbiter()
    call = arb.arbitrate("RELIANCE")
    assert call.executive_decision_card is not None
    assert isinstance(call.executive_decision_card, ExecutiveDecisionCard)
    assert call.executive_decision_card.fiduciary_action == call.verdict
    assert len(call.executive_decision_card.top_conviction_drivers) >= 1
    assert call.executive_decision_card.primary_invalidation_threat != ""
    assert "verdict" in call.executive_decision_card.execution_guardrails
    assert "conviction_score" in call.executive_decision_card.execution_guardrails


def test_machine_readable_report_executive_decision_card():
    """Phase 101: Verify MachineReadableStockReport includes ExecutiveDecisionCard."""
    arb = Arbiter()
    report = arb.generate_machine_readable_report("TCS")
    assert report.executive_decision_card is not None
    assert isinstance(report.executive_decision_card, ExecutiveDecisionCard)
    assert report.executive_decision_card.fiduciary_action == report.verdict
    assert report.executive_decision_card.conviction_tier == report.multibagger_tier
