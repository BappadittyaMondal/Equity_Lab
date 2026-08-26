"""Unit and integration tests for Phase 1 Longitudinal Intelligence Engine.
"""

import pytest
from app.models.schemas import MetricTrend, LifecycleState, ThesisMonitor, ContradictionReport
from app.services.longitudinal.trend_analyzer import classify_metric_trend, TrendAnalyzer
from app.services.longitudinal.lifecycle_engine import LifecycleEngine
from app.services.longitudinal.thesis_monitor import ThesisMonitorEngine
from app.services.longitudinal.alert_engine import AlertEngine
from app.services.decision_brain.arbiter import Arbiter
from app.core.config import settings


@pytest.fixture
def temp_db_path(tmp_path):
    db_file = tmp_path / "test_longitudinal.sqlite"
    original = settings.DATA_STORE_PATH
    settings.DATA_STORE_PATH = str(db_file)
    from app.services.db import _ensure_tables
    _ensure_tables()
    yield str(db_file)
    settings.DATA_STORE_PATH = original
    import gc
    gc.collect()


def test_classify_metric_trend():
    trend_acc = classify_metric_trend("revenue", current=120.0, prev_quarter=100.0, prev_year=90.0)
    assert trend_acc.classification == "accelerating"

    trend_imp = classify_metric_trend("pat", current=106.0, prev_quarter=100.0, prev_year=100.0)
    assert trend_imp.classification == "improving"

    trend_brk = classify_metric_trend("cfo", current=70.0, prev_quarter=100.0, prev_year=100.0)
    assert trend_brk.classification == "broken"


def test_lifecycle_engine(temp_db_path):
    engine = LifecycleEngine()
    engine_outputs = [
        {"engine_id": "E1", "verdict": "Buy", "raw": type("Obj", (), {"passed_gates": True})()},
        {"engine_id": "D15", "verdict": "Buy", "raw": type("Obj", (), {"passed_gates": True})()},
    ]
    lifecycle = engine.evaluate_lifecycle("RELIANCE", engine_outputs, conviction_score=85)
    assert lifecycle.symbol == "RELIANCE.NS"
    assert lifecycle.current_stage == "EARNINGS_ACCELERATION"


def test_thesis_monitor(temp_db_path):
    monitor = ThesisMonitorEngine()
    thesis = monitor.evaluate_thesis_state(
        symbol="TCS",
        conviction_score=85,
        verdict="Buy",
        contradictions=[],
        primary_thesis="Strong IT demand trajectory",
    )
    assert thesis.symbol == "TCS.NS"
    assert thesis.thesis_state == "STRENGTHENING"

    thesis_broken = monitor.evaluate_thesis_state(
        symbol="TCS",
        conviction_score=20,
        verdict="Avoid",
        contradictions=["C13"],
        primary_thesis="Governance veto trigger",
    )
    assert thesis_broken.thesis_state == "BROKEN"


def test_alert_engine(temp_db_path):
    alert_sys = AlertEngine()
    alert = alert_sys.emit_alert("INFY", "THESIS_WEAKENING", "WARNING", "Contradiction between fundamental and technical engines.")
    assert alert.symbol == "INFY"
    assert alert.event_type == "THESIS_WEAKENING"

    recent = alert_sys.get_recent_alerts(limit=10)
    assert len(recent) == 1
    assert recent[0].symbol == "INFY"


def test_contradiction_report(temp_db_path):
    arbiter = Arbiter()
    outputs = [
        {"engine_id": "E1", "verdict": "Buy"},
        {"engine_id": "C13", "verdict": "Avoid"},
    ]
    report = arbiter.generate_contradiction_report("WIPRO", outputs)
    assert report.symbol == "WIPRO.NS"
    assert "E1" in report.primary_positives
    assert "C13" in report.primary_negatives
    assert report.key_contradiction is not None
