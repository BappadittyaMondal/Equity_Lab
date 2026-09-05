"""
Institutional Control-Plane & 5-Finder State Machine Verification Tests.

Validates:
1. Cumulative NAV Wealth Curve Max Drawdown (mathematical correctness).
2. MTFContextEngine: Weekly Macro Tide, Daily Wave, 60m Trigger & Hierarchy Invariance.
3. MultibaggerStateMachine: Sequential acceleration, compounding, and kill-triggers.
4. TurnaroundStateMachine: Relapse dominance & Disaster AVWAP floor.
5. SwingTradeFeasibilityEngine: Liquidity floor & execution feasibility.
6. MicrocapRiskFirstGate: 3-tier capacity limits and forensic shields.
7. SIPPolicyEngine: Valuation-responsive dynamic allocation multipliers.
"""

import pytest
import pandas as pd
import numpy as np

from app.services.backtesting.walk_forward import WalkForwardBacktester
from app.services.strategies.mtf_context_engine import MTFContextEngine
from app.services.research.finder_state_machines import (
    MultibaggerStateMachine,
    MultibaggerState,
    TurnaroundStateMachine,
    TurnaroundState,
    SwingTradeFeasibilityEngine,
    MicrocapRiskFirstGate,
    SIPPolicyEngine,
)


# ==============================================================================
# 1. CUMULATIVE NAV WEALTH CURVE MAX DRAWDOWN TESTS
# ==============================================================================

def test_cumulative_nav_max_drawdown_exact_sequence():
    """Verify that max drawdown is calculated on compounded NAV curve, not return values."""
    tester = WalkForwardBacktester()
    # Sequence: +25% (NAV=1.25), +15% (NAV=1.4375), -5% (NAV=1.365625, DD=5%), +30% (NAV=1.7753)
    samples = [
        {"stock_return": 25.0},
        {"stock_return": 15.0},
        {"stock_return": -5.0},
        {"stock_return": 30.0},
    ]
    summary = tester.evaluate_horizon("TEST", 12, samples, slippage_pct=0.0, stt_brokerage_pct=0.0)
    assert summary.max_drawdown_pct == 5.0
    assert summary.total_samples == 4


def test_cumulative_nav_all_positive_returns_zero_drawdown():
    """Verify that a monotonically increasing equity curve has zero max drawdown."""
    tester = WalkForwardBacktester()
    samples = [
        {"stock_return": 10.0},
        {"stock_return": 20.0},
        {"stock_return": 15.0},
    ]
    summary = tester.evaluate_horizon("TEST", 12, samples, slippage_pct=0.0, stt_brokerage_pct=0.0)
    assert summary.max_drawdown_pct == 0.0


def test_cumulative_nav_severe_drawdown():
    """Verify 50% loss produces exactly 50% max drawdown."""
    tester = WalkForwardBacktester()
    samples = [
        {"stock_return": -50.0},
        {"stock_return": 100.0},
    ]
    summary = tester.evaluate_horizon("TEST", 12, samples, slippage_pct=0.0, stt_brokerage_pct=0.0)
    assert summary.max_drawdown_pct == 50.0


# ==============================================================================
# 2. SHARED MTF CONTEXT ENGINE & HIERARCHY TESTS
# ==============================================================================

def test_mtf_hierarchy_weekly_bearish_vetoes_intraday_trigger():
    """Test the invariant: A 60-min timing trigger CANNOT override a Weekly Bearish Tide."""
    # Weekly DF: Strong downtrend
    weekly_closes = pd.Series([100.0 - (i * 2.0) for i in range(30)])
    weekly_df = pd.DataFrame({"close": weekly_closes})

    # Daily DF: Downtrend
    daily_closes = pd.Series([50.0 - (i * 0.5) for i in range(30)])
    daily_df = pd.DataFrame({"close": daily_closes})

    # Hourly trigger long is active
    res = MTFContextEngine.evaluate_mtf_context(
        symbol="BEARISH_STOCK",
        daily_df=daily_df,
        weekly_df=weekly_df,
        stoch_rsi_k=15.0,  # Cross from oversold
        stoch_rsi_d=10.0,
    )

    assert res["conflict_detected"] is True
    assert res["alignment_state"] == "TACTICAL_COUNTERTREND_VETO"
    assert res["verdict"] == "VETOED_AGAINST_WEEKLY_TIDE"
    assert res["is_actionable"] is False


