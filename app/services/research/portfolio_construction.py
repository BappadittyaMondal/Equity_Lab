"""Portfolio Position Sizing, Exit Discipline & Drawdown Engine (§35, §36, §37).

Calculates fractional-Kelly sizing, liquidity-based position caps, archetype scaling ladders,
sell discipline exit triggers, and archetype-conditional drawdown tolerance bands.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from app.services.market_data import normalize_symbol, create_meta_header
from app.models.schemas import PortfolioPositionSizingSignal


def evaluate_portfolio_construction(
    symbol: str,
    mivs_score: float = 75.0,
    evidence_confidence_pct: float = 80.0,
    adtv_cr: float = 12.5,
    free_float_mcap_cr: float = 3500.0,
    archetype: str = "EARLY_GROWTH",
    portfolio_inputs: Optional[Dict[str, Any]] = None,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Calculates position sizing, liquidity caps, exit triggers, and drawdown tolerance."""
    norm_symbol = normalize_symbol(symbol)
    data = portfolio_inputs or {}
    evidence = []

    # 1. Fractional-Kelly Sizing (§35)
    win_prob = min(0.80, max(0.20, (mivs_score / 100.0) * (evidence_confidence_pct / 100.0)))
    payoff_ratio = 3.0  # 3:1 reward-to-risk benchmark for early multibaggers
    full_kelly = (win_prob * payoff_ratio - (1.0 - win_prob)) / payoff_ratio
    fractional_kelly = max(0.01, full_kelly * 0.25)  # Quarter-Kelly safety factor
    conviction_weight_pct = round(fractional_kelly * 100.0, 1)

    # 2. Liquidity, Thesis Maturity & Discovery Status Caps
    liquidity_cap_pct = round(min(8.0, max(1.0, (adtv_cr * 5.0 * 0.05 / 500.0) * 100.0)), 1)
    
    confirmed_quarters = data.get("confirmed_quarters", data.get("thesis_maturity", {}).get("confirmed_quarters", 0))
    if confirmed_quarters == 0:
        maturity_cap_pct = 2.5  # Starter position cap for unconfirmed hypothesis
        thesis_status = "Hypothesis (Starter Position)"
    elif confirmed_quarters == 1:
        maturity_cap_pct = 5.0  # Developing thesis cap
        thesis_status = "Early Confirmation (Developing)"
    else:
        maturity_cap_pct = 8.0  # Full proven execution
        thesis_status = "Confirmed Execution (Proven)"

    conviction_cap_pct = 7.5 if mivs_score >= 85.0 else (5.0 if mivs_score >= 70.0 else 2.5)

    recommended_pct = round(min(conviction_weight_pct, liquidity_cap_pct, conviction_cap_pct, maturity_cap_pct), 1)

    # 3. Scaling Ladder (§35)
    scaling_ladder = [
        {"stage": "STARTER_POSITION", "size_pct": round(recommended_pct * 0.5, 1), "condition": "Initial thesis formation & Gate pass"},
        {"stage": "FULL_POSITION", "size_pct": recommended_pct, "condition": f"Confirmed execution ({thesis_status})"}
    ]

    # 4. Sell Discipline & Exit Framework (§36)
    exit_triggers = [
        "VALUATION_TRIM: Expectation gap closed; Reverse DCF implied growth exceeds fundamental CAGR",
        "THESIS_PLAYED_OUT: Primary growth catalyst fully realized and public consensus formed",
        "KILL_SWITCH: Triggered if ROIC falls below 12% or promoter pledge exceeds 30%"
    ]

    # 5. Drawdown Tolerance Band per Archetype (§37)
    archetype_upper = archetype.upper().strip()
    if archetype_upper == "TURNAROUND":
        drawdown_tolerance_band = 40.0
    elif archetype_upper in ["EARLY_GROWTH", "HIGH_GROWTH"]:
        drawdown_tolerance_band = 25.0
    else:
        # COMPOUNDER / GARP
        drawdown_tolerance_band = 18.0

    evidence.append(f"Position Sizing: {recommended_pct}% (Conviction: {conviction_weight_pct}% | Liquidity Cap: {liquidity_cap_pct}%)")
    evidence.append(f"Fractional-Kelly (Quarter-Kelly): {fractional_kelly * 100.0:.1f}% | Win Prob: {win_prob * 100.0:.0f}%")
    evidence.append(f"Archetype Drawdown Tolerance: {drawdown_tolerance_band:.0f}% | Archetype: {archetype_upper}")

    signal = PortfolioPositionSizingSignal(
        recommended_position_pct=recommended_pct,
        fractional_kelly_weight=round(fractional_kelly, 4),
        liquidity_cap_pct=liquidity_cap_pct,
        correlation_group=f"{archetype_upper}_BASKET",
        scaling_ladder=scaling_ladder,
        exit_triggers=exit_triggers,
        drawdown_tolerance_band_pct=drawdown_tolerance_band
    )

    return {
        "symbol": norm_symbol,
        "executed_at": datetime.now().isoformat(),
        "recommended_position_pct": recommended_pct,
        "drawdown_tolerance_band_pct": drawdown_tolerance_band,
        "portfolio_signal": signal.model_dump(),
        "evidence": evidence,
        "meta": create_meta_header(source="Portfolio Position Sizing Engine (§35, §36, §37)")
    }
