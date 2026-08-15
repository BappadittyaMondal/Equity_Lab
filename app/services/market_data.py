"""Market data service providing quote retrieval, history fetching, and regime analysis.

Enforces provider abstraction, metadata tracking, IST timestamps, caching, and explicit HTTP 503 errors on upstream failure (never fabricates static mock data).
"""

import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, Optional, List
from fastapi import HTTPException, status
import yfinance as yf
import pandas as pd
from app.models.schemas import MetaHeader, TickerQuoteResponse, MarketRegimeResponse

# Simple in-memory cache: (key) -> (data, expire_timestamp)
_CACHE: Dict[str, Tuple[Any, float]] = {}
CACHE_TTL_SECONDS = 60

IST = timezone(timedelta(hours=5, minutes=30))


def get_ist_now_str() -> str:
    """Returns current ISO 8601 timestamp in IST (+05:30)."""
    return datetime.now(IST).isoformat()


def create_meta_header(source: str = "yfinance (NSE)", Limitations: Optional[List[str]] = None) -> MetaHeader:
    now_str = get_ist_now_str()
    return MetaHeader(
        source=source,
        as_of=now_str,
        retrieved_at=now_str,
        market_data_type="delayed",
        stale=False,
        limitations=Limitations or [
            "Data is subject to exchange delay (typically 15 minutes for NSE/BSE).",
            "Not for direct order routing or automated execution."
        ]
    )


def normalize_symbol(symbol: str) -> str:
    """Normalizes raw input symbol into standard yfinance format for Indian equities & indices."""
    if not symbol:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Symbol cannot be empty.")
    
    clean = symbol.strip().upper()
    
    # Indices mapping
    index_map = {
        "NIFTY": "^NSEI",
        "NIFTY 50": "^NSEI",
        "NIFTY50": "^NSEI",
        "^NSEI": "^NSEI",
        "SENSEX": "^BSESN",
        "^BSESN": "^BSESN",
        "BANKNIFTY": "^NSEBANK",
        "NIFTY BANK": "^NSEBANK",
        "^NSEBANK": "^NSEBANK",
        "INDIAVIX": "^INDIAVIX",
        "INDIA VIX": "^INDIAVIX",
        "VIX": "^INDIAVIX",
        "^INDIAVIX": "^INDIAVIX",
    }
    
    if clean in index_map:
        return index_map[clean]
        
    if clean.startswith("^"):
        return clean
        
    if clean.endswith(".NS") or clean.endswith(".BO"):
        return clean
        
    return f"{clean}.NS"


def get_cached_item(cache_key: str) -> Optional[Any]:
    if cache_key in _CACHE:
        data, expires_at = _CACHE[cache_key]
        if time.time() < expires_at:
            return data
        del _CACHE[cache_key]
    return None


def set_cached_item(cache_key: str, data: Any, ttl: int = CACHE_TTL_SECONDS):
    _CACHE[cache_key] = (data, time.time() + ttl)


def get_quote(symbol: str) -> TickerQuoteResponse:
    """Fetches real-time quote for symbol. Raises HTTP 503 if provider fails."""
    normalized = normalize_symbol(symbol)
    cache_key = f"quote:{normalized}"
    cached = get_cached_item(cache_key)
    if cached:
        return cached

    try:
        t = yf.Ticker(normalized)
        # Fetch history to get reliable recent prices
        hist = t.history(period="5d")
        if hist.empty:
            raise ValueError(f"No price history returned for symbol '{normalized}'")
            
        last_close = float(hist['Close'].iloc[-1])
        prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else last_close
        change = round(last_close - prev_close, 2)
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0.0

        info = t.info or {}
        high_52 = info.get("fiftyTwoWeekHigh") or float(hist['High'].max())
        low_52 = info.get("fiftyTwoWeekLow") or float(hist['Low'].min())
        mkt_cap = info.get("marketCap")
        pe = info.get("trailingPE")
        volume = info.get("volume") or int(hist['Volume'].iloc[-1]) if 'Volume' in hist else None

        exchange = "BSE" if normalized.endswith(".BO") or normalized == "^BSESN" else "NSE"
        
        response = TickerQuoteResponse(
            symbol=normalized,
            exchange=exchange,
            currency="INR",
            price=round(last_close, 2),
            previous_close=round(prev_close, 2),
            change=change,
            change_percent=change_pct,
            fifty_two_week_high=round(float(high_52), 2) if high_52 else None,
            fifty_two_week_low=round(float(low_52), 2) if low_52 else None,
            market_cap=float(mkt_cap) if mkt_cap else None,
            pe_ratio=round(float(pe), 2) if pe else None,
            volume=int(volume) if volume else None,
            meta=create_meta_header(source=f"yfinance ({exchange})")
        )
        
        set_cached_item(cache_key, response, ttl=60)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Market data provider error for symbol '{symbol}': {str(e)}"
        )


