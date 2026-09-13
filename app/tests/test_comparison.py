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
    def fake_quote(symbol, **kwargs):
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
        comparison.compare_stocks(req)


def test_comparison_benchmark_failure_fail_closed(monkeypatch):
    dates = pd.date_range("2024-01-01", periods=5, freq="B")
    prices = {
        "RELIANCE.NS": [100, 102, 101, 105, 110],
        "TCS.NS": [100, 101, 103, 104, 108],
    }
    meta = MetaHeader(source="test", as_of="2024-01-05T00:00:00+05:30", retrieved_at="2024-01-05T00:00:00+05:30", market_data_type="end_of_day")
    def fake_history(symbol, **kwargs):
        if symbol == "^NSEI":
            raise RuntimeError("Benchmark data feed unavailable")
        return pd.DataFrame({"Close": prices[symbol]}, index=dates)
    def fake_quote(symbol, **kwargs):
        return TickerQuoteResponse(symbol=symbol, price=prices[symbol][-1], previous_close=prices[symbol][-2], change=1, change_percent=1, fifty_two_week_high=115, fifty_two_week_low=90, market_cap=1_000_000, pe_ratio=20, meta=meta)
    monkeypatch.setattr(comparison, "get_history", fake_history)
    monkeypatch.setattr(comparison, "get_quote", fake_quote)

    req = ComparisonRequest(
        symbols=["RELIANCE", "TCS"],
        period="1y",
        benchmark="^NSEI"
    )
    res = comparison.compare_stocks(req)
    assert res.benchmark_return_pct is None
    for sym in ["RELIANCE.NS", "TCS.NS"]:
        assert res.metrics_data[sym]["relative_return_vs_benchmark_pct"] is None
        assert res.metrics_data[sym]["beta"] is None


def test_comparison_missing_volatility_no_fake_30(monkeypatch):
    """Verify that when price series fails, volatility penalty is None rather than falsified 30.0."""
    dates = pd.date_range("2024-01-01", periods=5, freq="B")
    meta = MetaHeader(source="test", as_of="2024-01-05T00:00:00+05:30", retrieved_at="2024-01-05T00:00:00+05:30", market_data_type="end_of_day")

    def fake_history(symbol, **kwargs):
        if "FAIL" in symbol:
            raise RuntimeError("History feed down")
        return pd.DataFrame({"Close": [100, 102, 101, 105, 110]}, index=dates)

    def fake_quote(symbol, **kwargs):
        return TickerQuoteResponse(symbol=symbol, price=110, previous_close=105, change=5, change_percent=4.7, fifty_two_week_high=115, fifty_two_week_low=90, market_cap=1_000_000, pe_ratio=20, meta=meta)

    monkeypatch.setattr(comparison, "get_history", fake_history)
    monkeypatch.setattr(comparison, "get_quote", fake_quote)

    req = ComparisonRequest(symbols=["FAILCORP", "TCS"], period="1y", benchmark="^NSEI")
    res = comparison.compare_stocks(req)
    assert res.score_breakdown["FAILCORP.NS"]["volatility_penalty"] is None
    assert res.score_breakdown["FAILCORP.NS"]["sharpe_ratio_proxy"] is None
    assert res.score_breakdown["FAILCORP.NS"]["data_completeness"] == "DATA_INSUFFICIENT_FOR_SHARPE"


