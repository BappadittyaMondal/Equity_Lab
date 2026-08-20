"""Unit tests for Data Ingestion Manager and Financial Statement Parser.
"""

from datetime import datetime, timezone
import pytest
from app.services.data.ingestion_manager import IngestionManager
from app.services.data.financial_statement_parser import FinancialStatementParser


@pytest.fixture
def ingestion_mgr():
    return IngestionManager()


@pytest.fixture
def parser():
    return FinancialStatementParser()


def test_symbol_normalization(ingestion_mgr):
    assert ingestion_mgr.normalize_symbol("RELIANCE") == "RELIANCE.NS"
    assert ingestion_mgr.normalize_symbol("tata-motors.ns") == "TATA-MOTORS.NS"
    assert ingestion_mgr.normalize_symbol("500325.BO") == "500325.BO"


def test_ingest_quarterly_financials_and_retrieve(ingestion_mgr):
    sample_records = [
        {
            "symbol": "TCS.NS",
            "period_ended": "2026-03-31",
            "revenue": 62000.0,
            "operating_profit": 16000.0,
            "net_profit": 12500.0,
            "eps": 34.5,
            "operating_margin_pct": 25.8,
            "net_margin_pct": 20.1,
            "roce_pct": 42.0,
            "roe_pct": 38.0,
            "as_of_date": "2026-04-15T00:00:00Z",
            "source": "bse_filing",
        },
        {
            "symbol": "TCS.NS",
            "period_ended": "2025-12-31",
            "revenue": 60500.0,
            "operating_profit": 15500.0,
            "net_profit": 12000.0,
            "eps": 33.1,
            "as_of_date": "2026-01-15T00:00:00Z",
            "source": "bse_filing",
        },
    ]

    count = ingestion_mgr.ingest_quarterly_financials(sample_records)
    assert count == 2

    # Point-in-Time Query: Before April 2026 filing publication
    pit_jan = ingestion_mgr.get_latest_financials("TCS.NS", as_of_date="2026-02-01T00:00:00Z")
    assert len(pit_jan) == 1
    assert pit_jan[0]["period_ended"] == "2025-12-31"

    # Point-in-Time Query: After April 2026 filing publication
    pit_may = ingestion_mgr.get_latest_financials("TCS.NS", as_of_date="2026-05-01T00:00:00Z")
    assert len(pit_may) == 2
    assert pit_may[0]["period_ended"] == "2026-03-31"


def test_promoter_shareholding_ingestion(ingestion_mgr):
    promoter_data = [
        {
            "symbol": "INFY",
            "period_ended": "2026-03-31",
            "promoter_holding_pct": 14.8,
            "pledged_pct": 0.0,
            "institutional_holding_pct": 62.5,
            "as_of_date": "2026-04-10T00:00:00Z",
            "source": "nse_shareholding",
        }
    ]

    count = ingestion_mgr.ingest_promoter_shareholding(promoter_data)
    assert count == 1


def test_financial_statement_parser_margin_calculation(parser):
    raw = {
        "symbol": "HDFCBANK",
        "period_ended": "2026-03-31",
        "revenue": 50000.0,
        "operating_profit": 20000.0,
        "net_profit": 15000.0,
        "eps": 25.0,
    }

    parsed = parser.parse_quarterly_statement(raw)
    assert parsed["symbol"] == "HDFCBANK"
    assert parsed["operating_margin_pct"] == 40.0
    assert parsed["net_margin_pct"] == 30.0
    assert parsed["data_insufficient"] is False


def test_financial_statement_parser_growth_rates(parser):
    quarters = [
        {"symbol": "TITAN.NS", "period_ended": "2026-03-31", "revenue": 12000.0, "net_profit": 1100.0},
        {"symbol": "TITAN.NS", "period_ended": "2025-12-31", "revenue": 11000.0, "net_profit": 1000.0},
        {"symbol": "TITAN.NS", "period_ended": "2025-09-30", "revenue": 10500.0, "net_profit": 950.0},
        {"symbol": "TITAN.NS", "period_ended": "2025-06-30", "revenue": 10000.0, "net_profit": 900.0},
        {"symbol": "TITAN.NS", "period_ended": "2025-03-31", "revenue": 10000.0, "net_profit": 880.0},
    ]

    growth = parser.compute_growth_rates(quarters)
    assert growth["symbol"] == "TITAN.NS"
    assert growth["qoq_revenue_growth"] == round(((12000.0 - 11000.0) / 11000.0) * 100.0, 2)
    assert growth["yoy_revenue_growth"] == round(((12000.0 - 10000.0) / 10000.0) * 100.0, 2)
    assert growth["yoy_pat_growth"] == round(((1100.0 - 880.0) / 880.0) * 100.0, 2)
    assert growth["data_insufficient"] is False
