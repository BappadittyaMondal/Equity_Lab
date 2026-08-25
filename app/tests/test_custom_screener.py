import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.research.custom_screener import CustomScreenerEngine

client = TestClient(app)


def test_custom_screener_engine_19_conditions():
    """Verify that the 19-condition Screener.in query evaluates correctly."""
    query = """
    Current price > 10 AND Volume > 90000 
    AND 100 * ((High price - Current price) / High price) < 25 
    AND 100 * (Current price / Low price - 1) > 75 
    AND Average return on equity 3Years > 14 AND Return on equity > 19 
    AND Average return on capital employed 3Years > 18 AND Return on capital employed > 23 
    AND Operating profit > 14 AND Operating profit growth > 12 
    AND OPM 5Year > 10 AND OPM > 14 
    AND Profit growth 3Years > 19 AND Profit growth > 23 
    AND Sales growth 3Years > 18 AND Sales growth > 23 
    AND EPS growth 3Years > 14 AND EPS > 18 AND Operating cash flow 3years > 0
    """
    result = CustomScreenerEngine.execute_query(query)
    assert result["total_universe_scanned"] >= 7
    symbols = [r["symbol"] for r in result["results"]]
    
    # Ground truth winners from Screener.in live search
    expected_winners = ["AFCOM.NS", "SJS.NS", "MANORAMA.NS", "EMMVEE.NS", "ACUTAAS.NS", "COFORGE.NS", "MCX.NS"]
    for w in expected_winners:
        assert w in symbols, f"Expected ground-truth winner {w} missing from custom screener result!"


def test_custom_screen_api_endpoint():
    """Verify POST /api/v1/data/custom-screen endpoint."""
    payload = {
        "query": "Current price > 100 AND Return on equity > 20"
    }
    response = client.post("/api/v1/data/custom-screen", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_results_found" in data
    assert data["total_results_found"] > 0