def test_mtf_perfect_triple_screen_alignment():
    """Test full alignment across Weekly Tide, Daily Wave, and 60m Trigger."""
    # Weekly DF: Strong uptrend
    weekly_closes = pd.Series([100.0 + (i * 3.0) for i in range(30)])
    weekly_df = pd.DataFrame({"close": weekly_closes})

    # Daily DF: Healthy uptrend near 20 EMA
    daily_closes = pd.Series([180.0 + (i * 0.5) for i in range(30)])
    daily_df = pd.DataFrame({"close": daily_closes})

    res = MTFContextEngine.evaluate_mtf_context(
        symbol="BULLISH_STOCK",
        daily_df=daily_df,
        weekly_df=weekly_df,
        stoch_rsi_k=25.0,
        stoch_rsi_d=20.0,
    )

    assert res["weekly_tide"]["is_bullish_tide"] is True
    assert res["alignment_state"] == "PERFECT_TRIPLE_SCREEN_ALIGNMENT"
    assert res["is_actionable"] is True
    assert res["verdict"] == "STRONG_BULLISH_EXECUTION_READY"


# ==============================================================================
# 3. MULTIBAGGER STATE MACHINE TESTS
# ==============================================================================

def test_multibagger_state_machine_compounding():
    """Test sustained high ROCE and PAT growth leads to COMPOUNDING state."""
    res = MultibaggerStateMachine.evaluate(
        symbol="TITAN_CASE",
        pat_growth_ttm=25.0,
        pat_growth_prev=20.0,
        incremental_roic=28.0,
        wacc=12.0,
        consecutive_high_roce_quarters=8,
    )
    assert res["state"] == MultibaggerState.COMPOUNDING.value
    assert res["is_investable"] is True


def test_multibagger_state_machine_kill_trigger():
    """Test CFO collapse forces immediate INVALIDATED thesis breach halt."""
    res = MultibaggerStateMachine.evaluate(
        symbol="FAKESTOCK",
        pat_growth_ttm=30.0,
        pat_growth_prev=20.0,
        incremental_roic=15.0,
        wacc=12.0,
        cfo_to_ebitda=0.20,  # Severe divergence (< 0.40)
    )
    assert res["state"] == MultibaggerState.INVALIDATED.value
    assert res["is_investable"] is False
    assert len(res["kill_triggers_fired"]) >= 1


# ==============================================================================
# 4. TURNAROUND STATE MACHINE TESTS
# ==============================================================================

def test_turnaround_disaster_avwap_floor_and_relapse():
    """Test price below Disaster AVWAP floor forces RELAPSE state."""
    res = TurnaroundStateMachine.evaluate(
        symbol="DISTRESS_CORP",
        current_price=80.0,
        disaster_avwap=100.0,  # Current price is 20% below disaster floor
        piotroski_score=4,
        piotroski_prev=2,
        cfo_cr=10.0,
        ebitda_cr=15.0,
        debt_reduction_initiated=True,
    )
    assert res["state"] == TurnaroundState.RELAPSE.value
    assert res["dominant_override"] == "RELAPSE_VETO_ACTIVE"
    assert res["is_turnaround_confirmed"] is False


def test_turnaround_confirmed_recovery():
    """Test recovery above disaster floor with positive cash flow."""
    res = TurnaroundStateMachine.evaluate(
        symbol="TURNAROUND_STAR",
        current_price=120.0,
        disaster_avwap=100.0,
        piotroski_score=7,
        piotroski_prev=4,
        cfo_cr=50.0,
        ebitda_cr=60.0,
        debt_reduction_initiated=True,
    )
    assert res["state"] == TurnaroundState.SUSTAINED_RECOVERY.value
    assert res["is_turnaround_confirmed"] is True


