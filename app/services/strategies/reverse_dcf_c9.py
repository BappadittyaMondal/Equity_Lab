"""Strategy Module C9: Reverse DCF Intrinsic Growth Check.

Calculates the market-implied FCF/Earnings growth rate required to justify current stock price.
"""

from app.models.schemas import StrategyRunResponse
from app.services.market_data import get_quote, create_meta_header, normalize_symbol


def run_reverse_dcf_c9(symbol: str, discount_rate: float = 0.12, terminal_growth: float = 0.04) -> StrategyRunResponse:
    norm_symbol = normalize_symbol(symbol)
    quote = get_quote(norm_symbol)
    
    pe = quote.pe_ratio or 25.0
    # Formula for implied growth rate from P/E multiple under Gordon Growth/DCF approximation
    # P/E = (1 + g) / (r - g) => Implied growth g ~ (r * P/E - 1) / (P/E + 1)
    if pe > 0:
        implied_growth = round(((discount_rate * pe - 1.0) / (pe + 1.0)) * 100.0, 2)
        # Cap range for reporting sanity
        implied_growth = max(-10.0, min(implied_growth, 50.0))
    else:
        implied_growth = 0.0

    passed = (0.0 < implied_growth < 25.0)

    results = {
        "implied_10y_cagr": f"{implied_growth}%",
        "market_expectations_verdict": "REASONABLE" if passed else ("HIGH_EXPECTATIONS" if implied_growth >= 25 else "NEGATIVE_GROWTH_PRICED_IN"),
        "discount_rate_assumed": f"{discount_rate * 100}%",
        "terminal_growth_assumed": f"{terminal_growth * 100}%"
    }

    metrics = {
        "price": quote.price,
        "pe_ratio": pe,
        "implied_growth_rate_pct": implied_growth,
        "market_cap_inr": quote.market_cap
    }

    risk_warnings = [
        "Reverse DCF relies on assumed discount rate (12% cost of equity).",
        "Sensitivity to P/E ratio is high. Verify against actual free cash flow trends."
    ]

    return StrategyRunResponse(
        strategy_id="C9",
        strategy_name="C9 Reverse DCF Intrinsic Growth Check",
        status="production",
        executed_at=quote.meta.retrieved_at,
        symbol=norm_symbol,
        passed_gates=passed,
        results=results,
        metrics=metrics,
        risk_warnings=risk_warnings,
        disclaimer="Reverse DCF valuation model. Implied growth is an estimate, not a forecast.",
        meta=create_meta_header(source=f"IERL Reverse DCF Engine ({norm_symbol})")
    )
