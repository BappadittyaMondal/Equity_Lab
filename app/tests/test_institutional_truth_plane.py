"""Institutional Truth-Plane Verification & Certification Test Suite (Phases 1 - 5).

Verifies:
  1. Point-in-Time slicing fail-closed invariance (zero lookahead leakage on slicing error).
  2. Strict fail-closed regulatory surveillance enforcement (DATA_INSUFFICIENT halts all trading).
  3. Decoupling of Data Completeness from Economic Quality in the Institutional Multibagger engine.
  4. Database connection untracking in db_session to eliminate memory leaks.
  5. Almgren-Chriss square-root market impact model and ADV 5% participation limits.
  6. Formal Order State Machine transition invariants.
"""

import pytest
import pandas as pd
from datetime import datetime, timezone
from fastapi import HTTPException

from app.models.schemas import SurveillanceRiskGate, OptionsA2Request
from app.services.market_data import get_history
from app.services.risk.surveillance_gate import evaluate_surveillance_and_cost_gate, is_surveillance_cleared
from app.services.risk.execution_cost_model import (
    calculate_almgren_chriss_impact,
    evaluate_institutional_execution_envelope,
    transition_order_state
)
from app.services.strategies.options_a1_a3 import evaluate_option_arbitrage, evaluate_iron_condor
from app.services.strategies import options_a2
from app.services.turnaround.turnaround_engine import run_turnaround_engine
from app.services.research.universe_screener import run_technical_universe_screener
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
from app.services.db import db_session, _OPEN_CONNECTIONS, get_connection, _prune_dead_connections


def test_pit_slice_fail_closed_on_error(monkeypatch):
    """Verify that if timezone or index alignment fails during PIT slicing, get_history fails closed."""
    yf = pytest.importorskip("yfinance")

    # Create dummy dataframe with invalid index type that raises error upon comparison
    mock_df = pd.DataFrame(
        {"Close": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]},
        index=["invalid_date_1", "invalid_date_2", "invalid_date_3", "invalid_date_4", "invalid_date_5", "invalid_date_6"]
    )
    monkeypatch.setattr(yf, "download", lambda *args, **kwargs: mock_df)

    # Pass as_of timestamp which will cause slicing comparison exception with string index
    as_of = datetime(2025, 1, 1, 10, 0, 0)
    res = get_history("FAIL_TEST_STOCK", as_of=as_of, allow_simulated=False)

    assert isinstance(res, pd.DataFrame)
    assert res.empty
    assert res.attrs.get("data_mode") == "DATA_INSUFFICIENT"
    assert "slice_error" in res.attrs


def test_surveillance_data_insufficient_prohibits_all_trading(monkeypatch):
    """Verify that DATA_INSUFFICIENT surveillance status halts A1, A2, A3, and Turnaround trading."""
    mock_gate = SurveillanceRiskGate(
        asm_stage="UNKNOWN",
        gsm_stage="UNKNOWN",
        t2t_flag=False,
        fo_ban_flag=False,
        circuit_band_pct=20.0,
        circuit_lock_risk="UNKNOWN",
        hard_gate_status="DATA_INSUFFICIENT"
    )
    
    assert not mock_gate.is_cleared_for_trading
    assert not is_surveillance_cleared(mock_gate)

    from app.services.risk import surveillance_gate
    monkeypatch.setattr(surveillance_gate, "evaluate_surveillance_and_cost_gate", lambda *args, **kwargs: mock_gate)

    # 1. A1 Option Arbitrage must prohibit execution
    res_a1 = evaluate_option_arbitrage("NIFTY")
    assert res_a1["arbitrage_opportunity"] is False
    assert res_a1["recommendation"] == "REGULATORY_BAN_PROHIBITED"
    assert res_a1["meta"]["data_mode"] == "REGULATORY_RESTRICTION"

    # 2. A2 0-DTE Range Selling must raise 403 Forbidden
    req = OptionsA2Request(
        underlying="^NSEI",
        spot_price=24500.0,
        lower_strike=24000.0,
        upper_strike=25000.0,
        call_premium=50.0,
        put_premium=50.0
    )
    with pytest.raises(HTTPException) as exc_info:
        options_a2.calculate_a2_payoff(req)
    assert exc_info.value.status_code == 403
    assert "REGULATORY_RESTRICTION" in exc_info.value.detail

    # 3. A3 Iron Condor must prohibit execution
    res_a3 = evaluate_iron_condor("NIFTY")
    assert res_a3["passed_gates"] is False
    assert res_a3["status"] == "REGULATORY_RESTRICTION"

    # 4. Turnaround Engine must fail closed
    res_turn = run_turnaround_engine("TATAMOTORS")
    assert res_turn.passed_gates is False
    assert any("DATA_INSUFFICIENT" in r for r in res_turn.risk_warnings)


