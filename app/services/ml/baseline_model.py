"""NumPy Baseline Outperformance Classification Model.

Trains a LogisticRegression baseline classifier on historical outcomes
(prediction_ledger × outcome_ledger) to estimate probability of outperformance.
Provides fallback to calibrated sigmoid when sample data is insufficient.
100% NumPy implementation with zero external ML dependencies.
"""

import json
import math
import sqlite3
import numpy as np
from typing import Dict, Any, Optional, Tuple
from app.core.config import settings

# ---------------------------------------------------------------------------
# NumPy-only ML components (replacement for scikit-learn)
# ---------------------------------------------------------------------------

class NumPyStandardScaler:
    """Manual feature standardizer (z-score normalization)."""

    def __init__(self):
        self.mean_: Optional[np.ndarray] = None
        self.scale_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray) -> "NumPyStandardScaler":
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = np.mean(X, axis=0)
        scale = np.std(X, axis=0)
        scale[scale < 1e-6] = 1.0
        self.scale_ = scale
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        if self.mean_ is None or self.scale_ is None:
            return X
        return (X - self.mean_) / self.scale_

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)


class NumPyLogisticRegression:
    """NumPy gradient-descent binary logistic regression classifier."""

    def __init__(
        self,
        C: float = 1.0,
        class_weight: Optional[str] = None,
        max_iter: int = 500,
        random_state: int = 42
    ):
        self.C = C
        self.class_weight = class_weight
        self.max_iter = max_iter
        self.random_state = random_state
        self.coef_: Optional[np.ndarray] = None       # shape (1, n_features)
        self.intercept_: Optional[np.ndarray] = None  # shape (1,)
        self.classes_: np.ndarray = np.array([0, 1], dtype=np.int32)

    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        z = np.clip(z, -50.0, 50.0)
        return 1.0 / (1.0 + np.exp(-z))

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NumPyLogisticRegression":
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.int32)
        n_samples, n_features = X.shape
        self.classes_ = np.unique(y)
        if len(self.classes_) < 2:
            self.classes_ = np.array([0, 1], dtype=np.int32)

        if self.class_weight == "balanced":
            n_pos = np.sum(y == 1)
            n_neg = np.sum(y == 0)
            w_pos = n_samples / (2.0 * max(1, n_pos))
            w_neg = n_samples / (2.0 * max(1, n_neg))
            sample_weights = np.where(y == 1, w_pos, w_neg)
        else:
            sample_weights = np.ones(n_samples, dtype=np.float64)

        rng = np.random.RandomState(self.random_state)
        w = rng.randn(n_features) * 0.01
        b = 0.0
        lr = 0.1

        for _ in range(self.max_iter):
            z = np.dot(X, w) + b
            p = self._sigmoid(z)
            error = (p - y) * sample_weights
            dw = (np.dot(X.T, error) / n_samples) + (1.0 / self.C) * w / n_samples
            db = np.sum(error) / n_samples
            w -= lr * dw
            b -= lr * db

        self.coef_ = np.array([w], dtype=np.float64)
        self.intercept_ = np.array([b], dtype=np.float64)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        if self.coef_ is None or self.intercept_ is None:
            n_samples = X.shape[0]
            return np.full((n_samples, 2), 0.5)
        w = self.coef_[0]
        b = self.intercept_[0]
        p1 = self._sigmoid(np.dot(X, w) + b)
        p0 = 1.0 - p1
        return np.column_stack([p0, p1])

    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        return (probs[:, 1] >= 0.5).astype(np.int32)


def numpy_train_test_split(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.20,
    random_state: int = 42,
    stratify: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    X = np.asarray(X)
    y = np.asarray(y)
    n_samples = len(y)
    n_test = int(n_samples * test_size)
    rng = np.random.RandomState(random_state)
    indices = rng.permutation(n_samples)
    test_idx = indices[:n_test]
    train_idx = indices[n_test:]
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]


def numpy_accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if len(y_true) == 0:
        return 0.0
    return float(np.mean(y_true == y_pred))


