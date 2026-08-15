"""Unit tests for return probability calculations.
"""

import pytest
import numpy as np
import pandas as pd
from app.models.schemas import ReturnProbabilityRequest
from app.services import probability


def test_return_probability_historical(monkeypatch):
    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    history = pd.DataFrame({"Close": np.linspace(100, 150, 100)}, index=dates)
    monkeypatch.setattr(probability, "get_history", lambda *args, **kwargs: history)

    req = ReturnProbabilityRequest(
        symbol="RELIANCE",
        horizon_days=30,
        return_threshold_pct=5.0,
        method="historical_empirical"
    )
    res = probability.calculate_return_probability(req)
    assert res.symbol == "RELIANCE.NS"
    assert res.horizon_days == 30
    assert 0.0 <= res.probability_above_threshold_pct <= 100.0
    assert 0.0 <= res.probability_negative_return_pct <= 100.0
    assert "P50" in res.percentiles
    assert res.sample_size > 0
    assert len(res.warnings) > 0
