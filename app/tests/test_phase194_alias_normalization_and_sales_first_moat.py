"""Phase 194 Dedicated Unit Tests.

Validates:
1. Canonical Objective Alias Normalization in QueryAdaptiveConstraintEngine and Arbiter.
2. Parity between shorthand string aliases ('SIP', 'SWING', 'VALUE') and canonical profiles.
3. Basant Maheshwari Sales-First Multiplier and Unsustainable Margin Expansion Warning.
4. Maintenance vs Growth Capex Sieve (Asset-Heavy sink vs Gigafactory supercycle clearance).
5. Scoping boundary isolation (Turnaround and BFSI exemptions).
6. Certified Dynamic Knowledge Entities #58 and #59 in learned_rules_registry.json.
"""

import json
import os
import pytest
from app.services.research.intent_adaptive_engine import (
    QueryAdaptiveConstraintEngine,
    ARCHETYPE_WEIGHT_PROFILES,
)
from app.services.decision_brain.arbiter import Arbiter
from app.services.research.institutional_multibagger_engine import (
    InstitutionalMultibaggerEngine,
    BasantMaheshwariGrowthSentinel,
)


def test_normalize_intent_alias():
    """Verify heterogeneous user/API aliases map to canonical archetype keys."""
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("SIP") == "SIP_COMPOUNDER"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("sip_compound") == "SIP_COMPOUNDER"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("SWING") == "SWING_POSITIONAL"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("swing_trade") == "SWING_POSITIONAL"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("VALUE") == "VALUE_BUYING"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("deep_value") == "VALUE_BUYING"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("MICROCAP") == "EARLY_MICROCAP"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("PREFLY") == "PRE_FLY"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("DEADLIEST") == "DEADLIEST_COMBO"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("TURNAROUND") == "TURNAROUND"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("SWING_3D") == "SWING_3D"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("POSITIONAL_30D") == "POSITIONAL_30D"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("UNKNOWN_FOO") == "GENERAL"


def test_get_weight_profile_alias_parity():
    """Verify get_weight_profile returns dedicated archetype profiles for shorthand aliases."""
    w_sip = QueryAdaptiveConstraintEngine.get_weight_profile("SIP")
    assert w_sip == ARCHETYPE_WEIGHT_PROFILES["SIP_COMPOUNDER"]
    assert w_sip["FUNDAMENTAL"] == 0.40
    assert w_sip["TECHNICAL"] == 0.00

    w_swing = QueryAdaptiveConstraintEngine.get_weight_profile("SWING")
    assert w_swing == ARCHETYPE_WEIGHT_PROFILES["SWING_POSITIONAL"]
    assert w_swing["TECHNICAL"] == 0.50
    assert w_swing["FUNDAMENTAL"] == 0.10

    w_val = QueryAdaptiveConstraintEngine.get_weight_profile("VALUE")
    assert w_val == ARCHETYPE_WEIGHT_PROFILES["VALUE_BUYING"]
    assert w_val["VALUATION"] == 0.35


def test_arbiter_weighted_score_alias_parity():
    """Verify Arbiter._compute_weighted_score uses dedicated weights for shorthand objectives."""
    arb = Arbiter()
    # B5 is TECHNICAL (VCP Pattern Breakout), E1 is FUNDAMENTAL
    dummy_outputs = [
        {"engine_id": "B5", "score_0_100": 80.0, "status": "ok", "verdict": "Buy", "confidence": 100.0},
        {"engine_id": "E1", "score_0_100": 40.0, "status": "ok", "verdict": "Buy", "confidence": 100.0},
    ]
    # For SWING, Technical has 50% weight, Fundamental has 10% weight (both are included)
    score_swing, breakdown_swing = arb._compute_weighted_score(dummy_outputs, objective="SWING")
    assert "TECHNICAL" in breakdown_swing
    assert breakdown_swing["TECHNICAL"] == 80.0

    # For SIP, Technical has 0% weight, Fundamental has 40% weight
    score_sip, breakdown_sip = arb._compute_weighted_score(dummy_outputs, objective="SIP")
    assert "FUNDAMENTAL" in breakdown_sip
    assert breakdown_sip["FUNDAMENTAL"] == 40.0
    # Technical engine with 0% weight is excluded from SIP breakdown
    assert "TECHNICAL" not in breakdown_sip


def test_basant_maheshwari_pristine_sales_growth():
    """Verify company with >= 20% sales CAGR is classified as pristine secular compounder."""
    item = {
        "symbol": "TRENT",
        "sales_growth_3yr": 35.0,
        "pat_growth_3yr": 38.0,
        "cfo_last_year": 900.0,
        "depreciation_last_year": 120.0,
        "sector": "RETAIL",
    }
    res = BasantMaheshwariGrowthSentinel.evaluate_growth_moat(item)
    assert res["moat_status"] == "PRISTINE_SECULAR_GROWTH_COMPOUNDER"
    assert res["moat_multiplier"] == 1.00
    assert len(res["flags"]) == 0


