"""
Unit and integration tests for Phase 37 enhancements:
1. Sector-calibrated WACC Matrix in Forward DCF (run_dcf_forward, resolve_sector_wacc)
2. Daily Bulk & Block Deals T+0 Tracking & Point-in-Time Persistence (ResearchDataStore, shareholding_pattern)
3. Smart Money Entity Matching (Vijay Kedia, Ashish Kacholia, Mukul Agrawal, Marquee Institutions)
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from app.services.strategies.dcf_forward import (
    SECTOR_WACC_MATRIX,
    resolve_sector_wacc,
    run_dcf_forward,
)
from app.services.strategies.shareholding_pattern import (
    match_smart_money_entity,
    track_daily_bulk_deals,
    evaluate_shareholding_pattern,
)
from app.services.research_data import ResearchDataStore


# ============================================================================
# 1. SECTOR WACC RESOLUTION TESTS
# ============================================================================

def test_resolve_sector_wacc_known_sectors():
    """Verify sector-calibrated discount rates map accurately to capital intensity."""
    assert resolve_sector_wacc("FMCG") == 0.105
    assert resolve_sector_wacc("Fast Moving Consumer Goods") == 0.105
    assert resolve_sector_wacc("Information Technology") == 0.115
    assert resolve_sector_wacc("IT Services", "Software") == 0.115
    assert resolve_sector_wacc("Pharmaceuticals") == 0.110
    assert resolve_sector_wacc("Banking & Financial Services") == 0.115
    assert resolve_sector_wacc("BFSI") == 0.115
    assert resolve_sector_wacc("Automotive") == 0.120
    assert resolve_sector_wacc("Capital Goods") == 0.125
    assert resolve_sector_wacc("Infrastructure") == 0.125
    assert resolve_sector_wacc("Real Estate") == 0.140
    assert resolve_sector_wacc("Realty") == 0.140


def test_resolve_sector_wacc_fallback_and_edge_cases():
    """Verify graceful fallback for unclassified sectors or empty inputs."""
    assert resolve_sector_wacc(None, None) == 0.120
    assert resolve_sector_wacc("", "") == 0.120
    assert resolve_sector_wacc("Space Exploration", "Asteroid Mining") == 0.120
    assert resolve_sector_wacc(None, "Telecommunications") == 0.130


def test_run_dcf_forward_with_sector_wacc_integration():
    """Verify Forward DCF dynamically applies sector WACC when discount_rate is unspecified."""
    mock_obs = [
        MagicMock(period_end="2023-06-30", metric="free_cash_flow", value=100.0),
        MagicMock(period_end="2023-09-30", metric="free_cash_flow", value=110.0),
        MagicMock(period_end="2023-12-31", metric="free_cash_flow", value=120.0),
        MagicMock(period_end="2024-03-31", metric="free_cash_flow", value=130.0),
        MagicMock(period_end="2023-06-30", metric="basic_eps", value=10.0),
        MagicMock(period_end="2023-09-30", metric="basic_eps", value=11.0),
        MagicMock(period_end="2023-12-31", metric="basic_eps", value=12.0),
        MagicMock(period_end="2024-03-31", metric="basic_eps", value=13.0),
    ]

    mock_quote = {
        "symbol": "TEST_CO",
        "price": 500.0,
        "pe_ratio": 22.0,
        "market_cap": 5000.0,
    }

    mock_company = MagicMock(sector="FMCG", industry="Packaged Foods")

    with patch.dict(os.environ, {"OFFLINE_TEST_MODE": "false"}):
        with patch("app.services.strategies.dcf_forward.get_quote", return_value=mock_quote):
            with patch("app.services.research_data.ResearchDataStore.get_timeline", return_value=(mock_company, mock_obs, [], [], [], [])):
                # 1. FMCG (Lower WACC: 10.5%) -> Higher intrinsic valuation
                fmcg_res = run_dcf_forward("TEST_CO", sector="FMCG")
                assert fmcg_res.metrics["discount_rate_wacc_pct"] == 10.5
                assert fmcg_res.metrics["sector_resolved"] == "FMCG"
                fmcg_val = fmcg_res.results["intrinsic_value_dcf"]
                assert fmcg_val is not None and fmcg_val > 0

                # 2. Real Estate (Higher WACC: 14.0%) -> Lower intrinsic valuation
                re_res = run_dcf_forward("TEST_CO", sector="Real Estate")
                assert re_res.metrics["discount_rate_wacc_pct"] == 14.0
                assert re_res.metrics["sector_resolved"] == "Real Estate"
                re_val = re_res.results["intrinsic_value_dcf"]
                assert re_val is not None and re_val > 0

                # Fundamental property: Higher discount rate -> lower discounted intrinsic value
                assert fmcg_val > re_val

                # 3. Explicit discount rate override takes precedence
                override_res = run_dcf_forward("TEST_CO", sector="FMCG", discount_rate=0.16)
                assert override_res.metrics["discount_rate_wacc_pct"] == 16.0
                assert override_res.results["intrinsic_value_dcf"] < fmcg_val


# ============================================================================
# 2. SMART MONEY ENTITY MATCHING TESTS
# ============================================================================

def test_match_smart_money_entity():
    """Verify regex matching for marquee Indian super-investors and institutions."""
    # Vijay Kedia
    assert match_smart_money_entity("VIJAY KISHANCHAND KEDIA") == "VIJAY_KEDIA"
    assert match_smart_money_entity("Kedia Securities Private Limited") == "VIJAY_KEDIA"

    # Ashish Kacholia
    assert match_smart_money_entity("ASHISH RAMESHCHANDRA KACHOLIA") == "ASHISH_KACHOLIA"
    assert match_smart_money_entity("Kacholia Ashish") == "ASHISH_KACHOLIA"

    # Mukul Agrawal (handles middle names)
    assert match_smart_money_entity("MUKUL MAHAVIR AGRAWAL") == "MUKUL_AGRAWAL"
    assert match_smart_money_entity("Mukul Agrawal") == "MUKUL_AGRAWAL"
    assert match_smart_money_entity("Mukul Agarwal") == "MUKUL_AGRAWAL"

    # Dolly Khanna
    assert match_smart_money_entity("DOLLY KHANNA") == "DOLLY_KHANNA"

    # Institutional Marquee
    assert match_smart_money_entity("LIFE INSURANCE CORPORATION OF INDIA") == "LIC_INDIA"
    assert match_smart_money_entity("SBI MUTUAL FUND TRUSTEE CO") == "SBI_MUTUAL_FUND"
    assert match_smart_money_entity("HDFC TRUSTEE COMPANY LIMITED") == "HDFC_MUTUAL_FUND"
    assert match_smart_money_entity("GOVERNMENT PENSION FUND GLOBAL - NORGES") == "NORGES_BANK"

    # Unknown / Retail entity
    assert match_smart_money_entity("RAMESHWAR PRASAD SHARMA") is None
    assert match_smart_money_entity("") is None
    assert match_smart_money_entity(None) is None


# ============================================================================
# 3. DAILY BULK & BLOCK DEALS TRACKING TESTS
# ============================================================================

def test_track_daily_bulk_deals_empty():
    """Verify behavior with no bulk deals."""
    res = track_daily_bulk_deals("INFY", [])
    assert res["total_deals_count"] == 0
    assert res["tracked_smart_money_count"] == 0
    assert res["net_smart_money_cr"] == 0.0
    assert res["activity_tier"] == "NEUTRAL_OR_UNTRACKED"
    assert len(res["smart_money_flows"]) == 0


def test_track_daily_bulk_deals_smart_money_accumulation():
    """Verify strong net accumulation detection from Mukul Agrawal and Kedia buys."""
    raw_deals = [
        {
            "deal_date": "2026-03-10",
            "client_name": "MUKUL MAHAVIR AGRAWAL",
            "deal_type": "BUY",
            "quantity": 100000,
            "trade_price": 600.0,  # 100k * 600 = 6 Cr
            "published_at": "2026-03-10T18:00:00Z",
        },
        {
            "deal_date": "2026-03-10",
            "client_name": "VIJAY KEDIA",
            "deal_type": "BUY",
            "quantity": 50000,
            "trade_price": 400.0,  # 50k * 400 = 2 Cr
            "published_at": "2026-03-10T18:05:00Z",
        },
        {
            "deal_date": "2026-03-10",
            "client_name": "UNKNOWN TRADER",
            "deal_type": "SELL",
            "quantity": 200000,
            "trade_price": 500.0,
            "published_at": "2026-03-10T18:10:00Z",
        },
    ]

    res = track_daily_bulk_deals("PATELENG", raw_deals)
    assert res["total_deals_count"] == 3
    assert res["tracked_smart_money_count"] == 2
    assert res["net_smart_money_cr"] == pytest.approx(8.0, 0.01)
    assert res["activity_tier"] == "STRONG_NET_ACCUMULATION"
    assert len(res["smart_money_flows"]) == 2
    assert res["smart_money_flows"][0]["smart_entity"] == "MUKUL_AGRAWAL"
    assert res["smart_money_flows"][0]["deal_type"] == "BUY"


def test_track_daily_bulk_deals_distribution():
    """Verify heavy distribution alert when smart money dumps holdings."""
    raw_deals = [
        {
            "deal_date": "2026-03-10",
            "client_name": "ASHISH RAMESHCHANDRA KACHOLIA",
            "deal_type": "SELL",
            "quantity": 200000,
            "trade_price": 300.0,  # 200k * 300 = 6 Cr sold
            "published_at": "2026-03-10T18:30:00Z",
        }
    ]
    res = track_daily_bulk_deals("SPEC_CHEM", raw_deals)
    assert res["tracked_smart_money_count"] == 1
    assert res["net_smart_money_cr"] == pytest.approx(-6.0, 0.01)
    assert res["activity_tier"] == "HEAVY_DISTRIBUTION"


def test_track_daily_bulk_deals_pit_filter():
    """Verify Point-in-Time as_of timestamp strictly filters subsequent bulk deals."""
    raw_deals = [
        {
            "deal_date": "2026-03-05",
            "client_name": "MUKUL MAHAVIR AGRAWAL",
            "deal_type": "BUY",
            "quantity": 100000,
            "trade_price": 500.0,  # 5 Cr
            "published_at": "2026-03-05T18:00:00Z",
        },
        {
            "deal_date": "2026-03-12",
            "client_name": "VIJAY KEDIA",
            "deal_type": "BUY",
            "quantity": 100000,
            "trade_price": 500.0,  # 5 Cr (FUTURE deal relative to as_of)
            "published_at": "2026-03-12T18:00:00Z",
        },
    ]

    # Evaluate as of 2026-03-10: only the first deal should be included
    res = track_daily_bulk_deals("AUTO_ANCILLARY", raw_deals, as_of="2026-03-10T00:00:00Z")
    assert res["total_deals_count"] == 1
    assert res["tracked_smart_money_count"] == 1
    assert res["net_smart_money_cr"] == pytest.approx(5.0, 0.01)


# ============================================================================
# 4. RESEARCH DATA STORE PIT PERSISTENCE TESTS
# ============================================================================

def test_research_data_store_bulk_deals(tmp_path):
    """Verify ResearchDataStore correctly stores and queries daily bulk deals with PIT support."""
    db_file = tmp_path / "test_research.db"
    store = ResearchDataStore(database_path=str(db_file))

    # Insert deals
    deal_1 = {
        "symbol": "RELIANCE",
        "deal_date": "2026-03-01",
        "client_name": "LIFE INSURANCE CORPORATION OF INDIA",
        "deal_type": "BUY",
        "quantity": 500000,
        "trade_price": 2800.0,
        "exchange": "NSE",
        "published_at": "2026-03-01T18:30:00Z",
    }
    deal_2 = {
        "symbol": "RELIANCE",
        "deal_date": "2026-03-10",
        "client_name": "FOREIGN PORTFOLIO INVESTOR",
        "deal_type": "SELL",
        "quantity": 300000,
        "trade_price": 2850.0,
        "exchange": "NSE",
        "published_at": "2026-03-10T18:30:00Z",
    }
    deal_3 = {
        "symbol": "TCS",
        "deal_date": "2026-03-05",
        "client_name": "MUKUL AGRAWAL",
        "deal_type": "BUY",
        "quantity": 50000,
        "trade_price": 3900.0,
        "exchange": "NSE",
        "published_at": "2026-03-05T18:00:00Z",
    }

    store.add_bulk_deal(deal_1)
    store.add_bulk_deal(deal_2)
    store.add_bulk_deal(deal_3)

    # 1. Query all for RELIANCE
    all_reliance = store.get_bulk_deals("RELIANCE")
    assert len(all_reliance) == 2

    # 2. Query PIT for RELIANCE before deal 2
    pit_reliance = store.get_bulk_deals("RELIANCE", as_of="2026-03-05T00:00:00Z")
    assert len(pit_reliance) == 1
    assert pit_reliance[0]["client_name"] == "LIFE INSURANCE CORPORATION OF INDIA"

    # 3. Query TCS
    tcs_deals = store.get_bulk_deals("TCS")
    assert len(tcs_deals) == 1
    assert tcs_deals[0]["client_name"] == "MUKUL AGRAWAL"


# ============================================================================
# 5. SHAREHOLDING PATTERN STRATEGY INTEGRATION TEST
# ============================================================================

def test_evaluate_shareholding_pattern_with_bulk_deals():
    """Verify evaluate_shareholding_pattern produces daily bulk deal summary and evidence."""
    snapshot = {
        "promoter_holding": 52.0,
        "promoter_holding_prev_qtr": 51.0,
        "pledged_promoter_holding": 0.0,
        "fii_holding": 18.0,
        "fii_holding_prev_qtr": 17.5,
        "dii_holding": 12.0,
        "dii_holding_prev_qtr": 11.0,
        "public_holding": 18.0,
        "daily_bulk_deals": [
            {
                "deal_date": "2026-03-10",
                "client_name": "KEDIA SECURITIES PRIVATE LIMITED",
                "deal_type": "BUY",
                "quantity": 100000,
                "trade_price": 550.0,
                "published_at": "2026-03-10T18:00:00Z",
            }
        ]
    }

    eval_res = evaluate_shareholding_pattern("PRECISION_ENG", snapshot)
    assert "daily_bulk_deals" in eval_res
    daily = eval_res["daily_bulk_deals"]
    assert daily["tracked_smart_money_count"] == 1
    assert daily["net_smart_money_cr"] == pytest.approx(5.5, 0.01)
    assert daily["activity_tier"] == "STRONG_NET_ACCUMULATION"

    # Verify evidence item is attached
    evidence = eval_res.get("evidence", [])
    assert any("Daily Bulk Deals (T+0): Net Smart Money Flow" in e for e in evidence)
