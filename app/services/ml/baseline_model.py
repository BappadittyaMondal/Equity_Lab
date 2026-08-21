"""Scikit-Learn Baseline Outperformance Classification Model.

Trains a LogisticRegression baseline classifier on historical outcomes
(prediction_ledger × outcome_ledger) to estimate probability of outperformance.
Provides fallback to calibrated sigmoid when sample data is insufficient.
"""

import math
import sqlite3
import numpy as np
from typing import Dict, Any, Optional, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from app.core.config import settings

_MODEL_CACHE: Dict[str, Any] = {
    "model": None,
    "scaler": None,
    "is_trained": False,
    "sample_count": 0,
}


def _get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DATA_STORE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def train_baseline_model() -> Dict[str, Any]:
    """Fetch historical outcomes and fit LogisticRegression classifier."""
    conn = _get_db_connection()
    rows = conn.execute(
        """
        SELECT 
            p.score,
            COALESCE(c.data_backed, 0) AS data_backed,
            o.excess_return_pct
        FROM prediction_ledger p
        JOIN outcome_ledger o ON p.id = o.prediction_id
        LEFT JOIN conviction_calls c ON p.conviction_call_id = c.id
        WHERE p.score IS NOT NULL AND o.excess_return_pct IS NOT NULL
        """
    ).fetchall()
    conn.close()

    if len(rows) < 20:
        return {
            "status": "INSUFFICIENT_SAMPLES",
            "sample_count": len(rows),
            "is_trained": False,
            "message": "Fewer than 20 outcomes available. Using calibrated sigmoid fallback."
        }

    X_data = []
    y_data = []
    for r in rows:
        score = float(r["score"])
        db_flag = float(r["data_backed"])
        target = 1 if r["excess_return_pct"] > 0 else 0
        X_data.append([score, db_flag])
        y_data.append(target)

    X = np.array(X_data, dtype=np.float64)
    y = np.array(y_data, dtype=np.int32)

    if len(np.unique(y)) < 2:
        return {
            "status": "SINGLE_CLASS_ONLY",
            "sample_count": len(rows),
            "is_trained": False,
            "message": "All historical outcomes fall into single class. Using calibrated sigmoid fallback."
        }

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=200, random_state=42)
    clf.fit(X_scaled, y)

    _MODEL_CACHE["model"] = clf
    _MODEL_CACHE["scaler"] = scaler
    _MODEL_CACHE["is_trained"] = True
    _MODEL_CACHE["sample_count"] = len(rows)

    return {
        "status": "TRAINED",
        "sample_count": len(rows),
        "is_trained": True,
        "classes": clf.classes_.tolist()
    }


def predict_outperformance_prob(
    symbol: str,
    composite_score: float,
    data_backed: bool = False,
    extra_features: Optional[Dict[str, float]] = None
) -> float:
    """Predict outperformance probability (0.0 to 1.0) using ML model or fallback."""
    if not _MODEL_CACHE["is_trained"]:
        # Attempt one-time lazy training
        try:
            train_baseline_model()
        except Exception:
            pass

    if _MODEL_CACHE["is_trained"] and _MODEL_CACHE["model"] is not None:
        try:
            db_flag = 1.0 if data_backed else 0.0
            x_vec = np.array([[float(composite_score), db_flag]], dtype=np.float64)
            x_scaled = _MODEL_CACHE["scaler"].transform(x_vec)
            probs = _MODEL_CACHE["model"].predict_proba(x_scaled)[0]
            # Index 1 corresponds to class 1 (outperformance > 0)
            class_idx = 1 if 1 in _MODEL_CACHE["model"].classes_ else 0
            prob = float(probs[class_idx])
            return round(max(0.0, min(1.0, prob)), 4)
        except Exception:
            pass

    # Calibrated Sigmoid Fallback when model data is sparse or uninitialized
    # Maps composite_score 60 -> 0.50, score 80 -> 0.77, score 40 -> 0.23
    val = -0.06 * (float(composite_score) - 60.0)
    fallback_prob = 1.0 / (1.0 + math.exp(val))
    return round(max(0.0, min(1.0, fallback_prob)), 4)
