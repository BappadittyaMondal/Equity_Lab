"""Comprehensive Unit Tests for Ace Investor Capabilities & Triple-Lens Alignment.

Validates:
1. Query-Intent Adaptive detection of Kedia, Kacholia, Agrawal, and SMILE queries.
2. Dynamic constraint relaxation and tightening under KEDIA_SMILE, KACHOLIA_SCALABILITY, and AGRAWAL_INFLECTION.
3. Skill 42 Primary Evidence synthesis with multi-metric evidence quality and red flag detection.
4. Virtual Ace Investor Committee 3-vector debate and consensus classification.
5. Reporting lag price spread risk evaluation (15-to-21 day disclosure lag protection).
6. Smart money clustering detection in public shareholding filings.
7. REST API endpoint contract for /api/v1/research/ai-committee/ace-investor-review.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.research.intent_adaptive_engine import QueryAdaptiveConstraintEngine
from app.services.research.genai_redteam_service import GenAIRedTeamService
from app.services.ai_committee.investment_committee import VirtualInvestmentCommittee
from app.services.strategies.shareholding_pattern import (
    calculate_reporting_lag_risk,
    detect_smart_money_clustering,
    evaluate_shareholding_pattern
)


def test_ace_investor_query_intent_detection():
    """Verify that natural language queries map to ace investor archetypes."""
    assert QueryAdaptiveConstraintEngine.detect_query_intent("Find stocks matching Vijay Kedia SMILE rules") == "KEDIA_SMILE"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("Ashish Kacholia capital scalability compounder") == "KACHOLIA_SCALABILITY"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("Mukul Agrawal techno funda inflection breakout") == "AGRAWAL_INFLECTION"
    assert QueryAdaptiveConstraintEngine.detect_query_intent("Smart money super investor multibagger picks") == "MULTIBAGGER"


def test_kedia_smile_constraints():
    """Verify Kedia SMILE strict promoter and solvency hurdles."""
    # 1. Clean Kedia compounder
    clean_kedia = {
        "promoter_holding": 62.0,
        "pledged_pct": 0.0,
        "debt_to_equity": 0.08,
        "interest_coverage": 6.5,
        "roce_latest": 24.0,
        "cfo_pat_ratio": 1.1,
    }
    res_clean = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("KEDIA_SMILE", clean_kedia)
    assert res_clean["passed"] is True
    assert any("promoter" in t.lower() for t in res_clean["tightened_parameters"])

    # 2. Leveraged and pledged scrip (must fail Kedia's rules)
    bad_kedia = {
        "promoter_holding": 40.0,  # Below 45%
        "pledged_pct": 12.0,       # Above 5%
        "debt_to_equity": 0.85,    # Above 0.30
        "interest_coverage": 2.1,  # Below 3.5x
        "roce_latest": 11.0,       # Below 15%
    }
    res_bad = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("KEDIA_SMILE", bad_kedia)
    assert res_bad["passed"] is False
    assert len(res_bad["objective_blocks"]) >= 3


def test_kacholia_scalability_constraints():
    """Verify Kacholia incremental ROIC and operating leverage hurdles."""
    good_scalability = {
        "incremental_roic": 26.5,
        "sales_growth_3yr": 22.0,
        "cfo_pat_ratio": 0.85,
        "debt_to_equity": 0.25,
    }
    res_good = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("KACHOLIA_SCALABILITY", good_scalability)
    assert res_good["passed"] is True
    assert any("incremental capital" in t.lower() for t in res_good["tightened_parameters"])

    low_roic = {
        "incremental_roic": 12.0,  # Fails 18%
        "sales_growth_3yr": 8.0,   # Fails 12%
        "debt_to_equity": 0.95,    # Fails 0.70
    }
    res_low = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("KACHOLIA_SCALABILITY", low_roic)
    assert res_low["passed"] is False
    assert any("productivity" in b.lower() for b in res_low["objective_blocks"])


def test_agrawal_inflection_constraints():
    """Verify Agrawal quarterly earnings acceleration and volume confirmation."""
    good_inflection = {
        "pat_growth_latest": 35.0,
        "volume_z_score": 2.4,
        "delivery_turnover_5d": 3.0,
    }
    res_good = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("AGRAWAL_INFLECTION", good_inflection)
    assert res_good["passed"] is True
    assert any("earnings inflection" in t.lower() for t in res_good["tightened_parameters"])

    decelerating = {
        "pat_growth_latest": 5.0,  # Fails 15%
        "volume_z_score": -0.5,
    }
    res_decel = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("AGRAWAL_INFLECTION", decelerating)
    assert res_decel["passed"] is False
    assert any("inflection" in b.lower() for b in res_decel["objective_blocks"])


def test_skill42_primary_evidence_hardening():
    """Verify that Skill 42 primary evidence synthesis grades quality accurately and flags traps."""
    # 1. High-quality scrip
    high_quality_data = {
        "roce_latest": 28.0,
        "incremental_roic": 32.0,
        "asset_turnover": 1.8,
        "sales_growth_3yr": 25.0,
        "promoter_holding": 65.0,
        "pledged_pct": 0.0,
        "debt_to_equity": 0.05,
        "pat_growth_latest": 30.0,
        "volume_z_score": 2.1,
        "delivery_turnover_5d": 2.8,
        "cfo_last_year": 200.0,
        "net_profit_last_year": 150.0,
        "capex_last_year": 30.0,
    }
    res_high = GenAIRedTeamService.synthesize_four_lens_evidence("EXCELLENT", high_quality_data)
    assert res_high["kacholia_evidence"]["evidence_quality"] == "HIGH"
    assert res_high["kedia_evidence"]["evidence_quality"] == "HIGH"
    assert res_high["agrawal_evidence"]["evidence_quality"] == "HIGH"
    assert res_high["parikh_evidence"]["evidence_quality"] == "HIGH"
    assert len(res_high["red_flags"]) == 0

    # 2. Trap scrip: High pledge + distributive financing trap (PAT > 0, CFO < 0)
    trap_data = {
        "promoter_holding": 45.0,
        "pledged_pct": 32.0,  # Critical pledge
        "debt_to_equity": 1.4,
        "cfo_last_year": -50.0,  # Negative CFO
        "net_profit_last_year": 80.0,  # Positive PAT
    }
    res_trap = GenAIRedTeamService.synthesize_four_lens_evidence("TRAP", trap_data)
    assert res_trap["kedia_evidence"]["evidence_quality"] == "LOW"
    assert res_trap["parikh_evidence"]["evidence_quality"] == "LOW"
    assert any("distributive financing trap" in rf.lower() for rf in res_trap["red_flags"])
    assert any("pledge" in rf.lower() for rf in res_trap["red_flags"])


def test_ace_investor_virtual_committee_debate():
    """Verify that evaluate_ace_investor_committee executes the 3-vector boardroom debate."""
    # 1. Triple Conviction Winner
    winner_data = {
        "market_cap": 2800.0,
        "promoter_holding": 62.0,
        "pledged_pct": 0.0,
        "debt_to_equity": 0.10,
        "roce_latest": 26.0,
        "incremental_roic": 28.0,
        "asset_turnover": 1.9,
        "sales_growth_3yr": 24.0,
        "pat_growth_3yr": 30.0,
        "pat_growth_latest": 35.0,
        "cfo_last_year": 160.0,
        "net_profit_last_year": 120.0,
        "volume_z_score": 2.2,
        "delivery_turnover_5d": 3.0,
        "current_price": 320.0,
        "high_52w": 335.0,
    }
    comm_winner = VirtualInvestmentCommittee.evaluate_ace_investor_committee("WINNER", winner_data)
    assert comm_winner["committee_decision"] == "TRIPLE_CONVICTION_MULTIBAGGER"
    assert comm_winner["vote_summary"]["approve"] == 3
    assert "ACE INVESTOR BOARDROOM" in comm_winner["ic_memo"]

    # 2. Leveraged candidate rejected by Kedia
    leveraged_data = dict(winner_data)
    leveraged_data["debt_to_equity"] = 1.6
    leveraged_data["pledged_pct"] = 28.0
    comm_lev = VirtualInvestmentCommittee.evaluate_ace_investor_committee("LEVERAGED", leveraged_data)
    assert comm_lev["committee_decision"] == "REJECT_INVESTMENT"


def test_reporting_lag_and_clustering_guards():
    """Verify post-discovery run-up spread caution and smart money clustering detection."""
    # 1. Reporting lag caution when stock rallied 45% post quarter-end filing
    lag_res = calculate_reporting_lag_risk(current_price=145.0, filing_quarter_end_price=100.0)
    assert lag_res["reporting_lag_assessed"] is True
    assert lag_res["lag_risk_tier"] == "HIGH_DISCOVERY_PREMIUM"
    assert "Reporting Lag Trap" in lag_res["warning"]

    # Extreme runup trap (>50%)
    extreme_lag = calculate_reporting_lag_risk(current_price=160.0, filing_quarter_end_price=100.0)
    assert extreme_lag["lag_risk_tier"] == "CRITICAL_RUNUP_TRAP"

    # Benign runup (<35%)
    benign_lag = calculate_reporting_lag_risk(current_price=110.0, filing_quarter_end_price=100.0)
    assert benign_lag["lag_risk_tier"] == "BENIGN"
    assert benign_lag["warning"] is None

    # 2. Smart money clustering detection with Indian middle names
    filings = [
        {"name": "Vijay Kishanlal Kedia", "holding_pct": 2.4, "quarter": "Q1FY26"},
        {"name": "Ashish Ramchandra Kacholia", "holding_pct": 1.9, "quarter": "Q2FY26"},
        {"name": "General Public Shareholder", "holding_pct": 1.2, "quarter": "Q2FY26"}
    ]
    clustering_res = detect_smart_money_clustering(filings)
    assert clustering_res["is_smart_money_clustered"] is True
    assert clustering_res["cluster_count"] == 2
    assert "VIJAY_KEDIA" in clustering_res["tracked_entities"]
    assert "ASHISH_KACHOLIA" in clustering_res["tracked_entities"]

    # Integrated engine output
    full_eval = evaluate_shareholding_pattern("TEST_SYM", {
        "current_price": 140.0,
        "filing_quarter_end_price": 100.0,
        "tracked_holders": filings
    })
    assert full_eval["reporting_lag_analysis"]["lag_risk_tier"] == "HIGH_DISCOVERY_PREMIUM"
    assert full_eval["smart_money_clustering"]["is_smart_money_clustered"] is True
    assert any("Reporting Lag Trap" in e for e in full_eval["evidence"])


def test_ace_investor_rest_endpoint():
    """Verify the FastAPI REST endpoint /api/v1/research/ai-committee/ace-investor-review."""
    client = TestClient(app)
    payload = {
        "symbol": "SHILCHAR",
        "stock_data": {
            "market_cap": 2500,
            "promoter_holding": 60,
            "pledged_pct": 0,
            "debt_to_equity": 0.1,
            "roce_latest": 25,
            "sales_growth_3yr": 25,
            "pat_growth_latest": 30,
            "cfo_last_year": 100,
            "net_profit_last_year": 80
        }
    }
    response = client.post("/api/v1/research/ai-committee/ace-investor-review", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "SHILCHAR"
    assert data["committee_decision"] == "TRIPLE_CONVICTION_MULTIBAGGER"
    assert len(data["agent_opinions"]) == 3
    assert "skill42_four_lens_synthesis" in data
    assert "ic_memo" in data