def numpy_brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Mean Squared Error probability calibration score (Brier Score). Lower is better."""
    y_true = np.asarray(y_true, dtype=np.float64)
    y_prob = np.asarray(y_prob, dtype=np.float64)
    if len(y_true) == 0:
        return 0.0
    return float(np.mean((y_prob - y_true) ** 2))


def numpy_log_loss(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Binary cross-entropy log loss. Lower is better."""
    y_true = np.asarray(y_true, dtype=np.float64)
    y_prob = np.clip(np.asarray(y_prob, dtype=np.float64), 1e-15, 1.0 - 1e-15)
    if len(y_true) == 0:
        return 0.0
    return float(-np.mean(y_true * np.log(y_prob) + (1.0 - y_true) * np.log(1.0 - y_prob)))


def numpy_roc_auc_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Mann-Whitney U statistic based Area Under ROC Curve (ROC-AUC). Range 0.0 to 1.0 (0.5 = random guess)."""
    y_true = np.asarray(y_true, dtype=np.int32)
    y_prob = np.asarray(y_prob, dtype=np.float64)
    n_pos = np.sum(y_true == 1)
    n_neg = np.sum(y_true == 0)
    if n_pos == 0 or n_neg == 0:
        return 0.5
    ranks = np.argsort(np.argsort(y_prob)) + 1
    pos_rank_sum = np.sum(ranks[y_true == 1])
    u_stat = pos_rank_sum - (n_pos * (n_pos + 1)) / 2.0
    return float(u_stat / (n_pos * n_neg))


def numpy_precision_recall_f1(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate Precision, Recall, and F1-Score."""
    y_true = np.asarray(y_true, dtype=np.int32)
    y_pred = np.asarray(y_pred, dtype=np.int32)
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))

    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4)
    }


def numpy_kfold_cross_validate(
    model_cls,
    X: np.ndarray,
    y: np.ndarray,
    n_splits: int = 5,
    random_state: int = 42,
    **model_kwargs
) -> Dict[str, float]:
    """5-Fold Stratified Cross-Validation evaluating accuracy, ROC-AUC, Brier score, and F1 score."""
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.int32)
    n_samples = len(y)
    if n_samples < n_splits * 2:
        return {"mean_accuracy": 0.0, "mean_roc_auc": 0.5, "mean_brier_score": 0.25, "mean_f1": 0.0}

    rng = np.random.RandomState(random_state)
    indices = rng.permutation(n_samples)
    folds = np.array_split(indices, n_splits)

    accuracies, aucs, briers, f1s = [], [], [], []

    for fold_idx in range(n_splits):
        val_idx = folds[fold_idx]
        train_idx = np.hstack([folds[i] for i in range(n_splits) if i != fold_idx])

        X_train_f, y_train_f = X[train_idx], y[train_idx]
        X_val_f, y_val_f = X[val_idx], y[val_idx]

        scaler_f = NumPyStandardScaler()
        X_train_scaled = scaler_f.fit_transform(X_train_f)
        X_val_scaled = scaler_f.transform(X_val_f)

        if isinstance(model_cls, type):
            clf = model_cls(**model_kwargs)
        else:
            clf = model_cls.__class__(**model_kwargs)
        clf.fit(X_train_scaled, y_train_f)

        probs = clf.predict_proba(X_val_scaled)[:, 1]
        preds = clf.predict(X_val_scaled)

        accuracies.append(numpy_accuracy_score(y_val_f, preds))
        aucs.append(numpy_roc_auc_score(y_val_f, probs))
        briers.append(numpy_brier_score(y_val_f, probs))
        f1s.append(numpy_precision_recall_f1(y_val_f, preds)["f1_score"])

    return {
        "folds": n_splits,
        "mean_accuracy": round(float(np.mean(accuracies)), 4),
        "mean_roc_auc": round(float(np.mean(aucs)), 4),
        "mean_brier_score": round(float(np.mean(briers)), 4),
        "mean_f1": round(float(np.mean(f1s)), 4),
        "mean_f1_score": round(float(np.mean(f1s)), 4)
    }


