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


def test_supply_chain_catalyst_sub_agent():
    agent = SupplyChainCatalystSubAgent()
    rep = agent.evaluate("TATA-POWER", sector="Power")
    assert rep.findings[0].severity == FindingSeverity.POSITIVE_CATALYST


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

