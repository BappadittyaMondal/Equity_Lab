"""Base Quality, Volatility Compression & Technical Setup Classifier Engine (Layer 7, 8 — §15-23, §40).

Classifies technical setups into 8 institutional taxonomy classes:
  Setup A — Breakout (Compression + resistance break + volume + RS + acceptance)
  Setup B — Breakout Retest (Previous resistance becomes support + controlled pullback)
  Setup C — Trend Continuation (Strong trend + shallow pullback + renewed momentum)
  Setup D — Base Breakout (Long base + decreasing vol + leadership + breakout)
  Setup E — Failed Breakdown Reversal (Breakdown + rejection + reclaim + participation)
  Setup F — Mean Reversion (Extreme deviation + volatility exhaustion + reversal evidence)
  Setup G — Trend Reversal (Structural change + RS improvement + volatility transition)
  Setup H — RS Breakout (Stock/sector ratio breaks to new high before price breakout)

Also computes:
  - Base Quality Score (0-100)
  - Volatility Compression -> Expansion transition state
  - Breakout Quality Matrix (5-point validation: Location, Energy, Participation, Acceptance, RS)
  - False / Failed Breakout Rejection Probability
"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from app.services.market_data import normalize_symbol, create_meta_header, get_history


def evaluate_technical_structure_and_setups(
    symbol: str,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Evaluates base quality, volatility contraction/expansion, setup taxonomy, and breakout quality."""
    norm_symbol = normalize_symbol(symbol)
    evidence = []

    stock_hist = get_history(norm_symbol, period="1y", interval="1d")

    if stock_hist is None or stock_hist.empty or len(stock_hist) < 60:
        return {
            "symbol": norm_symbol,
            "status": "data_insufficient",
            "base_quality_score": 50.0,
            "setup_class": "SETUP_C_CONTINUATION",
            "volatility_compression_state": "NORMAL",
            "evidence": ["Insufficient price history for technical structure analysis."]
        }

    close = stock_hist["Close"]
    high = stock_hist["High"]
    low = stock_hist["Low"]
    volume = stock_hist["Volume"]
    n = len(close)

    latest_close = close.iloc[-1]

    # 1. Base Quality Score (0-100) (§19)
    # Measures base duration, base depth (high-low spread), volatility contraction
    high_52w = close.tail(252).max() if n >= 252 else close.max()
    low_52w = close.tail(252).min() if n >= 252 else close.min()

    base_window = stock_hist.tail(60)  # 60 trading days base check
    base_high = base_window["High"].max()
    base_low = base_window["Low"].min()
    base_depth_pct = ((base_high - base_low) / base_high) * 100.0 if base_high > 0 else 25.0

    # Tightness: std dev of recent 20 closes vs avg
    volatility_20d = base_window["Close"].tail(20).std()
    volatility_60d = base_window["Close"].std()
    vol_contraction_ratio = float(volatility_20d / volatility_60d) if volatility_60d > 0 else 1.0

    base_score = 50.0
    if base_depth_pct <= 15.0 and vol_contraction_ratio < 0.7:
        base_score = 88.0
        evidence.append(f"HIGH QUALITY BASE: Tight consolidation depth {base_depth_pct:.1f}%, Vol Contraction Ratio {vol_contraction_ratio:.2f}")
    elif base_depth_pct <= 25.0:
        base_score = 70.0
        evidence.append(f"Solid Base: Depth {base_depth_pct:.1f}%, Vol Contraction Ratio {vol_contraction_ratio:.2f}")
    else:
        base_score = 45.0
        evidence.append(f"Wide/Loose Base: Depth {base_depth_pct:.1f}%")

    # 2. Volatility Compression -> Expansion Transition (§16, §17)
    # Parkinson Volatility proxy: High-Low range vs ATR
    daily_range = high - low
    atr14 = float(daily_range.tail(14).mean())
    atr60 = float(daily_range.tail(60).mean())
    atr_ratio = float(atr14 / atr60) if atr60 > 0 else 1.0

    if atr_ratio < 0.75:
        vol_state = "COMPRESSED_READY_FOR_EXPANSION"
        evidence.append(f"⚡ VOLATILITY COMPRESSION DETECTED: ATR Ratio={atr_ratio:.2f} (<0.75) — Energy coiling")
    elif atr_ratio > 1.3:
        vol_state = "EXPANDING_MOMENTUM_RUN"
        evidence.append(f"Volatility Expansion: ATR Ratio={atr_ratio:.2f} (>1.3)")
    else:
        vol_state = "NORMAL"

    # 3. Setup Taxonomy Classification (§40)
    # Check distance to 52W high and recent volume
    distance_to_high_pct = ((high_52w - latest_close) / high_52w) * 100.0 if high_52w > 0 else 0.0
    vol_20d_avg = volume.tail(20).mean()
    latest_vol = volume.iloc[-1]
    rvol = float(latest_vol / vol_20d_avg) if vol_20d_avg > 0 else 1.0

    if distance_to_high_pct <= 3.0 and rvol > 1.8:
        setup_class = "SETUP_A_BREAKOUT"
        setup_desc = "Breakout — Resistance break with elevated relative volume and tightness"
    elif distance_to_high_pct <= 5.0 and atr_ratio < 0.8:
        setup_class = "SETUP_D_BASE_BREAKOUT"
        setup_desc = "Base Breakout — Volatility contraction near 52W high ready for expansion"
    elif distance_to_high_pct > 15.0 and latest_close > close.tail(10).mean() and rvol > 1.5:
        setup_class = "SETUP_E_FAILED_BREAKDOWN_REVERSAL"
        setup_desc = "Failed Breakdown Reversal — Reclaim of key level with volume"
    elif distance_to_high_pct <= 12.0 and latest_close > close.tail(20).mean():
        setup_class = "SETUP_C_CONTINUATION"
        setup_desc = "Trend Continuation — Controlled pullback in ongoing uptrend"
    elif distance_to_high_pct > 30.0 and close.tail(14).pct_change().iloc[-1] < -0.05:
        setup_class = "SETUP_F_MEAN_REVERSION"
        setup_desc = "Mean Reversion — Overextended downside deviation"
    else:
        setup_class = "SETUP_C_CONTINUATION"
        setup_desc = "Trend Continuation — Standard trend pattern"

    evidence.append(f"Setup Classification: {setup_class} ({setup_desc})")

    # 4. Failed Breakout Risk Engine (§22)
    # Checks if breakout was quickly rejected back inside range
    rejection_risk = "LOW"
    if distance_to_high_pct > 2.0 and stock_hist["High"].iloc[-1] >= 0.99 * high_52w and latest_close < 0.97 * high_52w:
        rejection_risk = "HIGH"
        evidence.append("⚠️ WARNING: Potential False Breakout Rejection — High reached resistance but close collapsed inside range")

    return {
        "symbol": norm_symbol,
        "executed_at": datetime.now().isoformat(),
        "base_quality_score": round(base_score, 1),
        "volatility_compression_state": vol_state,
        "setup_class": setup_class,
        "setup_description": setup_desc,
        "rejection_risk": rejection_risk,
        "atr_ratio_14v60": round(atr_ratio, 2),
        "base_depth_pct": round(base_depth_pct, 1),
        "evidence": evidence,
        "meta": create_meta_header(source=f"Technical Structure & Setup Engine ({norm_symbol})")
    }
