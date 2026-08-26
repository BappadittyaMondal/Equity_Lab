"""Unit tests for Walk-Forward Evaluation Harness (Phase E Cycle N Hardening).
"""

import numpy as np
import pytest
from app.services.ml.evaluation_harness import evaluate_walk_forward_harness


def test_walk_forward_harness_production_mode_returns_insufficient_data():
    """Verify that when run against empty production DB, returns INSUFFICIENT_DATA."""
    res = evaluate_walk_forward_harness()
    assert res["status"] == "INSUFFICIENT_DATA"
    assert "INSUFFICIENT_DATA" in res["message"] or res["sample_count"] < 20


def test_walk_forward_harness_synthetic_fixture_mode():
    """Verify that when run with synthetic predictions and outcomes, computes exact metrics."""
    np.random.seed(42)
    synthetic_preds = np.array([0.9, 0.8, 0.7, 0.1, 0.2, 0.85, 0.15, 0.95, 0.05, 0.3])
    synthetic_targets = np.array([1, 1, 1, 0, 0, 1, 0, 1, 0, 0])

    res = evaluate_walk_forward_harness(
        synthetic_predictions=synthetic_preds,
        synthetic_outcomes=synthetic_targets
    )

    assert res["status"] == "EVALUATED"
    assert res["evaluation_mode"] == "SYNTHETIC_FIXTURE"
    assert res["sample_count"] == 10
    metrics = res["metrics"]
    assert "brier_score" in metrics
    assert "roc_auc" in metrics
    assert "accuracy" in metrics
    assert metrics["roc_auc"] > 0.8
    assert metrics["brier_score"] < 0.2
