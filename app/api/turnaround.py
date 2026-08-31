"""FastAPI Router for E20 Institutional Turnaround Prediction Framework.

Exposes single-stock turnaround scorecards, 2-layer probability estimates,
relapse risk metrics, and universe turnaround rankings.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models.schemas import StrategyRunResponse
from app.services.turnaround.turnaround_engine import run_turnaround_engine

router = APIRouter(prefix="/api/v1/turnaround", tags=["Turnaround Prediction Framework"])


@router.get("/{symbol}", response_model=StrategyRunResponse, summary="Get Single-Stock Turnaround Intelligence (E20)")
def get_turnaround_analysis(symbol: str, as_of: Optional[str] = Query(None)):
    """Runs 2-layer turnaround probability model, damage state detection, cash-flow truth, and FRMR expectation gap."""
    try:
        return run_turnaround_engine(symbol, as_of=as_of)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Turnaround evaluation failed for {symbol}: {str(e)}"
        )


from pydantic import BaseModel

class TurnaroundPredictionRequest(BaseModel):
    symbol: str

@router.post("/prediction", summary="Post Turnaround Prediction for Symbol")
def post_turnaround_prediction(req: TurnaroundPredictionRequest):
    """Runs E20 turnaround engine via POST payload."""
    try:
        res = run_turnaround_engine(req.symbol)
        return res.model_dump() if hasattr(res, "model_dump") else res.dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Turnaround prediction failed: {str(e)}"
        )


@router.get("/stage/{symbol}", summary="Get Turnaround Stage Details")
def get_turnaround_stage(symbol: str):
    """Get turnaround stage details for symbol."""
    res = run_turnaround_engine(symbol)
    return {
        "symbol": symbol.upper(),
        "stage": res.results.get("stage", "UNKNOWN"),
        "stage_description": res.results.get("stage_description", ""),
        "lifecycle": res.results.get("lifecycle_state", {})
    }


@router.get("/features/{symbol}", summary="Get Turnaround Feature Vector")
def get_turnaround_features(symbol: str):
    """Get calculated turnaround feature metrics."""
    res = run_turnaround_engine(symbol)
    return {
        "symbol": symbol.upper(),
        "metrics": res.metrics,
        "results": res.results
    }


@router.get("/transitions/{symbol}", summary="Get Turnaround Transition History")
def get_turnaround_transitions(symbol: str):
    """Get transition state history for symbol."""
    res = run_turnaround_engine(symbol)
    return {
        "symbol": symbol.upper(),
        "current_stage": res.results.get("stage", "UNKNOWN"),
        "transitions": res.results.get("lifecycle_state", {}).get("transition_history", [])
    }


@router.get("/rank/universe", summary="Rank Universe for Turnaround Opportunities")
def rank_turnaround_universe(min_score: float = Query(50.0)):
    """Ranks universe candidates for turnarounds using E20 engine."""
    symbols = ["RELIANCE", "TATAMOTORS", "SUZLON", "INFY", "TCS"]
    rankings = []
    for sym in symbols:
        resp = run_turnaround_engine(sym)
        if resp.metrics.get("turnaround_score", 0.0) >= min_score:
            rankings.append(resp.results)
    
    return {
        "total_candidates": len(rankings),
        "min_score_filter": min_score,
        "rankings": sorted(rankings, key=lambda x: x.get("turnaround_score", 0.0), reverse=True)
    }

