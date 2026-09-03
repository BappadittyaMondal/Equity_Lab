#!/usr/bin/env python3
"""
Pre-commit / CI Safeguard Script: check_no_real_secrets.py
Scans repository files for real API keys, credentials, or tokens using structural regex patterns.
Exits with 0 if clean, or 1 if unscrubbed credentials are detected.
"""

import sys
import os
import re
import zipfile

PATTERNS = [
    (re.compile(r'AIzaSy[A-Za-z0-9_-]{33}'), "Google AI / Gemini API Key"),
    (re.compile(r'gsk_[A-Za-z0-9]{48,}'), "Groq API Key"),
    (re.compile(r'sk-proj-[A-Za-z0-9_-]{40,}'), "OpenAI Project API Key"),
    (re.compile(r'sk-[A-Za-z0-9]{32,}'), "OpenAI API Key"),
    (re.compile(r'ghp_[A-Za-z0-9]{36}'), "GitHub Personal Access Token"),
    (re.compile(r'(?i)alpha_?vantage.*[=:][\s"\']([A-Z0-9]{16})["\']'), "Alpha Vantage API Key Assignment"),
    (re.compile(r'(?i)angel_?one.*totp.*[=:][\s"\']([A-Z2-7]{26,32})["\']'), "Angel One TOTP Secret Assignment"),
    (re.compile(r'(?i)angel_?one.*api_?key.*[=:][\s"\']([A-Za-z0-9]{8,16})["\']'), "Angel One API Key Assignment"),
]

EXCLUDE_DIRS = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', '.pytest_temp', '.pytest_tmp', 'unnecessary_files_archive', 'Not_Required_Upload', 'scratch'}

FORBIDDEN_ARCHIVE_EXTENSIONS = ('.env', '.db', '.sqlite', '.sqlite3', '.pem', '.key')

def scan_repo():
    findings = []
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    for current_root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            filepath = os.path.join(current_root, file)
            relpath = os.path.relpath(filepath, root_dir)
            
            # Skip script checking itself or innocuous image binaries
            if file in ('check_no_real_secrets.py', 'scan_secrets.py') or file.endswith(('.png', '.jpg', '.jpeg', '.pyc', '.exe')):
                continue

            # Recursive inspection of ZIP archives
            if file.endswith('.zip'):
                try:
                    with zipfile.ZipFile(filepath, 'r') as zf:
                        for info in zf.infolist():
                            fname = info.filename.lower()
                            if fname.endswith(FORBIDDEN_ARCHIVE_EXTENSIONS) or '.git/' in fname:
                                findings.append((f"{relpath}::{info.filename}", "Forbidden Sensitive File in Archive", info.filename))
                            if any(fname.endswith(ext) for ext in ('.py', '.env', '.json', '.txt', '.md', '.yml', '.yaml')):
                                try:
                                    with zf.open(info) as zf_file:
                                        content = zf_file.read().decode('utf-8', errors='ignore')
                                        for pattern, desc in PATTERNS:
                                            matches = pattern.findall(content)
                                            for match in matches:
                                                match_str = match if isinstance(match, str) else str(match)
                                                if "your_" not in match_str.lower() and "placeholder" not in match_str.lower():
                                                    findings.append((f"{relpath}::{info.filename}", desc, match_str))
                                except Exception:
                                    pass
                except Exception as ex:
                    findings.append((relpath, f"Corrupted or Unreadable Archive: {ex}", file))
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern, desc in PATTERNS:
                        matches = pattern.findall(content)
                        for match in matches:
                            match_str = match if isinstance(match, str) else str(match)
                            if "your_" not in match_str.lower() and "placeholder" not in match_str.lower():
                                findings.append((relpath, desc, match_str))
            except Exception as e:
                pass

    if findings:
        print("[FAIL] SECURITY AUDIT FAILED: Real secrets or unscrubbed credentials detected!")
        for relpath, desc, match in findings:
            masked = match[:4] + "*" * (len(match) - 8) + match[-4:] if len(match) > 8 else "****"
            print(f"  - {relpath}: Found {desc} ({masked})")
        sys.exit(1)
    else:
        print("[OK] SECURITY AUDIT PASSED: No real secrets or credentials detected in repository.")
        sys.exit(0)

if __name__ == '__main__':
    scan_repo()