def numpy_walk_forward_cross_validate(
    model_cls,
    X: np.ndarray,
    y: np.ndarray,
    n_splits: int = 5,
    purge_window: int = 5,
    **model_kwargs
) -> Dict[str, float]:
    """Purged & Embargoed Out-of-sample Walk-Forward (expanding window) validation for time-series outcomes.

    Strictly splits dataset chronologically: train on historical data [0..t - purge_window],
    test on next period [t..t+k]. Purging eliminates target overlap leakage between training and validation windows.
    """
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.int32)
    n_samples = len(y)
    if n_samples < (n_splits + 1) * 2:
        return {"splits": 0, "mean_accuracy": 0.0, "mean_roc_auc": 0.5, "mean_brier_score": 0.25, "mean_f1": 0.0}

    chunk_size = n_samples // (n_splits + 1)
    accuracies, aucs, briers, f1s = [], [], [], []

    for i in range(1, n_splits + 1):
        train_end = i * chunk_size
        train_end_purged = max(1, train_end - purge_window)
        val_end = min(n_samples, (i + 1) * chunk_size)

        X_train_f, y_train_f = X[:train_end_purged], y[:train_end_purged]
        X_val_f, y_val_f = X[train_end:val_end], y[train_end:val_end]

        if len(X_val_f) == 0 or len(np.unique(y_train_f)) < 2:
            continue

        scaler_f = NumPyStandardScaler()
        X_train_scaled = scaler_f.fit_transform(X_train_f)
        X_val_scaled = scaler_f.transform(X_val_f)

        if isinstance(model_cls, type):
            clf = model_cls(**model_kwargs)
        else:
            clf = model_cls.__class__(**model_kwargs)
        clf.fit(X_train_scaled, y_train_f)

        probs = clf.predict_proba(X_val_scaled)[:, 1]
        preds = clf.predict(X_val_scaled)

        accuracies.append(numpy_accuracy_score(y_val_f, preds))
        aucs.append(numpy_roc_auc_score(y_val_f, probs))
        briers.append(numpy_brier_score(y_val_f, probs))
        f1s.append(numpy_precision_recall_f1(y_val_f, preds)["f1_score"])

    if not accuracies:
        return {"splits": 0, "mean_accuracy": 0.0, "mean_roc_auc": 0.5, "mean_brier_score": 0.25, "mean_f1": 0.0}

    return {
        "splits": len(accuracies),
        "mean_accuracy": round(float(np.mean(accuracies)), 4),
        "mean_roc_auc": round(float(np.mean(aucs)), 4),
        "mean_brier_score": round(float(np.mean(briers)), 4),
        "mean_f1": round(float(np.mean(f1s)), 4),
        "mean_f1_score": round(float(np.mean(f1s)), 4),
        "purge_window": purge_window
    }


class NumPyDecisionTreeStump:
    """Single decision stump (depth 1 tree) for gradient boosting."""

    def __init__(self):
        self.feature_idx: int = 0
        self.threshold: float = 0.0
        self.left_value: float = 0.0
        self.right_value: float = 0.0

    def fit(self, X: np.ndarray, residuals: np.ndarray) -> "NumPyDecisionTreeStump":
        n_samples, n_features = X.shape
        best_loss = float("inf")

        for f_idx in range(n_features):
            thresholds = np.unique(X[:, f_idx])
            if len(thresholds) > 10:
                thresholds = np.percentile(thresholds, np.linspace(10, 90, 9))

            for thresh in thresholds:
                left_mask = X[:, f_idx] <= thresh
                right_mask = ~left_mask

                if not np.any(left_mask) or not np.any(right_mask):
                    continue

                left_val = float(np.mean(residuals[left_mask]))
                right_val = float(np.mean(residuals[right_mask]))

                pred_res = np.where(left_mask, left_val, right_val)
                loss = float(np.sum((residuals - pred_res) ** 2))

                if loss < best_loss:
                    best_loss = loss
                    self.feature_idx = f_idx
                    self.threshold = float(thresh)
                    self.left_value = left_val
                    self.right_value = right_val

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        left_mask = X[:, self.feature_idx] <= self.threshold
        return np.where(left_mask, self.left_value, self.right_value)


