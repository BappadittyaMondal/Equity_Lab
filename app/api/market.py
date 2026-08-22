"""Market data router for quotes, regime analysis, and ticker tape streams.
"""

from typing import List
from fastapi import APIRouter
from app.models.schemas import TickerQuoteResponse, MarketRegimeResponse
from app.services.market_data import get_quote, get_market_regime, get_ticker_strip_quotes

router = APIRouter(prefix="/api/v1", tags=["Market Data"])


@router.get("/ticker/{symbol}", response_model=TickerQuoteResponse)
def fetch_ticker_quote(symbol: str):
    """Fetches real-time price & metrics for any NSE/BSE stock or index."""
    return get_quote(symbol)


@router.get("/regime", response_model=MarketRegimeResponse)
def fetch_market_regime():
    """Evaluates live India VIX and Nifty volatility regime."""
    return get_market_regime()


@router.get("/ticker-strip", response_model=List[TickerQuoteResponse])
def fetch_ticker_strip():
    """Fetches quotes for live ticker tape strip."""
    return get_ticker_strip_quotes()


@router.get("/ticker/{symbol}/history")
def fetch_ticker_history(symbol: str, period: str = "1y", interval: str = "1d"):
    """Fetches historical OHLCV data for charting."""
    from app.services.market_data import get_history, normalize_symbol
    norm_symbol = normalize_symbol(symbol)
    df = get_history(norm_symbol, period=period, interval=interval)
    if df.empty:
        return {"symbol": norm_symbol, "history": []}
    
    # Format records for charting
    records = []
    for idx, row in df.iterrows():
        dt_str = idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx)
        records.append({
            "date": dt_str,
            "open": round(float(row.get("Open", 0)), 2),
            "high": round(float(row.get("High", 0)), 2),
            "low": round(float(row.get("Low", 0)), 2),
            "close": round(float(row.get("Close", 0)), 2),
            "volume": int(row.get("Volume", 0))
        })
    return {"symbol": norm_symbol, "period": period, "history": records}


@router.get("/community/posts")
def fetch_community_posts():
    """Fetches community research notes and institutional discussion posts."""
    return {"posts": [], "count": 0, "status": "active"}


