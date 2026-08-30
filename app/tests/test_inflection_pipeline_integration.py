"""Integration tests for Phase 4 Strategy Pipeline Assembly & Vectorized Backtester."""

import numpy as np
import pytest

from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
from app.services.backtesting.replay_engine import PointInTimeReplayEngine


def test_evaluate_company_integration():
    item = {
        "symbol": "STEALTH_STAR.NS",
        "company_name": "Stealth Star Ltd",
        "market_cap": 2500.0,
        "current_price": 120.0,
        "high_52w": 130.0,
        "low_52w": 60.0,
        "volume": 250000,
        "vol_1y_avg": 50000,
        "sales_growth_3yr": 28.0,
        "pat_growth_3yr": 45.0,
        "pat_growth_latest": 55.0,
        "opm_latest": 22.0,
        "opm_5yr": 16.0,
        "roce_latest": 26.0,
        "roce_3yr": 22.0,
        "cfo_last_year": 120.0,
        "net_profit_last_year": 85.0,
        "net_block": 400.0,
        "net_block_preceding_year": 250.0,
        "cwip": 50.0,
        "promoter_holding": 68.0,
        "pledged_pct": 0.0,
        "debt_to_equity": 0.2,
        "interest_coverage": 12.0,
        "peg_ratio": 0.6
    }
    
    res = InstitutionalMultibaggerEngine.evaluate_company(item)
    assert res["symbol"] == "STEALTH_STAR.NS"
    assert res["overall_score"] >= 75.0
    assert res["hard_risk_gate"]["passed"] is True
    assert res["archetype"] in ["Early Multibagger", "Emerging Compounder", "Capex Expansion", "Earnings Inflection"]


def test_vectorized_forward_returns_backtest():
    # Generate synthetic 100 weeks x 10 stocks matrix
    n_times, n_stocks = 100, 10
    prices = np.linspace(100, 200, n_times)[:, None] + np.random.normal(0, 5, (n_times, n_stocks))
    signals = np.zeros((n_times, n_stocks), dtype=bool)
    
    # Place signals at week 20 for stock 0 and 2
    signals[20, 0] = True
    signals[20, 2] = True
    
    res = PointInTimeReplayEngine.evaluate_vectorized_forward_returns(prices, signals, horizons_weeks=[12, 26, 52])
    assert res["total_signals_evaluated"] == 2
    assert "12W" in res["horizon_performance"]
    assert "26W" in res["horizon_performance"]
    assert "52W" in res["horizon_performance"]
    assert res["horizon_performance"]["12W"]["signal_count"] == 2
    assert res["horizon_performance"]["12W"]["win_rate_pct"] == 100.0
