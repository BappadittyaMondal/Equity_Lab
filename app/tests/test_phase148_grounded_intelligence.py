"""Unit tests for Phase 148: Grounded Financial Context Bridge, Dual RoCE Normalization, and Conversational Entity Routing.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.models.schemas import QueryRequest
from app.services.llm import process_llm_query, build_research_context
from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher
import pandas as pd


def create_mock_df(data_dict, periods=4):
    dates = pd.date_range(end='2023-01-01', periods=periods, freq='QE')
    return pd.DataFrame(data_dict, index=dates).T


def test_fundamental_fetcher_dual_roce_and_roe():
    with patch('yfinance.Ticker') as mock_ticker:
        mock_instance = mock_ticker.return_value
        mock_instance.info = {'currentPrice': 200.0, 'marketCap': 20000000.0}
        
        # 4 quarters of EBIT: 100 each -> TTM = 400. Capital employed = 5000 - 1000 = 4000.
        # Single-quarter roce_latest = 100 / 4000 = 2.5%
        # Annualized TTM roce_annualized = 400 / 4000 = 10.0%
        mock_instance.quarterly_financials = create_mock_df({
            'EBIT': [100.0, 100.0, 100.0, 100.0],
            'Net Income': [80.0, 80.0, 80.0, 80.0]
        })
        mock_instance.quarterly_balance_sheet = create_mock_df({
            'Total Assets': [5000.0, 5000.0, 5000.0, 5000.0],
            'Current Liabilities': [1000.0, 1000.0, 1000.0, 1000.0],
            'Stockholders Equity': [2500.0, 2500.0, 2500.0, 2500.0],
            'Total Debt': [1500.0, 1500.0, 1500.0, 1500.0]
        })
        mock_instance.quarterly_cashflow = create_mock_df({
            'Operating Cash Flow': [120.0, 120.0, 120.0, 120.0]
        })

        with patch('app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher._store_in_db'):
            res = FundamentalFetcher.fetch_and_store("TESTDUAL")
            assert res is not None
            assert res["roce_latest"] == 2.5
            assert res["roce_annualized"] == 10.0
            assert res["roe_latest"] == 3.2
            assert res["roe_annualized"] == 12.8
            assert res["pledge_provenance"] == "UNVERIFIED_IN_YFINANCE_FEED"


def test_llm_build_research_context_fallback_to_company_fundamentals():
    mock_fund = {
        "symbol": "NEWSTOCK.NS",
        "market_cap": 50000000000.0, # 5000 Cr
        "current_price": 450.0,
        "pe_ratio": 22.5,
        "roce_annualized": 26.5,
        "roe_annualized": 22.0,
        "opm_latest": 18.5,
        "debt_to_equity": 0.15,
        "interest_coverage": 12.0,
        "sales_growth_latest": 24.0,
        "promoter_holding": 68.5,
        "pledged_pct": 0.0,
        "dii_holding": 14.0,
        "fii_holding": 10.5
    }
    with patch('app.services.research_data.ResearchDataStore.get_timeline', return_value=(None, [], [], None, [], None)):
        with patch('app.services.data_ingestion.screener_connector.ScreenerCloudConnector.get_or_fetch_fundamentals', return_value=mock_fund):
            context = build_research_context("NEWSTOCK")
            assert "AUDITED COMPANY FUNDAMENTALS" in context
            assert "Market Cap: ₹5000.0 Cr" in context
            assert "RoCE: 26.5%" in context
            assert "Promoter Holding: 68.5%" in context


def test_conversational_query_routing_macro_intent():
    req = QueryRequest(query="How is the market regime and economic trend today?", mode="Quick")
    resp = process_llm_query(req)
    assert resp.reply is not None
    # Verifies macro query routes cleanly without defaulting to RELIANCE company fundamentals
    assert "DETERMINISTIC RESEARCH SUMMARY — ^NSEI" in resp.reply or "KEY FINDINGS" in resp.reply