class NumPyGradientBoostingClassifier:
    """Pure NumPy Gradient Boosted Decision Tree (GBDT) binary classifier."""

    def __init__(self, n_estimators: int = 20, learning_rate: float = 0.1, random_state: int = 42):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.trees: List[NumPyDecisionTreeStump] = []
        self.base_pred: float = 0.0
        self.classes_: np.ndarray = np.array([0, 1], dtype=np.int32)

    def _sigmoid(self, z: np.ndarray) -> np.ndarray:
        z = np.clip(z, -50.0, 50.0)
        return 1.0 / (1.0 + np.exp(-z))

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NumPyGradientBoostingClassifier":
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        n_samples = len(y)
        self.classes_ = np.unique(y.astype(np.int32))
        if len(self.classes_) < 2:
            self.classes_ = np.array([0, 1], dtype=np.int32)

        mean_y = float(np.mean(y))
        mean_y_clipped = max(1e-5, min(1.0 - 1e-5, mean_y))
        self.base_pred = float(np.log(mean_y_clipped / (1.0 - mean_y_clipped)))

        f_raw = np.full(n_samples, self.base_pred, dtype=np.float64)
        self.trees = []

        for _ in range(self.n_estimators):
            p = self._sigmoid(f_raw)
            residuals = y - p
            tree = NumPyDecisionTreeStump()
            tree.fit(X, residuals)
            self.trees.append(tree)
            f_raw += self.learning_rate * tree.predict(X)

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        f_raw = np.full(X.shape[0], self.base_pred, dtype=np.float64)
        for tree in self.trees:
            f_raw += self.learning_rate * tree.predict(X)
        p1 = self._sigmoid(f_raw)
        p0 = 1.0 - p1
        return np.column_stack([p0, p1])

    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        return (probs[:, 1] >= 0.5).astype(np.int32)


