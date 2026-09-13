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


def test_early_compounder_value_destroyer_rejected(monkeypatch):
    """Verify that a stock with severe capital destruction (negative incremental ROIC)
    scores below 40.0 and receives REJECT_KILL_TEST_FAILED, not Watchlist."""
    from app.services.research import early_compounder_engine
    
    # Mock offline fundamentals with negative delta NOPAT
    mock_fund = early_compounder_engine._get_offline_test_mock_fundamentals()
    mock_fund["delta_nopat"] = -45.0  # Deep negative NOPAT on capital
    mock_fund["delta_ic"] = 100.0     # Invested capital expanded by 100 Cr -> inc_roic = -45%
    
    monkeypatch.setattr(early_compounder_engine, "_get_offline_test_mock_fundamentals", lambda: mock_fund)
    
    res = run_early_compounder_engine("CAPITAL_DESTROYER_LTD")
    assert res.strategy_id == "E21"
    assert res.results["early_compounder_score"] < 40.0
    assert res.results["incubator_tier"] == "REJECT_KILL_TEST_FAILED"
    assert res.passed_gates is False


def test_early_compounder_microcap_gate_veto_enforced(monkeypatch):
    """Verify CR-004: When MicrocapRiskFirstGate vetoes an issue (e.g. auditor resignation),
    passed_gates is strictly False and tier is REJECT_KILL_TEST_FAILED."""
    from app.services.strategies import promoter_behaviour
    
    # Mock promoter behaviour to report auditor resignation
    monkeypatch.setattr(
        promoter_behaviour,
        "evaluate_promoter_behaviour",
        lambda symbol, promoter_data=None, as_of=None: {
            "red_flags": ["Auditor resigned abruptly within 6 months"],
            "related_party_pct": 2.0,
            "promoter_holding_pct": 50.0
        }
    )
    res = run_early_compounder_engine("AUDITOR_FRAUD_LTD")
    assert res.passed_gates is False
    assert res.results["incubator_tier"] == "REJECT_KILL_TEST_FAILED"
    assert res.results["risk_first_gate"]["is_investable"] is False
    assert any("auditor" in r.lower() for r in res.risk_warnings)


def test_early_compounder_unobserved_debt_fails_closed(monkeypatch):
    """Verify that unobserved Debt-to-Equity strictly triggers fail-closed data_insufficient in production."""
    import os
    from app.services.research import early_compounder_engine

    # Force production mode
    monkeypatch.setenv("OFFLINE_TEST_MODE", "false")

    # Mock ResearchDataStore to return observations where debt_to_equity is missing
    class MockObs:
        def __init__(self, val):
            self.value = val

    mock_map = {
        "invested_capital": [MockObs(100.0), MockObs(150.0)],
        "ebitda": [MockObs(20.0), MockObs(35.0)],
        # debt_to_equity intentionally omitted to simulate unobserved leverage
    }

    class MockRDS:
        def get_financial_series(self, symbol, as_of=None):
            return [{"pat": 25.0, "cfo": 30.0, "capex": 10.0}]
        def get_financial_observations(self, symbol, as_of=None):
            return mock_map
        def get_company_profile(self, symbol):
            return {"market_cap": 300.0, "current_price": 50.0}

    from app.services import research_data
    monkeypatch.setattr(research_data, "ResearchDataStore", lambda: MockRDS())

    res = early_compounder_engine.run_early_compounder_engine("UNOBSERVED_DEBT_CO")
    assert res.status == "data_insufficient"
    assert res.passed_gates is False
    assert any("DATA_GAP_UNOBSERVED_DEBT" in w for w in res.risk_warnings)



