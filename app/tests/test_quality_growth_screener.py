"""Unit tests for Quality-Growth Candidate Screener (Pre-Filter Engine)."""

import pytest
from app.services.strategies.quality_growth_screener import run_quality_growth_screener
from app.models.schemas import QualityGrowthScreenResponse


def test_quality_growth_screener_execution():
    res = run_quality_growth_screener("RELIANCE")
    assert isinstance(res, QualityGrowthScreenResponse)
    assert res.symbol == "RELIANCE.NS"
    assert res.total_conditions == 28
    assert len(res.condition_results) == 28
    assert res.screening_status in ["PASS", "FAIL", "DATA_UNAVAILABLE"]
    assert "growth_quality" in res.quality_growth_profile
    assert "earnings_quality" in res.quality_growth_profile
    assert "thesis_robustness" in res.quality_growth_profile


def test_quality_growth_screener_literal_52w_high_note():
    res = run_quality_growth_screener("RELIANCE")
    c27 = next(c for c in res.condition_results if c.condition_id == "C27")
    assert c27.description == "Down from 52w high > 0"
    assert "literal" in c27.notes.lower()


def test_quality_growth_screener_strategy_registry_integration():
    from app.services.strategies.registry import run_strategy_module
    strat_res = run_strategy_module("E6", "RELIANCE")
    assert strat_res.strategy_id == "E6"
    assert strat_res.status == "production"
    assert "screening_status" in strat_res.results


def test_quality_growth_screener_arbiter_downstream_consumption():
    from app.services.decision_brain.arbiter import Arbiter
    arbiter = Arbiter()
    outputs = arbiter._collect_engine_outputs("RELIANCE")
    e6_output = next((o for o in outputs if o["engine_id"] == "E6"), None)
    assert e6_output is not None, "E6 engine output must be collected by Arbiter"
    assert e6_output["raw"].strategy_id == "E6"
    assert "quality_growth_profile" in e6_output["raw"].results

