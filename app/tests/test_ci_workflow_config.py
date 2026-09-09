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


def test_boot_guards_production_abort(monkeypatch):
    """Verify that enforce_production_boot_invariants hard-aborts if OFFLINE_TEST_MODE is true in production."""
    import pytest
    from app.core.boot_guards import enforce_production_boot_invariants

    monkeypatch.setenv("IERL_ENVIRONMENT", "production")
    monkeypatch.setenv("OFFLINE_TEST_MODE", "true")

    with pytest.raises(RuntimeError, match="OFFLINE_TEST_MODE=true is prohibited in production"):
        enforce_production_boot_invariants()

