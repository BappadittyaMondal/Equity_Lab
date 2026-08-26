"""Canonical Clean-Room Build and Test Verification Script for Equity Lab.

Executes:
1. Environment preflight integrity checks (scripts/preflight_check.py)
2. Full pytest automated test suite (app/tests/)
"""

import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def run_step(command, description):
    print(f"\n========================================================")
    print(f"  RUNNING: {description}")
    print(f"========================================================")
    result = subprocess.run(command, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"\n[FAIL] Step failed: {description} (Exit code {result.returncode})")
        sys.exit(result.returncode)
    print(f"[PASS] Step passed: {description}")

def main():
    python_bin = sys.executable

    # 1. Preflight Integrity Check
    run_step(
        [python_bin, str(PROJECT_ROOT / "scripts" / "preflight_check.py")],
        "Preflight Integrity Checks"
    )

    # 2. Pytest Test Suite
    run_step(
        [python_bin, "-m", "pytest", "app/tests/", "-v", "--basetemp=temp_pytest"],
        "Pytest Full Validation Suite"
    )

    print("\n========================================================")
    print("  === ALL CLEAN-ROOM BUILD AND TEST GATES PASSED ===")
    print("========================================================\n")

if __name__ == "__main__":
    main()
