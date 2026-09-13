import pytest
from app.services.strategies.reverse_dcf_c9 import run_reverse_dcf_c9
from app.models.schemas import StrategyRunResponse


def test_reverse_dcf_pass():
    """Test clear pass scenario for Reverse DCF engine."""
    res = run_reverse_dcf_c9("RELIANCE", discount_rate=0.12, terminal_growth=0.04)
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "C9"
    assert "implied_10y_cagr" in res.results
    assert res.results.get("model_type") == "PE_IMPLIED_GROWTH_HEURISTIC"
    assert res.metrics.get("model_type") == "PE_IMPLIED_GROWTH_HEURISTIC"
    assert "fcf_yield_pct" in res.metrics


def test_reverse_dcf_high_discount_rate():
    """Test scenario with high cost of equity discount rate."""
    res = run_reverse_dcf_c9("TCS", discount_rate=0.15, terminal_growth=0.05)
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "C9"
    assert res.metrics["discount_rate"] == 0.15


def test_reverse_dcf_boundary_sensitivity():
    """Test boundary sensitivity matrix generation."""
    res = run_reverse_dcf_c9("INFY")
    assert isinstance(res, StrategyRunResponse)
    assert "sensitivity_matrix" in res.results
    assert isinstance(res.results["sensitivity_matrix"], dict)
    assert "earnings_yield_pct" in res.metrics


def test_reverse_dcf_with_retention_rate():
    """Test Gordon Growth with non-zero reinvestment/retention rate."""
    res_b0 = run_reverse_dcf_c9("RELIANCE", discount_rate=0.12, retention_rate=0.0)
    res_b50 = run_reverse_dcf_c9("RELIANCE", discount_rate=0.12, retention_rate=0.50)
    assert res_b0.status == "production"
    assert res_b50.status == "production"
    # When retention rate is 50%, required implied growth is higher than 0% retention
    g_b0 = res_b0.metrics["implied_growth_rate_pct"]
    g_b50 = res_b50.metrics["implied_growth_rate_pct"]
    assert g_b50 > g_b0
    assert res_b50.metrics["retention_rate"] == 0.50


def test_reverse_dcf_negative_pe_abstention(monkeypatch):
    """Test negative PE triggers clean valuation abstention for turnaround/distressed scenarios."""
    from app.services.strategies import reverse_dcf_c9
    monkeypatch.setattr(reverse_dcf_c9, "get_quote", lambda sym, as_of=None: {"price": 100.0, "pe_ratio": -5.2})
    res = run_reverse_dcf_c9("DISTRESSED_CO")
    assert res.status == "data_insufficient"
    assert res.passed_gates is False
    assert res.results["valuation_abstention_reason"] == "NEGATIVE_TRAILING_PE_REQUIRING_ASSET_OR_CFO_MODEL"
    assert res.metrics["pe_ratio"] == -5.2


def test_reverse_dcf_strict_graham_ncav(monkeypatch):
    """Verify strict Graham NCAV (current_assets - total_liabilities) is computed when balance sheet items are present."""
    from app.services.strategies import reverse_dcf_c9
    from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
    monkeypatch.setattr(reverse_dcf_c9, "get_quote", lambda sym, as_of=None: {"price": 50.0, "pe_ratio": -10.0})
    monkeypatch.setattr(
        ScreenerCloudConnector,
        "get_company_fundamentals",
        lambda sym: {"current_assets": 500.0, "total_liabilities": 300.0}
    )
    res = run_reverse_dcf_c9("DISTRESSED_CO")
    assert res.status == "data_insufficient"
    assert res.results["asset_floor_model"] == "AGGREGATE_NET_WORKING_CAPITAL"
    assert res.results["ncav_cr"] == 200.0
    assert res.results["estimated_asset_floor_cr"] == 200.0
    assert res.results["turnaround_asset_backing"] == "ADEQUATE"


def test_reverse_dcf_strict_graham_liquidation_haircuts(monkeypatch):
    """Verify strict Graham Liquidation NCAV applies 0.75x receivables and 0.50x inventory haircuts."""
    from app.services.strategies import reverse_dcf_c9
    from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
    monkeypatch.setattr(reverse_dcf_c9, "get_quote", lambda sym, as_of=None: {"price": 50.0, "pe_ratio": -10.0})
    monkeypatch.setattr(
        ScreenerCloudConnector,
        "get_company_fundamentals",
        lambda sym: {
            "cash": 100.0,
            "trade_receivables": 200.0,
            "inventory": 100.0,
            "current_assets": 500.0,
            "total_liabilities": 200.0
        }
    )
    # Liquidation NCAV = 100 + (0.75 * 200) + (0.50 * 100) - 200 = 100 + 150 + 50 - 200 = 100.0
    res = run_reverse_dcf_c9("DISTRESSED_CO")
    assert res.status == "data_insufficient"
    assert res.results["asset_floor_model"] == "STRICT_GRAHAM_LIQUIDATION_NCAV"
    assert res.results["tier"] == "STRICT_GRAHAM_LIQUIDATION"
    assert res.results["ncav_cr"] == 100.0
    assert res.results["estimated_asset_floor_cr"] == 100.0
    assert res.results["turnaround_asset_backing"] == "ADEQUATE"


def test_reverse_dcf_graham_tangible_bv_proxy(monkeypatch):
    """Verify fallback to GRAHAM_TANGIBLE_BV_PROXY when detailed current assets / liabilities are absent."""
    from app.services.strategies import reverse_dcf_c9
    from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
    monkeypatch.setattr(reverse_dcf_c9, "get_quote", lambda sym, as_of=None: {"price": 50.0, "pe_ratio": -10.0})
    monkeypatch.setattr(
        ScreenerCloudConnector,
        "get_company_fundamentals",
        lambda sym: {"cash": 50.0, "book_value": 100.0}
    )
    res = run_reverse_dcf_c9("DISTRESSED_CO")
    assert res.status == "data_insufficient"
    assert res.results["asset_floor_model"] == "GRAHAM_TANGIBLE_BV_PROXY"
    assert res.results["estimated_asset_floor_cr"] == 70.0
    assert res.results["turnaround_asset_backing"] == "ADEQUATE"


