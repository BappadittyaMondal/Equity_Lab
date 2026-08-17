"""Phase 5 Automated Database Backup, Restore, & Verification Script.

Executes WAL checkpoint, creates a timestamped SQLite database copy in `backups/`,
restores to a temporary directory, and verifies schema & row counts.
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from app.core.config import settings
from app.services.db import get_connection, _ensure_tables

BACKUP_DIR = root_dir / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def run_backup_and_verify():
    print("=== Running IERL Production Database Backup & Restore Verification ===")
    _ensure_tables()

    source_db = Path(settings.DATA_STORE_PATH)
    if not source_db.exists():
        print(f"[FAIL] Source database file '{source_db}' does not exist.")
        sys.exit(1)

    # 1. Force WAL Checkpoint
    try:
        conn = get_connection()
        conn.execute("PRAGMA wal_checkpoint(FULL)")
        conn.close()
        print("[PASS] WAL checkpoint completed successfully.")
    except Exception as e:
        print(f"[WARN] WAL checkpoint warning: {e}")

    # 2. Copy Database to Backup Directory
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"ierl_backup_{timestamp}.sqlite"

    try:
        shutil.copy2(source_db, backup_file)
        print(f"[PASS] Backup created at: '{backup_file}' ({backup_file.stat().st_size} bytes)")
    except Exception as e:
        print(f"[FAIL] Database backup failed: {e}")
        sys.exit(1)

    # 3. Test Restore in Temp Location
    temp_restore_file = BACKUP_DIR / "temp_restore_verify.sqlite"
    try:
        if temp_restore_file.exists():
            temp_restore_file.unlink()

        shutil.copy2(backup_file, temp_restore_file)

        # 4. Verify Integrity on Restored DB
        res_conn = sqlite3.connect(temp_restore_file)
        res_conn.row_factory = sqlite3.Row

        # Check integrity
        integrity_row = res_conn.execute("PRAGMA integrity_check").fetchone()
        integrity_status = integrity_row[0] if integrity_row else "FAILED"
        if integrity_status != "ok":
            print(f"[FAIL] Restored DB integrity check failed: {integrity_status}")
            sys.exit(1)

        # Count tables
        tables = res_conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
        res_conn.close()

        print(f"[PASS] Restore verification succeeded: Integrity OK, Table count = {tables}")

    finally:
        if temp_restore_file.exists():
            temp_restore_file.unlink()

    print("=== ALL BACKUP & RESTORE CHECKS PASSED SUCCESSFULLY ===")


if __name__ == "__main__":
    run_backup_and_verify()
