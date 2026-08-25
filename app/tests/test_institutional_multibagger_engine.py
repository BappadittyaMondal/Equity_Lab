import pytest
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine


def test_institutional_multibagger_scoring_universe():
    """Verify ranking universe returns candidate scorecards, archetypes, and thesis criteria."""
    rankings = InstitutionalMultibaggerEngine.rank_universe(min_score=50.0)
    assert len(rankings) > 0

    first = rankings[0]
    assert "symbol" in first
    assert "overall_score" in first
    assert "confidence_score" in first
    assert "archetype" in first
    assert "engine_breakdown" in first
    assert "causal_chain_steps" in first
    assert "positive_drivers" in first
    assert "invalidation_criteria" in first

    # Check score ranges
    assert 50.0 <= first["overall_score"] <= 100.0
    assert 0.0 <= first["confidence_score"] <= 100.0


def test_institutional_multibagger_archetype_assignment():
    """Test evaluating individual stock profiles for proper archetype assignments."""
    test_comp = {
        "symbol": "TEST.NS",
        "company_name": "Test Multibagger Inc.",
        "market_cap": 12000.0,
        "current_price": 1500.0,
        "high_52w": 1600.0,
        "low_52w": 800.0,
        "volume": 200000,
        "vol_1w_avg": 180000,
        "vol_1y_avg": 50000,
        "roe_3yr": 22.0,
        "roe_latest": 26.0,
        "roce_3yr": 24.0,
        "roce_latest": 28.0,
        "opm_5yr": 25.0,
        "opm_latest": 32.0,
        "op_growth": 35.0,
        "pat_growth_3yr": 38.0,
        "pat_growth_latest": 42.0,
        "sales_growth_3yr": 28.0,
        "sales_growth_latest": 32.0,
        "eps_growth_3yr": 36.0,
        "eps_latest": 45.0,
        "cfo_3yr": 500.0,
        "cfo_last_year": 220.0,
        "net_profit_last_year": 180.0,
        "net_block": 800.0,
        "net_block_3yr_back": 400.0,
        "net_block_preceding_year": 650.0,
        "cwip": 200.0,
        "cwip_preceding_year": 100.0,
        "piotroski_score": 8.0,
        "promoter_holding": 55.0,
        "pledged_pct": 0.0,
        "debt_to_equity": 0.25,
        "interest_coverage": 12.0,
        "peg_ratio": 0.95
    }

    result = InstitutionalMultibaggerEngine.evaluate_company(test_comp)
    assert result["overall_score"] >= 80.0
    assert result["archetype"] in ["Early Multibagger", "Emerging Compounder", "Capex Expansion"]
    assert len(result["causal_chain_steps"]) >= 4
    assert len(result["positive_drivers"]) >= 3


def test_institutional_risk_penalty_detection():
    """Verify risk penalties trigger on high pledge or poor cash conversion."""
    risky_comp = {
        "symbol": "RISK.NS",
        "company_name": "Risky Business Ltd.",
        "market_cap": 2000.0,
        "current_price": 100.0,
        "high_52w": 200.0,
        "low_52w": 80.0,
        "volume": 50000,
        "vol_1w_avg": 40000,
        "vol_1y_avg": 30000,
        "roe_3yr": 8.0,
        "roe_latest": 6.0,
        "roce_3yr": 9.0,
        "roce_latest": 7.0,
        "opm_5yr": 12.0,
        "opm_latest": 8.0,
        "op_growth": 2.0,
        "pat_growth_3yr": 3.0,
        "pat_growth_latest": 1.0,
        "sales_growth_3yr": 4.0,
        "sales_growth_latest": 2.0,
        "eps_growth_3yr": 2.0,
        "eps_latest": 5.0,
        "cfo_3yr": 10.0,
        "cfo_last_year": 20.0,
        "net_profit_last_year": 80.0,  # CFO << PAT!
        "net_block": 100.0,
        "net_block_3yr_back": 95.0,
        "net_block_preceding_year": 98.0,
        "cwip": 10.0,
        "cwip_preceding_year": 10.0,
        "piotroski_score": 3.0,
        "promoter_holding": 30.0,
        "pledged_pct": 25.0,  # High pledge!
        "debt_to_equity": 1.8,  # High debt!
        "interest_coverage": 1.5,  # Weak coverage!
        "peg_ratio": 3.5
    }

    result = InstitutionalMultibaggerEngine.evaluate_company(risky_comp)
    assert result["engine_breakdown"]["risk_penalties"] <= -20.0
    assert result["archetype"] == "Value Trap"
    assert len(result["risk_flags"]) >= 3
