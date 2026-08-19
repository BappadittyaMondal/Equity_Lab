"""Global Pytest Configuration for IERL OS Test Suite."""

import os
import pytest

# Enforce offline test mode for fast, deterministic, reproducible unit testing
os.environ["OFFLINE_TEST_MODE"] = "true"


@pytest.fixture(autouse=True)
def set_offline_mode(monkeypatch):
    monkeypatch.setenv("OFFLINE_TEST_MODE", "true")
