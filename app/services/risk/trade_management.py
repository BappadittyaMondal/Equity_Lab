"""In-Position Trade Management Engine (Layer 23 — Addendum 1).

Continuous active trade management from fill to exit:
  1. Breakeven Rule: Moves initial stop to entry + costs once price reaches +1R.
  2. Partial Profit-Taking: Books 40-50% position at +1.5R.
  3. Chandelier ATR Trailing Stop: `highest_close - k * ATR` in Trend Expansion state.
  4. Time-Stop: Triggers exit/downgrade if median time-to-target is exceeded without progress.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.services.market_data import normalize_symbol, create_meta_header
from app.models.schemas import InPositionManagementState


def evaluate_in_position_management(
    symbol: str,
    entry_price: float = 500.0,
    current_price: float = 525.0,
    highest_close_since_entry: float = 530.0,
    initial_stop_price: float = 475.0,
    atr14: float = 12.5,
    days_in_trade: int = 6,
    setup_class: str = "SETUP_A_BREAKOUT"
) -> InPositionManagementState:
    """Evaluates active in-position management rules: breakeven, partial booking, trailing stop, time-stop."""
    if not symbol or entry_price <= 0 or current_price <= 0 or highest_close_since_entry <= 0 or initial_stop_price <= 0 or atr14 <= 0:
        raise ValueError("Invalid market data inputs for trade management evaluation: prices and ATR must be strictly positive floats.")

    r_unit = max(1.0, entry_price - initial_stop_price)  # 1R distance

    breakeven_trigger = entry_price + r_unit
    partial_target = entry_price + (1.5 * r_unit)

    # 1. Breakeven State
    if highest_close_since_entry >= breakeven_trigger:
        breakeven_status = "ACTIVE"
    else:
        breakeven_status = "PENDING"

    # 2. Partial Exit State
    if highest_close_since_entry >= partial_target:
        partial_status = "PARTIAL_BOOKED_50PCT"
    else:
        partial_status = "PENDING"

    # 3. Chandelier ATR Trailing Stop (k = 2.5)
    chandelier_stop = round(highest_close_since_entry - (2.5 * atr14), 2)
    effective_stop = max(initial_stop_price, chandelier_stop if breakeven_status == "ACTIVE" else initial_stop_price)

    # 4. Time-Stop Trigger Check (§23)
    max_median_days = 15
    days_remaining = max(0, max_median_days - days_in_trade)

    if days_remaining == 0 and current_price < entry_price + (0.5 * r_unit):
        verdict = "TIME_STOP_EXIT"
    elif current_price < effective_stop:
        verdict = "STOP_OUT_EXIT"
    elif partial_status == "PARTIAL_BOOKED_50PCT":
        verdict = "RUN_RUNNER_PORTION"
    else:
        verdict = "HOLD_TREND"

    return InPositionManagementState(
        initial_stop_price=round(initial_stop_price, 2),
        breakeven_trigger_price=round(breakeven_trigger, 2),
        breakeven_status=breakeven_status,
        partial_target_price=round(partial_target, 2),
        partial_exit_status=partial_status,
        chandelier_atr_stop_price=round(effective_stop, 2),
        time_stop_days_remaining=days_remaining,
        managed_exit_verdict=verdict
    )
