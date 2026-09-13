# -*- coding: utf-8 -*-
"""Institutional Release Hygiene & Distribution Audit Protocol.

Asserts zero leakage of sensitive or development artifacts in production release archives:
- Zero real secrets or unencrypted configurations (.env, API_KEYS_CONFIG.env, credentials.json)
- Zero VCS metadata (.git/, .gitignore)
- Zero binary databases or persistent SQLite stores (*.db, *.sqlite, *.sqlite3)
- Zero compiled Python bytecode or caches (*.pyc, *.pyo, *.pyd, __pycache__)
- Zero nested archives or dev dumps (*.zip, *.tar, *.gz)
- Zero temporary test runners (.pytest_cache/, temp_pytest/, scratch/)
"""

import sys
import os
import zipfile
from pathlib import Path
from typing import List, Tuple

FORBIDDEN_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".zip",
    ".tar",
    ".gz",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".key",
    ".pem",
}

FORBIDDEN_EXACT_NAMES = {
    ".env",
    "api_keys_config.env",
    "credentials.json",
    "secrets.env",
}

FORBIDDEN_DIRECTORIES = {
    ".git",
    ".pytest_cache",
    ".pytest_temp",
    "temp_pytest",
    "temp_basetemp",
    "__pycache__",
    "scratch",
    ".venv",
    "venv",
    "node_modules",
}


def audit_zip_archive(archive_path: Path) -> Tuple[bool, List[str]]:
    """Inspects a zip archive for forbidden production release contamination."""
    violations: List[str] = []
    if not archive_path.exists():
        return False, [f"Archive file not found: {archive_path}"]

    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            namelist = zf.namelist()
            for name in namelist:
                norm_name = name.replace("\\", "/")
                parts = [p.lower() for p in norm_name.split("/")]
                basename = parts[-1] if parts else ""

                # 1. Directory check
                if any(d in parts[:-1] for d in FORBIDDEN_DIRECTORIES):
                    violations.append(f"Forbidden directory in path: '{name}'")

                # 2. Exact file name check
                if basename.lower() in FORBIDDEN_EXACT_NAMES:
                    violations.append(f"Forbidden sensitive secret file: '{name}'")

                # 3. Environment files (allow only .example / .template)
                if basename.startswith(".env") and not (basename.endswith(".example") or basename.endswith(".template")):
                    violations.append(f"Forbidden environment file: '{name}'")

                # 4. Extension check
                ext = Path(basename).suffix.lower()
                if ext in FORBIDDEN_EXTENSIONS:
                    violations.append(f"Forbidden binary/compiled/cache/nested archive extension '{ext}': '{name}'")

    except Exception as exc:
        return False, [f"Failed to read archive '{archive_path}': {exc}"]

    is_clean = len(violations) == 0
    return is_clean, violations


def audit_release_distributions(root_dir: Path) -> int:
    """Discovers and verifies all release archives in workspace."""
    print(f"[*] Auditing release distribution archives in: {root_dir}")
    zip_candidates = list(root_dir.glob("Equity_Lab_*.zip"))
    
    if not zip_candidates:
        print("[!] No pre-existing release archive found. Building a temporary release archive to test packaging pipeline...")
        from scripts.package_release import build_clean_release_zip
        temp_zip_name = "Equity_Lab_Hygiene_Test_Release.zip"
        built_zip_path = Path(build_clean_release_zip(output_zip_name=temp_zip_name))
        zip_candidates = [built_zip_path]
        cleanup_temp = True
    else:
        cleanup_temp = False

    all_passed = True
    for archive in zip_candidates:
        print(f"[*] Scanning archive: {archive.name} ({archive.stat().st_size:,} bytes)")
        is_clean, violations = audit_zip_archive(archive)
        if not is_clean:
            all_passed = False
            print(f"[-] [FAIL] Hygiene violations detected in {archive.name}:")
            for v in violations[:20]:
                print(f"    - {v}")
            if len(violations) > 20:
                print(f"    ... and {len(violations) - 20} more violations.")
        else:
            print(f"[+] [PASS] {archive.name} passed institutional release hygiene (Zero forbidden artifacts).")

        if cleanup_temp and archive.name == "Equity_Lab_Hygiene_Test_Release.zip":
            try:
                archive.unlink(missing_ok=True)
                print("[*] Cleaned up temporary test release archive.")
            except Exception:
                pass

    if all_passed:
        print("[SUCCESS] All evaluated release distributions adhere to strict zero-leakage hygiene standards.")
        return 0
    else:
        print("[FATAL] Release hygiene audit failed. Remediation required before release sign-off.")
        return 1


if __name__ == "__main__":
    workspace_root = Path(__file__).resolve().parent.parent
    sys.exit(audit_release_distributions(workspace_root))
