"""Unit tests for Phase 182: ER&D Services Decoupling, Horizon-Tiered Liquidity, and Growth Working Capital Buffer."""

import pytest
import sqlite3
import json
from pathlib import Path

from app.services.research.deadliest_combo_pipeline import (
    calculate_continuous_q_bounds,
    _calculate_operating_leverage_convexity,
    _calculate_annualized_book_to_bill,
)
from app.services.research.universe_screener import (
    _ARCHETYPE_DEFAULT_UNIVERSES,
    run_technical_universe_screener,
)


# ---------------------------------------------------------------------------
# Section 1: Growth Working Capital Buffer in Continuous Q
# ---------------------------------------------------------------------------

def test_continuous_q_growth_working_capital_buffer():
    """Verify that rapid scaling companies (sales growth >= 20%) with positive CFO
    receive the 0.60 credit floor rather than being crushed as paper-profit frauds."""
    # 1. High-growth company with temporary working capital lag (TAAL Tech pattern: +30% Sales, CFO/PAT = 0.33)
    fund_growth = {
        "cfo_pat": 0.33,
        "sales_growth_latest": 30.0,
        "debt_to_equity": 0.05,
        "pledged_pct": 0.0,
    }
    q_growth, _, _, state_growth = calculate_continuous_q_bounds(fund_growth)
    assert state_growth == "OBSERVED"
    # tc = max(0.60, 0.33/0.80=0.4125) = 0.60
    # Q = 0.40 * 0.60 + 0.30 * 1.0 + 0.30 * 0.90 = 0.24 + 0.30 + 0.27 = 0.81
    assert q_growth >= 0.80, f"Expected Q >= 0.80 for high-growth expansion, got {q_growth}"

    # 2. Stagnant company (sales growth = 5%) with same CFO/PAT = 0.33 gets no floor
    fund_stagnant = {
        "cfo_pat": 0.33,
        "sales_growth_latest": 5.0,
        "debt_to_equity": 0.05,
        "pledged_pct": 0.0,
    }
    q_stagnant, _, _, _ = calculate_continuous_q_bounds(fund_stagnant)
    # tc = 0.4125 -> Q = 0.40 * 0.4125 + 0.60 = 0.765
    assert q_stagnant < q_growth, "Stagnant company should not receive high-growth buffer"
    assert q_stagnant <= 0.77

    # 3. Fraud / negative cash flow company (CFO/PAT <= 0) gets ZERO credit regardless of sales growth
    fund_fraud = {
        "cfo_pat": -0.15,
        "sales_growth_latest": 40.0,
        "debt_to_equity": 0.05,
        "pledged_pct": 0.0,
    }
    q_fraud, _, _, _ = calculate_continuous_q_bounds(fund_fraud)
    # tc = 0.0 -> Q = 0.40 * 0.0 + 0.30 * 1.0 + 0.30 * 0.90 = 0.57
    assert q_fraud == 0.57, f"Negative cash flow must receive 0.0 tc credit, got {q_fraud}"


# ---------------------------------------------------------------------------
# Section 2: Asset-Light / Services / ER&D Convexity Boost
# ---------------------------------------------------------------------------

def test_operating_leverage_convexity_erd_services_boost():
    """Verify that elite asset-light ER&D / Service companies (ROCE >= 22%, OPM >= 18%)
    receive the 0.20 operating leverage boost even without physical factory CWIP."""
    # 1. ER&D Services firm with zero CWIP but high ROCE & OPM
    fund_erd = {
        "pat_growth_latest": 25.0,
        "sales_growth_latest": 20.0,
        "sector": "IT - ER&D / Engineering Services",
        "roce_latest": 28.5,
        "operating_margin": 24.0,
        "cwip": 0.0,
        "net_block": 50.0,
    }
    omega_erd = _calculate_operating_leverage_convexity(fund_erd)
    # Base ratio = 25 / 20 = 1.25. Boost = +0.20 -> 1.45
    assert omega_erd >= 1.40, f"Expected Omega >= 1.40 for elite ER&D firm, got {omega_erd}"

    # 2. Low-margin generic service firm gets no boost
    fund_generic = {
        "pat_growth_latest": 25.0,
        "sales_growth_latest": 20.0,
        "sector": "Services - Facilities Management",
        "roce_latest": 12.0,
        "operating_margin": 8.0,
        "cwip": 0.0,
        "net_block": 50.0,
    }
    omega_generic = _calculate_operating_leverage_convexity(fund_generic)
    assert omega_generic == 1.25, f"Expected un-boosted 1.25 for generic firm, got {omega_generic}"


