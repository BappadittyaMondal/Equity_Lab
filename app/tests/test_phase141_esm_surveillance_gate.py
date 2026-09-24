"""Tests for Phase 141: SEBI Enhanced Surveillance Measure (ESM) Gate & Capacity Protection."""

import pytest
from app.models.schemas import SurveillanceRiskGate
from app.services.risk.surveillance_gate import evaluate_surveillance_and_cost_gate, is_surveillance_cleared
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine


def test_esm_stage_schema_default():
    gate = SurveillanceRiskGate()
    assert gate.esm_stage == "CLEAN"
    assert gate.is_cleared_for_trading is True


def test_esm_stage_ii_hard_gate_fail():
    data = {
        "asm_stage": "CLEAN",
        "gsm_stage": "CLEAN",
        "esm_stage": "STAGE_II",
        "circuit_band_pct": 2.0
    }
    gate = evaluate_surveillance_and_cost_gate("MICRO_TEST", surveillance_data=data)
    assert gate.hard_gate_status == "FAIL"
    assert gate.circuit_lock_risk == "CRITICAL_CALL_AUCTION"
    assert gate.slippage_ceiling_pct == 2.0
    assert gate.is_cleared_for_trading is False
    assert is_surveillance_cleared(gate) is False


def test_esm_stage_i_hard_gate_amber():
    data = {
        "asm_stage": "CLEAN",
        "gsm_stage": "CLEAN",
        "esm_stage": "STAGE_I",
        "circuit_band_pct": 5.0
    }
    gate = evaluate_surveillance_and_cost_gate("MICRO_TEST_1", surveillance_data=data)
    assert gate.hard_gate_status == "FAIL" or gate.circuit_lock_risk in ("HIGH", "CRITICAL_CALL_AUCTION")
    assert gate.esm_stage == "STAGE_I"


def test_esm_stage_i_amber_with_wide_band():
    data = {
        "asm_stage": "CLEAN",
        "gsm_stage": "CLEAN",
        "esm_stage": "STAGE_I",
        "circuit_band_pct": 10.0
    }
    gate = evaluate_surveillance_and_cost_gate("MICRO_TEST_1B", surveillance_data=data)
    assert gate.hard_gate_status == "AMBER"
    assert gate.circuit_lock_risk == "MODERATE"
    assert gate.is_cleared_for_trading is True


def test_launchpad_readiness_esm_lock_override():
    # Candidate with perfect fundamentals but trapped in ESM Stage II
    item = {
        "symbol": "TRAPPED_MICRO",
        "market_cap": 250.0,
        "order_book_cr": 750.0,
        "promoter_holding": 62.0,
        "pledged_pct": 0.0,
        "recent_equity_dilution": False,
        "piotroski_score": 8.0,
        "cfo_last_year": 20.0,
        "opm_latest": 10.0,
        "opm_5yr": 8.0,
        "data_completeness_pct": 100.0,
        "revenue_cr": 100.0,
        "net_profit_last_year": 8.0,
        "export_revenue_pct": 25.0,
        "export_revenue_pct_prev_year": 5.0,
        "esm_stage": "STAGE_II",
        "circuit_band_pct": 2.0,
        "adtv_cr": 0.80
    }
    res = InstitutionalMultibaggerEngine.evaluate_launchpad_readiness_score(item)
    assert res["launchpad_readiness_score"] >= 70.0
    assert res["has_esm_circuit_lock"] is True
    assert res["conviction_tier"] == "SPECULATIVE_MONITORING_ESM_LOCKED"
    assert "FATAL SURVEILLANCE OVERLAY" in res["conviction_tier_note"]
    assert res["capacity_guard"]["adtv_cr"] == 0.80
    assert res["capacity_guard"]["max_institutional_position_cr"] == 0.08
    assert res["capacity_guard"]["max_retail_order_cr"] == 0.02


def test_launchpad_readiness_clean_candidate():
    item = {
        "symbol": "CLEAN_MICRO",
        "market_cap": 250.0,
        "order_book_cr": 750.0,
        "promoter_holding": 62.0,
        "pledged_pct": 0.0,
        "recent_equity_dilution": False,
        "piotroski_score": 8.0,
        "cfo_last_year": 20.0,
        "opm_latest": 10.0,
        "opm_5yr": 8.0,
        "data_completeness_pct": 100.0,
        "revenue_cr": 100.0,
        "net_profit_last_year": 8.0,
        "export_revenue_pct": 25.0,
        "export_revenue_pct_prev_year": 5.0,
        "esm_stage": "CLEAN",
        "circuit_band_pct": 20.0,
        "adtv_cr": 3.50
    }
    res = InstitutionalMultibaggerEngine.evaluate_launchpad_readiness_score(item)
    assert res["launchpad_readiness_score"] >= 70.0
    assert res["has_esm_circuit_lock"] is False
    assert res["conviction_tier"] == "HIGH_CONVICTION_LAUNCHPAD"
    assert res["capacity_guard"]["max_institutional_position_cr"] == 0.35
    assert res["capacity_guard"]["max_retail_order_cr"] == 0.07
    assert res["capacity_guard"]["liquidity_status"] == "LIQUID"
