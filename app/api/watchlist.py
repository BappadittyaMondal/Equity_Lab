"""Watchlist management router.

Provides CRUD operations for user watchlist items with live market quote integration.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import WatchlistItemRequest, WatchlistItemResponse, WatchlistListResponse
from app.services.research_data import ResearchDataStore
from app.services.market_data import get_quote, normalize_symbol

router = APIRouter(prefix="/api/v1/watchlist", tags=["Watchlist"])
data_store = ResearchDataStore()


@router.get("", response_model=WatchlistListResponse)
def get_watchlist():
    """Retrieves all watchlist items enriched with live quote data."""
    raw_items = data_store.get_watchlist()
    enriched_items = []
    
    for item in raw_items:
        sym = item["symbol"]
        curr_price = None
        chg_pct = None
        pe = None
        
        try:
            quote = get_quote(sym)
            curr_price = quote.price
            chg_pct = quote.change_percent
            pe = quote.pe_ratio
        except Exception:
            pass

        enriched_items.append(
            WatchlistItemResponse(
                id=item["id"],
                symbol=sym,
                company_name=item.get("company_name") or sym,
                target_price=item.get("target_price") or 0.0,
                notes=item.get("notes") or "",
                added_at=item.get("added_at") or "",
                current_price=curr_price,
                change_percent=chg_pct,
                pe_ratio=pe
            )
        )

    return WatchlistListResponse(items=enriched_items, count=len(enriched_items))


@router.post("", response_model=WatchlistItemResponse)
def add_to_watchlist(req: WatchlistItemRequest):
    """Adds or updates a security in the user watchlist."""
    norm_symbol = normalize_symbol(req.symbol)
    saved = data_store.add_to_watchlist(
        symbol=norm_symbol,
        company_name=req.company_name or norm_symbol,
        target_price=req.target_price or 0.0,
        notes=req.notes or ""
    )
    
    curr_price = None
    chg_pct = None
    pe = None
    try:
        quote = get_quote(norm_symbol)
        curr_price = quote.price
        chg_pct = quote.change_percent
        pe = quote.pe_ratio
    except Exception:
        pass

    return WatchlistItemResponse(
        id=saved["id"],
        symbol=saved["symbol"],
        company_name=saved["company_name"],
        target_price=saved["target_price"],
        notes=saved["notes"],
        added_at=saved["added_at"],
        current_price=curr_price,
        change_percent=chg_pct,
        pe_ratio=pe
    )


@router.delete("/{symbol}")
def delete_from_watchlist(symbol: str):
    """Removes a security from the user watchlist."""
    norm_symbol = normalize_symbol(symbol)
    removed = data_store.remove_from_watchlist(norm_symbol)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symbol '{norm_symbol}' not found in watchlist."
        )
    return {"status": "SUCCESS", "message": f"Removed '{norm_symbol}' from watchlist."}
