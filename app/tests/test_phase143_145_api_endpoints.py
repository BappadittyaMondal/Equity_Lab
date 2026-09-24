"""Integration test suite for Phases 143-145 REST API Endpoints.

Tests:
1. POST /api/v1/research/ipo/listing-gain-eval
2. GET  /api/v1/research/ipo/pipeline
3. POST /api/v1/research/geopolitical/ingest-weak-signal
4. POST /api/v1/research/geopolitical/auto-collect-outcomes
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
API_HEADERS = {"X-API-Key": "test-key-phase143"}


def test_api_ipo_listing_gain_eval():
    """Verify POST /api/v1/research/ipo/listing-gain-eval returns valid 5-factor model response."""
    payload = {
        "company_name": "Premier Drone Dynamics Ltd",
        "symbol": "PREMDRONE",
        "sector": "DEFENSE_ELECTRONICS",
        "gmp_inr": 85.0,
        "qib_multiple": 52.0,
        "nii_multiple": 25.0,
        "rii_multiple": 10.0,
        "total_multiple": 30.0,
        "total_issue_size_cr": 800.0,
        "fresh_issue_cr": 600.0,
        "offer_for_sale_cr": 200.0,
        "price_band_lower": 190.0,
        "price_band_upper": 200.0,
        "post_issue_promoter_holding_pct": 58.0,
        "anchor_lockin_days": 90,
        "implied_pe": 32.0,
        "peer_median_pe": 45.0,
        "roe_pct": 24.0,
        "market_regime_favorable": True,
        "india_vix": 13.0,
    }

    res = client.post("/api/v1/research/ipo/listing-gain-eval", json=payload, headers=API_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["company_name"] == "Premier Drone Dynamics Ltd"
    assert data["listing_gain_probability"] >= 0.80
    assert data["verdict"] == "STRONG_SUBSCRIBE_FOR_LISTING_GAIN"
    assert data["expected_listing_pop_pct"] > 25.0
    assert "qib_subscription_score" in data["sub_scores"]


def test_api_ipo_pipeline():
    """Verify GET /api/v1/research/ipo/pipeline returns unlisted company pipeline."""
    res = client.get("/api/v1/research/ipo/pipeline", headers=API_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 6
    pipeline_symbols = [item["symbol"] for item in data["pipeline"]]
    assert "NSE" in pipeline_symbols
    assert "TATACAP" in pipeline_symbols
    assert "HDBFS" in pipeline_symbols


def test_api_geopolitical_ingest_weak_signal():
    """Verify POST /api/v1/research/geopolitical/ingest-weak-signal processes raw dispatch."""
    payload = {
        "text": (
            "Regional dispatch: Commercial civil aviation publishes FIR closure NOTAM over southern corridor. "
            "Simultaneously, leadership photographed in tactical fatigues visiting naval base near Hormuz."
        ),
        "source": "DEFENSE_WIRE_FEED",
        "prior_probability": 0.05,
        "age_hours": 1.5,
    }

    res = client.post("/api/v1/research/geopolitical/ingest-weak-signal", json=payload, headers=API_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["theater"] == "MIDDLE_EAST"
    assert data["parsed_signals_count"] >= 2
    assert data["evaluation"]["pews_probability"] > 0.20


def test_api_geopolitical_auto_collect_outcomes():
    """Verify POST /api/v1/research/geopolitical/auto-collect-outcomes executes daemon cycle."""
    payload = {
        "min_age_hours": 0.0,
        "event_occurred": True,
        "benchmark_symbol": "^NSEI",
    }

    res = client.post("/api/v1/research/geopolitical/auto-collect-outcomes", json=payload, headers=API_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert "events_scanned" in data
    assert "calibrations_executed" in data
    assert "summary" in data
