"""Unit & Integration tests for Prediction Engine (Layer 10)."""

import pytest
from app.services.decision_brain.prediction_engine import (
    generate_prediction_summary, _empirical_returns, _risk_metrics, _build_scenario_tree
)
from app.services.monitoring.prediction_ledger import PredictionLedgerService
from app.models.schemas import ConvictionCall


def test_prediction_engine_summary_structure():
    res = generate_prediction_summary("RELIANCE")
    assert "symbol" in res
    assert "RELIANCE" in res["symbol"]
    assert "horizon_predictions" in res
    assert "1Y" in res["horizon_predictions"]
    assert "scenario_tree" in res["horizon_predictions"]["1Y"]
    assert "confidence_decomposition" in res
    
    st = res["horizon_predictions"]["1Y"]["scenario_tree"]
    assert abs(st["prob_sum_check"] - 1.0) < 0.01


def test_prediction_engine_missing_data_status():
    # Unknown ticker with no price or financial history
    res = generate_prediction_summary("UNKNOWN_TICKER_XYZ99")
    hp = res["horizon_predictions"]["1Y"]
    assert hp["data_status"] == "DATA_UNAVAILABLE" or hp["blended_expected_return_pct"] == 0.0


def test_prediction_engine_scenario_probabilities():
    st = _build_scenario_tree(
        current_price=100.0,
        empirical_p25=-5.0,
        empirical_p50=10.0,
        empirical_p75=25.0,
        fundamental_est=12.0,
        horizon_label="1Y"
    )
    assert st["bull_case"]["probability"] > 0
    assert st["base_case"]["probability"] > 0
    assert st["bear_case"]["probability"] > 0
    assert abs(st["prob_sum_check"] - 1.0) < 0.01


def test_prediction_ledger_logging():
    ledger = PredictionLedgerService()
    record = ledger.log_prediction(
        symbol="TEST_RELIANCE",
        score=75,
        verdict="Buy",
        confidence="Confirmed",
        thesis="Test thesis for prediction ledger auto-logging",
        reference_price=1310.0
    )
    assert record is not None
    assert record.id is not None
    assert record.id > 0