def test_comparison_pairwise_return_correlation(monkeypatch):
    """Verify pairwise return correlation is computed across compared symbols."""
    dates = pd.date_range("2024-01-01", periods=20, freq="B")
    meta = MetaHeader(source="test", as_of="2024-01-20T00:00:00+05:30", retrieved_at="2024-01-20T00:00:00+05:30", market_data_type="end_of_day")

    prices = {
        "RELIANCE.NS": [100 + i * 2 for i in range(20)],
        "TCS.NS": [100 + i * 1.5 for i in range(20)],
    }

    def fake_history(symbol, **kwargs):
        sym = symbol if symbol.endswith(".NS") else f"{symbol}.NS"
        return pd.DataFrame({"Close": prices.get(sym, prices["RELIANCE.NS"])}, index=dates)

    def fake_quote(symbol, **kwargs):
        sym = symbol if symbol.endswith(".NS") else f"{symbol}.NS"
        p = prices.get(sym, prices["RELIANCE.NS"])
        return TickerQuoteResponse(symbol=sym, price=p[-1], previous_close=p[-2], change=1, change_percent=1, fifty_two_week_high=150, fifty_two_week_low=90, market_cap=1_000_000, pe_ratio=20, meta=meta)

    monkeypatch.setattr(comparison, "get_history", fake_history)
    monkeypatch.setattr(comparison, "get_quote", fake_quote)

    req = ComparisonRequest(symbols=["RELIANCE", "TCS"], period="1y")
    res = comparison.compare_stocks(req)
    assert res.pairwise_correlations is not None
    assert "RELIANCE.NS_vs_TCS.NS" in res.pairwise_correlations
    assert isinstance(res.pairwise_correlations["RELIANCE.NS_vs_TCS.NS"], float)
    assert res.correlation_degrees_of_freedom is not None
    dof = res.correlation_degrees_of_freedom["RELIANCE.NS_vs_TCS.NS"]
    assert dof["sample_sessions"] == 19
    assert dof["correlation_significance"] == "SAMPLE_TOO_SMALL_HIGH_VARIANCE"


def test_comparison_correlation_robust_sample(monkeypatch):
    """Verify N >= 30 sessions earns STATISTICALLY_ROBUST significance."""
    dates = pd.date_range("2024-01-01", periods=45, freq="B")
    meta = MetaHeader(source="test", as_of="2024-03-01T00:00:00+05:30", retrieved_at="2024-03-01T00:00:00+05:30", market_data_type="end_of_day")
    prices = {
        "RELIANCE.NS": [100 + i * 2 for i in range(45)],
        "TCS.NS": [100 + i * 1.5 for i in range(45)],
    }

    def fake_history(symbol, **kwargs):
        sym = symbol if symbol.endswith(".NS") else f"{symbol}.NS"
        return pd.DataFrame({"Close": prices.get(sym, prices["RELIANCE.NS"])}, index=dates)

    def fake_quote(symbol, **kwargs):
        sym = symbol if symbol.endswith(".NS") else f"{symbol}.NS"
        p = prices.get(sym, prices["RELIANCE.NS"])
        return TickerQuoteResponse(symbol=sym, price=p[-1], previous_close=p[-2], change=1, change_percent=1, fifty_two_week_high=200, fifty_two_week_low=90, market_cap=1_000_000, pe_ratio=20, meta=meta)

    monkeypatch.setattr(comparison, "get_history", fake_history)
    monkeypatch.setattr(comparison, "get_quote", fake_quote)

    req = ComparisonRequest(symbols=["RELIANCE", "TCS"], period="1y")
    res = comparison.compare_stocks(req)
    dof = res.correlation_degrees_of_freedom["RELIANCE.NS_vs_TCS.NS"]
    assert dof["sample_sessions"] == 44
    assert dof["correlation_significance"] == "STATISTICALLY_ROBUST"
    assert dof["degrees_of_freedom"] == 42


