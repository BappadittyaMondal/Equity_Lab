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
    mivs_score: Optional[float] = None,
    evidence_confidence_pct: Optional[float] = None,
    adtv_cr: float = 12.5,
    free_float_mcap_cr: float = 3500.0,
    archetype: str = "EARLY_GROWTH",
    portfolio_inputs: Optional[Dict[str, Any]] = None,
    fund_aum_cr: float = 500.0,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Calculates position sizing, liquidity caps, exit triggers, and drawdown tolerance."""
    norm_symbol = normalize_symbol(symbol)
    data = portfolio_inputs or {}
    evidence = []

    if mivs_score is None:
        mivs_score = data.get("mivs_score")

    if mivs_score is None:
        return {
            "symbol": norm_symbol,
            "status": "data_insufficient",
            "executed_at": datetime.now().isoformat(),
            "recommended_position_pct": 0.0,
            "drawdown_tolerance_band_pct": 0.0,
            "portfolio_signal": None,
            "evidence": ["Cannot size position: MIVS conviction score or evidence confidence unobserved."],
            "meta": create_meta_header(source="Portfolio Construction & Sizing Engine (§35, §36, §37)")
        }

    conf_unobserved = (evidence_confidence_pct is None and "evidence_confidence_pct" not in data)
    conf_pct = float(evidence_confidence_pct if evidence_confidence_pct is not None else data.get("evidence_confidence_pct", 70.0))

    # Dynamic Fund AUM configuration (default 500 Cr)
    aum = float(data.get("fund_aum_cr") or fund_aum_cr or 500.0)

    # 1. Institutional Hard Risk-Budget Sizing (§CRO Capital Protection)
    # Maximum capital at risk per position target: 1.5% of AUM
    max_risk_budget_pct = float(data.get("max_risk_budget_pct", 1.5))
    stop_distance_pct = float(data.get("stop_loss_pct") or data.get("stop_distance_pct") or 6.5)
    stop_distance_pct = max(2.0, min(25.0, stop_distance_pct))
    risk_budget_weight_pct = round((max_risk_budget_pct / (stop_distance_pct / 100.0)), 1)

    # Informational Advisory Diagnostic: Fractional-Kelly Sizing
    # Note: win_prob is an informational heuristic derived from conviction and confidence scores,
    # clamped to empirical bounds [0.20, 0.80] to avoid extreme Kelly over-betting.
    win_prob = min(0.80, max(0.20, (mivs_score / 100.0) * (conf_pct / 100.0)))
    payoff_ratio = 3.0  # 3:1 reward-to-risk benchmark
    full_kelly = (win_prob * payoff_ratio - (1.0 - win_prob)) / payoff_ratio
    fractional_kelly = max(0.01, full_kelly * 0.25)
    advisory_kelly_pct = round(fractional_kelly * 100.0, 1)

    # 2. Liquidity, Thesis Maturity & Discovery Status Caps (§Phase 100 ADV Participation Protection)
    # Institutional liquidity limit: 5 days of 15% ADV participation (total 75% of single-day ADV) relative to fund AUM.
    # Micro-caps are not artificially clamped to 1.0% if their volume requires tighter risk control.
    # When adtv_cr <= 0.0 (untraded, suspended, or halted), allocation fails closed to 0.0% (§105).
    if adtv_cr <= 0.0:
        raw_liq_cap = 0.0
        liquidity_cap_pct = 0.0
    else:
        raw_liq_cap = (adtv_cr * 5.0 * 0.15 / max(aum, 1.0)) * 100.0
        liquidity_cap_pct = round(min(8.0, max(0.1, raw_liq_cap)), 1)
    
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

    base_recommended_pct = round(min(risk_budget_weight_pct, liquidity_cap_pct, conviction_cap_pct, maturity_cap_pct), 1)

    sizing_haircut = float(data.get("sizing_haircut_pct") or 0.0)
    haircut_mult = max(0.10, (100.0 - sizing_haircut) / 100.0) if sizing_haircut > 0 else 1.0

    event_multiplier = float(data.get("position_sizing_multiplier") or data.get("event_proximity_multiplier") or haircut_mult)
    recommended_pct = round(base_recommended_pct * event_multiplier, 1)

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

    evidence.append(f"Position Sizing: {recommended_pct}% (Base Cap: {base_recommended_pct}% | Risk Budget: {risk_budget_weight_pct}% | Liquidity Cap: {liquidity_cap_pct}%)")
    if adtv_cr <= 0.0:
        evidence.append("⚠️ Zero Observed Liquidity: ADTV is ₹0.00 Cr (untraded/halted); position allocation hard-floored to 0.0% to prevent capital lockup.")
    elif raw_liq_cap < 1.0:
        evidence.append(f"⚪ Micro-Cap Liquidity Constraint: ADTV of ₹{adtv_cr:.2f} Cr limits allocation to {liquidity_cap_pct}% of AUM.")
    if conf_unobserved:
        evidence.append("⚪ Evidence confidence unobserved: using conservative baseline 70.0% calibration for advisory Kelly calculation.")
    if event_multiplier < 1.0:
        evidence.append(f"Event Proximity Haircut Applied: {event_multiplier:.2f}x (Imminent binary catalyst risk; position reduced from {base_recommended_pct}% to {recommended_pct}%).")
    evidence.append(f"Fractional-Kelly (Quarter-Kelly): {fractional_kelly * 100.0:.1f}% | Win Prob: {win_prob * 100.0:.0f}%")
    evidence.append(f"Archetype Drawdown Tolerance: {drawdown_tolerance_band:.0f}% | Archetype: {archetype_upper}")

    signal = PortfolioPositionSizingSignal(
        recommended_position_pct=recommended_pct,
        fractional_kelly_weight=round(fractional_kelly, 4),
        liquidity_cap_pct=liquidity_cap_pct,
        correlation_group=f"{archetype_upper}_BASKET",
        scaling_ladder=scaling_ladder,
        exit_triggers=exit_triggers,
        drawdown_tolerance_band_pct=drawdown_tolerance_band,
        event_proximity_multiplier=event_multiplier,
        base_recommended_pct=base_recommended_pct
    )

    return {
        "symbol": norm_symbol,
        "executed_at": datetime.now().isoformat(),
        "recommended_position_pct": recommended_pct,
        "base_recommended_position_pct": base_recommended_pct,
        "event_proximity_multiplier": event_multiplier,
        "drawdown_tolerance_band_pct": drawdown_tolerance_band,
        "portfolio_signal": signal.model_dump(),
        "evidence": evidence,
        "meta": create_meta_header(source="Portfolio Position Sizing Engine (§35, §36, §37)")
    }
