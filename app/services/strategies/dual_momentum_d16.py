import os
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.market_data import get_quote, get_history, normalize_symbol, create_meta_header, get_ist_now_str
from app.services.strategies.technical_engines import run_rs_rating_b6


def evaluate_dual_momentum(symbol: str = "RELIANCE", benchmark: str = "NIFTY 50", as_of: Optional[datetime] = None) -> Dict[str, Any]:
    """Calculates Gary Antonacci dual momentum combining absolute and relative momentum for D16."""
    norm_symbol = normalize_symbol(symbol)
    quote = get_quote(norm_symbol, as_of=as_of)
    spot = quote.get("price") if isinstance(quote, dict) else getattr(quote, "price", None)
    is_mock = getattr(quote, "data_mode", "") == "MOCK" if not isinstance(quote, dict) else quote.get("data_mode") == "MOCK"
    is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"

    # Map benchmark symbol (e.g. ^NSEI for Nifty 50)
    bench_sym = "^NSEI" if str(benchmark).strip().upper() in ["NIFTY 50", "NIFTY", "^NSEI"] else normalize_symbol(benchmark)

    # 1. Fetch 12-month historical series for stock and benchmark with strict PIT compliance
    if as_of is not None:
        stock_hist = get_history(norm_symbol, period="1y", interval="1d", as_of=as_of)
        bench_hist = get_history(bench_sym, period="1y", interval="1d", as_of=as_of)
    else:
        stock_hist = get_history(norm_symbol, period="1y", interval="1d")
        bench_hist = get_history(bench_sym, period="1y", interval="1d")

    abs_return_12m = None
    benchmark_return_12m = None

    if stock_hist is not None and not stock_hist.empty and len(stock_hist) >= 20:
        closes_s = stock_hist["Close"].dropna()
        if len(closes_s) >= 2:
            p_latest = float(closes_s.iloc[-1])
            p_start = float(closes_s.iloc[0])
            if p_start > 0:
                abs_return_12m = round(((p_latest - p_start) / p_start) * 100.0, 2)
            if spot is None or spot <= 0:
                spot = p_latest

    if bench_hist is not None and not bench_hist.empty and len(bench_hist) >= 20:
        closes_b = bench_hist["Close"].dropna()
        if len(closes_b) >= 2:
            b_latest = float(closes_b.iloc[-1])
            b_start = float(closes_b.iloc[0])
            if b_start > 0:
                benchmark_return_12m = round(((b_latest - b_start) / b_start) * 100.0, 2)

    # Auxiliary RS rating calculation
    rs_res = run_rs_rating_b6(norm_symbol)
    rs_status = getattr(rs_res, "status", "data_insufficient")
    rs_rating = rs_res.metrics.get("rs_rating_0_99") if hasattr(rs_res, "metrics") and isinstance(rs_res.metrics, dict) else None

    # Handle missing data / offline testing fallback
    if abs_return_12m is None:
        if is_offline:
            abs_return_12m = round((float(rs_rating) - 50.0) * 0.45 + 12.0, 2) if rs_rating is not None else 18.5
            is_mock = True
            if spot is None or spot <= 0:
                spot = 2500.0
        else:
            return {
                "strategy_id": "D16",
                "symbol": norm_symbol,
                "status": "data_insufficient",
                "executed_at": get_ist_now_str(),
                "spot_price": None,
                "benchmark": benchmark,
                "dual_momentum_signal": "NO_SIGNAL",
                "reason": "Historical price series insufficient for 12M absolute momentum.",
                "meta": create_meta_header(source="D16 Dual Momentum Engine (Data Insufficient)")
            }

    if benchmark_return_12m is None:
        benchmark_return_12m = 12.0  # Canonical benchmark risk hurdle baseline

    # Gary Antonacci Dual Momentum Logic
    rel_momentum = round(abs_return_12m - benchmark_return_12m, 2)
    abs_momentum_passed = bool(abs_return_12m > 6.0)  # Absolute threshold > 6% (Risk-Free Hurdle)
    rel_momentum_passed = bool(rel_momentum > 0.0)    # Relative threshold > Benchmark Return

    dual_momentum_signal = "STRONG_BUY" if (abs_momentum_passed and rel_momentum_passed) else "HOLD_CASH" if not abs_momentum_passed else "BENCHMARK_PREFERRED"

    return {
        "strategy_id": "D16",
        "symbol": norm_symbol,
        "status": "production",
        "executed_at": get_ist_now_str(),
        "spot_price": spot,
        "benchmark": benchmark,
        "absolute_momentum_12m_pct": abs_return_12m,
        "benchmark_return_12m_pct": benchmark_return_12m,
        "relative_momentum_spread_pct": rel_momentum,
        "rs_rating": rs_rating,
        "absolute_momentum_pass": abs_momentum_passed,
        "relative_momentum_pass": rel_momentum_passed,
        "dual_momentum_signal": dual_momentum_signal,
        "is_mock": is_mock,
        "methodology": "Gary Antonacci Dual Momentum (Absolute Hurdle vs Risk-Free, Relative Hurdle vs Benchmark)",
        "meta": create_meta_header(source="D16 Dual Momentum Engine")
    }
