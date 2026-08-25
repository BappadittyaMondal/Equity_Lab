"""Unit tests verifying ML model probability wiring & fallback in Prediction Engine."""

import pytest
from unittest.mock import patch
from app.services.decision_brain.prediction_engine import _build_scenario_tree, generate_prediction_summary
from app.services.ml.baseline_model import _MODEL_CACHE


def test_prediction_ml_wiring_fallback_under_20_samples():
    """Assert that with <20 ledger samples, fallback prior (0.25, 0.50, 0.25) is used and confidence_mode is prior_insufficient_data."""
    with patch.dict(_MODEL_CACHE, {"is_trained": False, "sample_count": 5, "model": None}, clear=True):
        with patch("app.services.ml.baseline_model.train_baseline_model", return_value={"status": "INSUFFICIENT_SAMPLES", "sample_count": 5, "is_trained": False}):
            st = _build_scenario_tree(
                current_price=100.0,
                empirical_p25=-5.0,
                empirical_p50=10.0,
                empirical_p75=25.0,
                fundamental_est=12.0,
                horizon_label="1Y",
                symbol="TEST_FALLBACK"
            )
            assert st["confidence_mode"] == "prior_insufficient_data"
            assert st["bull_case"]["probability"] == 0.25
            assert st["base_case"]["probability"] == 0.50
            assert st["bear_case"]["probability"] == 0.25
            assert st["prob_sum_check"] == 1.0


def test_prediction_ml_wiring_calibrated_over_20_samples():
    """Assert that with >=20 ledger samples, scenario probabilities differ from static prior and confidence_mode is calibrated_ml_ensemble."""
    fake_model = lambda: None
    with patch.dict(_MODEL_CACHE, {"is_trained": True, "sample_count": 50, "model": fake_model}):
        with patch("app.services.ml.baseline_model.predict_outperformance_prob", return_value=0.80):
            st = _build_scenario_tree(
                current_price=100.0,
                empirical_p25=-5.0,
                empirical_p50=10.0,
                empirical_p75=25.0,
                fundamental_est=12.0,
                horizon_label="1Y",
                symbol="TEST_ML_CALIBRATED",
                composite_score=85.0
            )
            assert st["confidence_mode"] == "calibrated_ml_ensemble"
            # With p_out = 0.80, p_bull = 0.50 * 0.80 = 0.40, p_bear = 0.50 * 0.20 = 0.10, p_base = 0.50
            assert st["bull_case"]["probability"] != 0.25
            assert st["bull_case"]["probability"] == 0.40
            assert st["bear_case"]["probability"] == 0.10
            assert st["base_case"]["probability"] == 0.50
            assert abs(st["prob_sum_check"] - 1.0) < 0.001


def test_prediction_regime_aware_probability_shift():
    """Assert that market regime (e.g. CRISIS or VOLATILE) shifts scenario probabilities towards bear case."""
    fake_model = lambda: None
    with patch.dict(_MODEL_CACHE, {"is_trained": True, "sample_count": 50, "model": fake_model}):
        with patch("app.services.ml.baseline_model.predict_outperformance_prob", return_value=0.60):
            st_calm = _build_scenario_tree(
                current_price=100.0, empirical_p25=-5.0, empirical_p50=10.0, empirical_p75=25.0,
                fundamental_est=12.0, horizon_label="1Y", regime="CALM"
            )
            st_volatile = _build_scenario_tree(
                current_price=100.0, empirical_p25=-5.0, empirical_p50=10.0, empirical_p75=25.0,
                fundamental_est=12.0, horizon_label="1Y", regime="VOLATILE"
            )
            # In VOLATILE regime, bear probability increases relative to CALM regime
            assert st_volatile["bear_case"]["probability"] > st_calm["bear_case"]["probability"]
            assert st_volatile["bull_case"]["probability"] < st_calm["bull_case"]["probability"]
            assert abs(st_volatile["prob_sum_check"] - 1.0) < 0.001


def test_model_persistence_roundtrip():
    """Verify NumPyEnsembleClassifier serialization to_dict and restoration from_dict reproduces predictions exactly."""
    import numpy as np
    from app.services.ml.baseline_model import NumPyEnsembleClassifier

    X = np.array([[60.0, 1.0, 0.6, 0.5, 1.0], [85.0, 1.0, 1.0, 1.0, 1.0], [30.0, 0.0, 0.0, 0.0, 0.0]], dtype=np.float64)
    y = np.array([1, 1, 0], dtype=np.int32)

    clf = NumPyEnsembleClassifier(n_estimators=10, random_state=42)
    clf.fit(X, y)
    orig_probs = clf.predict_proba(X)

    state = clf.to_dict()
    restored_clf = NumPyEnsembleClassifier.from_dict(state)
    restored_probs = restored_clf.predict_proba(X)

    np.testing.assert_allclose(orig_probs, restored_probs, rtol=1e-6, atol=1e-6)

