"""Unit tests for Financial Forensics Engine."""

import pytest
from app.services.intelligence.financial_forensics import FinancialForensicsEngine


def test_cwip_gross_block_acceleration():
    res = FinancialForensicsEngine.compute_cwip_gross_block_acceleration(
        current_cwip=25.0,
        current_gross_block=100.0,
        prev_cwip=10.0,
        prev_gross_block=100.0,
    )
    assert res["cwip_ratio_pct"] == 25.0
    assert res["cwip_acceleration_pct"] == 15.0
    assert res["capacity_expansion_signal"] == "HIGH_CAPACITY_EXPANSION_IMMINENT"


def test_cash_to_cash_cycle_decomposition():
    res = FinancialForensicsEngine.compute_cash_to_cash_cycle_decomposition(
        dso=60.0, dio=90.0, dpo=40.0,
        prev_dso=40.0, prev_dio=70.0, prev_dpo=40.0,
    )
    assert res["current_ccc_days"] == 110.0
    assert res["delta_dso_days"] == 20.0
    assert res["delta_dio_days"] == 20.0
    assert res["working_capital_drag_flag"] is True
    assert res["quality_tier"] == "WARNING"


def test_cash_pat_divergence_persistence():
    cfo = [80.0, 70.0, 60.0, 50.0]
    pat = [100.0, 100.0, 100.0, 100.0]
    res = FinancialForensicsEngine.evaluate_cash_pat_divergence_persistence(cfo, pat, min_consecutive_years=3)
    assert res["consecutive_divergence_years"] == 4
    assert res["persistent_divergence_flag"] is True
    assert res["forensic_risk_severity"] == "CRITICAL"
