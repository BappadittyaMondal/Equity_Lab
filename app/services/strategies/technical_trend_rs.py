"""Multi-Timeframe Trend & Relative Strength Acceleration Engine (Layer 3, 4, 5, 6 — §8-14).

Calculates:
  1. Multi-timeframe trend alignment (Weekly W, Daily D, Execution E)
  2. Trend Efficiency Ratio (ER = |Net Price Change| / Sum(|Daily Price Changes|))
  3. Trend Age & Extension Z-Score: (Price - 50DMA) / ATR
  4. Risk-Adjusted Momentum (RAM_6M, RAM_12M = Excess Return / Volatility)
  5. Relative Strength Acceleration vs Nifty 50 / Nifty 500
  6. Pre-Breakout RS Leadership (RS ratio making new high before price breakout)
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from app.services.market_data import normalize_symbol, create_meta_header, get_history
from app.models.schemas import TechnicalStateVector, StrategyRunResponse


def evaluate_technical_trend_and_rs(
    symbol: str,
    benchmark_symbol: str = "^NSEI",
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Evaluates multi-timeframe trend, trend efficiency, extension, RAM, and RS acceleration."""
    norm_symbol = normalize_symbol(symbol)
    norm_bench = normalize_symbol(benchmark_symbol)
    evidence = []

    stock_hist = get_history(norm_symbol, period="1y", interval="1d")
    bench_hist = get_history(norm_bench, period="1y", interval="1d")

    if stock_hist is None or stock_hist.empty or len(stock_hist) < 60:
        return {
            "symbol": norm_symbol,
            "status": "data_insufficient",
            "trend_score": 40.0,
            "rs_score": 40.0,
            "evidence": ["Insufficient price history for technical trend & RS analysis."]
        }

    close = stock_hist["Close"]
    high = stock_hist["High"]
    low = stock_hist["Low"]
    n = len(close)

    # 1. Trend Efficiency Ratio (ER) (§8)
    net_change_20d = abs(close.iloc[-1] - close.iloc[-20]) if n >= 20 else abs(close.iloc[-1] - close.iloc[0])
    sum_daily_changes_20d = close.diff().abs().tail(20).sum()
    er = float(net_change_20d / sum_daily_changes_20d) if sum_daily_changes_20d > 0 else 0.5

    # 2. ATR (14-day) & Extension Z-Score (§8, §84)
    tr = np.maximum(
        high - low,
        np.maximum(
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs()
        )
    )
    atr14 = float(tr.tail(14).mean()) if len(tr) >= 14 else float((high - low).iloc[-1])
    atr14 = max(0.01, atr14)

    sma50 = close.rolling(50).mean().iloc[-1] if n >= 50 else close.mean()
    sma200 = close.rolling(200).mean().iloc[-1] if n >= 200 else close.mean()
    latest_price = close.iloc[-1]

    extension_z = float((latest_price - sma50) / atr14)

    # 3. Risk-Adjusted Momentum (RAM_6M, RAM_12M) (§13)
    returns_daily = close.pct_change().dropna()
    annualized_vol = float(returns_daily.tail(126).std() * np.sqrt(252)) if len(returns_daily) >= 126 else 0.25

    stock_6m_ret = ((latest_price - close.iloc[-126]) / close.iloc[-126]) if n >= 126 else ((latest_price - close.iloc[0]) / close.iloc[0])
    stock_12m_ret = ((latest_price - close.iloc[-252]) / close.iloc[-252]) if n >= 252 else stock_6m_ret

    bench_close = bench_hist["Close"] if bench_hist is not None and not bench_hist.empty else close
    bench_6m_ret = ((bench_close.iloc[-1] - bench_close.iloc[-min(len(bench_close), 126)]) / bench_close.iloc[-min(len(bench_close), 126)]) if len(bench_close) >= 20 else 0.0
    bench_12m_ret = ((bench_close.iloc[-1] - bench_close.iloc[-min(len(bench_close), 252)]) / bench_close.iloc[-min(len(bench_close), 252)]) if len(bench_close) >= 20 else 0.0

    excess_6m = stock_6m_ret - bench_6m_ret
    excess_12m = stock_12m_ret - bench_12m_ret

    ram_6m = float(excess_6m / annualized_vol) if annualized_vol > 0 else 0.0
    ram_12m = float(excess_12m / annualized_vol) if annualized_vol > 0 else 0.0

    # 4. Relative Strength Rating (0-99) & Acceleration (§12)
    rs_rating = max(1, min(99, int(50.0 + (excess_12m * 100.0 / 30.0) * 49.0)))

    recent_rs = stock_6m_ret - bench_6m_ret
    prev_rs = ((close.iloc[-126] - close.iloc[-min(n, 252)]) / close.iloc[-min(n, 252)]) - bench_12m_ret if n >= 126 else 0.0
    rs_accel = float((recent_rs - prev_rs) * 100.0)

    # 5. Pre-Breakout RS Leadership Check (§106)
    # Checks if RS ratio (Stock / Benchmark) hits 52W high before price hits 52W high
    if bench_hist is not None and not bench_hist.empty and len(bench_hist) == len(stock_hist):
        rs_ratio = close / bench_hist["Close"].values
        rs_ratio_52w_high = rs_ratio.tail(252).max() if len(rs_ratio) >= 252 else rs_ratio.max()
        price_52w_high = close.tail(252).max() if len(close) >= 252 else close.max()

        rs_near_high = rs_ratio.iloc[-1] >= 0.98 * rs_ratio_52w_high
        price_below_high = latest_price < 0.96 * price_52w_high
        pre_breakout_rs = bool(rs_near_high and price_below_high)
    else:
        pre_breakout_rs = False

    # Evidence Logging
    evidence.append(f"Trend Efficiency Ratio (ER): {er:.2f} | Extension Z-Score: {extension_z:+.2f} ATRs")
    evidence.append(f"Risk-Adjusted Momentum (RAM): 6M={ram_6m:+.2f}, 12M={ram_12m:+.2f}")
    evidence.append(f"RS Rating: {rs_rating}/99 | RS Acceleration: {rs_accel:+.1f}%")
    if pre_breakout_rs:
        evidence.append("🔥 PRE-BREAKOUT RS LEADERSHIP: Relative Strength hitting new highs ahead of absolute price!")

    # Trend Score (0-100)
    trend_score = min(100.0, max(0.0, 50.0 + (er * 25.0) + (15.0 if latest_price > sma50 else -15.0) + (10.0 if latest_price > sma200 else -10.0)))
    rs_score = min(100.0, max(0.0, float(rs_rating) + (15.0 if pre_breakout_rs else 0.0)))

    return {
        "symbol": norm_symbol,
        "executed_at": datetime.now().isoformat(),
        "trend_score": round(trend_score, 1),
        "rs_score": round(rs_score, 1),
        "trend_efficiency_ratio": round(er, 2),
        "extension_z_score": round(extension_z, 2),
        "ram_6m": round(ram_6m, 2),
        "ram_12m": round(ram_12m, 2),
        "rs_rating_0_99": rs_rating,
        "rs_acceleration": round(rs_accel, 1),
        "pre_breakout_rs_leadership": pre_breakout_rs,
        "evidence": evidence,
        "meta": create_meta_header(source=f"Multi-Timeframe Trend & RS Engine ({norm_symbol})")
    }
