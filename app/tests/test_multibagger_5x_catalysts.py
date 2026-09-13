"""Unit tests for Phase 80: Multibagger 5x Operational Inflection Catalysts."""

import pytest
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine


def test_5x_operational_catalysts_clean_triple_inflection():
    """Verify 5x operational catalysts trigger on capex, low float, and debt elimination."""
    candidate = {
        "symbol": "5X_INFLECTION_TEST",
        "company_name": "5X Inflection Test Corp",
        "current_price": 150.0,
        "market_cap": 800.0,
        "cwip": 80.0,
        "net_block": 200.0,  # CWIP / Net Block = 40.0% (>= 30%)
        "promoter_holding": 75.0,
        "dii_holding": 2.0,
        "fii_holding": 1.5,   # Free Float = 21.5% - 75% = ~21.5%, Inst = 3.5%
        "free_float_pct": 18.0,
        "debt": 20.0,
        "prev_debt": 60.0,   # Debt reduced by 66.7% (>= 50%)
        "cash": 30.0,        # Net Cash = ₹10 Cr
        "tier1_auditor": True,
        "related_party_flag": False,
        "promoter_comp_pct_of_profit": 2.5,
    }

    res = InstitutionalMultibaggerEngine.evaluate_5x_operational_catalysts(candidate)
    assert res["catalyst_score"] >= 80.0
    assert res["has_5x_catalyst"] is True
    assert res["active_catalysts_count"] == 3
    assert res["catalysts"]["capacity_inflection"]["is_active"] is True
    assert res["catalysts"]["float_and_institutional"]["is_active"] is True
    assert res["catalysts"]["radical_deleveraging"]["is_active"] is True
    assert res["catalysts"]["forensic_baseline"]["is_active"] is True


def test_5x_operational_catalysts_blocked_by_forensic_failure():
    """Verify forensic red flag (related party lending) disables 5x catalyst qualification."""
    candidate = {
        "symbol": "DIRTY_5X_TEST",
        "cwip": 100.0,
        "net_block": 200.0,
        "free_float_pct": 12.0,
        "dii_holding": 3.0,
        "debt": 10.0,
        "prev_debt": 50.0,
        "tier1_auditor": False,       # Local unknown 2-partner firm
        "related_party_flag": True,   # Promoters lending to shell companies
    }

    res = InstitutionalMultibaggerEngine.evaluate_5x_operational_catalysts(candidate)
    assert res["catalysts"]["capacity_inflection"]["is_active"] is True
    assert res["catalysts"]["forensic_baseline"]["is_active"] is False
    # Even if score from capex is high, forensic failure must block 5x catalyst endorsement
    assert res["has_5x_catalyst"] is False
