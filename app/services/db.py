import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings


class PostgresCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = None

    def execute(self, sql: str, params: Optional[tuple] = None):
        pg_sql = sql.replace("?", "%s")
        pg_sql = pg_sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        pg_sql = pg_sql.replace("AUTOINCREMENT", "")
        
        if pg_sql.strip().upper().startswith("PRAGMA TABLE_INFO"):
            raw = pg_sql.strip()
            table_name = raw[raw.find("(")+1:raw.find(")")].strip("'\" ")
            pg_sql = "SELECT ordinal_position as cid, column_name as name, data_type as type, 0 as notnull, NULL as dflt_value, 0 as pk FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position"
            params = (table_name,)
            
        if params is not None:
            self._cursor.execute(pg_sql, params)
        else:
            self._cursor.execute(pg_sql)
            
        if pg_sql.strip().upper().startswith("INSERT") and "RETURNING" not in pg_sql.upper():
            try:
                self._cursor.execute("SELECT LASTVAL()")
                row = self._cursor.fetchone()
                if row:
                    self.lastrowid = list(row.values())[0] if isinstance(row, dict) else row[0]
            except Exception:
                pass
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchmany(self, size: int):
        return self._cursor.fetchmany(size)

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def __iter__(self):
        return iter(self._cursor)


