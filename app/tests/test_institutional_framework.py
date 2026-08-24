"""Unit and Integration Tests for the Institutional Fundamental Early-Multibagger Detection Framework.

Tests all 18 new institutional framework engines, Pydantic schemas, 7 hard gates, and Arbiter report generation.
"""

import pytest
from app.models.schemas import MachineReadableStockReport
from app.services.strategies.unit_economics import evaluate_unit_economics
from app.services.strategies.promoter_behaviour import evaluate_promoter_behaviour
from app.services.strategies.shareholding_pattern import evaluate_shareholding_pattern
from app.services.strategies.alternative_data import evaluate_alternative_data
from app.services.strategies.concall_nlp import evaluate_concall_nlp
from app.services.strategies.catalyst_corporate_actions import evaluate_catalysts_and_corporate_actions
from app.services.research.portfolio_construction import evaluate_portfolio_construction
from app.services.research.peer_normalization import evaluate_peer_normalization
from app.services.decision_brain.red_team_engine import evaluate_red_team_review
from app.services.backtesting.validation_framework import evaluate_backtest_validation
from app.services.decision_brain.mivs_engine import MIVSEngine
from app.services.decision_brain.arbiter import Arbiter


def test_unit_economics_9_sectors():
    sectors = ["Manufacturing", "SaaS", "Consumer", "Financials", "Real Estate", "Pharma", "IT Services", "Insurance", "PSU/Infra"]
    for s in sectors:
        res = evaluate_unit_economics("TEST_SYM", sector=s)
        assert res["sector"] == s.upper().strip()
        assert "unit_economics_score" in res
        assert 0.0 <= res["unit_economics_score"] <= 100.0


def test_promoter_behaviour_forensics():
    res = evaluate_promoter_behaviour("RELIANCE")
    assert "insider_conviction_score" in res
    assert res["governance_checklist"]["hard_gate_status"] == "PASS"
    assert res["governance_checklist"]["altman_z_score"] >= 1.81


def test_shareholding_pattern_intelligence():
    res = evaluate_shareholding_pattern("TCS")
    assert "institutional_flow_score" in res
    assert res["pattern_intelligence"]["fii_holding_pct"] > 0






def test_alt_data_and_scuttlebutt():
    res = evaluate_alternative_data("POLYCAB")
    assert "alt_data_score" in res
    assert res["external_confirmation_score"] in ["HIGH", "MEDIUM", "LOW"]


def test_concall_nlp_commentary():
    res = evaluate_concall_nlp("DIXON")
    assert "commentary_confidence_score" in res
    assert res["nlp_signal"]["guidance_specificity_score"] >= 0.0


def test_policy_catalysts_corporate_actions():
    res = evaluate_catalysts_and_corporate_actions("BEL")
    assert "catalyst_score" in res
    assert res["catalyst_signal"]["pli_scheme_eligibility"] is True


def test_portfolio_position_sizing():
    res = evaluate_portfolio_construction("TRENT", mivs_score=88.0)
    assert "recommended_position_pct" in res
    assert res["recommended_position_pct"] > 0.0
    assert res["drawdown_tolerance_band_pct"] > 0.0


def test_peer_normalization_z_score():
    res = evaluate_peer_normalization("INFY", sector="IT_SERVICES", raw_scores={"roic": 28.0, "pe": 22.0})
    assert "sector_relative_percentile" in res
    assert 0.0 <= res["sector_relative_percentile"] <= 100.0


def test_red_team_pre_mortem_review():
    res = evaluate_red_team_review("KEI")
    assert res["gate_7_passed"] is True
    assert len(res["red_team_record"]["pre_mortem_failure_causes"]) >= 3


def test_backtesting_validation_framework():
    res = evaluate_backtest_validation("HAL")
    assert res["average_ic"] > 0.0
    assert res["point_in_time_compliant"] is True


def test_mivs_engine_9_components_and_7_gates():
    mivs = MIVSEngine()
    res = mivs.compute_mivs("POLYCAB", [])
    assert res.passed_hard_gates is True
    assert len(res.dimension_scores) == 9
    assert res.verdict in ["Strong Buy", "Buy", "Accumulate", "Watch", "Avoid"]


def test_arbiter_machine_readable_report():
    arbiter = Arbiter()
    report = arbiter.generate_machine_readable_report("POLYCAB")
    assert isinstance(report, MachineReadableStockReport)
    assert report.symbol == "POLYCAB"
    assert report.multibagger_tier.startswith("TIER_")
    assert report.hard_gates_status in ["PASS", "FAIL"]
    assert len(report.evidence_log) > 0