def get_history(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetches historical OHLCV data. Raises HTTP 503 if unavailable."""
    normalized = normalize_symbol(symbol)
    cache_key = f"hist:{normalized}:{period}:{interval}"
    cached = get_cached_item(cache_key)
    if cached is not None:
        return cached

    try:
        t = yf.Ticker(normalized)
        hist = t.history(period=period, interval=interval)
        if hist.empty:
            raise ValueError(f"No historical data returned for symbol '{normalized}'")
            
        set_cached_item(cache_key, hist, ttl=300)
        return hist
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to retrieve historical data for '{symbol}': {str(e)}"
        )


def get_market_regime() -> MarketRegimeResponse:
    """Evaluates live market regime based on India VIX and NIFTY 50.
    
    CRITICAL RULE: Never returns static default values on failure. Raises 503 if upstream fails.
    """
    cache_key = "regime:live"
    cached = get_cached_item(cache_key)
    if cached:
        return cached

    try:
        vix_ticker = yf.Ticker("^INDIAVIX")
        vix_hist = vix_ticker.history(period="5d")
        if vix_hist.empty:
            raise ValueError("India VIX data feed returned empty dataframe")
            
        vix_val = round(float(vix_hist['Close'].iloc[-1]), 2)
        
        nifty_quote = get_quote("^NSEI")
        nifty_spot = nifty_quote.price

        # Evaluate regime rules
        if vix_val < 13.0:
            regime = "Low Volatility (<13)"
            score = 65
            suitability = "COMPRESSED"
            obs = f"India VIX is {vix_val} (<13). Option premiums compressed. Yield for A2/A3 range selling reduced."
        elif 13.0 <= vix_val <= 20.0:
            regime = "Normal Volatility (13-20)"
            score = 85
            suitability = "OPTIMAL"
            obs = f"India VIX is {vix_val} (13-20). Optimal range for 0-DTE A2 option selling. Volatility balanced."
        elif 20.0 < vix_val <= 25.0:
            regime = "Elevated Volatility (20-25)"
            score = 50
            suitability = "CAUTION"
            obs = f"India VIX is {vix_val} (20-25). High premium environment. Apply wider strike buffers (+250 pt) and reduce position sizing."
        else:
            regime = "HARD STOP Volatility (>25)"
            score = 20
            suitability = "SUSPEND"
            obs = f"India VIX is {vix_val} (>25). Extreme volatility spike. Hard Stop triggered: suspend option selling."

        response = MarketRegimeResponse(
            vix_level=vix_val,
            regime=regime,
            score=score,
            a2_suitability=suitability,
            observation=obs,
            nifty_spot=nifty_spot,
            meta=create_meta_header(source="yfinance (^INDIAVIX, ^NSEI)")
        )

        set_cached_item(cache_key, response, ttl=60)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Live regime market data stream unavailable: {str(e)}"
        )


def get_ticker_strip_quotes() -> List[TickerQuoteResponse]:
    """Fetches benchmark quotes for frontend ticker tape."""
    symbols = ["^NSEI", "^BSESN", "^NSEBANK", "^INDIAVIX", "RELIANCE.NS", "TCS.NS", "INFY.NS"]
    quotes = []
    for s in symbols:
        try:
            q = get_quote(s)
            quotes.append(q)
        except Exception:
            pass  # omit failed symbol, do not crash whole strip
    return quotes


def calculate_corporate_action_adjustment_factors(corporate_actions: List[Any]) -> Dict[str, float]:
    """Calculates cumulative price adjustment multipliers for historical corporate actions.
    
    Split N:D (e.g. 5:1 split): factor multiplier = ratio_denominator / ratio_numerator = 1/5.
    Bonus N:D (e.g. 1:2 bonus): factor multiplier = ratio_denominator / (ratio_denominator + ratio_numerator) = 2/3.
    """
    cumulative_factor = 1.0
    action_factors = {}
    
    for action in sorted(corporate_actions, key=lambda x: getattr(x, 'ex_date', ''), reverse=True):
        act_type = getattr(action, 'action_type', '')
        num = getattr(action, 'ratio_numerator', None)
        den = getattr(action, 'ratio_denominator', None)
        ex_date_str = str(getattr(action, 'ex_date', ''))
        
        factor = 1.0
        if act_type == "split" and num and den and num > 0 and den > 0:
            factor = den / num
        elif act_type == "bonus" and num and den and num > 0 and den > 0:
            factor = den / (den + num)
            
        cumulative_factor *= factor
        action_factors[ex_date_str] = cumulative_factor
        
    return action_factors


def adjust_price_series(df: pd.DataFrame, corporate_actions: List[Any]) -> pd.DataFrame:
    """Adjusts historical OHLCV DataFrame using point-in-time corporate action ex-dates.
    
    Prices prior to ex_date are multiplied by cumulative adjustment factor.
    Volumes prior to ex_date are divided by cumulative adjustment factor.
    """
    if df.empty or not corporate_actions:
        return df
        
    adjusted_df = df.copy()
    action_factors = calculate_corporate_action_adjustment_factors(corporate_actions)
    
    for ex_date_str, factor in action_factors.items():
        if factor == 1.0:
            continue
        try:
            ex_dt = pd.to_datetime(ex_date_str).tz_localize(df.index.tz if hasattr(df.index, 'tz') else None)
            mask = adjusted_df.index < ex_dt
            for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
                if col in adjusted_df.columns:
                    adjusted_df.loc[mask, col] = adjusted_df.loc[mask, col] * factor
            if 'Volume' in adjusted_df.columns:
                adjusted_df.loc[mask, 'Volume'] = (adjusted_df.loc[mask, 'Volume'] / factor).astype(int)
        except Exception:
            continue
            
    return adjusted_df

