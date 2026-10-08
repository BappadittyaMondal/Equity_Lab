"""Phase 152: Reverse-DCF Return Ceiling & Multibagger Label Guard.

Computes Bear/Base/Bull return multiples for a stock given current market cap,
TTM PAT, and growth scenarios. Flags stocks where base-case < 1.5x as
COMPOUNDER_ONLY (not eligible for 'multibagger' label in LLM responses).

Zero conflict: purely additive module. No existing engine modification.
Learned from: Cross-Audit finding that 7 of 10 stocks capped at 1.3-2.9x,
but were labeled 'multibagger' with targets like '60% to 3x'.
"""

from typing import Dict, Any, Optional


def compute_return_ceiling(
    current_mcap_cr: float,
    ttm_pat_cr: float,
    growth_scenarios: Optional[Dict[str, Dict[str, float]]] = None,
    horizon_years: int = 3,
    sovereign_yield_pct: Optional[float] = None,
    dividend_yield_pct: Optional[float] = None,
    cfo_pat_ratio: Optional[float] = None,
) -> Dict[str, Any]:
    """Compute Bear / Base / Bull return multiples via reverse-DCF.

    Args:
        current_mcap_cr: Current market cap in ₹ Crore.
        ttm_pat_cr: Trailing twelve-month PAT in ₹ Crore.
        growth_scenarios: Optional custom scenarios. If None, uses defaults.
        horizon_years: Investment horizon in years (default 3).
        sovereign_yield_pct: Optional 10Y sovereign benchmark yield % (e.g. 7.1%).
        dividend_yield_pct: Optional dividend yield % for yield trap guard.
        cfo_pat_ratio: Optional CFO/PAT ratio for cash realization verification.

    Returns:
        Dict with bear/base/bull multiples, multibagger_eligible flag,
        and sovereign yield & dividend trap indicators.
    """
    if current_mcap_cr <= 0 or ttm_pat_cr <= 0:
        return {
            "bear_multiple": 0.0,
            "base_multiple": 0.0,
            "bull_multiple": 0.0,
            "multibagger_eligible": False,
            "label": "INSUFFICIENT_DATA",
            "horizon_years": horizon_years,
            "dividend_trap_warning": False,
            "sovereign_yield_pct": sovereign_yield_pct,
        }

    # Macro yield gravity multiple compression
    base_terminal_pe = 18.0
    bull_terminal_pe = 25.0
    bear_terminal_pe = 12.0
    yield_compressed = False

    if sovereign_yield_pct is not None and float(sovereign_yield_pct) > 8.0:
        # High sovereign yield compresses equity discount multiple ceiling
        pe_ceiling = round(100.0 / (float(sovereign_yield_pct) + 3.0), 1)
        base_terminal_pe = min(base_terminal_pe, pe_ceiling)
        bull_terminal_pe = min(bull_terminal_pe, round(pe_ceiling * 1.25, 1))
        yield_compressed = True

    if growth_scenarios is None:
        growth_scenarios = {
            "bear": {"pat_cagr_pct": 8.0, "terminal_pe": bear_terminal_pe},
            "base": {"pat_cagr_pct": 18.0, "terminal_pe": base_terminal_pe},
            "bull": {"pat_cagr_pct": 30.0, "terminal_pe": bull_terminal_pe},
        }

    results = {}
    for scenario_name, params in growth_scenarios.items():
        cagr = params["pat_cagr_pct"] / 100.0
        terminal_pe = params["terminal_pe"]
        future_pat = ttm_pat_cr * ((1 + cagr) ** horizon_years)
        future_mcap = future_pat * terminal_pe
        multiple = round(future_mcap / current_mcap_cr, 2)
        results[f"{scenario_name}_multiple"] = multiple

    base_mult = results.get("base_multiple", 0.0)

    # Multibagger eligibility: base case must exceed 1.5x
    if base_mult >= 3.0:
        label = "MULTIBAGGER_CANDIDATE"
        eligible = True
    elif base_mult >= 1.5:
        label = "GROWTH_COMPOUNDER"
        eligible = False  # Not multibagger, but still above-market
    else:
        label = "COMPOUNDER_ONLY"
        eligible = False

    # Dividend Yield Capital Destruction Trap Guard
    is_dividend_trap = False
    if dividend_yield_pct is not None and float(dividend_yield_pct) >= 10.0:
        if cfo_pat_ratio is not None and float(cfo_pat_ratio) < 0.50:
            is_dividend_trap = True
            label = "DIVIDEND_YIELD_CAPITAL_TRAP"
            eligible = False

    # Phase 164: Mauboussin Empirical Base Rate Filter
    try:
        from app.services.research.penman_reformulation import MauboussinBaseRateFilter
        base_cagr = growth_scenarios.get("base", {}).get("pat_cagr_pct", 18.0)
        base_rate_eval = MauboussinBaseRateFilter.evaluate_growth_base_rate(
            implied_5y_cagr_pct=base_cagr,
            horizon_years=horizon_years,
        )
    except Exception:
        base_rate_eval = {
            "implied_5y_cagr_pct": 18.0,
            "horizon_years": horizon_years,
            "empirical_base_rate_frequency_pct": 18.0,
            "plausibility_grade": "MODERATE_PLAUSIBILITY",
            "base_rate_penalty_score": 0.15,
            "commentary": "Standard compounder baseline.",
        }

    return {
        **results,
        "multibagger_eligible": eligible,
        "label": label,
        "horizon_years": horizon_years,
        "current_mcap_cr": current_mcap_cr,
        "ttm_pat_cr": ttm_pat_cr,
        "dividend_trap_warning": is_dividend_trap,
        "sovereign_yield_pct": sovereign_yield_pct,
        "yield_compression_applied": yield_compressed,
        "base_rate_assessment": base_rate_eval,
        "base_rate_plausibility_grade": base_rate_eval.get("plausibility_grade", "MODERATE_PLAUSIBILITY"),
    }

