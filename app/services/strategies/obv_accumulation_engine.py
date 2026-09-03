r"""OBV Slope Acceleration & Stealth Accumulation Engine ($\mathcal{C}_{OBV}$)

Implements corporate-action-adjusted cumulative OBV slope acceleration tracking.
Detects institutional stealth accumulation during multi-year price consolidation bases.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.models.schemas import StrategyRunResponse
from app.services.market_data import (
    create_meta_header, normalize_symbol, get_ist_now_str, get_history
)

logger = logging.getLogger(__name__)

_MIN_WEEKLY_BARS = 52


def calculate_obv_series(df: pd.DataFrame) -> pd.Series:
    """Calculates split-adjusted Cumulative On-Balance Volume (OBV)."""
    close = df["Close"].values
    volume = df["Volume"].values
    
    if len(close) == 0:
        return pd.Series([], dtype=float)
        
    diff = np.diff(close)
    direction = np.zeros(len(close))
    direction[1:] = np.sign(diff)
    
    obv = np.cumsum(direction * volume)
    return pd.Series(obv, index=df.index)


def _calc_obv_weekly_rate(obv_series: pd.Series, mean_volume: float) -> float:
    """Computes normalized weekly OBV accumulation rate (in units of average weekly volume)."""
    n = len(obv_series)
    if n < 3 or mean_volume <= 0:
        return 0.0
    x = np.arange(n)
    y = obv_series.values / mean_volume
    slope, _ = np.polyfit(x, y, 1)
    return float(slope)


def compute_obv_convexity(weekly_df: pd.DataFrame) -> Dict[str, Any]:
    """Computes OBV Acceleration Convexity C_OBV over 12W vs 40W windows."""
    if len(weekly_df) < _MIN_WEEKLY_BARS:
        return {
            "c_obv": 0.0,
            "slope_12w": 0.0,
            "slope_40w": 0.0,
            "obv_z_score": 0.0,
            "sufficient_data": False
        }
        
    obv = calculate_obv_series(weekly_df)
    mean_vol = float(weekly_df["Volume"].tail(52).mean())
    if mean_vol <= 0:
        mean_vol = 1.0
    
    # 12-week recent accumulation rate
    recent_12w = obv.tail(12)
    rate_12w = _calc_obv_weekly_rate(recent_12w, mean_vol)
    
    # Prior 40-week baseline rate (t-52 to t-12)
    prior_40w = obv.iloc[-52:-12] if len(obv) >= 52 else obv.iloc[:-12]
    rate_40w = _calc_obv_weekly_rate(prior_40w, mean_vol)
    
    # Compute rolling 12w rates across trailing 52w to estimate rolling volatility
    rolling_rates = []
    for i in range(12, min(len(obv), 52)):
        sub_seg = obv.iloc[-i-12:-i]
        if len(sub_seg) >= 5:
            rolling_rates.append(_calc_obv_weekly_rate(sub_seg, mean_vol))
            
    std_rates = max(0.5, float(np.std(rolling_rates))) if len(rolling_rates) > 3 else 0.5
    
    c_obv = (rate_12w - rate_40w) / std_rates
    
    return {
        "c_obv": round(float(c_obv), 2),
        "slope_12w": round(float(rate_12w), 4),
        "slope_40w": round(float(rate_40w), 4),
        "std_rates": round(float(std_rates), 4),
        "sufficient_data": True
    }


def run_obv_accumulation(symbol: str, hist_df: Optional[pd.DataFrame] = None, as_of: Optional[Any] = None) -> StrategyRunResponse:
    """Runs Cumulative OBV Acceleration Convexity Engine on symbol."""
    norm = normalize_symbol(symbol)
    
    if hist_df is None or hist_df.empty:
        try:
            hist_df = get_history(norm, period="3y", interval="1wk", as_of=as_of)
        except Exception as e:
            logger.warning("Failed fetching weekly data for OBV Engine (%s): %s", norm, e)
            hist_df = None
            
    if hist_df is None or hist_df.empty or len(hist_df) < _MIN_WEEKLY_BARS:
        return StrategyRunResponse(
            strategy_id="OBV_ACC",
            strategy_name="OBV Slope Acceleration Convexity",
            status="data_insufficient",
            executed_at=get_ist_now_str(),
            symbol=norm,
            passed_gates=False,
            results={"status": "data_insufficient", "reason": f"Need ≥{_MIN_WEEKLY_BARS} weekly bars"},
            metrics={},
            risk_warnings=["Insufficient multi-year weekly price data."],
            disclaimer="OBV Slope Acceleration Analysis.",
            meta=create_meta_header(source=f"IERL OBV Accumulation Engine ({norm})"),
        )
        
    metrics = compute_obv_convexity(hist_df)
    c_obv = metrics["c_obv"]
    
    evidence = []
    score = 50.0
    
    if c_obv >= 2.5:
        score = 95.0
        evidence.append(f"EXTREME OBV ACCELERATION: C_OBV={c_obv:.2f}σ (Heavy Institutional Cornering)")
    elif c_obv >= 1.5:
        score = 80.0
        evidence.append(f"STRONG OBV ACCELERATION: C_OBV={c_obv:.2f}σ (Stealth Institutional Accumulation)")
    elif c_obv >= 0.5:
        score = 65.0
        evidence.append(f"MODERATE OBV ACCELERATION: C_OBV={c_obv:.2f}σ")
    elif c_obv < -1.0:
        score = 25.0
        evidence.append(f"OBV DISTRIBUTION DIVERGENCE: C_OBV={c_obv:.2f}σ")
    else:
        evidence.append(f"OBV neutral/dormant: C_OBV={c_obv:.2f}σ")
        
    passed = c_obv >= 1.5
    
    return StrategyRunResponse(
        strategy_id="OBV_ACC",
        strategy_name="OBV Slope Acceleration Convexity",
        status="production",
        executed_at=get_ist_now_str(),
        symbol=norm,
        passed_gates=passed,
        results={
            "obv_convexity_score": round(score, 1),
            "c_obv": c_obv,
            "slope_12w": metrics["slope_12w"],
            "slope_40w": metrics["slope_40w"],
            "evidence": evidence,
        },
        metrics={
            "c_obv": c_obv,
            "obv_convexity_score": round(score, 1),
        },
        risk_warnings=[
            "OBV signals require volume-weighted delivery confirmation.",
            "Verify low-base consolidation prior to breakout.",
        ],
        disclaimer="Cumulative OBV slope acceleration detector.",
        meta=create_meta_header(source=f"IERL OBV Engine ({norm})"),
    )
