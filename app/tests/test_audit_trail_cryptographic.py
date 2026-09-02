"""Test Suite for Cryptographic Immutability of Decision Audit Trail."""

import pytest
import sqlite3
from app.services.decision_brain.audit_trail import (
    verify_audit_chain_integrity,
    _ensure_table,
    query_audit_history,
)
from app.services.db import get_connection


def test_audit_trail_schema_has_hash_chain():
    _ensure_table()
    conn = get_connection()
    cols = [r[1] for r in conn.execute("PRAGMA table_info(decision_audit_trail)").fetchall()]
    conn.close()
    assert "record_hash" in cols
    assert "prev_record_hash" in cols


def test_audit_trail_chain_integrity_verification():
    res = verify_audit_chain_integrity(limit=50)
    assert "chain_valid" in res
    assert res["chain_valid"] is True


def test_audit_trail_immutability_trigger_blocks_update_and_delete():
    conn = get_connection()
    try:
        row = conn.execute("SELECT id FROM decision_audit_trail LIMIT 1").fetchone()
        if row:
            target_id = row[0]
            # UPDATE must fail closed via SQLite trigger
            with pytest.raises(sqlite3.DatabaseError, match="cryptographically immutable"):
                try:
                    conn.execute(f"UPDATE decision_audit_trail SET final_score = 100 WHERE id = {target_id}")
                finally:
                    conn.rollback()

            # DELETE must fail closed via SQLite trigger
            with pytest.raises(sqlite3.DatabaseError, match="cryptographically immutable"):
                try:
                    conn.execute(f"DELETE FROM decision_audit_trail WHERE id = {target_id}")
                finally:
                    conn.rollback()
    finally:
        conn.close()

