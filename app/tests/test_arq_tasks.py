# -*- coding: utf-8 -*-
"""Test suite for ARQ task worker and scheduler configuration."""

import pytest
from app.tasks.worker import refresh_market_data_task, retrain_ml_model_task, evaluate_champion_challenger_task, WorkerSettings
from app.tasks.scheduler import get_schedule_summary


@pytest.mark.anyio
async def test_arq_market_data_task_execution():
    ctx = {}
    res = await refresh_market_data_task(ctx, symbol_universe="NIFTY50")
    assert res["status"] == "success"
    assert "refreshed_count" in res


@pytest.mark.anyio
async def test_arq_ml_task_execution():
    ctx = {}
    res = await retrain_ml_model_task(ctx)
    assert res["status"] == "success"
    assert "metrics" in res


@pytest.mark.anyio
async def test_arq_champion_challenger_task_execution():
    ctx = {}
    res = await evaluate_champion_challenger_task(ctx)
    assert res["status"] == "success"
    assert "benchmarks" in res


def test_arq_scheduler_summary():
    summary = get_schedule_summary()
    assert summary["scheduled_jobs"] == 2
    assert len(summary["schedule"]) == 2


def test_worker_settings():
    assert len(WorkerSettings.functions) == 3
    assert evaluate_champion_challenger_task in WorkerSettings.functions
