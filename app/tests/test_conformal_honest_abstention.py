"""Unit tests for Phase 79: Statistically Honest Conformal Calibration & Abstention."""

import pytest
import numpy as np
from app.services.ml.conformal_prediction import ConformalPredictor, ConformalPredictionInterval
from app.services.probability import calculate_return_probability
from app.models.schemas import ReturnProbabilityRequest


def test_conformal_prediction_dataclass_default_is_uncalibrated():
    """Verify default ConformalPredictionInterval does not falsely claim calibration."""
    cpi = ConformalPredictionInterval(
        point_estimate=0.75,
        lower_bound_90=0.60,
        upper_bound_90=0.90,
        lower_bound_95=0.55,
        upper_bound_95=0.95,
        coverage_guarantee_pct=90.0,
        strata="GENERAL",
    )
    assert cpi.is_calibrated is False
    assert cpi.calibration_sample_size == 0
    assert cpi.calibration_status == "UNVERIFIED"


def test_conformal_predictor_abstain_on_small_samples():
    """Verify ConformalPredictor returns ABSTAIN_INSUFFICIENT_DATA when sample size < 10."""
    cp = ConformalPredictor(auto_load=False)
    # Empty strata
    interval_empty = cp.predict_interval(0.50, strata="NON_EXISTENT_STRATA")
    assert interval_empty.is_calibrated is False
    assert interval_empty.calibration_status == "ABSTAIN_INSUFFICIENT_DATA"

    # Strata with only 5 samples (< 10)
    cp.residuals_by_strata["SMALL_SAMPLE"] = np.array([0.02, 0.05, 0.03, 0.04, 0.06])
    interval_small = cp.predict_interval(0.50, strata="SMALL_SAMPLE")
    assert interval_small.is_calibrated is False
    assert interval_small.calibration_sample_size == 5
    assert interval_small.calibration_status == "ABSTAIN_INSUFFICIENT_DATA"

    # Strata with 55 samples (>= 50)
    cp.residuals_by_strata["LARGE_SAMPLE"] = np.random.uniform(0.01, 0.10, size=55)
    interval_large = cp.predict_interval(0.50, strata="LARGE_SAMPLE")
    assert interval_large.is_calibrated is True
    assert interval_large.calibration_sample_size == 55
    assert interval_large.calibration_status == "EMPIRICALLY_VERIFIED"
