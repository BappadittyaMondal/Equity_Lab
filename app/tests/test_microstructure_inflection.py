"""Unit tests for Phase 1 Microstructure & OBV Accumulation Engine."""

import numpy as np
import pandas as pd
import pytest

from app.services.strategies.obv_accumulation_engine import (
    calculate_obv_series, compute_obv_convexity, run_obv_accumulation
)
from app.services.strategies.technical_engines import run_vpa_b4


def generate_mock_weekly_data(n_bars=60, base_volume=100000, spike=False):
    """Generates synthetic weekly OHLCV DataFrame."""
    dates = pd.date_range(end="2026-08-30", periods=n_bars, freq="1W")
    
    # Flat price with slight upward drift
    close = np.linspace(100.0, 110.0, n_bars) + np.random.normal(0, 0.2, n_bars)
    high = close + 2.0
    low = close - 2.0
    volume = np.full(n_bars, float(base_volume)) + np.random.normal(0, 2000, n_bars)
    
    if spike:
        # OBV acceleration: heavy volume on up weeks in last 12 bars
        for i in range(-12, 0):
            close[i] = close[i-1] + 2.0
            volume[i] = base_volume * 6.0
            
    df = pd.DataFrame({
        "Open": close - 0.5,
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": volume
    }, index=dates)
    return df


def test_obv_series_calculation():
    df = generate_mock_weekly_data(n_bars=20)
    obv = calculate_obv_series(df)
    assert len(obv) == 20
    assert isinstance(obv, pd.Series)


def test_obv_convexity_calculation_flat():
    df = generate_mock_weekly_data(n_bars=60, spike=False)
    res = compute_obv_convexity(df)
    assert res["sufficient_data"] is True
    # Flat data should not produce extreme C_OBV
    assert res["c_obv"] < 2.5


def test_obv_convexity_calculation_spike():
    df = generate_mock_weekly_data(n_bars=60, spike=True)
    res = compute_obv_convexity(df)
    assert res["sufficient_data"] is True
    assert res["c_obv"] >= 1.5


def test_run_obv_accumulation_mock():
    df = generate_mock_weekly_data(n_bars=60, spike=True)
    res = run_obv_accumulation("MOCK_STOCK.NS", hist_df=df)
    assert res.status == "production"
    assert res.results["c_obv"] >= 1.5
    assert res.passed_gates is True


def test_vpa_b4_circuit_guard_upper_circuit(monkeypatch):
    """Verifies run_vpa_b4 handles upper circuit (High == Low and price > prev_close)."""
    dates = pd.date_range(end="2026-08-30", periods=70, freq="1D")
    close = np.linspace(100, 150, 70)
    high = close.copy()
    low = close.copy()
    
    # Upper circuit on last bar
    close[-1] = 150.0
    high[-1] = 150.0
    low[-1] = 150.0
    close[-2] = 145.0
    
    volume = np.full(70, 50000.0)
    volume[-5:] = 500000.0  # Heavy 5-day log volume spike
    
    df = pd.DataFrame({"Open": close, "High": high, "Low": low, "Close": close, "Volume": volume}, index=dates)
    
    import app.services.strategies.technical_engines as te
    monkeypatch.setattr(te, "_get_price_data", lambda symbol: df)
    
    res = te.run_vpa_b4("UPPER_CIRCUIT.NS")
    assert res.status == "production"
    assert res.results["close_position"] == 1.0
    assert res.results["volume_z_score"] >= 1.5
