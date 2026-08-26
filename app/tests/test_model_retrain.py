import pytest
import sqlite3
from app.services.ml.baseline_model import evaluate_and_retrain_model, train_baseline_model
from app.services.monitoring.score_calibration import get_model_versions
from app.core.config import settings


@pytest.fixture(scope="module", autouse=True)
def seed_test_outcomes():
    conn = sqlite3.connect(settings.DATA_STORE_PATH, timeout=30.0)
    now_str = "2026-01-01T00:00:00Z"
    try:
        count = conn.execute("SELECT count(*) FROM prediction_ledger WHERE symbol LIKE 'MOCKSTOCK%'").fetchone()[0]
    except Exception:
        count = 0
    if count < 25:
        for i in range(25):
            score = 50.0 + i * 1.5
            sym = f"MOCKSTOCK{i}.NS"
            cur = conn.execute(
                """INSERT INTO prediction_ledger 
                (symbol, score, verdict, confidence, reference_price, timestamp, created_at, pre_fix_unverified) 
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
                (sym, score, "Buy", "Confirmed", 100.0, now_str, now_str)
            )
            pred_id = cur.lastrowid
            exc_ret = 5.0 if i % 2 == 0 else -3.0
            out_cls = "OUTPERFORM" if exc_ret > 0 else "UNDERPERFORM"
            conn.execute(
                """INSERT INTO outcome_ledger 
                (prediction_id, symbol, horizon_months, actual_return_pct, benchmark_return_pct, excess_return_pct, outcome_class, recorded_at, pre_fix_unverified) 
                VALUES (?, ?, 12, ?, 0.0, ?, ?, ?, 0)""",
                (pred_id, sym, exc_ret, exc_ret, out_cls, now_str)
            )
        conn.commit()
    conn.close()
    train_baseline_model(force_retrain=True)



def test_evaluate_and_retrain_model_returns_valid_structure():
    """Verify evaluate_and_retrain_model returns expected evaluation fields."""
    result = evaluate_and_retrain_model()
    assert "status" in result
    assert "sample_count" in result
    assert "promoted" in result
    assert isinstance(result["promoted"], bool)


def test_registered_model_versions_contains_active_version():
    """Verify registered model versions table contains baseline or retrained model version."""
    versions = get_model_versions()
    assert len(versions) > 0
    version_names = [v["version"] for v in versions]
    assert any("ML-" in v for v in version_names)

