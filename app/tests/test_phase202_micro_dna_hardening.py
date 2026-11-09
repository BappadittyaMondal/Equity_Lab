# -*- coding: utf-8 -*-
"""Phase 202 Test Suite: Micro-Level Mathematical & Architectural Hardening Tests."""
import pytest
from app.services.research.intent_adaptive_engine import (
    QueryAdaptiveConstraintEngine,
    ARCHETYPE_WEIGHT_PROFILES,
)


def test_phase202_working_capital_narrative_sieve_multibagger():
    """Verify that Multibagger blocks narrative revenue expansion when receivables blow out."""
    divergent_data = {
        "market_cap": 3000.0,
        "roce_latest": 25.0,
        "incremental_roic": 26.0,
        "promoter_holding": 65.0,
        "pledged_pct": 0.0,
        "delta_dso": 45.0,  # +45 days expansion in receivables
        "cfo_pat_ratio": 0.30,  # Weak cash conversion
    }
    result = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("MULTIBAGGER", divergent_data)
    assert any("Narrative vs Cash-Flow divergence" in v for v in result["vetoes"]), (
        f"Expected narrative divergence veto, got: {result['vetoes']}"
    )


def test_phase202_working_capital_narrative_sieve_deadliest_combo():
    """Verify that Deadliest Combo vetoes uncollected receivables expansion."""
    divergent_data = {
        "market_cap": 2500.0,
        "debt_to_equity": 0.20,
        "pledged_pct": 0.0,
        "roce_latest": 22.0,
        "cfo": 10.0,
        "cfo_pat_ratio": 0.35,
        "delta_dso": 40.0,  # DSO expanded by 40 days
        "circuit_headroom": 5.0,
        "operating_leverage_convexity": 1.25,
        "weinstein_stage": "STAGE_2_EARLY",
    }
    result = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("DEADLIEST_COMBO", divergent_data)
    assert any("Narrative vs Cash-Flow divergence" in v for v in result["vetoes"]), (
        f"Expected Deadliest Combo narrative divergence veto, got: {result['vetoes']}"
    )


def test_phase202_healthy_compounder_passes():
    """Verify that a pristine company with clean DSO and high CFO/PAT passes."""
    healthy_data = {
        "market_cap": 4500.0,
        "debt_to_equity": 0.15,
        "pledged_pct": 0.0,
        "roce_latest": 28.0,
        "cfo": 120.0,
        "cfo_pat_ratio": 0.95,
        "delta_dso": -5.0,  # Receivables improved
        "dso": 65.0,
        "circuit_headroom": 6.0,
        "operating_leverage_convexity": 1.40,
        "weinstein_stage": "STAGE_2_UPTREND",
    }
    result = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("DEADLIEST_COMBO", healthy_data)
    assert len(result["objective_blocks"]) == 0, f"Unexpected blocks: {result['objective_blocks']}"
    assert any("Positive cash conversion verified" in t for t in result["tightened_parameters"])


def test_phase202_natural_currency_hedge_exporter():
    """Verify that exporters with >= 40% export revenue get natural currency hedge recognition."""
    exporter_data = {
        "market_cap": 3500.0,
        "debt_to_equity": 0.25,
        "pledged_pct": 0.0,
        "roce_latest": 24.0,
        "cfo": 80.0,
        "cfo_pat_ratio": 0.88,
        "export_revenue_pct": 65.0,  # High export revenue
        "operating_leverage_convexity": 1.30,
        "circuit_headroom": 5.0,
    }
    result = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("DEADLIEST_COMBO", exporter_data)
    assert any("Foreign currency debt naturally hedged" in r for r in result["relaxed_parameters"]), (
        f"Expected natural hedge relaxation, got: {result['relaxed_parameters']}"
    )


def test_phase202_outlier_resistant_ep_volume_gate():
    """Verify that EP volume ignition gate correctly recognizes institutional volume vs illiquid churn."""
    # Case A: High RVOL with safe ADTV
    inst_vol_data = {
        "rvol_50": 3.8,
        "adtv_cr": 8.5,
        "circuit_headroom": 5.0,
    }
    result_inst = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("PRE_FLY", inst_vol_data)
    assert any("Institutional volume ignition verified" in t for t in result_inst["tightened_parameters"])

    # Case B: High RVOL on micro-liquidity
    illiquid_vol_data = {
        "rvol_50": 4.5,
        "adtv_cr": 0.35,  # Only Rs 35 Lakhs turnover
        "circuit_headroom": 5.0,
    }
    result_illiquid = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("PRE_FLY", illiquid_vol_data)
    assert any("micro-turnover" in w for w in result_illiquid["warnings"])
