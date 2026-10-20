"""Institutional Model Portfolio Delta Rebalancing & Profit-Taking Engine.

Computes multi-dimensional capital rotation and delta rebalancing decisions
between screening intervals (e.g., Month T vs Month T-1), isolating:
  1. HOLD: Continuing high-conviction positions with valuation headroom intact.
  2. TAKE_PROFIT: Positions achieving target gains (>= 30-50%) where valuation
     ceiling or technical extension Z-score (+2.50 sigma) indicates saturation.
  3. NEW_ENTRY: Fresh coiled base candidates (Stage 1/2 VCP) entering the ranking.
  4. STOP_LOSS / VETO_EXIT: Positions breaching governance, leverage, or trend gates.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class RebalanceAction(str, Enum):
    HOLD = "HOLD"
    TAKE_PROFIT = "TAKE_PROFIT"
    NEW_ENTRY = "NEW_ENTRY"
    STOP_LOSS = "STOP_LOSS"
    TRIM = "TRIM"


class RebalanceDecision(BaseModel):
    symbol: str
    action: RebalanceAction
    previous_rank: Optional[int] = None
    current_rank: Optional[int] = None
    price_change_pct: float = 0.0
    extension_z: float = 0.0
    reverse_dcf_headroom_pct: float = 0.0
    rationale: str
    urgency: str = "NORMAL"  # IMMEDIATE, NORMAL, MONITOR


class PortfolioDeltaSummary(BaseModel):
    rebalanced_at: str
    total_previous_positions: int
    total_current_positions: int
    hold_count: int
    take_profit_count: int
    new_entry_count: int
    stop_loss_count: int
    turnover_rate_pct: float
    retention_rate_pct: float
    decisions: List[RebalanceDecision]


def compute_portfolio_delta_rebalance(
    previous_portfolio: List[Dict[str, Any]],
    current_portfolio: List[Dict[str, Any]],
    profit_take_gain_threshold: float = 30.0,
    max_extension_z: float = 2.50,
    min_reverse_dcf_headroom: float = 10.0,
    stop_loss_pct: float = -12.0
) -> Dict[str, Any]:
    """Computes deterministic delta rebalance actions comparing two portfolio snapshots."""
    prev_map = {item.get("symbol", "").upper().strip(): item for item in previous_portfolio if item.get("symbol")}
    curr_map = {item.get("symbol", "").upper().strip(): item for item in current_portfolio if item.get("symbol")}

    decisions: List[RebalanceDecision] = []
    
    # Process all stocks that were in the previous portfolio
    for sym, prev_data in prev_map.items():
        curr_data = curr_map.get(sym)
        prev_price = float(prev_data.get("price") or prev_data.get("current_price") or prev_data.get("entry_price") or 1.0)
        curr_price = float(curr_data.get("price") or curr_data.get("current_price") or prev_data.get("current_price") or prev_price) if curr_data else float(prev_data.get("current_price") or prev_price)
        
        # Calculate price change
        price_gain = ((curr_price - prev_price) / prev_price) * 100.0 if prev_price > 0 else 0.0
        reported_gain = float(curr_data.get("unrealized_return_pct") or prev_data.get("unrealized_return_pct") or price_gain) if curr_data else price_gain
        effective_gain = reported_gain if reported_gain != 0.0 else price_gain

        prev_rank = prev_data.get("rank")
        curr_rank = curr_data.get("rank") if curr_data else None

        # Check technical extension & valuation metrics
        src = curr_data if curr_data else prev_data
        extension_z = float(src.get("extension_z") or src.get("extension_zscore") or 0.0)
        dcf_headroom = float(src.get("reverse_dcf_headroom") or src.get("headroom_pct") or 50.0)
        rsi = float(src.get("rsi") or 50.0)
        is_vetoed = bool(src.get("is_vetoed") or src.get("fatal_veto") or src.get("vetoes"))

        # Rule 1: Fatal Veto or Severe Breakdown -> STOP_LOSS / VETO_EXIT
        if is_vetoed or effective_gain <= stop_loss_pct:
            reason = (
                f"Fatal risk veto triggered ({src.get('veto_reason') or 'Governance/Solvency breach'})"
                if is_vetoed else
                f"Stop-loss limit breached ({effective_gain:+.1f}% <= {stop_loss_pct:.1f}%); preserve capital."
            )
            decisions.append(RebalanceDecision(
                symbol=sym,
                action=RebalanceAction.STOP_LOSS,
                previous_rank=prev_rank,
                current_rank=curr_rank,
                price_change_pct=round(effective_gain, 2),
                extension_z=round(extension_z, 2),
                reverse_dcf_headroom_pct=round(dcf_headroom, 2),
                rationale=reason,
                urgency="IMMEDIATE"
            ))
            continue

        # Rule 2: Take Profit Conditions (Run-up achieved + Exhaustion signals OR dropped out due to valuation)
        take_profit_triggered = False
        reasons = []

        if effective_gain >= profit_take_gain_threshold:
            if extension_z >= max_extension_z:
                take_profit_triggered = True
                reasons.append(f"Climactic technical extension (Z-score {extension_z:+.2f} >= {max_extension_z:+.2f})")
            if dcf_headroom < min_reverse_dcf_headroom:
                take_profit_triggered = True
                reasons.append(f"Reverse-DCF headroom exhausted ({dcf_headroom:.1f}% < {min_reverse_dcf_headroom:.1f}%)")
            if rsi >= 78.0:
                take_profit_triggered = True
                reasons.append(f"RSI overbought exhaustion ({rsi:.1f} >= 78.0)")

        # Dropped completely out of current top ranking after >= 25% run
        if not curr_data and effective_gain >= 25.0:
            take_profit_triggered = True
            reasons.append(f"Dropped out of current top ranking with solid gain ({effective_gain:+.1f}%); rotate into fresh base.")

        if take_profit_triggered:
            decisions.append(RebalanceDecision(
                symbol=sym,
                action=RebalanceAction.TAKE_PROFIT,
                previous_rank=prev_rank,
                current_rank=curr_rank,
                price_change_pct=round(effective_gain, 2),
                extension_z=round(extension_z, 2),
                reverse_dcf_headroom_pct=round(dcf_headroom, 2),
                rationale=f"Lock in profits ({effective_gain:+.1f}% gain): " + "; ".join(reasons),
                urgency="NORMAL"
            ))
            continue

        # Rule 3: Still in current portfolio with safe headroom -> HOLD
        if curr_data:
            decisions.append(RebalanceDecision(
                symbol=sym,
                action=RebalanceAction.HOLD,
                previous_rank=prev_rank,
                current_rank=curr_rank,
                price_change_pct=round(effective_gain, 2),
                extension_z=round(extension_z, 2),
                reverse_dcf_headroom_pct=round(dcf_headroom, 2),
                rationale=f"Thesis intact; position ranked #{curr_rank} with {dcf_headroom:.1f}% valuation runway remaining.",
                urgency="MONITOR"
            ))
        else:
            # Dropped out without big gain -> TRIM / ROTATE OUT
            decisions.append(RebalanceDecision(
                symbol=sym,
                action=RebalanceAction.TRIM,
                previous_rank=prev_rank,
                current_rank=None,
                price_change_pct=round(effective_gain, 2),
                extension_z=round(extension_z, 2),
                reverse_dcf_headroom_pct=round(dcf_headroom, 2),
                rationale=f"Relative rank displaced by higher-scoring candidates ({effective_gain:+.1f}% return); rotate capital.",
                urgency="NORMAL"
            ))

    # Process all stocks that are new in the current portfolio
    for sym, curr_data in curr_map.items():
        if sym not in prev_map:
            curr_rank = curr_data.get("rank")
            extension_z = float(curr_data.get("extension_z") or curr_data.get("extension_zscore") or 0.0)
            dcf_headroom = float(curr_data.get("reverse_dcf_headroom") or curr_data.get("headroom_pct") or 50.0)
            decisions.append(RebalanceDecision(
                symbol=sym,
                action=RebalanceAction.NEW_ENTRY,
                previous_rank=None,
                current_rank=curr_rank,
                price_change_pct=0.0,
                extension_z=round(extension_z, 2),
                reverse_dcf_headroom_pct=round(dcf_headroom, 2),
                rationale=f"Fresh entry at rank #{curr_rank}; Stage 1/2 base coiling with {dcf_headroom:.1f}% valuation headroom.",
                urgency="NORMAL"
            ))

    # Calculate summary metrics
    n_prev = len(prev_map)
    n_curr = len(curr_map)
    hold_count = sum(1 for d in decisions if d.action == RebalanceAction.HOLD)
    tp_count = sum(1 for d in decisions if d.action == RebalanceAction.TAKE_PROFIT)
    new_count = sum(1 for d in decisions if d.action == RebalanceAction.NEW_ENTRY)
    sl_count = sum(1 for d in decisions if d.action == RebalanceAction.STOP_LOSS)
    
    turnover = (new_count / max(1, n_curr)) * 100.0
    retention = (hold_count / max(1, n_prev)) * 100.0

    summary = PortfolioDeltaSummary(
        rebalanced_at=datetime.now(timezone.utc).isoformat(),
        total_previous_positions=n_prev,
        total_current_positions=n_curr,
        hold_count=hold_count,
        take_profit_count=tp_count,
        new_entry_count=new_count,
        stop_loss_count=sl_count,
        turnover_rate_pct=round(turnover, 2),
        retention_rate_pct=round(retention, 2),
        decisions=decisions
    )

    return summary.model_dump()