def test_basant_maheshwari_margin_trick_penalty():
    """Verify company with high PAT growth but stagnant sales triggers warning and haircut."""
    item = {
        "symbol": "COST_CUT_CO",
        "sales_growth_3yr": 3.8,  # Subdued top-line
        "pat_growth_3yr": 32.0,   # High PAT
        "cfo_last_year": 80.0,
        "depreciation_last_year": 20.0,
        "sector": "SPECIALTY_CHEMICALS",
    }
    res = BasantMaheshwariGrowthSentinel.evaluate_growth_moat(item)
    assert res["moat_status"] == "UNSUSTAINABLE_MARGIN_EXPANSION_TRICK"
    assert res["moat_multiplier"] == 0.70
    assert any("PAT CAGR" in f for f in res["flags"])


def test_basant_maheshwari_turnaround_and_bfsi_exemption():
    """Verify Turnarounds and BFSI are strictly exempted from manufacturing sales/depreciation filters."""
    # 1. Turnaround
    turnaround_item = {
        "symbol": "TURNAROUND_STEEL",
        "sales_growth_3yr": -4.0,
        "pat_growth_3yr": 5.0,
        "sector": "STEEL",
    }
    res_t = BasantMaheshwariGrowthSentinel.evaluate_growth_moat(turnaround_item, objective="TURNAROUND")
    assert res_t["is_exempt"] is True
    assert res_t["moat_status"] == "EXEMPT_NON_MANUFACTURING_OR_TURNAROUND"
    assert res_t["moat_multiplier"] == 1.00

    # 2. BFSI
    bfsi_item = {
        "symbol": "ICICIBANK",
        "sales_growth_3yr": 12.0,
        "pat_growth_3yr": 22.0,
        "sector": "BANKING",
    }
    res_b = BasantMaheshwariGrowthSentinel.evaluate_growth_moat(bfsi_item)
    assert res_b["is_exempt"] is True
    assert res_b["moat_status"] == "EXEMPT_NON_MANUFACTURING_OR_TURNAROUND"


def test_maintenance_capex_sink_penalty():
    """Verify depreciation consuming >75% of CFO with low sales triggers maintenance sink flag."""
    item = {
        "symbol": "AGING_PLANT_CO",
        "sales_growth_3yr": 5.0,
        "pat_growth_3yr": 8.0,
        "cfo_last_year": 100.0,
        "depreciation_last_year": 85.0,  # 85% of CFO consumed by depreciation
        "sector": "TEXTILES",
    }
    res = BasantMaheshwariGrowthSentinel.evaluate_growth_moat(item)
    assert res["maintenance_drag_ratio"] == 0.85
    assert any("ASSET_HEAVY_MAINTENANCE_SINK" in f for f in res["flags"])
    assert res["moat_multiplier"] <= 0.75


def test_expansion_gigafactory_supercycle_clearance():
    """Verify high capex backed by CWIP > 35% capex and sales >= 15% is cleared as gigafactory supercycle."""
    item = {
        "symbol": "DIXON_TECH",
        "sales_growth_3yr": 28.0,
        "pat_growth_3yr": 35.0,
        "cfo_last_year": 400.0,
        "capex_last_year": 350.0,
        "cwip": 180.0,  # 51% of capex in CWIP
        "depreciation_last_year": 60.0,
        "sector": "EMS_MANUFACTURING",
    }
    res = BasantMaheshwariGrowthSentinel.evaluate_growth_moat(item)
    assert any("EXPANSION_GIGAFACTORY_SUPERCYCLE" in f for f in res["flags"])
    assert res["moat_status"] == "PRISTINE_SECULAR_GROWTH_COMPOUNDER"
    assert res["moat_multiplier"] == 1.00


def test_dynamic_knowledge_entities_phase194():
    """Verify Entities #58 and #59 are certified in learned_rules_registry.json."""
    registry_path = os.path.join("data", "dynamic_knowledge", "learned_rules_registry.json")
    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_entities_count"] >= 59
    assert "BASANT_MAHESHWARI_SALES_FIRST_COMPOUNDER_RULE" in data["entities"]
    assert "MAINTENANCE_VS_GROWTH_CAPEX_SIEVE_RULE" in data["entities"]

    e58 = data["entities"]["BASANT_MAHESHWARI_SALES_FIRST_COMPOUNDER_RULE"]
    assert e58["confidence_score"] == 0.99
    assert e58["verification_status"] == "CERTIFIED_FACT"

    e59 = data["entities"]["MAINTENANCE_VS_GROWTH_CAPEX_SIEVE_RULE"]
    assert e59["confidence_score"] == 0.98
    assert e59["verification_status"] == "CERTIFIED_FACT"
