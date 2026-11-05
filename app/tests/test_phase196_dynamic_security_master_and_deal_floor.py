"""Unit and regression test suite for Phase 196.

Validates:
1. Dynamic SecurityMaster Database Bridge (resolves non-static database stocks like GRSE, TRENT, SHRIRAMFIN).
2. Fallback dynamic record synthesis for valid ticker strings.
3. Institutional Deal-to-Valuation Floor Bridge (InstitutionalDealFloorSentinel).
4. Active institutional floor cushion vs broken floor warning.
5. Certified Dynamic Knowledge Entity #62 in learned_rules_registry.json.
"""

import pytest
import json
from pathlib import Path
from app.services.research.security_master import SecurityMaster, SecurityRecord
from app.services.research.institutional_multibagger_engine import (
    InstitutionalMultibaggerEngine,
    InstitutionalDealFloorSentinel
)


def test_security_master_dynamic_database_resolution():
    """Verify SecurityMaster resolves non-static database stocks via ResearchDataStore bridge."""
    # 1. GRSE (Shipbuilding)
    rec_grse = SecurityMaster.resolve_record("GRSE")
    assert rec_grse is not None
    assert rec_grse.canonical_symbol == "GRSE"
    assert "Shipbuilders" in rec_grse.company_name
    assert rec_grse.yahoo_ticker == "GRSE.NS"
    # Phase 197 C1: sector is now normalized via SecurityMaster.normalize_sector()
    # Raw DB value "Capital Goods" -> canonical "CAPITAL_GOODS"
    assert rec_grse.sector == "CAPITAL_GOODS"

    # 2. TRENT (Retail)
    rec_trent = SecurityMaster.resolve_record("TRENT")
    assert rec_trent is not None
    assert rec_trent.canonical_symbol == "TRENT"
    assert "Trent" in rec_trent.company_name
    assert rec_trent.yahoo_ticker == "TRENT.NS"

    # 3. SHRIRAMFIN (Finance)
    rec_sfin = SecurityMaster.resolve_record("SHRIRAMFIN")
    assert rec_sfin is not None
    assert rec_sfin.canonical_symbol == "SHRIRAMFIN"
    assert "Shriram" in rec_sfin.company_name
    assert rec_sfin.yahoo_ticker == "SHRIRAMFIN.NS"


def test_security_master_dynamic_fallback_synthesis():
    """Verify SecurityMaster dynamically synthesizes valid SecurityRecord for any uppercase ticker."""
    rec_custom = SecurityMaster.resolve_record("NEW_TECH_AI")
    assert rec_custom is not None
    assert rec_custom.canonical_symbol == "NEW_TECH_AI"
    assert rec_custom.yahoo_ticker == "NEW_TECH_AI.NS"
    assert rec_custom.exchange == "NSE"


def test_institutional_deal_floor_active_cushion():
    """Verify preferential allotment price creates an active institutional floor cushion."""
    # Shriram Finance: CMP 885.0 vs MUFG Floor 840.93 -> 4.98% downside to floor
    res = InstitutionalDealFloorSentinel.evaluate_deal_floor("SHRIRAMFIN", current_price=885.0)
    assert res["has_institutional_floor"] is True
    assert res["floor_price"] == 840.93
    assert res["downside_cushion_pct"] == pytest.approx(4.98, rel=1e-2)
    assert res["status"] == "ACTIVE_INSTITUTIONAL_VALUATION_ANCHOR_FLOOR"
    assert res["valuation_floor_multiplier"] == 1.15
    assert any("Institutional Valuation Floor" in f for f in res["flags"])


def test_institutional_deal_floor_moderate_cushion():
    """Verify stock extended >8% but <=20% above floor receives moderate cushion."""
    res = InstitutionalDealFloorSentinel.evaluate_deal_floor("SHRIRAMFIN", current_price=950.0)
    assert res["has_institutional_floor"] is True
    assert res["status"] == "MODERATE_DEAL_FLOOR_CUSHION"
    assert res["valuation_floor_multiplier"] == 1.05


def test_institutional_deal_floor_broken_warning():
    """Verify price falling >5% below institutional entry triggers broken floor warning."""
    res = InstitutionalDealFloorSentinel.evaluate_deal_floor("SHRIRAMFIN", current_price=780.0)
    assert res["has_institutional_floor"] is True
    assert res["status"] == "BROKEN_INSTITUTIONAL_FLOOR_WARNING"
    assert res["valuation_floor_multiplier"] == 0.80
    assert any("Broken Institutional Floor Warning" in f for f in res["flags"])


def test_custom_deal_floor_injection():
    """Verify ad-hoc custom deal floor can be passed dynamically for newly announced deals."""
    res = InstitutionalDealFloorSentinel.evaluate_deal_floor(
        symbol="TCS",
        current_price=3100.0,
        custom_floor_price=3000.0
    )
    assert res["has_institutional_floor"] is True
    assert res["floor_price"] == 3000.0
    assert res["downside_cushion_pct"] == pytest.approx(3.23, rel=1e-2)
    assert res["status"] == "ACTIVE_INSTITUTIONAL_VALUATION_ANCHOR_FLOOR"
    assert res["valuation_floor_multiplier"] == 1.15


def test_dynamic_knowledge_entity_62():
    """Verify Entity #62 exists, is certified, and registry total count is 62."""
    reg_path = Path("data/dynamic_knowledge/learned_rules_registry.json")
    with open(reg_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "INSTITUTIONAL_DEAL_VALUATION_FLOOR_RULE" in data["entities"]
    assert len(data["entities"]) >= 62  # Phase 198: 67 entities with 5 new additions (was 62 in Phase 197)

    e62 = data["entities"]["INSTITUTIONAL_DEAL_VALUATION_FLOOR_RULE"]
    assert e62["verification_status"] == "CERTIFIED_FACT"
    assert e62["confidence_score"] == 0.99
    assert e62["shadow_status"] == "PROMOTED"
