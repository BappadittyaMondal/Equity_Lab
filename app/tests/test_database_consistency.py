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


def test_get_table_columns_sqlite_and_postgres_dict():
    from app.services.db import get_table_columns
    conn = get_connection()
    cols = get_table_columns(conn, "conviction_calls")
    assert "symbol" in cols
    assert "conviction_score" in cols
    assert "data_backed" in cols
    conn.close()

    class MockPostgresConn:
        def execute(self, sql):
            class MockCursor:
                def fetchall(self):
                    return [
                        {"cid": 1, "name": "col_a", "type": "text"},
                        {"cid": 2, "name": "col_b", "type": "integer"}
                    ]
            return MockCursor()

    pg_cols = get_table_columns(MockPostgresConn(), "test_table")
    assert pg_cols == ["col_a", "col_b"]


def test_db_health_render_and_production_checks(monkeypatch):
    from app.core.db_health import check_db_health

    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.setenv("IERL_ENVIRONMENT", "development")
    monkeypatch.setenv("DATABASE_URL", "")
    h1 = check_db_health()
    assert h1["is_postgres"] is False
    assert h1["is_prod"] is False

    monkeypatch.setenv("RENDER", "true")
    h2 = check_db_health()
    assert h2["is_render"] is True
    assert h2["is_prod"] is True
    assert "PRODUCTION DATABASE WARNING" in (h2["warning"] or "")

    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")
    h3 = check_db_health()
    assert h3["is_postgres"] is True
    assert h3["status"] == "HEALTHY"


def test_alembic_consolidated_migration_upgrade(monkeypatch):
    """Verify Alembic migration 002 successfully parses and executes against canonical DB (DEF-002)."""
    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location("migration_002", os.path.join("alembic", "versions", "002_consolidate_all_tables.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    executed_statements = []
    class MockOp:
        @staticmethod
        def execute(sql):
            executed_statements.append(sql)
            # Verify SQL statement executes against canonical SQLite connection
            conn = get_connection()
            conn.execute(sql)
            conn.close()

    monkeypatch.setattr(mod, "op", MockOp)
    mod.upgrade()

    assert len(executed_statements) >= 15
    assert any("company_fundamentals" in s for s in executed_statements)
    assert any("quarterly_financials" in s for s in executed_statements)


def test_alembic_remaining_tables_migration_003(monkeypatch):
    """Verify Alembic migration 003 successfully parses and creates the 8 remaining platform tables."""
    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location("migration_003", os.path.join("alembic", "versions", "003_consolidate_remaining_tables.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    executed_statements = []
    class MockOp:
        @staticmethod
        def execute(sql):
            executed_statements.append(sql)
            conn = get_connection()
            conn.execute(sql)
            conn.close()

    monkeypatch.setattr(mod, "op", MockOp)
    mod.upgrade()

    assert len(executed_statements) >= 8
    assert any("decision_audit_trail" in s for s in executed_statements)
    assert any("filing_documents" in s for s in executed_statements)
    assert any("investment_theses" in s for s in executed_statements)
    assert any("prediction_ledger_conformal" in s for s in executed_statements)


def test_alembic_reconcile_foreign_keys_migration_004(monkeypatch):
    """Verify Alembic migration 004 successfully creates foreign key index on prediction_ledger."""
    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location("migration_004", os.path.join("alembic", "versions", "004_reconcile_foreign_keys.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    executed = []
    class MockOp:
        @staticmethod
        def execute(sql):
            executed.append(sql)
            conn = get_connection()
            conn.execute(sql)
            conn.close()

    monkeypatch.setattr(mod, "op", MockOp)
    mod.upgrade()

    assert len(executed) >= 2
    assert any("idx_prediction_ledger_conviction_id" in s for s in executed)
    assert any("idx_decision_audit_symbol_timestamp" in s for s in executed)

