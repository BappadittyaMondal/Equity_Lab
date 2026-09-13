from fastapi import APIRouter, HTTPException
from app.services.decision_brain import Arbiter
from app.models.schemas import ConvictionCall

router = APIRouter(prefix="/api/v1/decision", tags=["Decision"])

from typing import Optional
from datetime import datetime

@router.get("/{symbol}", response_model=ConvictionCall)
def get_decision(
    symbol: str,
    objective: str = "GENERAL",
    as_of: Optional[str] = None,
    query: Optional[str] = None,
):
    arbiter = Arbiter()
    try:
        as_of_dt = None
        if as_of:
            try:
                import pandas as pd
                as_of_dt = pd.to_datetime(as_of).to_pydatetime()
            except Exception:
                pass
        return arbiter.arbitrate(symbol, as_of=as_of_dt, objective=objective, query=query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

