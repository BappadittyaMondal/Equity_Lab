"""Unit Tests for Phase 185: Model Portfolio Delta Rebalancing & Profit-Taking Engine."""

import pytest
from app.services.research.portfolio_rebalancing import (
    compute_portfolio_delta_rebalance,
    RebalanceAction
)


def test_hold_decision_when_headroom_intact():
    """Verify that a continuing high-conviction position is marked HOLD."""
    prev_port = [
        {"symbol": "CONCORD", "rank": 1, "price": 100.0, "reverse_dcf_headroom": 45.0, "extension_z": 1.1}
    ]
    curr_port = [
        {"symbol": "CONCORD", "rank": 2, "price": 112.0, "reverse_dcf_headroom": 38.0, "extension_z": 1.4}
    ]
    res = compute_portfolio_delta_rebalance(prev_port, curr_port)
    assert res["total_previous_positions"] == 1
    assert res["total_current_positions"] == 1
    assert res["hold_count"] == 1
    decision = res["decisions"][0]
    assert decision["action"] == RebalanceAction.HOLD.value
    assert decision["symbol"] == "CONCORD"
    assert decision["price_change_pct"] == 12.0


def test_take_profit_when_gain_and_extension_exhausted():
    """Verify that a stock running +40% with +2.8 sigma extension triggers TAKE_PROFIT."""
    prev_port = [
        {"symbol": "TAALTECH", "rank": 3, "price": 200.0, "reverse_dcf_headroom": 50.0, "extension_z": 0.5}
    ]
    curr_port = [
        {"symbol": "TAALTECH", "rank": 8, "price": 285.0, "reverse_dcf_headroom": 8.0, "extension_z": 2.8, "rsi": 81.0}
    ]
    res = compute_portfolio_delta_rebalance(prev_port, curr_port, profit_take_gain_threshold=30.0)
    assert res["take_profit_count"] == 1
    decision = res["decisions"][0]
    assert decision["action"] == RebalanceAction.TAKE_PROFIT.value
    assert "Climactic technical extension" in decision["rationale"]
    assert "Reverse-DCF headroom exhausted" in decision["rationale"]


def test_take_profit_when_dropped_after_major_gain():
    """Verify that a stock dropping out of ranking after a 35% run triggers TAKE_PROFIT."""
    prev_port = [
        {"symbol": "SHAKTIPUMP", "rank": 5, "price": 1000.0, "current_price": 1380.0, "unrealized_return_pct": 38.0}
    ]
    curr_port = [
        {"symbol": "NEW_STOCK", "rank": 1, "price": 500.0}
    ]
    res = compute_portfolio_delta_rebalance(prev_port, curr_port)
    decision = [d for d in res["decisions"] if d["symbol"] == "SHAKTIPUMP"][0]
    assert decision["action"] == RebalanceAction.TAKE_PROFIT.value
    assert "Dropped out of current top ranking with solid gain" in decision["rationale"]


def test_new_entry_detection():
    """Verify fresh stocks in current portfolio are marked NEW_ENTRY."""
    prev_port = [
        {"symbol": "OLD_STOCK", "rank": 1, "price": 100.0}
    ]
    curr_port = [
        {"symbol": "OLD_STOCK", "rank": 2, "price": 105.0},
        {"symbol": "SWARAJENG", "rank": 1, "price": 3000.0, "reverse_dcf_headroom": 40.0, "extension_z": 0.8}
    ]
    res = compute_portfolio_delta_rebalance(prev_port, curr_port)
    assert res["new_entry_count"] == 1
    decision = [d for d in res["decisions"] if d["symbol"] == "SWARAJENG"][0]
    assert decision["action"] == RebalanceAction.NEW_ENTRY.value
    assert decision["current_rank"] == 1


def test_stop_loss_and_veto_exit():
    """Verify that severe drawdown or fatal veto triggers STOP_LOSS with IMMEDIATE urgency."""
    prev_port = [
        {"symbol": "BAD_STOCK_1", "rank": 10, "price": 100.0, "current_price": 84.0},  # -16% drop
        {"symbol": "BAD_STOCK_2", "rank": 11, "price": 100.0, "is_vetoed": True, "veto_reason": "Promoter pledge breach"}
    ]
    curr_port = []
    res = compute_portfolio_delta_rebalance(prev_port, curr_port, stop_loss_pct=-12.0)
    assert res["stop_loss_count"] == 2
    for d in res["decisions"]:
        assert d["action"] == RebalanceAction.STOP_LOSS.value
        assert d["urgency"] == "IMMEDIATE"


def test_portfolio_turnover_metrics():
    """Verify turnover and retention percentages."""
    prev_port = [
        {"symbol": "S1", "rank": 1, "price": 100.0},
        {"symbol": "S2", "rank": 2, "price": 100.0},
        {"symbol": "S3", "rank": 3, "price": 100.0},
        {"symbol": "S4", "rank": 4, "price": 100.0},
    ]
    curr_port = [
        {"symbol": "S1", "rank": 1, "price": 105.0},  # Hold
        {"symbol": "S2", "rank": 2, "price": 102.0},  # Hold
        {"symbol": "S5", "rank": 3, "price": 100.0},  # New
        {"symbol": "S6", "rank": 4, "price": 100.0},  # New
    ]
    res = compute_portfolio_delta_rebalance(prev_port, curr_port)
    assert res["hold_count"] == 2
    assert res["new_entry_count"] == 2
    assert res["retention_rate_pct"] == 50.0  # 2 out of 4 retained
    assert res["turnover_rate_pct"] == 50.0   # 2 new out of 4 total current
