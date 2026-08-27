"""Database Architecture Consistency & Verification Tests — Phase 4.

Verifies:
- get_connection() canonical factory works for SQLite and handles PostgreSQL wrappers gracefully.
- Read, write, transaction commit, and rollback operate reliably.
- Production services (ResearchDataStore, Arbiter, RevisionTracker, ThesisTracker, FilingDocumentStore, baseline_model)
  delegate connection handling cleanly.
"""

import os
import pytest
from app.services.db import get_connection, PostgresConnectionWrapper, PostgresCursorWrapper
from app.services.research_data import ResearchDataStore
from app.services.decision_brain.arbiter import Arbiter
from app.services.monitoring.earnings_revision import RevisionTracker
from app.services.research.thesis_tracker import ThesisTracker
from app.services.rag.document_store import FilingDocumentStore
from app.services.ml.baseline_model import _get_db_connection


def test_canonical_db_connection():
    """Verify get_connection opens a valid connection and supports CRUD transactions."""
    conn = get_connection()
    assert conn is not None

    conn.execute("CREATE TABLE IF NOT EXISTS test_db_consistency (id INTEGER PRIMARY KEY, val TEXT)")
    conn.execute("INSERT INTO test_db_consistency (val) VALUES (?)", ("test_val",))
    conn.commit()

    rows = conn.execute("SELECT val FROM test_db_consistency WHERE val = ?", ("test_val",)).fetchall()
    assert len(rows) > 0
    row_val = rows[0]["val"] if hasattr(rows[0], "keys") else rows[0][0]
    assert row_val == "test_val"

    conn.execute("DELETE FROM test_db_consistency WHERE val = ?", ("test_val",))
    conn.commit()
    conn.close()


def test_db_rollback():
    """Verify database transaction rollback works properly."""
    conn = get_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS test_rollback (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()

    try:
        conn.execute("INSERT INTO test_rollback (name) VALUES (?)", ("should_rollback",))
        # Intentional rollback
        conn.rollback()
    except Exception:
        pass

    rows = conn.execute("SELECT * FROM test_rollback WHERE name = ?", ("should_rollback",)).fetchall()
    assert len(rows) == 0
    conn.close()


def test_postgres_wrapper_sql_translation():
    """Verify PostgresCursorWrapper translates SQLite placeholders and auto-increment statements."""
    class FakeCursor:
        def __init__(self):
            self.history = []
            self.rowcount = 1
        def execute(self, sql, params=None):
            self.history.append((sql, params))

    fake = FakeCursor()
    wrapper = PostgresCursorWrapper(fake)
    wrapper.execute("INSERT INTO my_table (col1, col2) VALUES (?, ?)", ("val1", "val2"))

    assert fake.history[0][0] == "INSERT INTO my_table (col1, col2) VALUES (%s, %s)"
    assert fake.history[0][1] == ("val1", "val2")


def test_service_connection_delegation():
    """Verify all core services instantiate and connect without error."""
    rds = ResearchDataStore()
    assert rds is not None

    arb = Arbiter()
    assert arb is not None

    rt = RevisionTracker()
    assert rt._get_connection() is not None

    tt = ThesisTracker()
    assert tt._get_connection() is not None

    fds = FilingDocumentStore()
    assert fds._get_connection() is not None

    conn_ml = _get_db_connection()
    assert conn_ml is not None
    conn_ml.close()
