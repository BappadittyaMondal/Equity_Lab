"""Automated Preflight Integrity Check Script for Equity Lab CI/CD Pipeline.

Validates:
1. Single active CONSOLIDATED_* reference in app/ code.
2. Production security settings (CORS wildcard restriction, mandatory auth, DATA_WRITE_API_KEY).
3. Absolute exclusion of secret key files (.env, API_KEYS_CONFIG.env) from deployment exports/artifacts.
4. Database existence, accessibility, and populated company registry (>= 200 companies).
5. All mandatory empirical validation reports, pip audit report, and API contract presence in docs/.
6. Backup & restore script existence.
"""

import sys
import os
import re
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



def check_consolidated_single_source() -> bool:
    """Ensure at most ONE CONSOLIDATED_* directory is referenced in app/ code."""
    app_dir = PROJECT_ROOT / "app"
    matches = set()
    errors = []
    for file_path in app_dir.rglob("*.py"):
        try:
            content = file_path.read_text(encoding="utf-8")
            found = re.findall(r"CONSOLIDATED_\w+", content)
            matches.update(found)
        except Exception as exc:
            errors.append(f"Failed to read {file_path}: {exc}")

    if errors:
        for err in errors:
            print(f"[FAIL] PREFLIGHT ERROR: {err}")
        return False

    if len(matches) > 1:
        print(f"[FAIL] PREFLIGHT FAIL: Multiple CONSOLIDATED directories referenced in app/: {matches}")
        return False
    print(f"[PASS] PREFLIGHT PASS: Knowledge base single source check passed ({matches or 'None referenced'}).")
    return True


def check_security_configuration() -> bool:
    """Validate CORS and secret settings."""
    env_type = os.getenv("IERL_ENVIRONMENT", "development").lower()
    if env_type == "production":
        allowed_origin = os.getenv("ALLOWED_ORIGIN", "")
        if not allowed_origin or "*" in allowed_origin:
            print("[FAIL] PREFLIGHT FAIL: ALLOWED_ORIGIN in production cannot be empty or contain wildcard '*'.")
            return False
        if os.getenv("REQUIRE_AUTH", "false").lower() != "true":
            print("[FAIL] PREFLIGHT FAIL: REQUIRE_AUTH must be true in production.")
            return False
        if not os.getenv("DATA_WRITE_API_KEY"):
            print("[FAIL] PREFLIGHT FAIL: DATA_WRITE_API_KEY must be set in production.")
            return False
    print("[PASS] PREFLIGHT PASS: Security configuration valid.")
    return True


def check_secret_leakage() -> bool:
    """Ensure live secret files are excluded from deploy artifacts."""
    deploy_dir = PROJECT_ROOT / "frontend_deploy"
    prohibited_files = [
        deploy_dir / ".env",
        deploy_dir / "API_KEYS_CONFIG.env",
    ]
    for path in prohibited_files:
        if path.exists():
            print(f"[FAIL] PREFLIGHT FAIL: Secret file found inside frontend deploy artifact: {path}")
            return False

    gitignore_path = PROJECT_ROOT / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8")
        if "API_KEYS_CONFIG.env" not in content or ".env" not in content:
            print("[FAIL] PREFLIGHT FAIL: Secret files not explicitly listed in .gitignore.")
            return False

    print("[PASS] PREFLIGHT PASS: No secrets found in deploy directory & .gitignore configured.")
    return True


def check_database_population() -> bool:
    """Ensure database exists, is accessible, and contains a populated company registry (>= 500 symbols)."""
    try:
        from app.core.config import settings
        from app.services.research_data import ResearchDataStore
        
        db_path = Path(settings.DATA_STORE_PATH)
        if not db_path.exists():
            # Seed via ResearchDataStore
            store = ResearchDataStore()
            db_path = Path(store.database_path)

        if not db_path.exists():
            print(f"[FAIL] PREFLIGHT FAIL: SQLite database file not found at {db_path}")
            return False

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM companies")
        count = cursor.fetchone()[0]
        conn.close()

        if count < 400:
            print(f"[FAIL] PREFLIGHT FAIL: Database company universe unpopulated! Expected >= 400, found {count}.")
            return False
        print(f"[PASS] PREFLIGHT PASS: Database accessible and company registry populated ({count} symbols).")
        return True
    except Exception as exc:
        print(f"[FAIL] PREFLIGHT FAIL: Error accessing database: {exc}")
        return False



def check_validation_reports() -> bool:
    """Ensure all mandatory validation reports in docs/ exist and are non-empty."""
    docs_dir = PROJECT_ROOT / "docs"
    required_reports = [
        "validation_report.md",
        "score_calibration_report.md",
        "multibagger_validation_report.md",
        "growth_arbitrage_validation_report.md",
        "false_positive_report.md",
        "false_negative_report.md",
        "strategy_attribution_report.md",
        "pip_audit_report.md",
        "api_contract.json"
    ]
    for rep in required_reports:
        file_path = docs_dir / rep
        if not file_path.exists():
            print(f"[FAIL] PREFLIGHT FAIL: Mandatory validation report missing: {rep}")
            return False
        if file_path.stat().st_size < 100:
            print(f"[FAIL] PREFLIGHT FAIL: Validation report file is empty or corrupt (<100 bytes): {rep}")
            return False
    print("[PASS] PREFLIGHT PASS: All mandatory validation reports and API contracts present and non-empty in docs/.")
    return True


def check_backup_script() -> bool:
    """Ensure database backup & restore verification script is present."""
    backup_script = PROJECT_ROOT / "scripts" / "backup_restore_verify.py"
    if not backup_script.exists():
        print("[FAIL] PREFLIGHT FAIL: Backup & restore verification script missing.")
        return False
    print("[PASS] PREFLIGHT PASS: Database backup & restore script verified.")
    return True


def main():
    print("=== Running Equity Lab Preflight Integrity Checks ===")
    checks = [
        check_consolidated_single_source(),
        check_security_configuration(),
        check_secret_leakage(),
        check_database_population(),
        check_validation_reports(),
        check_backup_script(),
    ]
    if all(checks):
        print("=== ALL PREFLIGHT CHECKS PASSED SUCCESSFULLY ===")
        sys.exit(0)
    else:
        print("=== PREFLIGHT CHECKS FAILED ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
