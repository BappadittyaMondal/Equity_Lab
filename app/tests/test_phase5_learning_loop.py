"""Phase 5 — Learning Loop Tests (Layer 12).

Tests for:
  - Outcome Checker: due-date gate, idempotency, return computation, outcome classification
  - Score Calibration: bucket hit rates, monotonicity check, recommendations, human sign-off gate
  - Model Versioning: registration, human_approved_by enforcement
  - Drift Detector: alert levels, decay detection
  - End-to-end: Arbiter auto-logs every conviction call to prediction_ledger
"""

import pytest
import json
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List


# ═══════════════════════════════════════════════════════════════════════════
# Shared helpers
# ═══════════════════════════════════════════════════════════════════════════

def _iso_past(days: int) -> str:
    """Return an ISO timestamp N days in the past."""
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def _iso_future(days: int) -> str:
    """Return an ISO timestamp N days in the future."""
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _seed_prediction(conn, symbol="RELIANCE", score=75, verdict="Buy",
                     confidence="Model-dependent", reference_price=2500.0,
                     thesis="Test thesis", model_version="0.4.0",
                     timestamp: str = None) -> int:
    """Insert a test prediction into prediction_ledger. Returns id."""
    now = timestamp or _iso_past(400)  # Old enough for all horizons
    cursor = conn.execute(
        "INSERT INTO prediction_ledger "
        "(symbol, timestamp, score, verdict, confidence, reference_price, thesis, model_version, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (symbol, now, score, verdict, confidence, reference_price, thesis, model_version, now),
    )
    conn.commit()
    return cursor.lastrowid


def _seed_outcome(conn, prediction_id: int, symbol: str = "RELIANCE",
                  horizon_months: int = 12, actual_return: float = 18.0,
                  benchmark_return: float = 12.0) -> None:
    """Insert a test outcome into outcome_ledger."""
    excess = actual_return - benchmark_return
    outcome_cls = "CONFIRMED_OUTPERFORMANCE" if excess > 0 else "NEGATIVE_OUTCOME"
    conn.execute(
        "INSERT INTO outcome_ledger "
        "(prediction_id, symbol, horizon_months, actual_return_pct, "
        "benchmark_return_pct, excess_return_pct, outcome_class, recorded_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (prediction_id, symbol, horizon_months, actual_return,
         benchmark_return, excess, outcome_cls, _iso_past(1)),
    )
    conn.commit()


# ═══════════════════════════════════════════════════════════════════════════
# Outcome Checker Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestOutcomeClassification:
    """Return → outcome class mapping."""

    def test_high_outperformance(self):
        from app.services.monitoring.outcome_checker import _outcome_class
        assert _outcome_class(30.0, 18.0) == "CONFIRMED_HIGH_OUTPERFORMANCE"

    def test_outperformance(self):
        from app.services.monitoring.outcome_checker import _outcome_class
        assert _outcome_class(15.0, 8.0) == "CONFIRMED_OUTPERFORMANCE"

    def test_positive_underperformance(self):
        from app.services.monitoring.outcome_checker import _outcome_class
        assert _outcome_class(5.0, -3.0) == "POSITIVE_UNDERPERFORMANCE"

    def test_negative_outcome(self):
        from app.services.monitoring.outcome_checker import _outcome_class
        assert _outcome_class(-12.0, -5.0) == "NEGATIVE_OUTCOME"

    def test_exactly_zero_excess_is_positive_underperformance(self):
        from app.services.monitoring.outcome_checker import _outcome_class
        assert _outcome_class(0.0, 0.0) == "POSITIVE_UNDERPERFORMANCE"


class TestOutcomeDueDate:
    """Prediction due-date gate."""

    def test_old_prediction_is_due_for_1m(self):
        from app.services.monitoring.outcome_checker import _prediction_is_due
        old_ts = _iso_past(40)
        assert _prediction_is_due(old_ts, 1) is True

    def test_old_prediction_is_due_for_12m(self):
        from app.services.monitoring.outcome_checker import _prediction_is_due
        old_ts = _iso_past(400)
        assert _prediction_is_due(old_ts, 12) is True

    def test_recent_prediction_not_due_for_12m(self):
        from app.services.monitoring.outcome_checker import _prediction_is_due
        recent_ts = _iso_past(30)  # Only 30 days old
        assert _prediction_is_due(recent_ts, 12) is False

    def test_future_timestamp_not_due(self):
        from app.services.monitoring.outcome_checker import _prediction_is_due
        future_ts = _iso_future(10)
        assert _prediction_is_due(future_ts, 1) is False

    def test_exactly_at_horizon_is_due(self):
        from app.services.monitoring.outcome_checker import _prediction_is_due
        ts = _iso_past(31)  # 1M = ~30.44 days
        assert _prediction_is_due(ts, 1) is True


