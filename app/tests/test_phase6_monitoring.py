"""Unit and integration tests for Phase 6 Live Monitoring, Prediction Ledger, & Drift Detection.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.services.monitoring.prediction_ledger import PredictionLedgerService
from app.services.monitoring.drift_detector import DriftDetector


@pytest.fixture
def temp_db_path(tmp_path):
    db_file = tmp_path / "test_phase6.sqlite"
    original = settings.DATA_STORE_PATH
    settings.DATA_STORE_PATH = str(db_file)
    from app.services.db import _ensure_tables
    _ensure_tables()
    yield str(db_file)
    settings.DATA_STORE_PATH = original


def test_prediction_ledger_flow(temp_db_path):
    ledger = PredictionLedgerService()
    pred = ledger.log_prediction(
        symbol="TCS",
        score=88,
        verdict="Buy",
        confidence="Confirmed",
        thesis="Strong AI & Cloud backlog growth",
        reference_price=3850.0,
    )
    assert pred.id is not None
    assert pred.symbol == "TCS.NS"
    assert pred.score == 88

    outcome = ledger.record_outcome(
        prediction_id=pred.id,
        symbol="TCS",
        horizon_months=12,
        actual_return_pct=24.5,
        benchmark_return_pct=10.0,
    )
    assert outcome.prediction_id == pred.id
    assert outcome.excess_return_pct == 14.5
    assert outcome.outcome_class == "CONFIRMED_OUTPERFORMANCE"

    history = ledger.get_prediction_history("TCS")
    assert len(history) == 1
    assert history[0].score == 88


def test_drift_detector(temp_db_path):
    ledger = PredictionLedgerService()
    pred = ledger.log_prediction("INFY", 92, "Buy", "Confirmed", "Digital transformation catalyst")
    ledger.record_outcome(pred.id, "INFY", 12, 28.0, 10.0)

    detector = DriftDetector()
    report = detector.evaluate_drift()
    assert report.total_predictions_evaluated == 1
    assert report.rolling_30d_accuracy_pct == 100.0
    assert report.high_score_decay_detected is False
    assert report.drift_alert_level == "GREEN"


def test_monitoring_api_endpoints(temp_db_path):
    client = TestClient(app)

    # 1. Test POST /api/v1/monitoring/prediction-ledger
    post_res = client.post(
        "/api/v1/monitoring/prediction-ledger",
        json={
            "symbol": "RELIANCE",
            "score": 90,
            "verdict": "Buy",
            "confidence": "Confirmed",
            "thesis": "Retail & Telecom margin expansion",
        },
    )
    assert post_res.status_code == 201
    data = post_res.json()
    assert data["symbol"] == "RELIANCE.NS"
    pred_id = data["id"]

    # 2. Test POST /api/v1/monitoring/outcome
    out_res = client.post(
        "/api/v1/monitoring/outcome",
        json={
            "prediction_id": pred_id,
            "symbol": "RELIANCE",
            "horizon_months": 12,
            "actual_return_pct": 32.0,
            "benchmark_return_pct": 12.0,
        },
    )
    assert out_res.status_code == 201
    assert out_res.json()["excess_return_pct"] == 20.0

    # 3. Test GET /api/v1/monitoring/prediction-ledger
    get_res = client.get("/api/v1/monitoring/prediction-ledger?symbol=RELIANCE")
    assert get_res.status_code == 200
    assert len(get_res.json()) == 1

    # 4. Test GET /api/v1/monitoring/drift
    drift_res = client.get("/api/v1/monitoring/drift")
    assert drift_res.status_code == 200
    assert drift_res.json()["drift_alert_level"] == "GREEN"

    # 5. Test GET /api/v1/monitoring/strategy-health
    health_res = client.get("/api/v1/monitoring/strategy-health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "HEALTHY"
