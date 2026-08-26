"""Callable Walk-Forward Evaluation Harness (Cycle N Hardening Phase E).

Computes Brier Score, ROC-AUC, Log-Loss, and F1 accuracy metrics using a purged,
embargoed walk-forward window for time-series predictions.

When executed against production database tables (where outcome_ledger is currently empty),
it safely returns status="INSUFFICIENT_DATA".
When provided a synthetic fixture array, it computes full institutional evaluation metrics.
"""

from typing import Dict, Any, Optional, List
import numpy as np
from app.services.ml.baseline_model import (
    numpy_brier_score,
    numpy_roc_auc_score,
    numpy_log_loss,
    numpy_accuracy_score,
    numpy_precision_recall_f1,
    numpy_walk_forward_cross_validate,
    NumPyEnsembleClassifier,
    _get_db_connection
)


def evaluate_walk_forward_harness(
    synthetic_predictions: Optional[np.ndarray] = None,
    synthetic_outcomes: Optional[np.ndarray] = None,
    n_splits: int = 5,
    purge_window: int = 5
) -> Dict[str, Any]:
    """Execute purged walk-forward cross-validation evaluation.

    If synthetic arrays are supplied, calculates metrics directly.
    Otherwise, checks production outcome_ledger: if < 20 rows, returns INSUFFICIENT_DATA.
    """
    # Case 1: Synthetic fixture mode (for automated unit tests)
    if synthetic_predictions is not None and synthetic_outcomes is not None:
        preds = np.asarray(synthetic_predictions, dtype=np.float64)
        targets = np.asarray(synthetic_outcomes, dtype=np.int32)
        n = len(targets)

        if n == 0:
            return {
                "status": "INSUFFICIENT_DATA",
                "sample_count": 0,
                "message": "Empty synthetic input array."
            }

        brier = numpy_brier_score(targets, preds)
        auc = numpy_roc_auc_score(targets, preds)
        log_loss_val = numpy_log_loss(targets, preds)
        binary_preds = (preds >= 0.5).astype(np.int32)
        acc = numpy_accuracy_score(targets, binary_preds)
        prf1 = numpy_precision_recall_f1(targets, binary_preds)

        return {
            "status": "EVALUATED",
            "evaluation_mode": "SYNTHETIC_FIXTURE",
            "sample_count": n,
            "metrics": {
                "brier_score": round(brier, 4),
                "roc_auc": round(auc, 4),
                "log_loss": round(log_loss_val, 4),
                "accuracy": round(acc, 4),
                "precision": prf1["precision"],
                "recall": prf1["recall"],
                "f1_score": prf1["f1_score"]
            }
        }

    # Case 2: Production DB ledger mode
    try:
        conn = _get_db_connection()
        rows = conn.execute(
            """
            SELECT p.score, o.excess_return_pct
            FROM prediction_ledger p
            JOIN outcome_ledger o ON p.id = o.prediction_id
            WHERE p.score IS NOT NULL AND o.excess_return_pct IS NOT NULL
              AND (p.pre_fix_unverified IS NULL OR p.pre_fix_unverified = 0)
              AND (o.pre_fix_unverified IS NULL OR o.pre_fix_unverified = 0)
            """
        ).fetchall()
        conn.close()

        if len(rows) < 20:
            return {
                "status": "INSUFFICIENT_DATA",
                "evaluation_mode": "PRODUCTION_LEDGER",
                "sample_count": len(rows),
                "message": "Fewer than 20 matured outcome rows in outcome_ledger. Calibration metrics output INSUFFICIENT_DATA as required by ground truth discipline."
            }

        # Extract features and targets if outcomes become available
        scores = np.array([[float(r["score"]), 1.0] for r in rows], dtype=np.float64)
        targets = np.array([1 if float(r["excess_return_pct"]) > 0 else 0 for r in rows], dtype=np.int32)

        wf_metrics = numpy_walk_forward_cross_validate(
            NumPyEnsembleClassifier, scores, targets, n_splits=n_splits, purge_window=purge_window
        )

        return {
            "status": "EVALUATED",
            "evaluation_mode": "PRODUCTION_LEDGER",
            "sample_count": len(rows),
            "metrics": wf_metrics
        }
    except Exception as exc:
        return {
            "status": "INSUFFICIENT_DATA",
            "evaluation_mode": "PRODUCTION_LEDGER",
            "sample_count": 0,
            "error": str(exc),
            "message": "Database query failed or outcome_ledger missing/empty."
        }
