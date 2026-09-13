# -*- coding: utf-8 -*-
"""Institutional tests for Centralized Security Master and Brier Score Calibration."""

import pytest
import sqlite3
from datetime import datetime, timezone
from app.services.research.security_master import SecurityMaster, SecurityRecord
from app.services.market_data import normalize_symbol
from app.services.monitoring.outcome_checker import compute_brier_calibration_score
from app.core.config import settings


def test_security_master_alias_resolution():
    """Verify alias mapping and provider ticker resolution for turnaround and microcap scrips."""
    # Apollo Micro Systems aliases
    assert normalize_symbol("APOLLOMICR") == "APOLLO.NS"
    assert normalize_symbol("APOLLOMICRO") == "APOLLO.NS"
    assert normalize_symbol("APOLLO MICRO") == "APOLLO.NS"
    assert normalize_symbol("NSE:APOLLO") == "APOLLO.NS"
    assert normalize_symbol("BSE:540879") == "540879.BO"

    # Data Patterns aliases
    assert normalize_symbol("DATAPATTERN") == "DATAPATTNS.NS"
    assert normalize_symbol("DATAPATTERNS") == "DATAPATTNS.NS"
    assert normalize_symbol("DATA PATTERNS") == "DATAPATTNS.NS"

    # Shilchar Tech aliases
    assert normalize_symbol("SHILCHAR") == "SHILCHAR.NS"
    assert normalize_symbol("SHILCHARTECH") == "SHILCHAR.NS"
    assert normalize_symbol("SHILCHAR TECHNOLOGIES") == "SHILCHAR.NS"
    assert SecurityMaster.get_provider_ticker("SHILCHAR", "yfinance") == "SHILCTECH.NS"

    # Other peer test scrips
    assert normalize_symbol("AXIS CADES") == "AXISCADES.NS"
    assert normalize_symbol("MOSCHIP TECH") == "MOSCHIP.NS"
    assert normalize_symbol("IZMO LTD") == "IZMO.NS"
    assert normalize_symbol("TEJAS NETWORKS") == "TEJASNET.NS"


def test_security_master_record_and_providers():
    """Verify metadata extraction and provider-specific ticker formatting."""
    rec = SecurityMaster.resolve_record("APOLLOMICR")
    assert rec is not None
    assert rec.canonical_symbol == "APOLLO"
    assert rec.company_name == "Apollo Micro Systems Ltd"
    assert rec.isin == "INE713T01028"
    assert rec.bse_code == "540879"
    assert rec.nse_symbol == "APOLLO"

    # Test provider tickers
    assert SecurityMaster.get_provider_ticker("APOLLOMICR", "yfinance") == "APOLLO.NS"
    assert SecurityMaster.get_provider_ticker("APOLLOMICR", "nse") == "APOLLO"
    assert SecurityMaster.get_provider_ticker("APOLLOMICR", "bse") == "540879"


def test_security_master_unregistered_fallback():
    """Verify unregistered tickers fallback gracefully without exceptions."""
    assert normalize_symbol("NONEXISTENT_XYZ") == "NONEXISTENT_XYZ.NS"
    assert normalize_symbol("CUSTOM_SCRIP.BO") == "CUSTOM_SCRIP.BO"
    assert normalize_symbol("^CUSTOM_INDEX") == "^CUSTOM_INDEX"


def test_brier_score_empty_ledger():
    """Verify Brier score handles empty or unobserved outcome cohorts gracefully."""
    result = compute_brier_calibration_score(symbol="NONEXISTENT_TEST_TICKER")
    assert result["matured_samples"] == 0
    assert result["brier_score"] is None
    assert result["hit_rate_pct"] is None
    assert result["calibration_status"] == "INSUFFICIENT_MATURED_OUTCOMES"


