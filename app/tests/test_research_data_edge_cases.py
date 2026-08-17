import pytest
import os
from datetime import datetime, timezone
from app.services.research_data import ResearchDataStore
from app.core.config import settings

@pytest.fixture
def temp_db_path(tmp_path):
    db_file = tmp_path / "test_research.sqlite"
    original = settings.DATA_STORE_PATH
    settings.DATA_STORE_PATH = str(db_file)
    yield str(db_file)
    settings.DATA_STORE_PATH = original

def test_missing_symbol_upsert_company(temp_db_path):
    store = ResearchDataStore()
    # Upsert a company with missing required fields should raise HTTPException
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        store.upsert_company({})
    assert exc.value.status_code == 400

def test_duplicate_company_upsert(temp_db_path):
    store = ResearchDataStore()
    company = {
        "symbol": "TEST",
        "legal_name": "Test Corp",
        "sector": "Tech",
        "industry": "Software",
    }
    # First insert succeeds
    res1 = store.upsert_company(company)
    assert res1.symbol == "TEST.NS"
    # Second insert with same symbol updates existing record cleanly
    res2 = store.upsert_company(company)
    assert res2.symbol == "TEST.NS"

def test_invalid_timestamp_financial_observation(temp_db_path):
    store = ResearchDataStore()
    # Insert a company first
    store.upsert_company({"symbol": "TEST", "legal_name": "Test Corp"})
    # Provide an invalid datetime string
    bad_obs = {
        "symbol": "TEST",
        "metric": "revenue",
        "value": 1000,
        "unit": "USD",
        "period_end": "not-a-date",
        "period_type": "quarterly",
        "statement_scope": "consolidated",
        "published_at": "invalid",
        "source_name": "source",
        "source_url": "http://example.com",
        "confidence": 0.9,
    }
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        store.upsert_financial_observation(bad_obs)
    assert exc.value.status_code == 400
