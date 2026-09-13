"""Unit tests verifying authentic 14-day Wilder RSI resolution in CustomScreenerEngine."""

import pytest
import pandas as pd
import numpy as np
from app.services.research.custom_screener import CustomScreenerEngine, FIELD_MAP


def test_custom_screener_rsi_field_map_decoupled_from_opm():
    """Verify that 'rsi' in FIELD_MAP points to 'rsi_14', not 'opm_latest'."""
    assert FIELD_MAP["rsi"] == "rsi_14"
    assert FIELD_MAP["rsi 14"] == "rsi_14"
    assert FIELD_MAP["relative strength index"] == "rsi_14"
    assert FIELD_MAP["opm"] == "opm_latest"


def test_custom_screener_rsi_evaluation_truth():
    """Verify that RSI < 30 does NOT match a stock where opm_latest is 25% but rsi_14 is 65."""
    comp = {
        "symbol": "TEST_MOMENTUM.NS",
        "company_name": "Test Momentum Ltd.",
        "opm_latest": 25.0,  # 25% OPM (< 30)
        "rsi_14": 65.0,      # 65 RSI (> 30)
        "current_price": 500.0,
        "market_cap": 2500.0,
    }

    # If bug was present: RSI would evaluate to opm_latest (25.0) and pass "RSI < 30"
    # With fix: RSI evaluates to rsi_14 (65.0) and correctly FAILS "RSI < 30"
    assert CustomScreenerEngine._eval_boolean_expr(comp, "RSI < 30") is False
    assert CustomScreenerEngine._eval_boolean_expr(comp, "RSI > 60") is True
    assert CustomScreenerEngine._eval_boolean_expr(comp, "OPM < 30") is True

    # Test oversold stock with low RSI
    comp_oversold = {
        "symbol": "TEST_OVERSOLD.NS",
        "company_name": "Test Oversold Ltd.",
        "opm_latest": 40.0,  # High OPM (> 30)
        "rsi_14": 25.0,      # Low RSI (< 30)
        "current_price": 200.0,
        "market_cap": 1000.0,
    }
    assert CustomScreenerEngine._eval_boolean_expr(comp_oversold, "RSI < 30") is True
    assert CustomScreenerEngine._eval_boolean_expr(comp_oversold, "OPM > 35") is True


def test_custom_screener_dynamic_rsi_calculation_from_history(monkeypatch):
    """Verify dynamic computation of Wilder RSI when rsi_14 is not pre-populated."""
    # Generate 30 days of rising prices (RSI will be high, > 70)
    dates = pd.date_range(end="2026-09-12", periods=30, freq="B")
    prices = [100.0 + i * 2.0 for i in range(30)]
    mock_df = pd.DataFrame({"Close": prices, "Volume": [100000] * 30}, index=dates)

    from app.services import market_data
    monkeypatch.setattr(market_data, "get_history", lambda sym, period="6mo", interval="1d", as_of=None: mock_df)

    comp = {
        "symbol": "DYNAMIC_RSI.NS",
        "company_name": "Dynamic RSI Ltd.",
        "opm_latest": 15.0,
        "current_price": prices[-1],
    }

    # Should dynamically calculate RSI > 70 from the monotonic upward price series
    resolved_rsi = CustomScreenerEngine._resolve_val(comp, "rsi")
    assert resolved_rsi > 70.0
    assert CustomScreenerEngine._eval_boolean_expr(comp, "RSI > 70") is True
    assert CustomScreenerEngine._eval_boolean_expr(comp, "RSI < 40") is False