def test_comparison_intent_conditioned_ranking(monkeypatch):
    """Verify intent-conditioned multi-vector winner evaluation for SIP vs SWING."""
    dates = pd.date_range("2024-01-01", periods=10, freq="B")
    meta = MetaHeader(source="test", as_of="2024-01-10T00:00:00+05:30", retrieved_at="2024-01-10T00:00:00+05:30", market_data_type="end_of_day")
    prices = {
        "RELIANCE.NS": [100 + i * 2 for i in range(10)],
        "TCS.NS": [100 + i * 1 for i in range(10)],
    }

    def fake_history(symbol, **kwargs):
        sym = symbol if symbol.endswith(".NS") else f"{symbol}.NS"
        return pd.DataFrame({"Close": prices.get(sym, prices["RELIANCE.NS"]), "Volume": [100000]*10}, index=dates)

    def fake_quote(symbol, **kwargs):
        sym = symbol if symbol.endswith(".NS") else f"{symbol}.NS"
        p = prices.get(sym, prices["RELIANCE.NS"])
        return TickerQuoteResponse(symbol=sym, price=p[-1], previous_close=p[-2], change=1, change_percent=1, fifty_two_week_high=120, fifty_two_week_low=90, market_cap=1_000_000, pe_ratio=20, meta=meta)

    monkeypatch.setattr(comparison, "get_history", fake_history)
    monkeypatch.setattr(comparison, "get_quote", fake_quote)

    # Test SIP_COMPOUNDER
    req_sip = ComparisonRequest(symbols=["RELIANCE", "TCS"], period="1y", intent="SIP_COMPOUNDER")
    res_sip = comparison.compare_stocks(req_sip)
    assert res_sip.intent_conditioned_ranking is not None
    assert res_sip.intent_conditioned_ranking["intent"] == "SIP_COMPOUNDER"
    assert "winner" in res_sip.intent_conditioned_ranking
    assert "institutional_justification" in res_sip.intent_conditioned_ranking
    assert len(res_sip.intent_conditioned_ranking["ranked_symbols"]) == 2

    # Test SWING_POSITIONAL
    req_swing = ComparisonRequest(symbols=["RELIANCE", "TCS"], period="1y", intent="SWING_POSITIONAL")
    res_swing = comparison.compare_stocks(req_swing)
    assert res_swing.intent_conditioned_ranking is not None
    assert res_swing.intent_conditioned_ranking["intent"] == "SWING_POSITIONAL"
    assert "winner" in res_swing.intent_conditioned_ranking

    # Test TURNAROUND intent
    req_turn = ComparisonRequest(symbols=["RELIANCE", "TCS"], period="1y", intent="TURNAROUND")
    res_turn = comparison.compare_stocks(req_turn)
    assert res_turn.intent_conditioned_ranking is not None
    assert res_turn.intent_conditioned_ranking["intent"] == "TURNAROUND"
    assert "winner" in res_turn.intent_conditioned_ranking
    assert len(res_turn.intent_conditioned_ranking["ranked_symbols"]) == 2

    # Test MULTIBAGGER intent
    req_multi = ComparisonRequest(symbols=["RELIANCE", "TCS"], period="1y", intent="MULTIBAGGER")
    res_multi = comparison.compare_stocks(req_multi)
    assert res_multi.intent_conditioned_ranking is not None
    assert res_multi.intent_conditioned_ranking["intent"] == "MULTIBAGGER"
    assert "winner" in res_multi.intent_conditioned_ranking

    # Test VALUE_BUYING intent
    req_val = ComparisonRequest(symbols=["RELIANCE", "TCS"], period="1y", intent="VALUE_BUYING")
    res_val = comparison.compare_stocks(req_val)
    assert res_val.intent_conditioned_ranking is not None
    assert res_val.intent_conditioned_ranking["intent"] == "VALUE_BUYING"
    assert "winner" in res_val.intent_conditioned_ranking


def test_comparison_cross_sector_normalization_notes(monkeypatch):
    """Verify that comparing a bank and a non-bank generates cross-sector advisory notes."""
    dates = pd.date_range("2024-01-01", periods=5, freq="B")
    meta = MetaHeader(source="test", as_of="2024-01-05T00:00:00+05:30", retrieved_at="2024-01-05T00:00:00+05:30", market_data_type="end_of_day")

    def fake_history(symbol, **kwargs):
        return pd.DataFrame({"Close": [100, 101, 102, 103, 104]}, index=dates)

    def fake_quote(symbol, **kwargs):
        return TickerQuoteResponse(symbol=symbol, price=104, previous_close=103, change=1, change_percent=1, fifty_two_week_high=110, fifty_two_week_low=90, market_cap=1_000_000, pe_ratio=20, meta=meta)

    monkeypatch.setattr(comparison, "get_history", fake_history)
    monkeypatch.setattr(comparison, "get_quote", fake_quote)

    req = ComparisonRequest(symbols=["HDFCBANK", "TCS"], period="1y")
    res = comparison.compare_stocks(req)
    assert res.cross_sector_comparison_notes is not None
    assert len(res.cross_sector_comparison_notes) > 0
    assert "Fiduciary Cross-Sector Advisory" in res.cross_sector_comparison_notes[0]
    assert "Price-to-Book (P/B)" in res.cross_sector_comparison_notes[0]





