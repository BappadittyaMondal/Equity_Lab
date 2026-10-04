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
) -> Dict[str, Any]:
    """Compute Bear / Base / Bull return multiples via reverse-DCF.

    Args:
        current_mcap_cr: Current market cap in ₹ Crore.
        ttm_pat_cr: Trailing twelve-month PAT in ₹ Crore.
        growth_scenarios: Optional custom scenarios. If None, uses defaults:
            Bear:  8% PAT CAGR, 12x terminal P/E
            Base: 18% PAT CAGR, 18x terminal P/E
            Bull: 30% PAT CAGR, 25x terminal P/E
        horizon_years: Investment horizon in years (default 3).

    Returns:
        Dict with bear/base/bull multiples and multibagger_eligible flag.
    """
    if current_mcap_cr <= 0 or ttm_pat_cr <= 0:
        return {
            "bear_multiple": 0.0,
            "base_multiple": 0.0,
            "bull_multiple": 0.0,
            "multibagger_eligible": False,
            "label": "INSUFFICIENT_DATA",
            "horizon_years": horizon_years,
        }

    if growth_scenarios is None:
        growth_scenarios = {
            "bear": {"pat_cagr_pct": 8.0, "terminal_pe": 12.0},
            "base": {"pat_cagr_pct": 18.0, "terminal_pe": 18.0},
            "bull": {"pat_cagr_pct": 30.0, "terminal_pe": 25.0},
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

    return {
        **results,
        "multibagger_eligible": eligible,
        "label": label,
        "horizon_years": horizon_years,
        "current_mcap_cr": current_mcap_cr,
        "ttm_pat_cr": ttm_pat_cr,
    }
