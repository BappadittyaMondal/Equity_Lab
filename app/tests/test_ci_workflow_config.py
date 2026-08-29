# -*- coding: utf-8 -*-
"""Test suite verifying CI/CD workflow configuration."""

import os


def test_ci_workflow_exists():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ci_path = os.path.join(base_dir, ".github", "workflows", "ci.yml")
    assert os.path.exists(ci_path), "CI/CD workflow file .github/workflows/ci.yml missing!"
    
    with open(ci_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "name: Equity Lab CI/CD" in content
    assert "python -m pytest app/tests/" in content
