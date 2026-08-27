"""Certification Test Suite — Phase 6.

Systematically certifies that all 18 strategy modules (A1-D18) and 17 research engines (E1-E17)
execute cleanly through the canonical registry, returning valid StrategyRunResponse instances with zero unhandled exceptions.
"""

import pytest
from app.services.strategies.registry import (
    STRATEGY_MODULES,
    RESEARCH_ENGINES,
    run_strategy_module
)
from app.models.schemas import StrategyRunResponse


@pytest.mark.parametrize("module_id", list(STRATEGY_MODULES.keys()))
def test_certify_strategy_modules(module_id):
    """Certify each of the 18 Strategy Modules (A1-D18)."""
    res = run_strategy_module(module_id, symbol="RELIANCE")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == module_id
    assert res.status in ["production", "coming_soon", "data_insufficient"]
    assert res.executed_at is not None
    assert res.meta is not None


@pytest.mark.parametrize("engine_id", list(RESEARCH_ENGINES.keys()))
def test_certify_research_engines(engine_id):
    """Certify each of the 17 Research Engines (E1-E17)."""
    res = run_strategy_module(engine_id, symbol="RELIANCE")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == engine_id
    assert res.status in ["production", "coming_soon", "data_insufficient"]
    assert res.executed_at is not None
    assert res.meta is not None
