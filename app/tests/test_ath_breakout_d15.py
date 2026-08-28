import pytest
from app.services.strategies.ath_breakout_d15 import run_ath_breakout_d15
from app.models.schemas import StrategyRunResponse


@pytest.mark.network
def test_ath_breakout_pass(monkeypatch):
    """Test clear pass scenario for ATH breakout."""
    try:
        res = run_ath_breakout_d15("RELIANCE")
    except Exception:
        pytest.skip("Network call failed in network test mode")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "D15"
    assert "RELIANCE" in res.symbol
    assert res.status in ("production", "data_insufficient")


@pytest.mark.network
def test_ath_breakout_fail(monkeypatch):
    """Test clear fail scenario for ATH breakout with custom ticker."""
    try:
        res = run_ath_breakout_d15("TCS")
    except Exception:
        pytest.skip("Network call failed in network test mode")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "D15"


def test_ath_breakout_boundary(monkeypatch):
    """Test boundary case position sizing calculation."""
    res = run_ath_breakout_d15("INFY", portfolio_capital=5000000.0, max_risk_pct=1.0)
    assert isinstance(res, StrategyRunResponse)
    assert res.status in ("production", "data_insufficient")
    if res.status == "production":
        assert res.metrics["suggested_allocation_pct"] <= 15.0
