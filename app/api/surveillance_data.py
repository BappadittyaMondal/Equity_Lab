"""Protected endpoints for pushing and fetching surveillance data."""

import hmac
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Header, HTTPException, status
from app.core.config import settings
from app.services.data_ingestion.surveillance_resolver import SurveillanceResolver

router = APIRouter(prefix="/api/v1/data/surveillance", tags=["Surveillance Data"])

class SurveillanceRecord(BaseModel):
    symbol: str
    asm_stage: str = 'CLEAN'
    gsm_stage: str = 'CLEAN'
    esm_stage: str = 'CLEAN'
    t2t_flag: bool = False
    fo_ban_flag: bool = False
    circuit_band_pct: float = 20.0

@router.post("")
def bulk_update_surveillance(
    records: List[SurveillanceRecord],
    x_api_key: str = Header(...)
):
    if not settings.DATA_WRITE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data ingestion is disabled (DATA_WRITE_API_KEY not configured)"
        )
    
    # Safe constant-time comparison
    if not hmac.compare_digest(x_api_key, settings.DATA_WRITE_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid DATA_WRITE_API_KEY"
        )
    
    count = SurveillanceResolver.bulk_update([r.model_dump() for r in records])
    return {"status": "success", "updated_count": count}

@router.get("/flagged")
def get_flagged_surveillance():
    return SurveillanceResolver.get_all_flagged()

@router.get("/{symbol}")
def get_surveillance(symbol: str):
    return SurveillanceResolver.resolve(symbol)
