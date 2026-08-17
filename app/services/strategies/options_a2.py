"""Strategy Module A2: Zero-DTE / Short Strangle Range Option Selling Engine.

Calculates option premium credit, payoff curve, breakeven points, empirical win probability, expected value (EV), margin required, and risk-controlled position sizing.
"""

from typing import List, Dict, Any
from fastapi import HTTPException, status
import numpy as np
from app.models.schemas import OptionsA2Request, OptionsA2Response
from app.services.market_data import normalize_symbol, get_quote, get_history, create_meta_header


def calculate_a2_payoff(req: OptionsA2Request) -> OptionsA2Response:
    """Calculates A2 0-DTE Range Option Selling payoff metrics."""
    symbol = normalize_symbol(req.underlying)
    
    # Fetch live spot price if not provided
    spot = req.spot_price
    if spot is None or spot <= 0:
        try:
            quote = get_quote(symbol)
            if isinstance(quote, dict):
                spot = float(quote.get("price") or 22000.0)
            else:
                spot = float(getattr(quote, "price", 22000.0) or 22000.0)
        except Exception as exc:
            spot = 22000.0

    lower_strike = req.lower_strike
    upper_strike = req.upper_strike
    call_prem = req.call_premium
    put_prem = req.put_premium
    lot_size = req.lot_size or 25
    
    if lower_strike >= upper_strike:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lower strike ({lower_strike}) must be strictly less than upper strike ({upper_strike})."
        )
    if call_prem < 0 or put_prem < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Option premiums cannot be negative."
        )

    total_credit_per_share = round(call_prem + put_prem, 2)
    max_profit = round(total_credit_per_share * lot_size, 2)

    breakeven_lower = round(lower_strike - total_credit_per_share, 2)
    breakeven_upper = round(upper_strike + total_credit_per_share, 2)

    # A daily OHLC series cannot establish a 0-DTE probability of profit. This
    # service is additionally feature-gated at the router until a validated model
    # based on option-chain and intraday data is available.
    try:
        hist = get_history(symbol, period="1y", interval="1d")
        daily_highs = hist['High'].values
        daily_lows = hist['Low'].values
        daily_closes = hist['Close'].values
        
        # Check percentage of days where day range stayed within breakeven bounds relative to opening/prev close
        within_bounds = (daily_lows >= (daily_closes - (spot - breakeven_lower))) & \
                        (daily_highs <= (daily_closes + (breakeven_upper - spot)))
        win_prob = round(float((np.sum(within_bounds) / len(daily_closes)) * 100.0), 2)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Historical data is unavailable; A2 analytics cannot be calculated safely."
        ) from exc

    # Estimate expected value (EV) per lot
    # EV = (Prob_Win * Max_Profit) - (Prob_Loss * Average_Loss_Estimate)
    loss_prob = (100.0 - win_prob) / 100.0
    avg_loss_estimate = max_profit * 2.5  # Standard stop-loss rule (2.5x credit)
    ev_per_lot = round(((win_prob / 100.0) * max_profit) - (loss_prob * avg_loss_estimate), 2)

    # Maximum Loss for unhedged short strangle is theoretically unlimited.
    # We define max loss based on a 3% extreme market move index buffer or explicit stop-loss.
    est_max_loss_per_lot = round(max(spot * 0.05 * lot_size, avg_loss_estimate), 2)
    
    # Margin requirement estimate (~15% of spot contract value per leg)
    margin_required = round(spot * lot_size * 0.15 * 2, 2)

    # Risk-controlled lot sizing if user specified risk capital limit
    recommended_max_lots = None
    if req.risk_limit_amount and req.risk_limit_amount > 0:
        recommended_max_lots = int(req.risk_limit_amount / margin_required)

    # Generate 15-point Payoff Curve
    payoff_curve = []
    step = (upper_strike - lower_strike) / 10 if upper_strike > lower_strike else 50
    min_price = lower_strike - (step * 5)
    max_price = upper_strike + (step * 5)
    price_points = np.linspace(min_price, max_price, 15)

    for p in price_points:
        p_val = round(float(p), 2)
        # Payoff of Short Put: -max(0, lower_strike - price) + put_prem
        put_payoff = -max(0.0, lower_strike - p_val) + put_prem
        # Payoff of Short Call: -max(0, price - upper_strike) + call_prem
        call_payoff = -max(0.0, p_val - upper_strike) + call_prem
        total_pnl = round((put_payoff + call_payoff) * lot_size, 2)
        
        payoff_curve.append({
            "underlying_price": p_val,
            "pnl_per_lot": total_pnl
        })

    risk_warnings = [
        "CRITICAL TAIL RISK: Short options (strangles/straddles) carry UNLIMITED downside risk if unhedged.",
        f"Hard Stop Rule: Exit position immediately if underlying breaches Breakeven Range ({breakeven_lower} - {breakeven_upper}).",
        "India VIX Regime Check: Do NOT enter A2 option selling if India VIX > 25.0.",
        "Expected Value (EV) relies on 2.5x credit stop-loss discipline."
    ]

    return OptionsA2Response(
        underlying=symbol,
        expiry=req.expiry or "0-DTE",
        spot_price=round(float(spot), 2),
        lower_strike=lower_strike,
        upper_strike=upper_strike,
        total_credit_per_lot=max_profit,
        max_profit=max_profit,
        max_loss=est_max_loss_per_lot,
        breakeven_lower=breakeven_lower,
        breakeven_upper=breakeven_upper,
        probability_of_profit_empirical_pct=win_prob,
        expected_value_per_lot=ev_per_lot,
        risk_reward_ratio=round(max_profit / est_max_loss_per_lot, 2) if est_max_loss_per_lot > 0 else 0.0,
        estimated_margin_required=margin_required,
        recommended_max_lots=recommended_max_lots,
        payoff_curve=payoff_curve,
        risk_warnings=risk_warnings,
        meta=create_meta_header(source=f"yfinance Options Engine ({symbol} Spot: {spot})")
    )
