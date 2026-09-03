"""Initial authoritative baseline migration for Equity Lab platform.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-03 19:42:00
"""

from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT UNIQUE NOT NULL,
        legal_name TEXT NOT NULL,
        sector TEXT,
        market_cap_tier TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TEXT NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS prediction_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        score INTEGER NOT NULL,
        verdict TEXT NOT NULL,
        confidence TEXT,
        reference_price REAL,
        thesis TEXT,
        model_version TEXT NOT NULL DEFAULT '1.0',
        created_at TEXT NOT NULL,
        conviction_call_id INTEGER,
        pre_fix_unverified BOOLEAN DEFAULT 0
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS outcome_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        horizon_months INTEGER NOT NULL,
        actual_return_pct REAL NOT NULL,
        benchmark_return_pct REAL NOT NULL,
        excess_return_pct REAL NOT NULL,
        outcome_class TEXT NOT NULL,
        recorded_at TEXT NOT NULL,
        pre_fix_unverified BOOLEAN DEFAULT 0
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS model_versions (
        version TEXT PRIMARY KEY,
        trained_at TEXT NOT NULL,
        train_samples INTEGER NOT NULL,
        test_samples INTEGER NOT NULL,
        brier_score REAL NOT NULL,
        log_loss REAL NOT NULL,
        roc_auc REAL NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 0,
        metadata_json TEXT
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS audit_trail_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT UNIQUE NOT NULL,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        payload_hash TEXT NOT NULL,
        previous_hash TEXT NOT NULL,
        current_hash TEXT NOT NULL,
        metadata_json TEXT
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS thesis_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        entry_date TEXT NOT NULL,
        entry_price REAL NOT NULL,
        target_price REAL NOT NULL,
        stop_price REAL NOT NULL,
        status TEXT NOT NULL,
        invalidation_reason TEXT,
        metadata_json TEXT
    );
    """)


def downgrade():
    pass