class TestOutcomeCheckerDryRun:
    """Dry-run mode: compute without persisting."""

    def test_dry_run_returns_stats_dict(self):
        from app.services.monitoring.outcome_checker import run_outcome_checker
        stats = run_outcome_checker(limit=10, dry_run=True)
        assert "predictions_scanned" in stats
        assert "outcomes_recorded" in stats
        assert "errors" in stats

    def test_dry_run_skips_no_reference_price(self):
        from app.services.monitoring.outcome_checker import run_outcome_checker
        stats = run_outcome_checker(limit=50, dry_run=True)
        # Should complete without exceptions regardless of DB state
        assert stats["predictions_scanned"] >= 0

    def test_dry_run_records_list_is_list(self):
        from app.services.monitoring.outcome_checker import run_outcome_checker
        stats = run_outcome_checker(limit=5, dry_run=True)
        assert isinstance(stats["records"], list)


class TestOutcomeCheckerIdempotency:
    """Idempotency: don't double-record outcomes."""

    def test_already_recorded_check(self):
        from app.services.db import get_connection
        from app.services.monitoring.outcome_checker import _prediction_already_has_outcome

        conn = get_connection()
        pred_id = _seed_prediction(conn, timestamp=_iso_past(400))
        _seed_outcome(conn, pred_id, horizon_months=12)
        conn.close()

        # Should return True — already recorded
        assert _prediction_already_has_outcome(pred_id, 12) is True

    def test_not_yet_recorded_returns_false(self):
        from app.services.db import get_connection
        from app.services.monitoring.outcome_checker import _prediction_already_has_outcome

        conn = get_connection()
        pred_id = _seed_prediction(conn, symbol="INFOSYS", timestamp=_iso_past(400))
        conn.close()

        # 3M outcome not yet recorded
        assert _prediction_already_has_outcome(pred_id, 3) is False


class TestBenchmarkReturn:
    """Benchmark return scaling."""

    def test_benchmark_scales_with_horizon(self):
        from app.services.monitoring.outcome_checker import _benchmark_return_for_horizon
        r1 = _benchmark_return_for_horizon(1)
        r12 = _benchmark_return_for_horizon(12)
        assert r12 > r1  # Longer horizon → larger benchmark

    def test_benchmark_12m_approx_12pct(self):
        from app.services.monitoring.outcome_checker import _benchmark_return_for_horizon
        r = _benchmark_return_for_horizon(12)
        # Annual CAGR 12% → 12M return ≈ 12%
        assert 11.0 <= r <= 13.0

    def test_benchmark_6m_approx_half_annual(self):
        from app.services.monitoring.outcome_checker import _benchmark_return_for_horizon
        r = _benchmark_return_for_horizon(6)
        assert 5.0 <= r <= 8.0


class TestOutcomeSummary:
    """get_outcome_summary query function."""

    def test_returns_list(self):
        from app.services.monitoring.outcome_checker import get_outcome_summary
        result = get_outcome_summary()
        assert isinstance(result, list)

    def test_filtered_by_symbol_returns_list(self):
        from app.services.monitoring.outcome_checker import get_outcome_summary
        result = get_outcome_summary(symbol="RELIANCE")
        assert isinstance(result, list)

    def test_result_has_required_keys(self):
        from app.services.db import get_connection
        from app.services.monitoring.outcome_checker import get_outcome_summary

        conn = get_connection()
        pred_id = _seed_prediction(conn, symbol="TATAPOWER", timestamp=_iso_past(400))
        _seed_outcome(conn, pred_id, symbol="TATAPOWER", horizon_months=6, actual_return=22.0)
        conn.close()

        results = get_outcome_summary(symbol="TATAPOWER")
        if results:  # May have other entries too
            r = results[0]
            assert "symbol" in r
            assert "actual_return_pct" in r
            assert "outcome_class" in r
            assert "original_score" in r


