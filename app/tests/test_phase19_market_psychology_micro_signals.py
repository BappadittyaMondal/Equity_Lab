"""Unit tests for Phase 19: Market Psychology, Operator Churn Trap & Steenbarger Performance Guard.
"""

from datetime import datetime
import pandas as pd
import numpy as np

from app.services.strategies.technical_volume_microstructure import evaluate_volume_and_microstructure
from app.services.research.portfolio_construction import evaluate_portfolio_construction


def test_operator_churn_trap_detection(monkeypatch):
    """Verify that high RVOL with low delivery % is correctly flagged as an operator churn trap."""
    # Generate mock history with recent high volume
    dates = pd.date_range(end=datetime.now(), periods=40, freq="D")
    df = pd.DataFrame({
        "Open": [100.0] * 39 + [102.0],
        "High": [105.0] * 39 + [115.0],
        "Low": [95.0] * 39 + [96.0],
        "Close": [101.0] * 39 + [108.0],
        "Volume": [10000.0] * 39 + [35000.0]  # 3.5x volume surge
    }, index=dates)

    monkeypatch.setattr(
        "app.services.strategies.technical_volume_microstructure.get_history",
        lambda symbol, period="1y", interval="1d", as_of=None: df
    )

    # 1. Speculative churn trap: low delivery (15%)
    res_churn = evaluate_volume_and_microstructure("TEST_CHURN", delivery_override_pct=15.0)
    assert res_churn["rvol"] >= 2.5
    assert res_churn["operator_churn_trap"] is True
    assert "OPERATOR CHURN TRAP DETECTED" in " ".join(res_churn["evidence"])
    assert res_churn["is_exchange_reported_delivery"] is True

    # 2. Genuine institutional accumulation: high delivery (55%)
    res_accum = evaluate_volume_and_microstructure("TEST_ACCUM", delivery_override_pct=55.0)
    assert res_accum["rvol"] >= 2.5
    assert res_accum["operator_churn_trap"] is False
    assert res_accum["participation_score"] > res_churn["participation_score"]


def test_steenbarger_drawdown_circuit_breaker():
    """Verify that consecutive stop-outs trigger the 50% capital allocation throttle."""
    # 1. Baseline normal sizing with 0 stop-outs
    res_normal = evaluate_portfolio_construction(
        "TEST_TICKER",
        mivs_score=85.0,
        evidence_confidence_pct=80.0,
        portfolio_inputs={"consecutive_stop_losses": 0}
    )
    assert res_normal["tilt_protection_active"] is False
    assert res_normal["tilt_multiplier"] == 1.0
    normal_pct = res_normal["recommended_position_pct"]
    assert normal_pct > 0.0

    # 2. Drawdown event: 2 consecutive stop-outs triggers 50% throttle
    res_tilt = evaluate_portfolio_construction(
        "TEST_TICKER",
        mivs_score=85.0,
        evidence_confidence_pct=80.0,
        portfolio_inputs={"consecutive_stop_losses": 2}
    )
    assert res_tilt["tilt_protection_active"] is True
    assert res_tilt["tilt_multiplier"] == 0.50
    assert res_tilt["recommended_position_pct"] == round(normal_pct * 0.50, 1)
    assert "STEENBARGER DRAWDOWN CIRCUIT BREAKER ACTIVE" in " ".join(res_tilt["evidence"])


def test_backwards_compatibility_and_defaults():
    """Verify that legacy callers without new arguments run with full backward compatibility."""
    # Portfolio construction with empty inputs
    res_legacy_port = evaluate_portfolio_construction("TEST_LEGACY", mivs_score=75.0)
    assert res_legacy_port["tilt_protection_active"] is False
    assert "recommended_position_pct" in res_legacy_port
    assert res_legacy_port["portfolio_signal"]["tilt_protection_active"] is False

    # Volume microstructure with default signature
    res_legacy_vol = evaluate_volume_and_microstructure("TEST_LEGACY")
    assert "operator_churn_trap" in res_legacy_vol
    assert "rvol" in res_legacy_vol
    assert "delivery_pct" in res_legacy_vol
