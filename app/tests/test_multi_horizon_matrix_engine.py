"""Unit tests for MultiHorizonMatrixEngine service module."""

import pytest
from app.services.research.multi_horizon_matrix_engine import MultiHorizonMatrixEngine
from app.models.schemas import MultiHorizonMatrixRequest, MultiHorizonMatrixResponse


def test_single_symbol_calculation():
    sample_data = {
        "symbol": "NETWEB.NS",
        "company_name": "Netweb Technologies India",
        "sector": "AI Supercomputing & Data Center",
        "market_cap": 14200.0,
        "current_price": 2520.00,
        "eps_growth_3yr": 85.0,
        "roce_latest": 35.8,
        "cfo_pat_ratio": 1.15,
        "debt_to_equity": 0.05,
        "pledged_pct": 0.0,
        "piotroski_score": 8,
    }

    item = MultiHorizonMatrixEngine.calculate_single_symbol_matrix("NETWEB.NS", sample_data)

    assert item.symbol == "NETWEB.NS"
    assert item.company_name == "Netweb Technologies India"
    assert item.conformal_confidence_label == "HIGH (Institutional Grade)"
    assert item.conformal_confidence_score >= 88.0
    
    # CAGR bounds check
    assert item.cagr_1y_pct > 0
    assert item.cagr_3y_pct > 0
    assert item.cagr_5y_pct > 0

    # Target prices check
    assert item.target_price_1y > item.current_price
    assert item.target_price_3y > item.target_price_1y
    assert item.target_price_5y > item.target_price_3y

    # Probability range checks (0.0 to 100.0%)
    assert 0.0 <= item.prob_6m_positive_pct <= 100.0
    assert 0.0 <= item.prob_1y_positive_pct <= 100.0
    assert 0.0 <= item.prob_3y_3x_pct <= 100.0
    assert 0.0 <= item.prob_5y_5x_pct <= 100.0


def test_speculative_confidence_classification():
    sample_data = {
        "symbol": "PRIMECABLE.BO",
        "company_name": "Prime Cable Industries Ltd.",
        "market_cap": 346.0,
        "current_price": 185.00,
        "eps_growth_3yr": 58.0,
        "roce_latest": 22.0,
        "cfo_pat_ratio": -0.65,  # Negative CFO penalty
        "debt_to_equity": 0.85,  # High debt penalty
        "pledged_pct": 0.0,
        "piotroski_score": 6,
    }

    item = MultiHorizonMatrixEngine.calculate_single_symbol_matrix("PRIMECABLE.BO", sample_data)

    assert item.symbol == "PRIMECABLE.BO"
    assert "SPECULATIVE" in item.conformal_confidence_label or "MEDIUM" in item.conformal_confidence_label
    assert len(item.forensic_invalidation_rules) > 0


def test_batch_universe_analysis():
    override_map = {
        "NETWEB.NS": {
            "symbol": "NETWEB.NS",
            "company_name": "Netweb Tech",
            "current_price": 2520.0,
            "eps_growth_3yr": 80.0,
            "roce_latest": 35.0,
            "cfo_pat_ratio": 1.2,
            "debt_to_equity": 0.05,
            "piotroski_score": 8,
        },
        "SHILCHAR.BO": {
            "symbol": "SHILCHAR.BO",
            "company_name": "Shilchar Tech",
            "current_price": 7050.0,
            "eps_growth_3yr": 60.0,
            "roce_latest": 45.0,
            "cfo_pat_ratio": 1.2,
            "debt_to_equity": 0.02,
            "piotroski_score": 9,
        }
    }

    symbols = ["NETWEB.NS", "SHILCHAR.BO"]
    res = MultiHorizonMatrixEngine.analyze_universe_matrix(symbols, override_data_map=override_map)

    assert isinstance(res, MultiHorizonMatrixResponse)
    assert res.symbols_evaluated == 2
    assert len(res.matrix) == 2
    assert res.matrix[0].conformal_confidence_score >= res.matrix[1].conformal_confidence_score


def test_missing_pledge_in_production_penalized(monkeypatch):
    monkeypatch.setenv("OFFLINE_TEST_MODE", "false")
    data_with_zero_pledge = {
        "symbol": "TEST1.NS",
        "current_price": 500.0,
        "eps_growth_3yr": 30.0,
        "roce_latest": 25.0,
        "cfo_pat_ratio": 1.1,
        "debt_to_equity": 0.2,
        "pledged_pct": 0.0,
        "piotroski_score": 8,
    }
    data_missing_pledge = {
        "symbol": "TEST2.NS",
        "current_price": 500.0,
        "eps_growth_3yr": 30.0,
        "roce_latest": 25.0,
        "cfo_pat_ratio": 1.1,
        "debt_to_equity": 0.2,
        # pledged_pct deliberately missing
        "piotroski_score": 8,
    }

    item_clean = MultiHorizonMatrixEngine.calculate_single_symbol_matrix("TEST1.NS", data_with_zero_pledge)
    item_missing = MultiHorizonMatrixEngine.calculate_single_symbol_matrix("TEST2.NS", data_missing_pledge)

    # Missing pledge must be lower confidence due to -15 vs +5 difference (20 pts)
    assert item_clean.conformal_confidence_score > item_missing.conformal_confidence_score
    assert any("pledge filings" in rule for rule in item_missing.forensic_invalidation_rules)

