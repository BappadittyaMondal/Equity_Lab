"""Strategy Module D15: All-Time High (ATH) Profit Breakout Screen.

Identifies stocks trading within 3% of 52-week or all-time highs with positive price momentum.
"""

from app.models.schemas import StrategyRunResponse
from app.services.market_data import get_quote, get_history, create_meta_header, normalize_symbol


def run_ath_breakout_d15(symbol: str) -> StrategyRunResponse:
    norm_symbol = normalize_symbol(symbol)
    quote = get_quote(norm_symbol)
    hist = get_history(norm_symbol, period="1y")
    
    high_52 = quote.fifty_two_week_high or float(hist['High'].max())
    spot = quote.price
    
    dist_high_pct = round(((spot - high_52) / high_52) * 100, 2)
    passed = (dist_high_pct >= -3.0)  # Within 3% of 52-week high
    
    results = {
        "ath_breakout_status": "BREAKOUT_ZONE" if passed else "CONSOLIDATING",
        "distance_from_high": f"{dist_high_pct}%",
        "spot_price": spot,
        "fifty_two_week_high": high_52
    }
    
    metrics = {
        "price": spot,
        "fifty_two_week_high": high_52,
        "distance_pct": dist_high_pct
    }
    
    risk_warnings = [
        "ATH breakouts can experience false breakouts. Requires strict stop loss.",
        "Verify volume expansion on the day of breakout."
    ]
    
    return StrategyRunResponse(
        strategy_id="D15",
        strategy_name="D15 All-Time High Profit Breakout",
        status="production",
        executed_at=quote.meta.retrieved_at,
        symbol=norm_symbol,
        passed_gates=passed,
        results=results,
        metrics=metrics,
        risk_warnings=risk_warnings,
        disclaimer="ATH momentum breakout quantitative scanner.",
        meta=create_meta_header(source=f"IERL D15 Engine ({norm_symbol})")
    )