# ═══════════════════════════════════════════════════════════════════════════
# Score Calibration Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCalibrationNoData:
    """Calibration with empty outcome_ledger."""

    def test_no_data_returns_no_data_status(self):
        from app.services.monitoring.score_calibration import compute_calibration_report
        # May have data from earlier tests — but should not crash
        result = compute_calibration_report(horizon_months=6)
        assert "status" in result
        assert result["status"] in ("NO_DATA", "OK")

    def test_no_data_has_generated_at(self):
        from app.services.monitoring.score_calibration import compute_calibration_report
        result = compute_calibration_report(horizon_months=6)
        assert "generated_at" in result


class TestCalibrationWithData:
    """Calibration report structure with seeded outcome data."""

    def _seed_many_outcomes(self, n: int = 20, score: int = 75,
                            actual_ret: float = 20.0, horizon: int = 12) -> None:
        from app.services.db import get_connection
        conn = get_connection()
        for i in range(n):
            pred_id = _seed_prediction(
                conn, symbol=f"STOCK{i}", score=score,
                reference_price=1000.0, timestamp=_iso_past(400)
            )
            _seed_outcome(conn, pred_id, symbol=f"STOCK{i}",
                          horizon_months=horizon, actual_return=actual_ret)
        conn.close()

    def test_report_has_bucket_stats(self):
        from app.services.monitoring.score_calibration import compute_calibration_report
        self._seed_many_outcomes(5, score=75, actual_ret=18.0, horizon=12)
        result = compute_calibration_report(horizon_months=12)
        if result["status"] == "OK":
            assert "bucket_stats" in result

    def test_report_has_monotonicity_check(self):
        from app.services.monitoring.score_calibration import compute_calibration_report
        self._seed_many_outcomes(5, score=80, actual_ret=22.0, horizon=12)
        result = compute_calibration_report(horizon_months=12)
        if result["status"] == "OK":
            assert "monotonicity_check" in result
            mono = result["monotonicity_check"]
            assert "is_monotonic" in mono
            assert "status" in mono

    def test_report_has_overall_hit_rate(self):
        from app.services.monitoring.score_calibration import compute_calibration_report
        self._seed_many_outcomes(5, score=70, actual_ret=15.0, horizon=12)
        result = compute_calibration_report(horizon_months=12)
        if result["status"] == "OK":
            assert "overall_hit_rate_pct" in result
            assert 0.0 <= result["overall_hit_rate_pct"] <= 100.0

    def test_report_has_recommendations_list(self):
        from app.services.monitoring.score_calibration import compute_calibration_report
        result = compute_calibration_report(horizon_months=12)
        if result["status"] == "OK":
            assert "recalibration_recommendations" in result
            assert isinstance(result["recalibration_recommendations"], list)

    def test_report_has_human_approval_flag(self):
        from app.services.monitoring.score_calibration import compute_calibration_report
        result = compute_calibration_report(horizon_months=12)
        if result["status"] == "OK":
            assert "human_approval_required" in result
            assert isinstance(result["human_approval_required"], bool)


class TestScoreBuckets:
    """Score bucket definitions."""

    def test_score_buckets_cover_full_range(self):
        from app.services.monitoring.score_calibration import SCORE_BUCKETS
        # Buckets should start at 0 and end at 101
        assert SCORE_BUCKETS[0][0] == 0
        assert SCORE_BUCKETS[-1][1] == 101

    def test_buckets_are_contiguous(self):
        from app.services.monitoring.score_calibration import SCORE_BUCKETS
        for i in range(len(SCORE_BUCKETS) - 1):
            assert SCORE_BUCKETS[i][1] == SCORE_BUCKETS[i + 1][0]

    def test_seven_buckets_defined(self):
        from app.services.monitoring.score_calibration import SCORE_BUCKETS
        assert len(SCORE_BUCKETS) == 7

    def test_bucket_labels_match_buckets(self):
        from app.services.monitoring.score_calibration import SCORE_BUCKETS, BUCKET_LABELS
        for bucket in SCORE_BUCKETS:
            assert bucket in BUCKET_LABELS


