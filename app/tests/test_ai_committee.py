"""Verification & Regression Test Suite for Next-Gen GenAI & Multi-Agent Committee.

Tests:
1. Virtual Investment Committee Multi-Agent Boardroom Protocol
2. Footnote & Related Party Transaction (RPT) Auditor
3. Supply Chain & Interconnection Inflection Graph Engine
4. Natural Language Quant Query Compiler
5. Continuous Post-Mortem Failure Audit Engine
6. API Endpoint Integration
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.ai_committee.investment_committee import VirtualInvestmentCommittee
from app.services.research.footnote_rpt_auditor import FootnoteRPTAuditor
from app.services.research.supply_chain_graph import SupplyChainGraphEngine
from app.services.query.nl_quant_compiler import NLQuantCompiler
from app.services.ml.post_mortem_learning import PostMortemLearningEngine


def test_virtual_investment_committee_debate():
    """Verify multi-agent boardroom debate and consensus score calculation."""
    res = VirtualInvestmentCommittee.evaluate_investment_committee("SHILCHAR")
    
    assert res["symbol"] == "SHILCHAR"
    assert res["committee_decision"] in ("STRONG_CONVICTION_BUY", "MODERATE_BUY", "CAUTION_WATCHLIST", "REJECT_INVESTMENT")
    assert res["consensus_conviction_score"] >= 70.0
    assert len(res["agent_opinions"]) == 4
    assert "INSTITUTIONAL INVESTMENT COMMITTEE (IC) MEMO" in res["ic_memo"]


def test_footnote_rpt_auditor():
    """Verify RPT governance auditor detects high RPT or promoter pledging risks."""
    # Clean stock
    clean_res = FootnoteRPTAuditor.audit_governance_and_footnotes("SHILCHAR")
    assert clean_res["governance_status"] == "PRISTINE"
    assert clean_res["governance_penalty"] == 0.0

    # Risky stock profile
    risky_res = FootnoteRPTAuditor.audit_governance_and_footnotes("RISKY_STOCK", rpt_data={
        "rpt_revenue_pct": 18.5,
        "promoter_pledged_pct": 25.0,
        "auditor_qualification": "Going concern warning",
        "contingent_liabilities_pct_networth": 30.0
    })
    assert risky_res["governance_status"] == "HIGH_RISK"
    assert len(risky_res["risk_flags"]) == 4
    assert risky_res["governance_penalty"] <= -50.0


def test_supply_chain_graph_engine():
    """Verify customer-supplier graph lookup and catalyst chain propagation."""
    sc_res = SupplyChainGraphEngine.get_supply_chain_profile("SHILCHAR")
    assert sc_res["symbol"] == "SHILCHAR"
    assert sc_res["sector"] == "TRANSFORMERS"
    assert "Power Grid Corporation" in sc_res["primary_customers"]
    assert len(sc_res["second_order_beneficiaries"]) >= 1


def test_nl_quant_compiler():
    """Verify natural language queries translate into quantitative filters."""
    nl_res = NLQuantCompiler.compile_natural_language_query(
        "Find me capital goods stocks under 2000Cr market cap with debt-free balance sheet and FCF > 100"
    )
    filters = nl_res["compiled_filters"]
    assert filters["max_market_cap_cr"] == 2000.0
    assert filters["max_debt_to_equity"] == 0.1
    assert filters["min_fcf_cr"] == 100.0
    assert "HEAVY_ENGINEERING" in filters["target_sectors"]


def test_post_mortem_learning_engine():
    """Verify failure audit loop diagnoses false-positive root causes."""
    pm_res = PostMortemLearningEngine.audit_stock_drawdown(
        symbol="COFORGE",
        initial_score=91.5,
        forward_return_pct=-18.0,
        actual_drawdown_pct=24.0
    )
    assert pm_res["symbol"] == "COFORGE"
    assert pm_res["is_false_positive"] is True
    assert len(pm_res["root_causes"]) >= 1
    assert "MacroGeopoliticalOverlay" in pm_res["remediation_action"]


def test_ai_committee_api_endpoints():
    """Verify FastAPI routes for Next-Gen AI Committee & Intelligence."""
    client = TestClient(app)
    headers = {"X-API-Key": "test_dev_key"}

    # IC Boardroom Review Endpoint
    res1 = client.post("/api/v1/research/ai-committee/review", json={"symbol": "SHILCHAR"}, headers=headers)
    assert res1.status_code == 200
    assert "committee_decision" in res1.json()

    # Governance Audit Endpoint
    res2 = client.get("/api/v1/research/ai-committee/governance-audit/SHILCHAR", headers=headers)
    assert res2.status_code == 200
    assert res2.json()["governance_status"] == "PRISTINE"

    # Supply Chain Graph Endpoint
    res3 = client.get("/api/v1/research/ai-committee/supply-chain/SHILCHAR", headers=headers)
    assert res3.status_code == 200
    assert res3.json()["sector"] == "TRANSFORMERS"

    # Natural Language Query Endpoint
    res4 = client.post("/api/v1/research/ai-committee/nl-query", json={
        "user_query": "Find capital goods stocks under 2000Cr market cap with debt-free balance sheet"
    }, headers=headers)
    assert res4.status_code == 200
    assert "compiled_filters" in res4.json()

    # Post-Mortem Failure Audit Endpoint
    res5 = client.post("/api/v1/research/ai-committee/post-mortem", json={
        "symbol": "COFORGE",
        "initial_score": 91.5,
        "forward_return_pct": -18.0,
        "actual_drawdown_pct": 24.0
    }, headers=headers)
    assert res5.status_code == 200
    assert res5.json()["is_false_positive"] is True
