"""Extreme Value Theory (EVT) GPD Engine — Tail Fitting for Breakout Volatility (§1B).

Fits Generalized Pareto Distribution (GPD) to extreme positive return exceedances:
F_u(y) = 1 - (1 + \\xi y / \\sigma)^{-1/\\xi}

Enables institutional point-in-time calculation of 99th percentile breakout return potential and tail risk.
"""

import logging
from typing import Any, Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class EVTGPDEngine:
    """Extreme Value Theory (EVT) Generalized Pareto Distribution (GPD) Tail Model."""

    @staticmethod
    def fit_gpd_tail_exceedances(
        returns: np.ndarray,
        threshold_quantile: float = 0.90,
    ) -> Dict[str, Any]:
        """Fits GPD parameters (scale sigma, shape xi) to returns exceeding threshold_quantile.

        Positive xi -> Heavy-tailed distribution (Power law / Multibagger potential)
        Negative xi -> Short-tailed distribution (Bounded returns)
        """
        if returns is None or len(returns) < 30:
            return {
                "threshold": 0.03,
                "exceedance_count": 0,
                "scale_sigma": 0.02,
                "shape_xi": 0.15,
                "tail_type": "HEAVY_TAILED",
                "var_99_pct": 5.5,
                "expected_shortfall_99_pct": 7.2,
            }

        clean_rets = np.sort(returns[~np.isnan(returns)])
        threshold = float(np.quantile(clean_rets, threshold_quantile))
        exceedances = clean_rets[clean_rets > threshold] - threshold

        n_exceed = len(exceedances)
        if n_exceed < 5:
            return {
                "threshold": round(threshold, 4),
                "exceedance_count": n_exceed,
                "scale_sigma": 0.02,
                "shape_xi": 0.10,
                "tail_type": "LIGHT_TAILED",
                "var_99_pct": round(threshold * 1.5 * 100.0, 2),
                "expected_shortfall_99_pct": round(threshold * 2.0 * 100.0, 2),
            }

        mean_exc = float(np.mean(exceedances))
        var_exc = float(np.var(exceedances))

        # Method-of-moments estimator for GPD parameters (sigma, xi)
        if var_exc > 0:
            shape_xi = 0.5 * (((mean_exc ** 2) / var_exc) - 1.0)
            scale_sigma = 0.5 * mean_exc * (((mean_exc ** 2) / var_exc) + 1.0)
        else:
            shape_xi = 0.10
            scale_sigma = max(0.01, mean_exc)

        shape_xi = float(np.clip(shape_xi, -0.5, 0.8))
        scale_sigma = float(max(0.005, scale_sigma))

        if shape_xi > 0.15:
            tail_type = "VERY_HEAVY_TAILED_MULTIBAGGER_CONVEXITY"
        elif shape_xi > 0.0:
            tail_type = "MODERATE_HEAVY_TAILED"
        else:
            tail_type = "THIN_TAILED"

        # Calculate 99th percentile Value-at-Risk / Expected Shortfall
        prob_exceed = n_exceed / len(clean_rets)
        q99 = threshold + (scale_sigma / max(0.01, shape_xi)) * (((0.01 / prob_exceed) ** (-shape_xi)) - 1.0)
        es99 = (q99 + scale_sigma - shape_xi * threshold) / (1.0 - shape_xi)

        return {
            "threshold": round(threshold, 4),
            "exceedance_count": n_exceed,
            "scale_sigma": round(scale_sigma, 4),
            "shape_xi": round(shape_xi, 4),
            "tail_type": tail_type,
            "var_99_pct": round(float(q99) * 100.0, 2),
            "expected_shortfall_99_pct": round(float(es99) * 100.0, 2),
        }
