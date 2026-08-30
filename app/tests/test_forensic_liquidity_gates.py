"""Unit tests for Phase 3 Forensic Risk Gates & Liquidity Ingestion Pre-Filter."""

import numpy as np
import pandas as pd
import pytest

from app.services.decision_brain.mivs_engine import MIVSEngine
from app.services.ingestion.daily_price_ingester import DailyPriceIngester


def test_adtv_liquidity_floor():
    dates = pd.date_range(end="2026-08-30", periods=20, freq="1D")
    
    # Liquid stock: ₹100 close x 50,000 vol = ₹5,000,000 > ₹2.5M
    liquid_df = pd.DataFrame({"Close": [100.0]*20, "Volume": [50000.0]*20}, index=dates)
    assert DailyPriceIngester.check_adtv_liquidity_floor(liquid_df) is True

    # Illiquid stock: ₹10 close x 1,000 vol = ₹10,000 < ₹2.5M
    illiquid_df = pd.DataFrame({"Close": [10.0]*20, "Volume": [1000.0]*20}, index=dates)
    assert DailyPriceIngester.check_adtv_liquidity_floor(illiquid_df) is False


def test_vpvr_vacuum_ratio_calculation():
    dates = pd.date_range(end="2026-08-30", periods=100, freq="1D")
    close = np.linspace(50.0, 100.0, 100)
    volume = np.full(100, 10000.0)
    
    df = pd.DataFrame({"Close": close, "Volume": volume}, index=dates)
    svr = DailyPriceIngester.compute_vpvr_vacuum_ratio(df)
    assert isinstance(svr, float)
    assert 0.0 <= svr <= 1.0


def test_mivs_gate7_pledge_25_pct_veto():
    engine = MIVSEngine()
    mock_output = [{
        "engine_id": "TEST",
        "confidence": 80.0,
        "verdict": "Buy",
        "raw": type("Raw", (), {"results": {"promoter_pledge_pct": 30.0}, "metrics": {}})()
    }]
    res = engine.compute_mivs("HIGH_PLEDGE.NS", mock_output)
    assert res.passed_hard_gates is False
    assert any("Gate 7 Veto" in reason for reason in res.gate_reasons)


def test_mivs_gate8_high_leverage_veto():
    engine = MIVSEngine()
    mock_output = [{
        "engine_id": "TEST",
        "confidence": 80.0,
        "verdict": "Buy",
        "raw": type("Raw", (), {"results": {"debt_to_equity": 1.8, "interest_coverage": 2.0}, "metrics": {}})()
    }]
    res = engine.compute_mivs("HIGH_LEVERAGE.NS", mock_output)
    assert res.passed_hard_gates is False
    assert any("Gate 8 Veto" in reason for reason in res.gate_reasons)
