# -*- coding: utf-8 -*-
"""ARQ Cron Task Scheduler definitions."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

CRON_SCHEDULE = [
    {
        "name": "refresh_market_data_6h",
        "task": "refresh_market_data_task",
        "cron": "0 */6 * * *",
        "kwargs": {"symbol_universe": "NIFTY500"}
    },
    {
        "name": "retrain_ml_model_daily",
        "task": "retrain_ml_model_task",
        "cron": "0 2 * * *",
        "kwargs": {}
    }
]

def get_schedule_summary() -> Dict[str, Any]:
    return {
        "scheduled_jobs": len(CRON_SCHEDULE),
        "schedule": CRON_SCHEDULE
    }
