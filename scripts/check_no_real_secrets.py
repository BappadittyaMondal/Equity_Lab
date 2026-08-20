#!/usr/bin/env python3
"""
Pre-commit / CI Safeguard Script: check_no_real_secrets.py
Scans repository files for real API keys, credentials, or tokens.
Exits with 0 if clean, or 1 if unscrubbed credentials are detected.
"""

import sys
import os
import re

PATTERNS = [
    (re.compile(r'AIzaSy[A-Za-z0-9_-]{33}'), "Google AI / Gemini API Key"),
    (re.compile(r'gsk_[A-Za-z0-9]{48,}'), "Groq API Key"),
    (re.compile(r'sk-proj-[A-Za-z0-9_-]{40,}'), "OpenAI Project API Key"),
    (re.compile(r'sk-[A-Za-z0-9]{32,}'), "OpenAI API Key"),
    (re.compile(r'ghp_[A-Za-z0-9]{36}'), "GitHub Personal Access Token"),
    (re.compile(r'P169VNJ4OA0C9PP6'), "Alpha Vantage API Key"),
    (re.compile(r'PBDOZTKGCQI7SYLDHSIE6B3UPM'), "Angel One TOTP Secret"),
    (re.compile(r'1UqpybT5'), "Angel One Smart API Key"),
    (re.compile(r'Omira@2018'), "Angel One Password"),
    (re.compile(r'B261090'), "Angel One Client Code"),
]

EXCLUDE_DIRS = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', '.pytest_temp', '.pytest_tmp', 'unnecessary_files_archive', 'Not_Required_Upload', 'scratch'}

def scan_repo():
    findings = []
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    for current_root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            filepath = os.path.join(current_root, file)
            relpath = os.path.relpath(filepath, root_dir)
            
            # Skip binary or script checking itself
            if file in ('check_no_real_secrets.py', 'scan_secrets.py') or file.endswith(('.png', '.jpg', '.jpeg', '.pyc', '.zip', '.exe', '.db', '.sqlite3')):
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern, desc in PATTERNS:
                        matches = pattern.findall(content)
                        for match in matches:
                            if "your_" not in match.lower() and "placeholder" not in match.lower():
                                findings.append((relpath, desc, match))
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