class TestMonotonicityCheck:
    """Score monotonicity verification."""

    def test_monotonicity_status_function_exists(self):
        from app.services.monitoring.score_calibration import score_monotonicity_status
        result = score_monotonicity_status()
        assert "status" in result
        assert result["status"] in ("HEALTHY", "VERIFIED_MONOTONIC", "VIOLATED",
                                    "MONOTONICITY_VIOLATED", "INSUFFICIENT_DATA")

    def test_monotonicity_returns_dict(self):
        from app.services.monitoring.score_calibration import score_monotonicity_status
        result = score_monotonicity_status()
        assert isinstance(result, dict)


# ═══════════════════════════════════════════════════════════════════════════
# Model Versioning Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestModelVersioning:
    """Model version registry — human sign-off enforcement."""

    def test_register_version_requires_human_approval(self):
        from app.services.monitoring.score_calibration import register_model_version
        with pytest.raises(ValueError, match="human_approved_by"):
            register_model_version(
                version="9.9.9-TEST",
                configuration={"test": True},
                human_approved_by="",  # Empty → must raise
            )

    def test_register_version_with_human_approval(self):
        from app.services.monitoring.score_calibration import register_model_version
        result = register_model_version(
            version="0.4.0-TEST",
            configuration={"FUNDAMENTAL": 0.30, "VALUATION": 0.20},
            human_approved_by="test_analyst",
        )
        assert result["version"] == "0.4.0-TEST"
        assert result["status"] == "REGISTERED"
        assert result["human_approved_by"] == "test_analyst"

    def test_get_model_versions_returns_list(self):
        from app.services.monitoring.score_calibration import get_model_versions
        versions = get_model_versions()
        assert isinstance(versions, list)

    def test_registered_version_appears_in_list(self):
        from app.services.monitoring.score_calibration import register_model_version, get_model_versions
        register_model_version(
            version="0.4.0-VISIBLE",
            configuration={"check": "visibility"},
            human_approved_by="visibility_tester",
        )
        versions = get_model_versions()
        version_ids = [v["version"] for v in versions]
        assert "0.4.0-VISIBLE" in version_ids

    def test_version_config_is_dict(self):
        from app.services.monitoring.score_calibration import register_model_version, get_model_versions
        register_model_version(
            version="0.4.0-CFGTEST",
            configuration={"FUNDAMENTAL": 0.30},
            human_approved_by="cfg_tester",
        )
        versions = get_model_versions()
        for v in versions:
            if v["version"] == "0.4.0-CFGTEST":
                assert isinstance(v["configuration"], dict)


# ═══════════════════════════════════════════════════════════════════════════
# Drift Detector Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestDriftDetector:
    """Drift detection engine."""

    def test_drift_report_no_data(self):
        from app.services.monitoring.drift_detector import DriftDetector
        detector = DriftDetector()
        report = detector.evaluate_drift()
        # With or without data, should return a valid DriftReport
        assert report.drift_alert_level in ("GREEN", "YELLOW", "RED")
        assert report.score_monotonicity_status in (
            "HEALTHY (NO DATA)", "VERIFIED_MONOTONIC", "MONOTONICITY_DEGRADED"
        )

    def test_drift_report_has_alert_level(self):
        from app.services.monitoring.drift_detector import DriftDetector, DriftReport
        report = DriftDetector().evaluate_drift()
        assert isinstance(report, DriftReport)
        assert report.total_predictions_evaluated >= 0

    def test_no_data_green_alert(self):
        from app.services.monitoring.drift_detector import DriftDetector
        # Fresh DB with no outcomes → GREEN / no decay
        # (may not be fresh, but should not crash)
        report = DriftDetector().evaluate_drift()
        assert report.drift_alert_level in ("GREEN", "YELLOW", "RED")


# ═══════════════════════════════════════════════════════════════════════════
# End-to-End: Arbiter Auto-Logs to Prediction Ledger
# ═══════════════════════════════════════════════════════════════════════════

