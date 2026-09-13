"""Tests for Phase 26 Thread-Safe Request-Scoped Intent Routing & Gate Taxonomy Alignment."""

import pytest
from app.services.research.intent_adaptive_engine import QueryAdaptiveConstraintEngine
from app.services.strategies.registry import run_strategy_module
from app.models.schemas import StrategyRunRequest


def test_evaluate_adaptive_constraints_4tier_alignment():
    """Verify objective blocks vs fatal vetoes distinction."""
    # Turnaround with low interest coverage -> Objective Block (not fatal accounting fraud)
    distressed_data = {
        "interest_coverage": 1.1,
        "cfo_pat": 0.5,
        "pledged_pct": 5.0
    }
    res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("TURNAROUND", distressed_data)
    assert not res["passed"]
    assert len(res["objective_blocks"]) >= 1
    assert any("OBJECTIVE_BLOCK" in b for b in res["objective_blocks"])
    assert len(res["fatal_vetoes"]) == 0
    assert len(res["vetoes"]) == len(res["objective_blocks"])

    # High promoter pledge in microcap -> Fatal Veto
    fraud_risk_data = {
        "promoter_holding": 55.0,
        "pledged_pct": 25.0
    }
    res_mcap = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("EARLY_MICROCAP", fraud_risk_data)
    assert not res_mcap["passed"]
    assert len(res_mcap["fatal_vetoes"]) >= 1
    assert any("FATAL" in v for v in res_mcap["fatal_vetoes"])


def test_run_strategy_module_with_request_scoped_intent():
    """Verify run_strategy_module evaluates per-request intent without relying on global env."""
    res_turn = run_strategy_module("INTENT_ADAPTIVE", "RELIANCE", intent="TURNAROUND")
    assert res_turn.strategy_id == "INTENT_ADAPTIVE"
    assert res_turn.results.get("intent") == "TURNAROUND"

    res_sip = run_strategy_module("INTENT_ADAPTIVE", "RELIANCE", intent="SIP_COMPOUNDER")
    assert res_sip.results.get("intent") == "SIP_COMPOUNDER"

    # Natural language query text classification
    res_nlp = run_strategy_module("INTENT_ADAPTIVE", "RELIANCE", query_text="find multibagger compounder for coffee can portfolio")
    assert res_nlp.results.get("intent") in ("SIP_COMPOUNDER", "EARLY_MICROCAP")


def test_strategy_run_request_schema_serialization():
    """Verify StrategyRunRequest accepts and preserves query_intent, query_text, visual_features."""
    req = StrategyRunRequest(
        symbol="TATAMOTORS",
        query_intent="TURNAROUND",
        query_text="will tatamotors recover from distress",
        visual_features={"visual_price": 750.0}
    )
    assert req.query_intent == "TURNAROUND"
    assert req.query_text == "will tatamotors recover from distress"
    assert req.visual_features == {"visual_price": 750.0}
