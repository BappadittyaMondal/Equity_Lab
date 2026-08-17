"""Build a clean AI platform upload ZIP archive excluding cache, venv, backups, and DBs.

This script creates `ierl_ai_upload_export.zip` in the repository root containing
only canonical platform code, documentation, scripts, and skills.
"""

import os
import sys
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_ZIP = BASE_DIR / "ierl_ai_upload_export.zip"

EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "ENV",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".pytest_temp",
    ".pytest_tmp",
    "temp_pytest",
    "backups",
    "node_modules",
    "dist",
    "build",
    ".gemini",
    "brain",
    "artifacts",
}

EXCLUDED_FILE_PATTERNS = {
    ".DS_Store",
    "Thumbs.db",
    "API_KEYS_CONFIG.env",
}

EXCLUDED_EXTENSIONS = {
    ".db",
    ".sqlite3",
    ".pyc",
    ".pyo",
    ".pyd",
    ".zip",
    ".tar",
    ".gz",
}


def should_exclude(rel_path: Path) -> bool:
    parts = set(rel_path.parts)
    if parts & EXCLUDED_DIR_NAMES:
        return True
    filename = rel_path.name
    if filename in EXCLUDED_FILE_PATTERNS:
        return True
    if rel_path.suffix.lower() in EXCLUDED_EXTENSIONS:
        return True
    if filename.startswith(".env") and filename != ".env.example":
        return True
    return False


def create_export() -> None:
    print(f"Creating export archive: {OUTPUT_ZIP.name}")
    file_count = 0
    total_bytes = 0

    with zipfile.ZipFile(OUTPUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(BASE_DIR):
            # Prune excluded directories in-place to skip walking into them
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES]
            
            for file in sorted(files):
                abs_file = Path(root) / file
                rel_file = abs_file.relative_to(BASE_DIR)
                
                if should_exclude(rel_file):
                    continue
                    
                zf.write(abs_file, arcname=str(rel_file).replace("\\", "/"))
                file_count += 1
                total_bytes += abs_file.stat().st_size

    zip_bytes = OUTPUT_ZIP.stat().st_size
    print(f"Export complete!")
    print(f"Total files packaged: {file_count:,}")
    print(f"Uncompressed size: {total_bytes / (1024 * 1024):.2f} MB")
    print(f"Compressed ZIP size: {zip_bytes / (1024 * 1024):.2f} MB")


def verify_export() -> bool:
    print("\nVerifying export ZIP contents...")
    violations = []
    with zipfile.ZipFile(OUTPUT_ZIP, "r") as zf:
        namelist = zf.namelist()
        for name in namelist:
            p = Path(name)
            parts = set(p.parts)
            if parts & EXCLUDED_DIR_NAMES:
                violations.append(f"Excluded directory found: {name}")
            if p.suffix.lower() in EXCLUDED_EXTENSIONS:
                violations.append(f"Excluded extension found: {name}")

    if violations:
        print("VERIFICATION FAILED:")
        for v in violations[:10]:
            print(f" - {v}")
        return False
    else:
        print("VERIFICATION PASSED: No excluded directories or extension patterns found in ZIP archive.")
        return True


if __name__ == "__main__":
    create_export()
    if not verify_export():
        sys.exit(1)
