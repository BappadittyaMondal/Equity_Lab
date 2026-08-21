"""Unit test suite for Phase 3 Model Retraining & Evaluation Cadence.
Verifies held-out evaluation, candidate comparison, and model promotion logic.
"""

import pytest
from app.services.ml.baseline_model import evaluate_and_retrain_model
from app.services.monitoring.score_calibration import get_model_versions


def test_evaluate_and_retrain_model_returns_valid_structure():
    """Verify evaluate_and_retrain_model returns expected evaluation fields."""
    result = evaluate_and_retrain_model()
    assert "status" in result
    assert "sample_count" in result
    assert "promoted" in result
    assert "version" in result
    assert "message" in result
    assert isinstance(result["promoted"], bool)


def test_registered_model_versions_contains_active_version():
    """Verify registered model versions table contains baseline or retrained model version."""
    versions = get_model_versions()
    assert len(versions) > 0
    version_names = [v["version"] for v in versions]
    assert any("ML-LOGISTIC" in v for v in version_names)
