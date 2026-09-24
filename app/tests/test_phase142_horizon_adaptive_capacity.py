"""Tests for Phase 142: Horizon-Adaptive Evidence Matrix & Capacity Sizing Engine."""

import pytest
from app.services.decision_brain.horizon_adaptive_engine import HorizonAdaptiveEngine


def test_capacity_limits_calculation():
    # 1. High liquidity scrip (ADTV ₹15 Cr)
    c1 = HorizonAdaptiveEngine.compute_capacity_limits(adtv_cr=15.0)
    assert c1["adtv_cr"] == 15.0
    assert c1["max_institutional_position_cr"] == 1.50
    assert c1["max_retail_order_cr"] == 0.30
    assert c1["capacity_status"] == "HIGH_LIQUIDITY"
    assert c1["is_liquid_enough"] is True

    # 2. Micro-cap liquidity constrained (ADTV ₹0.80 Cr)
    c2 = HorizonAdaptiveEngine.compute_capacity_limits(adtv_cr=0.80)
    assert c2["adtv_cr"] == 0.80
    assert c2["max_institutional_position_cr"] == 0.08
    assert c2["max_retail_order_cr"] == 0.02
    assert c2["capacity_status"] == "MICRO_LIQUIDITY_CONSTRAINED"
    assert c2["is_liquid_enough"] is True

    # 3. Illiquid hazard (ADTV ₹0.20 Cr)
    c3 = HorizonAdaptiveEngine.compute_capacity_limits(adtv_cr=0.20)
    assert c3["capacity_status"] == "ILLIQUID_HAZARD"
    assert c3["is_liquid_enough"] is False

    # 4. Derivation from volume and price
    c4 = HorizonAdaptiveEngine.compute_capacity_limits(volume=200000.0, price=250.0)
    # 200,000 * 250 = 50,000,000 INR = ₹5.0 Cr
    assert c4["adtv_cr"] == 5.0
    assert c4["max_institutional_position_cr"] == 0.50
    assert c4["max_retail_order_cr"] == 0.10


def test_horizon_tactical_swing_3d_pass():
    data = {
        "adtv_cr": 8.0,
        "volume_z_score": 2.5,
        "rvol": 2.1,
        "close_position": 0.88,
        "circuit_band_pct": 20.0,
        "asm_stage": "CLEAN",
        "esm_stage": "CLEAN"
    }
    res = HorizonAdaptiveEngine.evaluate_horizon_evidence("SWING_STOCK", "SWING_3D", data)
    assert res["target_horizon"] == "TACTICAL_SWING_3D"
    assert res["is_approved"] is True
    assert res["status"] == "APPROVED"
    assert res["evidence_score"] >= 80.0
    assert len(res["breached_gates"]) == 0
    assert len(res["relaxed_parameters"]) >= 3


def test_horizon_tactical_swing_3d_illiquidity_breach():
    data = {
        "adtv_cr": 1.2,  # Below 2.0 Cr floor for 3-day swing
        "volume_z_score": 2.5,
        "rvol": 2.1,
        "close_position": 0.88,
        "circuit_band_pct": 20.0,
        "asm_stage": "CLEAN",
        "esm_stage": "CLEAN"
    }
    res = HorizonAdaptiveEngine.evaluate_horizon_evidence("SWING_STOCK_2", "SWING_3D", data)
    assert res["is_approved"] is False
    assert res["status"] == "REJECTED_EVIDENCE_BREACH"
    assert any("ADTV" in b for b in res["breached_gates"])


def test_horizon_esm_stage_ii_fatal_veto():
    data = {
        "adtv_cr": 5.0,
        "volume_z_score": 2.5,
        "rvol": 2.1,
        "close_position": 0.88,
        "circuit_band_pct": 2.0,
        "asm_stage": "CLEAN",
        "esm_stage": "STAGE_II"
    }
    res = HorizonAdaptiveEngine.evaluate_horizon_evidence("ESM_LOCKED", "SWING_3D", data)
    assert res["is_approved"] is False
    assert res["has_surveillance_veto"] is True
    assert res["status"] == "VETOED_SURVEILLANCE"
    assert any("ESM Stage II" in b for b in res["breached_gates"])


def test_horizon_turnaround_pass():
    data = {
        "adtv_cr": 2.5,
        "sales_growth_3yr": -15.0,  # Negative historical growth relaxed!
        "pat_growth_3yr": -30.0,
        "cfo_last_year": 25.0,       # Sequential positive CFO
        "interest_coverage": 2.2,    # Debt coverage safe
        "opm_inflection": True,
        "circuit_band_pct": 20.0,
        "asm_stage": "CLEAN",
        "esm_stage": "CLEAN"
    }
    res = HorizonAdaptiveEngine.evaluate_horizon_evidence("TURN_STOCK", "TURNAROUND", data)
    assert res["target_horizon"] == "TURNAROUND_1_3Y"
    assert res["is_approved"] is True
    assert res["status"] == "APPROVED"
    assert res["evidence_score"] >= 90.0
    assert any("relaxed" in p.lower() for p in res["relaxed_parameters"])


def test_horizon_quality_compounder_pass():
    data = {
        "adtv_cr": 25.0,
        "roce_10y_avg": 22.5,
        "debt_to_equity": 0.15,
        "pledged_pct": 0.0,
        "circuit_band_pct": 20.0,
        "asm_stage": "CLEAN",
        "esm_stage": "CLEAN"
    }
    res = HorizonAdaptiveEngine.evaluate_horizon_evidence("COMPOUND_STOCK", "SIP_COMPOUNDER", data)
    assert res["target_horizon"] == "QUALITY_COMPOUNDER_5_10Y"
    assert res["is_approved"] is True
    assert res["status"] == "APPROVED"
    assert res["evidence_score"] == 100.0


def test_horizon_launchpad_multibagger_pass():
    data = {
        "market_cap": 300.0,
        "ob_to_mcap_ratio": 2.4,
        "has_jaw_effect_setup": True,
        "promoter_holding": 64.0,
        "adtv_cr": 1.5,
        "circuit_band_pct": 20.0,
        "asm_stage": "CLEAN",
        "esm_stage": "CLEAN"
    }
    res = HorizonAdaptiveEngine.evaluate_horizon_evidence("LAUNCH_STOCK", "MULTIBAGGER", data)
    assert res["target_horizon"] == "PRE_DISCOVERY_LAUNCHPAD"
    assert res["is_approved"] is True
    assert res["status"] == "APPROVED"
    assert res["evidence_score"] == 100.0
    assert res["capacity_limits"]["max_institutional_position_cr"] == 0.15
    assert res["capacity_limits"]["max_retail_order_cr"] == 0.03
