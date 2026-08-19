"""Build a clean AI platform upload ZIP archive and synchronize Upload_97Files_AI_Project directory.

This script walks the full live tree (app/services/strategies/, app/services/decision_brain/,
app/services/monitoring/, app/services/orchestration/, app/services/backtesting/, etc.),
synchronizes python files into Upload_97Files_AI_Project/, stamps SHA256-per-source MANIFEST.json,
and creates `ierl_ai_upload_export.zip` in the repository root.
"""

import hashlib
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "Upload_97Files_AI_Project"
OUTPUT_ZIP = BASE_DIR / "ierl_ai_upload_export.zip"

LIVE_TREE_SEARCH_DIRS = [
    BASE_DIR / "app" / "services" / "strategies",
    BASE_DIR / "app" / "services" / "decision_brain",
    BASE_DIR / "app" / "services" / "monitoring",
    BASE_DIR / "app" / "services" / "orchestration",
    BASE_DIR / "app" / "services" / "backtesting",
    BASE_DIR / "app" / "services" / "synthesis",
    BASE_DIR / "app" / "services",
    BASE_DIR / "app" / "core",
    BASE_DIR / "app" / "models",
    BASE_DIR / "app",
    BASE_DIR / "scripts",
]

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


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    hasher.update(filepath.read_bytes())
    return hasher.hexdigest()


def sync_live_tree_to_upload_dir() -> int:
    """Sync live Python files into Upload_97Files_AI_Project."""
    UPLOAD_DIR.mkdir(exist_ok=True)
    synced_count = 0
    
    for search_dir in LIVE_TREE_SEARCH_DIRS:
        if not search_dir.exists():
            continue
        for root, dirs, files in os.walk(search_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES]
            for file in sorted(files):
                abs_file = Path(root) / file
                if abs_file.suffix.lower() == ".py":
                    dest_file = UPLOAD_DIR / file
                    shutil.copy2(abs_file, dest_file)
                    synced_count += 1
                    
    print(f"Synchronized {synced_count} live python source files to `{UPLOAD_DIR.name}/`")
    return synced_count


def generate_manifest() -> dict:
    """Generate SHA256 manifest for all files in Upload_97Files_AI_Project."""
    manifest_entries = {}
    if UPLOAD_DIR.exists():
        for filepath in sorted(UPLOAD_DIR.glob("*")):
            if filepath.is_file() and not should_exclude(filepath.relative_to(BASE_DIR)):
                digest = compute_sha256(filepath)
                manifest_entries[filepath.name] = {
                    "sha256": digest,
                    "bytes": filepath.stat().st_size,
                    "last_modified": datetime.fromtimestamp(filepath.stat().st_mtime, timezone.utc).isoformat()
                }

    manifest_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_files": len(manifest_entries),
        "files": manifest_entries
    }

    manifest_path = UPLOAD_DIR / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8", newline="")
    print(f"Stamped MANIFEST.json in `{UPLOAD_DIR.name}/` with {len(manifest_entries)} source hashes.")
    return manifest_data


def create_export() -> None:
    sync_live_tree_to_upload_dir()
    generate_manifest()
    
    print(f"Creating export archive: {OUTPUT_ZIP.name}")
    file_count = 0
    total_bytes = 0

    with zipfile.ZipFile(OUTPUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(BASE_DIR):
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
