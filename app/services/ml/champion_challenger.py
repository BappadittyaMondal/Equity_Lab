"""Champion/Challenger Model Benchmarking Engine.

Evaluates out-of-sample prediction accuracy across candidate forecasting models:
- Champion: Baseline GBDT Stump Ensemble
- Challenger A: LightGBM / CatBoost Tabular Model
- Challenger B: Chronos-2 Zero-Shot Time-Series Model

Calculates empirical Mean Absolute Error (MAE), Root Mean Squared Error (RMSE),
and Brier Score before promoting any model to Champion status.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np


@dataclass
class ModelBenchmarkResult:
    model_name: str
    mae: float
    rmse: float
    brier_score: float
    is_champion: bool
    samples_evaluated: int


class ChampionChallengerEvaluator:
    """Out-of-sample model benchmark runner."""

    def evaluate_models(
        self,
        y_true: np.ndarray,
        predictions_dict: Dict[str, np.ndarray],
        current_champion_name: str = "Baseline_GBDT_Ensemble"
    ) -> List[ModelBenchmarkResult]:
        """Evaluate out-of-sample accuracy across candidate models."""
        if len(y_true) == 0:
            return []

        results = []
        n = len(y_true)

        for name, preds in predictions_dict.items():
            if len(preds) != n:
                continue

            errors = y_true - preds
            mae = float(np.mean(np.abs(errors)))
            rmse = float(np.sqrt(np.mean(errors ** 2)))

            # Brier Score calculation for binary direction target
            y_binary = (y_true > 0).astype(float)
            p_binary = np.clip(preds, 0.0, 1.0)
            brier = float(np.mean((p_binary - y_binary) ** 2))

            results.append(ModelBenchmarkResult(
                model_name=name,
                mae=round(mae, 4),
                rmse=round(rmse, 4),
                brier_score=round(brier, 4),
                is_champion=(name == current_champion_name),
                samples_evaluated=n
            ))

        results.sort(key=lambda r: r.brier_score)
        return results
