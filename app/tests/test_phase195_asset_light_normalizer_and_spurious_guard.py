"""Unit and regression test suite for Phase 195.

Validates:
1. Asset-Light ROCE Denominator Normalizer (Asset-Light Distortion vs Pristine vs Sovereign Capex Champion).
2. Contextual Order-Book vs Consumer Velocity Sieve (Eliminates Universal Book-to-Bill Trap).
3. Anti-Spurious Cross-Asset & Retail Derivative Quarantine Guard.
4. Dynamic Knowledge Inscription (Entities #60 and #61).
"""

import pytest
import json
from pathlib import Path
from app.services.research.institutional_multibagger_engine import (
    InstitutionalMultibaggerEngine,
    AssetLightDenominatorNormalizer,
    SectorOrderBookOrVelocitySieve,
    AntiSpuriousIntermarketGuard
)


def test_asset_light_denominator_distortion_penalty():
    """Sluggish sales with high ROCE due to near-zero asset base gets penalized."""
    item = {
        "symbol": "KSOLVES_DISTORTION.NS",
        "company_name": "Test Asset Light Distorted",
        "sector": "Information Technology",
        "revenue": 100.0,
        "fixed_assets": 5.0,
        "working_capital": 5.0,
        "roce": 85.0,
        "sales_growth_3yr": 4.0,
        "pat_growth_3yr": 28.0,
        "fcf_last_year": 10.0,
        "pat_last_year": 20.0
    }
    
    # Direct class evaluation
    res = AssetLightDenominatorNormalizer.evaluate_capital_intensity(item)
    assert res["status"] == "ASSET_LIGHT_DENOMINATOR_DISTORTION"
    assert res["normalized_roce_multiplier"] == 0.80
    assert res["capital_intensity"] == 0.10
    assert any("Asset-Light Denominator Distortion" in f for f in res["flags"])
    
    # Engine candidate evaluation applies penalty
    scored = InstitutionalMultibaggerEngine.evaluate_company(item)
    assert any("Asset-Light Denominator Distortion" in f for f in scored["risk_flags"])


def test_pristine_asset_light_compounder_clearance():
    """Asset-light software company with real >20% sales volume and FCF conversion clears cleanly."""
    item = {
        "symbol": "PRISTINE_SAAS.NS",
        "sector": "Information Technology",
        "revenue": 500.0,
        "fixed_assets": 20.0,
        "working_capital": 30.0,
        "roce": 65.0,
        "sales_growth_3yr": 26.0,
        "pat_growth_3yr": 28.0,
        "fcf_last_year": 90.0,
        "pat_last_year": 100.0
    }
    
    res = AssetLightDenominatorNormalizer.evaluate_capital_intensity(item)
    assert res["status"] == "PRISTINE_ASSET_LIGHT_COMPOUNDER"
    assert res["normalized_roce_multiplier"] == 1.00
    assert res["capital_intensity"] == 0.10
    assert any("Pristine Asset-Light Compounder" in f for f in res["flags"])


def test_sovereign_capex_champion_bonus():
    """Capital intensive industrial (shipbuilder/transformer) with high ROCE gets sovereign bonus."""
    item = {
        "symbol": "GRSE_CHAMPION.NS",
        "sector": "Defence Shipbuilding",
        "revenue": 3000.0,
        "fixed_assets": 1200.0,
        "working_capital": 600.0,
        "roce": 28.0,
        "sales_growth_3yr": 24.0,
        "pat_growth_3yr": 35.0,
        "cwip": 500.0,
        "capex_last_year": 400.0
    }
    
    res = AssetLightDenominatorNormalizer.evaluate_capital_intensity(item)
    assert res["status"] == "SOVEREIGN_CAPEX_CHAMPION"
    assert res["normalized_roce_multiplier"] == 1.05
    assert res["capital_intensity"] == 0.60
    assert any("Sovereign Capex Champion" in f for f in res["flags"])


def test_turnaround_and_bfsi_capital_intensity_exemption():
    """Turnaround and Banking sectors are strictly exempt from capital intensity penalties."""
    bfsi_item = {
        "symbol": "HDFCBANK.NS",
        "sector": "Private Sector Bank",
        "revenue": 100000.0,
        "roce": 16.0,
        "sales_growth_3yr": 18.0
    }
    bfsi_res = AssetLightDenominatorNormalizer.evaluate_capital_intensity(bfsi_item)
    assert bfsi_res["is_exempt"] is True
    assert bfsi_res["status"] == "EXEMPT_BFSI_OR_TURNAROUND"

    turnaround_item = {
        "symbol": "RECOVERY_CORP.NS",
        "sector": "Industrial",
        "revenue": 200.0,
        "roce": -5.0,
        "sales_growth_3yr": -10.0,
        "strategy_type": "TURNAROUND"
    }
    ta_res = AssetLightDenominatorNormalizer.evaluate_capital_intensity(turnaround_item, objective="TURNAROUND")
    assert ta_res["is_exempt"] is True
    assert ta_res["status"] == "EXEMPT_BFSI_OR_TURNAROUND"


