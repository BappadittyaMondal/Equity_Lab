# -*- coding: utf-8 -*-
"""Unit tests for Phase 190: Domestic SIP Liquidity Firewall, Concall Guidance Velocity & AI Data Center Thermal Infrastructure Ontology."""

import pytest
import json
from pathlib import Path

from app.services.research.market_regime import DIIAbsorptionRatioScorer
from app.services.ingestion.announcements_radar import GuidanceRevisionVelocityScorer, CorporateAnnouncementsRadar
from app.services.research.security_master import SecurityMaster
from app.services.research.supply_chain_graph import SupplyChainGraphEngine


class TestPhase190DIIAbsorptionAndGuidanceVelocity:
    """Test suite validating Phase 190 macro liquidity, guidance revision velocity, and AI thermal ontology."""

    def test_dii_super_absorption_firewall(self):
        """Test DII super absorption when domestic inflows overwhelm foreign selling."""
        res = DIIAbsorptionRatioScorer.calculate_absorption_ratio(
            dii_net_cr=30000.0,
            fii_net_cr=-20000.0,
            monthly_sip_runrate_cr=26000.0
        )
        assert res["status"] == "COMPUTED"
        assert res["absorption_ratio"] == 1.50
        assert res["regime_status"] == "DOMESTIC_SUPER_ABSORPTION"
        assert res["firewall_active"] is True
        assert res["risk_haircut"] == 0.0
        assert "DOMESTIC_FIREWALL_SUPER_ABSORPTION" in res["signals"]
        assert "SIP_RUNRATE_COVERS_OUTFLOW" in res["signals"]

    def test_dii_stable_absorption(self):
        """Test DII stable absorption buffering foreign outflows (1.0x <= ratio < 1.25x)."""
        res = DIIAbsorptionRatioScorer.calculate_absorption_ratio(
            dii_net_cr=22000.0,
            fii_net_cr=-20000.0
        )
        assert res["absorption_ratio"] == 1.10
        assert res["regime_status"] == "DOMESTIC_ABSORPTION_STABLE"
        assert res["firewall_active"] is True
        assert res["risk_haircut"] == 0.0
        assert "DOMESTIC_FIREWALL_STABLE_ABSORPTION" in res["signals"]

    def test_partial_absorption_and_deficit_haircuts(self):
        """Test moderate deficit and severe unabsorbed liquidation haircuts."""
        # Partial absorption (0.5x <= ratio < 1.0x)
        partial = DIIAbsorptionRatioScorer.calculate_absorption_ratio(
            dii_net_cr=14000.0,
            fii_net_cr=-20000.0
        )
        assert partial["absorption_ratio"] == 0.70
        assert partial["regime_status"] == "PARTIAL_DOMESTIC_ABSORPTION"
        assert partial["firewall_active"] is False
        assert partial["risk_haircut"] == 0.10
        assert "MODERATE_FOREIGN_LIQUIDITY_DRAIN" in partial["signals"]

        # Severe unabsorbed outflow (ratio < 0.5x)
        severe = DIIAbsorptionRatioScorer.calculate_absorption_ratio(
            dii_net_cr=6000.0,
            fii_net_cr=-20000.0
        )
        assert severe["absorption_ratio"] == 0.30
        assert severe["regime_status"] == "NET_LIQUIDITY_DEFICIT_HAIRCUT"
        assert severe["firewall_active"] is False
        assert severe["risk_haircut"] == 0.20
        assert "UNABSORBED_FII_OUTFLOW_PANIC" in severe["signals"]

    def test_fii_net_buyer_and_unobserved_flow_data(self):
        """Test dual buying tailwind and fail-closed unobserved flow baseline."""
        # Dual buying
        dual = DIIAbsorptionRatioScorer.calculate_absorption_ratio(
            dii_net_cr=12000.0,
            fii_net_cr=8000.0
        )
        assert dual["regime_status"] == "DUAL_CAPITAL_INFLOW"
        assert dual["firewall_active"] is True
        assert dual["risk_haircut"] == 0.0

        # Unobserved flow data
        unobs = DIIAbsorptionRatioScorer.calculate_absorption_ratio(None, None)
        assert unobs["status"] == "DATA_UNAVAILABLE"
        assert unobs["regime_status"] == "DATA_UNAVAILABLE_BASELINE"
        assert unobs["risk_haircut"] == 0.0

    def test_guidance_revision_velocity_accelerating_alpha(self):
        """Test consecutive quarters of guidance upgrades triggering institutional alpha boost."""
        res = GuidanceRevisionVelocityScorer.evaluate_guidance_velocity(
            consecutive_quarters_raised=2,
            revenue_guidance_delta_pct=15.0,
            pat_guidance_delta_pct=22.0,
            order_book_to_bill_ratio=3.5
        )
        assert res["velocity_tier"] == "ACCELERATING_INSTITUTIONAL_ALPHA"
        assert res["catalyst_score_delta"] == 17.5  # 15.0 base + 2.5 order book modifier
        assert res["institutional_stance"] == "STRONG_ACCUMULATION_CATALYST"
        assert "CONSECUTIVE_GUIDANCE_UPGRADE_ACCELERATION" in res["signals"]
        assert "MULTI_YEAR_ORDER_BOOK_RUNWAY" in res["signals"]

        # Test single quarter guidance raise
        single = GuidanceRevisionVelocityScorer.evaluate_guidance_velocity(
            consecutive_quarters_raised=1,
            revenue_guidance_delta_pct=10.0
        )
        assert single["velocity_tier"] == "POSITIVE_GUIDANCE_INFLECTION"
        assert single["catalyst_score_delta"] == 7.5

        # Test consecutive guidance cut de-rating
        downgrade = GuidanceRevisionVelocityScorer.evaluate_guidance_velocity(
            consecutive_quarters_raised=-2,
            revenue_guidance_delta_pct=-12.0
        )
        assert downgrade["velocity_tier"] == "CONSECUTIVE_GUIDANCE_DOWNGRADE_DE_RATING"
        assert downgrade["catalyst_score_delta"] == -20.0
        assert downgrade["institutional_stance"] == "STRUCTURAL_DE_RATING_RISK"

        # Test direct exposure on CorporateAnnouncementsRadar
        radar_call = CorporateAnnouncementsRadar.evaluate_guidance_velocity(consecutive_quarters_raised=2)
        assert radar_call["velocity_tier"] == "ACCELERATING_INSTITUTIONAL_ALPHA"

    def test_ai_datacenter_thermal_ontology_classification(self):
        """Test classification of high-density AI data center thermal equipment and liquid cooling."""
        # Known Tier 1 thermal equipment provider
        thermax = SecurityMaster.classify_ai_datacenter_exposure("THERMAX")
        assert thermax["has_ai_datacenter_exposure"] is True
        assert thermax["tier"] == "TIER_1_DATA_CENTER_INFRASTRUCTURE"
        assert "PRECISION_CHILLERS" in thermax["subsectors_matched"]
        assert thermax["institutional_tailwind_score"] == 85.0

        # Known Tier 1 grid/power provider
        schneider = SecurityMaster.classify_ai_datacenter_exposure("SCHNEIDER")
        assert schneider["has_ai_datacenter_exposure"] is True
        assert schneider["tier"] == "TIER_1_DATA_CENTER_INFRASTRUCTURE"
        assert "POWER_TRANSFORMERS_GRID" in schneider["subsectors_matched"]

        # Keyword match on custom company text
        custom_match = SecurityMaster.classify_ai_datacenter_exposure(
            symbol="CUSTOM_CO",
            description_or_products="Manufacturing CDU coolant distribution units and direct-to-chip cold plates"
        )
        assert custom_match["has_ai_datacenter_exposure"] is True
        assert "LIQUID_COOLING_SKIDS" in custom_match["subsectors_matched"]
        assert custom_match["cooling_architecture"] == "DIRECT_TO_CHIP_LIQUID_COOLING"

        # Completely unrelated stock
        unrelated = SecurityMaster.classify_ai_datacenter_exposure("TRENT")
        assert unrelated["has_ai_datacenter_exposure"] is False
        assert unrelated["cooling_architecture"] == "NONE"

    def test_supply_chain_graph_data_center_nodes(self):
        """Test supply chain graph customer-supplier linkages for AI data center infrastructure."""
        thermax_sc = SupplyChainGraphEngine.get_supply_chain_profile("THERMAX")
        assert thermax_sc["sector"] == "AI_DATA_CENTER_THERMAL"
        assert any("CtrlS" in c for c in thermax_sc["primary_customers"])
        assert "VOLTAS" in thermax_sc["second_order_beneficiaries"]

        schneider_sc = SupplyChainGraphEngine.get_supply_chain_profile("SCHNEIDER")
        assert schneider_sc["sector"] == "DATA_CENTER_ELECTRICAL_INFRASTRUCTURE"
        assert "POLYCAB" in schneider_sc["second_order_beneficiaries"]

    def test_learned_rules_registry_51_entities(self):
        """Test that dynamic knowledge registry contains at least 51 certified entities including Phase 190 rules."""
        base_dir = Path(__file__).resolve().parent.parent.parent
        reg_file = base_dir / "data" / "dynamic_knowledge" / "learned_rules_registry.json"
        with open(reg_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["total_entities_count"] >= 51
        assert "DII_SIP_LIQUIDITY_FIREWALL_RULE" in data["entities"]
        assert "DATA_CENTER_LIQUID_COOLING_INFRASTRUCTURE_RULE" in data["entities"]

        dii_rule = data["entities"]["DII_SIP_LIQUIDITY_FIREWALL_RULE"]
        assert dii_rule["confidence_score"] == 0.99
        assert dii_rule["verification_status"] == "CERTIFIED_FACT"

        dc_rule = data["entities"]["DATA_CENTER_LIQUID_COOLING_INFRASTRUCTURE_RULE"]
        assert dc_rule["confidence_score"] == 0.98
        assert dc_rule["verification_status"] == "CERTIFIED_FACT"
