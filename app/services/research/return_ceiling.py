"""Phase 152: Reverse-DCF Return Ceiling & Multibagger Label Guard.

Computes Bear/Base/Bull return multiples for a stock given current market cap,
TTM PAT, and growth scenarios. Flags stocks where base-case < 1.5x as
COMPOUNDER_ONLY (not eligible for 'multibagger' label in LLM responses).

Zero conflict: purely additive module. No existing engine modification.
Learned from: Cross-Audit finding that 7 of 10 stocks capped at 1.3-2.9x,
but were labeled 'multibagger' with targets like '60% to 3x'.
"""

from typing import Dict, Any, Optional


# Phase 180: Sector-Specific Baseline Terminal P/E multiples
SECTOR_TERMINAL_PE_MAP: Dict[str, Dict[str, float]] = {
    "FMCG": {"base": 35.0, "bull": 45.0, "bear": 25.0},
    "CONSUMER": {"base": 35.0, "bull": 45.0, "bear": 25.0},
    "CONSUMER DURABLES": {"base": 30.0, "bull": 40.0, "bear": 20.0},
    "TECHNOLOGY": {"base": 25.0, "bull": 32.0, "bear": 18.0},
    "IT SERVICES": {"base": 25.0, "bull": 32.0, "bear": 18.0},
    "HEALTHCARE": {"base": 25.0, "bull": 32.0, "bear": 18.0},
    "PHARMACEUTICALS": {"base": 25.0, "bull": 32.0, "bear": 18.0},
    "CAPITAL GOODS": {"base": 24.0, "bull": 30.0, "bear": 16.0},
    "DEFENCE": {"base": 25.0, "bull": 32.0, "bear": 16.0},
    "AUTOMOBILE": {"base": 18.0, "bull": 24.0, "bear": 12.0},
    "CHEMICALS": {"base": 22.0, "bull": 28.0, "bear": 15.0},
    "FINANCIAL SERVICES": {"base": 18.0, "bull": 22.0, "bear": 12.0},
    "METALS & MINING": {"base": 10.0, "bull": 14.0, "bear": 7.0},
    "ENERGY": {"base": 10.0, "bull": 14.0, "bear": 7.0},
    "UTILITIES": {"base": 12.0, "bull": 16.0, "bear": 8.0},
    "REAL ESTATE": {"base": 18.0, "bull": 24.0, "bear": 12.0},
    "GENERAL": {"base": 18.0, "bull": 25.0, "bear": 12.0},
}


def compute_return_ceiling(
    current_mcap_cr: float,
    ttm_pat_cr: float,
    growth_scenarios: Optional[Dict[str, Dict[str, float]]] = None,
    horizon_years: int = 3,
    sovereign_yield_pct: Optional[float] = None,
    dividend_yield_pct: Optional[float] = None,
    cfo_pat_ratio: Optional[float] = None,
    sector: Optional[str] = None,
) -> Dict[str, Any]:
    """Compute Bear / Base / Bull return multiples via reverse-DCF with sector awareness."""
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
            "sector": str(sector or "GENERAL").upper(),
        }

    # Macro yield gravity multiple compression
    norm_sector = str(sector or "GENERAL").upper().strip()
    pe_defaults = SECTOR_TERMINAL_PE_MAP.get(norm_sector)
    if not pe_defaults:
        for k, v in SECTOR_TERMINAL_PE_MAP.items():
            if k in norm_sector or norm_sector in k:
                pe_defaults = v
                break
    if not pe_defaults:
        pe_defaults = SECTOR_TERMINAL_PE_MAP["GENERAL"]

    base_terminal_pe = pe_defaults["base"]
    bull_terminal_pe = pe_defaults["bull"]
    bear_terminal_pe = pe_defaults["bear"]
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
        "sector": norm_sector,
        "dividend_trap_warning": is_dividend_trap,
        "sovereign_yield_pct": sovereign_yield_pct,
        "yield_compression_applied": yield_compressed,
        "base_rate_assessment": base_rate_eval,
        "base_rate_plausibility_grade": base_rate_eval.get("plausibility_grade", "MODERATE_PLAUSIBILITY"),
    }