def test_sector_order_book_sieve_capital_goods():
    """Capital goods and defence evaluated on book-to-bill and burn rate."""
    item_good = {
        "symbol": "TRIL.NS",
        "sector": "Power Capital Goods",
        "revenue": 1500.0,
        "order_book": 3600.0,
        "order_book_burn_rate": 0.28
    }
    res_good = SectorOrderBookOrVelocitySieve.evaluate_sector_pipeline_velocity(item_good)
    assert res_good["status"] == "ROBUST_SOVEREIGN_BACKLOG"
    assert res_good["velocity_score"] == 100.0
    assert res_good["is_order_book_sector"] is True

    item_depleted = {
        "symbol": "WEAK_EPC.NS",
        "sector": "Engineering & Construction",
        "revenue": 1000.0,
        "order_book": 700.0,
        "order_book_burn_rate": 0.12
    }
    res_depleted = SectorOrderBookOrVelocitySieve.evaluate_sector_pipeline_velocity(item_depleted)
    assert res_depleted["status"] == "DEPLETED_ORDER_BOOK"
    assert res_depleted["velocity_score"] <= 85.0


def test_sector_velocity_sieve_consumer_retail():
    """Retail / FMCG evaluated on inventory turnover without requiring order book."""
    trent_item = {
        "symbol": "TRENT.NS",
        "sector": "Consumer Retail",
        "revenue": 12000.0,
        "inventory_turnover": 7.2
    }
    res = SectorOrderBookOrVelocitySieve.evaluate_sector_pipeline_velocity(trent_item)
    assert res["status"] == "RAPID_INVENTORY_VELOCITY"
    assert res["velocity_score"] == 100.0
    assert res["is_consumer_pharma"] is True
    assert res["is_order_book_sector"] is False


def test_anti_spurious_intermarket_non_constituent_veto():
    """Linking Bank Nifty to Asian Paints triggers fatal spurious correlation veto."""
    res = AntiSpuriousIntermarketGuard.validate_intermarket_transmission(
        driver_symbol="ASIANPAINT",
        target_index="BANK_NIFTY"
    )
    assert res["verdict"] == "FATAL_SPURIOUS_VETO"
    assert res["status"] == "SPURIOUS_NON_CONSTITUENT_CLAIM"
    assert res["index_weight_pct"] == 0.0


def test_anti_spurious_intermarket_subordinate_weight():
    """Linking Nifty 50 solely to TCS (only 3.8% weight) is quashed as insufficient index leverage."""
    res = AntiSpuriousIntermarketGuard.validate_intermarket_transmission(
        driver_symbol="TCS",
        target_index="NIFTY_50"
    )
    assert res["verdict"] == "INSUFFICIENT_INDEX_LEVERAGE"
    assert res["is_dominant_driver"] is False
    assert res["index_weight_pct"] == 3.8


def test_anti_spurious_intermarket_dominant_heavyweight():
    """HDFCBANK (29.5% Bank Nifty, 11.5% Nifty) is recognized as a valid transmission driver."""
    res_bn = AntiSpuriousIntermarketGuard.validate_intermarket_transmission(
        driver_symbol="HDFCBANK",
        target_index="BANK_NIFTY"
    )
    assert res_bn["verdict"] == "VALID_TRANSMISSION_DRIVER"
    assert res_bn["is_dominant_driver"] is True
    assert res_bn["index_weight_pct"] >= 25.0


def test_dynamic_knowledge_entities_phase195():
    """Dynamic knowledge registry contains certified Entities #60 and #61."""
    reg_path = Path("data/dynamic_knowledge/learned_rules_registry.json")
    assert reg_path.exists(), "Registry file must exist"
    
    with open(reg_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "ASSET_LIGHT_ROCE_DENOMINATOR_RULE" in data["entities"]
    assert "ANTI_SPURIOUS_INTERMARKET_GUARD_RULE" in data["entities"]
    assert len(data["entities"]) >= 61
    
    e60 = data["entities"]["ASSET_LIGHT_ROCE_DENOMINATOR_RULE"]
    assert e60["verification_status"] == "CERTIFIED_FACT"
    assert e60["confidence_score"] >= 0.98
    
    e61 = data["entities"]["ANTI_SPURIOUS_INTERMARKET_GUARD_RULE"]
    assert e61["verification_status"] == "CERTIFIED_FACT"
    assert e61["confidence_score"] >= 0.98
