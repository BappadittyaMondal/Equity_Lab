"""Unit tests for Phase 78: Volatility-Calibrated Dynamic Swing Trading Stops."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from app.services.strategies.swing_alerts_service import get_swing_trade_alerts
from app.models.schemas import SwingTradeAlertsResponse, SwingTradeAlertItem


def test_swing_alerts_dynamic_atr_calculation():
    """Verify swing alerts use dynamic 2.0x ATR stop loss and 4.0x ATR target."""
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

    with patch("app.services.strategies.swing_alerts_service.run_mean_reversion_d17", return_value=mock_d17), \
         patch("app.services.strategies.swing_alerts_service.run_pocket_pivot_b7", return_value=mock_pp), \
         patch("app.services.strategies.swing_alerts_service.run_rs_rating_b6", return_value=mock_rs), \
         patch("app.services.strategies.swing_alerts_service.run_vpa_b4", return_value=mock_vpa), \
         patch("app.services.strategies.swing_alerts_service.get_quote", return_value=mock_quote), \
         patch("app.services.strategies.swing_alerts_service.get_history", return_value=synthetic_df):

        res = get_swing_trade_alerts(["TEST_TICKER"])
        assert isinstance(res, SwingTradeAlertsResponse)
        assert len(res.alerts) == 1
        alert = res.alerts[0]

        assert alert.alert_type == "STAGE_2_POCKET_PIVOT"
        assert alert.atr_14 is not None
        assert alert.atr_14 > 0.0
        expected_stop = round(200.0 - 2.0 * alert.atr_14, 2)
        expected_target = round(200.0 + 4.0 * alert.atr_14, 2)
        assert alert.stop_loss_level == expected_stop
        assert alert.target_price == expected_target
        assert alert.risk_reward_ratio == 2.0
        assert alert.stop_loss_distance_pct == round(((200.0 - expected_stop) / 200.0) * 100.0, 2)


def test_swing_alerts_conservative_fallback_when_no_history():
    """Verify swing alerts fall back safely to -6%/+18% when history is empty."""
    mock_d17 = MagicMock()
    mock_d17.metrics = {"weinstein_stage": "STAGE_2_ADVANCING"}
    mock_pp = MagicMock()
    mock_pp.metrics = {"pocket_pivot_count": 1}
    mock_rs = MagicMock()
    mock_rs.metrics = {"rs_rating_0_99": 75}
    mock_vpa = MagicMock()
    mock_vpa.metrics = {"vpa_score": 60.0}
    mock_vpa.results = {"accumulation_signal": "MODERATE"}

    mock_quote = MagicMock()
    mock_quote.price = 100.0

    with patch("app.services.strategies.swing_alerts_service.run_mean_reversion_d17", return_value=mock_d17), \
         patch("app.services.strategies.swing_alerts_service.run_pocket_pivot_b7", return_value=mock_pp), \
         patch("app.services.strategies.swing_alerts_service.run_rs_rating_b6", return_value=mock_rs), \
         patch("app.services.strategies.swing_alerts_service.run_vpa_b4", return_value=mock_vpa), \
         patch("app.services.strategies.swing_alerts_service.get_quote", return_value=mock_quote), \
         patch("app.services.strategies.swing_alerts_service.get_history", return_value=None):

        res = get_swing_trade_alerts(["EMPTY_HIST_TICKER"])
        assert len(res.alerts) == 1
        alert = res.alerts[0]
        assert alert.stop_loss_level == 94.0
        assert alert.target_price == 118.0
        assert alert.stop_loss_distance_pct == 6.0
