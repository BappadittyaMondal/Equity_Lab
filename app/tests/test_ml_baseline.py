"""Unit tests for Scikit-Learn baseline outperformance prediction module."""

import pytest
from app.services.ml.baseline_model import train_baseline_model, predict_outperformance_prob
from app.services.decision_brain.arbiter import Arbiter
from app.models.schemas import ConvictionCall


def test_baseline_model_training():
    res = train_baseline_model()
    assert isinstance(res, dict)
    assert "status" in res
    assert "sample_count" in res


def test_predict_outperformance_prob():
    prob_high = predict_outperformance_prob("RELIANCE", 85.0, data_backed=True)
    prob_low = predict_outperformance_prob("RELIANCE", 35.0, data_backed=False)

    assert 0.0 <= prob_high <= 1.0
    assert 0.0 <= prob_low <= 1.0
    assert prob_high > prob_low


def test_arbiter_integration_with_ml_prob():
    arb = Arbiter()
    call = arb.arbitrate("RELIANCE")
    assert isinstance(call, ConvictionCall)
    assert call.ml_outperformance_probability is not None
    assert 0.0 <= call.ml_outperformance_probability <= 1.0
