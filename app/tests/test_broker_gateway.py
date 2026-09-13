"""Unit tests for Institutional Broker Gateway & Order Management System.
"""

import pytest
from app.services.execution.broker_gateway import (
    OrderTicket,
    OrderExecutionResult,
    PaperBrokerGateway,
    get_broker_gateway,
)
from app.services.db import get_connection


def test_paper_broker_market_buy_execution():
    """Verify market buy execution calculates positive slippage and fills order."""
    gw = PaperBrokerGateway(default_adv_shares=1_000_000.0)
    ticket = OrderTicket(
        symbol="RELIANCE",
        side="BUY",
        quantity=500,
        order_type="MARKET",
        strategy_id="TEST_SWING"
    )
    result = gw.place_order(ticket)

    assert result.status == "FILLED"
    assert result.filled_quantity == 500
    assert result.side == "BUY"
    assert result.fill_price >= result.reference_price  # Slippage increases buy price
    assert result.slippage_pct >= 0.0
    assert result.total_execution_cost_inr > 0.0
    assert result.order_id.startswith("ORD-")


def test_paper_broker_market_sell_execution():
    """Verify market sell execution calculates negative fill price and fills order."""
    gw = PaperBrokerGateway(default_adv_shares=1_000_000.0)
    ticket = OrderTicket(
        symbol="TCS",
        side="SELL",
        quantity=200,
        order_type="MARKET",
        strategy_id="TEST_EXIT"
    )
    result = gw.place_order(ticket)

    assert result.status == "FILLED"
    assert result.filled_quantity == 200
    assert result.side == "SELL"
    assert result.fill_price <= result.reference_price  # Slippage decreases sell price
    assert result.total_execution_cost_inr > 0.0


def test_paper_broker_circuit_limit_rejection():
    """Verify that a limit order outside exchange circuit limits is rejected."""
    gw = PaperBrokerGateway(default_adv_shares=500_000.0)
    # Very high limit price exceeding +20% circuit
    ticket = OrderTicket(
        symbol="INFY",
        side="BUY",
        quantity=100,
        order_type="LIMIT",
        limit_price=10_000.0  # Reference price is ~1500, so 10000 violates circuit
    )
    result = gw.place_order(ticket)

    assert result.status == "REJECTED"
    assert result.filled_quantity == 0
    assert "violates exchange circuit limits" in result.rejection_reason


def test_paper_broker_invalid_side_rejection():
    """Verify that an invalid order side is rejected."""
    gw = PaperBrokerGateway()
    ticket = OrderTicket(
        symbol="INFY",
        side="HOLD",  # Invalid side
        quantity=100,
        order_type="MARKET"
    )
    result = gw.place_order(ticket)
    assert result.status == "REJECTED"
    assert "Must be 'BUY' or 'SELL'" in result.rejection_reason


def test_paper_broker_order_persistence():
    """Verify that orders are recorded in execution_orders table."""
    gw = PaperBrokerGateway(default_adv_shares=500_000.0)
    ticket = OrderTicket(
        symbol="HDFCBANK",
        side="BUY",
        quantity=50,
        order_type="MARKET"
    )
    result = gw.place_order(ticket)

    conn = get_connection()
    row = conn.execute(
        "SELECT order_id, symbol, status, fill_price FROM execution_orders WHERE order_id = ?",
        (result.order_id,)
    ).fetchone()
    conn.close()

    assert row is not None
    assert row[0] == result.order_id
    assert row[1] == result.symbol
    assert row[2] == "FILLED"


def test_get_broker_gateway_factory():
    """Verify gateway factory initializes gateway correctly."""
    gw = get_broker_gateway("paper")
    assert isinstance(gw, PaperBrokerGateway)


def test_paper_broker_circuit_queue_liquidity_freeze():
    """Verify buy/sell orders during circuit lock receive QUEUED_CIRCUIT_HOLD with 0 fill."""
    gw = PaperBrokerGateway()
    
    # Buy order during upper circuit lock
    buy_ticket = OrderTicket(
        symbol="CIRCUIT_BUY",
        side="BUY",
        quantity=100,
        order_type="MARKET",
        is_circuit_locked=True
    )
    buy_res = gw.place_order(buy_ticket)
    assert buy_res.status == "QUEUED_CIRCUIT_HOLD"
    assert buy_res.filled_quantity == 0
    assert "locked at upper circuit" in buy_res.rejection_reason
    assert buy_res.execution_algorithm == "CIRCUIT_QUEUE_HOLD"

    # Sell order during lower circuit lock
    sell_ticket = OrderTicket(
        symbol="CIRCUIT_SELL",
        side="SELL",
        quantity=50,
        order_type="MARKET",
        is_circuit_locked=True
    )
    sell_res = gw.place_order(sell_ticket)
    assert sell_res.status == "QUEUED_CIRCUIT_HOLD"
    assert sell_res.filled_quantity == 0
    assert "locked at lower circuit" in sell_res.rejection_reason

