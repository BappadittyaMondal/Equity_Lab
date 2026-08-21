"""Unit & Integration tests for Gap Closure Features: Scorecard, CAGR Matrix, and Swing Alerts."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.research.scorecard_service import generate_scorecard_for_symbol, generate_scorecard_matrix
from app.services.research.cagr_matrix_service import generate_cagr_sensitivity_matrix
from app.services.strategies.swing_alerts_service import get_swing_trade_alerts
from app.models.schemas import (
    ScorecardItemResponse,
    ScorecardMatrixResponse,
    CAGRSensitivityMatrixResponse,
    SwingTradeAlertsResponse,
)

client = TestClient(app)
AUTH_HEADERS = {"x-api-key": settings.API_KEY_SECRET or "dev-secret-key-12345"}


def test_scorecard_service_single_symbol():
    res = generate_scorecard_for_symbol("RELIANCE")
    assert isinstance(res, ScorecardItemResponse)
    assert "RELIANCE" in res.symbol
    assert res.scores.overall_score >= 0
    assert "10" in res.scores.business_quality
    assert res.horizon_probabilities.prob_1y != ""


def test_scorecard_matrix():
    res = generate_scorecard_matrix(["RELIANCE", "TCS"])
    assert isinstance(res, ScorecardMatrixResponse)
    assert res.count == 2
    assert len(res.items) == 2
    assert res.items[0].rank == 1


def test_cagr_sensitivity_matrix():
    res = generate_cagr_sensitivity_matrix("RELIANCE")
    assert isinstance(res, CAGRSensitivityMatrixResponse)
    assert "RELIANCE" in res.symbol
    assert len(res.scenario_matrix) == 5
    assert res.scenario_matrix[0].revenue_eps_cagr_pct == 10.0
    assert res.scenario_matrix[4].revenue_eps_cagr_pct == 30.0


def test_swing_trade_alerts_service():
    res = get_swing_trade_alerts(["RELIANCE", "TCS", "E2E"])
    assert isinstance(res, SwingTradeAlertsResponse)
    assert isinstance(res.alerts, list)


def test_scorecard_api_endpoint():
    resp = client.get("/api/v1/research/scorecard?symbol=RELIANCE", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "RELIANCE" in data["symbol"]
    assert "scores" in data


def test_scorecard_matrix_api_endpoint():
    resp = client.post("/api/v1/research/scorecard-matrix", json={"symbols": ["RELIANCE", "TCS"]}, headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 2


def test_cagr_matrix_api_endpoint():
    resp = client.get("/api/v1/research/cagr-matrix?symbol=RELIANCE", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "scenario_matrix" in data


def test_swing_alerts_api_endpoint():
    resp = client.get("/api/v1/strategies/swing-alerts", headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "alerts" in data