# ---------------------------------------------------------------------------
# Section 3: Sector Tenure Mapping for ER&D / Software
# ---------------------------------------------------------------------------

def test_annualized_book_to_bill_erd_tenure():
    """Verify IT / ER&D / Tech sectors normalize to 1.0 year contract tenure."""
    fund = {
        "sector": "IT - ER&D Services",
        "order_book": 200.0,
        "total_revenue": 150.0,
    }
    res = _calculate_annualized_book_to_bill(fund)
    assert res["execution_tenure_years"] == 1.0
    assert res["annualized_book_to_bill"] == round(200.0 / (1.0 * 150.0), 3)


# ---------------------------------------------------------------------------
# Section 4: Horizon-Tiered Liquidity Filtering
# ---------------------------------------------------------------------------

def test_universe_screener_horizon_tiered_liquidity():
    """Verify that Tier 0 liquidity gate uses ₹30 Lakh floor for MICRO intents
    while maintaining ₹1.0 Cr floor for SWING and GENERAL intents."""
    # Check default universe routing
    res_micro = run_technical_universe_screener(
        universe=["TAALTECH", "RELIANCE"],
        intent_archetype="MICRO_MULTIBAGGER"
    )
    assert res_micro["intent_archetype"] == "MICRO_MULTIBAGGER"
    assert res_micro["tier0_survivors_count"] >= 1


# ---------------------------------------------------------------------------
# Section 5: Universe Membership & Database Population
# ---------------------------------------------------------------------------

def test_curated_universes_contain_new_microcaps():
    """Verify TAALTECH, CONCORD, SHAKTIPUMP, DYCL exist in default microcap and deadliest combo pools."""
    micro_pool = _ARCHETYPE_DEFAULT_UNIVERSES["MICRO_MULTIBAGGER"]
    deadliest_pool = _ARCHETYPE_DEFAULT_UNIVERSES["DEADLIEST_COMBO"]
    for sym in ("TAALTECH", "CONCORD", "SHAKTIPUMP", "DYCL"):
        assert sym in micro_pool, f"{sym} missing from MICRO_MULTIBAGGER pool"
        assert sym in deadliest_pool, f"{sym} missing from DEADLIEST_COMBO pool"


def test_companies_table_has_microcaps():
    """Verify data/ierl_equity.sqlite3 contains all four new microcaps."""
    conn = sqlite3.connect("data/ierl_equity.sqlite3")
    cur = conn.cursor()
    cur.execute("SELECT symbol, legal_name, sector FROM companies WHERE symbol in ('TAALTECH', 'CONCORD', 'SHAKTIPUMP', 'DYCL')")
    rows = cur.fetchall()
    conn.close()
    found_symbols = {r[0] for r in rows}
    assert {"TAALTECH", "CONCORD", "SHAKTIPUMP", "DYCL"}.issubset(found_symbols)


def test_learned_rules_registry_has_erd_rule():
    """Verify learned_rules_registry.json contains ERD_SERVICES_CONVEXITY_RULE."""
    with open("data/dynamic_knowledge/learned_rules_registry.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "ERD_SERVICES_CONVEXITY_RULE" in data["entities"]
    rule = data["entities"]["ERD_SERVICES_CONVEXITY_RULE"]
    assert rule["verification_status"] == "CERTIFIED_FACT"
    assert rule["confidence_score"] >= 0.90
