"""Consolidate remaining unmanaged platform tables into authoritative Alembic chain.

Revision ID: 003_consolidate_remaining_tables
Revises: 002_consolidate_all_tables
Create Date: 2026-09-08 22:30:00
"""

try:
    from alembic import op
    import sqlalchemy as sa
except (ImportError, ModuleNotFoundError):
    class MockOp:
        @staticmethod
        def execute(sql):
            pass
    op = MockOp
    sa = None

revision = '003_consolidate_remaining_tables'
down_revision = '002_consolidate_all_tables'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Decision Audit Trail
    op.execute("""
    CREATE TABLE IF NOT EXISTS decision_audit_trail (
        id                       INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol                   TEXT NOT NULL,
        timestamp                TEXT NOT NULL,
        model_version            TEXT NOT NULL DEFAULT '0.4.0',
        final_score              INTEGER NOT NULL,
        final_verdict            TEXT NOT NULL,
        governance_veto_applied  INTEGER NOT NULL DEFAULT 0,
        macro_regime             TEXT DEFAULT 'CALM',
        india_vix                REAL,
        contradiction_severity   TEXT DEFAULT 'LOW',
        net_evidence_balance     TEXT,
        expected_return_1y_pct   REAL,
        confidence_composite_pct REAL,
        catalyst_count           INTEGER DEFAULT 0,
        why_this_verdict         TEXT,
        falsification_conditions TEXT,
        engine_outputs           TEXT,
        data_lineage             TEXT,
        created_at               TEXT NOT NULL,
        record_hash              TEXT,
        prev_record_hash         TEXT
    );
    """)

    # 2. Document Metadata
    op.execute("""
    CREATE TABLE IF NOT EXISTS document_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        document_type TEXT NOT NULL,
        title TEXT NOT NULL,
        financial_period TEXT,
        document_date TEXT NOT NULL,
        publication_date TEXT NOT NULL,
        source_name TEXT NOT NULL,
        source_url TEXT NOT NULL,
        confidence REAL NOT NULL,
        metadata_json TEXT,
        ingested_at TEXT NOT NULL
    );
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_document_lookup
        ON document_metadata(symbol, publication_date);
    """)

    # 3. Filing Documents (RAG)
    op.execute("""
    CREATE TABLE IF NOT EXISTS filing_documents (
        document_hash TEXT PRIMARY KEY,
        symbol TEXT NOT NULL,
        doc_type TEXT NOT NULL,
        effective_date TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        section TEXT,
        page_number INTEGER,
        metadata_json TEXT,
        created_at TEXT NOT NULL
    );
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_filing_symbol_date
        ON filing_documents(symbol, effective_date);
    """)

    # 4. Investment Theses
    op.execute("""
    CREATE TABLE IF NOT EXISTS investment_theses (
        thesis_id TEXT PRIMARY KEY,
        symbol TEXT NOT NULL,
        primary_thesis TEXT NOT NULL,
        status TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        created_at TEXT NOT NULL,
        last_evaluated_at TEXT NOT NULL,
        kill_conditions_json TEXT NOT NULL,
        invalidation_reason TEXT
    );
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_thesis_symbol
        ON investment_theses(symbol);
    """)

    # 5. Market Cache
    op.execute("""
    CREATE TABLE IF NOT EXISTS market_cache (
        symbol TEXT PRIMARY KEY,
        json_blob TEXT NOT NULL,
        fetched_at INTEGER NOT NULL
    );
    """)

    # 6. Market Daily Snapshots
    op.execute("""
    CREATE TABLE IF NOT EXISTS market_daily_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        trading_date TEXT NOT NULL,
        open_price REAL NOT NULL,
        high_price REAL NOT NULL,
        low_price REAL NOT NULL,
        close_price REAL NOT NULL,
        volume INTEGER NOT NULL,
        delivery_volume INTEGER,
        delivery_pct REAL,
        market_cap REAL,
        published_at TEXT NOT NULL,
        source_name TEXT NOT NULL,
        source_url TEXT NOT NULL,
        ingested_at TEXT NOT NULL
    );
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_market_daily_lookup
        ON market_daily_snapshots(symbol, trading_date, published_at);
    """)

    # 7. Prediction Ledger Conformal
    op.execute("""
    CREATE TABLE IF NOT EXISTS prediction_ledger_conformal (
        prediction_id TEXT PRIMARY KEY,
        symbol TEXT NOT NULL,
        logged_at TEXT NOT NULL,
        base_price REAL NOT NULL,
        predicted_target REAL NOT NULL,
        conformal_lower REAL NOT NULL,
        conformal_upper REAL NOT NULL,
        confidence_tier TEXT NOT NULL,
        invalidation_triggers TEXT NOT NULL,
        evaluations TEXT NOT NULL
    );
    """)

    # 8. Watchlist
    op.execute("""
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT UNIQUE NOT NULL,
        company_name TEXT,
        target_price REAL DEFAULT 0.0,
        notes TEXT,
        added_at TEXT NOT NULL
    );
    """)


def downgrade():
    pass
