"""Consolidate all remaining platform tables into authoritative Alembic migration chain.

Revision ID: 002_consolidate_all_tables
Revises: 001_initial_schema
Create Date: 2026-09-05 12:00:00
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

revision = '002_consolidate_all_tables'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE IF NOT EXISTS conviction_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        verdict TEXT NOT NULL,
        conviction_score INTEGER NOT NULL,
        primary_thesis TEXT,
        contributing_engines TEXT,
        contradicting_engines TEXT,
        confidence_tier TEXT,
        created_at TEXT NOT NULL,
        data_backed BOOLEAN DEFAULT 0
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS thesis_drift_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        old_score INTEGER,
        new_score INTEGER,
        delta INTEGER,
        old_verdict TEXT,
        new_verdict TEXT,
        triggering_engines TEXT,
        created_at TEXT NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS llm_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        provider TEXT NOT NULL,
        token_count INTEGER NOT NULL,
        estimated_cost REAL NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS lifecycle_transitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        previous_stage TEXT,
        current_stage TEXT NOT NULL,
        transition_reason TEXT NOT NULL,
        confidence REAL NOT NULL,
        supporting_evidence TEXT,
        created_at TEXT NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS system_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        event_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        details TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS earnings_estimates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        fiscal_period TEXT NOT NULL,
        estimate_type TEXT NOT NULL,
        estimate_value REAL NOT NULL,
        as_of_date TEXT NOT NULL,
        published_at TEXT,
        available_at TEXT,
        effective_at TEXT,
        source TEXT NOT NULL,
        revision_of INTEGER REFERENCES earnings_estimates(id)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS quarterly_financials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        period_ended TEXT NOT NULL,
        revenue REAL,
        operating_profit REAL,
        net_profit REAL,
        eps REAL,
        operating_margin_pct REAL,
        net_margin_pct REAL,
        roce_pct REAL,
        roe_pct REAL,
        as_of_date TEXT NOT NULL,
        published_at TEXT,
        available_at TEXT,
        effective_at TEXT,
        source TEXT NOT NULL,
        UNIQUE(symbol, period_ended)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS promoter_shareholding (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        period_ended TEXT NOT NULL,
        promoter_holding_pct REAL NOT NULL,
        pledged_pct REAL DEFAULT 0.0,
        institutional_holding_pct REAL DEFAULT 0.0,
        as_of_date TEXT NOT NULL,
        published_at TEXT,
        available_at TEXT,
        effective_at TEXT,
        source TEXT NOT NULL,
        UNIQUE(symbol, period_ended)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS market_corporate_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        action_type TEXT NOT NULL,
        ex_date TEXT NOT NULL,
        ratio_or_amount REAL NOT NULL,
        details TEXT,
        as_of_date TEXT NOT NULL,
        published_at TEXT,
        available_at TEXT,
        effective_at TEXT,
        UNIQUE(symbol, action_type, ex_date)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS historical_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        date TEXT NOT NULL,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        volume INTEGER NOT NULL,
        adjusted_close REAL NOT NULL,
        as_of_date TEXT NOT NULL,
        published_at TEXT,
        available_at TEXT,
        effective_at TEXT,
        UNIQUE(symbol, date)
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS company_fundamentals (
        symbol TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        market_cap REAL DEFAULT 0.0,
        current_price REAL DEFAULT 0.0,
        volume INTEGER DEFAULT 0,
        high_52w REAL DEFAULT 0.0,
        low_52w REAL DEFAULT 0.0,
        roe_3yr REAL DEFAULT 0.0,
        roe_latest REAL DEFAULT 0.0,
        roce_3yr REAL DEFAULT 0.0,
        roce_latest REAL DEFAULT 0.0,
        opm_5yr REAL DEFAULT 0.0,
        opm_latest REAL DEFAULT 0.0,
        operating_profit REAL DEFAULT 0.0,
        op_growth REAL DEFAULT 0.0,
        pat_growth_3yr REAL DEFAULT 0.0,
        pat_growth_latest REAL DEFAULT 0.0,
        sales_growth_3yr REAL DEFAULT 0.0,
        sales_growth_latest REAL DEFAULT 0.0,
        eps_growth_3yr REAL DEFAULT 0.0,
        eps_latest REAL DEFAULT 0.0,
        cfo_3yr REAL DEFAULT 0.0,
        net_block REAL DEFAULT 0.0,
        net_block_3yr_back REAL DEFAULT 0.0,
        net_block_preceding_year REAL DEFAULT 0.0,
        cwip REAL DEFAULT 0.0,
        cwip_preceding_year REAL DEFAULT 0.0,
        cfo_last_year REAL DEFAULT 0.0,
        net_profit_last_year REAL DEFAULT 0.0,
        vol_1w_avg REAL DEFAULT 0.0,
        vol_1m_avg REAL DEFAULT 0.0,
        vol_1y_avg REAL DEFAULT 0.0,
        piotroski_score REAL DEFAULT 0.0,
        promoter_holding REAL DEFAULT 0.0,
        pledged_pct REAL DEFAULT 0.0,
        debt_to_equity REAL DEFAULT 0.0,
        interest_coverage REAL DEFAULT 0.0,
        peg_ratio REAL DEFAULT 0.0,
        order_book REAL DEFAULT 0.0,
        fii_holding REAL DEFAULT 0.0,
        dii_holding REAL DEFAULT 0.0,
        total_assets REAL DEFAULT 0.0,
        dma_50 REAL DEFAULT 0.0,
        dma_200 REAL DEFAULT 0.0,
        shares_count REAL DEFAULT 0.0,
        shares_count_10yr_back REAL DEFAULT 0.0,
        updated_at TEXT
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS financial_observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        period_end TEXT NOT NULL,
        metric TEXT NOT NULL,
        value REAL NOT NULL,
        observation_date TEXT NOT NULL,
        valid_from TEXT NOT NULL,
        valid_to TEXT,
        source_doc_id TEXT,
        created_at TEXT NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS business_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        event_date TEXT NOT NULL,
        event_type TEXT NOT NULL,
        description TEXT NOT NULL,
        sentiment REAL DEFAULT 0.0,
        observation_date TEXT NOT NULL,
        valid_from TEXT NOT NULL,
        source_doc_id TEXT,
        created_at TEXT NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS corporate_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        action_type TEXT NOT NULL,
        announcement_date TEXT NOT NULL,
        record_date TEXT,
        effective_date TEXT NOT NULL,
        ratio_or_amount REAL NOT NULL,
        observation_date TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS ownership_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        quarter_end TEXT NOT NULL,
        promoter_pct REAL NOT NULL,
        fii_pct REAL NOT NULL,
        dii_pct REAL NOT NULL,
        public_pct REAL NOT NULL,
        promoter_pledged_pct REAL DEFAULT 0.0,
        observation_date TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS user_feedback_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        feedback_type TEXT NOT NULL,
        rating INTEGER,
        comments TEXT,
        metadata_json TEXT,
        created_at TEXT NOT NULL
    );
    """)


def downgrade():
    pass
