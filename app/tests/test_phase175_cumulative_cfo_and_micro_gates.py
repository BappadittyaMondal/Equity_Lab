"""Unit tests for Phase 175: 3-Year Cumulative Cash Flow Enforcement, Debt-Free Coverage Exemption & Micro-Level Accounting Hard Gates."""

import pytest
from app.services.research.deadliest_combo_pipeline import (
    _check_hard_gates,
    _calculate_order_book_burn_rate,
)
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine


def test_phase175_negative_cumulative_cfo_rejection():
    """Verify that stocks with negative 3-year cumulative operating cash flow are disqualified."""
    # TARIL ground truth profile: Cumulative 3Y CFO is -Rs 65 Cr vs PAT Rs 454 Cr
    taril_fund = {
        "market_cap": 7500.0,
        "debt_to_equity": 0.25,
        "pledged_pct": 0.0,
        "roce_latest": 22.0,
        "pe_ratio": 45.0,
        "pat_growth_latest": 55.0,
        "cfo_3yr": -65.0,
        "pat_3yr": 454.0,
    }
    reason = _check_hard_gates(taril_fund)
    assert reason is not None
    assert "3Y Cumulative CFO ₹-65.0 Cr < 0" in reason


def test_phase175_sub_070_cumulative_cfo_rejection():
    """Verify that stocks with 3Y cumulative CFO/PAT < 0.70x are disqualified as working capital traps."""
    # SHAKTIPUMP ground truth profile: 3Y cumulative CFO/PAT is ~0.31x
    shakti_fund = {
        "market_cap": 8200.0,
        "debt_to_equity": 0.20,
        "pledged_pct": 0.0,
        "roce_latest": 24.5,
        "pe_ratio": 28.0,
        "pat_growth_latest": 42.0,
        "cfo_3yr": 40.0,
        "pat_3yr": 130.0,  # 40 / 130 = 0.31x < 0.70x
    }
    reason = _check_hard_gates(shakti_fund)
    assert reason is not None
    assert "3Y Cumulative CFO/PAT 0.31x < 0.70x institutional floor" in reason


def test_phase175_negative_pe_loss_maker_rejection():
    """Verify that loss-making entities with negative P/E are disqualified from compounder pipelines."""
    loss_maker_fund = {
        "market_cap": 1200.0,
        "debt_to_equity": 0.10,
        "pledged_pct": 0.0,
        "roce_latest": 22.0,
        "pe_ratio": -15.4,
        "pat_growth_latest": 45.0,  # Narrowing loss showing positive statistical growth
    }
    reason = _check_hard_gates(loss_maker_fund)
    assert reason is not None
    assert "P/E -15.4 <= 0 (negative earnings" in reason


def test_phase175_zero_debt_interest_coverage_exemption():
    """Verify that completely debt-free companies (D/E = 0.0) are NOT penalized when interest_coverage is None."""
    item_debt_free = {
        "symbol": "PRISTINE_DEBT_FREE",
        "market_cap": 5000.0,
        "current_price": 500.0,
        "sales_growth_3yr": 20.0,
        "pat_growth_3yr": 25.0,
        "sales_growth_latest": 22.0,
        "pat_growth_latest": 28.0,
        "roce_latest": 30.0,
        "roe_latest": 25.0,
        "opm_latest": 22.0,
        "debt_to_equity": 0.0,
        "interest_coverage": None,  # Undefined EBIT / 0
        "pledged_pct": 0.0,
        "promoter_holding": 60.0,
        "cfo_last_year": 120.0,
        "net_profit_last_year": 100.0,
        "pe_ratio": 25.0,
    }
    res = InstitutionalMultibaggerEngine.evaluate_company(item_debt_free)
    # Must NOT have interest coverage penalty or flag
    assert "Interest Coverage Data Missing/Unverified" not in res["risk_flags"]


def test_phase175_qualifying_cash_compounder_passes():
    """Verify that a genuine cash-generating compounder meeting all hard gates passes cleanly."""
    clean_fund = {
        "market_cap": 9500.0,
        "debt_to_equity": 0.15,
        "pledged_pct": 0.0,
        "roce_latest": 28.0,
        "pe_ratio": 26.0,
        "pat_growth_latest": 32.0,
        "cfo_3yr": 350.0,
        "pat_3yr": 300.0,  # 350 / 300 = 1.17x >= 0.70x
        "sector": "SPECIALTY CHEMICALS",
    }
    reason = _check_hard_gates(clean_fund)
    assert reason is None


def test_phase175_slow_burn_order_book_flag():
    """Verify that kappa < 0.20 indicates execution slow-burn risk."""
    fund_slow_burn = {
        "order_book": 12000.0,
        "total_revenue": 1000.0,  # kappa = 1000 / 12000 = 0.083 < 0.20
    }
    kappa = _calculate_order_book_burn_rate(fund_slow_burn)
    assert kappa is not None
    assert kappa < 0.20
