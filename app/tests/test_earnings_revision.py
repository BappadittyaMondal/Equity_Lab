"""Unit tests for RevisionTracker service and earnings estimates ingestion.

Tests:
1. Single estimate insertion (no revision).
2. Upward revision calculation.
3. Downward revision calculation.
4. Missing data handling.
5. CSV ingestion script round-trip.
"""

import os
import tempfile
import pytest
from pathlib import Path

from app.services.monitoring.earnings_revision import RevisionTracker
from scripts.ingest_earnings_estimates import ingest_csv


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    # Initialize DB schema on temp DB
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS earnings_estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            fiscal_period TEXT NOT NULL,
            estimate_type TEXT NOT NULL,
            estimate_value REAL NOT NULL,
            as_of_date TEXT NOT NULL,
            source TEXT NOT NULL,
            revision_of INTEGER REFERENCES earnings_estimates(id)
        )
        """
    )
    conn.commit()
    conn.close()
    
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


def test_single_estimate(temp_db):
    tracker = RevisionTracker(db_path=temp_db)
    est_id = tracker.add_estimate(
        symbol="TCS",
        fiscal_period="FY25",
        estimate_value=120.0,
        as_of_date="2025-01-01",
        source="TEST"
    )
    assert est_id > 0

    rev = tracker.compute_revision("TCS", "FY25")
    assert rev["has_revision"] is False
    assert rev["revision_direction"] == "NO_REVISION"
    assert rev["estimate_count"] == 1
    assert rev["latest_estimate"] == 120.0


def test_upward_revision(temp_db):
    tracker = RevisionTracker(db_path=temp_db)
    tracker.add_estimate("RELIANCE", "FY25", 100.0, as_of_date="2025-01-01")
    tracker.add_estimate("RELIANCE", "FY25", 120.0, as_of_date="2025-02-01")

    rev = tracker.compute_revision("RELIANCE", "FY25")
    assert rev["has_revision"] is True
    assert rev["revision_direction"] == "UP"
    assert rev["revision_magnitude_pct"] == 20.0
    assert rev["estimate_count"] == 2
    assert rev["initial_estimate"] == 100.0
    assert rev["latest_estimate"] == 120.0


def test_downward_revision(temp_db):
    tracker = RevisionTracker(db_path=temp_db)
    tracker.add_estimate("INFY", "FY25", 80.0, as_of_date="2025-01-01")
    tracker.add_estimate("INFY", "FY25", 60.0, as_of_date="2025-02-01")

    rev = tracker.compute_revision("INFY", "FY25")
    assert rev["has_revision"] is True
    assert rev["revision_direction"] == "DOWN"
    assert rev["revision_magnitude_pct"] == -25.0
    assert rev["estimate_count"] == 2


def test_no_data(temp_db):
    tracker = RevisionTracker(db_path=temp_db)
    rev = tracker.compute_revision("UNKNOWN_TICKER", "FY25")
    assert rev["has_revision"] is False
    assert rev["revision_direction"] == "NO_DATA"
    assert rev["estimate_count"] == 0


def test_csv_ingestion(temp_db, monkeypatch):
    # Patch settings.DATA_STORE_PATH to point to temp_db
    from app.core.config import settings
    monkeypatch.setattr(settings, "DATA_STORE_PATH", temp_db)

    csv_content = """symbol,fiscal_period,estimate_type,estimate_value,as_of_date,source,revision_of
TATAMOTORS,FY25,consensus_eps,45.0,2025-01-01,ANALYST_A,
TATAMOTORS,FY25,consensus_eps,52.5,2025-02-01,ANALYST_B,
"""
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False, encoding="utf-8") as tmp_csv:
        tmp_csv.write(csv_content)
        tmp_csv_path = tmp_csv.name

    try:
        count = ingest_csv(tmp_csv_path)
        assert count == 2

        tracker = RevisionTracker(db_path=temp_db)
        rev = tracker.compute_revision("TATAMOTORS", "FY25")
        assert rev["has_revision"] is True
        assert rev["revision_direction"] == "UP"
        assert rev["latest_estimate"] == 52.5
    finally:
        if os.path.exists(tmp_csv_path):
            os.remove(tmp_csv_path)
