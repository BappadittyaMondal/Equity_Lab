from fastapi.testclient import TestClient
from app.main import app
from app.services.strategies.growth_arbitrage import evaluate_growth_arbitrage

client = TestClient(app)


def test_growth_arbitrage_direct_engine():
    res = evaluate_growth_arbitrage("RELIANCE")
    assert "RELIANCE" in res.symbol
    assert res.current_price > 0
    assert res.expected_growth_rate > 0
    assert res.market_implied_growth > 0
    assert res.intrinsic_value_dcf > 0
    assert "bear_case" in res.fair_value_range
    assert "base_case" in res.fair_value_range
    assert "bull_case" in res.fair_value_range
    assert "6_months" in res.horizon_forecasts
    assert "1_year" in res.horizon_forecasts
    assert "2_years" in res.horizon_forecasts
    assert "5_years" in res.horizon_forecasts
    assert res.composite_score >= 0.0 and res.composite_score <= 100.0


def test_growth_arbitrage_api_endpoint():
    response = client.get("/api/v1/research/growth-arbitrage?symbol=TCS")
    assert response.status_code == 200
    data = response.json()
    assert "TCS" in data["symbol"]
    assert "growth_arbitrage_gap" in data
    assert "fair_value_range" in data
    assert "horizon_forecasts" in data
    assert data["composite_score"] > 0

