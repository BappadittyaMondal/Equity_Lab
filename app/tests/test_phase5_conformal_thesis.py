"""Test Suite for Phase 5 Conformal Prediction, Thesis Invalidation, and Champion/Challenger Benchmark."""

import tempfile
from pathlib import Path
import numpy as np
import pytest

from app.services.ml.conformal_prediction import ConformalPredictor
from app.services.research.thesis_tracker import ThesisTracker, KillCondition
from app.services.ml.champion_challenger import ChampionChallengerEvaluator


def test_conformal_prediction_intervals():
    y_true = np.array([0.10, 0.15, -0.05, 0.20, 0.08, 0.12, -0.02, 0.25])
    y_pred = np.array([0.08, 0.12,  0.00, 0.18, 0.10, 0.10,  0.02, 0.20])

    cp = ConformalPredictor(alpha=0.10)
    cp.fit(y_true, y_pred, strata="SMALL_CAP")

    res = cp.predict_interval(point_estimate=0.15, strata="SMALL_CAP")
    assert res.lower_bound_90 < 0.15 < res.upper_bound_90
    assert res.lower_bound_95 <= res.lower_bound_90
    assert res.upper_bound_95 >= res.upper_bound_90
    assert res.coverage_guarantee_pct == 90.0


def test_thesis_tracker_lifecycle_and_invalidation():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = str(Path(tmp_dir) / "test_thesis.db")
        tracker = ThesisTracker(db_path=db_file)

        thesis = tracker.create_thesis(
            symbol="POLYCAB",
            primary_thesis="Operating leverage driving 25% PAT growth",
            confidence_score=80.0
        )
        assert thesis.status == "NEW"

        # Evaluate healthy metrics -> Should advance to CONFIRMED
        healthy_metrics = {
            "cfo_ebitda_ratio": 0.85,
            "promoter_pledge_pct": 2.5,
            "quarterly_revenue_growth_pct": 18.5
        }
        t1 = tracker.evaluate_thesis(thesis.thesis_id, healthy_metrics)
        assert t1.status == "CONFIRMED"
        assert t1.invalidation_reason is None

        # Evaluate invalidating metrics -> Should trigger BROKEN
        broken_metrics = {
            "cfo_ebitda_ratio": 0.40,  # Below 0.65 threshold
            "promoter_pledge_pct": 2.5,
            "quarterly_revenue_growth_pct": 18.5
        }
        t2 = tracker.evaluate_thesis(thesis.thesis_id, broken_metrics)
        assert t2.status == "BROKEN"
        assert "Kill condition triggered" in t2.invalidation_reason


def test_champion_challenger_evaluator():
    np.random.seed(42)
    y_true = np.array([0.05, 0.12, -0.08, 0.20, -0.03, 0.15])
    preds_gbt = y_true + np.random.randn(6) * 0.05
    preds_chronos = y_true + np.random.randn(6) * 0.02

    evaluator = ChampionChallengerEvaluator()
    res = evaluator.evaluate_models(
        y_true,
        {"Baseline_GBDT_Ensemble": preds_gbt, "Chronos_2_ZeroShot": preds_chronos},
        current_champion_name="Baseline_GBDT_Ensemble"
    )

    assert len(res) == 2
    assert res[0].brier_score <= res[1].brier_score


def test_benjamini_hochberg_fdr():
    from app.services.ml.statistical_fdr import benjamini_hochberg_fdr
    raw_p = [0.001, 0.012, 0.045, 0.20, 0.55]
    results = benjamini_hochberg_fdr(raw_p, alpha=0.05)
    assert len(results) == 5
    assert results[0]["adjusted_p_value"] <= results[1]["adjusted_p_value"]
    assert results[0]["is_significant"] is True
    assert results[4]["is_significant"] is False