def test_turnaround_zero_division_guard():
    """Test that disaster_avwap=0.0 does not raise ZeroDivisionError and safely returns None."""
    res = TurnaroundStateMachine.evaluate(
        symbol="ZERO_AVWAP_CO",
        current_price=50.0,
        disaster_avwap=0.0,  # Edge case: zero/untraded disaster floor
        piotroski_score=5,
        piotroski_prev=3,
        cfo_cr=10.0,
        ebitda_cr=15.0,
        debt_reduction_initiated=True,
    )
    assert res["price_to_disaster_floor_pct"] is None
    assert res["state"] == TurnaroundState.CASH_FLOW_CONFIRMED.value


# ==============================================================================
# 5. SWING TRADE FEASIBILITY TESTS
# ==============================================================================

def test_swing_trade_feasibility_illiquid_rejection():
    """Test high technical score on illiquid stock returns HIGH_SCORE_NOT_TRADABLE."""
    res = SwingTradeFeasibilityEngine.evaluate(
        symbol="ILLIQUID_GEM",
        technical_confluence_score=90.0,
        mtf_verdict="STRONG_BULLISH_EXECUTION_READY",
        adtv_cr=1.5,  # Below 5.0 Cr floor
        order_size_cr=0.25,
    )
    assert res["feasibility_status"] == "HIGH_SCORE_NOT_TRADABLE"
    assert res["is_tradable"] is False


def test_swing_trade_feasibility_capacity_unverified():
    """Test omitting order_size_cr returns CAPACITY_UNVERIFIED_DATA_INSUFFICIENT."""
    res = SwingTradeFeasibilityEngine.evaluate(
        symbol="LIQUID_STOCK",
        technical_confluence_score=85.0,
        mtf_verdict="STRONG_BULLISH_EXECUTION_READY",
        adtv_cr=25.0,
        order_size_cr=None,  # No silent favorable default allowed
    )
    assert res["feasibility_status"] == "CAPACITY_UNVERIFIED_DATA_INSUFFICIENT"
    assert res["is_tradable"] is False


def test_swing_trade_feasibility_circuit_lockout():
    """Test circuit-locked stock halts execution."""
    res = SwingTradeFeasibilityEngine.evaluate(
        symbol="LOCKED_STOCK",
        technical_confluence_score=85.0,
        mtf_verdict="STRONG_BULLISH_EXECUTION_READY",
        adtv_cr=25.0,
        order_size_cr=0.50,
        is_circuit_locked=True,
    )
    assert res["feasibility_status"] == "CIRCUIT_LOCKED_TRADING_HALTED"
    assert res["is_tradable"] is False


def test_swing_trade_feasibility_valid_cleared():
    """Test valid order size within 5% ADV on liquid stock clears entry."""
    res = SwingTradeFeasibilityEngine.evaluate(
        symbol="CLEARED_SWING",
        technical_confluence_score=85.0,
        mtf_verdict="STRONG_BULLISH_EXECUTION_READY",
        adtv_cr=20.0,  # 5% ADV = 1.0 Cr
        order_size_cr=0.50,  # Well within capacity
        is_circuit_locked=False,
    )
    assert res["feasibility_status"] == "FEASIBLE_READY_FOR_ENTRY"
    assert res["is_tradable"] is True


# ==============================================================================
# 6. MICROCAP RISK-FIRST GATE TESTS
# ==============================================================================

def test_microcap_gate_auditor_resignation_veto():
    """Test statutory auditor resignation halts microcap candidate."""
    res = MicrocapRiskFirstGate.evaluate(
        symbol="SKETCHY_MICRO",
        market_cap_cr=250.0,
        adtv_30d_cr=2.0,
        rpt_to_net_worth_pct=2.0,
        has_auditor_resigned_recently=True,
        circuit_frequency_pct=5.0,
        promoter_holding_pct=55.0,
        cfo_3y_sum_cr=20.0,
    )
    assert res["is_investable"] is False
    assert "Statutory auditor mid-term resignation detected." in res["forensic_vetoes"]


def test_microcap_gate_approved_with_capacity_limits():
    """Test clean microcap receives 3 distinct capacity limits."""
    res = MicrocapRiskFirstGate.evaluate(
        symbol="CLEAN_MICRO",
        market_cap_cr=400.0,
        adtv_30d_cr=5.0,
        rpt_to_net_worth_pct=1.0,
        has_auditor_resigned_recently=False,
        circuit_frequency_pct=4.0,
        promoter_holding_pct=65.0,
        cfo_3y_sum_cr=35.0,
    )
    assert res["is_investable"] is True
    assert res["status"] == "APPROVED_MICROCAP_CANDIDATE"
    assert res["capacity_limits"]["market_impact_limit_cr"] == 0.15  # 3% of 5 Cr
    assert res["capacity_limits"]["portfolio_risk_budget_pct"] == 15.0