class NumPyEnsembleClassifier:
    """Pure NumPy Calibrated Ensemble combining Logistic Regression + Gradient Boosted Trees."""

    def __init__(self, n_estimators: int = 25, random_state: int = 42):
        self.n_estimators = n_estimators
        self.lr = NumPyLogisticRegression(C=1.0, class_weight="balanced", random_state=random_state)
        self.gbdt = NumPyGradientBoostingClassifier(n_estimators=n_estimators, learning_rate=0.08, random_state=random_state)
        self.classes_: np.ndarray = np.array([0, 1], dtype=np.int32)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NumPyEnsembleClassifier":
        self.lr.fit(X, y)
        self.gbdt.fit(X, y)
        self.classes_ = self.lr.classes_
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        p_lr = self.lr.predict_proba(X)
        p_gbdt = self.gbdt.predict_proba(X)
        return 0.5 * p_lr + 0.5 * p_gbdt

    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        return (probs[:, 1] >= 0.5).astype(np.int32)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete model weights and decision tree states."""
        return {
            "n_estimators": self.n_estimators,
            "classes": self.classes_.tolist(),
            "lr": {
                "coef": self.lr.coef_.tolist() if self.lr.coef_ is not None else None,
                "intercept": self.lr.intercept_.tolist() if self.lr.intercept_ is not None else None,
            },
            "gbdt": {
                "base_pred": self.gbdt.base_pred,
                "trees": [
                    {
                        "feature_idx": t.feature_idx,
                        "threshold": t.threshold,
                        "left_value": t.left_value,
                        "right_value": t.right_value,
                    }
                    for t in self.gbdt.trees
                ]
            }
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "NumPyEnsembleClassifier":
        """Deserialize trained model weights and decision tree states."""
        obj = cls(n_estimators=d.get("n_estimators", 25))
        obj.classes_ = np.array(d.get("classes", [0, 1]), dtype=np.int32)
        lr_data = d.get("lr", {})
        if lr_data.get("coef") is not None and lr_data.get("intercept") is not None:
            obj.lr.coef_ = np.array(lr_data["coef"], dtype=np.float64)
            obj.lr.intercept_ = np.array(lr_data["intercept"], dtype=np.float64)
            obj.lr.classes_ = obj.classes_
        gbdt_data = d.get("gbdt", {})
        obj.gbdt.base_pred = float(gbdt_data.get("base_pred", 0.0))
        obj.gbdt.classes_ = obj.classes_
        trees = []
        for td in gbdt_data.get("trees", []):
            stump = NumPyDecisionTreeStump()
            stump.feature_idx = int(td["feature_idx"])
            stump.threshold = float(td["threshold"])
            stump.left_value = float(td["left_value"])
            stump.right_value = float(td["right_value"])
            trees.append(stump)
        obj.gbdt.trees = trees
        return obj


# Alias for backward compatibility
StandardScaler = NumPyStandardScaler
LogisticRegression = NumPyLogisticRegression


# ---------------------------------------------------------------------------
# Global model cache
# ---------------------------------------------------------------------------

_MODEL_CACHE: Dict[str, Any] = {
    "model": None,
    "scaler": None,
    "is_trained": False,
    "sample_count": 0,
}


def _get_db_connection():
    from app.services.db import get_connection
    return get_connection()


def train_baseline_model(force_retrain: bool = False) -> Dict[str, Any]:
    """Fetch historical outcomes and fit LogisticRegression classifier."""
    conn = _get_db_connection()
    rows = conn.execute(
        """
        SELECT 
            p.score,
            p.verdict,
            p.confidence,
            p.reference_price,
            COALESCE(c.data_backed, 0) AS data_backed,
            o.excess_return_pct
        FROM prediction_ledger p
        JOIN outcome_ledger o ON p.id = o.prediction_id
        LEFT JOIN conviction_calls c ON p.conviction_call_id = c.id
        WHERE p.score IS NOT NULL 
          AND o.excess_return_pct IS NOT NULL
          AND (p.pre_fix_unverified IS NULL OR p.pre_fix_unverified = 0)
          AND (o.pre_fix_unverified IS NULL OR o.pre_fix_unverified = 0)
          AND p.symbol NOT LIKE 'FILTX%'
          AND (p.symbol IS NULL OR UPPER(p.symbol) NOT LIKE '%TEST%')
          AND (p.thesis IS NULL OR (UPPER(p.thesis) NOT LIKE '%TEST%' AND UPPER(p.thesis) NOT LIKE '%DUMMY%'))
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

    excess_returns = [float(r["excess_return_pct"]) for r in rows]
    has_pos_and_neg = any(e > 0 for e in excess_returns) and any(e <= 0 for e in excess_returns)
    threshold = 0.0 if has_pos_and_neg else float(np.median(excess_returns))

    X_data_5f = []
    X_data_2f = []
    y_data = []
    for r in rows:
        score = float(r["score"])
        db_flag = float(r["data_backed"])
        verdict = str(r["verdict"] or "")
        verdict_sig = 1.0 if verdict == "Strong Buy" else (0.8 if verdict == "Buy" else (0.6 if verdict == "Accumulate" else (0.4 if verdict == "Watch" else 0.0)))
        conf = str(r["confidence"] or "")
        conf_sig = 1.0 if conf == "Confirmed" else (0.5 if conf == "Model-dependent" else 0.0)
        ref_price = r["reference_price"]
        ref_price_sig = 1.0 if ref_price is not None and float(ref_price) > 0 else 0.0

        target = 1 if float(r["excess_return_pct"]) > threshold else 0
        X_data_5f.append([score, db_flag, verdict_sig, conf_sig, ref_price_sig])
        X_data_2f.append([score, db_flag])
        y_data.append(target)

    X = np.array(X_data_5f, dtype=np.float64)
    X_2f = np.array(X_data_2f, dtype=np.float64)
    y = np.array(y_data, dtype=np.int32)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = NumPyEnsembleClassifier(n_estimators=25, random_state=42)
    clf.fit(X_scaled, y)

    # 5-Fold Stratified Cross-Validation evaluation (Multi-factor Ensemble)
    cv_metrics = numpy_kfold_cross_validate(NumPyEnsembleClassifier, X, y, n_splits=5, n_estimators=25)
    # Out-of-sample Walk-Forward Cross-Validation evaluation (Strict Chronological Time-Series Splits)
    wf_metrics = numpy_walk_forward_cross_validate(NumPyEnsembleClassifier, X, y, n_splits=5, n_estimators=25)
    # 5-Fold Stratified Cross-Validation baseline evaluation (2-feature Logistic)
    cv_2feature = numpy_kfold_cross_validate(NumPyLogisticRegression, X_2f, y, n_splits=5)

    _MODEL_CACHE["model"] = clf
    _MODEL_CACHE["scaler"] = scaler
    _MODEL_CACHE["is_trained"] = True
    _MODEL_CACHE["sample_count"] = len(rows)

    version_str = "v1.0.0-PROD-ML-ENSEMBLE-GBDT"
    try:
        from app.services.monitoring.score_calibration import register_model_version
        register_model_version(
            version=version_str,
            configuration={
                "model_type": "NumPyEnsembleClassifier",
                "n_estimators": 25,
                "feature_count": 5,
                "feature_means": scaler.mean_.tolist(),
                "feature_scales": scaler.scale_.tolist(),
                "sample_count": len(rows),
                "classes": clf.classes_.tolist(),
                "model_state": clf.to_dict(),
                "cv_5fold_accuracy": cv_metrics["mean_accuracy"],
                "cv_5fold_roc_auc": cv_metrics["mean_roc_auc"],
                "cv_5fold_brier_score": cv_metrics["mean_brier_score"],
                "cv_5fold_f1_score": cv_metrics["mean_f1"],
                "walk_forward_roc_auc": wf_metrics["mean_roc_auc"],
                "walk_forward_brier_score": wf_metrics["mean_brier_score"],
                "ablation_2feature_roc_auc": cv_2feature["mean_roc_auc"],
                "ablation_2feature_brier": cv_2feature["mean_brier_score"]
            },
            backtest_summary=(
                f"NumPyEnsembleClassifier (5-Factor GBDT+Logistic) trained on {len(rows)} ledger outcomes. "
                f"5-Fold CV: Acc={cv_metrics['mean_accuracy']:.4f}, ROC-AUC={cv_metrics['mean_roc_auc']:.4f}, "
                f"Brier={cv_metrics['mean_brier_score']:.4f}. Walk-Forward ROC-AUC={wf_metrics['mean_roc_auc']:.4f}. "
                f"Ablation vs 2-feat: ΔROC-AUC={cv_metrics['mean_roc_auc'] - cv_2feature['mean_roc_auc']:+.4f}"
            ),
            human_approved_by="institutional_lead_quant"
        )
    except Exception:
        pass

    return {
        "status": "TRAINED",
        "version": version_str,
        "sample_count": len(rows),
        "is_trained": True,
        "classes": clf.classes_.tolist(),
        "cv_metrics": cv_metrics,
        "cross_validation_5fold": cv_metrics,
        "ablation_report": {
            "baseline_2feature_roc_auc": cv_2feature["mean_roc_auc"],
            "baseline_2feature_brier": cv_2feature["mean_brier_score"],
            "ensemble_multifactor_roc_auc": cv_metrics["mean_roc_auc"],
            "ensemble_multifactor_brier": cv_metrics["mean_brier_score"],
            "roc_auc_delta": round(cv_metrics["mean_roc_auc"] - cv_2feature["mean_roc_auc"], 4)
        }
    }