class PostgresConnectionWrapper:
    def __init__(self, pg_conn):
        self._conn = pg_conn

    def execute(self, sql: str, params: Optional[tuple] = None):
        cursor = self._conn.cursor()
        wrapper = PostgresCursorWrapper(cursor)
        wrapper.execute(sql, params)
        return wrapper

    def executescript(self, sql: str):
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for stmt in statements:
            self.execute(stmt)
        self.commit()

    def cursor(self):
        return PostgresCursorWrapper(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()


_OPEN_CONNECTIONS = set()

def close_all_connections():
    global _OPEN_CONNECTIONS
    for conn in list(_OPEN_CONNECTIONS):
        try:
            conn.close()
        except Exception:
            pass
    _OPEN_CONNECTIONS.clear()

def get_connection():
    """Return a database connection to the shared data store.
    Supports PostgreSQL if `DATABASE_URL` is set, with seamless fallback to SQLite.
    On Vercel serverless environments, falls back to `/tmp/ierl_research.db` to prevent read-only filesystem locks.
    """
    db_url = os.getenv("DATABASE_URL")
    if db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")):
        try:
            import psycopg2
            import psycopg2.extras
            # Support optional pooling options from settings / env
            connect_timeout = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
            conn = psycopg2.connect(
                db_url,
                cursor_factory=psycopg2.extras.RealDictCursor,
                connect_timeout=connect_timeout
            )
            return PostgresConnectionWrapper(conn)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("Failed to connect to DATABASE_URL, falling back to SQLite: %s", exc)

    # SQLite connection with /tmp fallback for Vercel serverless execution
    db_path = settings.DATA_STORE_PATH
    if os.getenv("VERCEL") == "1" or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        tmp_db = "/tmp/ierl_research.db"
        if not os.path.exists(tmp_db) and os.path.exists(db_path):
            import shutil
            try:
                shutil.copy2(db_path, tmp_db)
            except Exception:
                pass
        if os.path.exists(tmp_db):
            db_path = tmp_db

    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.execute("PRAGMA journal_mode = WAL")
    except Exception:
        pass
    _OPEN_CONNECTIONS.add(conn)
    return conn



def _ensure_tables() -> None:
    """Create any additional tables needed for orchestration.
    Currently ensures the `thesis_drift_events` table exists.
    """
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS conviction_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            verdict TEXT NOT NULL,
            conviction_score INTEGER NOT NULL,
            primary_thesis TEXT,
            contributing_engines TEXT,   -- JSON array
            contradicting_engines TEXT,  -- JSON array
            confidence_tier TEXT,
            created_at TEXT NOT NULL,
            data_backed BOOLEAN DEFAULT 0
        )
        """
    )
    # Check if data_backed column exists in conviction_calls, migrate and backfill as false if missing
    try:
        existing_cols = [r[1] for r in conn.execute("PRAGMA table_info(conviction_calls)").fetchall()]
        if "data_backed" not in existing_cols:
            conn.execute("ALTER TABLE conviction_calls ADD COLUMN data_backed BOOLEAN DEFAULT 0")
            conn.execute("UPDATE conviction_calls SET data_backed = 0 WHERE data_backed IS NULL")
    except Exception:
        pass
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS thesis_drift_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            old_score INTEGER,
            new_score INTEGER,
            delta INTEGER,
            old_verdict TEXT,
            new_verdict TEXT,
            triggering_engines TEXT,  -- JSON array
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS llm_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            provider TEXT NOT NULL,
            token_count INTEGER NOT NULL,
            estimated_cost REAL NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_usage_ts ON llm_usage(timestamp)")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lifecycle_transitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            previous_stage TEXT,
            current_stage TEXT NOT NULL,
            transition_reason TEXT NOT NULL,
            confidence REAL NOT NULL,
            supporting_evidence TEXT, -- JSON array
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lifecycle_sym ON lifecycle_transitions(symbol)")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS thesis_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL UNIQUE,
            why_buy TEXT NOT NULL,
            growth_drivers TEXT, -- JSON array
            catalysts TEXT, -- JSON array
            risks TEXT, -- JSON array
            thesis_conditions TEXT, -- JSON array
            invalidation_conditions TEXT, -- JSON array
            thesis_state TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS system_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_sym ON system_alerts(symbol)")

    # NOTE (Leakage Fix Audit): Records created prior to point-in-time leakage remediation (2026-08-20)
    # are marked pre_fix_unverified = 1 to prevent invalid backtest calibration baselines.
    conn.execute(
        """
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
            conviction_call_id INTEGER REFERENCES conviction_calls(id),
            pre_fix_unverified BOOLEAN DEFAULT 0
        )
        """
    )
    # Check if conviction_call_id and pre_fix_unverified columns exist in prediction_ledger, migrate if missing
    try:
        existing_cols = [r[1] for r in conn.execute("PRAGMA table_info(prediction_ledger)").fetchall()]
        if "conviction_call_id" not in existing_cols:
            conn.execute("ALTER TABLE prediction_ledger ADD COLUMN conviction_call_id INTEGER REFERENCES conviction_calls(id)")
        if "pre_fix_unverified" not in existing_cols:
            conn.execute("ALTER TABLE prediction_ledger ADD COLUMN pre_fix_unverified BOOLEAN DEFAULT 0")
            # Flag all legacy records created prior to point-in-time leakage fix as pre_fix_unverified = 1
            conn.execute("UPDATE prediction_ledger SET pre_fix_unverified = 1 WHERE pre_fix_unverified IS NULL OR pre_fix_unverified = 0")
    except Exception:
        pass
    conn.execute("CREATE INDEX IF NOT EXISTS idx_pred_sym ON prediction_ledger(symbol)")

    conn.execute(
        """
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
            pre_fix_unverified BOOLEAN DEFAULT 0,
            FOREIGN KEY (prediction_id) REFERENCES prediction_ledger(id)
        )
        """
    )
    try:
        existing_outcome_cols = [r[1] for r in conn.execute("PRAGMA table_info(outcome_ledger)").fetchall()]
        if "pre_fix_unverified" not in existing_outcome_cols:
            conn.execute("ALTER TABLE outcome_ledger ADD COLUMN pre_fix_unverified BOOLEAN DEFAULT 0")
            conn.execute("UPDATE outcome_ledger SET pre_fix_unverified = 1 WHERE pre_fix_unverified IS NULL OR pre_fix_unverified = 0")
    except Exception:
        pass

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS model_versions (
            version TEXT PRIMARY KEY,
            released_at TEXT NOT NULL,
            configuration_json TEXT NOT NULL,
            backtest_summary TEXT,
            human_approved_by TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
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
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_estimates_sym_period ON earnings_estimates(symbol, fiscal_period)")

    conn.execute(
        """
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
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_qtr_fin_sym ON quarterly_financials(symbol, period_ended)")

    conn.execute(
        """
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
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_promoter_sym ON promoter_shareholding(symbol, period_ended)")

    conn.execute(
        """
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
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_corp_act_sym ON market_corporate_actions(symbol)")

    conn.execute(
        """
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
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hist_px_sym_date ON historical_prices(symbol, date)")

    # Auto-migration for published_at, available_at, effective_at columns across point-in-time tables
    try:
        pit_tables = ["earnings_estimates", "quarterly_financials", "promoter_shareholding", "market_corporate_actions", "historical_prices"]
        for tbl in pit_tables:
            existing_cols = [r[1] for r in conn.execute(f"PRAGMA table_info({tbl})").fetchall()]
            for col in ["published_at", "available_at", "effective_at"]:
                if col not in existing_cols:
                    conn.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} TEXT")
    except Exception:
        pass

    conn.execute(
        """
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
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_comp_fund_mcap ON company_fundamentals(market_cap)")

    # Migration for new company_fundamentals columns if existing table is present
    try:
        existing_cols = [r[1] for r in conn.execute("PRAGMA table_info(company_fundamentals)").fetchall()]
        new_cols = [
            ("net_block", "REAL DEFAULT 0.0"),
            ("net_block_3yr_back", "REAL DEFAULT 0.0"),
            ("net_block_preceding_year", "REAL DEFAULT 0.0"),
            ("cwip", "REAL DEFAULT 0.0"),
            ("cwip_preceding_year", "REAL DEFAULT 0.0"),
            ("cfo_last_year", "REAL DEFAULT 0.0"),
            ("net_profit_last_year", "REAL DEFAULT 0.0"),
            ("vol_1w_avg", "REAL DEFAULT 0.0"),
            ("vol_1m_avg", "REAL DEFAULT 0.0"),
            ("vol_1y_avg", "REAL DEFAULT 0.0"),
            ("piotroski_score", "REAL DEFAULT 0.0"),
            ("promoter_holding", "REAL DEFAULT 0.0"),
            ("pledged_pct", "REAL DEFAULT 0.0"),
            ("debt_to_equity", "REAL DEFAULT 0.0"),
            ("interest_coverage", "REAL DEFAULT 0.0"),
            ("peg_ratio", "REAL DEFAULT 0.0")
        ]
        for col_name, col_def in new_cols:
            if col_name not in existing_cols:
                conn.execute(f"ALTER TABLE company_fundamentals ADD COLUMN {col_name} {col_def}")
    except Exception:
        pass

    conn.commit()
    conn.close()
    if conn in _OPEN_CONNECTIONS:
        _OPEN_CONNECTIONS.remove(conn)

# Ensure tables are present on import
_ensure_tables()
