"""Phase 2 Verification & Regression Test Suite.

Tests FCF Capex Trap differentiation and User Feedback / Counter-Question Engine.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
from app.services.research.user_feedback_engine import UserFeedbackEngine


def test_fcf_capex_trap_differentiation():
    """Verify that severe FCF burn triggers a risk penalty while positive FCF compounders pass clean."""
    # SHILCHAR: Positive FCF compounder (+256 Cr FCF)
    shilchar_res = InstitutionalMultibaggerEngine.evaluate_company({
        "symbol": "SHILCHAR",
        "sales_growth_3yr": 42.0,
        "pat_growth_3yr": 52.0,
        "eps_growth_3yr": 55.0,
        "cfo_last_year": 256.0,
        "net_profit_last_year": 180.0,
        "fcf_last_year": 256.0,
        "debt_to_equity": 0.05,
        "interest_coverage": 45.0,
        "peg_ratio": 0.8,
        "piotroski_score": 8
    })
    
    # WAAREEENER: High EBITDA/Sales growth (+91%) but burning -2355 Cr FCF
    waaree_res = InstitutionalMultibaggerEngine.evaluate_company({
        "symbol": "WAAREEENER",
        "sales_growth_3yr": 91.0,
        "pat_growth_3yr": 85.0,
        "eps_growth_3yr": 88.0,
        "cfo_last_year": -1500.0,
        "net_profit_last_year": 850.0,
        "fcf_last_year": -2355.0,
        "debt_to_equity": 1.10,
        "interest_coverage": 3.5,
        "peg_ratio": 1.2,
        "piotroski_score": 5
    })

    # Verify SHILCHAR has no FCF burn risk penalty
    assert not any("Severe Free Cash Flow Burn" in flag for flag in shilchar_res["risk_flags"])
    
    # Verify WAAREEENER triggers severe FCF burn penalty (-15.0 pts)
    assert any("Severe Free Cash Flow Burn" in flag for flag in waaree_res["risk_flags"])
    assert waaree_res["engine_breakdown"]["risk_penalties"] <= -15.0


def test_user_feedback_engine_counter_questions():
    """Verify Phase 2 UserFeedbackEngine ingests counter-questions and returns structured feedback."""
    engine = UserFeedbackEngine()
    
    # Question 1: Comparing FCF between Shilchar and Waaree
    res1 = engine.process_counter_question("Why is Shilchar ranked higher on cash flow than Waaree?")
    assert res1["status"] == "SUCCESS"
    assert "SHILCHAR" in res1["extracted_symbols"]
    assert "WAAREEENER" in res1["extracted_symbols"]
    assert "FREE_CASH_FLOW_BURN" in res1["risk_topics"]
    assert "FCF CAPEX TRAP ANALYSIS" in res1["analytical_response"]

    # Question 2: Geopolitical IT Headwinds
    res2 = engine.process_counter_question("What about IT headwinds in geopolitics for Coforge?")
    assert res2["status"] == "SUCCESS"
    assert "COFORGE" in res2["extracted_symbols"]
    assert "IT" in res2["extracted_sectors"]
    assert "GEOPOLITICAL OVERLAY" in res2["analytical_response"]


def test_user_feedback_api_endpoint():
    """Verify API endpoint POST /api/v1/research/user-feedback."""
    client = TestClient(app)
    headers = {"X-API-Key": "test_dev_key"}
    
    payload = {
        "user_query": "Why is Shilchar not in the top list given FCF burn in Waaree?"
    }
    
    response = client.post("/api/v1/research/user-feedback", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "analytical_response" in data
