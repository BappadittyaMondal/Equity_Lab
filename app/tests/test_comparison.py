"""Unit tests for stock comparison engine.
"""

import pytest
import pandas as pd
from app.models.schemas import ComparisonRequest
from app.models.schemas import MetaHeader, TickerQuoteResponse
from app.services import comparison


def test_comparison_valid_symbols(monkeypatch):
    dates = pd.date_range("2024-01-01", periods=5, freq="B")
    prices = {
        "RELIANCE.NS": [100, 102, 101, 105, 110],
        "TCS.NS": [100, 101, 103, 104, 108],
        "^NSEI": [100, 100, 102, 103, 105],
    }
    meta = MetaHeader(source="test", as_of="2024-01-05T00:00:00+05:30", retrieved_at="2024-01-05T00:00:00+05:30", market_data_type="end_of_day")
    def fake_history(symbol, **kwargs):
        return pd.DataFrame({"Close": prices[symbol]}, index=dates)
    def fake_quote(symbol):
        return TickerQuoteResponse(symbol=symbol, price=prices[symbol][-1], previous_close=prices[symbol][-2], change=1, change_percent=1, fifty_two_week_high=115, fifty_two_week_low=90, market_cap=1_000_000, pe_ratio=20, meta=meta)
    monkeypatch.setattr(comparison, "get_history", fake_history)
    monkeypatch.setattr(comparison, "get_quote", fake_quote)

    req = ComparisonRequest(
        symbols=["RELIANCE", "TCS"],
        period="1y",
        benchmark="^NSEI"
    )
    res = comparison.compare_stocks(req)
    assert len(res.symbols) == 2
    assert "RELIANCE.NS" in res.symbols
    assert "TCS.NS" in res.symbols
    assert res.benchmark == "^NSEI"
    assert "price_return_pct" in res.formula_explanations
    assert res.disclaimer != ""


def test_comparison_invalid_count():
    with pytest.raises(Exception):
        req = ComparisonRequest(symbols=["RELIANCE"])
        compare_stocks(req)
