"""Unit and integration tests for Phase 4 Point-in-Time Integrity Audit.
"""

from datetime import datetime, timezone
import pytest

from app.core.config import settings
from app.services.backtesting.replay_engine import PointInTimeReplayEngine
from app.services.research_data import ResearchDataStore


@pytest.fixture
def temp_db_path(tmp_path):
    db_file = tmp_path / "test_validation.sqlite"
    original = settings.DATA_STORE_PATH
    settings.DATA_STORE_PATH = str(db_file)
    from app.services.db import _ensure_tables
    _ensure_tables()
    yield str(db_file)
    settings.DATA_STORE_PATH = original


def test_version_is_canonical():
    assert settings.VERSION in ["0.0.5", "0.0.9", "1.0.0"]


def test_look_ahead_protection(temp_db_path):
    store = ResearchDataStore()
    store.upsert_company({
        "symbol": "TESTCOMP",
        "company_name": "Test Company",
        "legal_name": "Test Company Ltd",
        "isin": "INE000A01010",
        "sector": "Technology",
    })

    # Add observation in past
    past_date = "2023-01-15T00:00:00Z"
    future_date = "2023-12-15T00:00:00Z"

    store.add_financial_observation({
        "symbol": "TESTCOMP",
        "metric": "revenue",
        "value": 1000.0,
        "unit": "INR_CR",
        "period_end": "2022-12-31",
        "period_type": "quarterly",
        "published_at": past_date,
        "source_name": "BSE Filing",
        "source_url": "https://bseindia.com/filing",
    })

    store.add_financial_observation({
        "symbol": "TESTCOMP",
        "metric": "revenue",
        "value": 2500.0,
        "unit": "INR_CR",
        "period_end": "2023-09-30",
        "period_type": "quarterly",
        "published_at": future_date,
        "source_name": "BSE Filing",
        "source_url": "https://bseindia.com/filing",
    })

    # Timeline at 2023-06-30 should NOT include 2023-12-15 observation
    as_of = datetime.fromisoformat("2023-06-30T23:59:59+00:00")
    comp, financials, events, corp_actions, ownership, docs = store.get_timeline("TESTCOMP", as_of=as_of)

    assert len(financials) == 1
    assert financials[0].value == 1000.0
