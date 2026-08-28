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


def test_causal_and_thesis_rest_api_endpoints():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    
    # Causal inference route test
    resp1 = client.post("/api/v1/data/causal-inference", json={"symbol": "RELIANCE"}, headers={"X-API-Key": "test-key"})
    assert resp1.status_code == 200
    res1 = resp1.json()
    assert "status" in res1
    assert "net_causal_conviction_delta" in res1

    # Thesis tracker route test
    resp2 = client.get("/api/v1/data/thesis-tracker/RELIANCE", headers={"X-API-Key": "test-key"})
    assert resp2.status_code == 200
    res2 = resp2.json()
    assert "status" in res2
    assert res2["symbol"] == "RELIANCE"

