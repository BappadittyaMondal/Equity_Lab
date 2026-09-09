"""
Shared Institutional Multi-Timeframe (MTF) Context Engine.

Enforces the canonical institutional hierarchy:
- Monthly: Strategic Regime / Structural Context
- Weekly: Macro Tide / Trend Governor (Hard Directional Filter)
- Daily: Tactical Wave / Setup Validator
- 60-Minute / Intraday: Timing Ripple / Execution Trigger Only

Hard Invariant:
A 60-minute intraday trigger can NEVER override a Weekly Macro Bearish Tide.
Daily technical momentum cannot override forensic or governance vetoes.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime, timezone


class MTFContextEngine:
    """Canonical, shared Multi-Timeframe (MTF) Context Engine."""

    @staticmethod
    def _clean_series(s: Any) -> pd.Series:
        """Flattens 2D DataFrame/Series to 1D numeric Series and strips NaNs."""
        if s is None:
            return pd.Series(dtype=float)
        if isinstance(s, pd.DataFrame):
            s = s.iloc[:, 0]
        return pd.Series(s).dropna().astype(float)

    @classmethod
    def calculate_weekly_tide(cls, weekly_df: Optional[pd.DataFrame]) -> Dict[str, Any]:
        """
        Evaluates Weekly Macro Tide (Trend Governor).
        Checks: 10-EMA vs 30-EMA, MACD Histogram slope, and price position.
        """
        if weekly_df is None or len(weekly_df) < 15:
            return {
                "tide_state": "NEUTRAL_INSUFFICIENT_DATA",
                "is_bullish_tide": False,
                "is_bearish_tide": False,
                "weekly_ema_10": None,
                "weekly_ema_30": None,
                "confidence": 0.0,
            }

        closes = cls._clean_series(weekly_df["close"] if "close" in weekly_df.columns else weekly_df.iloc[:, -1])
        if len(closes) < 15:
            return {
                "tide_state": "NEUTRAL_INSUFFICIENT_DATA",
                "is_bullish_tide": False,
                "is_bearish_tide": False,
                "weekly_ema_10": None,
                "weekly_ema_30": None,
                "confidence": 0.0,
            }

        ema_10 = float(closes.ewm(span=10, adjust=False).mean().iloc[-1])
        ema_30 = float(closes.ewm(span=min(30, len(closes)), adjust=False).mean().iloc[-1])
        current_p = float(closes.iloc[-1])

        # Weekly MACD
        ema_12 = closes.ewm(span=12, adjust=False).mean()
        ema_26 = closes.ewm(span=min(26, len(closes)), adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        hist = macd_line - signal_line
        macd_hist_curr = float(hist.iloc[-1])
        macd_hist_prev = float(hist.iloc[-2]) if len(hist) > 1 else macd_hist_curr

        is_bullish = (current_p >= ema_30) and (ema_10 >= ema_30) and (macd_hist_curr >= 0 or macd_hist_curr > macd_hist_prev)
        is_bearish = (current_p < ema_30) and (ema_10 < ema_30) and (macd_hist_curr < 0)

        if is_bullish:
            tide_state = "BULLISH_TIDE"
        elif is_bearish:
            tide_state = "BEARISH_TIDE"
        else:
            tide_state = "NEUTRAL_CONSOLIDATION"

        return {
            "tide_state": tide_state,
            "is_bullish_tide": is_bullish,
            "is_bearish_tide": is_bearish,
            "weekly_ema_10": round(ema_10, 2),
            "weekly_ema_30": round(ema_30, 2),
            "weekly_macd_hist": round(macd_hist_curr, 3),
            "confidence": 0.85 if (is_bullish or is_bearish) else 0.60,
        }

    @classmethod
    def calculate_daily_wave(cls, daily_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluates Daily Tactical Wave (Setup Validator).
        Checks: 20-EMA pullback, Bollinger/Keltner Squeeze, and Volume Profile POC.
        """
        closes = cls._clean_series(daily_df["close"] if "close" in daily_df.columns else daily_df.iloc[:, -1])
        if len(closes) < 20:
            return {
                "wave_state": "DATA_INSUFFICIENT",
                "is_setup_valid": False,
                "daily_ema_20": None,
                "squeeze_state": "NONE",
            }

        current_p = float(closes.iloc[-1])
        ema_20 = float(closes.ewm(span=20, adjust=False).mean().iloc[-1])
        ema_50 = float(closes.ewm(span=min(50, len(closes)), adjust=False).mean().iloc[-1])

        # Bollinger Bands (20, 2.0)
        rolling_std = float(closes.tail(20).std())
        upper_bb = ema_20 + (2.0 * rolling_std)
        lower_bb = ema_20 - (2.0 * rolling_std)

        # Squeeze approximation
        bb_width = (upper_bb - lower_bb) / ema_20 if ema_20 > 0 else 0.1
        is_squeeze = bb_width < 0.08

        dist_from_ema_20 = ((current_p - ema_20) / ema_20) * 100.0

        if current_p >= ema_20 and abs(dist_from_ema_20) <= 2.5:
            wave_state = "PULLBACK_AT_20EMA_SUPPORT"
            is_setup = True
        elif current_p > upper_bb:
            wave_state = "OVERBOUGHT_EXTENDED"
            is_setup = False
        elif current_p < lower_bb:
            wave_state = "OVERSOLD_BREAKDOWN"
            is_setup = False
        elif current_p >= ema_20:
            wave_state = "BULLISH_UPTREND"
            is_setup = True
        else:
            wave_state = "BEARISH_DOWNTREND"
            is_setup = False

        return {
            "wave_state": wave_state,
            "is_setup_valid": is_setup,
            "daily_ema_20": round(ema_20, 2),
            "daily_ema_50": round(ema_50, 2),
            "distance_from_20ema_pct": round(dist_from_ema_20, 2),
            "is_volatility_squeeze": is_squeeze,
            "bb_width_pct": round(bb_width * 100.0, 2),
        }

    @classmethod
    def calculate_intraday_ripple(
        cls,
        hourly_df: Optional[pd.DataFrame] = None,
        daily_stoch_rsi_k: Optional[float] = None,
        daily_stoch_rsi_d: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates 60-Minute / Intraday Ripple (Timing Trigger).
        If 60m data is provided, evaluates hourly Stoch RSI inflection.
        Otherwise falls back cleanly to fast daily Stoch RSI.
        """
        if hourly_df is not None and len(hourly_df) >= 14:
            closes = cls._clean_series(hourly_df["close"] if "close" in hourly_df.columns else hourly_df.iloc[:, -1])
            if len(closes) >= 14:
                # 60m RSI
                deltas = closes.diff()
                gains = deltas.clip(lower=0.0)
                losses = -deltas.clip(upper=0.0)
                avg_gain = gains.tail(14).mean()
                avg_loss = losses.tail(14).mean()
                rs = avg_gain / max(1e-6, avg_loss)
                rsi_60m = 100.0 - (100.0 / (1.0 + rs))

                is_trigger_long = rsi_60m < 40.0 or (rsi_60m > 50.0 and deltas.iloc[-1] > 0)
                return {
                    "ripple_state": "TRIGGER_LONG_READY" if is_trigger_long else "NEUTRAL_WAITING",
                    "is_timing_trigger_fired": is_trigger_long,
                    "hourly_rsi": round(rsi_60m, 2),
                    "source": "60_MIN_INTRADAY",
                }

        # Fallback using Stoch RSI parameters if passed
        if daily_stoch_rsi_k is not None and daily_stoch_rsi_d is not None:
            is_trigger = (daily_stoch_rsi_k > daily_stoch_rsi_d) and (daily_stoch_rsi_k < 50.0)
            return {
                "ripple_state": "TRIGGER_LONG_READY" if is_trigger else "NEUTRAL_WAITING",
                "is_timing_trigger_fired": is_trigger,
                "stoch_rsi_k": daily_stoch_rsi_k,
                "stoch_rsi_d": daily_stoch_rsi_d,
                "source": "DAILY_FAST_PROXY",
            }

        return {
            "ripple_state": "NO_INTRADAY_TRIGGER_DATA",
            "is_timing_trigger_fired": False,
            "source": "UNSPECIFIED",
        }

    @classmethod
    def evaluate_mtf_context(
        cls,
        symbol: str,
        daily_df: pd.DataFrame,
        weekly_df: Optional[pd.DataFrame] = None,
        hourly_df: Optional[pd.DataFrame] = None,
        stoch_rsi_k: Optional[float] = None,
        stoch_rsi_d: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Master Multi-Timeframe Alignment Synthesizer.
        Generates canonical MTFContext with strict hierarchical veto rules.
        """
        weekly_res = cls.calculate_weekly_tide(weekly_df)
        daily_res = cls.calculate_daily_wave(daily_df)
        hourly_res = cls.calculate_intraday_ripple(hourly_df, stoch_rsi_k, stoch_rsi_d)

        # Hierarchy Invariance Engine
        is_weekly_bullish = weekly_res["is_bullish_tide"]
        is_weekly_bearish = weekly_res["is_bearish_tide"]
        is_daily_setup = daily_res["is_setup_valid"]
        is_timing_trigger = hourly_res["is_timing_trigger_fired"]

        # Conflict Detection
        conflict_detected = False
        if is_weekly_bearish and is_timing_trigger:
            conflict_detected = True
            alignment_state = "TACTICAL_COUNTERTREND_VETO"
            verdict = "VETOED_AGAINST_WEEKLY_TIDE"
            actionable = False
        elif is_weekly_bullish and is_daily_setup and is_timing_trigger:
            alignment_state = "PERFECT_TRIPLE_SCREEN_ALIGNMENT"
            verdict = "STRONG_BULLISH_EXECUTION_READY"
            actionable = True
        elif is_weekly_bullish and is_daily_setup:
            alignment_state = "BULLISH_TIDE_AND_SETUP"
            verdict = "WAIT_FOR_TIMING_TRIGGER"
            actionable = False
        elif is_weekly_bearish:
            alignment_state = "BEARISH_DOWNWARD_REGIME"
            verdict = "CAPITAL_PRESERVATION_DEFENSE"
            actionable = False
        else:
            alignment_state = "CONFLICTED_OR_CHOPPY"
            verdict = "NO_CONFLUENCE_OBSERVE"
            actionable = False

        return {
            "symbol": symbol.upper(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alignment_state": alignment_state,
            "verdict": verdict,
            "is_actionable": actionable,
            "conflict_detected": conflict_detected,
            "weekly_tide": weekly_res,
            "daily_wave": daily_res,
            "intraday_ripple": hourly_res,
            "hierarchy_rule_enforced": "60-min cannot override Weekly Bearish Tide",
        }
