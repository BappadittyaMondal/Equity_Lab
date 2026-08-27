"""Technical Analysis Engines — Phase 2, Layer 6.

Implements real calculation logic for:
  B4  — Volume Price Analysis (VPA) with accumulation detection
  B6  — Relative Strength (RS) Rating vs Nifty 50
  B7  — Pocket Pivot Volume Accumulation
  D17 — Mean Reversion with Weinstein stage analysis

Each engine reads from real price history (yfinance or market_daily_snapshots)
and returns a normalized 0–100 score with evidence.
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from app.models.schemas import StrategyRunResponse
from app.services.market_data import (
    create_meta_header, normalize_symbol, get_ist_now_str, get_history
)

logger = logging.getLogger(__name__)

_FALLBACK_PERIOD = "1y"
_MIN_BARS = 60  # Minimum bars for meaningful technical analysis


def _get_price_data(symbol: str, period: str = _FALLBACK_PERIOD) -> Optional[pd.DataFrame]:
    """Safely fetch observed OHLCV data as a DataFrame. Rejects synthetic/mock data."""
    try:
        hist = get_history(symbol, period=period, interval="1d")
        if hist is not None and not hist.empty and len(hist) >= _MIN_BARS:
            if getattr(hist, "attrs", {}).get("is_mock", False) or getattr(hist, "attrs", {}).get("data_mode") == "MOCK":
                return None
            return hist
        return None
    except Exception as e:
        logger.warning("Could not fetch price history for %s: %s", symbol, e)
        return None


def _insufficient(strategy_id: str, name: str, symbol: str, reason: str) -> StrategyRunResponse:
    return StrategyRunResponse(
        strategy_id=strategy_id,
        strategy_name=name,
        status="data_insufficient",
        executed_at=get_ist_now_str(),
        symbol=symbol,
        passed_gates=False,
        results={"status": "data_insufficient", "reason": reason},
        metrics={},
        risk_warnings=[reason],
        disclaimer="Insufficient price data for technical analysis.",
        meta=create_meta_header(source=f"IERL Technical Engine ({symbol})"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# B4 — Volume Price Analysis
# ─────────────────────────────────────────────────────────────────────────────

def run_vpa_b4(symbol: str) -> StrategyRunResponse:
    """Volume Price Analysis — detects institutional accumulation.

    Uses volume z-score and price spread ratio to identify:
    - High volume narrow range bars (potential distribution)
    - High volume wide range bars (genuine accumulation)
    - Volume dry-up patterns before base breakout
    """
    norm = normalize_symbol(symbol)
    hist = _get_price_data(norm)

    if hist is None:
        return _insufficient("B4", "Volume Price Analysis", norm, f"Insufficient price history (need ≥{_MIN_BARS} bars)")

    evidence = []
    score = 50.0  # neutral start

    close = hist["Close"]
    volume = hist["Volume"]
    high = hist["High"]
    low = hist["Low"]

    # ── Volume Z-Score (last 20-day window vs 50-day avg) ─────────────────
    vol_20d_avg = volume.tail(20).mean()
    vol_50d_avg = volume.tail(50).mean()
    vol_std = volume.tail(50).std()
    latest_vol = volume.iloc[-1]

    vol_z = (latest_vol - vol_50d_avg) / vol_std if vol_std > 0 else 0.0

    # ── Price Spread Ratio (today's range / 20d avg range) ────────────────
    daily_range = high - low
    avg_range_20d = daily_range.tail(20).mean()
    latest_range = daily_range.iloc[-1]
    spread_ratio = (latest_range / avg_range_20d) if avg_range_20d > 0 else 1.0

    # ── Accumulation signal: High vol + wide spread + close near high ──────
    close_position = (close.iloc[-1] - low.iloc[-1]) / latest_range if latest_range > 0 else 0.5

    accumulation_score = 0.0
    if vol_z > 1.5 and spread_ratio > 1.2 and close_position > 0.7:
        accumulation_score = 30.0
        evidence.append(
            f"STRONG ACCUMULATION: Vol z-score={vol_z:.1f}, spread ratio={spread_ratio:.2f}, "
            f"close near high ({close_position*100:.0f}th percentile)"
        )
    elif vol_z > 0.5 and spread_ratio > 0.8:
        accumulation_score = 15.0
        evidence.append(f"Moderate volume expansion: z-score={vol_z:.1f}")
    elif vol_z < -1.0:
        accumulation_score = -10.0
        evidence.append(f"Volume DRYING UP (z-score={vol_z:.1f}) — potential basing or distribution")

    # ── Volume trend (20d vs 50d avg) ─────────────────────────────────────
    vol_trend = ((vol_20d_avg - vol_50d_avg) / vol_50d_avg) * 100 if vol_50d_avg > 0 else 0.0

    # ── Price trend context ────────────────────────────────────────────────
    sma_20 = close.tail(20).mean()
    sma_50 = close.tail(50).mean()
    price_above_sma20 = bool(close.iloc[-1] > sma_20)
    price_above_sma50 = bool(close.iloc[-1] > sma_50)

    if price_above_sma20 and price_above_sma50:
        score += 20 + accumulation_score
        evidence.append(f"Price above both 20DMA ({sma_20:.0f}) and 50DMA ({sma_50:.0f})")
    elif price_above_sma50:
        score += 10 + accumulation_score
    else:
        score += accumulation_score
        evidence.append(f"Price below 50DMA — trend not confirmed")

    final_score = max(0.0, min(100.0, round(score, 1)))
    passed = final_score >= 55 and accumulation_score > 0

    return StrategyRunResponse(
        strategy_id="B4",
        strategy_name="Volume Price Analysis (VPA) Liquidity Spike",
        status="production",
        executed_at=get_ist_now_str(),
        symbol=norm,
        passed_gates=passed,
        results={
            "vpa_score": final_score,
            "accumulation_signal": "STRONG" if accumulation_score >= 30 else ("MODERATE" if accumulation_score > 0 else "NONE"),
            "volume_z_score": round(vol_z, 2),
            "price_spread_ratio": round(spread_ratio, 2),
            "volume_trend_20v50_pct": round(vol_trend, 1),
            "price_above_sma20": price_above_sma20,
            "price_above_sma50": price_above_sma50,
            "evidence": evidence,
        },
        metrics={
            "vpa_score": final_score,
            "volume_z_score": round(vol_z, 2),
            "price_spread_ratio": round(spread_ratio, 2),
        },
        risk_warnings=[
            "Volume signals require confirmation over 2–3 sessions.",
            "High volume near resistance may indicate distribution, not accumulation.",
        ],
        disclaimer="Volume Price Analysis — institutional accumulation detector.",
        meta=create_meta_header(source=f"IERL VPA Engine ({norm})"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# B6 — Relative Strength Rating
# ─────────────────────────────────────────────────────────────────────────────

def run_rs_rating_b6(symbol: str, benchmark: str = "^NSEI") -> StrategyRunResponse:
    """Relative Strength Rating — 12-month weighted return vs Nifty 50.

    Weights: Q1 (oldest) = 40%, Q2 = 20%, Q3 = 20%, Q4 (recent) = 20%.
    RS Rating 0–99 (IBD-style).
    """
    norm = normalize_symbol(symbol)
    bench_norm = normalize_symbol(benchmark)

    stock_hist = _get_price_data(norm, "1y")
    bench_hist = _get_price_data(bench_norm, "1y")

    if stock_hist is None or bench_hist is None:
        return _insufficient("B6", "RS Rating", norm, "Need 1Y price history for both stock and benchmark")

    evidence = []

    def _quarterly_return(df: pd.DataFrame, start_pct: float, end_pct: float) -> float:
        n = len(df)
        s = int(n * start_pct)
        e = int(n * end_pct)
        if s >= e or e > n:
            return 0.0
        start_price = df["Close"].iloc[s]
        end_price = df["Close"].iloc[e - 1]
        return ((end_price - start_price) / start_price) * 100.0 if start_price > 0 else 0.0

    # Quarterly returns (oldest Q first)
    weights = [0.40, 0.20, 0.20, 0.20]
    quarters = [(0.0, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 1.0)]

    stock_weighted = sum(
        w * _quarterly_return(stock_hist, s, e)
        for w, (s, e) in zip(weights, quarters)
    )
    bench_weighted = sum(
        w * _quarterly_return(bench_hist, s, e)
        for w, (s, e) in zip(weights, quarters)
    )

    # RS Line = stock return / bench return (excess return)
    excess_return = stock_weighted - bench_weighted

    # Map excess return to 0–99 rating
    # +30% excess → RS 99, -30% excess → RS 1
    rs_raw = 50.0 + (excess_return / 30.0) * 49.0
    rs_rating = max(1, min(99, int(rs_raw)))

    latest_price = stock_hist["Close"].iloc[-1]
    sma_200 = float(stock_hist["Close"].tail(200).mean() if len(stock_hist) >= 200 else stock_hist["Close"].mean())
    price_above_200dma = bool(latest_price > sma_200)

    if rs_rating >= 80:
        evidence.append(f"RS Rating {rs_rating}/99: TOP PERFORMER — outperforming 80%+ of stocks")
    elif rs_rating >= 60:
        evidence.append(f"RS Rating {rs_rating}/99: Above average relative strength")
    else:
        evidence.append(f"RS Rating {rs_rating}/99: Underperforming benchmark")

    evidence.append(f"Stock 12M weighted return: {stock_weighted:.1f}% vs Nifty: {bench_weighted:.1f}%")
    evidence.append(f"Excess return vs benchmark: {excess_return:+.1f}%")

    if price_above_200dma:
        evidence.append(f"Price above 200DMA ({sma_200:.0f}) — long-term uptrend intact")

    passed = rs_rating >= 70 and price_above_200dma

    return StrategyRunResponse(
        strategy_id="B6",
        strategy_name="Relative Strength RS Rating",
        status="production",
        executed_at=get_ist_now_str(),
        symbol=norm,
        passed_gates=passed,
        results={
            "rs_rating": rs_rating,
            "stock_weighted_return_pct": round(stock_weighted, 2),
            "benchmark_weighted_return_pct": round(bench_weighted, 2),
            "excess_return_pct": round(excess_return, 2),
            "price_above_200dma": price_above_200dma,
            "evidence": evidence,
        },
        metrics={
            "rs_rating_0_99": rs_rating,
            "excess_return_pct": round(excess_return, 2),
            "price_above_200dma": price_above_200dma,
        },
        risk_warnings=[
            "RS Rating is backward-looking — a stock with high RS may be extended.",
            "Screen for RS Rating ≥ 80 in Stage 2 uptrend for best results.",
        ],
        disclaimer="RS Rating based on 12-month price momentum vs Nifty 50.",
        meta=create_meta_header(source=f"IERL RS Rating Engine ({norm})"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# B7 — Pocket Pivot Volume
# ─────────────────────────────────────────────────────────────────────────────

def run_pocket_pivot_b7(symbol: str) -> StrategyRunResponse:
    """Pocket Pivot — early institutional entry signal before base breakout.

    A pocket pivot occurs when:
    1. Stock closes in the upper half of its day's range
    2. Volume on up-day exceeds the highest down-volume in prior 10 sessions
    3. Stock is in a basing pattern (within 20% of 52W high)
    """
    norm = normalize_symbol(symbol)
    hist = _get_price_data(norm)

    if hist is None:
        return _insufficient("B7", "Pocket Pivot Volume Accumulation", norm, f"Need ≥{_MIN_BARS} bars of price data")

    evidence = []
    close = hist["Close"]
    high = hist["High"]
    low = hist["Low"]
    volume = hist["Volume"]

    recent = hist.tail(50)
    pocket_pivots_last30 = 0

    for i in range(10, len(recent)):
        window = recent.iloc[i - 10:i]
        today = recent.iloc[i]

        # Up day?
        prev_close = recent.iloc[i - 1]["Close"]
        if today["Close"] <= prev_close:
            continue

        # Close in upper half of range
        day_range = today["High"] - today["Low"]
        if day_range > 0:
            close_position = (today["Close"] - today["Low"]) / day_range
            if close_position < 0.5:
                continue

        # Volume > max down-volume in prior 10 days
        down_volumes = [
            row["Volume"]
            for _, row in window.iterrows()
            if row["Close"] <= row["Open"]
        ]
        if not down_volumes:
            continue
        max_down_vol = max(down_volumes)
        if today["Volume"] > max_down_vol:
            pocket_pivots_last30 += 1

    # Basing check: price within 20% of 52W high
    high_52w = close.tail(252).max() if len(close) >= 252 else close.max()
    latest_price = close.iloc[-1]
    distance_from_high_pct = ((high_52w - latest_price) / high_52w) * 100 if high_52w > 0 else 100.0
    in_base = distance_from_high_pct <= 20.0

    # Score
    score = 30.0
    if pocket_pivots_last30 >= 3:
        score = 85.0
        evidence.append(f"STRONG: {pocket_pivots_last30} pocket pivots detected in last 30 days")
    elif pocket_pivots_last30 >= 1:
        score = 60.0
        evidence.append(f"MODERATE: {pocket_pivots_last30} pocket pivot(s) detected")
    else:
        evidence.append("No pocket pivot signals in last 30 trading days")

    if in_base:
        evidence.append(f"Stock in base: {distance_from_high_pct:.1f}% below 52W high ({high_52w:.0f})")
    else:
        evidence.append(f"Extended: {distance_from_high_pct:.1f}% below 52W high — wait for base formation")
        score *= 0.7

    passed = pocket_pivots_last30 >= 1 and in_base

    return StrategyRunResponse(
        strategy_id="B7",
        strategy_name="Pocket Pivot Volume Accumulation",
        status="production",
        executed_at=get_ist_now_str(),
        symbol=norm,
        passed_gates=passed,
        results={
            "pocket_pivot_score": round(score, 1),
            "pocket_pivots_last30": pocket_pivots_last30,
            "in_base": in_base,
            "distance_from_52w_high_pct": round(distance_from_high_pct, 2),
            "evidence": evidence,
        },
        metrics={
            "pocket_pivot_count": pocket_pivots_last30,
            "distance_from_52w_high_pct": round(distance_from_high_pct, 2),
            "in_base": in_base,
        },
        risk_warnings=[
            "Pocket pivots must occur in constructive price action, not during distribution.",
            "Confirm with volume > 20d average on the pocket pivot day.",
        ],
        disclaimer="Pocket pivot detection — early institutional accumulation signal.",
        meta=create_meta_header(source=f"IERL Pocket Pivot Engine ({norm})"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# D17 — Mean Reversion + Weinstein Stage Analysis
# ─────────────────────────────────────────────────────────────────────────────

def run_mean_reversion_d17(symbol: str) -> StrategyRunResponse:
    """Mean Reversion + Weinstein Stage Classification.

    Stage analysis (Weinstein/Mansfield):
      Stage 1: Basing    — price flat, 30WMA flat
      Stage 2: Advancing — price above rising 30WMA
      Stage 3: Topping   — price below declining 30WMA, extended prior run
      Stage 4: Declining — price and 30WMA both declining

    Mean reversion signal: RSI oversold in Stage 1/2 = buy opportunity.
    """
    norm = normalize_symbol(symbol)
    hist = _get_price_data(norm, "2y")  # Need more data for 30-week MA

    if hist is None:
        return _insufficient("D17", "Mean Reversion + Stage Analysis", norm, "Need ≥120 bars for stage analysis")

    evidence = []
    close = hist["Close"]

    # ── 30-week (150-day) Moving Average for stage analysis ───────────────
    n = len(close)
    sma150 = close.rolling(150).mean() if n >= 150 else close.rolling(n // 2).mean()
    sma30d = close.rolling(30).mean()
    sma200d = close.rolling(200).mean() if n >= 200 else None

    latest_close = close.iloc[-1]
    latest_sma150 = sma150.iloc[-1]
    latest_sma30 = sma30d.iloc[-1]

    # ── Weinstein Stage ────────────────────────────────────────────────────
    # 150DMA slope over 4 weeks
    sma150_slope = None
    if not pd.isna(sma150.iloc[-1]) and not pd.isna(sma150.iloc[-20]):
        sma150_slope = (sma150.iloc[-1] - sma150.iloc[-20]) / sma150.iloc[-20] * 100

    above_sma150 = bool(latest_close > latest_sma150) if not pd.isna(latest_sma150) else False
    above_sma30 = bool(latest_close > latest_sma30)

    if above_sma150 and sma150_slope and sma150_slope > 0:
        stage = "STAGE_2_ADVANCING"
        evidence.append(f"✅ Stage 2 — Price above rising 150DMA ({latest_sma150:.0f}). Uptrend intact.")
        stage_score = 75.0
    elif not above_sma150 and sma150_slope and sma150_slope < 0:
        stage = "STAGE_4_DECLINING"
        evidence.append(f"⚠️ Stage 4 — Price and 150DMA both declining. Avoid.")
        stage_score = 15.0
    elif above_sma150 and sma150_slope and sma150_slope <= 0:
        stage = "STAGE_3_TOPPING"
        evidence.append(f"Stage 3 — Price above but 150DMA flattening. Distribution risk.")
        stage_score = 35.0
    else:
        stage = "STAGE_1_BASING"
        evidence.append(f"Stage 1 — Basing phase. Wait for breakout above 150DMA ({latest_sma150:.0f})")
        stage_score = 50.0

    # ── RSI (14-day) for mean reversion ───────────────────────────────────
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, float("inf"))
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    rsi_score = 0.0
    if not pd.isna(latest_rsi):
        if latest_rsi < 30:
            rsi_score = 20.0
            evidence.append(f"RSI OVERSOLD: {latest_rsi:.1f} — potential mean reversion bounce")
        elif latest_rsi < 40:
            rsi_score = 12.0
            evidence.append(f"RSI low: {latest_rsi:.1f} — approaching oversold")
        elif latest_rsi > 70:
            rsi_score = -10.0
            evidence.append(f"RSI OVERBOUGHT: {latest_rsi:.1f} — extended, caution on new entries")
        else:
            evidence.append(f"RSI neutral: {latest_rsi:.1f}")

    # ── 52-week position ───────────────────────────────────────────────────
    high_52w = close.tail(252).max() if len(close) >= 252 else close.max()
    low_52w = close.tail(252).min() if len(close) >= 252 else close.min()
    position_pct = ((latest_close - low_52w) / (high_52w - low_52w)) * 100 if high_52w > low_52w else 50.0
    evidence.append(f"52W position: {position_pct:.0f}th percentile (low={low_52w:.0f}, high={high_52w:.0f})")

    final_score = max(0, min(100, stage_score + rsi_score))
    passed = stage in ("STAGE_1_BASING", "STAGE_2_ADVANCING") and latest_rsi < 50

    return StrategyRunResponse(
        strategy_id="D17",
        strategy_name="Mean Reversion + Weinstein Stage Analysis",
        status="production",
        executed_at=get_ist_now_str(),
        symbol=norm,
        passed_gates=passed,
        results={
            "mean_reversion_score": round(final_score, 1),
            "weinstein_stage": stage,
            "sma150_slope_4w_pct": round(sma150_slope, 2) if sma150_slope else None,
            "rsi_14d": round(latest_rsi, 1) if not pd.isna(latest_rsi) else None,
            "price_above_150dma": above_sma150,
            "position_in_52w_range_pct": round(position_pct, 1),
            "evidence": evidence,
        },
        metrics={
            "weinstein_stage": stage,
            "rsi_14d": round(latest_rsi, 1) if not pd.isna(latest_rsi) else None,
            "price_above_150dma": above_sma150,
            "mean_reversion_score": round(final_score, 1),
        },
        risk_warnings=[
            "Stage 1 basing can last 6–18 months — patience required before entry.",
            "Mean reversion RSI signals work best in Stage 2 uptrends, not Stage 4.",
        ],
        disclaimer="Weinstein Stage + RSI mean reversion analysis.",
        meta=create_meta_header(source=f"IERL Stage Analysis Engine ({norm})"),
    )
