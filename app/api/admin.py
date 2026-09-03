"""Admin API – observability endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.services.db import get_connection
import datetime

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

import hmac

def verify_admin_key(x_api_key: str = Header(...)):
    if not settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Admin API key not configured.")
    if not hmac.compare_digest(x_api_key, settings.ADMIN_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid admin API key.")
    return True

@router.get("/llm-usage", dependencies=[Depends(verify_admin_key)])
def get_llm_usage():
    conn = get_connection()
    now = datetime.datetime.now(datetime.timezone.utc)
    start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    day_rows = conn.execute(
        "SELECT SUM(token_count) as tokens, SUM(estimated_cost) as cost FROM llm_usage WHERE timestamp >= ?",
        (start_day.isoformat(),)
    ).fetchone()
    month_rows = conn.execute(
        "SELECT SUM(token_count) as tokens, SUM(estimated_cost) as cost FROM llm_usage WHERE timestamp >= ?",
        (start_month.isoformat(),)
    ).fetchone()
    conn.close()
    return {
        "daily": {"tokens": day_rows["tokens"] or 0, "estimated_cost": round(day_rows["cost"] or 0, 4)},
        "monthly": {"tokens": month_rows["tokens"] or 0, "estimated_cost": round(month_rows["cost"] or 0, 4)},
    }

# Simple in‑memory rolling request counters (reset every hour)
_request_counters = {"total": 0, "errors": 0}
_last_reset = datetime.datetime.now(datetime.timezone.utc)

def _reset_counters_if_needed():
    global _request_counters, _last_reset
    now = datetime.datetime.now(datetime.timezone.utc)
    if (now - _last_reset).total_seconds() >= 3600:
        _request_counters = {"total": 0, "errors": 0}
        _last_reset = now

@router.get("/request-stats", dependencies=[Depends(verify_admin_key)])
def get_request_stats():
    _reset_counters_if_needed()
    return _request_counters

@router.post("/sync-market-data", dependencies=[Depends(verify_admin_key)], summary="Trigger On-Demand Market Data Refresh (Max 72h Gap Enforced)")
async def sync_market_data(max_age_hours: int = 72):
    """Triggers an on-demand market data freshness scan across universe symbols."""
    try:
        from app.services.market_data import AutoRefreshMarketDataService
        result = await AutoRefreshMarketDataService.auto_refresh_universe(max_age_hours=max_age_hours)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market data sync failed: {str(e)}")


# Middleware to increment counters – will be added in main.py
