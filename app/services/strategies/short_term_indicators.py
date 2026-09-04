"""Short-Term Quantitative Technical Indicators & Microstructure Analytics.

Implements:
  1. Wilder's Classical RSI (14-period)
  2. Stochastic RSI (14, 14, 3, 3) with Overbought Counter-Trend Exhaustion Detector
  3. Multi-Anchor VWAP Engine (52W High Supply Anchor, 52W Low Demand Anchor, Volume Peak Anchor)
  4. Bollinger Bands & Keltner Channels (TTM Squeeze Detector)
  5. Moving Average Multiples & Overhead Traffic Ribbon (10, 20, 50, 100, 200 MAs)
"""

import math
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np


def clean_series(s: Any) -> pd.Series:
    """Flattens 2D DataFrame/Series to 1D numeric Series and strips NaNs."""
    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]
    return pd.Series(s).dropna().astype(float)


def calculate_wilder_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculates classical Wilder's Relative Strength Index (RSI)."""
    clean_s = clean_series(series)
    if len(clean_s) < period + 1:
        return pd.Series([50.0] * len(clean_s), index=clean_s.index)

    delta = clean_s.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)

    avg_gain = pd.Series(index=clean_s.index, dtype=float)
    avg_loss = pd.Series(index=clean_s.index, dtype=float)

    # Initial simple average
    avg_gain.iloc[period] = gain.iloc[1:period + 1].mean()
    avg_loss.iloc[period] = loss.iloc[1:period + 1].mean()

    # Wilder's exponential smoothing
    for i in range(period + 1, len(clean_s)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi = rsi.fillna(50.0)
    return rsi


def calculate_stochastic_rsi(
    series: pd.Series,
    rsi_period: int = 14,
    stoch_period: int = 14,
    k_smooth: int = 3,
    d_smooth: int = 3
) -> Dict[str, Any]:
    """Calculates Stochastic RSI (%K, %D) and evaluates momentum divergence/exhaustion states."""
    clean_s = clean_series(series)
    if len(clean_s) < rsi_period + stoch_period:
        return {
            "rsi": 50.0,
            "stoch_k": 50.0,
            "stoch_d": 50.0,
            "momentum_exhaustion_state": "NEUTRAL_CONSOLIDATION",
            "is_bearish_exhaustion": False,
            "is_bullish_exhaustion": False,
            "interpretation": "Insufficient historical candles for Stochastic RSI calculation."
        }

    rsi = calculate_wilder_rsi(clean_s, period=rsi_period)
    rsi_min = rsi.rolling(stoch_period).min()
    rsi_max = rsi.rolling(stoch_period).max()

    denom = (rsi_max - rsi_min).replace(0, np.nan)
    raw_stoch = ((rsi - rsi_min) / denom) * 100.0
    raw_stoch = raw_stoch.fillna(50.0)

    stoch_k = raw_stoch.rolling(k_smooth).mean().fillna(50.0)
    stoch_d = stoch_k.rolling(d_smooth).mean().fillna(50.0)

    curr_rsi = round(float(rsi.iloc[-1]), 2)
    curr_k = round(float(stoch_k.iloc[-1]), 2)
    curr_d = round(float(stoch_d.iloc[-1]), 2)

    # Momentum Exhaustion Classification
    if curr_k >= 80.0 and curr_rsi < 50.0:
        state = "BEARISH_EXHAUSTION_COUNTER_TREND"
        is_bearish_ex = True
        is_bullish_ex = False
        interp = f"Bearish Exhaustion: Stoch RSI ({curr_k}) is overbought while Base RSI ({curr_rsi}) is below 50. Counter-trend bounce running out of fuel."
    elif curr_k <= 20.0 and curr_rsi > 50.0:
        state = "BULLISH_OVERSOLD_ACCUMULATION"
        is_bearish_ex = False
        is_bullish_ex = True
        interp = f"Bullish Accumulation Dip: Stoch RSI ({curr_k}) is oversold while Base RSI ({curr_rsi}) retains bullish regime (>50). High-probability long entry zone."
    elif curr_rsi >= 55.0 and curr_k >= 50.0:
        state = "BULLISH_MOMENTUM_EXPANSION"
        is_bearish_ex = False
        is_bullish_ex = False
        interp = f"Bullish Expansion: Both RSI ({curr_rsi}) and Stoch RSI ({curr_k}) confirm directional momentum expansion."
    elif curr_rsi <= 45.0 and curr_k <= 50.0:
        state = "BEARISH_MOMENTUM_EXPANSION"
        is_bearish_ex = True
        is_bullish_ex = False
        interp = f"Bearish Expansion: Both RSI ({curr_rsi}) and Stoch RSI ({curr_k}) confirm sustained downward distribution."
    else:
        state = "NEUTRAL_CONSOLIDATION"
        is_bearish_ex = False
        is_bullish_ex = False
        interp = f"Neutral Momentum: RSI={curr_rsi}, Stoch %K={curr_k}. Trading inside consolidation zone."

    return {
        "rsi": curr_rsi,
        "stoch_k": curr_k,
        "stoch_d": curr_d,
        "momentum_exhaustion_state": state,
        "is_bearish_exhaustion": is_bearish_ex,
        "is_bullish_exhaustion": is_bullish_ex,
        "interpretation": interp
    }


def calculate_multi_anchor_vwap(df: pd.DataFrame, lookback: int = 120) -> Dict[str, Any]:
    """Calculates multi-anchor VWAPs:
      1. 52-Week / Multi-Month High Anchor (Trapped Supply Breakeven)
      2. 52-Week / Multi-Month Low Anchor (Smart Money Demand Defense)
      3. Volume Peak Anchor (Institutional Absorption Level)
    """
    for col in ('close', 'high', 'low', 'volume'):
        if col not in df.columns and col.capitalize() in df.columns:
            df[col] = df[col.capitalize()]

    closes = clean_series(df['close'])
    highs = clean_series(df['high'])
    lows = clean_series(df['low'])
    volumes = clean_series(df['volume'])

    n = len(closes)
    if n < 15:
        cp = float(closes.iloc[-1]) if n > 0 else 100.0
        return {
            "current_price": cp,
            "avwap_high": cp,
            "avwap_low": cp,
            "avwap_vol_peak": cp,
            "dist_to_supply_avwap_pct": 0.0,
            "dist_to_demand_avwap_pct": 0.0,
            "avwap_pinch_spread_pct": 0.0,
            "avwap_structural_bias": "NEUTRAL"
        }

    cp = float(closes.iloc[-1])
    eff_lookback = min(n, lookback)
    sub_df = df.tail(eff_lookback).copy()

    # Anchor 1: High Anchor (trapped overhead supply)
    high_anchor_idx = sub_df['high'].idxmax()
    df_from_high = df.loc[high_anchor_idx:]
    tp_high = (df_from_high['high'] + df_from_high['low'] + df_from_high['close']) / 3.0
    vol_high = df_from_high['volume'].replace(0, 1.0)
    avwap_high = float((tp_high * vol_high).sum() / max(1.0, vol_high.sum()))

    # Anchor 2: Low Anchor (demand defense floor)
    low_anchor_idx = sub_df['low'].idxmin()
    df_from_low = df.loc[low_anchor_idx:]
    tp_low = (df_from_low['high'] + df_from_low['low'] + df_from_low['close']) / 3.0
    vol_low = df_from_low['volume'].replace(0, 1.0)
    avwap_low = float((tp_low * vol_low).sum() / max(1.0, vol_low.sum()))

    # Anchor 3: Volume Peak Anchor (institutional absorption pivot)
    vol_anchor_idx = sub_df['volume'].idxmax()
    df_from_vol = df.loc[vol_anchor_idx:]
    tp_vol = (df_from_vol['high'] + df_from_vol['low'] + df_from_vol['close']) / 3.0
    vol_peak = df_from_vol['volume'].replace(0, 1.0)
    avwap_vol_peak = float((tp_vol * vol_peak).sum() / max(1.0, vol_peak.sum()))

    dist_supply_pct = round(((cp - avwap_high) / avwap_high) * 100.0, 2)
    dist_demand_pct = round(((cp - avwap_low) / avwap_low) * 100.0, 2)
    pinch_spread_pct = round((abs(avwap_high - avwap_low) / cp) * 100.0, 2)

    # Structural Bias Evaluation
    if cp > avwap_high and cp > avwap_low:
        structural_bias = "BULLISH_ABOVE_ALL_ANCHORS"
    elif cp < avwap_high and cp < avwap_low:
        structural_bias = "BEARISH_BELOW_ALL_ANCHORS"
    elif cp >= avwap_low and cp <= avwap_high:
        structural_bias = "CONSOLIDATION_PINCHED_BETWEEN_ANCHORS"
    else:
        structural_bias = "MIXED_TRANSITION"

    return {
        "current_price": round(cp, 2),
        "avwap_high": round(avwap_high, 2),
        "avwap_low": round(avwap_low, 2),
        "avwap_vol_peak": round(avwap_vol_peak, 2),
        "dist_to_supply_avwap_pct": dist_supply_pct,
        "dist_to_demand_avwap_pct": dist_demand_pct,
        "avwap_pinch_spread_pct": pinch_spread_pct,
        "avwap_structural_bias": structural_bias
    }


def calculate_bollinger_keltner_squeeze(
    df: pd.DataFrame,
    bb_period: int = 20,
    bb_mult: float = 2.0,
    kc_period: int = 20,
    kc_mult: float = 1.5
) -> Dict[str, Any]:
    """Calculates Bollinger Bands, Keltner Channels, and John Carter's TTM Squeeze state."""
    for col in ('close', 'high', 'low'):
        if col not in df.columns and col.capitalize() in df.columns:
            df[col] = df[col.capitalize()]

    closes = clean_series(df['close'])
    highs = clean_series(df['high'])
    lows = clean_series(df['low'])

    if len(closes) < max(bb_period, kc_period) + 5:
        cp = float(closes.iloc[-1]) if len(closes) > 0 else 100.0
        return {
            "squeeze_state": "NO_SQUEEZE_NORMAL",
            "is_squeeze_on": False,
            "bb_upper": cp * 1.05,
            "bb_lower": cp * 0.95,
            "bb_middle": cp,
            "bandwidth_pct": 10.0,
            "momentum_histogram": 0.0
        }

    cp = float(closes.iloc[-1])

    # 1. Bollinger Bands
    sma_20 = closes.rolling(bb_period).mean()
    std_20 = closes.rolling(bb_period).std()
    bb_upper = sma_20 + (std_20 * bb_mult)
    bb_lower = sma_20 - (std_20 * bb_mult)
    bandwidth_pct = ((bb_upper.iloc[-1] - bb_lower.iloc[-1]) / sma_20.iloc[-1]) * 100.0

    # 2. Keltner Channels (20 EMA +/- 1.5 * ATR_14)
    ema_20 = closes.ewm(span=kc_period).mean()
    tr1 = highs - lows
    tr2 = (highs - closes.shift(1)).abs()
    tr3 = (lows - closes.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr_14 = tr.rolling(14).mean()

    kc_upper = ema_20 + (atr_14 * kc_mult)
    kc_lower = ema_20 - (atr_14 * kc_mult)

    # 3. Squeeze Detection (BB inside KC)
    is_squeeze_on = bool(bb_upper.iloc[-1] <= kc_upper.iloc[-1] and bb_lower.iloc[-1] >= kc_lower.iloc[-1])
    was_squeeze_on = bool(bb_upper.iloc[-2] <= kc_upper.iloc[-2] and bb_lower.iloc[-2] >= kc_lower.iloc[-2])

    # 4. Linear regression momentum histogram of deviation from mid
    mid_price = (highs.rolling(bb_period).max() + lows.rolling(bb_period).min()) / 2.0
    avg_basis = (mid_price + ema_20) / 2.0
    val = closes - avg_basis
    mom = float(val.tail(5).mean())

    if is_squeeze_on:
        squeeze_state = "SQUEEZE_ON"
    elif was_squeeze_on and not is_squeeze_on:
        squeeze_state = "SQUEEZE_FIRED_LONG" if mom > 0 else "SQUEEZE_FIRED_SHORT"
    else:
        squeeze_state = "NO_SQUEEZE_NORMAL"

    return {
        "squeeze_state": squeeze_state,
        "is_squeeze_on": is_squeeze_on,
        "bb_upper": round(float(bb_upper.iloc[-1]), 2),
        "bb_lower": round(float(bb_lower.iloc[-1]), 2),
        "bb_middle": round(float(sma_20.iloc[-1]), 2),
        "bandwidth_pct": round(float(bandwidth_pct), 2),
        "momentum_histogram": round(mom, 2)
    }


def calculate_moving_average_ribbon(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates 10D, 20D, 50D, 100D, 200D moving averages and quantifies overhead resistance traffic."""
    for col in ('close', 'high', 'low'):
        if col not in df.columns and col.capitalize() in df.columns:
            df[col] = df[col.capitalize()]

    closes = clean_series(df['close'])
    cp = float(closes.iloc[-1]) if len(closes) > 0 else 100.0

    ma_map = {}
    periods = [10, 20, 50, 100, 200]
    for p in periods:
        if len(closes) >= p:
            val = float(closes.rolling(p).mean().iloc[-1])
            slope = float((val - closes.rolling(p).mean().iloc[-5]) / val) * 100.0 if len(closes) >= p + 5 else 0.0
            ma_map[f"sma_{p}"] = round(val, 2)
            ma_map[f"sma_{p}_slope_pct"] = round(slope, 2)
        else:
            ma_map[f"sma_{p}"] = None
            ma_map[f"sma_{p}_slope_pct"] = 0.0

    # Count overhead resistance traffic (declining moving averages lying within 6% above current spot)
    overhead_count = 0
    for p in [50, 100, 200]:
        val = ma_map.get(f"sma_{p}")
        slope = ma_map.get(f"sma_{p}_slope_pct", 0.0)
        if val is not None and val > cp and ((val - cp) / cp) <= 0.08:
            if slope <= 0.0:  # declining moving average
                overhead_count += 1

    if overhead_count >= 2:
        traffic_tier = "HEAVY_OVERHEAD_RESISTANCE_CEILING"
    elif overhead_count == 1:
        traffic_tier = "MODERATE_OVERHEAD_RESISTANCE"
    else:
        traffic_tier = "CLEAR_SKY_NO_IMMEDIATE_MA_OVERHEAD"

    return {
        "current_price": round(cp, 2),
        "moving_averages": ma_map,
        "overhead_declining_ma_count": overhead_count,
        "overhead_traffic_tier": traffic_tier
    }
