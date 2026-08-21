"""Unit test suite for Phase 1 Data-Source Diversification and Fallback.
Verifies multi-provider fallback logic when primary market data source fails.
"""

import pytest
import asyncio
from app.services.market_data import (
    YFinanceProvider,
    YahooDirectJSONProvider,
    NSEIndiaProvider,
    _async_get_market_quote,
    _get_mock_fallback_quote,
)


def test_yfinance_provider_raises_on_invalid_data(monkeypatch):
    """Simulate yfinance returning empty or invalid price data."""
    provider = YFinanceProvider()

    class MockTicker:
        def __init__(self, sym):
            self.info = {}

    monkeypatch.setattr(provider.yf, "Ticker", MockTicker)

    async def _run():
        with pytest.raises(ValueError, match="Price not found"):
            await provider.get_quote("INVALID_SYMBOL")

    asyncio.run(_run())


def test_fallback_chain_handles_primary_failure(monkeypatch):
    """Verify that when YFinanceProvider fails, fallback provider succeeds or offline mock serves data."""
    async def failing_yfinance_quote(self, symbol: str):
        raise ValueError("Simulated YFinance primary outage")

    monkeypatch.setattr(YFinanceProvider, "get_quote", failing_yfinance_quote)

    quote = asyncio.run(_async_get_market_quote("RELIANCE.NS"))
    assert quote is not None
    assert "symbol" in quote
    assert "price" in quote
    assert quote["price"] > 0


def test_mock_fallback_structure():
    """Verify offline mock fallback returns valid quote schema with metadata header."""
    mock_quote = _get_mock_fallback_quote("TCS")
    assert mock_quote["symbol"] == "TCS.NS"
    assert "meta" in mock_quote
    assert mock_quote["meta"]["data_mode"] == "MOCK"
