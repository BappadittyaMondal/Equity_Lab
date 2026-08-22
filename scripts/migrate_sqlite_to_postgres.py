"""SQLite to PostgreSQL Migration Script for Equity Lab OS.

Copies local SQLite tables and observations to PostgreSQL (Neon/Supabase) when `DATABASE_URL` is set.
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.core.config import settings


def migrate():
    db_url = os.getenv("DATABASE_URL")
    if not db_url or not (db_url.startswith("postgres://") or db_url.startswith("postgresql://")):
        print("[ERROR] DATABASE_URL environment variable is missing or invalid. Set DATABASE_URL to a valid PostgreSQL connection string.")
        sys.exit(1)

    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        print("[ERROR] psycopg2 library is not installed. Install with `pip install psycopg2-binary`.")
        sys.exit(1)

    sqlite_path = settings.DATA_STORE_PATH
    if not os.path.exists(sqlite_path):
        print(f"[ERROR] SQLite database not found at {sqlite_path}.")
        sys.exit(1)

    print(f"[*] Opening SQLite database: {sqlite_path}")
    sq_conn = sqlite3.connect(sqlite_path)
    sq_conn.row_factory = sqlite3.Row
    sq_cursor = sq_conn.cursor()

    print(f"[*] Connecting to PostgreSQL database...")
    pg_conn = psycopg2.connect(db_url)
    pg_cursor = pg_conn.cursor()

    tables = [
        "companies",
        "financial_observations",
        "business_events",
        "corporate_actions",
        "ownership_snapshots",
        "document_metadata",
        "market_daily_snapshots",
        "conviction_calls",
        "thesis_drift_events",
        "prediction_ledger",
        "outcome_ledger",
        "model_versions",
        "system_alerts"
    ]

    for table in tables:
        try:
            sq_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not sq_cursor.fetchone():
                print(f"[SKIP] Table '{table}' does not exist in SQLite.")
                continue

            rows = sq_cursor.execute(f"SELECT * FROM {table}").fetchall()
            if not rows:
                print(f"[SKIP] Table '{table}' is empty.")
                continue

            col_names = [description[0] for description in sq_cursor.description]
            placeholders = ", ".join(["%s"] * len(col_names))
            cols_str = ", ".join(col_names)

            insert_sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;"

            migrated_count = 0
            for r in rows:
                row_vals = [r[col] for col in col_names]
                pg_cursor.execute(insert_sql, row_vals)
                migrated_count += 1

            pg_conn.commit()
            print(f"[SUCCESS] Migrated {migrated_count} records into table '{table}'.")

        except Exception as e:
            pg_conn.rollback()
            print(f"[WARNING] Migration for table '{table}' failed: {e}")

    sq_conn.close()
    pg_conn.close()
    print("[COMPLETE] SQLite to PostgreSQL migration finished successfully.")


if __name__ == "__main__":
    migrate()
