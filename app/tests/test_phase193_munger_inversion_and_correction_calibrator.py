"""Phase 193 Test Suite: Charlie Munger Inversion-First Sentinel,
Abhishek Kar 41/45 Annual Correction Calibrator, and IT Headcount Disruption Guard.
"""

import json
import os
import pytest
from app.services.research.institutional_multibagger_engine import (
    InstitutionalMultibaggerEngine,
    MungerInversionSentinel,
)
from app.services.research.finder_state_machines import SIPPolicyEngine
from app.services.research.cagr_matrix_service import generate_cagr_sensitivity_matrix


def test_munger_inversion_pristine_pass():
    """Verify clean compounder passes Munger inversion with 100 score."""
    item = {
        "symbol": "PRISTINE_CO",
        "debt_to_equity": 0.10,
        "market_cap_cr": 4500.0,
        "cfo_last_year": 120.0,
        "net_profit_last_year": 100.0,
        "ccc_delta_yoy": -5.0,
        "beneish_m_score": -2.85,
        "pledged_pct": 0.0,
        "roce_latest": 26.5,
        "sector": "SPECIALTY_CHEMICALS",
    }
    res = MungerInversionSentinel.evaluate_inversion(item)
    assert res["inversion_passed"] is True
    assert res["inversion_status"] == "PRISTINE_INVERSION_PASS"
    assert res["inversion_score"] == 100.0
    assert len(res["fatal_killers_triggered"]) == 0


def test_munger_inversion_excessive_leverage_and_suffocation():
    """Verify heavily indebted and overtrading company is disqualified."""
    item = {
        "symbol": "TRAP_CO",
        "debt_to_equity": 1.45,
        "market_cap_cr": 1200.0,
        "cfo_last_year": -45.0,
        "net_profit_last_year": 35.0,
        "ccc_delta_yoy": 38.0,  # CCC elongated +38d with negative CFO (Lamba Overtrading Trap)
        "beneish_m_score": -1.50,  # Fraud red flag
        "pledged_pct": 22.0,
        "roce_latest": 8.0,
    }
    res = InstitutionalMultibaggerEngine.evaluate_munger_inversion(item)
    assert res["inversion_passed"] is False
    assert res["inversion_status"] == "FATAL_INVERSION_DISQUALIFICATION"
    assert res["killer_count"] >= 3
    assert any("EXCESSIVE_FINANCIAL_LEVERAGE" in k for k in res["fatal_killers_triggered"])
    assert any("WORKING_CAPITAL_SUFFOCATION" in k for k in res["fatal_killers_triggered"])
    assert any("FORENSIC_MANIPULATION" in k for k in res["fatal_killers_triggered"])


def test_munger_inversion_turnaround_context_exemption():
    """Verify depressed ROCE does not trigger fatal disqualification under Turnaround objective."""
    item = {
        "symbol": "TURNAROUND_CO",
        "debt_to_equity": 0.25,
        "market_cap_cr": 5000.0,
        "cfo_last_year": 50.0,
        "net_profit_last_year": 10.0,
        "ccc_delta_yoy": 0.0,
        "beneish_m_score": -2.60,
        "pledged_pct": 0.0,
        "roce_latest": 6.5,  # Depressed past ROCE
        "sector": "AUTO_COMPONENTS",
    }
    res = MungerInversionSentinel.evaluate_inversion(item, objective="TURNAROUND")
    assert res["inversion_passed"] is True
    assert res["inversion_status"] == "CONDITIONAL_INVERSION_WARNING"
    assert any("TURNAROUND_DEPRESSED_ROCE" in w for w in res["warnings"])
    assert not any("NEGATIVE_CAPITAL_SPREAD" in k for k in res["fatal_killers_triggered"])


def test_munger_inversion_sovereign_regulatory_cap():
    """Verify sovereign price control triggers warning and score haircut."""
    item = {
        "symbol": "FERT_CO",
        "debt_to_equity": 0.20,
        "market_cap_cr": 3500.0,
        "cfo_last_year": 80.0,
        "net_profit_last_year": 70.0,
        "roce_latest": 18.0,
        "sector": "FERTILIZERS",
    }
    res = MungerInversionSentinel.evaluate_inversion(item)
    assert any("SOVEREIGN_REGULATORY_CAP" in w for w in res["warnings"])
    assert res["inversion_score"] <= 85.0


def test_sip_41_45_annual_correction_boost():
    """Verify Abhishek Kar 41/45 annual correction boosts SIP allocation to 1.5x."""
    res = SIPPolicyEngine.evaluate(
        "TCS",
        roce_10y_avg=32.0,
        debt_to_equity=0.05,
        valuation_z_score=0.2,  # Fair valuation
        drawdown_from_52w_high=12.5,  # 12.5% drawdown from peak
    )
    assert res["is_41_45_annual_correction_opportunity"] is True
    assert res["allocation_multiplier"] == 1.50
    assert res["policy_action"] == "EXPANDED_SIP_ANNUAL_CORRECTION_ACCUMULATION"
    assert "abhishek_kar_correction_axiom" in res


def test_sip_41_45_historical_panic_boost_2x():
    """Verify deep drawdown (>= 15%) below 200 SMA boosts SIP allocation to 2.0x."""
    res = SIPPolicyEngine.evaluate(
        "INFY",
        roce_10y_avg=28.0,
        debt_to_equity=0.08,
        valuation_z_score=-1.2,
        is_price_below_200sma=True,
        drawdown_from_52w_high=18.0,  # 18% drawdown from peak
    )
    assert res["is_41_45_annual_correction_opportunity"] is True
    assert res["allocation_multiplier"] == 2.00
    assert res["policy_action"] == "EXPANDED_SIP_HISTORICAL_PANIC_DEPLOYMENT"


def test_cagr_matrix_it_linear_headcount_pe_cap(monkeypatch):
    """Verify linear IT services terminal P/E is capped at 25.0 to protect against multiple compression."""
    monkeypatch.setenv("OFFLINE_TEST_MODE", "true")
    res = generate_cagr_sensitivity_matrix("WIPRO", sector="IT_SERVICES")
    assert "WIPRO" in res.symbol
    res_tech = generate_cagr_sensitivity_matrix("WIPRO", sector="TECH")
    # For high growth scenarios (e.g. 30%), IT_SERVICES terminal P/E is capped at 25.0
    # whereas general TECH allows expansion up to 50.0, resulting in lower target price
    assert res.scenario_matrix[-1].target_price_5y < res_tech.scenario_matrix[-1].target_price_5y


def test_dynamic_knowledge_entities_phase193():
    """Verify Entities #56 and #57 are certified in learned_rules_registry.json."""
    registry_path = os.path.join("data", "dynamic_knowledge", "learned_rules_registry.json")
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    entities = registry.get("entities", {})
    assert "MUNGER_INVERSION_FIRST_SENTINEL_RULE" in entities
    assert "ABHISHEK_KAR_41_45_CORRECTION_CALIBRATOR_RULE" in entities

    munger_rule = entities["MUNGER_INVERSION_FIRST_SENTINEL_RULE"]
    assert munger_rule["verification_status"] == "CERTIFIED_FACT"
    assert munger_rule["confidence_score"] == 0.99

    kar_rule = entities["ABHISHEK_KAR_41_45_CORRECTION_CALIBRATOR_RULE"]
    assert kar_rule["verification_status"] == "CERTIFIED_FACT"
    assert kar_rule["confidence_score"] == 0.98

    assert registry.get("total_entities_count") >= 57
