"""Unit test suite for Fundamental Metrics Library (Phase 6)."""

from types import SimpleNamespace
import pytest
from app.services.strategies.fundamental_metrics import (
    compute_revenue_metrics,
    compute_profitability_metrics,
    compute_balance_sheet_metrics,
    compute_cashflow_metrics,
    compute_working_capital_turnover,
    compute_roic_wacc_spread,
    compute_debt_ebitda,
    compute_ocf_yield,
    compute_dupont_roe,
    compute_fundamental_quality_score,
)


def _make_obs(metric: str, value: float, period_end: str = "2026-03-31"):
    return SimpleNamespace(metric=metric, value=value, period_end=period_end)


def test_cfo_pat_earnings_quality():
    financials = [
        _make_obs("cfo", 1200.0),
        _make_obs("pat", 1000.0),
    ]
    res = compute_cashflow_metrics(financials)
    assert res["status"] == "PRODUCTION"
    assert res["earnings_quality_ratio"] == 1.2


def test_working_capital_turnover():
    financials = [
        _make_obs("revenue", 5000.0),
        _make_obs("working_capital", 1000.0),
    ]
    res = compute_working_capital_turnover(financials)
    assert res["status"] == "PRODUCTION"
    assert res["working_capital_turnover"] == 5.0

    # Missing data handling
    empty_res = compute_working_capital_turnover([])
    assert empty_res["status"] == "DATA_UNAVAILABLE"
    assert empty_res["working_capital_turnover"] is None


def test_roic_wacc_spread():
    financials = [_make_obs("roic", 18.5)]
    res = compute_roic_wacc_spread(financials, wacc=11.5)
    assert res["status"] == "PRODUCTION"
    assert res["spread_pct"] == 7.0
    assert res["value_creating"] is True

    # Missing data handling
    empty_res = compute_roic_wacc_spread([])
    assert empty_res["status"] == "DATA_UNAVAILABLE"
    assert empty_res["spread_pct"] is None


def test_debt_ebitda():
    financials = [
        _make_obs("total_debt", 3000.0),
        _make_obs("ebitda", 1500.0),
    ]
    res = compute_debt_ebitda(financials)
    assert res["status"] == "PRODUCTION"
    assert res["debt_ebitda_ratio"] == 2.0

    # Missing data handling
    empty_res = compute_debt_ebitda([])
    assert empty_res["status"] == "DATA_UNAVAILABLE"
    assert empty_res["debt_ebitda_ratio"] is None


def test_ocf_yield():
    financials = [_make_obs("cfo", 2500.0)]
    res = compute_ocf_yield(financials, market_cap=50000.0)
    assert res["status"] == "PRODUCTION"
    assert res["ocf_yield_pct"] == 5.0

    # Missing data handling
    empty_res = compute_ocf_yield(financials, market_cap=None)
    assert empty_res["status"] == "DATA_UNAVAILABLE"
    assert empty_res["ocf_yield_pct"] is None


def test_dupont_roe():
    financials = [
        _make_obs("pat", 500.0),
        _make_obs("revenue", 5000.0),
        _make_obs("total_assets", 10000.0),
        _make_obs("total_equity", 2500.0),
    ]
    res = compute_dupont_roe(financials)
    assert res["status"] == "PRODUCTION"
    assert res["roe_pct"] == 20.0
    assert res["net_margin_pct"] == 10.0
    assert res["asset_turnover"] == 0.5
    assert res["equity_multiplier"] == 4.0


def test_empty_financials_data_unavailable():
    assert compute_revenue_metrics([])["status"] == "DATA_UNAVAILABLE"
    assert compute_profitability_metrics([])["status"] == "DATA_UNAVAILABLE"
    assert compute_balance_sheet_metrics([])["status"] == "DATA_UNAVAILABLE"
    assert compute_cashflow_metrics([])["status"] == "DATA_UNAVAILABLE"
