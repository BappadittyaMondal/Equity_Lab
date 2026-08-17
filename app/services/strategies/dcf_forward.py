"""Forward DCF Engine — Phase 2, Layer 5 (Valuation Engine).

Implements 3-stage Forward DCF using real FCF/earnings data from ResearchDataStore.
Adds relative valuation (P/E vs sector/own-history), PEG ratio, scenario analysis,
and margin of safety calculation.

This complements the existing Reverse DCF (C9) which works backwards from price.
Forward DCF works forward from fundamentals → intrinsic value.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.models.schemas import StrategyRunResponse
from app.services.market_data import get_quote, create_meta_header, normalize_symbol, get_ist_now_str
from app.services.research_data import ResearchDataStore
from app.services.strategies.fundamental_metrics import (
    _extract_series, _cagr, _pct_change
)


# ─────────────────────────────────────────────────────────────────────────────
# Sector median reference values (Indian equity — approximate medians)
# Updated periodically. Source: NSE indices sector data.
# ─────────────────────────────────────────────────────────────────────────────
SECTOR_MEDIANS: Dict[str, Dict[str, float]] = {
    "Technology": {"pe": 28.0, "pb": 7.0, "roe": 22.0},
    "Financials": {"pe": 16.0, "pb": 2.5, "roe": 14.0},
    "Consumer": {"pe": 50.0, "pb": 12.0, "roe": 24.0},
    "Healthcare": {"pe": 32.0, "pb": 5.0, "roe": 15.0},
    "Automobile": {"pe": 20.0, "pb": 3.5, "roe": 16.0},
    "Energy": {"pe": 12.0, "pb": 2.0, "roe": 12.0},
    "Materials": {"pe": 14.0, "pb": 2.0, "roe": 12.0},
    "Infrastructure": {"pe": 30.0, "pb": 4.0, "roe": 12.0},
    "Telecom": {"pe": 35.0, "pb": 6.0, "roe": 10.0},
    "Real Estate": {"pe": 25.0, "pb": 3.0, "roe": 10.0},
}
NIFTY_50_MEDIANS: Dict[str, float] = {"pe": 22.0, "pb": 3.5, "roe": 14.0}


def _safe_float(val: Any, default: float = 0.0) -> float:
    if val is None:
        return default
    try:
        return float(val)
    except Exception:
        return default


def run_dcf_forward(
    symbol: str,
    store: Optional[ResearchDataStore] = None,
    discount_rate: float = 0.12,
    terminal_growth: float = 0.04,
) -> StrategyRunResponse:
    """Execute Forward DCF + Relative Valuation for a symbol.

    Returns:
        StrategyRunResponse with intrinsic value, margin of safety,
        scenario analysis, valuation zone, and PEG ratio.
    """
    norm = normalize_symbol(symbol)
    data_store = store or ResearchDataStore()
    evidence = []
    results: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}

    # ── 1. Get live price and P/E ──────────────────────────────────────────
    quote = get_quote(norm)
    price = _safe_float(quote.get("price") if isinstance(quote, dict) else getattr(quote, "price", None), 0.0)
    pe = _safe_float(quote.get("pe_ratio") if isinstance(quote, dict) else getattr(quote, "pe_ratio", None), 0.0)
    market_cap = _safe_float(quote.get("market_cap") if isinstance(quote, dict) else getattr(quote, "market_cap", None), 0.0)

    if price <= 0:
        return _insufficient_response(norm, "No valid price data from market data provider")

    # ── 2. Get financial history from ResearchDataStore ────────────────────
    try:
        _, financials, _, _, _, _ = data_store.get_timeline(norm)
    except Exception as e:
        return _insufficient_response(norm, f"ResearchDataStore unavailable: {e}")

    if not financials:
        return _insufficient_response(norm, "No financial observations in database — run seed_watchlist first")

    # ── 3. Extract FCF and earnings series ────────────────────────────────
    fcf_series = _extract_series(financials, ["free_cash_flow", "fcf", "operating_cash_flow"])
    pat_series = _extract_series(financials, ["net_income", "pat"])
    rev_series = _extract_series(financials, ["revenue", "total_revenue"])
    eps_series = _extract_series(financials, ["basic_eps", "diluted_eps"])

    # ── 4. Compute FCF growth CAGR for projection ─────────────────────────
    fcf_base = None
    growth_rate_annual = 0.10  # default 10% if insufficient data
    intrinsic_value_dcf = None

    if len(fcf_series) >= 4:
        fcf_4q = sum(v for _, v in fcf_series[-4:])  # TTM FCF (4-quarter sum)
        fcf_base = fcf_4q

        cagr_8q = _cagr(fcf_series, 8) if len(fcf_series) >= 9 else None
        if cagr_8q is not None and 0 < cagr_8q < 80.0:
            growth_rate_annual = cagr_8q / 100.0
            evidence.append(f"FCF 2Y CAGR used as projection base: {cagr_8q:.1f}%")
        else:
            growth_rate_annual = 0.10
            evidence.append("FCF CAGR unavailable — using conservative 10% growth assumption")

        # ── 5. 3-Stage Forward DCF ─────────────────────────────────────────
        # Stage 1: Years 1–3 at estimated growth
        # Stage 2: Years 4–7 at half the growth (fade)
        # Stage 3: Terminal value at terminal_growth forever
        pv_sum = 0.0
        g1 = min(growth_rate_annual, 0.40)  # cap at 40%
        g2 = g1 * 0.5

        for yr in range(1, 4):
            fcf_yr = fcf_base * ((1 + g1) ** yr)
            pv_sum += fcf_yr / ((1 + discount_rate) ** yr)

        fcf_after_3 = fcf_base * ((1 + g1) ** 3)
        for yr in range(1, 5):
            fcf_yr = fcf_after_3 * ((1 + g2) ** yr)
            pv_sum += fcf_yr / ((1 + discount_rate) ** (3 + yr))

        # Terminal value
        fcf_terminal = fcf_after_3 * ((1 + g2) ** 4) * (1 + terminal_growth)
        tv = fcf_terminal / (discount_rate - terminal_growth)
        pv_terminal = tv / ((1 + discount_rate) ** 7)
        enterprise_value = pv_sum + pv_terminal

        # Approximate equity value (no net-debt adjustment — use market cap ratio)
        if market_cap > 0 and price > 0 and enterprise_value > 0:
            intrinsic_value_dcf = round((enterprise_value / market_cap) * price, 2)
            evidence.append(
                f"3-Stage DCF intrinsic value: ₹{intrinsic_value_dcf} "
                f"(discount={int(discount_rate*100)}%, g1={g1*100:.0f}%, terminal={terminal_growth*100:.0f}%)"
            )
    else:
        evidence.append(f"Insufficient FCF history ({len(fcf_series)} qtrs) for DCF — need ≥4 quarters")

    # ── 6. Margin of Safety ───────────────────────────────────────────────
    margin_of_safety_pct = None
    if intrinsic_value_dcf and intrinsic_value_dcf > 0:
        margin_of_safety_pct = round(((intrinsic_value_dcf - price) / intrinsic_value_dcf) * 100, 2)
        if margin_of_safety_pct > 20:
            evidence.append(f"MARGIN OF SAFETY: {margin_of_safety_pct:.1f}% — significant discount to intrinsic value")
        elif margin_of_safety_pct > 0:
            evidence.append(f"Margin of safety: {margin_of_safety_pct:.1f}% (modest)")
        else:
            evidence.append(f"Stock trading at PREMIUM to DCF value: {margin_of_safety_pct:.1f}% margin of safety")

    # ── 7. EPS CAGR for PEG ratio ─────────────────────────────────────────
    peg_ratio = None
    eps_cagr = None
    if len(eps_series) >= 8:
        eps_cagr = _cagr(eps_series, 8)  # 2Y annualised EPS CAGR
    elif pat_series and len(pat_series) >= 8:
        eps_cagr = _cagr(pat_series, 8)

    if eps_cagr and eps_cagr > 0 and pe > 0:
        peg_ratio = round(pe / eps_cagr, 2)
        evidence.append(f"PEG Ratio: {peg_ratio:.2f} (P/E={pe:.1f} ÷ EPS CAGR={eps_cagr:.1f}%)")
        if peg_ratio < 1.0:
            evidence.append("PEG < 1.0: Stock may be undervalued relative to growth")
        elif peg_ratio > 2.0:
            evidence.append("PEG > 2.0: Growth expectations appear expensive")

    # ── 8. Valuation Zone (relative) ──────────────────────────────────────
    valuation_zone = _compute_valuation_zone(pe, peg_ratio, margin_of_safety_pct)

    # ── 9. Scenario Analysis ──────────────────────────────────────────────
    scenarios = _compute_scenarios(fcf_base, market_cap, price, discount_rate, terminal_growth)

    # ── 10. Sensitivity table ─────────────────────────────────────────────
    sensitivity = {}
    if fcf_base and market_cap > 0:
        for dr in [0.10, 0.12, 0.15]:
            for g in [0.03, 0.04, 0.05]:
                key = f"dr{int(dr*100)}_g{int(g*100)}"
                sensitivity[key] = _quick_dcf(fcf_base, market_cap, price, growth_rate_annual, dr, g)

    # ── Compile results ────────────────────────────────────────────────────
    passed = (
        margin_of_safety_pct is not None and margin_of_safety_pct > 10
    ) or (
        peg_ratio is not None and peg_ratio < 1.5
    )

    results = {
        "current_price": price,
        "intrinsic_value_dcf": intrinsic_value_dcf,
        "margin_of_safety_pct": margin_of_safety_pct,
        "valuation_zone": valuation_zone,
        "peg_ratio": peg_ratio,
        "eps_cagr_used_pct": round(eps_cagr, 2) if eps_cagr else None,
        "fcf_growth_rate_used_pct": round(growth_rate_annual * 100, 2),
        "scenarios": scenarios,
        "sensitivity_table": sensitivity,
        "evidence": evidence,
    }
    metrics = {
        "pe_ratio": pe,
        "price": price,
        "intrinsic_value": intrinsic_value_dcf,
        "margin_of_safety_pct": margin_of_safety_pct,
        "peg_ratio": peg_ratio,
        "valuation_zone": valuation_zone,
    }

    return StrategyRunResponse(
        strategy_id="DCF_FWD",
        strategy_name="Forward DCF + Relative Valuation Engine",
        status="production",
        executed_at=get_ist_now_str(),
        symbol=norm,
        passed_gates=passed,
        results=results,
        metrics=metrics,
        risk_warnings=[
            "DCF is highly sensitive to growth rate and discount rate assumptions.",
            "Use alongside Reverse DCF (C9) and Relative Valuation for triangulation.",
            "FCF-based DCF may mislead for capital-intensive businesses in CAPEX cycle.",
        ],
        disclaimer="Forward DCF intrinsic value estimate. Not a guarantee of future returns.",
        meta=create_meta_header(source=f"IERL Forward DCF Engine ({norm})"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _compute_valuation_zone(
    pe: float,
    peg: Optional[float],
    mos_pct: Optional[float],
) -> str:
    """Map P/E, PEG, and margin of safety into a valuation zone."""
    signals = []
    if mos_pct is not None:
        if mos_pct > 30:
            signals.append("DEEPLY_UNDERVALUED")
        elif mos_pct > 10:
            signals.append("UNDERVALUED")
        elif mos_pct > -10:
            signals.append("FAIR")
        elif mos_pct > -30:
            signals.append("OVERVALUED")
        else:
            signals.append("EXTREMELY_OVERVALUED")
    if peg is not None:
        if peg < 0.75:
            signals.append("DEEPLY_UNDERVALUED")
        elif peg < 1.5:
            signals.append("UNDERVALUED")
        elif peg < 2.5:
            signals.append("FAIR")
        else:
            signals.append("OVERVALUED")
    if not signals:
        if pe > 0 and pe < 15:
            return "UNDERVALUED"
        elif pe > 50:
            return "EXTREMELY_OVERVALUED"
        return "FAIR"
    # Return the most pessimistic signal for conservatism
    order = ["EXTREMELY_OVERVALUED", "OVERVALUED", "FAIR", "UNDERVALUED", "DEEPLY_UNDERVALUED"]
    for zone in order:
        if zone in signals:
            return zone
    return "FAIR"


def _compute_scenarios(
    fcf_base: Optional[float],
    market_cap: float,
    price: float,
    discount_rate: float,
    terminal_growth: float,
) -> Dict[str, Any]:
    """Bull / Base / Bear scenario with probability-weighted expected return."""
    if not fcf_base or market_cap <= 0:
        return {"status": "insufficient_data"}

    bull = _quick_dcf(fcf_base, market_cap, price, 0.25, discount_rate - 0.02, terminal_growth + 0.01)
    base = _quick_dcf(fcf_base, market_cap, price, 0.12, discount_rate, terminal_growth)
    bear = _quick_dcf(fcf_base, market_cap, price, 0.05, discount_rate + 0.02, terminal_growth - 0.01)

    prob_bull, prob_base, prob_bear = 0.25, 0.50, 0.25
    expected = round(
        (bull or price) * prob_bull +
        (base or price) * prob_base +
        (bear or price) * prob_bear, 2
    )
    expected_return_pct = round(((expected - price) / price) * 100, 2) if price > 0 else 0.0

    return {
        "bull_case": {
            "intrinsic_value": bull, "growth_assumption": "25%",
            "probability": prob_bull, "return_pct": round(((bull or price) - price) / price * 100, 1) if price > 0 else 0
        },
        "base_case": {
            "intrinsic_value": base, "growth_assumption": "12%",
            "probability": prob_base, "return_pct": round(((base or price) - price) / price * 100, 1) if price > 0 else 0
        },
        "bear_case": {
            "intrinsic_value": bear, "growth_assumption": "5%",
            "probability": prob_bear, "return_pct": round(((bear or price) - price) / price * 100, 1) if price > 0 else 0
        },
        "probability_weighted_value": expected,
        "expected_return_pct": expected_return_pct,
    }


def _quick_dcf(
    fcf_base: float, market_cap: float, price: float,
    growth: float, dr: float, tg: float
) -> Optional[float]:
    """Quick DCF for scenario / sensitivity calculations."""
    try:
        pv = sum(fcf_base * ((1 + growth) ** yr) / ((1 + dr) ** yr) for yr in range(1, 8))
        fcf_7 = fcf_base * ((1 + growth) ** 7)
        tv = fcf_7 * (1 + tg) / max(dr - tg, 0.01)
        ev = pv + tv / ((1 + dr) ** 7)
        return round((ev / market_cap) * price, 2)
    except Exception:
        return None


def _insufficient_response(symbol: str, reason: str) -> StrategyRunResponse:
    return StrategyRunResponse(
        strategy_id="DCF_FWD",
        strategy_name="Forward DCF + Relative Valuation Engine",
        status="data_insufficient",
        executed_at=get_ist_now_str(),
        symbol=symbol,
        passed_gates=False,
        results={"status": "data_insufficient", "reason": reason},
        metrics={},
        risk_warnings=[reason],
        disclaimer="Insufficient data for DCF analysis.",
        meta=create_meta_header(source=f"IERL Forward DCF Engine ({symbol})"),
    )
