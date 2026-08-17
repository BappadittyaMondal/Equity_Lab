import os
import json
import pytest
import asyncio
from unittest import mock

from app.services import market_data
from app.core.config import settings

@pytest.fixture
def temp_db_path(tmp_path, monkeypatch):
    db_file = tmp_path / "test_market_cache.sqlite"
    original_path = getattr(market_data, "_CACHE_DB", settings.DATA_STORE_PATH)
    monkeypatch.setattr(market_data, "_CACHE_DB", str(db_file))
    monkeypatch.setattr(settings, "DATA_STORE_PATH", str(db_file))
    yield str(db_file)
    monkeypatch.setattr(market_data, "_CACHE_DB", original_path)
    monkeypatch.setattr(settings, "DATA_STORE_PATH", original_path)

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
