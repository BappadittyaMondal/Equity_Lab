"""Phase 3 Verification & Regression Test Suite.

Tests MacroGeopoliticalOverlay (+15% Defense, +10% Renewables, -20% IT Exporters)
and Generative AI Qualitative Red-Team Service.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.research.geopolitical_engine import evaluate_geopolitical_risk
from app.services.research.genai_redteam_service import GenAIRedTeamService


def test_macro_geopolitical_overlay_matrix():
    """Verify sector premiums and penalties in MacroGeopoliticalOverlay."""
    # 1. Defense Tailwind Premium (+15%)
    hbl = evaluate_geopolitical_risk("HBLPOWER")
    assert hbl["overlay_pct"] == 15.0
    assert hbl["overlay_type"] == "TAILWIND_PREMIUM"
    
    # 2. Renewable Energy Policy Protection (+10%)
    shilchar = evaluate_geopolitical_risk("SHILCHAR")
    assert shilchar["overlay_pct"] == 10.0
    assert shilchar["overlay_type"] == "POLICY_PROTECTION"
    
    # 3. IT Exporter Macro Risk Penalty (-20%)
    coforge = evaluate_geopolitical_risk("COFORGE")
    assert coforge["overlay_pct"] == -20.0
    assert coforge["overlay_type"] == "MACRO_RISK_PENALTY"
    assert coforge["macro_risk_rating"] == "HIGH"
    
    # 4. Shipping Volatility Index (-10%)
    geship = evaluate_geopolitical_risk("GESHIP")
    assert geship["overlay_pct"] == -10.0
    assert geship["overlay_type"] == "VOLATILITY_INDEX"


def test_genai_concall_auditor_and_stress_tester():
    """Verify Automated Concall Analyst and Geopolitical Stress Tester."""
    # Concall Risk Audit
    audit_res = GenAIRedTeamService.audit_earnings_call_transcript(
        "COFORGE",
        transcript_text="Management highlighted slowing us enterprise demand and pricing pressure on tech contracts."
    )
    assert audit_res["sentiment_score"] < 70.0
    assert len(audit_res["flagged_concall_risks"]) >= 2
    
    # Geopolitical Stress Tester
    stress_res = GenAIRedTeamService.run_geopolitical_stress_test(
        "COFORGE",
        scenario="US_IT_BUDGET_CUT_15PCT"
    )
    assert stress_res["estimated_revenue_impact_pct"] == -22.0
    assert stress_res["pass_stress_test"] is False
    assert stress_res["stress_test_recommendation"] == "APPLY_MACRO_HEDGE"


def test_genai_counter_thesis_redteam_bot():
    """Verify Automated Counter-Thesis Bot generates bear cases."""
    redteam_res = GenAIRedTeamService.generate_counter_thesis_redteam(
        "SHILCHAR",
        primary_bull_thesis="High-growth transformer super-cycle compounder"
    )
    assert redteam_res["symbol"] == "SHILCHAR"
    assert "RED-TEAM BEAR CASE FOR SHILCHAR" in redteam_res["bear_case_summary"]
    assert len(redteam_res["failure_causes"]) >= 3


def test_phase3_genai_api_endpoints():
    """Verify Phase 3 API endpoints via FastAPI TestClient."""
    client = TestClient(app)
    headers = {"X-API-Key": "test_dev_key"}
    
    # Geopolitical Overlay Endpoint
    res1 = client.get("/api/v1/research/genai-redteam/geopolitical-overlay/HBLPOWER", headers=headers)
    assert res1.status_code == 200
    assert res1.json()["overlay_pct"] == 15.0
    
    # Concall Audit Endpoint
    res2 = client.post("/api/v1/research/genai-redteam/concall-audit", json={"symbol": "COFORGE"}, headers=headers)
    assert res2.status_code == 200
    assert "sentiment_score" in res2.json()
    
    # Stress Test Endpoint
    res3 = client.post("/api/v1/research/genai-redteam/stress-test", json={"symbol": "COFORGE", "scenario": "US_IT_BUDGET_CUT_15PCT"}, headers=headers)
    assert res3.status_code == 200
    assert res3.json()["estimated_revenue_impact_pct"] == -22.0
    
    # Red Team Review Endpoint
    res4 = client.post("/api/v1/research/genai-redteam/red-team-review", json={"symbol": "SHILCHAR"}, headers=headers)
    assert res4.status_code == 200
    assert "bear_case_summary" in res4.json()
