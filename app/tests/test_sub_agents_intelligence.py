"""Unit tests for Sub-Agent Intelligence Layer & Virtual IC Arbiter.
"""

import pytest
from app.services.intelligence.event_extractor import FindingSeverity
from app.services.intelligence.sub_agents import (
    ForensicAuditorSubAgent,
    SupplyChainCatalystSubAgent,
    RedTeamBearCaseSubAgent,
)
from app.services.intelligence.arbiter import VirtualICArbiter


def test_forensic_auditor_sub_agent():
    agent = ForensicAuditorSubAgent()
    rep = agent.evaluate("RELIANCE", ownership_snapshot={"promoter_pledge_pct": 30.0})
    assert rep.symbol == "RELIANCE"
    assert len(rep.findings) == 1
    assert rep.findings[0].severity == FindingSeverity.HIGH_PENALTY
    assert rep.findings[0].thesis_invalidation_trigger is not None

    # Test 45.0% (>40.0%) triggers CRITICAL_RED_FLAG
    rep_crit = agent.evaluate("HIGH_PLEDGE", ownership_snapshot={"promoter_pledge_pct": 45.0})
    assert rep_crit.findings[0].severity == FindingSeverity.CRITICAL_RED_FLAG


def test_supply_chain_catalyst_sub_agent():
    agent = SupplyChainCatalystSubAgent()
    rep = agent.evaluate("TATA-POWER", sector="Power")
    assert rep.findings[0].severity == FindingSeverity.POSITIVE_CATALYST

    # Test case and whitespace normalization
    rep_norm = agent.evaluate("INFRA_CO", sector="  infrastructure  ")
    assert rep_norm.findings[0].severity == FindingSeverity.POSITIVE_CATALYST


def test_red_team_bear_case_sub_agent():
    agent = RedTeamBearCaseSubAgent()
    rep = agent.evaluate("LEVERAGED", de_ratio=2.0)
    assert rep.findings[0].severity == FindingSeverity.HIGH_PENALTY


def test_virtual_ic_arbiter_synthesis():
    forensic = ForensicAuditorSubAgent().evaluate("STK1", ownership_snapshot={"promoter_pledge_pct": 30.0})
    supply = SupplyChainCatalystSubAgent().evaluate("STK1", sector="Power")
    red_team = RedTeamBearCaseSubAgent().evaluate("STK1", de_ratio=0.5)

    arbiter = VirtualICArbiter()
    synth = arbiter.synthesize([forensic, supply, red_team], base_score=75.0)

    assert synth["base_score"] == 75.0
    assert "adjusted_score" in synth
    assert synth["is_halted"] is False
    assert len(synth["invalidation_triggers"]) >= 1


def test_virtual_ic_arbiter_critical_red_flag():
    critical = ForensicAuditorSubAgent().evaluate("BADCO", ownership_snapshot={"promoter_pledge_pct": 60.0})
    arbiter = VirtualICArbiter()
    synth = arbiter.synthesize([critical], base_score=75.0)
    assert synth["is_halted"] is True


def test_ai_committee_api_endpoints():
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)

    res_forensics = client.get("/api/v1/research/ai-committee/forensics/SHILCHAR")
    assert res_forensics.status_code == 200
    assert "forensic_risk_level" in res_forensics.json()

    res_evt = client.get("/api/v1/research/ai-committee/evt-tail/SHILCHAR")
    assert res_evt.status_code == 200
    assert "scale_sigma" in res_evt.json()
    assert "shape_xi" in res_evt.json()


def test_incremental_roic_sub_agent():
    from app.services.intelligence.sub_agents import IncrementalROICSubAgent
    agent = IncrementalROICSubAgent()

    # High inflection test: ΔNOPAT 30 on ΔInvested Capital 100 -> 30% inc ROIC
    rep_high = agent.evaluate("INFLECTING_CO", delta_nopat=30.0, delta_invested_capital=100.0, trailing_roce=14.0)
    assert rep_high.findings[0].severity == FindingSeverity.POSITIVE_CATALYST
    assert "surging" in rep_high.findings[0].evidence

    # Poor return test: ΔNOPAT 5 on ΔInvested Capital 100 -> 5% inc ROIC
    rep_low = agent.evaluate("POOR_CAPEX", delta_nopat=5.0, delta_invested_capital=100.0)
    assert rep_low.findings[0].severity == FindingSeverity.HIGH_PENALTY


def test_reverse_valuation_sub_agent():
    from app.services.intelligence.sub_agents import ReverseValuationSubAgent
    agent = ReverseValuationSubAgent()

    # Feasible: 3x target over 4Y
    rep_feas = agent.evaluate("GROWTH_CO", current_market_cap_cr=200.0, current_revenue_cr=150.0, target_multiple=3.0, target_years=4)
    assert rep_feas.findings[0].severity == FindingSeverity.POSITIVE_CATALYST

    # Implausible: 10x target on tiny revenue over 3Y
    rep_imp = agent.evaluate("OVERHYPED", current_market_cap_cr=500.0, current_revenue_cr=50.0, target_multiple=10.0, target_years=3)
    assert rep_imp.findings[0].severity == FindingSeverity.CRITICAL_RED_FLAG


def test_pm_kill_test_sub_agent():
    from app.services.intelligence.sub_agents import PMKillTestSubAgent
    agent = PMKillTestSubAgent()

    # Clean pass
    rep_pass = agent.evaluate("QUALITY_WINNER")
    assert rep_pass.summary_verdict == "PASSED_PM_KILL_TEST"
    assert rep_pass.findings[0].severity == FindingSeverity.POSITIVE_CATALYST

    # Failed kill-test: CFO divergence and capex delay
    rep_fail = agent.evaluate("VALUATION_TRAP", economic_earnings_divergence=True, management_execution_delay=True)
    assert rep_fail.summary_verdict == "REJECTED_PM_KILL_TEST_FAILED"
    assert any(f.severity == FindingSeverity.CRITICAL_RED_FLAG for f in rep_fail.findings)


