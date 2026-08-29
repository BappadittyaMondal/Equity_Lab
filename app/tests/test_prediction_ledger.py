"""Unit tests for PredictionLedgerStore.
"""

import pytest
from app.services.intelligence.prediction_ledger import PredictionLedgerStore


def test_prediction_ledger_flow():
    store = PredictionLedgerStore()
    pred_id = store.log_prediction(
        symbol="INFY",
        predicted_target=1800.0,
        conformal_lower=1600.0,
        conformal_upper=2000.0,
        confidence_tier="CONFIRMED_HIGH",
        invalidation_triggers=["D/E > 0.5"],
        base_price=1500.0,
    )

    assert pred_id.startswith("PRED-")
    pred = store.get_prediction(pred_id)
    assert pred["symbol"] == "INFY"

    # Evaluate 30d post-mortem
    eval_res = store.evaluate_post_mortem(pred_id, horizon_days=30, actual_price=1750.0)
    assert eval_res["within_conformal_bounds"] is True
    assert eval_res["error_pct"] == -2.78
    assert "30d" in pred["evaluations"]
