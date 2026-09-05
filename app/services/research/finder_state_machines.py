"""
Institutional Lifecycle State Machines for the Five Core Investment Pillars:
1. Multibagger Finder (Lifecycle Progression & Float Absorption)
2. Turnaround Finder (Relapse-First Dominance & Disaster AVWAP)
3. Swing Trade Finder (Execution Feasibility & Liquidity Capacity)
4. Microcap Finder (Risk-First Discovery & Forensic Shield)
5. SIP / Compounder Finder (Valuation-Responsive Dynamic Allocation)

Strict Zero-Compromise Invariants:
- Deterministic, immutable state transitions.
- Hard fail-closed logic when forensic, regulatory, or liquidity criteria fail.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone


# ==============================================================================
# 1. MULTIBAGGER LIFECYCLE STATE MACHINE
# ==============================================================================

class MultibaggerState(str, Enum):
    UNPROVEN = "UNPROVEN"
    BUILDING = "BUILDING"
    INFLECTING = "INFLECTING"
    BREAKOUT = "BREAKOUT"
    COMPOUNDING = "COMPOUNDING"
    EXHAUSTION = "EXHAUSTION"
    INVALIDATED = "INVALIDATED"


class MultibaggerStateMachine:
    """Tracks secular multibagger progression and enforces structural kill-triggers."""

    @classmethod
    def evaluate(
        cls,
        symbol: str,
        pat_growth_ttm: float,
        pat_growth_prev: float,
        incremental_roic: float,
        wacc: float = 12.0,
        cfo_to_ebitda: float = 0.80,
        promoter_pledge_pct: float = 0.0,
        is_breakout_cleared: bool = False,
        consecutive_high_roce_quarters: int = 0,
        valuation_z_score: float = 0.0,
    ) -> Dict[str, Any]:
        """Evaluates Multibagger lifecycle state with hard thesis kill triggers."""
        kill_triggers: List[str] = []

        # 1. Kill Triggers (Immediate transition to INVALIDATED)
        if cfo_to_ebitda < 0.40:
            kill_triggers.append(f"CFO to EBITDA collapse ({cfo_to_ebitda:.2f} < 0.40)")
        if incremental_roic < (wacc - 2.0):
            kill_triggers.append(f"Incremental ROIC below WACC ({incremental_roic:.1f}% < {wacc:.1f}%)")
        if promoter_pledge_pct > 25.0:
            kill_triggers.append(f"Excessive promoter pledge ({promoter_pledge_pct:.1f}% > 25.0%)")

        if kill_triggers:
            return {
                "symbol": symbol.upper(),
                "state": MultibaggerState.INVALIDATED.value,
                "is_investable": False,
                "kill_triggers_fired": kill_triggers,
                "conviction": "THESIS_BREACH_HALT",
                "reinvestment_spread": round(incremental_roic - wacc, 2),
            }

        # 2. Sequential Acceleration: Δ^2(PAT) > 0
        acceleration = pat_growth_ttm - pat_growth_prev

        # 3. State Progression
        if valuation_z_score > 2.5:
            state = MultibaggerState.EXHAUSTION
        elif consecutive_high_roce_quarters >= 6 and pat_growth_ttm >= 20.0:
            state = MultibaggerState.COMPOUNDING
        elif is_breakout_cleared and acceleration > 0 and incremental_roic > wacc:
            state = MultibaggerState.BREAKOUT
        elif acceleration > 5.0 and incremental_roic > wacc:
            state = MultibaggerState.INFLECTING
        elif incremental_roic > wacc and pat_growth_ttm > 10.0:
            state = MultibaggerState.BUILDING
        else:
            state = MultibaggerState.UNPROVEN

        return {
            "symbol": symbol.upper(),
            "state": state.value,
            "is_investable": state in (MultibaggerState.BUILDING, MultibaggerState.INFLECTING, MultibaggerState.BREAKOUT, MultibaggerState.COMPOUNDING),
            "acceleration_delta_pct": round(acceleration, 2),
            "reinvestment_spread": round(incremental_roic - wacc, 2),
            "kill_triggers_fired": [],
            "conviction": "HIGH_GROWTH_CONVEXITY" if state in (MultibaggerState.INFLECTING, MultibaggerState.BREAKOUT, MultibaggerState.COMPOUNDING) else "MONITOR_STAGE",
        }


# ==============================================================================
# 2. TURNAROUND LIFECYCLE STATE MACHINE (RELAPSE-FIRST)
# ==============================================================================

class TurnaroundState(str, Enum):
    DISTRESS = "DISTRESS"
    STABILIZATION = "STABILIZATION"
    EARLY_RECOVERY = "EARLY_RECOVERY"
    CASH_FLOW_CONFIRMED = "CASH_FLOW_CONFIRMED"
    SUSTAINED_RECOVERY = "SUSTAINED_RECOVERY"
    RELAPSE = "RELAPSE"


class TurnaroundStateMachine:
    """Tracks turnaround progression with dominant RELAPSE override and Disaster AVWAP."""

    @classmethod
    def evaluate(
        cls,
        symbol: str,
        current_price: float,
        disaster_avwap: float,
        piotroski_score: int,
        piotroski_prev: int,
        cfo_cr: float,
        ebitda_cr: float,
        debt_reduction_initiated: bool,
        is_relapse_signal: bool = False,
    ) -> Dict[str, Any]:
        """Evaluates Turnaround lifecycle state."""
        # Hard Rule: If price breaks below Disaster AVWAP floor or relapse fired -> RELAPSE
        price_below_disaster_floor = (disaster_avwap > 0) and (current_price < (disaster_avwap * 0.97))
        if is_relapse_signal or price_below_disaster_floor or (piotroski_score <= 2 and cfo_cr < 0):
            floor_pct = round(((current_price - disaster_avwap) / disaster_avwap) * 100.0, 2) if disaster_avwap and disaster_avwap > 0 else None
            return {
                "symbol": symbol.upper(),
                "state": TurnaroundState.RELAPSE.value,
                "is_turnaround_confirmed": False,
                "dominant_override": "RELAPSE_VETO_ACTIVE",
                "price_to_disaster_floor_pct": floor_pct,
                "action": "AVOID_VALUE_TRAP_OR_EXIT",
            }

        f_score_delta = piotroski_score - piotroski_prev
        above_floor = (current_price >= disaster_avwap) if disaster_avwap and disaster_avwap > 0 else True

        if piotroski_score >= 7 and cfo_cr > 0 and ebitda_cr > 0 and (cfo_cr >= 0.7 * ebitda_cr) and above_floor:
            state = TurnaroundState.SUSTAINED_RECOVERY
        elif cfo_cr > 0 and above_floor:
            state = TurnaroundState.CASH_FLOW_CONFIRMED
        elif f_score_delta >= 2 and above_floor:
            state = TurnaroundState.EARLY_RECOVERY
        elif debt_reduction_initiated or f_score_delta >= 1:
            state = TurnaroundState.STABILIZATION
        else:
            state = TurnaroundState.DISTRESS

        floor_pct = round(((current_price - disaster_avwap) / disaster_avwap) * 100.0, 2) if disaster_avwap and disaster_avwap > 0 else None
        return {
            "symbol": symbol.upper(),
            "state": state.value,
            "is_turnaround_confirmed": state in (TurnaroundState.EARLY_RECOVERY, TurnaroundState.CASH_FLOW_CONFIRMED, TurnaroundState.SUSTAINED_RECOVERY),
            "price_to_disaster_floor_pct": floor_pct,
            "piotroski_delta": f_score_delta,
            "action": "ALLOCATE_TURNAROUND" if state in (TurnaroundState.CASH_FLOW_CONFIRMED, TurnaroundState.SUSTAINED_RECOVERY) else "MONITOR_STABILIZATION",
        }


# ==============================================================================
# 3. SWING TRADE FEASIBILITY & EXECUTION LAYER
# ==============================================================================

class SwingTradeFeasibilityEngine:
    """Verifies technical setup validity against market liquidity and execution feasibility."""

    @classmethod
    def evaluate(
        cls,
        symbol: str,
        technical_confluence_score: float,
        mtf_verdict: str,
        adtv_cr: float,
        order_size_cr: Optional[float] = None,
        is_circuit_locked: bool = False,
    ) -> Dict[str, Any]:
        """Evaluates swing trade execution feasibility without silent capacity assumptions."""
        # 1. Circuit Lockout Check
        if is_circuit_locked:
            return {
                "symbol": symbol.upper(),
                "feasibility_status": "CIRCUIT_LOCKED_TRADING_HALTED",
                "is_tradable": False,
                "reason": "Stock locked in price circuit filter; 0 execution depth.",
            }

        # 2. Macro Trend Veto
        if "VETOED" in mtf_verdict or "BEARISH" in mtf_verdict:
            return {
                "symbol": symbol.upper(),
                "feasibility_status": "VETOED_AGAINST_WEEKLY_TIDE",
                "is_tradable": False,
                "reason": f"MTF Macro Tide conflict: {mtf_verdict}",
            }

        # 3. Liquidity Capacity Floor
        max_order_allowed = round(0.05 * adtv_cr, 3)  # Max 5% ADV participation
        if adtv_cr < 5.0:
            return {
                "symbol": symbol.upper(),
                "feasibility_status": "HIGH_SCORE_NOT_TRADABLE",
                "is_tradable": False,
                "reason": f"ADTV ₹{adtv_cr:.2f}Cr below institutional ₹5.0Cr floor.",
            }

        if order_size_cr is None:
            # Capacity unverified: Do not assume a favorable token order size
            return {
                "symbol": symbol.upper(),
                "feasibility_status": "CAPACITY_UNVERIFIED_DATA_INSUFFICIENT",
                "is_tradable": False,
                "reason": "order_size_cr not provided; capacity cannot be verified against 5% ADV limit.",
            }

        if order_size_cr > max_order_allowed:
            return {
                "symbol": symbol.upper(),
                "feasibility_status": "HIGH_SCORE_NOT_TRADABLE",
                "is_tradable": False,
                "reason": f"Order size ₹{order_size_cr:.2f}Cr exceeds 5% ADV capacity limit of ₹{max_order_allowed:.2f}Cr.",
            }

        # 4. Final Feasibility Check
        is_ready = technical_confluence_score >= 65.0
        return {
            "symbol": symbol.upper(),
            "feasibility_status": "FEASIBLE_READY_FOR_ENTRY" if is_ready else "SETUP_INCOMPLETE",
            "is_tradable": is_ready,
            "adtv_cr": round(adtv_cr, 2),
            "max_position_size_cr": round(max_order_allowed, 2),
            "reason": "Technical confluence and execution liquidity fully verified.",
        }


# ==============================================================================
# 4. MICROCAP RISK-FIRST DISCOVERY MACHINE
# ==============================================================================

class MicrocapRiskFirstGate:
    """Risk-first microcap incubator enforcing capacity limits and forensic shields."""

    @classmethod
    def evaluate(
        cls,
        symbol: str,
        market_cap_cr: Optional[float] = None,
        adtv_30d_cr: Optional[float] = None,
        rpt_to_net_worth_pct: Optional[float] = 0.0,
        has_auditor_resigned_recently: bool = False,
        circuit_frequency_pct: float = 0.0,
        promoter_holding_pct: float = 0.0,
        cfo_3y_sum_cr: float = 0.0,
    ) -> Dict[str, Any]:
        """Evaluates microcap eligibility with strict forensic vetoes."""
        if market_cap_cr is None:
            return {
                "symbol": symbol.upper(),
                "is_investable": False,
                "status": "CAPACITY_UNVERIFIED_DATA_INSUFFICIENT",
                "forensic_vetoes": ["Market capitalization missing or unverified."],
                "allowed_market_impact_order_cr": 0.0,
            }

        if adtv_30d_cr is None:
            return {
                "symbol": symbol.upper(),
                "is_investable": False,
                "status": "CAPACITY_UNVERIFIED_DATA_INSUFFICIENT",
                "forensic_vetoes": ["ADTV (30-day average daily traded volume) missing or unverified."],
                "allowed_market_impact_order_cr": 0.0,
            }

        forensic_vetoes: List[str] = []

        # 1. Forensic Red-Flags
        if has_auditor_resigned_recently:
            forensic_vetoes.append("Statutory auditor mid-term resignation detected.")
        if rpt_to_net_worth_pct is None:
            forensic_vetoes.append("Related-party transaction ratio missing or unverified (Fail-closed forensic shield).")
        elif rpt_to_net_worth_pct > 5.0:
            forensic_vetoes.append(f"Excessive Related-Party Transactions ({rpt_to_net_worth_pct:.1f}% > 5.0%).")
        if circuit_frequency_pct > 15.0:
            forensic_vetoes.append(f"Manipulated order book: circuit frequency ({circuit_frequency_pct:.1f}% > 15.0%).")
        if promoter_holding_pct < 35.0:
            forensic_vetoes.append(f"Low promoter alignment ({promoter_holding_pct:.1f}% < 35.0%).")
        if cfo_3y_sum_cr <= 0:
            forensic_vetoes.append("Cumulative 3-year Cash from Operations is negative.")

        if forensic_vetoes:
            return {
                "symbol": symbol.upper(),
                "is_investable": False,
                "status": "FORENSIC_OR_LIQUIDITY_VETO",
                "forensic_vetoes": forensic_vetoes,
                "allowed_market_impact_order_cr": 0.0,
            }

        # 2. Three Distinct Capacity Limits
        market_impact_limit_cr = round(0.03 * adtv_30d_cr, 3)  # Max 3% ADTV
        strategy_position_limit_cr = round(min(1.50, 0.025 * market_cap_cr), 2)  # Max 2.5% mcap or ₹1.5Cr
        portfolio_risk_budget_pct = 15.0  # Max 15% total portfolio allocation to microcaps

        return {
            "symbol": symbol.upper(),
            "is_investable": True,
            "status": "APPROVED_MICROCAP_CANDIDATE",
            "capacity_limits": {
                "market_impact_limit_cr": market_impact_limit_cr,
                "strategy_position_limit_cr": strategy_position_limit_cr,
                "portfolio_risk_budget_pct": portfolio_risk_budget_pct,
            },
            "forensic_vetoes": [],
            "risk_tier": "INCUBATOR_MICROCAP_WATCH",
        }


# ==============================================================================
# 5. SIP / COMPOUNDER POLICY ENGINE
# ==============================================================================

class SIPPolicyEngine:
    """Valuation-responsive dynamic allocation policy engine for secular compounders."""

    @classmethod
    def evaluate(
        cls,
        symbol: str,
        roce_10y_avg: float,
        debt_to_equity: float,
        valuation_z_score: float,
        thesis_intact: bool,
        is_price_below_200sma: bool,
    ) -> Dict[str, Any]:
        """Evaluates SIP contribution allocation multiplier and thesis preservation."""
        # Hard Invalidation: If thesis broken or ROCE decaying below 15% -> PAUSE
        if not thesis_intact or roce_10y_avg < 15.0 or debt_to_equity > 1.0:
            return {
                "symbol": symbol.upper(),
                "policy_action": "PAUSE_SIP_OR_EXIT_REVIEW",
                "allocation_multiplier": 0.0,
                "reason": "Secular moat decay: ROCE < 15%, excessive debt, or thesis invalidation.",
                "accumulate_dry_powder": False,
            }

        # Valuation-Responsive Allocation Multiplier
        if valuation_z_score > 1.5:
            multiplier = 0.50
            action = "REDUCED_SIP_ACCUMULATE_DRY_POWDER"
            desc = "Valuation extended (> +1.5σ); deploy half capital and preserve cash buffer."
        elif -0.5 <= valuation_z_score <= 0.5:
            multiplier = 1.00
            action = "STANDARD_SIP_EXECUTION"
            desc = "Fair valuation; execute standard monthly tranche."
        elif valuation_z_score < -1.5 and is_price_below_200sma:
            multiplier = 1.75
            action = "EXPANDED_SIP_DEPLOY_BUFFER"
            desc = "Severe valuation discount (< -1.5σ) at long-term support with intact ROCE; deploy dry powder."
        elif valuation_z_score < -0.5:
            multiplier = 1.25
            action = "MILD_EXPANDED_SIP"
            desc = "Moderate valuation discount; scale allocation to 1.25x."
        else:
            multiplier = 0.75
            action = "MODERATE_SIP"
            desc = "Mild premium; scale allocation to 0.75x."

        return {
            "symbol": symbol.upper(),
            "policy_action": action,
            "allocation_multiplier": multiplier,
            "description": desc,
            "roce_10y_avg": round(roce_10y_avg, 2),
            "valuation_z_score": round(valuation_z_score, 2),
        }
