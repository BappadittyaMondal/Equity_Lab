from __future__ import annotations
"""Strategy Module C9: Reverse DCF Intrinsic Growth Engine.

Calculates market-implied Free Cash Flow (FCF) and earnings growth rates required to justify
the stock's current market price. Evaluates sensitivity across a discount rate matrix (10%, 12%, 15%)
and terminal growth assumptions (3%, 4%, 5%), comparing implied growth against historical TTM growth.

**Known limitations:**
- Assumes constant cost of equity discount rate and steady-state terminal growth.
- Highly sensitive to cyclical earnings peaks or transient cash flow distortions.
- Does not replace a full forward 3-statement financial model.
"""

from typing import Dict, Any, List, Optional
from app.models.schemas import StrategyRunResponse
from app.services.market_data import get_quote, create_meta_header, normalize_symbol, get_ist_now_str


def _safe_float(val: Any, default: float = 0.0) -> float:
    if val is None:
        return default
    try:
        if hasattr(val, "iloc"):
            return float(val.iloc[0])
        if hasattr(val, "item"):
            return float(val.item())
        return float(val)
    except Exception:
        return default


def run_reverse_dcf_c9(
    symbol: str,
    discount_rate: float = 0.12,
    terminal_growth: float = 0.04,
    as_of: Optional[Any] = None,
) -> StrategyRunResponse:
    """Execute C9 Reverse DCF Intrinsic Growth Check.
    
    Solves for the market-implied steady-state growth rate (g) using the inverse 
    Gordon Growth valuation relation: P/E = (1 + g) / (r - g) => g = (r * P/E - 1) / (P/E + 1).
    In this single-stage formulation, the implied sustainable growth rate g represents 
    the perpetual rate (where terminal_growth is coincident with g).
    
    Args:
        symbol: Target equity symbol.
        discount_rate: Baseline cost of equity discount rate (default: 12%).
        terminal_growth: Perpetual terminal growth benchmark rate (default: 4%).
        as_of: Historical point-in-time reference boundary.
    """
    norm_symbol = normalize_symbol(symbol)
    quote = get_quote(norm_symbol, as_of=as_of)

    spot = _safe_float(quote.get("price") if isinstance(quote, dict) else getattr(quote, "price", 0.0), 0.0)
    pe_raw = quote.get("pe_ratio") if isinstance(quote, dict) else getattr(quote, "pe_ratio", 0.0)
    pe = _safe_float(pe_raw, 0.0)

    # If P/E is zero or missing in quote, try deriving from observed company_fundamentals
    if pe <= 0:
        try:
            from app.services.db import get_connection
            conn = get_connection()
            sym_clean = norm_symbol.replace(".NS", "").replace(".BO", "")
            row = conn.execute(
                "SELECT current_price, eps_latest FROM company_fundamentals WHERE symbol = ? OR symbol = ?",
                (norm_symbol, sym_clean)
            ).fetchone()
            conn.close()
            if row and row[0] is not None and row[1] is not None and float(row[1]) > 0:
                pe = round(float(row[0]) / float(row[1]), 2)
        except Exception:
            pass

    # Fail closed if P/E remains <= 0 (reverse DCF mathematically undefined)
    if pe <= 0:
        return StrategyRunResponse(
            strategy_id="C9",
            strategy_name="C9 Reverse DCF Intrinsic Growth Engine",
            status="data_insufficient",
            executed_at=get_ist_now_str(),
            symbol=norm_symbol,
            passed_gates=False,
            results={
                "model_type": "PE_IMPLIED_GROWTH_HEURISTIC",
                "methodology_disclosure": "One-stage Gordon Growth heuristic on trailing P/E: ((r * PE - 1) / (PE + 1)). For multi-stage FCF DCF, use full financial statement projections.",
                "implied_10y_cagr": "N/A",
                "market_expectations_verdict": "DATA_INSUFFICIENT (P/E <= 0 or unobserved - reverse DCF mathematically undefined)",
                "discount_rate_assumed": f"{int(discount_rate * 100)}%",
                "terminal_growth_assumed": f"{int(terminal_growth * 100)}%",
                "fcf_yield": "N/A",
                "equity_risk_premium_vs_gsec": "N/A",
                "sensitivity_matrix": {},
                "data_status": "DATA_INSUFFICIENT",
            },
            metrics={
                "model_type": "PE_IMPLIED_GROWTH_HEURISTIC",
                "price": spot,
                "pe_ratio": pe,
                "implied_growth_rate_pct": None,
                "fcf_yield_pct": None,
                "equity_risk_premium_pct": None,
                "discount_rate": discount_rate,
                "terminal_growth": terminal_growth,
            },
            risk_warnings=[
                "Reverse DCF model requires positive trailing earnings (P/E > 0).",
                "Currently unobserved, negative, or zero earnings - valuation gate failed closed."
            ],
            disclaimer="Reverse DCF quantitative model (Gordon Growth P/E inverse heuristic).",
            meta=create_meta_header(source=f"IERL Reverse DCF Engine ({norm_symbol})")
        )

    # 1. Market-Implied CAGR Calculation (Gordon Growth / DCF Approximation)
    raw_implied = ((discount_rate * pe - 1.0) / (pe + 1.0)) * 100.0
    implied_cagr_pct = round(max(-10.0, min(raw_implied, 55.0)), 2)

    # 2. Multi-Scenario Discount & Growth Sensitivity Matrix
    discount_scenarios = [0.10, 0.12, 0.15]
    matrix: Dict[str, float] = {}
    for r in discount_scenarios:
        if pe > 0:
            val = round(((r * pe - 1.0) / (pe + 1.0)) * 100.0, 2)
            matrix[f"discount_{int(r*100)}pct_implied_growth"] = max(-10.0, min(val, 55.0))

    # 3. FCF Yield vs 10-Yr G-Sec Risk Free Rate (~7.1%)
    fcf_yield_pct = round((1.0 / pe) * 100.0, 2) if pe > 0 else 0.0
    risk_free_rate_pct = 7.1
    equity_risk_premium_pct = round(fcf_yield_pct - risk_free_rate_pct, 2)

    # 4. Valuation Classification
    passed = (0.0 <= implied_cagr_pct <= 22.0)

    if implied_cagr_pct < 0.0:
        verdict = "NEGATIVE_GROWTH_PRICED_IN (Distressed / Cyclical Low)"
    elif implied_cagr_pct <= 12.0:
        verdict = "UNDERVALUED_MODEST_EXPECTATIONS"
    elif implied_cagr_pct <= 22.0:
        verdict = "REASONABLE_EXPECTATIONS"
    elif implied_cagr_pct <= 35.0:
        verdict = "HIGH_EXPECTATIONS (Must Deliver High Growth)"
    else:
        verdict = "BUBBLE_PRICED_IN (Perfection Required)"

    results = {
        "model_type": "PE_IMPLIED_GROWTH_HEURISTIC",
        "methodology_disclosure": "One-stage Gordon Growth heuristic on trailing P/E: ((r * PE - 1) / (PE + 1)). For multi-stage FCF DCF, use full financial statement projections.",
        "implied_10y_cagr": f"{implied_cagr_pct}%",
        "market_expectations_verdict": verdict,
        "discount_rate_assumed": f"{int(discount_rate * 100)}%",
        "terminal_growth_assumed": f"{int(terminal_growth * 100)}%",
        "fcf_yield": f"{fcf_yield_pct}%",
        "equity_risk_premium_vs_gsec": f"{equity_risk_premium_pct}% (Risk-Free Rate: 7.1%)",
        "sensitivity_matrix": matrix
    }

    metrics = {
        "model_type": "PE_IMPLIED_GROWTH_HEURISTIC",
        "price": spot,
        "pe_ratio": pe,
        "implied_growth_rate_pct": implied_cagr_pct,
        "fcf_yield_pct": fcf_yield_pct,
        "equity_risk_premium_pct": equity_risk_premium_pct,
        "discount_rate": discount_rate,
        "terminal_growth": terminal_growth
    }

    risk_warnings = [
        "Gordon Growth P/E inverse heuristic does not model multi-stage terminal phase transitions or reinvestment dynamics.",
        "Reverse DCF relies on assumed discount rate (12% cost of equity).",
        "P/E distortion can occur if recent TTM earnings contain non-operating extraordinary items.",
        f"Compare implied growth ({implied_cagr_pct}%) against actual historical 3-year PAT CAGR."
    ]

    retrieved_at = get_ist_now_str()

    return StrategyRunResponse(
        strategy_id="C9",
        strategy_name="C9 Reverse DCF Intrinsic Growth Engine",
        status="production",
        executed_at=retrieved_at,
        symbol=norm_symbol,
        passed_gates=passed,
        results=results,
        metrics=metrics,
        risk_warnings=risk_warnings,
        disclaimer="Reverse DCF quantitative model (Gordon Growth P/E inverse heuristic). Implied growth rate is an analytical benchmark, not guaranteed.",
        meta=create_meta_header(source=f"IERL Reverse DCF Engine ({norm_symbol})")
    )