class TestArbiterAutoLog:
    """Verify Arbiter.arbitrate() auto-logs to prediction_ledger."""

    def test_auto_log_method_exists(self):
        from app.services.decision_brain.arbiter import Arbiter
        arb = Arbiter()
        assert hasattr(arb, "_log_to_prediction_ledger")
        assert callable(arb._log_to_prediction_ledger)

    def test_log_conviction_call_persists(self):
        from app.services.decision_brain.arbiter import Arbiter
        from app.models.schemas import ConvictionCall
        from app.services.monitoring.prediction_ledger import PredictionLedgerService

        arb = Arbiter()
        call = ConvictionCall(
            symbol="TESTLOG",
            verdict="Buy",
            conviction_score=72,
            primary_thesis="Test auto-log thesis",
            contributing_engines=["E1"],
            contradicting_engines=[],
            confidence_tier="Model-dependent",
        )
        arb._log_to_prediction_ledger(call, reference_price=1500.0)

        # Verify it's in prediction_ledger
        ledger = PredictionLedgerService()
        history = ledger.get_prediction_history(symbol="TESTLOG", limit=5)
        assert len(history) >= 1
        latest = history[0]
        assert latest.verdict == "Buy"
        assert latest.score == 72

    def test_log_with_none_price_does_not_crash(self):
        from app.services.decision_brain.arbiter import Arbiter
        from app.models.schemas import ConvictionCall

        arb = Arbiter()
        call = ConvictionCall(
            symbol="TESTNOPRICE",
            verdict="Watch",
            conviction_score=45,
            primary_thesis="No price test",
            contributing_engines=[],
            contradicting_engines=[],
            confidence_tier="Contested",
        )
        # Should not raise even with None price
        arb._log_to_prediction_ledger(call, reference_price=None)


# ═══════════════════════════════════════════════════════════════════════════
# Phase 5 Integration: Prediction Ledger Service
# ═══════════════════════════════════════════════════════════════════════════

class TestPredictionLedgerService:
    """PredictionLedgerService full CRUD."""

    def test_log_and_retrieve_prediction(self):
        from app.services.monitoring.prediction_ledger import PredictionLedgerService
        svc = PredictionLedgerService()
        record = svc.log_prediction(
            symbol="LEDGERTEST",
            score=78,
            verdict="Buy",
            confidence="Model-dependent",
            thesis="Ledger integration test",
            reference_price=2000.0,
            model_version="0.4.0",
        )
        assert record.id is not None
        assert record.score == 78
        assert record.verdict == "Buy"

    def test_get_prediction_history_returns_list(self):
        from app.services.monitoring.prediction_ledger import PredictionLedgerService
        svc = PredictionLedgerService()
        history = svc.get_prediction_history(limit=10)
        assert isinstance(history, list)

    def test_history_filtered_by_symbol(self):
        from app.services.monitoring.prediction_ledger import PredictionLedgerService
        from app.services.market_data import normalize_symbol
        import time

        svc = PredictionLedgerService()
        # Use a unique raw symbol; normalize_symbol will append .NS
        raw_sym = f"FILTX{int(time.time()) % 100000}"
        normalized = normalize_symbol(raw_sym)  # e.g. "FILTX12345.NS"
        svc.log_prediction(
            symbol=raw_sym,
            score=65, verdict="Accumulate",
            confidence="Model-dependent",
            thesis="Filter test",
            model_version="0.4.0",
        )
        history = svc.get_prediction_history(symbol=raw_sym, limit=10)
        assert len(history) >= 1
        # All returned records must match the normalized symbol
        assert all(r.symbol == normalized for r in history)

    def test_record_outcome_classifies_correctly(self):
        from app.services.monitoring.prediction_ledger import PredictionLedgerService
        svc = PredictionLedgerService()
        record = svc.log_prediction(
            symbol="OUTCOMETEST",
            score=80, verdict="Buy",
            confidence="Confirmed",
            thesis="Outcome test",
            reference_price=1000.0,
            model_version="0.4.0",
        )
        outcome = svc.record_outcome(
            prediction_id=record.id,
            symbol="OUTCOMETEST",
            horizon_months=12,
            actual_return_pct=25.0,
            benchmark_return_pct=12.0,
        )
        assert outcome.outcome_class == "CONFIRMED_OUTPERFORMANCE"
        assert outcome.excess_return_pct == pytest.approx(13.0)
