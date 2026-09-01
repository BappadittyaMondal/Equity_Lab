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


def test_is_live_data_and_data_mode():
    import pandas as pd
    from app.services.market_data import is_live_data, get_data_mode

    live_df = pd.DataFrame({"Close": [100, 101, 102]})
    assert is_live_data(live_df) is True
    assert get_data_mode(live_df) == "LIVE"

    mock_df = pd.DataFrame({"Close": [100, 101, 102]})
    mock_df.attrs["data_mode"] = "MOCK"
    mock_df.attrs["is_mock"] = True
    assert is_live_data(mock_df) is False
    assert get_data_mode(mock_df) == "MOCK"


def test_swing_predictive_engine_synthetic_tagging():
    import pandas as pd
    from app.services.strategies.swing_predictive_engine import SwingPredictiveEngine

    dates_d = pd.date_range(end="2026-04-01", periods=60, freq="B")
    mock_df = pd.DataFrame({
        "open": [100.0] * 60,
        "high": [105.0] * 60,
        "low": [98.0] * 60,
        "close": [102.0] * 60,
        "volume": [500000] * 60
    }, index=dates_d)
    mock_df.attrs["data_mode"] = "MOCK"
    mock_df.attrs["is_mock"] = True

    dates_w = pd.date_range(end="2026-04-01", periods=30, freq="W")
    mock_w = pd.DataFrame({
        "open": [100.0] * 30,
        "high": [105.0] * 30,
        "low": [98.0] * 30,
        "close": [102.0] * 30,
        "volume": [2500000] * 30
    }, index=dates_w)

    res = SwingPredictiveEngine.predict_swing_30d(mock_df, mock_w)
    assert res["data_mode"] == "MOCK"
    assert res["is_synthetic"] is True

