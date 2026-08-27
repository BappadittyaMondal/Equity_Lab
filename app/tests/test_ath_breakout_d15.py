import pytest
from app.services.strategies.ath_breakout_d15 import run_ath_breakout_d15
from app.models.schemas import StrategyRunResponse


def test_ath_breakout_pass(monkeypatch):
    """Test clear pass scenario for ATH breakout."""
    res = run_ath_breakout_d15("RELIANCE")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "D15"
    assert "RELIANCE" in res.symbol
    assert "ath_breakout_status" in res.results
    assert "distance_high_pct" in res.metrics


def test_ath_breakout_fail(monkeypatch):
    """Test clear fail scenario for ATH breakout with custom ticker."""
    res = run_ath_breakout_d15("TCS")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "D15"
    assert "position_size_inr" in res.metrics


def test_ath_breakout_boundary(monkeypatch):
    """Test boundary case position sizing calculation."""
    res = run_ath_breakout_d15("INFY", portfolio_capital=5000000.0, max_risk_pct=1.0)
    assert isinstance(res, StrategyRunResponse)
    assert res.status in ("production", "data_insufficient")
    if res.status == "production":
        assert res.metrics["suggested_allocation_pct"] <= 15.0
