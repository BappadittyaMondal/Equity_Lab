"""Institutional Execution Cost & Liquidity Impact Model (Phase 4 — Institutional Truth-Plane).

Implements:
  1. Almgren-Chriss Square-Root Law Market Impact Model:
     Impact = gamma * sigma_daily * sqrt(Order_Shares / ADV_20d)
  2. Institutional ADV Participation Limit (5% Cap):
     Limits single-session execution to <= 5% of 20-day Average Daily Volume.
     Recommends multi-day TWAP/VWAP algorithmic slicing if order exceeds cap.
  3. Strict Order State Machine:
     DRAFT -> VALIDATED -> SURVEILLANCE_CLEARED -> ROUTED -> FILLED | REJECTED | VETOED_SURVEILLANCE
"""

import math
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from app.services.market_data import normalize_symbol, create_meta_header, get_ist_now_str
from app.services.risk.surveillance_gate import evaluate_surveillance_and_cost_gate, is_surveillance_cleared


ORDER_VALID_STATES = {
    "DRAFT",
    "VALIDATED",
    "SURVEILLANCE_CLEARED",
    "ROUTED",
    "FILLED",
    "REJECTED",
    "VETOED_SURVEILLANCE"
}


def calculate_almgren_chriss_impact(
    order_shares: float,
    adv_20d_shares: float,
    daily_volatility_pct: float = 2.0,
    gamma: float = 0.14
) -> Dict[str, Any]:
    """Calculates expected market impact slippage under the Almgren-Chriss square-root law.
    
    Args:
        order_shares: Intended order size in number of shares.
        adv_20d_shares: 20-day Average Daily Volume in shares.
        daily_volatility_pct: Daily price volatility percentage (e.g. 2.0%).
        gamma: Institutional market impact constant (default 0.14 for Indian equities).
    """
    if adv_20d_shares <= 0 or order_shares <= 0:
        return {
            "market_impact_pct": 0.0,
            "participation_rate_pct": 0.0,
            "adv_cap_exceeded": False,
            "recommended_execution_horizon_days": 1,
            "execution_algorithm": "DIRECT_LIMIT_EXECUTION"
        }

    participation_rate = float(order_shares / adv_20d_shares)
    participation_rate_pct = round(participation_rate * 100.0, 3)

    # Square-root market impact: I = gamma * sigma * sqrt(Q / V)
    sigma_dec = max(0.005, daily_volatility_pct / 100.0)
    impact_dec = gamma * sigma_dec * math.sqrt(participation_rate)
    impact_pct = round(impact_dec * 100.0, 4)

    # Institutional 5% ADV Participation Cap
    adv_cap_exceeded = participation_rate > 0.05
    if adv_cap_exceeded:
        horizon_days = max(1, math.ceil(participation_rate / 0.05))
        exec_algo = "ALGORITHMIC_TWAP_VWAP"
        max_daily_shares = round(0.05 * adv_20d_shares, 0)
    else:
        horizon_days = 1
        exec_algo = "DIRECT_LIMIT_EXECUTION"
        max_daily_shares = float(order_shares)

    return {
        "market_impact_pct": impact_pct,
        "participation_rate_pct": participation_rate_pct,
        "adv_cap_exceeded": adv_cap_exceeded,
        "max_recommended_daily_shares": max_daily_shares,
        "recommended_execution_horizon_days": horizon_days,
        "execution_algorithm": exec_algo
    }


def evaluate_institutional_execution_envelope(
    symbol: str,
    price: float = 500.0,
    order_value_inr: float = 1_000_000.0,
    adv_20d_inr: float = 50_000_000.0,
    daily_volatility_pct: float = 2.0,
    surveillance_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Evaluates the full institutional execution envelope:
    Regulatory surveillance veto, Indian transaction costs, and Almgren-Chriss market impact.
    """
    norm_sym = normalize_symbol(symbol)
    surv_gate = evaluate_surveillance_and_cost_gate(
        symbol=norm_sym,
        price=price,
        trade_value_inr=order_value_inr,
        surveillance_data=surveillance_data
    )

    cleared_for_trading = is_surveillance_cleared(surv_gate)
    order_shares = order_value_inr / max(1.0, price)
    adv_shares = adv_20d_inr / max(1.0, price)

    impact_metrics = calculate_almgren_chriss_impact(
        order_shares=order_shares,
        adv_20d_shares=adv_shares,
        daily_volatility_pct=daily_volatility_pct
    )

    # Total Expected Execution Drag = Regulatory Trade Costs + Market Impact
    total_expected_friction_pct = round(
        surv_gate.total_roundtrip_cost_pct + impact_metrics["market_impact_pct"], 3
    )

    status_code = "APPROVED_FOR_EXECUTION" if cleared_for_trading else "VETOED_REGULATORY_SURVEILLANCE"
    if cleared_for_trading and impact_metrics["adv_cap_exceeded"]:
        status_code = "APPROVED_ALGORITHMIC_SLICING_REQUIRED"

    meta = create_meta_header(source="Institutional Execution & Liquidity Engine")
    meta["surveillance_status"] = surv_gate.hard_gate_status

    return {
        "symbol": norm_sym,
        "evaluated_at": get_ist_now_str(),
        "status_code": status_code,
        "cleared_for_trading": cleared_for_trading,
        "order_value_inr": order_value_inr,
        "order_shares": round(order_shares, 1),
        "surveillance_gate": surv_gate.model_dump() if hasattr(surv_gate, "model_dump") else surv_gate.dict(),
        "regulatory_roundtrip_cost_pct": surv_gate.total_roundtrip_cost_pct,
        "market_impact_pct": impact_metrics["market_impact_pct"],
        "total_expected_friction_pct": total_expected_friction_pct,
        "participation_rate_pct": impact_metrics["participation_rate_pct"],
        "adv_cap_exceeded": impact_metrics["adv_cap_exceeded"],
        "max_recommended_daily_shares": impact_metrics["max_recommended_daily_shares"],
        "recommended_execution_horizon_days": impact_metrics["recommended_execution_horizon_days"],
        "execution_algorithm": impact_metrics["execution_algorithm"],
        "meta": meta
    }


def transition_order_state(
    current_state: str,
    target_state: str,
    cleared_surveillance: bool = True
) -> Tuple[str, str]:
    """Validates and executes formal state transitions in the Order State Machine.
    
    Allowed transitions:
      DRAFT -> VALIDATED
      VALIDATED -> SURVEILLANCE_CLEARED (or VETOED_SURVEILLANCE if not cleared)
      SURVEILLANCE_CLEARED -> ROUTED
      ROUTED -> FILLED | REJECTED
    """
    curr = current_state.upper()
    target = target_state.upper()

    if curr not in ORDER_VALID_STATES:
        return "REJECTED", f"Invalid origin state: {curr}"
    if target not in ORDER_VALID_STATES:
        return "REJECTED", f"Invalid target state: {target}"

    if curr == "DRAFT" and target == "VALIDATED":
        return "VALIDATED", "Order parameters mathematically validated."

    if curr == "VALIDATED" and target == "SURVEILLANCE_CLEARED":
        if not cleared_surveillance:
            return "VETOED_SURVEILLANCE", "Order vetoed: failed regulatory surveillance gate."
        return "SURVEILLANCE_CLEARED", "Regulatory clearance approved for routing."

    if curr == "SURVEILLANCE_CLEARED" and target == "ROUTED":
        return "ROUTED", "Order routed to execution venue."

    if curr == "ROUTED" and target in ("FILLED", "REJECTED"):
        return target, f"Order finalized as {target}."

    return "REJECTED", f"Illegal state transition from {curr} to {target}."
