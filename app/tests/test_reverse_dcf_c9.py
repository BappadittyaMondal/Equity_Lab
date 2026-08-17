import pytest
from app.services.strategies.reverse_dcf_c9 import run_reverse_dcf_c9
from app.models.schemas import StrategyRunResponse


def test_reverse_dcf_pass():
    """Test clear pass scenario for Reverse DCF engine."""
    res = run_reverse_dcf_c9("RELIANCE", discount_rate=0.12, terminal_growth=0.04)
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "C9"
    assert "implied_10y_cagr" in res.results
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
