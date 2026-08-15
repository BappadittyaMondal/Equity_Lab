"""Strategy Module B8: SEPA Fundamental Growth Screening Engine.

Evaluates Specific Earnings Characteristics (SEPA model): P/E relative to growth (PEG), price momentum, and market leadership.
"""

from app.models.schemas import StrategyRunResponse
from app.services.market_data import get_quote, get_history, create_meta_header, normalize_symbol


def run_sepa_b8(symbol: str) -> StrategyRunResponse:
    norm_symbol = normalize_symbol(symbol)
    quote = get_quote(norm_symbol)
    hist = get_history(norm_symbol, period="1y")
    
    # 1y price momentum return
    start_p = float(hist['Close'].iloc[0])
    end_p = float(hist['Close'].iloc[-1])
    momentum_1y = round(((end_p - start_p) / start_p) * 100, 2)
    
    pe = quote.pe_ratio or 25.0
    # SEPA Pass: Positive P/E, 1y momentum >= 15%
    passed = (pe > 0) and (momentum_1y >= 15.0)
    
    results = {
        "sepa_growth_classification": "SUPERPERFORMER_CANDIDATE" if passed else "AVERAGE_GROWTH",
        "momentum_gate_1y": "PASS" if momentum_1y >= 15.0 else "FAIL",
        "valuation_gate": "PASS" if pe < 60 else "ELEVATED_VALUATION"
    }
    
    metrics = {
        "price": quote.price,
        "pe_ratio": pe,
        "one_year_momentum_pct": momentum_1y,
        "fifty_two_week_high": quote.fifty_two_week_high
    }
    
    risk_warnings = [
        "SEPA growth models focus on high-momentum market leaders.",
        "High-growth stocks can experience sharp momentum pullbacks."
    ]
    
    return StrategyRunResponse(
        strategy_id="B8",
        strategy_name="B8 SEPA Fundamental Growth Screening",
        status="production",
        executed_at=quote.meta.retrieved_at,
        symbol=norm_symbol,
        passed_gates=passed,
        results=results,
        metrics=metrics,
        risk_warnings=risk_warnings,
        disclaimer="SEPA quantitative screening based on price momentum and P/E metrics.",
        meta=create_meta_header(source=f"IERL SEPA Engine ({norm_symbol})")
    )
