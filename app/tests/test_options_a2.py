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
