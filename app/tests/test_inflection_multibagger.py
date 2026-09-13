# -*- coding: utf-8 -*-
"""Test suite for Strategy Module E19: Multibagger Inflection Engine."""

import pytest
from app.services.strategies.inflection_multibagger import run_inflection_multibagger


def test_inflection_multibagger_missing_data():
    res = run_inflection_multibagger("INVALID_SYMBOL_999")
    assert res.strategy_id == "E19"
    assert res.status in ["data_insufficient", "production"]
    assert hasattr(res, "passed_gates")


def test_inflection_multibagger_valid_symbol():
    res = run_inflection_multibagger("TCS")
    assert res.strategy_id == "E19"
    assert res.strategy_name == "E19 Multibagger Inflection Engine"
    assert "inflection_signal" in res.results


def test_inflection_multibagger_no_synthetic_fakes(monkeypatch):
    """Ensure no synthetic F-score=7 or mock PAT is manufactured for missing data."""
    # When timeline is completely empty, it must fail closed honestly without synthetic mocks
    res = run_inflection_multibagger("NON_EXISTENT_TICKER")
    assert res.status == "data_insufficient"
    assert res.passed_gates is False
    assert res.results.get("inflection_signal") == "NO_SIGNAL"
    assert "f_score" not in res.results.get("financial_observations", {})


def test_inflection_multibagger_case_insensitive_delivery_columns(monkeypatch):
    """Verify defensive case-insensitive column resolution for delivery data (e.g. 'delivery_pct', 'deliv_pct')."""
    import pandas as pd
    import numpy as np
    from unittest.mock import patch, MagicMock

    dates = pd.date_range("2026-01-01", periods=60)
    # Historical volume with a 5-day spike
    vol = np.ones(60) * 10000.0
    vol[-5:] = 50000.0  # Spike
    # Lowercase delivery_pct column with jump from 25% to 55% (+30% delta)
    deliv = np.ones(60) * 25.0
    deliv[-5:] = 55.0

    mock_df = pd.DataFrame({
        "Close": np.linspace(100, 120, 60),
        "High": np.linspace(102, 122, 60),
        "Low": np.linspace(99, 119, 60),
        "Volume": vol,
        "delivery_pct": deliv  # Lowercase naming!
    }, index=dates)

    # Mock get_history, get_quote and research timeline to isolate delivery column test
    mock_obs = [
        MagicMock(period_end="2025-12-31", metric="pat", value=100.0),
        MagicMock(period_end="2026-03-31", metric="pat", value=140.0),
        MagicMock(period_end="2026-03-31", metric="pe", value=15.0),
    ]
    mock_own = [MagicMock(period_end="2026-03-31", promoter_pledge_pct=0.0)]

    with patch("app.services.strategies.inflection_multibagger.get_history", return_value=mock_df):
        with patch("app.services.strategies.inflection_multibagger.get_quote", return_value={"price": 120.0, "data_mode": "REAL"}):
            with patch("app.services.strategies.inflection_multibagger.ResearchDataStore.get_timeline",
                       return_value=(None, mock_obs, [], [], mock_own, [])):
                with patch("app.services.strategies.inflection_multibagger.compute_piotroski_fscore",
                           return_value={"status": "success", "f_score": 8}):
                    res = run_inflection_multibagger("ACCUM_TEST.NS")
                    assert res.status == "production"
                assert "delivery_delta_pct" in res.results
                assert res.results["delivery_delta_pct"] != "UNOBSERVED"
                assert "+30.0%" in res.results["delivery_delta_pct"]
                assert res.results["float_absorption_signal"] == "ACTIVE_ACCUMULATION"


