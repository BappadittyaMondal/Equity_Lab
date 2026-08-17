from fastapi import APIRouter, HTTPException
from app.services.decision_brain import Arbiter
from app.models.schemas import ConvictionCall

router = APIRouter(prefix="/api/v1/decision", tags=["Decision"])

@router.get("/{symbol}", response_model=ConvictionCall)
def get_decision(symbol: str):
    arbiter = Arbiter()
    try:
        return arbiter.arbitrate(symbol)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
