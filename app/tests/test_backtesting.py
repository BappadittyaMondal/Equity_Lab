"""Unit and integration tests for Phase 2 Point-in-Time Backtesting Engine.
"""

import os
from datetime import datetime, timezone
import pytest

from app.services.backtesting.replay_engine import PointInTimeReplayEngine
from app.services.backtesting.walk_forward import WalkForwardBacktester
from app.services.backtesting.score_bucket_analysis import ScoreCalibrator
from app.core.config import settings


@pytest.fixture
def temp_db_path():
    os.makedirs("data", exist_ok=True)
    db_file = os.path.abspath("data/test_backtesting.sqlite")
    original = settings.DATA_STORE_PATH
    settings.DATA_STORE_PATH = db_file
    from app.services.db import _ensure_tables
    _ensure_tables()
    yield db_file
    settings.DATA_STORE_PATH = original
    import gc
    gc.collect()
    try:
        from app.services.db import close_all_connections
        close_all_connections()
    except Exception:
        pass
    gc.collect()



def test_point_in_time_replay_engine(temp_db_path):
    replay = PointInTimeReplayEngine()
    as_of = datetime.now(timezone.utc)
    res = replay.replay_analysis("TATAMOTORS", as_of)
    assert res.symbol == "TATAMOTORS.NS"
    assert res.historical_score >= 0
    assert res.verdict in ("Strong Buy", "Buy", "Accumulate", "Watch", "Avoid", "ABSTAIN")
    assert res.data_snapshot.as_of == as_of


def test_replay_engine_passes_as_of_to_arbiter(monkeypatch):
    from unittest.mock import MagicMock
    replay = PointInTimeReplayEngine()
    mock_arbiter = MagicMock()
    fake_call = MagicMock(
        conviction_score=80,
        verdict="Buy",
        confidence_tier="Confirmed",
        contributing_engines=["E1"],
        contradicting_engines=[],
    )
    mock_arbiter.arbitrate.return_value = fake_call
    replay.arbiter = mock_arbiter

    as_of = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    res = replay.replay_analysis("INFY", as_of)

    mock_arbiter.arbitrate.assert_called_once_with("INFY.NS", as_of=as_of)
    assert res.analysis_date == as_of.isoformat()
    assert res.historical_score == 80



def test_walk_forward_backtester():
    tester = WalkForwardBacktester()
    samples = [
        {"stock_return": 25.0},
        {"stock_return": 15.0},
        {"stock_return": -5.0},
        {"stock_return": 30.0},
    ]
    bm = [8.0, 8.0, 8.0, 8.0]
    summary = tester.evaluate_horizon("INFY", 12, samples, bm, slippage_pct=0.0, stt_brokerage_pct=0.0)
    assert summary.symbol == "INFY.NS"
    assert summary.total_samples == 4
    assert summary.win_rate_pct == 75.0
    assert summary.mean_stock_return == 16.25
    assert summary.mean_alpha == 8.25


def test_walk_forward_backtester_with_transaction_costs():
    tester = WalkForwardBacktester()
    samples = [
        {"stock_return": 25.0},
        {"stock_return": 15.0},
        {"stock_return": -5.0},
        {"stock_return": 30.0},
    ]
    bm = [8.0, 8.0, 8.0, 8.0]
    summary = tester.evaluate_horizon("INFY", 12, samples, bm, slippage_pct=0.05, stt_brokerage_pct=0.10)
    assert summary.symbol == "INFY.NS"
    assert summary.mean_stock_return == 16.10  # 16.25 - 0.15
    assert summary.mean_alpha == 8.10


def test_score_calibration():
    calibrator = ScoreCalibrator()
    samples = [
        {"symbol": "RELIANCE", "conviction_score": 95, "forward_return": 30.0, "contributing_engines": ["E1", "E4"]},
        {"symbol": "TCS", "conviction_score": 85, "forward_return": 18.0, "contributing_engines": ["E1"]},
        {"symbol": "WIPRO", "conviction_score": 55, "forward_return": 5.0, "contributing_engines": ["E2"]},
        {"symbol": "BADCO", "conviction_score": 20, "forward_return": -15.0, "contributing_engines": []},
        {"symbol": "FALSE_POS", "conviction_score": 80, "forward_return": -12.0, "contributing_engines": ["D15"]},
        {"symbol": "FALSE_NEG", "conviction_score": 40, "forward_return": 35.0, "contributing_engines": ["E2"]},
    ]
    report = calibrator.calibrate(samples)
    assert report.total_evaluations == 6
    assert "90–100" in report.bucket_metrics
    assert len(report.false_positives) == 1
    assert len(report.false_negatives) == 1
    assert report.score_monotonicity_verified is True


def test_spa_stationary_block_bootstrap_and_pit_forwarding():
    """Verify White's SPA runs stationary block bootstrap and evaluate_backtest_validation forwards as_of."""
    import numpy as np
    from app.services.backtesting.validation_framework import (
        compute_family_wise_significance_spa,
        evaluate_backtest_validation
    )

    # 1. Test SPA with actual observed return distribution
    ic_map = {
        "Factor_A": 0.18,
        "Factor_B": 0.05,
        "Factor_C": -0.02,
        "Factor_D": 0.12,
    }
    dummy_returns = np.sin(np.linspace(0, 20, 100)) * 0.02
    spa_res = compute_family_wise_significance_spa(
        ic_map,
        num_bootstrap_draws=100,
        observed_returns=dummy_returns
    )
    assert spa_res["total_modules_tested"] == 4
    assert spa_res["bootstrap_draws_executed"] == 100
    assert "spa_critical_value" in spa_res
    assert isinstance(spa_res["adjusted_ic_by_module"], dict)

    # 2. Test Point-in-Time as_of parameter acceptance
    as_of = datetime(2025, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
    res = evaluate_backtest_validation("TCS", as_of=as_of)
    assert res["symbol"] == "TCS.NS"
    assert "ic_by_factor" in res
    assert res["average_ic"] > 0.0

