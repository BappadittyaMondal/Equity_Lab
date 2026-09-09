"""FastAPI Router for E20 Institutional Turnaround Prediction Framework.

Exposes single-stock turnaround scorecards, 2-layer probability estimates,
relapse risk metrics, and universe turnaround rankings.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models.schemas import StrategyRunResponse
from app.services.turnaround.turnaround_engine import run_turnaround_engine
from app.services.strategies.turnaround_stage import evaluate_turnaround_stage

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
    res_e20 = run_turnaround_engine(symbol)
    e20_stage = res_e20.results.get("turnaround_stage", "UNKNOWN")
    stage_desc = res_e20.results.get("capital_structure_warning", "")
    
    # Also evaluate E2 stage classification for full diagnostic parity
    try:
        res_e2 = evaluate_turnaround_stage(symbol)
        e2_stage = res_e2.current_stage
        e2_desc = res_e2.stage_description
        prob_success = res_e2.success_probability_pct
        false_risk = res_e2.false_turnaround_risk
    except Exception:
        e2_stage = e20_stage
        e2_desc = stage_desc
        prob_success = res_e20.metrics.get("p_recovery", 0.0) * 100.0
        false_risk = "MODERATE"

    return {
        "symbol": symbol.upper(),
        "stage": e2_stage or e20_stage,
        "stage_description": e2_desc or stage_desc,
        "e20_stage": e20_stage,
        "success_probability_pct": prob_success,
        "false_turnaround_risk": false_risk,
        "lifecycle": res_e20.results.get("lifecycle_state", {}),
        "is_relapse_active": res_e20.results.get("is_relapse_active", False)
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
def rank_turnaround_universe(
    min_score: float = Query(50.0),
    universe: str = Query("NIFTY50", description="Universe identifier: NIFTY50, MEGA_CAP, or ALL"),
    limit: int = Query(50, ge=1, le=500)
):
    """Ranks universe candidates for turnarounds using E20 engine."""
    from app.services.ingestion.universe_discovery import get_universe_symbols
    symbols = get_universe_symbols(universe)[:limit]
    rankings = []
    for sym in symbols:
        resp = run_turnaround_engine(sym)
        if resp.metrics.get("turnaround_score", 0.0) >= min_score:
            rankings.append(resp.results)
    
    return {
        "total_candidates": len(rankings),
        "min_score_filter": min_score,
        "universe": universe,
        "rankings": sorted(rankings, key=lambda x: x.get("turnaround_score", 0.0), reverse=True)
    }

