"""Global Pytest Configuration for IERL OS Test Suite."""

import os
import shutil
import tempfile
import pytest
from app.core.config import settings

# Enforce offline test mode for fast, deterministic, reproducible unit testing
os.environ["OFFLINE_TEST_MODE"] = "true"


@pytest.fixture(scope="session", autouse=True)
def isolate_test_database():
    """Redirect all test database interactions to an ephemeral SQLite database.

    Prevents automated test runs from contaminating the production SQLite database.
    """
    temp_dir = tempfile.mkdtemp(prefix="ierl_test_db_")
    temp_db_path = os.path.join(temp_dir, "test_ierl_equity.sqlite3")

    prod_db = settings.DATA_STORE_PATH
    if os.path.exists(prod_db):
        shutil.copy2(prod_db, temp_db_path)

    os.environ["DATA_STORE_PATH"] = temp_db_path
    settings.DATA_STORE_PATH = temp_db_path

    yield temp_db_path

    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass


@pytest.fixture(autouse=True)
def set_offline_mode(monkeypatch):
    monkeypatch.setenv("OFFLINE_TEST_MODE", "true")

