import pytest
from app.services.strategies.sepa_b8 import run_sepa_b8
from app.models.schemas import StrategyRunResponse


def test_sepa_pass():
    """Test clear pass scenario for SEPA growth engine."""
    res = run_sepa_b8("RELIANCE")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "B8"
    assert "sepa_classification" in res.results
    assert "one_year_momentum_pct" in res.metrics


def test_sepa_fail():
    """Test fail scenario for low momentum symbol."""
    res = run_sepa_b8("LAGGING_STOCK")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "B8"
    assert "peg_ratio" in res.metrics


def test_sepa_boundary():
    """Test boundary metrics checking."""
    res = run_sepa_b8("TCS")
    assert isinstance(res, StrategyRunResponse)
    assert res.metrics["peg_ratio"] >= 0
    assert "three_month_momentum_pct" in res.metrics
