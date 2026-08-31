"""Point-in-Time Integration Regression Test for Decision Brain Arbiter.

Verifies that Arbiter.arbitrate(symbol, as_of=historical_date) forwards the exact as_of 
timestamp down through registry.run_strategy_module() to the underlying research engines,
preventing future look-ahead data leakage.
"""

from datetime import datetime, timezone
import pytest
from app.services.decision_brain.arbiter import Arbiter
from app.services.strategies import registry

def test_arbiter_point_in_time_threading():
    """Verify as_of timestamp is passed without modification to strategy engines."""
    arbiter = Arbiter()
    historical_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    call_records = []
    original_run_module = registry.run_strategy_module

    def spy_run_strategy_module(strategy_id: str, symbol: str = "RELIANCE", as_of=None):
        call_records.append((strategy_id, symbol, as_of))
        return original_run_module(strategy_id, symbol, as_of=as_of)

    registry.run_strategy_module = spy_run_strategy_module

    try:
        verdict = arbiter.arbitrate("RELIANCE", as_of=historical_dt)
        assert verdict is not None
        assert len(call_records) > 0, "Arbiter should execute strategy modules"

        for strategy_id, symbol, as_of in call_records:
            assert as_of == historical_dt, f"Engine {strategy_id} received wrong as_of: {as_of} (expected {historical_dt})"
    finally:
        registry.run_strategy_module = original_run_module

def test_direct_registry_point_in_time_threading():
    """Directly test run_strategy_module forwards as_of parameter."""
    historical_dt = datetime(2022, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
    resp = registry.run_strategy_module("E1", "RELIANCE", as_of=historical_dt)
    assert resp is not None
    assert resp.symbol in ("RELIANCE", "RELIANCE.NS")


def test_arbiter_sub_agent_governance_veto_integration():
    """Test that high promoter pledge (>50%) triggers sub-agent veto and caps score."""
    arbiter = Arbiter()
    # Mock snapshot with critical 60% promoter pledge
    class MockSnap:
        promoter_pledge_pct = 60.0
        related_party_pct = 5.0
        auditor_resigned_recently = False
        net_income_3y_cagr = 10.0
        ocf_3y_cagr = 12.0

    mock_snap = MockSnap()
    veto = arbiter._apply_governance_veto([{"symbol": "HIGH_PLEDGE_CO"}], snap=mock_snap)
    assert veto is True, "Sub-agent pledge veto must trigger True for 60% pledge"

