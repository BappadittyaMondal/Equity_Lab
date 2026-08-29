# -*- coding: utf-8 -*-
"""Release packaging hygiene tool for Equity Lab.

Cleans cache directories, temporary pytest folders, and scratch build artifacts before packaging release artifacts.
"""

import sys
import os
import shutil
import argparse
from pathlib import Path

IGNORE_PATTERNS = [
    ".pytest_cache",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "scratch",
    "temp_pytest",
    ".pytest_temp"
]

def clean_workspace(root_dir: Path, verify_only: bool = False) -> int:
    removed_count = 0
    print(f"[*] Scanning workspace directory: {root_dir}")
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dp = Path(dirpath)
        
        # Remove __pycache__ and .pytest_cache
        if dp.name in [".pytest_cache", "__pycache__", "scratch", "temp_pytest", ".pytest_temp"]:
            if dp.name == "scratch" and "brain" in str(dp):
                continue  # Preserve antigravity internal brain scratch
            print(f"  [+] Found dev artifact: {dp}")
            removed_count += 1
            if not verify_only:
                try:
                    shutil.rmtree(dp)
                except Exception as e:
                    print(f"      [!] Warning: Could not remove {dp}: {e}")
                    
        for f in filenames:
            if f.endswith(".pyc") or f.endswith(".pyo"):
                fp = dp / f
                removed_count += 1
                if not verify_only:
                    try:
                        fp.unlink()
                    except Exception as e:
                        print(f"      [!] Warning: Could not unlink {fp}: {e}")
                        
    if verify_only:
        print(f"[SUCCESS] Verification complete. Found {removed_count} dev artifact files/folders eligible for cleanup.")
    else:
        print(f"[SUCCESS] Packaging hygiene cleanup complete. Removed {removed_count} item(s).")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Equity Lab Release Package Hygiene Tool")
    parser.add_argument("--verify", action="store_true", help="Scan and report dev artifacts without deleting")
    args = parser.parse_args()
    
    workspace = Path(__file__).parent.parent
    sys.exit(clean_workspace(workspace, verify_only=args.verify))
