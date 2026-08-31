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


def test_growth_arbitrage_cagr_small_pat_base(monkeypatch, tmp_path):
    from app.services.research_data import ResearchDataStore, FinancialObservationIn

    db_path = str(tmp_path / "test_ga.sqlite")
    store = ResearchDataStore(database_path=db_path)
    store.upsert_company({"symbol": "SMALL_PAT.NS", "legal_name": "Small Pat Ltd", "sector": "Test", "industry": "Test"})

    # Seed observations with small PAT base (0.3 Cr -> 50.0 Cr over 3 years)
    obs1 = FinancialObservationIn(symbol="SMALL_PAT.NS", metric="pat", value=0.3, unit="Cr", currency="INR", period_end="2022-03-31", period_type="annual", statement_scope="standalone", published_at="2022-04-15T00:00:00Z", source_name="test", source_url="http://test", confidence=0.9)
    obs2 = FinancialObservationIn(symbol="SMALL_PAT.NS", metric="pat", value=50.0, unit="Cr", currency="INR", period_end="2025-03-31", period_type="annual", statement_scope="standalone", published_at="2025-04-15T00:00:00Z", source_name="test", source_url="http://test", confidence=0.9)
    obs3 = FinancialObservationIn(symbol="SMALL_PAT.NS", metric="revenue", value=10.0, unit="Cr", currency="INR", period_end="2022-03-31", period_type="annual", statement_scope="standalone", published_at="2022-04-15T00:00:00Z", source_name="test", source_url="http://test", confidence=0.9)
    obs4 = FinancialObservationIn(symbol="SMALL_PAT.NS", metric="revenue", value=100.0, unit="Cr", currency="INR", period_end="2025-03-31", period_type="annual", statement_scope="standalone", published_at="2025-04-15T00:00:00Z", source_name="test", source_url="http://test", confidence=0.9)
    store.add_financial_observation(obs1)
    store.add_financial_observation(obs2)
    store.add_financial_observation(obs3)
    store.add_financial_observation(obs4)

    monkeypatch.setattr("app.services.strategies.growth_arbitrage.get_quote", lambda sym: {"price": 100.0, "pe_ratio": 20.0, "fifty_two_week_high": 110.0})

    res = evaluate_growth_arbitrage("SMALL_PAT.NS", store=store)
    # Expected PAT CAGR against 0.3 base: ((50 / 0.3) ** (1/3) - 1) * 100 = ~450.4%
    # Expected Rev CAGR against 10.0 base: ((100 / 10) ** (1/3) - 1) * 100 = ~115.4%
    # Expected weighted growth = 115.44 * 0.4 + 450.36 * 0.6 = ~316.4%
    assert res.expected_growth_rate > 200.0