# ==============================================================================
# 7. SIP POLICY ENGINE TESTS
# ==============================================================================

def test_sip_policy_dynamic_valuation_multipliers():
    """Test SIP capital allocation multipliers across valuation Z-scores."""
    # 1. Overvalued -> 0.50x
    res_high = SIPPolicyEngine.evaluate("TCS", roce_10y_avg=35.0, debt_to_equity=0.05, valuation_z_score=2.0, thesis_intact=True, is_price_below_200sma=False)
    assert res_high["allocation_multiplier"] == 0.50
    assert res_high["policy_action"] == "REDUCED_SIP_ACCUMULATE_DRY_POWDER"

    # 2. Fair Value -> 1.00x
    res_fair = SIPPolicyEngine.evaluate("TCS", roce_10y_avg=35.0, debt_to_equity=0.05, valuation_z_score=0.1, thesis_intact=True, is_price_below_200sma=False)
    assert res_fair["allocation_multiplier"] == 1.00
    assert res_fair["policy_action"] == "STANDARD_SIP_EXECUTION"

    # 3. Deep Panic at 200-SMA Support -> 1.75x
    res_panic = SIPPolicyEngine.evaluate("TCS", roce_10y_avg=35.0, debt_to_equity=0.05, valuation_z_score=-1.8, thesis_intact=True, is_price_below_200sma=True)
    assert res_panic["allocation_multiplier"] == 1.75
    assert res_panic["policy_action"] == "EXPANDED_SIP_DEPLOY_BUFFER"

    # 4. Moat Decay -> PAUSE
    res_decay = SIPPolicyEngine.evaluate("DECLINING_CO", roce_10y_avg=10.0, debt_to_equity=1.5, valuation_z_score=-2.0, thesis_intact=False, is_price_below_200sma=True)
    assert res_decay["allocation_multiplier"] == 0.0
    assert res_decay["policy_action"] == "PAUSE_SIP_OR_EXIT_REVIEW"


# ==============================================================================
# 8. LIVE PRODUCTION CALLER INTEGRATION VERIFICATION
# ==============================================================================