def test_brier_score_synthetic_calculation(tmp_path, monkeypatch):
    """Verify exact mathematical calculation of Brier Score and Hit Rate against ground-truth outcomes."""
    db_file = tmp_path / "test_calibration.db"
    conn = sqlite3.connect(str(db_file))
    conn.execute(
        """CREATE TABLE prediction_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            score REAL,
            verdict TEXT,
            model_version TEXT,
            predicted_at TEXT
        )"""
    )
    conn.execute(
        """CREATE TABLE outcome_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER,
            symbol TEXT,
            horizon_months INTEGER,
            actual_return_pct REAL,
            benchmark_return_pct REAL,
            excess_return_pct REAL,
            outcome_class TEXT,
            recorded_at TEXT
        )"""
    )

    # Insert 3 deterministic sample rows:
    # 1) prob = 0.80, actual = +10% (outcome = 1.0) -> (0.80 - 1.0)^2 = 0.04
    # 2) prob = 0.60, actual = -5% (outcome = 0.0)  -> (0.60 - 0.0)^2 = 0.36
    # 3) prob = 0.70, actual = +15% (outcome = 1.0) -> (0.70 - 1.0)^2 = 0.09
    # Mean Squared Error (Brier) = (0.04 + 0.36 + 0.09) / 3 = 0.49 / 3 = 0.1633
    # Hit Rate = 2 / 3 = 66.7%
    conn.execute("INSERT INTO prediction_ledger (id, symbol, score, verdict, model_version, predicted_at) VALUES (1, 'TEST.NS', 80.0, 'STRONG_BUY', 'v1.0', '2025-01-01')")
    conn.execute("INSERT INTO prediction_ledger (id, symbol, score, verdict, model_version, predicted_at) VALUES (2, 'TEST.NS', 60.0, 'BUY', 'v1.0', '2025-01-01')")
    conn.execute("INSERT INTO prediction_ledger (id, symbol, score, verdict, model_version, predicted_at) VALUES (3, 'TEST.NS', 70.0, 'BUY', 'v1.0', '2025-01-01')")

    conn.execute("INSERT INTO outcome_ledger (prediction_id, symbol, horizon_months, actual_return_pct, benchmark_return_pct, excess_return_pct, outcome_class, recorded_at) VALUES (1, 'TEST.NS', 6, 10.0, 5.0, 5.0, 'OUTPERFORM', '2025-07-01')")
    conn.execute("INSERT INTO outcome_ledger (prediction_id, symbol, horizon_months, actual_return_pct, benchmark_return_pct, excess_return_pct, outcome_class, recorded_at) VALUES (2, 'TEST.NS', 6, -5.0, 2.0, -7.0, 'UNDERPERFORM', '2025-07-01')")
    conn.execute("INSERT INTO outcome_ledger (prediction_id, symbol, horizon_months, actual_return_pct, benchmark_return_pct, excess_return_pct, outcome_class, recorded_at) VALUES (3, 'TEST.NS', 6, 15.0, 4.0, 11.0, 'OUTPERFORM', '2025-07-01')")
    conn.commit()
    conn.close()

    monkeypatch.setattr("app.services.monitoring.outcome_checker.get_connection", lambda: sqlite3.connect(str(db_file)))

    stats = compute_brier_calibration_score("TEST.NS")
    assert stats["matured_samples"] == 3
    assert stats["brier_score"] == 0.1633
    assert stats["hit_rate_pct"] == 66.7
    assert stats["calibration_status"] == "EARLY_CALIBRATION_COHORT"


def test_delisted_equities_registry_and_point_in_time():
    """Verify that known historical insolvent/delisted securities are detected and PIT validated."""
    # Test delisted detection
    dhfl_info = SecurityMaster.is_security_delisted("DHFL")
    assert dhfl_info is not None
    assert dhfl_info["delisted_date"] == "2021-06-14"
    assert dhfl_info["final_status"] == "LIQUIDATED_TOTAL_LOSS"

    rcom_info = SecurityMaster.is_security_delisted("RCOM.NS")
    assert rcom_info is not None
    assert rcom_info["sector"] == "Telecom"

    # Test active stock returns None
    assert SecurityMaster.is_security_delisted("RELIANCE") is None
    assert SecurityMaster.is_security_delisted("TCS") is None

    # Test Point-in-Time activity
    # DHFL was active in 2020, but delisted by late 2021
    assert SecurityMaster.is_security_active_as_of("DHFL", "2020-01-01") is True
    assert SecurityMaster.is_security_active_as_of("DHFL", "2022-01-01") is False


def test_survivorship_bias_penalty_computation():
    """Verify institutional survivorship bias alpha haircut modeling."""
    # 5-Year All-Cap backtest
    res = SecurityMaster.calculate_survivorship_bias_penalty(backtest_years=5.0, universe_tier="ALL_CAP")
    assert res["annual_failure_rate_pct"] == 1.8
    assert res["cumulative_survivorship_drag_pct"] > 8.0  # ~8.68%
    assert res["annual_cagr_haircut_pct"] == 1.8
    assert "fiduciary_guidance" in res

    # 3-Year Small/Micro Cap backtest
    res_micro = SecurityMaster.calculate_survivorship_bias_penalty(backtest_years=3.0, universe_tier="SMALL_MICRO_CAP")
    assert res_micro["annual_failure_rate_pct"] == 2.8
    assert res_micro["cumulative_survivorship_drag_pct"] > 8.0  # 1 - 0.972^3 = ~8.16%

