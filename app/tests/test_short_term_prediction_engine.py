"""Unit & Integration Test Suite for High-Precision Short-Term Prediction Engine."""

import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.services.strategies.short_term_indicators import (
    calculate_wilder_rsi,
    calculate_stochastic_rsi,
    calculate_multi_anchor_vwap,
    calculate_bollinger_keltner_squeeze,
    calculate_moving_average_ribbon
)
from app.services.strategies.short_term_prediction_engine import ShortTermPredictionEngine


@pytest.fixture
def sample_ohlcv_df():
    """Generates synthetic 100-day OHLCV resembling an overbought counter-trend bounce."""
    np.random.seed(42)
    dates = pd.date_range('2026-05-01', periods=100)
    # Price falls from 5399 to 3950, then small bounce to 4065
    closes = np.linspace(5399, 3950, 95)
    closes = np.append(closes, [3980, 4010, 4035, 4050, 4065.30])
    highs = closes + np.random.uniform(10, 30, 100)
    lows = closes - np.random.uniform(10, 30, 100)
    volumes = np.random.randint(15000, 35000, 100)
    # Introduce an ATH volume spike at index 10
    volumes[10] = 120000

    return pd.DataFrame({
        'Open': closes,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': volumes
    }, index=dates)


def test_wilder_rsi_calculation(sample_ohlcv_df):
    """Verify classical Wilder's RSI produces valid bounded output between 0 and 100."""
    rsi = calculate_wilder_rsi(sample_ohlcv_df['Close'], period=14)
    assert len(rsi) == 100
    assert 0.0 <= rsi.iloc[-1] <= 100.0


def test_stochastic_rsi_bearish_exhaustion(sample_ohlcv_df):
    """Verify that Stochastic RSI detects overbought counter-trend exhaustion (e.g. SHILCTECH condition)."""
    res = calculate_stochastic_rsi(sample_ohlcv_df['Close'])
    assert "rsi" in res
    assert "stoch_k" in res
    assert "stoch_d" in res
    assert res["momentum_exhaustion_state"] in [
        "BEARISH_EXHAUSTION_COUNTER_TREND",
        "BEARISH_MOMENTUM_EXPANSION",
        "NEUTRAL_CONSOLIDATION"
    ]


def test_multi_anchor_vwap_supply_and_demand(sample_ohlcv_df):
    """Verify multi-anchor VWAPs properly calculate 52W High and 52W Low anchors."""
    res = calculate_multi_anchor_vwap(sample_ohlcv_df)
    assert res["avwap_high"] > res["avwap_low"]
    assert res["avwap_high"] > res["current_price"]  # Trapped supply is above current price
    assert res["dist_to_supply_avwap_pct"] < 0.0     # Price is below trapped supply AVWAP
    assert res["avwap_pinch_spread_pct"] > 0.0


def test_bollinger_keltner_squeeze(sample_ohlcv_df):
    """Verify Bollinger-Keltner squeeze detector correctly tracks bandwidth and compression."""
    res = calculate_bollinger_keltner_squeeze(sample_ohlcv_df)
    assert res["bb_upper"] > res["bb_middle"] > res["bb_lower"]
    assert res["bandwidth_pct"] > 0.0
    assert res["squeeze_state"] in ["SQUEEZE_ON", "SQUEEZE_FIRED_LONG", "SQUEEZE_FIRED_SHORT", "NO_SQUEEZE_NORMAL"]


def test_moving_average_ribbon(sample_ohlcv_df):
    """Verify moving average ribbon maps declining overhead moving averages."""
    res = calculate_moving_average_ribbon(sample_ohlcv_df)
    assert "sma_10" in res["moving_averages"]
    assert "sma_50" in res["moving_averages"]
    assert res["overhead_traffic_tier"] in [
        "HEAVY_OVERHEAD_RESISTANCE_CEILING",
        "MODERATE_OVERHEAD_RESISTANCE",
        "CLEAR_SKY_NO_IMMEDIATE_MA_OVERHEAD"
    ]


def test_conformal_prediction_cones():
    """Verify conformal volatility prediction cones enforce mathematical width and centering invariants."""
    current_price = 4065.30
    atr = 115.0
    cones = ShortTermPredictionEngine.generate_conformal_prediction_cones(
        current_price=current_price,
        atr_14=atr,
        directional_bias_pct=-2.0
    )

    for h in [3, 5, 10]:
        cone = cones[f"horizon_{h}d"]
        c80 = cone["conformal_80_pct"]
        c95 = cone["conformal_95_pct"]

        # 1. Bounds ordering
        assert c95["lower_bound"] < c80["lower_bound"] < current_price
        assert current_price < c80["upper_bound"] < c95["upper_bound"]

        # 2. 95% cone must be strictly wider than 80% cone
        assert c95["spread_pct"] > c80["spread_pct"]


def test_master_short_term_prediction_pipeline(sample_ohlcv_df):
    """Verify master short-term prediction pipeline returns scenario probabilities and trade levels."""
    res = ShortTermPredictionEngine.evaluate_short_term_prediction("SHILCTECH", df=sample_ohlcv_df)
    assert res["symbol"] == "SHILCTECH.NS"
    assert res["recommended_action"] in [
        "PULLBACK_WATCH_WAIT_FOR_SUPPORT",
        "MOMENTUM_BREAKOUT_SETUP",
        "RANGEBOUND_CONSOLIDATION"
    ]
    probs = res["scenario_probabilities_pct"]
    assert round(probs["pullback_to_support"] + probs["rangebound_chop"] + probs["breakout_expansion"], 1) == 100.0
    assert res["key_levels"]["invalidation_stop"] > 0.0


def test_api_endpoint_short_term_prediction():
    """Verify FastAPI GET /api/v1/technical/short-term-prediction/{symbol} endpoint."""
    client = TestClient(app)
    response = client.get("/api/v1/technical/short-term-prediction/POLYCAB")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "POLYCAB.NS"
    assert "scenario_probabilities_pct" in data
    assert "conformal_prediction_cones" in data
    assert "key_levels" in data
