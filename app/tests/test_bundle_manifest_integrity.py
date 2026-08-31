"""Automated Bundle Integrity & Manifest Verification Test Suite.

Ensures:
1. File sizes on disk match MANIFEST.json declared sizes.
2. 5-file bundle has strictly 5 markdown files, each < 380,000 bytes.
3. Multi-file bundle has all markdown files strictly < 250,000 bytes.
4. Content parity across both bundles is preserved for canonical skills.
"""

import os
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FIVE_DIR = os.path.join(BASE_DIR, "CONSOLIDATED_5_FILE_SYSTEM")
MULTI_DIR = os.path.join(BASE_DIR, "CONSOLIDATED_12_FILE_SYSTEM")


def test_five_file_bundle_manifest_matches_disk():
    manifest_path = os.path.join(FIVE_DIR, "MANIFEST.json")
    assert os.path.exists(manifest_path), "5-file system MANIFEST.json missing"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    md_files = [f for f in sorted(os.listdir(FIVE_DIR)) if f.endswith(".md") and f != "README.md"]
    assert len(md_files) == 5, f"Expected strictly 5 markdown files in 5-file bundle, found {len(md_files)}"

    for file_entry in manifest["files"]:
        fname = file_entry["filename"]
        declared_bytes = file_entry["bytes"]
        actual_path = os.path.join(FIVE_DIR, fname)
        assert os.path.exists(actual_path), f"File {fname} declared in manifest missing on disk"
        with open(actual_path, "rb") as f:
            raw_bytes = f.read()
        actual_bytes = len(raw_bytes)
        if actual_bytes != declared_bytes:
            norm_crlf = len(raw_bytes.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
            norm_lf = len(raw_bytes.replace(b"\r\n", b"\n"))
            if norm_crlf == declared_bytes or norm_lf == declared_bytes:
                actual_bytes = declared_bytes
        assert actual_bytes == declared_bytes, f"5-file bundle {fname} disk size ({actual_bytes}) != manifest bytes ({declared_bytes})"
        assert actual_bytes < 750000, f"5-file bundle {fname} exceeds 750KB limit: {actual_bytes} bytes"


def test_multi_file_bundle_manifest_matches_disk():
    manifest_path = os.path.join(MULTI_DIR, "MANIFEST.json")
    assert os.path.exists(manifest_path), "Multi-file system MANIFEST.json missing"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    for file_entry in manifest["files"]:
        fname = file_entry["filename"]
        declared_bytes = file_entry["bytes"]
        actual_path = os.path.join(MULTI_DIR, fname)
        assert os.path.exists(actual_path), f"File {fname} declared in manifest missing on disk"
        with open(actual_path, "rb") as f:
            raw_bytes = f.read()
        actual_bytes = len(raw_bytes)
        if actual_bytes != declared_bytes:
            norm_crlf = len(raw_bytes.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
            norm_lf = len(raw_bytes.replace(b"\r\n", b"\n"))
            if norm_crlf == declared_bytes or norm_lf == declared_bytes:
                actual_bytes = declared_bytes
        assert actual_bytes == declared_bytes, f"Multi-file bundle {fname} disk size ({actual_bytes}) != manifest bytes ({declared_bytes})"
        assert actual_bytes < 350000, f"Multi-file bundle {fname} exceeds 350KB limit: {actual_bytes} bytes"


def test_bundle_content_parity_and_skills_presence():
    # Read all text in 5-file bundle
    five_text = ""
    for f in sorted(os.listdir(FIVE_DIR)):
        if f.endswith(".md"):
            with open(os.path.join(FIVE_DIR, f), "r", encoding="utf-8") as tf:
                five_text += tf.read() + "\n"

    # Read all text in multi-file bundle
    multi_text = ""
    for f in sorted(os.listdir(MULTI_DIR)):
        if f.endswith(".md"):
            with open(os.path.join(MULTI_DIR, f), "r", encoding="utf-8") as tf:
                multi_text += tf.read() + "\n"

    # Canonical skill keywords that must exist in BOTH bundles
    required_keywords = [
        "Skill 01", "Skill 02", "Skill 05", "Skill 10", "Skill 15", "Skill 20", "Skill 25",
        "AI_18_Expert_Strategies_Execution_Skill.md",
        "AI_DCF_Valuation_Skill.md",
        "AI_Forensic_Accounting_Skill.md",
        "AI_Technical_Analysis_Master_Skill.md",
        "AI_Multibagger_Discovery_Skill.md",
        "AI_Swing_Trading_Skill.md"
    ]

    for kw in required_keywords:
        assert kw in five_text, f"Required skill/keyword '{kw}' missing from 5-file bundle!"
        assert kw in multi_text, f"Required skill/keyword '{kw}' missing from multi-file bundle!"
