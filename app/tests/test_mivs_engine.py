"""Unit tests for MIVSEngine and Arbiter MIVS integration."""

import pytest
from app.services.decision_brain.mivs_engine import MIVSEngine, MIVSScoreResult
from app.services.decision_brain.arbiter import Arbiter


class MockEngineOutput:
    def __init__(self, score_0_100=80.0, results=None, metrics=None):
        self.score_0_100 = score_0_100
        self.results = results or {}
        self.metrics = metrics or {}


def test_mivs_hard_gate_rejections():
    engine = MIVSEngine()

    # Case 1: High promoter pledge veto (>40%)
    outputs_pledge_veto = [
        {
            "engine_id": "E1",
            "verdict": "Buy",
            "confidence": 85,
            "raw": MockEngineOutput(results={"promoter_pledge_pct": 45.0}),
        }
    ]
    res_pledge = engine.compute_mivs("TEST_PLE", outputs_pledge_veto)
    assert not res_pledge.passed_hard_gates
    assert res_pledge.mivs_score <= 30.0
    assert any("Pledge" in r for r in res_pledge.gate_reasons)

    # Case 2: Altman Z-Score distress veto (<1.81)
    outputs_altman_veto = [
        {
            "engine_id": "E1",
            "verdict": "Buy",
            "confidence": 85,
            "raw": MockEngineOutput(results={"altman_z_score": 1.2}),
        }
    ]
    res_altman = engine.compute_mivs("TEST_ALT", outputs_altman_veto)
    assert not res_altman.passed_hard_gates
    assert res_altman.mivs_score <= 30.0
    assert any("Altman" in r for r in res_altman.gate_reasons)

    # Case 3: Beneish M-Score veto (> -1.78)
    outputs_beneish_veto = [
        {
            "engine_id": "C11",
            "verdict": "Avoid",
            "confidence": 90,
            "raw": MockEngineOutput(results={"beneish_m_score": -1.2}),
        }
    ]
    res_beneish = engine.compute_mivs("TEST_BEN", outputs_beneish_veto)
    assert not res_beneish.passed_hard_gates
    assert res_beneish.mivs_score <= 30.0
    assert any("Beneish" in r for r in res_beneish.gate_reasons)


def test_mivs_dimension_scoring():
    engine = MIVSEngine()

    clean_outputs = [
        {"engine_id": "E1", "verdict": "Buy", "confidence": 85, "raw": MockEngineOutput(score_0_100=85.0)},
        {"engine_id": "B5", "verdict": "Buy", "confidence": 90, "raw": MockEngineOutput(score_0_100=90.0)},
        {"engine_id": "D18", "verdict": "Buy", "confidence": 80, "raw": MockEngineOutput(score_0_100=80.0)},
        {"engine_id": "E7", "verdict": "Buy", "confidence": 85, "raw": MockEngineOutput(score_0_100=85.0)},
        {"engine_id": "E2", "verdict": "Buy", "confidence": 75, "raw": MockEngineOutput(score_0_100=75.0)},
        {"engine_id": "C13", "verdict": "Buy", "confidence": 85, "raw": MockEngineOutput(score_0_100=85.0)},
        {"engine_id": "C9", "verdict": "Buy", "confidence": 80, "raw": MockEngineOutput(score_0_100=80.0)},
        {"engine_id": "C11", "verdict": "Buy", "confidence": 85, "raw": MockEngineOutput(score_0_100=85.0)},
        {"engine_id": "EVIDENCE", "verdict": "Buy", "confidence": 90, "raw": MockEngineOutput(score_0_100=90.0)},
    ]

    res = engine.compute_mivs("CLEAN_TICKER", clean_outputs)
    assert res.passed_hard_gates
    assert res.mivs_score > 70.0
    assert res.verdict in ("Buy", "Strong Buy")
    assert len(res.dimension_scores) == 9


def test_arbiter_mivs_integration():
    arbiter = Arbiter()
    call = arbiter.arbitrate("RELIANCE")
    assert call is not None
    assert call.symbol == "RELIANCE"
    assert call.conviction_score >= 0


def test_arbiter_subagent_critical_red_flag_veto(monkeypatch):
    from app.services.intelligence.sub_agents import ForensicAuditorSubAgent
    from app.services.intelligence.event_extractor import SubAgentAuditReport, QualitativeEvidenceFinding, FindingSeverity

    def mock_evaluate(self, symbol, snap=None):
        return SubAgentAuditReport(
            agent_name="ForensicAuditorSubAgent",
            symbol=symbol,
            findings=[
                QualitativeEvidenceFinding(
                    category="GOVERNANCE_FRAUD",
                    finding="High promoter pledge exceeding critical threshold",
                    severity=FindingSeverity.CRITICAL_RED_FLAG,
                    confidence=0.95,
                    source_tag="BSE_FILING"
                )
            ]
        )

    monkeypatch.setattr(ForensicAuditorSubAgent, "evaluate", mock_evaluate)

    arbiter = Arbiter()
    call = arbiter.arbitrate("RELIANCE")
    assert call.verdict in ("Avoid", "ABSTAIN")
    assert call.conviction_score <= 30.0

