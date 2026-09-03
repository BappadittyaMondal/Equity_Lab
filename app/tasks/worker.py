# -*- coding: utf-8 -*-
"""ARQ (Async Redis Queue) worker settings and task handlers.

Offloads heavy market data updates and ML model retraining outside
FastAPI web server event loops.
"""

import asyncio
import logging
from typing import Any, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)


async def refresh_market_data_task(ctx: Dict[str, Any], symbol_universe: str = "NIFTY50") -> Dict[str, Any]:
    """Asynchronous background task to refresh market quotes and fundamentals."""
    logger.info("Executing background market data refresh for universe: %s", symbol_universe)
    try:
        from app.services.market_data import get_market_quote
        try:
            from app.services.ingestion.universe_discovery import get_universe_symbols
            target_symbols = get_universe_symbols(symbol_universe)
        except Exception:
            target_symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

        # Limit per batch if universe is large to avoid API rate limits
        batch_limit = int(ctx.get("batch_limit", 50)) if isinstance(ctx, dict) else 50
        symbols_to_run = target_symbols[:batch_limit]

        refreshed = 0
        for sym in symbols_to_run:
            try:
                get_market_quote(sym)
                refreshed += 1
            except Exception as e:
                logger.warning("Error refreshing %s: %s", sym, e)
        return {
            "status": "success",
            "refreshed_count": refreshed,
            "total_universe_count": len(target_symbols),
            "universe": symbol_universe,
        }
    except Exception as exc:
        logger.error("Market data refresh task failed: %s", exc)
        return {"status": "error", "error": str(exc)}


async def retrain_ml_model_task(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Asynchronous background task to retrain baseline ML model."""
    logger.info("Executing background ML baseline model retraining task...")
    try:
        try:
            from app.services.ml.baseline_model import evaluate_and_retrain_model
        except ImportError:
            from services.ml.baseline_model import evaluate_and_retrain_model
        results = evaluate_and_retrain_model()
        return {"status": "success", "metrics": results}
    except Exception as exc:
        logger.error("ML model retraining task failed: %s", exc)
        return {"status": "error", "error": str(exc)}


async def evaluate_champion_challenger_task(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Asynchronous background task to benchmark champion vs challenger forecasting models."""
    logger.info("Executing background Champion/Challenger model evaluation task...")
    try:
        from app.services.ml.champion_challenger import ChampionChallengerEvaluator
        import numpy as np
        evaluator = ChampionChallengerEvaluator()

        # Attempt to load real resolved prediction outcomes from database
        rows = []
        try:
            from app.services.db import get_connection
            conn = get_connection()
            rows = conn.execute(
                """SELECT o.actual_return_pct, p.score
                   FROM outcome_ledger o
                   JOIN prediction_ledger p ON o.prediction_id = p.id
                   ORDER BY o.id DESC LIMIT 50"""
            ).fetchall()
            conn.close()
        except Exception as db_err:
            logger.debug("Database outcome ledger query skipped: %s", db_err)
            rows = []

        import os
        is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"

        if rows and len(rows) >= 5:
            y_test = np.array([float(r["actual_return_pct"] or 0.0) for r in rows])
            baseline_preds = np.array([(float(r["score"] or 50.0) - 50.0) * 0.4 for r in rows])
            challenger_preds = baseline_preds * 0.95 + float(np.mean(y_test)) * 0.05
            preds = {
                "Baseline_Decision_Score_Proxy": baseline_preds,
                "Challenger_Regularized_Mean": challenger_preds,
            }
            benchmarks = evaluator.evaluate_models(y_test, preds)
            results = [b.__dict__ if hasattr(b, "__dict__") else str(b) for b in benchmarks]
            return {"status": "success", "data_mode": "EMPIRICAL_LEDGER", "sample_size": len(rows), "benchmarks": results}
        elif is_offline:
            # Deterministic test fixture for offline test mode only
            y_test = np.array([2.5, -1.2, 3.8, -0.5, 1.9, -2.1, 4.0, 0.5])
            preds = {
                "Baseline_GBDT_Ensemble": np.array([2.1, -0.8, 3.2, -0.2, 1.5, -1.8, 3.5, 0.3]),
                "LightGBM_Challenger": np.array([2.4, -1.0, 3.6, -0.4, 1.8, -2.0, 3.9, 0.4]),
            }
            benchmarks = evaluator.evaluate_models(y_test, preds)
            results = [b.__dict__ if hasattr(b, "__dict__") else str(b) for b in benchmarks]
            return {"status": "success", "data_mode": "TEST_FIXTURE", "benchmarks": results}
        else:
            return {
                "status": "BOOTSTRAPPING",
                "sample_size": len(rows),
                "data_mode": "INSUFFICIENT_OUTCOMES",
                "message": "Awaiting minimum 5 resolved outcomes in outcome_ledger before benchmarking champion vs challenger models."
            }
    except Exception as exc:
        logger.error("Champion/Challenger evaluation task failed: %s", exc)
        return {"status": "error", "error": str(exc)}


class WorkerSettings:
    """ARQ Worker Settings."""
    functions = [refresh_market_data_task, retrain_ml_model_task, evaluate_champion_challenger_task]
    try:
        from arq.connections import RedisSettings
        _redis_url = getattr(settings, "REDIS_URL", None) or "redis://localhost:6379/0"
        redis_settings = RedisSettings.from_dsn(_redis_url)
    except Exception:
        redis_settings = getattr(settings, "REDIS_URL", None) or "redis://localhost:6379/0"
    max_jobs = 10
    poll_delay = 0.5
