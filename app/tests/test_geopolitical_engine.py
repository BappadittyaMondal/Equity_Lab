"""Unit tests for Geopolitical Engine (Phase 8)."""

import pytest
from app.services.research.geopolitical_engine import evaluate_geopolitical_risk


def test_geopolitical_engine_data_unavailable():
    res = evaluate_geopolitical_risk("UNKNOWN_TICKER_XYZ99")
    assert res["status"] == "DATA_UNAVAILABLE"
    assert res["conviction_penalty_pct"] == 0.0
    assert "DATA_UNAVAILABLE" in res["evidence"][0]


def test_geopolitical_engine_reliance():
    res = evaluate_geopolitical_risk("RELIANCE")
    assert "status" in res
    assert "macro_risk_rating" in res
    assert "conviction_penalty_pct" in res
    assert "meta" in res
