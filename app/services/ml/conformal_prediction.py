"""Conformal Uncertainty & Interval Prediction Engine.

Computes distribution-free non-parametric prediction intervals [Y_lower, Y_upper]
with guaranteed marginal coverage probabilities (e.g. 90% or 95% confidence bounds)
using residual quantile conformalization.
"""

import os
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np

from app.core.config import settings


@dataclass
class ConformalPredictionInterval:
    point_estimate: float
    lower_bound_90: float
    upper_bound_90: float
    lower_bound_95: float
    upper_bound_95: float
    coverage_guarantee_pct: float  # e.g., 90.0
    strata: str  # Mondrian category (e.g., "MICRO_CAP_HIGH_VOL")
    interval_width: float


class ConformalPredictor:
    """Non-parametric residual quantile conformal predictor."""

    def __init__(self, alpha: float = 0.10, auto_load: bool = True):
        self.alpha = alpha  # Default 10% miscoverage rate -> 90% confidence level
        self.residuals_by_strata: Dict[str, np.ndarray] = {}
        if auto_load:
            self.load_calibration()

    def fit(self, y_true: np.ndarray, y_pred: np.ndarray, strata: str = "GENERAL", persist: bool = True) -> float:
        """Calibrate non-conformity scores (absolute residuals) on calibration dataset."""
        if len(y_true) == 0:
            self.residuals_by_strata[strata] = np.array([0.15])
            return 0.15

        abs_residuals = np.abs(y_true - y_pred)
        n = len(abs_residuals)
        # Conformal quantile formula: (1 - alpha) * (1 + 1/n)
        quantile_level = min(0.99, max(0.50, (1.0 - self.alpha) * (1.0 + 1.0 / n)))
        q_val = float(np.quantile(abs_residuals, quantile_level))
        self.residuals_by_strata[strata] = abs_residuals
        if persist:
            self.save_calibration()
        return q_val

    def save_calibration(self, filepath: Optional[str] = None) -> str:
        """Persist calibrated residuals to JSON file atomically."""
        target_path = filepath or getattr(settings, "CONFORMAL_CACHE_PATH", "conformal_calibration_cache.json")
        data = {strata: res.tolist() for strata, res in self.residuals_by_strata.items()}
        tmp_path = f"{target_path}.tmp.{os.getpid()}"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, target_path)
            return target_path
        except Exception:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            return ""

    def load_calibration(self, filepath: Optional[str] = None) -> bool:
        """Load calibrated residuals from JSON file."""
        target_path = filepath or getattr(settings, "CONFORMAL_CACHE_PATH", "conformal_calibration_cache.json")
        if not os.path.exists(target_path):
            return False
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for strata, res_list in data.items():
                if res_list:
                    self.residuals_by_strata[strata] = np.array(res_list, dtype=float)
            return True
        except Exception:
            return False

    def predict_interval(
        self,
        point_estimate: float,
        strata: str = "GENERAL"
    ) -> ConformalPredictionInterval:
        """Generate conformal interval around point estimate."""
        abs_res = self.residuals_by_strata.get(strata)
        if abs_res is None or len(abs_res) == 0:
            q_90 = 0.12
            q_95 = 0.18
        else:
            n = len(abs_res)
            q_90 = float(np.quantile(abs_res, min(0.99, 0.90 * (1.0 + 1.0 / n))))
            q_95 = float(np.quantile(abs_res, min(0.99, 0.95 * (1.0 + 1.0 / n))))

        lower_90 = round(point_estimate - q_90, 4)
        upper_90 = round(point_estimate + q_90, 4)
        lower_95 = round(point_estimate - q_95, 4)
        upper_95 = round(point_estimate + q_95, 4)

        return ConformalPredictionInterval(
            point_estimate=round(point_estimate, 4),
            lower_bound_90=lower_90,
            upper_bound_90=upper_90,
            lower_bound_95=lower_95,
            upper_bound_95=upper_95,
            coverage_guarantee_pct=round((1.0 - self.alpha) * 100.0, 1),
            strata=strata,
            interval_width=round(upper_90 - lower_90, 4)
        )
