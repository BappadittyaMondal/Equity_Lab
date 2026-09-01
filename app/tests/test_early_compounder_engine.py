"""Unit tests for Early-Stage ₹100Cr+ Microcap Compounder Engine (E21).
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.research.early_compounder_engine import run_early_compounder_engine
from app.services.strategies.registry import run_strategy_module, get_strategy_module


def test_early_compounder_engine_direct_execution():
    res = run_early_compounder_engine("SHILCHAR")
    assert res.strategy_id == "E21"
    assert res.status == "production"
    assert "early_compounder_score" in res.results
    assert "incubator_tier" in res.results
    assert "incremental_roic_pct" in res.results
    assert res.results["incubator_tier"] in [
        "A_PLUS_HIGH_CONVICTION",
        "A_COMPOUNDER_CANDIDATE",
        "B_WATCHLIST_TRIGGER_REQUIRED",
        "REJECT_KILL_TEST_FAILED"
    ]


def test_early_compounder_registry_dispatch():
    mod = get_strategy_module("E21")
    assert mod.id == "E21"
    assert mod.category == "Microcap Incubator Intelligence"

    res = run_strategy_module("E21", "TATACHEM")
    assert res.strategy_id == "E21"
    assert res.results["symbol"] == "TATACHEM"


def test_early_compounder_api_endpoint():
    client = TestClient(app)
    res = client.get("/api/v1/research/early-compounder?symbol=RELIANCE")
    assert res.status_code == 200
    data = res.json()
    assert data["strategy_id"] == "E21"
    assert "results" in data
    assert "incubator_tier" in data["results"]
