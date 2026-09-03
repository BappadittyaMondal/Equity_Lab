"""Automated Clean Production Release Packaging Script.

Creates a clean, production-ready ZIP artifact of the Equity Lab project,
automatically excluding:
- .git / .pytest_cache / .pytest_temp / temp_pytest
- ierl_ai_upload_export.zip (nested zip artifacts)
- api_legacy/
- scratch/
- __pycache__ / *.pyc / *.pyo
"""

import os
import shutil
import zipfile
from pathlib import Path


EXCLUDE_DIRS = {
    ".git",
    ".pytest_cache",
    ".pytest_temp",
    "temp_pytest",
    "temp_basetemp",
    "api_legacy",
    "scratch",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
}

EXCLUDE_FILES = {
    ".env",
    "API_KEYS_CONFIG.env",
    "credentials.json",
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".zip",
    ".sqlite",
    ".sqlite3",
    ".db",
}


def build_clean_release_zip(output_zip_name: str = "Equity_Lab_v0.3.0_Clean_Release.zip") -> str:
    root_dir = Path(__file__).resolve().parent.parent
    output_path = root_dir / output_zip_name

    print(f"Building clean release archive at: {output_path}")
    count = 0

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip_out:
        for item in root_dir.rglob("*"):
            if item.name == output_zip_name or item.suffix in EXCLUDE_EXTENSIONS or item.name in EXCLUDE_FILES:
                continue

            rel_path = item.relative_to(root_dir)
            parts = rel_path.parts

            if any(part in EXCLUDE_DIRS for part in parts):
                continue

            if item.is_file():
                zip_out.write(item, arcname=rel_path)
                count += 1

    print(f"Successfully packaged {count} files into {output_zip_name}")
    return str(output_path)


if __name__ == "__main__":
    build_clean_release_zip()
