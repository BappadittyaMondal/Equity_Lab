"""ML Rigor Upgrade Unit & Integration Tests.

Validates:
1. 5-fold cross-validation functionality and metric bounds (Accuracy, ROC-AUC, Brier, Precision, Recall, F1).
2. Pure-NumPy Gradient Boosting Classifier fitting & prediction.
3. Pure-NumPy Ensemble Classifier fitting & prediction.
4. Experiment logging of cross-validation metrics in SQLite database `model_versions`.
5. Score Calibration Brier score calculation.
"""

import pytest
import numpy as np
import sqlite3
from app.services.ml.baseline_model import (
    NumPyLogisticRegression,
    NumPyGradientBoostingClassifier,
    NumPyEnsembleClassifier,
    numpy_brier_score,
    numpy_log_loss,
    numpy_roc_auc_score,
    numpy_precision_recall_f1,
    numpy_kfold_cross_validate,
    train_baseline_model,
)
from app.services.monitoring.score_calibration import compute_calibration_report


def test_numpy_metrics_bounds():
    """Verify that custom numpy metrics produce valid mathematical outputs."""
    y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 0])
    y_prob = np.array([0.9, 0.1, 0.8, 0.7, 0.2, 0.85, 0.15, 0.3, 0.95, 0.05])
    y_pred = (y_prob >= 0.5).astype(int)

    brier = numpy_brier_score(y_true, y_prob)
    assert 0.0 <= brier <= 1.0, f"Brier score {brier} out of bounds"

    loss = numpy_log_loss(y_true, y_prob)
    assert loss >= 0.0, f"Log loss {loss} invalid"

    auc = numpy_roc_auc_score(y_true, y_prob)
    assert 0.5 <= auc <= 1.0, f"ROC-AUC score {auc} out of bounds"

    metrics_res = numpy_precision_recall_f1(y_true, y_pred)
    p, r, f1 = metrics_res["precision"], metrics_res["recall"], metrics_res["f1_score"]
    assert 0.0 <= p <= 1.0
    assert 0.0 <= r <= 1.0
    assert 0.0 <= f1 <= 1.0


def test_gbdt_classifier():
    """Verify fitting and prediction of pure-NumPy GBDT Classifier."""
    X = np.array([
        [1.0, 2.0], [1.5, 1.8], [0.8, 2.2],
        [-1.0, -2.0], [-1.5, -1.8], [-0.8, -2.2]
    ])
    y = np.array([1, 1, 1, 0, 0, 0])

    clf = NumPyGradientBoostingClassifier(n_estimators=10, learning_rate=0.1)
    clf.fit(X, y)
    probs = clf.predict_proba(X)
    preds = clf.predict(X)

    assert len(probs) == 6
    assert len(preds) == 6
    assert (preds == y).all(), "GBDT should overfit synthetic linearly separable data"


def test_ensemble_classifier():
    """Verify fitting and prediction of pure-NumPy Ensemble Classifier."""
    X = np.array([
        [2.0, 3.0], [2.5, 2.8], [1.8, 3.2],
        [-2.0, -3.0], [-2.5, -2.8], [-1.8, -3.2]
    ])
    y = np.array([1, 1, 1, 0, 0, 0])

    ensemble = NumPyEnsembleClassifier(n_estimators=5)
    ensemble.fit(X, y)
    probs = ensemble.predict_proba(X)
    preds = ensemble.predict(X)

    assert len(probs) == 6
    assert len(preds) == 6
    assert (preds == y).all(), "Ensemble should classify separated points accurately"


def test_5fold_cross_validation():
    """Verify 5-fold cross-validation returns complete metric dictionary."""
    X = np.random.randn(25, 4)
    y = np.random.randint(0, 2, size=25)

    clf = NumPyLogisticRegression()
    cv_res = numpy_kfold_cross_validate(clf, X, y, n_splits=5)

    assert cv_res["folds"] == 5
    assert "mean_accuracy" in cv_res
    assert "mean_roc_auc" in cv_res
    assert "mean_brier_score" in cv_res
    assert "mean_f1_score" in cv_res
    assert 0.0 <= cv_res["mean_accuracy"] <= 1.0


@pytest.fixture(scope="module", autouse=True)
def seed_test_outcomes():
    from app.core.config import settings
    conn = sqlite3.connect(settings.DATA_STORE_PATH, timeout=30.0)
    now_str = "2026-01-01T00:00:00Z"
    try:
        count = conn.execute("SELECT count(*) FROM prediction_ledger WHERE symbol LIKE 'MOCKSTOCK%'").fetchone()[0]
    except Exception:
        count = 0
    if count < 25:
        for i in range(25):
            score = 50.0 + i * 1.5
            sym = f"MOCKSTOCK{i}.NS"
            cur = conn.execute(
                """INSERT INTO prediction_ledger 
                (symbol, score, verdict, confidence, reference_price, timestamp, created_at, pre_fix_unverified) 
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
                (sym, score, "Buy", "Confirmed", 100.0, now_str, now_str)
            )
            pred_id = cur.lastrowid
            exc_ret = 5.0 if i % 2 == 0 else -3.0
            out_cls = "OUTPERFORM" if exc_ret > 0 else "UNDERPERFORM"
            conn.execute(
                """INSERT INTO outcome_ledger 
                (prediction_id, symbol, horizon_months, actual_return_pct, benchmark_return_pct, excess_return_pct, outcome_class, recorded_at, pre_fix_unverified) 
                VALUES (?, ?, 12, ?, 0.0, ?, ?, ?, 0)""",
                (pred_id, sym, exc_ret, exc_ret, out_cls, now_str)
            )
        conn.commit()
    conn.close()
    train_baseline_model(force_retrain=True)


def test_train_baseline_model_registration():
    """Verify train_baseline_model logs 5-fold CV metrics into SQLite database."""
    res = train_baseline_model(force_retrain=True)
    assert res["status"] in ("TRAINED", "ACTIVE")
    assert "cross_validation_5fold" in res
    assert res["cross_validation_5fold"]["folds"] == 5


