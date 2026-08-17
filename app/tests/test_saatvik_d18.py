import pytest
from app.services.strategies.saatvik_d18 import run_saatvik_d18
from app.models.schemas import StrategyRunResponse


def test_saatvik_pass_clean_company():
    """Test clear pass for clean non-sin business."""
    res = run_saatvik_d18("INFY")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "D18"
    assert res.passed_gates is True
    assert res.results["sin_business_activity_flag"] is False
    assert res.metrics["governance_score"] > 0


def test_saatvik_fail_sin_company():
    """Test clear fail for sin business keyword matching."""
    res = run_saatvik_d18("TOBACCO_IND")
    assert isinstance(res, StrategyRunResponse)
    assert res.strategy_id == "D18"
    assert res.passed_gates is False
    assert res.results["sin_business_activity_flag"] is True
    assert res.metrics["governance_score"] == 0


def test_saatvik_boundary_liquor_company():
    """Test boundary case for alcohol/liquor exclusion."""
    res = run_saatvik_d18("GLOBAL_BREWERY")
    assert isinstance(res, StrategyRunResponse)
    assert res.passed_gates is False
    assert "TOBACCO_CIGARETTES" in res.results["flagged_categories"] or "LIQUOR_ALCOHOL" in res.results["flagged_categories"]