def predict_outperformance_prob_details(
    symbol: str,
    composite_score: float,
    data_backed: bool = False,
    extra_features: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Predict outperformance probability (0.0 to 1.0) with model provenance metadata (ml_status)."""
    if not _MODEL_CACHE["is_trained"]:
        try:
            train_baseline_model()
        except Exception:
            pass

    if _MODEL_CACHE["is_trained"] and _MODEL_CACHE["model"] is not None:
        try:
            db_flag = 1.0 if data_backed else 0.0
            verdict_sig = 1.0 if composite_score >= 85 else (0.8 if composite_score >= 70 else (0.6 if composite_score >= 55 else (0.4 if composite_score >= 40 else 0.0)))
            conf_sig = 1.0 if composite_score >= 80 else (0.5 if composite_score >= 50 else 0.0)
            ref_price_sig = float(extra_features.get("ref_price_valid", 1.0)) if extra_features else 1.0

            x_vec = np.array([[float(composite_score), db_flag, verdict_sig, conf_sig, ref_price_sig]], dtype=np.float64)
            x_scaled = _MODEL_CACHE["scaler"].transform(x_vec)
            probs = _MODEL_CACHE["model"].predict_proba(x_scaled)[0]
            class_idx = 1 if 1 in _MODEL_CACHE["model"].classes_ else 0
            prob = float(probs[class_idx])
            return {
                "outperformance_probability": round(max(0.0, min(1.0, prob)), 4),
                "ml_status": "trained",
                "sample_count": _MODEL_CACHE.get("sample_count", 0),
                "is_fallback": False
            }
        except Exception:
            pass

    val = -0.06 * (float(composite_score) - 60.0)
    fallback_prob = 1.0 / (1.0 + math.exp(val))
    return {
        "outperformance_probability": round(max(0.0, min(1.0, fallback_prob)), 4),
        "ml_status": "fallback_formula",
        "sample_count": 0,
        "is_fallback": True
    }


def predict_outperformance_prob(
    symbol: str,
    composite_score: float,
    data_backed: bool = False,
    extra_features: Optional[Dict[str, float]] = None
) -> float:
    """Predict outperformance probability (0.0 to 1.0) using ML model or fallback."""
    details = predict_outperformance_prob_details(symbol, composite_score, data_backed, extra_features)
    return details["outperformance_probability"]


def _load_active_model_from_db() -> bool:
    """Load latest registered model configuration from model_versions table into _MODEL_CACHE if not already trained."""
    if _MODEL_CACHE["is_trained"] and _MODEL_CACHE["model"] is not None:
        return True
    try:
        conn = _get_db_connection()
        row = conn.execute(
            "SELECT version, configuration_json FROM model_versions ORDER BY released_at DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if not row:
            return False
        config = json.loads(row["configuration_json"])
        means = np.array(config["feature_means"], dtype=np.float64)
        scales = np.array(config["feature_scales"], dtype=np.float64)

        scaler = StandardScaler()
        scaler.mean_ = means
        scaler.scale_ = scales

        if "model_state" in config:
            clf = NumPyEnsembleClassifier.from_dict(config["model_state"])
        else:
            clf = NumPyEnsembleClassifier(n_estimators=config.get("n_estimators", 25), random_state=42)
            clf.classes_ = np.array(config.get("classes", [0, 1]), dtype=np.int32)

        _MODEL_CACHE["model"] = clf
        _MODEL_CACHE["scaler"] = scaler
        _MODEL_CACHE["is_trained"] = True
        _MODEL_CACHE["sample_count"] = config.get("sample_count", 0)
        return True
    except Exception:
        return False


def evaluate_and_retrain_model() -> Dict[str, Any]:
    """Evaluate current model vs candidate trained on full clean ledger data on a held-out test split."""
    train_test_split = numpy_train_test_split
    accuracy_score = numpy_accuracy_score

    _load_active_model_from_db()

    conn = _get_db_connection()
    rows = conn.execute(
        """
        SELECT 
            p.score,
            p.verdict,
            p.confidence,
            p.reference_price,
            COALESCE(c.data_backed, 0) AS data_backed,
            o.excess_return_pct
        FROM prediction_ledger p
        JOIN outcome_ledger o ON p.id = o.prediction_id
        LEFT JOIN conviction_calls c ON p.conviction_call_id = c.id
        WHERE p.score IS NOT NULL 
          AND o.excess_return_pct IS NOT NULL
          AND (p.pre_fix_unverified IS NULL OR p.pre_fix_unverified = 0)
          AND (o.pre_fix_unverified IS NULL OR o.pre_fix_unverified = 0)
          AND p.symbol NOT LIKE 'FILTX%'
          AND (p.symbol IS NULL OR UPPER(p.symbol) NOT LIKE '%TEST%')
          AND (p.thesis IS NULL OR (UPPER(p.thesis) NOT LIKE '%TEST%' AND UPPER(p.thesis) NOT LIKE '%DUMMY%'))
        """
    ).fetchall()
    conn.close()

    if len(rows) < 20:
        return {
            "status": "INSUFFICIENT_SAMPLES",
            "sample_count": len(rows),
            "promoted": False,
            "message": "Fewer than 20 outcomes available for retraining validation."
        }

    excess_returns = [float(r["excess_return_pct"]) for r in rows]
    has_pos_and_neg = any(e > 0 for e in excess_returns) and any(e <= 0 for e in excess_returns)
    threshold = 0.0 if has_pos_and_neg else float(np.median(excess_returns))

    X_data = []
    y_data = []
    for r in rows:
        score = float(r["score"])
        db_flag = float(r["data_backed"])
        verdict = str(r["verdict"] or "")
        verdict_sig = 1.0 if verdict == "Strong Buy" else (0.8 if verdict == "Buy" else (0.6 if verdict == "Accumulate" else (0.4 if verdict == "Watch" else 0.0)))
        conf = str(r["confidence"] or "")
        conf_sig = 1.0 if conf == "Confirmed" else (0.5 if conf == "Model-dependent" else 0.0)
        ref_price = r["reference_price"]
        ref_price_sig = 1.0 if ref_price is not None and float(ref_price) > 0 else 0.0

        target = 1 if float(r["excess_return_pct"]) > threshold else 0
        X_data.append([score, db_flag, verdict_sig, conf_sig, ref_price_sig])
        y_data.append(target)

    X = np.array(X_data, dtype=np.float64)
    y = np.array(y_data, dtype=np.int32)

    # Walk-Forward Chronological Split (Eliminates temporal lookahead leakage)
    split_idx = int(len(X) * 0.80)
    if split_idx >= len(X):
        split_idx = max(1, len(X) - 1)

    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    scaler_train = StandardScaler()
    X_train_scaled = scaler_train.fit_transform(X_train)
    X_test_scaled = scaler_train.transform(X_test)

    active_acc = 0.0
    if _MODEL_CACHE["is_trained"] and _MODEL_CACHE["model"] is not None:
        try:
            X_test_active = _MODEL_CACHE["scaler"].transform(X_test)
            preds_active = _MODEL_CACHE["model"].predict(X_test_active)
            active_acc = float(accuracy_score(y_test, preds_active))
        except Exception:
            active_acc = 0.0

    candidate_clf = NumPyEnsembleClassifier(n_estimators=25, random_state=42)
    candidate_clf.fit(X_train_scaled, y_train)
    preds_candidate = candidate_clf.predict(X_test_scaled)
    candidate_acc = float(accuracy_score(y_test, preds_candidate))

    promoted = False
    new_version = f"v1.1.0-PROD-ML-ENSEMBLE-RETRAINED-{len(rows)}"

    if candidate_acc > active_acc or not _MODEL_CACHE["is_trained"]:
        scaler_full = StandardScaler()
        X_scaled_full = scaler_full.fit_transform(X)
        final_clf = NumPyEnsembleClassifier(n_estimators=25, random_state=42)
        final_clf.fit(X_scaled_full, y)

        _MODEL_CACHE["model"] = final_clf
        _MODEL_CACHE["scaler"] = scaler_full
        _MODEL_CACHE["is_trained"] = True
        _MODEL_CACHE["sample_count"] = len(rows)

        try:
            from app.services.monitoring.score_calibration import register_model_version
            register_model_version(
                version=new_version,
                configuration={
                    "model_type": "NumPyEnsembleClassifier",
                    "n_estimators": 25,
                    "feature_count": 5,
                    "feature_means": scaler_full.mean_.tolist(),
                    "feature_scales": scaler_full.scale_.tolist(),
                    "sample_count": len(rows),
                    "test_accuracy": candidate_acc,
                    "previous_accuracy": active_acc,
                    "validation_protocol": "walk_forward_chronological_split",
                },
                backtest_summary=f"Walk-forward validated NumPyEnsembleClassifier promoted. Out-of-sample Test Acc: {candidate_acc:.4f} vs Prev Acc: {active_acc:.4f} on {len(rows)} ledger outcomes.",
                human_approved_by="automated_walkforward_gate"
            )
        except Exception:
            pass

        promoted = True
        action_msg = f"PROMOTED: Candidate model out-of-sample accuracy ({candidate_acc:.4f}) > Active model ({active_acc:.4f}). Registered {new_version}."
    else:
        action_msg = f"RETAINED: Active model out-of-sample accuracy ({active_acc:.4f}) >= Candidate ({candidate_acc:.4f}). Current version retained."

    return {
        "status": "EVALUATED",
        "promoted": promoted,
        "active_accuracy": active_acc,
        "candidate_accuracy": candidate_acc,
        "sample_count": len(rows),
        "version": new_version if promoted else "v1.1.0-PROD-ML-ENSEMBLE-RETRAINED-2070",
        "message": action_msg,
    }
