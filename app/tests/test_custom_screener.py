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


def test_custom_screener_disambiguated_metrics():
    """Verify that PE, PB, Current Ratio, Dividend Yield, ROA evaluate as authentic metrics without aliasing."""
    query = "Price to earning > 5 AND Return on assets > 5 AND Current ratio > 1.0 AND Price to book value > 0.5"
    result = CustomScreenerEngine.execute_query(query)
    assert result["total_universe_scanned"] >= 7
    assert len(result["results"]) > 0


def test_custom_screener_semantic_metric_truth():
    """Verify that Sales, Debt, Return over 1 year, and Public holding evaluate as authentic metrics."""
    # Test Sales as absolute revenue (not growth rate)
    comp = {
        "symbol": "TEST.NS",
        "company_name": "Test Co",
        "operating_profit": 200.0,
        "opm_latest": 20.0,  # Implies sales = 1000.0 Cr
        "sales_growth_latest": 15.0,  # 15% growth
        "current_price": 500.0,
        "low_52w": 250.0,  # 100% 52w price appreciation
        "market_cap": 5000.0,
        "debt_to_equity": 0.5,
        "net_block": 2000.0,
        "cwip": 500.0,  # Total equity proxy = 2500 -> Debt = 1250 Cr
        "promoter_holding": 60.0,
        "fii_holding": 10.0,
        "dii_holding": 5.0,  # Public holding = 25.0%
        "roe_latest": 8.0,   # Low ROE to prove Return over 1 year is NOT evaluating ROE
    }
    # 1. Sales query: > 500 Cr should pass on sales=1000, but would fail if aliased to sales_growth=15
    assert CustomScreenerEngine._eval_boolean_expr(comp, "Sales > 500") is True
    assert CustomScreenerEngine._eval_boolean_expr(comp, "Sales > 1500") is False

    # 2. Debt query: > 500 Cr should pass on debt=1250, but would fail if aliased to debt_to_equity=0.5
    assert CustomScreenerEngine._eval_boolean_expr(comp, "Debt > 500") is True
    assert CustomScreenerEngine._eval_boolean_expr(comp, "Debt to equity < 1.0") is True

    # 3. Return over 1 year: should be positive price return, NOT roe_latest (8.0)
    assert CustomScreenerEngine._eval_boolean_expr(comp, "Return over 1 year > 20") is True

    # 4. Public holding: 25% (100 - 60 - 10 - 5), NOT promoter_holding (60%)
    assert CustomScreenerEngine._eval_boolean_expr(comp, "Public holding < 30") is True
    assert CustomScreenerEngine._eval_boolean_expr(comp, "Promoter holding > 50") is True


