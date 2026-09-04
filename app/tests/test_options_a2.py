"""Unit tests for A2 0-DTE Option strategy payoff engine.
"""

import pytest
import pandas as pd
from app.models.schemas import OptionsA2Request
from app.services.strategies import options_a2


def test_options_a2_payoff(monkeypatch):
    history = pd.DataFrame({
        "High": [22500.0, 22525.0, 22575.0],
        "Low": [22350.0, 22375.0, 22400.0],
        "Close": [22400.0, 22450.0, 22500.0],
    })
    monkeypatch.setattr(options_a2, "get_history", lambda *args, **kwargs: history)
    req = OptionsA2Request(
        underlying="^NSEI",
        expiry="0-DTE",
        spot_price=22450.0,
        lower_strike=22200.0,
        upper_strike=22700.0,
        call_premium=45.0,
        put_premium=55.0,
        lot_size=25,
        risk_limit_amount=100000.0
    )
    res = options_a2.calculate_a2_payoff(req)
    assert res.spot_price == 22450.0
    assert res.total_credit_per_lot == 2500.0  # (45 + 55) * 25
    assert res.breakeven_lower == 22100.0     # 22200 - 100
    assert res.breakeven_upper == 22800.0     # 22700 + 100
    assert len(res.payoff_curve) == 15
    assert len(res.risk_warnings) >= 3
    # A capital limit below the estimated margin must recommend no position,
    # rather than forcing the user into one lot.
    assert res.recommended_max_lots == 0


def test_options_a2_invalid_strikes():
    with pytest.raises(Exception):
        req = OptionsA2Request(
            underlying="^NSEI",
            lower_strike=22700.0,
            upper_strike=22200.0,  # Invalid: lower > upper
            call_premium=10.0,
            put_premium=10.0
        )
        options_a2.calculate_a2_payoff(req)


def test_options_a2_regulatory_fo_ban_veto(monkeypatch):
    """Verify that options A2 engine raises 403 HTTP exception if underlying is in F&O ban or ASM Stage III/IV."""
    from fastapi import HTTPException
    from app.services.risk import surveillance_gate
    from app.models.schemas import SurveillanceRiskGate

    mock_gate = SurveillanceRiskGate(
        asm_stage="STAGE_III",
        gsm_stage="CLEAN",
        t2t_flag=False,
        fo_ban_flag=True,
        circuit_band_pct=20.0,
        hard_gate_status="FAIL"
    )
    monkeypatch.setattr(
        surveillance_gate,
        "evaluate_surveillance_and_cost_gate",
        lambda *args, **kwargs: mock_gate
    )

    req = OptionsA2Request(
        underlying="BANNED_STOCK",
        spot_price=500.0,
        lower_strike=480.0,
        upper_strike=520.0,
        call_premium=10.0,
        put_premium=10.0
    )

    with pytest.raises(HTTPException) as exc_info:
        options_a2.calculate_a2_payoff(req)
    assert exc_info.value.status_code == 403
    assert "REGULATORY_RESTRICTION" in exc_info.value.detail

