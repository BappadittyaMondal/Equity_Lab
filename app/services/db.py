import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection to the shared data store.
    The connection uses `Row` factory, enables foreign keys, and sets 30s lock timeout.
    """
    conn = sqlite3.connect(settings.DATA_STORE_PATH, detect_types=sqlite3.PARSE_DECLTYPES, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.execute("PRAGMA journal_mode = WAL")
    except Exception:
        pass
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
            UNIQUE(symbol, date)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hist_px_sym_date ON historical_prices(symbol, date)")

    conn.commit()
    conn.close()

# Ensure tables are present on import
_ensure_tables()
