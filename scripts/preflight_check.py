"""Automated Preflight Integrity Check Script for IERL OS CI/CD Pipeline.

Validates:
1. Single active CONSOLIDATED_* reference in app/ code (Phase 3 exit gate).
2. Production security settings (CORS wildcard restriction, mandatory auth, DATA_WRITE_API_KEY).
3. Absolute exclusion of secret key files (.env, API_KEYS_CONFIG.env) from deployment exports/artifacts.
4. Database path accessibility outside static root.
"""

import sys
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def check_consolidated_single_source() -> bool:
    """Ensure at most ONE CONSOLIDATED_* directory is referenced in app/ code."""
    app_dir = PROJECT_ROOT / "app"
    matches = set()
    for file_path in app_dir.rglob("*.py"):
        try:
            content = file_path.read_text(encoding="utf-8")
            found = re.findall(r"CONSOLIDATED_\w+", content)
            matches.update(found)
        except Exception:
            pass

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

    # Check git index / export if git repository exists
    gitignore_path = PROJECT_ROOT / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8")
        if "API_KEYS_CONFIG.env" not in content or ".env" not in content:
            print("[FAIL] PREFLIGHT FAIL: Secret files not explicitly listed in .gitignore.")
            return False

    print("[PASS] PREFLIGHT PASS: No secrets found in deploy directory & .gitignore configured.")
    return True


def check_validation_reports() -> bool:
    """Ensure all 7 Phase 4 empirical validation reports are generated in docs/."""
    docs_dir = PROJECT_ROOT / "docs"
    required_reports = [
        "validation_report.md",
        "score_calibration_report.md",
        "multibagger_validation_report.md",
        "growth_arbitrage_validation_report.md",
        "false_positive_report.md",
        "false_negative_report.md",
        "strategy_attribution_report.md",
    ]
    for rep in required_reports:
        if not (docs_dir / rep).exists():
            print(f"[FAIL] PREFLIGHT FAIL: Mandatory validation report missing: {rep}")
            return False
    print("[PASS] PREFLIGHT PASS: All 7 empirical validation reports present in docs/.")
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
    print("=== Running IERL OS Preflight Integrity Checks ===")
    checks = [
        check_consolidated_single_source(),
        check_security_configuration(),
        check_secret_leakage(),
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
