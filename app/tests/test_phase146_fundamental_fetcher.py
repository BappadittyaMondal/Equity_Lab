import pytest
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np

from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher
from app.services.data_ingestion.screener_connector import ScreenerCloudConnector

@pytest.fixture
def mock_yf_ticker():
    with patch('yfinance.Ticker') as mock_ticker:
        yield mock_ticker

def create_mock_df(data_dict, periods=4):
    """Helper to create mock DataFrames similar to yfinance structure"""
    dates = pd.date_range(end='2023-01-01', periods=periods, freq='QE')
    return pd.DataFrame(data_dict, index=dates).T

def test_fundamental_fetcher_returns_dict_for_known_stock(mock_yf_ticker):
    mock_instance = mock_yf_ticker.return_value
    mock_instance.info = {
        'shortName': 'Test Corp',
        'currentPrice': 150.0,
        'marketCap': 1000000.0,
        'trailingEps': 5.5
    }
    mock_instance.quarterly_financials = create_mock_df({
        'Net Income': [100.0, 110.0, 105.0, 90.0],
        'Total Revenue': [1000.0, 1050.0, 1000.0, 950.0]
    })
    mock_instance.quarterly_balance_sheet = create_mock_df({
        'Total Assets': [5000.0, 4900.0, 4800.0, 4700.0],
        'Current Liabilities': [1000.0, 950.0, 900.0, 850.0]
    })
    mock_instance.quarterly_cashflow = create_mock_df({
        'Operating Cash Flow': [150.0, 160.0, 140.0, 130.0]
    })

    with patch('app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher._store_in_db') as mock_store:
        result = FundamentalFetcher.fetch_and_store("TEST")
        
        assert result is not None
        assert result["symbol"] == "TEST.NS"
        assert result["company_name"] == "Test Corp"
        assert result["current_price"] == 150.0
        assert result["eps_latest"] == 5.5
        mock_store.assert_called_once()

def test_fundamental_fetcher_computes_roce(mock_yf_ticker):
    mock_instance = mock_yf_ticker.return_value
    mock_instance.info = {'currentPrice': 100.0}
    # RoCE = EBIT / (Total Assets - Current Liabilities) * 100
    # 500 / (5000 - 1000) = 500 / 4000 = 12.5%
    mock_instance.quarterly_financials = create_mock_df({'EBIT': [500.0]})
    mock_instance.quarterly_balance_sheet = create_mock_df({
        'Total Assets': [5000.0],
        'Current Liabilities': [1000.0]
    })
    
    with patch('app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher._store_in_db'):
        result = FundamentalFetcher.fetch_and_store("TEST2")
        assert result is not None
        assert result["roce_latest"] == 12.5

def test_fundamental_fetcher_computes_debt_to_equity(mock_yf_ticker):
    mock_instance = mock_yf_ticker.return_value
    mock_instance.info = {'currentPrice': 100.0}
    # D/E = Total Debt / Shareholder Equity
    # 2000 / 4000 = 0.5
    mock_instance.quarterly_balance_sheet = create_mock_df({
        'Total Debt': [2000.0],
        'Stockholders Equity': [4000.0]
    })
    
    with patch('app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher._store_in_db'):
        result = FundamentalFetcher.fetch_and_store("TEST3")
        assert result is not None
        assert result["debt_to_equity"] == 0.5

def test_fundamental_fetcher_handles_missing_data_gracefully(mock_yf_ticker):
    mock_instance = mock_yf_ticker.return_value
    mock_instance.info = {} # Empty info
    
    result = FundamentalFetcher.fetch_and_store("BADDATA")
    assert result is None

def test_fundamental_fetcher_cache_freshness():
    # Cache is less than 24h old
    recent_time = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    cached_data = {"symbol": "FRESH.NS", "updated_at": recent_time, "roce_latest": 15.0}
    
    with patch('app.services.data_ingestion.screener_connector.ScreenerCloudConnector.get_company_fundamentals', return_value=cached_data):
        with patch('app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher.fetch_and_store') as mock_live_fetch:
            result = ScreenerCloudConnector.get_or_fetch_fundamentals("FRESH")
            assert result == cached_data
            mock_live_fetch.assert_not_called()

def test_get_or_fetch_falls_back_to_cache():
    # Cache is stale (> 24h old)
    stale_time = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    cached_data = {"symbol": "STALE.NS", "updated_at": stale_time, "roce_latest": 10.0}
    
    with patch('app.services.data_ingestion.screener_connector.ScreenerCloudConnector.get_company_fundamentals', return_value=cached_data):
        with patch('app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher.fetch_and_store', side_effect=Exception("API Down")):
            result = ScreenerCloudConnector.get_or_fetch_fundamentals("STALE")
            # Should return stale cache because live fetch failed
            assert result == cached_data

def test_fundamental_fetcher_batch(mock_yf_ticker):
    mock_instance = mock_yf_ticker.return_value
    mock_instance.info = {'currentPrice': 100.0}
    
    with patch('app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher._store_in_db'):
        results = FundamentalFetcher.fetch_batch(["BATCH1", "BATCH2"])
        assert len(results) == 2
        assert results[0]["symbol"] == "BATCH1.NS"
        assert results[1]["symbol"] == "BATCH2.NS"