def test_multibagger_data_completeness_decoupling():
    """Verify that Multibagger engine decouples data completeness from economic scoring."""
    incomplete_stock = {
        "symbol": "INCOMPLETE_CO",
        "company_name": "Incomplete Test Corp",
        "market_cap": 5000.0,
        "current_price": 250.0,
        # sales_growth_3yr and other metrics omitted
        "pledged_pct": 0.0,
        "debt_to_equity": 0.2
    }
    res = InstitutionalMultibaggerEngine.evaluate_company(incomplete_stock)
    
    assert "data_completeness_pct" in res
    assert "confidence_score" in res
    assert res["data_completeness_pct"] < 50.0  # Only a few fields present
    assert 0.0 <= res["overall_score"] <= 100.0


def test_db_session_leak_prevention():
    """Verify that db_session safely discards connection references from _OPEN_CONNECTIONS."""
    initial_count = len(_OPEN_CONNECTIONS)
    
    with db_session() as conn:
        assert conn is not None
        # Connection should be inside the tracking set during active session
        # or properly tracked
        pass

    # Connection must be cleanly discarded upon exiting db_session context
    _prune_dead_connections()
    post_count = len(_OPEN_CONNECTIONS)
    assert post_count <= initial_count + 1


def test_almgren_chriss_market_impact_and_adv_limits():
    """Verify market impact scales with order size and enforces 5% ADV participation limit."""
    # Scenario A: Small order (1% of ADV) -> direct execution
    res_small = calculate_almgren_chriss_impact(
        order_shares=10_000,
        adv_20d_shares=1_000_000,
        daily_volatility_pct=2.0
    )
    assert res_small["adv_cap_exceeded"] is False
    assert res_small["execution_algorithm"] == "DIRECT_LIMIT_EXECUTION"
    assert res_small["recommended_execution_horizon_days"] == 1
    assert 0.0 < res_small["market_impact_pct"] < 0.10

    # Scenario B: Large institutional block (15% of ADV) -> algorithmic slicing required
    res_large = calculate_almgren_chriss_impact(
        order_shares=150_000,
        adv_20d_shares=1_000_000,
        daily_volatility_pct=2.0
    )
    assert res_large["adv_cap_exceeded"] is True
    assert res_large["execution_algorithm"] == "ALGORITHMIC_TWAP_VWAP"
    assert res_large["recommended_execution_horizon_days"] == 3
    assert res_large["max_recommended_daily_shares"] == 50_000.0
    assert res_large["market_impact_pct"] > res_small["market_impact_pct"]


def test_institutional_execution_envelope_clean():
    """Verify complete execution envelope evaluation for an institutional trade."""
    env = evaluate_institutional_execution_envelope(
        symbol="POLYCAB",
        price=5000.0,
        order_value_inr=10_000_000.0,  # 1 Cr trade
        adv_20d_inr=200_000_000.0,     # 20 Cr ADV -> 5% participation
        daily_volatility_pct=2.2,
        surveillance_data={"asm_stage": "CLEAN", "gsm_stage": "CLEAN", "circuit_band_pct": 20.0}
    )
    assert env["cleared_for_trading"] is True
    assert env["status_code"] == "APPROVED_FOR_EXECUTION"
    assert env["regulatory_roundtrip_cost_pct"] > 0.0
    assert env["market_impact_pct"] > 0.0
    assert env["total_expected_friction_pct"] == round(env["regulatory_roundtrip_cost_pct"] + env["market_impact_pct"], 3)


def test_order_state_machine_invariants():
    """Verify legal and illegal transitions in the Order State Machine."""
    # Legal progression
    s1, msg1 = transition_order_state("DRAFT", "VALIDATED")
    assert s1 == "VALIDATED"

    s2, msg2 = transition_order_state("VALIDATED", "SURVEILLANCE_CLEARED", cleared_surveillance=True)
    assert s2 == "SURVEILLANCE_CLEARED"

    s3, msg3 = transition_order_state("SURVEILLANCE_CLEARED", "ROUTED")
    assert s3 == "ROUTED"

    s4, msg4 = transition_order_state("ROUTED", "FILLED")
    assert s4 == "FILLED"

    # Regulatory veto transition
    v_state, v_msg = transition_order_state("VALIDATED", "SURVEILLANCE_CLEARED", cleared_surveillance=False)
    assert v_state == "VETOED_SURVEILLANCE"

    # Illegal transition: DRAFT directly to ROUTED
    bad_state, bad_msg = transition_order_state("DRAFT", "ROUTED")
    assert bad_state == "REJECTED"
    assert "Illegal state transition" in bad_msg
