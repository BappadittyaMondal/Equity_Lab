"""Daily Price Ingester — Stores OHLCV into market_daily_snapshots.

Fetches daily OHLCV data from yfinance and stores it in the
ResearchDataStore's market_daily_snapshots table for use by
technical analysis engines.
"""

import logging
import pandas as pd
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.research_data import ResearchDataStore
from app.services.market_data import normalize_symbol, get_history
from app.services.utils.data_sanitizer import DataSanitizer

logger = logging.getLogger(__name__)


class DailyPriceIngester:
    """Ingests daily OHLCV price data into market_daily_snapshots."""

    def __init__(self, store: Optional[ResearchDataStore] = None):
        self.store = store or ResearchDataStore()

    def ingest_symbol(self, symbol: str, period: str = "3y") -> Dict[str, Any]:
        """Ingest daily price data for a symbol over given period.

        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
            period: Data period (e.g., "1y", "2y", "3y", "5y")

        Returns:
            Summary dict with ingestion counts.
        """
        norm = normalize_symbol(symbol)
        ticker_str = norm if norm.endswith(".NS") else norm + ".NS"

        result = {
            "symbol": ticker_str.replace(".NS", ""),
            "snapshots_ingested": 0,
            "errors": [],
        }

        # Ensure company record exists
        try:
            self.store.upsert_company({
                "symbol": ticker_str,
                "company_name": ticker_str.replace(".NS", ""),
                "legal_name": ticker_str.replace(".NS", ""),
                "sector": "",
            })
        except Exception:
            pass

        try:
            hist = get_history(norm, period=period, interval="1d")
            if hist is None or hist.empty:
                result["errors"].append(f"No historical data returned for {norm}")
                return result
        except Exception as e:
            result["errors"].append(f"History fetch failed: {e}")
            return result

        now_iso = datetime.now(timezone.utc).isoformat()

        # Outlier screening: Invoke DataSanitizer MAD (Median Absolute Deviation > 4.0) filter
        outlier_indices = set()
        if len(hist) >= 5 and "Close" in hist.columns:
            try:
                closes = hist["Close"].astype(float).tolist()
                flags = DataSanitizer.calculate_mad_outliers(closes, threshold=4.0)
                outlier_indices = {idx for idx, is_out in zip(hist.index, flags) if is_out}
            except Exception:
                outlier_indices = set()

        for idx, row in hist.iterrows():
            try:
                if idx in outlier_indices:
                    logger.warning("MAD price outlier spike detected for %s on %s — skipping row", norm, idx)
                    continue

                open_val = row.get("Open")
                high_val = row.get("High")
                low_val = row.get("Low")
                close_val = row.get("Close")

                # Guard against NaN / None / corrupted zero price entries
                if any(v is None or pd.isna(v) or float(v) <= 0.0 for v in [open_val, high_val, low_val, close_val]):
                    logger.warning("Null or invalid OHLC for %s on %s — skipping row", norm, idx)
                    continue

                # DEF-001: Guard against inverted High/Low
                if float(high_val) < float(low_val):
                    logger.warning("Inverted High/Low for %s on %s (H=%s, L=%s) — skipping row", norm, idx, high_val, low_val)
                    continue

                trading_date = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)[:10]
                vol_val = row.get("Volume", 0)
                vol_int = int(vol_val) if (vol_val is not None and not pd.isna(vol_val)) else 0

                self.store.add_market_daily_snapshot({
                    "symbol": ticker_str,
                    "trading_date": trading_date,
                    "open_price": float(open_val),
                    "high_price": float(high_val),
                    "low_price": float(low_val),
                    "close_price": float(close_val),
                    "volume": vol_int,
                    "delivery_volume": None,
                    "delivery_pct": None,
                    "market_cap": None,
                    "published_at": now_iso,
                    "source_name": "yfinance",
                    "source_url": f"https://finance.yahoo.com/quote/{norm}/history/",
                })
                result["snapshots_ingested"] += 1
            except Exception as e:
                logger.debug("Daily snapshot store error for %s on %s: %s", norm, idx, e)

        logger.info("Ingested %d daily snapshots for %s", result["snapshots_ingested"], norm)
        return result

    @staticmethod
    def check_adtv_liquidity_floor(df: pd.DataFrame, min_adtv_inr: float = 2500000.0) -> bool:
        """Verifies 20-day Average Daily Turnover Volume (ADTV_20d) >= ₹2,500,000."""
        if df is None or len(df) < 20:
            return False
        tail_20 = df.tail(20)
        daily_turnover = tail_20["Close"] * tail_20["Volume"]
        adtv_20d = float(daily_turnover.mean())
        return adtv_20d >= min_adtv_inr

    @staticmethod
    def compute_vpvr_vacuum_ratio(df: pd.DataFrame, num_bins: int = 50) -> float:
        """Computes VPVR Volume Profile Overhead Vacuum Ratio (SVR_VPVR)."""
        import numpy as np
        if df is None or len(df) < 52:
            return 1.0
            
        close = df["Close"].values
        volume = df["Volume"].values
        
        breakout_price = close[-1]
        p_min = np.min(close[-252:]) if len(close) >= 252 else np.min(close)
        
        if breakout_price <= p_min or breakout_price <= 0:
            return 1.0
            
        bins = np.linspace(p_min, breakout_price * 1.5, num_bins + 1)
        hist_vol, _ = np.histogram(close, bins=bins, weights=volume)
        
        # Split bins into base region (p_min -> breakout) vs overhead region (breakout -> 1.5x)
        idx_breakout = np.digitize(breakout_price, bins) - 1
        vol_base = np.sum(hist_vol[:max(1, idx_breakout)])
        vol_overhead = np.sum(hist_vol[max(1, idx_breakout):])
        
        if vol_base <= 0:
            return 1.0
            
        return float(vol_overhead / vol_base)

