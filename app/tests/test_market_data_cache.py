import os
import json
import pytest
import asyncio
from unittest import mock

from app.services import market_data
from app.core.config import settings

import tempfile

@pytest.fixture
def temp_db_path(monkeypatch):
    db_fd, db_path_str = tempfile.mkstemp(suffix="_market_cache.sqlite")
    os.close(db_fd)
    original_path = getattr(market_data, "_CACHE_DB", settings.DATA_STORE_PATH)
    monkeypatch.setattr(market_data, "_CACHE_DB", db_path_str)
    monkeypatch.setattr(settings, "DATA_STORE_PATH", db_path_str)
    yield db_path_str
    monkeypatch.setattr(market_data, "_CACHE_DB", original_path)
    monkeypatch.setattr(settings, "DATA_STORE_PATH", original_path)
    from app.services.db import close_all_connections
    close_all_connections()
    import gc
    gc.collect()
    try:
        os.remove(db_path_str)
    except Exception:
        pass

def test_store_and_load_cache(temp_db_path):
    quote = {"symbol": "TEST", "price": 100.5, "currency": "INR"}
    # Store in cache
    market_data._store_in_cache("TEST", quote)
    # Load from cache
    cached = market_data._load_from_cache("TEST")
    assert cached is not None
    assert cached["price"] == 100.5

def test_provider_fallback(monkeypatch, temp_db_path):
    class FailingProvider(market_data.MarketDataProvider):
        async def get_quote(self, symbol: str):
            raise RuntimeError("Provider failure")

    class SuccessProvider(market_data.MarketDataProvider):
        async def get_quote(self, symbol: str):
            return {"symbol": symbol, "price": 123.4, "currency": "INR"}

    monkeypatch.setattr(market_data, "_PROVIDER_MAP", {"fail": FailingProvider, "success": SuccessProvider})
    monkeypatch.setenv("MARKET_DATA_PROVIDER_CHAIN", "fail,success")
    monkeypatch.setenv("OFFLINE_TEST_MODE", "false")
    market_data._PROVIDERS = None

    quote = asyncio.run(market_data._async_get_market_quote("TEST"))
    assert quote["price"] == 123.4
    assert quote["symbol"] == "TEST"


def test_get_latest_db_delivery_pct_retrieves_seeded_value(temp_db_path):
    # Ensure database schema is initialized
    conn = market_data._get_connection()
    try:
        conn.execute(
            """INSERT INTO market_daily_snapshots 
               (symbol, trading_date, open_price, high_price, low_price, close_price, volume, delivery_pct, published_at, source_name, source_url, ingested_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("DELIV_TEST.NS", "2025-01-01", 100.0, 105.0, 95.0, 102.0, 500000, 58.5, "2025-01-01T10:00:00Z", "Test", "http://test", "2025-01-01T10:00:00Z")
        )
        conn.commit()
    finally:
        conn.close()

    deliv_pct = market_data.get_latest_db_delivery_pct("DELIV_TEST.NS")
    assert deliv_pct == 58.5
