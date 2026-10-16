"""Unit tests for Phase 173: Institutional Hard Gates, Tenure Normalization, and Self-Learning Engine."""

import pytest
from app.services.research.deadliest_combo_pipeline import (
    _check_hard_gates,
    _calculate_annualized_book_to_bill,
)
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
from app.services.research.self_learning_engine import SelfLearningEngine


def test_phase173_hard_gate_roce_rejection():
    """Verify that stocks with ROCE < 20.0% are disqualified by the hard gate."""
    # Texmaco Rail ground truth: ROCE ~11.5%
    texmaco_fund = {
        "market_cap": 4650.0,
        "debt_to_equity": 0.35,
        "pledged_pct": 0.0,
        "roce_latest": 11.5,
        "pe_ratio": 21.0,
        "pat_growth_latest": 35.0,
    }
    reason = _check_hard_gates(texmaco_fund)
    assert reason is not None
    assert "ROCE 11.5% < 20.0% institutional floor" in reason

    # KPI Green ground truth: ROCE ~13.7%
    kpi_fund = {
        "market_cap": 6450.0,
        "debt_to_equity": 0.35,
        "pledged_pct": 0.0,
        "roce_latest": 13.7,
        "pe_ratio": 14.1,
        "pat_growth_latest": 62.0,
    }
    reason = _check_hard_gates(kpi_fund)
    assert reason is not None
    assert "ROCE 13.7% < 20.0% institutional floor" in reason


def test_phase173_hard_gate_multiple_compression_rejection():
    """Verify that stocks with P/E > 80.0 are disqualified from core compounders."""
    # PTC Industries ground truth: P/E ~304.4x
    ptcil_fund = {
        "market_cap": 40395.0,
        "debt_to_equity": 0.28,
        "pledged_pct": 0.0,
        "roce_latest": 20.4,
        "pe_ratio": 304.4,
        "pat_growth_latest": 44.0,
    }
    # MCap in Cr > 15,000 Cr, but let's test within MCap band to verify P/E gate specifically
    ptcil_mid = {
        "market_cap": 12000.0,
        "debt_to_equity": 0.28,
        "pledged_pct": 0.0,
        "roce_latest": 20.4,
        "pe_ratio": 304.4,
        "pat_growth_latest": 44.0,
    }
    reason = _check_hard_gates(ptcil_mid)
    assert reason is not None
    assert "P/E 304.4 > 80.0 multiple-compression ceiling" in reason


def test_phase173_hard_gate_pat_contraction_rejection():
    """Verify that stocks with negative or contracting PAT growth are disqualified."""
    # Shilchar Technologies ground truth: Q1 FY27 PAT -49.7% YoY
    shilchar_fund = {
        "market_cap": 4500.0,
        "debt_to_equity": 0.01,
        "pledged_pct": 0.0,
        "roce_latest": 50.7,
        "pe_ratio": 32.8,
        "pat_growth_latest": -49.7,
    }
    reason = _check_hard_gates(shilchar_fund)
    assert reason is not None
    assert "PAT growth -49.7% <= 0.0% (contracting net profit)" in reason


def test_phase173_hard_gate_qualifying_compounder_passes():
    """Verify that a genuine compounder meeting all hard gates passes cleanly."""
    # Genus Power / Kernex profile
    genus_fund = {
        "market_cap": 8990.0,
        "debt_to_equity": 0.32,
        "pledged_pct": 0.0,
        "roce_latest": 25.4,
        "pe_ratio": 14.0,
        "pat_growth_latest": 85.0,
        "sector": "ELECTRICAL EQUIPMENT",
    }
    reason = _check_hard_gates(genus_fund)
    assert reason is None


def test_phase173_annualized_book_to_bill_normalization():
    """Verify contract execution tenure normalization for multi-year concessions."""
    # Genus Power: ₹22,000 Cr backlog over 7-year AMISP concession with ₹1,850 Cr annual sales
    genus_b2b_fund = {
        "order_book": 22000.0,
        "total_revenue": 1850.0,
        "contract_execution_tenure_years": 7.0,
        "sector": "SMART METERING",
    }
    res = _calculate_annualized_book_to_bill(genus_b2b_fund)
    assert res["raw_book_to_bill"] == round(22000.0 / 1850.0, 3)  # ~11.892x raw
    assert res["execution_tenure_years"] == 7.0
    assert res["annualized_book_to_bill"] == round(22000.0 / (7.0 * 1850.0), 3)  # ~1.699x annualized

    # Sectoral default fallback test (765kV green transformers -> 1.75 years)
    taril_b2b_fund = {
        "order_book": 7237.0,
        "total_revenue": 1420.0,
        "sector": "TRANSFORMER AND POWER",
    }
    taril_res = _calculate_annualized_book_to_bill(taril_b2b_fund)
    assert taril_res["execution_tenure_years"] == 1.75
    assert taril_res["annualized_book_to_bill"] == round(7237.0 / (1.75 * 1420.0), 3)  # ~2.912x


def test_phase173_multiple_compression_penalty_in_multibagger_engine():
    """Verify that InstitutionalMultibaggerEngine applies multiple-compression penalties."""
    base_item = {
        "symbol": "HIGH_PE_TEST",
        "market_cap": 5000.0,
        "current_price": 500.0,
        "roe_latest": 25.0,
        "roce_latest": 30.0,
        "opm_latest": 20.0,
        "sales_growth_latest": 40.0,
        "pat_growth_latest": 50.0,
        "cfo_last_year": 120.0,
        "net_profit_last_year": 100.0,
        "debt_to_equity": 0.1,
        "promoter_holding": 60.0,
        "pledged_pct": 0.0,
        "pe_ratio": 25.0,
    }
    res_normal = InstitutionalMultibaggerEngine.evaluate_company(base_item)

    # Test extreme P/E (>150x)
    extreme_item = dict(base_item, pe_ratio=180.0)
    res_extreme = InstitutionalMultibaggerEngine.evaluate_company(extreme_item)
    assert any("Extreme Valuation Compression Risk" in f for f in res_extreme["risk_flags"])
    assert res_extreme["overall_score"] < res_normal["overall_score"]


def test_phase173_self_learning_engine_record_empirical_rule():
    """Verify that record_empirical_rule stores and persists rules to the registry."""
    engine = SelfLearningEngine()
    rule = engine.record_empirical_rule(
        rule_name="TEXRAIL_ROCE_HARD_GATE_BREACH",
        category="HARD_GATE_DISQUALIFICATION",
        confidence=1.0,
        logic_statement="Texmaco Rail ROCE is 11.5% on Screener, which breaches the 20.0% institutional floor.",
        target_symbol="TEXRAIL",
    )
    assert rule.entity_id == "TEXRAIL_ROCE_HARD_GATE_BREACH"
    assert rule.verification_status == "CERTIFIED_FACT"
    assert rule.confidence_score == 1.0

    # Query back
    priors = engine.query_learned_priors(category="HARD_GATE_DISQUALIFICATION")
    found = any(p["entity_id"] == "TEXRAIL_ROCE_HARD_GATE_BREACH" for p in priors)
    assert found is True
