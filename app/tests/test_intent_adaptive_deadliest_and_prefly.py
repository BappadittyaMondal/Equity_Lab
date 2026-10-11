"""Unit tests for Phase 171 Intent-Adaptive Integration of Deadliest Combo, Pre-Fly, and Micro-Multibagger."""

import pytest
from app.services.research.intent_adaptive_engine import QueryAdaptiveConstraintEngine
from app.services.strategies.registry import run_strategy_module


def test_detect_query_intent_deadliest_and_prefly():
    """Verify natural language query detection for the new archetypes."""
    assert QueryAdaptiveConstraintEngine.detect_query_intent("find deadliest combo stocks for 2026") == "DEADLIEST_COMBO"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("scan for pre-fly stage 1 base coiling setup") == "PRE_FLY"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("micro multibagger sub 15000cr compounder") == "MICRO_MULTIBAGGER"


def test_deadliest_combo_adaptive_constraints_pass():
    """Verify passing evaluation under DEADLIEST_COMBO constraints."""
    data = {
        "market_cap": 3500.0,
        "debt_to_equity": 0.15,
        "pledged_pct": 0.0,
        "roce_latest": 26.5,
        "cfo_pat_ratio": 1.15,
        "circuit_headroom": 5.2,
        "adtv_cr": 8.5,
    }
    res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("DEADLIEST_COMBO", data)
    assert res["passed"] is True
    assert res["status"] == "APPROVED"
    assert len(res["fatal_vetoes"]) == 0
    assert len(res["objective_blocks"]) == 0
    assert any("Universe bounds verified" in t for t in res["tightened_parameters"])


def test_deadliest_combo_adaptive_constraints_blocks_and_veto():
    """Verify hard gate blocks and fatal vetos under DEADLIEST_COMBO."""
    # 1. MCap > 15,000 Cr -> Objective Block
    data_large_mcap = {
        "market_cap": 25000.0,
        "debt_to_equity": 0.10,
        "pledged_pct": 0.0,
        "roce": 25.0,
        "cfo_pat": 1.0,
    }
    res_mcap = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("DEADLIEST_COMBO", data_large_mcap)
    assert res_mcap["passed"] is False
    assert any("outside Deadliest Combo band" in b for b in res_mcap["objective_blocks"])

    # 2. Promoter pledge > 5.0% -> Fatal Veto
    data_pledge = {
        "market_cap": 2000.0,
        "debt_to_equity": 0.10,
        "pledged_pct": 8.5,
        "roce": 25.0,
        "cfo_pat": 1.0,
    }
    res_pledge = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("DEADLIEST_COMBO", data_pledge)
    assert res_pledge["passed"] is False
    assert len(res_pledge["fatal_vetoes"]) == 1
    assert any("FATAL" in v for v in res_pledge["fatal_vetoes"])

    # 3. D/E > 0.35 -> Objective Block
    data_debt = {
        "market_cap": 2000.0,
        "debt_to_equity": 0.65,
        "pledged_pct": 0.0,
        "roce": 25.0,
        "cfo_pat": 1.0,
    }
    res_debt = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("DEADLIEST_COMBO", data_debt)
    assert res_debt["passed"] is False
    assert any("exceeds Deadliest Combo threshold (0.35)" in b for b in res_debt["objective_blocks"])


def test_pre_fly_constraints():
    """Verify PRE_FLY constraints on circuit headroom and liquidity."""
    data_good = {
        "circuit_headroom": 4.5,
        "adtv_cr": 12.0,
    }
    res_good = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("PRE_FLY", data_good)
    assert res_good["passed"] is True
    assert any("Safe circuit headroom verified" in t for t in res_good["tightened_parameters"])

    # Near circuit -> block
    data_locked = {
        "circuit_headroom": 1.2,
        "adtv_cr": 12.0,
    }
    res_locked = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("PRE_FLY", data_locked)
    assert res_locked["passed"] is False
    assert any("Upper circuit headroom" in b for b in res_locked["objective_blocks"])


def test_micro_multibagger_constraints():
    """Verify MICRO_MULTIBAGGER constraints on ROCE and CFO/PAT."""
    data_solid = {
        "market_cap": 850.0,
        "debt_to_equity": 0.10,
        "pledged_pct": 0.0,
        "roce_latest": 24.0,
        "cfo_pat_ratio": 0.95,
    }
    res_solid = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("MICRO_MULTIBAGGER", data_solid)
    assert res_solid["passed"] is True

    # Negative cash conversion -> block
    data_neg_cfo = {
        "market_cap": 850.0,
        "debt_to_equity": 0.10,
        "pledged_pct": 0.0,
        "roce_latest": 24.0,
        "cfo_pat_ratio": -0.20,
    }
    res_cfo = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("MICRO_MULTIBAGGER", data_neg_cfo)
    assert res_cfo["passed"] is False
    assert any("non-positive" in b for b in res_cfo["objective_blocks"])


def test_run_strategy_module_with_deadliest_intent():
    """Verify strategy registry dispatches DEADLIEST_COMBO smoothly."""
    res = run_strategy_module("INTENT_ADAPTIVE", "RELIANCE", intent="DEADLIEST_COMBO")
    assert res.strategy_id == "INTENT_ADAPTIVE"
    assert res.results.get("intent") == "DEADLIEST_COMBO"