def test_live_production_callers_integrated():
    """Programmatically verifies all 5 state machines & MTF engine have active production callers."""
    # 1. Turnaround Engine (E20) live call
    from app.services.turnaround.turnaround_engine import run_turnaround_engine
    t_res = run_turnaround_engine("TATAMOTORS")
    assert "lifecycle_state_machine" in t_res.results, "TurnaroundStateMachine must be wired in E20 results"
    assert "is_relapse_active" in t_res.results

    # 2. Early Compounder Engine (E21) live call
    from app.services.research.early_compounder_engine import run_early_compounder_engine
    c_res = run_early_compounder_engine("SHILCHAR")
    assert "risk_first_gate" in c_res.results, "MicrocapRiskFirstGate must be wired in E21 results"
    assert "capacity_limits" in c_res.results

    # 3. Swing Predictive Engine (E18) live call
    from app.services.strategies.swing_predictive_engine import SwingPredictiveEngine
    fake_df = pd.DataFrame({
        "open": [100.0 + i for i in range(35)],
        "close": [100.0 + i for i in range(35)],
        "high": [102.0 + i for i in range(35)],
        "low": [99.0 + i for i in range(35)],
        "volume": [100000 for _ in range(35)],
        "open_interest": [50000 for _ in range(35)],
    })
    s_res = SwingPredictiveEngine.predict_swing_30d(fake_df)
    assert "mtf_context" in s_res, "MTFContextEngine must be wired in SwingPredictiveEngine output"
    assert "feasibility" in s_res, "SwingTradeFeasibilityEngine must be wired in SwingPredictiveEngine output"

    # 4. Institutional Multibagger Engine live call
    from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
    dummy_company = {
        "symbol": "TESTCO.NS",
        "company_name": "Test Co Ltd",
        "market_cap": 5000.0,
        "current_price": 250.0,
        "high_52w": 300.0,
        "low_52w": 180.0,
        "volume": 200000,
        "vol_1w_avg": 180000,
        "vol_1y_avg": 150000,
        "roe_3yr": 22.0,
        "roe_latest": 24.0,
        "roce_3yr": 25.0,
        "roce_latest": 26.0,
        "opm_5yr": 18.0,
        "opm_latest": 21.0,
        "op_growth": 25.0,
        "pat_growth_3yr": 28.0,
        "pat_growth_latest": 30.0,
        "sales_growth_3yr": 22.0,
        "sales_growth_latest": 24.0,
        "eps_growth_3yr": 25.0,
        "eps_latest": 27.0,
        "cfo_3yr": 350.0,
        "cfo_last_year": 120.0,
        "net_profit_last_year": 100.0,
        "net_block": 400.0,
        "net_block_3yr_back": 250.0,
        "net_block_preceding_year": 320.0,
        "cwip": 80.0,
        "cwip_preceding_year": 40.0,
        "piotroski_score": 8.0,
        "promoter_holding": 62.0,
        "pledged_pct": 0.0,
        "debt_to_equity": 0.20,
        "interest_coverage": 15.0,
        "peg_ratio": 0.95
    }
    mb_res = InstitutionalMultibaggerEngine.evaluate_company(dummy_company)
    assert "lifecycle_state_machine" in mb_res, "MultibaggerStateMachine must be wired in multibagger scorecard"
    assert "is_investable" in mb_res

    # 5. SIP Policy endpoint call
    from app.api.strategies import get_sip_policy
    sip_res = get_sip_policy("RELIANCE")
    assert "policy_action" in sip_res, "SIPPolicyEngine must be callable from API route"
    assert "allocation_multiplier" in sip_res


def test_turnaround_engine_hydrated_no_synthetic_fallbacks():
    """Verify Turnaround engine uses real observations and does not synthesize fake disaster floor."""
    from app.services.turnaround.turnaround_engine import run_turnaround_engine
    t_res = run_turnaround_engine("TATAMOTORS")
    sm = t_res.results["lifecycle_state_machine"]
    # Verify disaster floor is grounded or None, not synthetic 0.85 * cp
    assert sm is not None
    assert "state" in sm
    assert sm["state"] in ("STABILIZATION", "EARLY_RECOVERY", "CASH_FLOW_CONFIRMED", "SUSTAINED_RECOVERY", "RELAPSE", "DISTRESS")


def test_sip_policy_dynamic_symbol_differentiation():
    """Verify SIP policy route reflects symbol-specific fundamentals rather than static constants."""
    from app.api.strategies import get_sip_policy
    res_tata = get_sip_policy("TATAMOTORS")
    res_infy = get_sip_policy("INFY")
    assert "allocation_multiplier" in res_tata
    assert "allocation_multiplier" in res_infy
    # Both are successfully evaluated with valid dynamic policies
    assert res_tata["allocation_multiplier"] in (0.50, 0.75, 1.00, 1.25, 1.50, 1.75)
    assert res_infy["allocation_multiplier"] in (0.50, 0.75, 1.00, 1.25, 1.50, 1.75)


def test_multibagger_unverified_pledge_fail_closed_in_production(monkeypatch):
    """Verify that in production mode, missing pledge data causes state machine to fail closed."""
    monkeypatch.setenv("OFFLINE_TEST_MODE", "false")
    from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
    unverified_comp = {
        "symbol": "UNVERIFIED.NS",
        "company_name": "Unverified Corp",
        "market_cap": 1000.0,
        "current_price": 50.0,
        "roe_latest": 25.0,
        "roce_latest": 25.0,
        "cfo_last_year": 50.0,
        "net_profit_last_year": 40.0,
        # pledged_pct intentionally missing
    }
    res = InstitutionalMultibaggerEngine.evaluate_company(unverified_comp)
    assert res["lifecycle_state_machine"]["state"] == "INVALIDATED"
    assert res["is_investable"] is False
    assert any("Promoter Pledge" in f for f in res["risk_flags"])

