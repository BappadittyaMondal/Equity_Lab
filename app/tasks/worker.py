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
        # Sample quotes refresh
        sample_symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
        refreshed = 0
        for sym in sample_symbols:
            try:
                get_market_quote(sym)
                refreshed += 1
            except Exception as e:
                logger.warning("Error refreshing %s: %s", sym, e)
        return {"status": "success", "refreshed_count": refreshed, "universe": symbol_universe}
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


class WorkerSettings:
    """ARQ Worker Settings."""
    functions = [refresh_market_data_task, retrain_ml_model_task]
    redis_settings = settings.REDIS_URL if hasattr(settings, "REDIS_URL") and settings.REDIS_URL else "redis://localhost:6379/0"
    max_jobs = 10
    poll_delay = 0.5
