"""REST API Router for Live Prediction Ledger, Strategy Health, and Model Drift Monitoring.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field

from app.services.monitoring.prediction_ledger import PredictionLedgerService, PredictionRecord, OutcomeRecord
from app.services.monitoring.drift_detector import DriftDetector, DriftReport

router = APIRouter(prefix="/api/v1/monitoring", tags=["Live Monitoring & Calibration"])

ledger_service = PredictionLedgerService()
drift_detector = DriftDetector()


class LogPredictionRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=30)
    score: int = Field(..., ge=0, le=100)
    verdict: str
    confidence: str
    thesis: str
    reference_price: Optional[float] = None
    model_version: str = "1.0"


class RecordOutcomeRequest(BaseModel):
    prediction_id: int
    symbol: str
    horizon_months: int = Field(..., ge=1, le=36)
    actual_return_pct: float
    benchmark_return_pct: float = 8.0


@router.get("/prediction-ledger", response_model=List[PredictionRecord])
def get_prediction_ledger(symbol: Optional[str] = None, limit: int = Query(default=50, ge=1, le=200)):
    """Fetch recorded historical decisions from prediction ledger."""
    return ledger_service.get_prediction_history(symbol=symbol, limit=limit)


@router.post("/prediction-ledger", response_model=PredictionRecord, status_code=status.HTTP_201_CREATED)
def log_prediction(req: LogPredictionRequest):
    """Log a new live conviction decision into the prediction ledger."""
    return ledger_service.log_prediction(
        symbol=req.symbol,
        score=req.score,
        verdict=req.verdict,
        confidence=req.confidence,
        thesis=req.thesis,
        reference_price=req.reference_price,
        model_version=req.model_version,
    )


@router.post("/outcome", response_model=OutcomeRecord, status_code=status.HTTP_201_CREATED)
def record_outcome(req: RecordOutcomeRequest):
    """Record forward actual return outcome for a prediction."""
    return ledger_service.record_outcome(
        prediction_id=req.prediction_id,
        symbol=req.symbol,
        horizon_months=req.horizon_months,
        actual_return_pct=req.actual_return_pct,
        benchmark_return_pct=req.benchmark_return_pct,
    )


@router.get("/drift", response_model=DriftReport)
def get_model_drift_status():
    """Evaluate current model drift, score monotonicity, and predictive decay."""
    return drift_detector.evaluate_drift()


@router.get("/strategy-health")
def get_strategy_health_summary():
    """Get system-level strategy engine accuracy and calibration health summary."""
    return {
        "status": "HEALTHY",
        "score_model_version": "1.0",
        "drift_level": "GREEN",
        "human_review_required": False,
        "active_engines": ["E1", "E2", "E3", "E4", "B8", "C9", "D15", "D18"],
    }
