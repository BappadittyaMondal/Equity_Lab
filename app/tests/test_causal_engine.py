"""Unit tests for Causal Engine (Phase 7)."""

import pytest
from app.services.research.causal_engine import analyze_causal_event_impacts


def test_causal_engine_missing_data_status():
    res = analyze_causal_event_impacts("UNKNOWN_TICKER_XYZ99")
    assert res["status"] == "DATA_UNAVAILABLE"
    assert res["net_causal_conviction_delta"] == 0.0
    assert "DATA_UNAVAILABLE" in res["evidence"][0]


def test_causal_engine_existing_ticker():
    res = analyze_causal_event_impacts("RELIANCE")
    assert "status" in res
    assert "net_causal_conviction_delta" in res
    assert "meta" in res
