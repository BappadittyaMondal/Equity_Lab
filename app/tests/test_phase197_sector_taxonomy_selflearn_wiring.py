# -*- coding: utf-8 -*-
"""Phase 197 Test Suite.

Covers all 7 machine-verified fixes:
  C1 + I4 : Sector Taxonomy Normalizer + Known Sector Overrides  (security_master.py)
  C2       : SIP Phantom Approval fix                             (horizon_adaptive_engine.py)
  C3       : Self-Learning Auto-Hook wired into arbiter           (arbiter.py)
  C4       : NIFTY_DEFENCE + NIFTY_IT registered                  (institutional_multibagger_engine.py)
  C5       : learned_rules_registry.json count sync              (data/dynamic_knowledge/)
  I1       : HorizonAdaptiveEngine HORIZON_MAP missing entries    (horizon_adaptive_engine.py)
  I3       : AssetLightDenominatorNormalizer boundary <= 0.20     (institutional_multibagger_engine.py)
"""
import json
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# C1 + I4  :  SecurityMaster.normalize_sector() & _KNOWN_SECTOR_OVERRIDES
# ─────────────────────────────────────────────────────────────────────────────
class TestSectorTaxonomyNormalizer:
    """C1 — Sector Naming Chaos: canonical normalisation of all variant spellings."""

    def setup_method(self):
        from app.services.research.security_master import SecurityMaster
        self.SM = SecurityMaster

    def test_capital_goods_mixed_case(self):
        assert self.SM.normalize_sector("Capital Goods") == "CAPITAL_GOODS"

    def test_capital_goods_upper(self):
        assert self.SM.normalize_sector("CAPITAL_GOODS") == "CAPITAL_GOODS"

    def test_defence_uk_spelling(self):
        assert self.SM.normalize_sector("DEFENCE") == "DEFENSE"

    def test_defence_lower(self):
        assert self.SM.normalize_sector("defence") == "DEFENSE"

    def test_defense_us_spelling(self):
        assert self.SM.normalize_sector("DEFENSE") == "DEFENSE"

    def test_it_services_mixed_case(self):
        assert self.SM.normalize_sector("IT Services") == "IT_SERVICES"

    def test_it_services_upper(self):
        assert self.SM.normalize_sector("IT_SERVICES") == "IT_SERVICES"

    def test_technology_maps_to_it_services(self):
        assert self.SM.normalize_sector("TECHNOLOGY") == "IT_SERVICES"

    def test_financial_services_to_bfsi(self):
        assert self.SM.normalize_sector("Financial Services") == "BFSI"

    def test_banking_to_bfsi(self):
        assert self.SM.normalize_sector("BANKING") == "BFSI"

    def test_power_to_power_infra(self):
        assert self.SM.normalize_sector("Power") == "POWER_INFRA"

    def test_infrastructure_to_power_infra(self):
        assert self.SM.normalize_sector("INFRASTRUCTURE") == "POWER_INFRA"

    def test_retail_fast_fashion(self):
        assert self.SM.normalize_sector("Retail & Fast Fashion") == "RETAIL"

    def test_consumer_services(self):
        assert self.SM.normalize_sector("Consumer Services") == "CONSUMER_SERVICES"

    def test_empty_string_returns_unclassified(self):
        assert self.SM.normalize_sector("") == "UNCLASSIFIED"

    def test_none_equivalent_empty(self):
        # normalize_sector("") must not raise
        result = self.SM.normalize_sector("")
        assert result == "UNCLASSIFIED"

    def test_unknown_sector_open_world_tolerance(self):
        # Unknown sector returns uppercased original — does not crash
        result = self.SM.normalize_sector("EXOTIC_SECTOR_XYZ")
        assert result == "EXOTIC_SECTOR_XYZ"

    def test_i4_ksolves_known_override(self):
        """I4 — KSOLVES must map to IT_SERVICES in _KNOWN_SECTOR_OVERRIDES."""
        assert self.SM._KNOWN_SECTOR_OVERRIDES.get("KSOLVES") == "IT_SERVICES"

    def test_i4_nlcindia_known_override(self):
        """I4 — NLCINDIA must map to POWER_INFRA in _KNOWN_SECTOR_OVERRIDES."""
        assert self.SM._KNOWN_SECTOR_OVERRIDES.get("NLCINDIA") == "POWER_INFRA"


# ─────────────────────────────────────────────────────────────────────────────
# C2  :  SIP Phantom Approval fix
# ─────────────────────────────────────────────────────────────────────────────
class TestSIPPhantomApprovalFix:
    """C2 — SIP Phantom Approval: empty / all-None data must NEVER produce evidence_score=100."""

    def setup_method(self):
        from app.services.decision_brain.horizon_adaptive_engine import HorizonAdaptiveEngine
        self.HAE = HorizonAdaptiveEngine

    def test_empty_dict_sip_not_approved(self):
        result = self.HAE.evaluate_horizon_evidence("TEST", "SIP", {})
        assert result["evidence_score"] == 0.0, (
            f"Empty data must yield 0.0 score, got {result['evidence_score']}"
        )

    def test_empty_dict_sip_has_data_insufficient_gate(self):
        result = self.HAE.evaluate_horizon_evidence("TEST", "SIP", {})
        gates = result["breached_gates"]
        assert any("DATA_INSUFFICIENT_ROCE" in g for g in gates), (
            f"DATA_INSUFFICIENT_ROCE not in breached_gates: {gates}"
        )

    def test_all_none_sip_not_approved(self):
        data = {"roce_10y_avg": None, "debt_to_equity": None, "pledged_pct": None}
        result = self.HAE.evaluate_horizon_evidence("TEST", "SIP", data)
        assert result["evidence_score"] == 0.0

    def test_all_none_sip_has_data_insufficient_gate(self):
        data = {"roce_10y_avg": None, "debt_to_equity": None, "pledged_pct": None}
        result = self.HAE.evaluate_horizon_evidence("TEST", "SIP", data)
        gates = result["breached_gates"]
        assert any("DATA_INSUFFICIENT_ROCE" in g for g in gates)

    def test_zero_pledge_valid_real_value_not_missing(self):
        """pledge_pct=0.0 is a real value (zero pledge = excellent).  Must not trigger DATA_INSUFFICIENT."""
        data = {"roce_10y_avg": 20.0, "debt_to_equity": 0.1, "pledged_pct": 0.0}
        result = self.HAE.evaluate_horizon_evidence("TEST", "SIP", data)
        gates = result["breached_gates"]
        # DATA_INSUFFICIENT_ROCE must NOT be raised when real values are present
        assert not any("DATA_INSUFFICIENT_ROCE" in g for g in gates), (
            f"DATA_INSUFFICIENT raised even with real data present: {gates}"
        )

    def test_good_sip_stock_passes(self):
        """A stock meeting all 3 compounder gates must PASS (evidence_score > 0, is_approved True)."""
        data = {"roce_10y_avg": 22.0, "debt_to_equity": 0.15, "pledged_pct": 0.0}
        result = self.HAE.evaluate_horizon_evidence("TEST", "SIP", data)
        assert result["evidence_score"] > 0.0
        # evaluate_horizon_evidence returns "is_approved" not "passed"
        assert result.get("is_approved") is True or result.get("status") == "APPROVED"


# ─────────────────────────────────────────────────────────────────────────────
# C3  :  Self-Learning Auto-Hook accessible from arbiter context
# ─────────────────────────────────────────────────────────────────────────────
class TestSelfLearningAutoHook:
    """C3 — SelfLearningEngine must be importable and arbiter.py must contain the hook."""

    def test_self_learning_engine_importable(self):
        from app.services.research.self_learning_engine import SelfLearningEngine
        assert hasattr(SelfLearningEngine, "learn_from_text"), (
            "SelfLearningEngine must have learn_from_text method"
        )

    def test_arbiter_source_contains_self_learning_hook(self):
        import pathlib
        arbiter_path = pathlib.Path("app/services/decision_brain/arbiter.py")
        src = arbiter_path.read_text(encoding="utf-8")
        assert "SelfLearningEngine" in src, (
            "arbiter.py must reference SelfLearningEngine (Phase 197 C3 hook)"
        )
        assert "learn_from_text" in src, (
            "arbiter.py must call learn_from_text (Phase 197 C3 hook)"
        )

    def test_self_learning_learn_from_text_non_fatal(self):
        """learn_from_text must not raise on a valid conviction summary string."""
        from app.services.research.self_learning_engine import SelfLearningEngine
        try:
            SelfLearningEngine().learn_from_text(
                "Symbol: GRSE, Verdict: Buy, Score: 72, Objective: MULTIBAGGER, Regime: BULL"
            )
        except Exception as exc:
            pytest.fail(f"learn_from_text raised unexpectedly: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# C4  :  NIFTY_DEFENCE + NIFTY_IT registered in AntiSpuriousIntermarketGuard
# ─────────────────────────────────────────────────────────────────────────────
class TestNiftyDefenceItRegistration:
    """C4 — NIFTY_DEFENCE and NIFTY_IT must be registered; defence stocks must NOT FATAL_VETO."""

    def setup_method(self):
        from app.services.research.institutional_multibagger_engine import AntiSpuriousIntermarketGuard
        self.Guard = AntiSpuriousIntermarketGuard

    def test_grse_nifty_defence_not_fatal_veto(self):
        result = self.Guard.validate_intermarket_transmission("GRSE", "NIFTY_DEFENCE")
        assert result["verdict"] != "FATAL_SPURIOUS_VETO", (
            f"GRSE must not be FATAL_SPURIOUS_VETO against NIFTY_DEFENCE; got {result}"
        )

    def test_hal_nifty_defence_weight_positive(self):
        result = self.Guard.validate_intermarket_transmission("HAL", "NIFTY_DEFENCE")
        assert result["index_weight_pct"] > 0.0, (
            f"HAL must have positive weight in NIFTY_DEFENCE; got {result['index_weight_pct']}"
        )

    def test_hal_nifty_defence_valid_transmission(self):
        """HAL is ~19% of NIFTY_DEFENCE — a heavyweight driver."""
        result = self.Guard.validate_intermarket_transmission("HAL", "NIFTY_DEFENCE")
        assert result["verdict"] == "VALID_TRANSMISSION_DRIVER"

    def test_tcs_nifty_it_valid_transmission(self):
        result = self.Guard.validate_intermarket_transmission("TCS", "NIFTY_IT")
        assert result["verdict"] == "VALID_TRANSMISSION_DRIVER"

    def test_infy_nifty_it_weight_positive(self):
        result = self.Guard.validate_intermarket_transmission("INFY", "NIFTY_IT")
        assert result["index_weight_pct"] > 0.0

    def test_grse_nifty_50_still_fatal_veto(self):
        """GRSE is NOT in NIFTY_50 — the original behaviour must be preserved."""
        result = self.Guard.validate_intermarket_transmission("GRSE", "NIFTY_50")
        assert result["verdict"] == "FATAL_SPURIOUS_VETO"

    def test_nifty_defence_all_6_audit_stocks_pass(self):
        """All 6 stocks that were FATAL_SPURIOUS_VETO in audit must now pass."""
        for sym in ("GRSE", "HAL", "BEL", "COCHINSHIP", "MAZDOCK", "BHEL"):
            r = self.Guard.validate_intermarket_transmission(sym, "NIFTY_DEFENCE")
            assert r["verdict"] != "FATAL_SPURIOUS_VETO", (
                f"{sym} still returns FATAL_SPURIOUS_VETO against NIFTY_DEFENCE"
            )


# ─────────────────────────────────────────────────────────────────────────────
# C5  :  Registry count sync
# ─────────────────────────────────────────────────────────────────────────────
class TestRegistryCountSync:
    """C5 — total_entities_count must match len(entities)."""

    def test_registry_count_matches_actual(self):
        with open("data/dynamic_knowledge/learned_rules_registry.json", encoding="utf-8") as f:
            data = json.load(f)
        header = data.get("total_entities_count", -1)
        actual = len(data.get("entities", []))
        assert header == actual, (
            f"total_entities_count={header} != actual len(entities)={actual}"
        )

    def test_registry_count_is_62(self):
        with open("data/dynamic_knowledge/learned_rules_registry.json", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("total_entities_count") == 62


# ─────────────────────────────────────────────────────────────────────────────
# I1  :  HorizonAdaptiveEngine HORIZON_MAP new entries
# ─────────────────────────────────────────────────────────────────────────────
class TestHorizonMapNewEntries:
    """I1 — All 7 previously unmapped objectives must resolve to correct profiles."""

    def setup_method(self):
        from app.services.decision_brain.horizon_adaptive_engine import HorizonAdaptiveEngine
        self.HAE = HorizonAdaptiveEngine

    def test_value_buying_maps_to_turnaround(self):
        assert self.HAE.resolve_horizon_profile("VALUE_BUYING") == "TURNAROUND_1_3Y"

    def test_deadliest_combo_maps_to_launchpad(self):
        assert self.HAE.resolve_horizon_profile("DEADLIEST_COMBO") == "PRE_DISCOVERY_LAUNCHPAD"

    def test_pre_fly_maps_to_launchpad(self):
        assert self.HAE.resolve_horizon_profile("PRE_FLY") == "PRE_DISCOVERY_LAUNCHPAD"

    def test_micro_multibagger_maps_to_launchpad(self):
        assert self.HAE.resolve_horizon_profile("MICRO_MULTIBAGGER") == "PRE_DISCOVERY_LAUNCHPAD"

    def test_kedia_smile_maps_to_compounder(self):
        assert self.HAE.resolve_horizon_profile("KEDIA_SMILE") == "QUALITY_COMPOUNDER_5_10Y"

    def test_peer_compare_maps_to_positional(self):
        assert self.HAE.resolve_horizon_profile("PEER_COMPARE") == "POSITIONAL_SWING_10_30D"

    def test_general_maps_to_positional(self):
        assert self.HAE.resolve_horizon_profile("GENERAL") == "POSITIONAL_SWING_10_30D"


# ─────────────────────────────────────────────────────────────────────────────
# I3  :  AssetLightDenominatorNormalizer boundary <= 0.20
# ─────────────────────────────────────────────────────────────────────────────
class TestAssetLightBoundary:
    """I3 — cap_intensity exactly 0.20 must trigger ASSET_LIGHT_DENOMINATOR_DISTORTION."""

    def setup_method(self):
        from app.services.research.institutional_multibagger_engine import AssetLightDenominatorNormalizer
        self.AL = AssetLightDenominatorNormalizer

    def test_exact_boundary_020_triggers_flag(self):
        """KSOLVES scenario: cap_intensity = 20/100 = 0.20 exactly.
        Uses 'fixed_assets' key (the actual field name in evaluate_capital_intensity).
        ROCE > 45 and sales_growth < 10 -> ASSET_LIGHT_DENOMINATOR_DISTORTION.
        """
        result = self.AL.evaluate_capital_intensity({
            "fixed_assets": 20.0,   # cap_intensity = 20/100 = 0.20 exactly
            "revenue": 100.0,
            "roce": 50.0,           # > 45.0 — triggers the asset-light branch
            "sales_growth_3yr": 5.0,  # < 10.0 — triggers DENOMINATOR_DISTORTION
        })
        flags = result.get("flags", [])
        assert any("Asset-Light" in f or "ASSET_LIGHT" in f for f in flags), (
            f"cap_intensity=0.20 must trigger Asset-Light Distortion flag; flags={flags}"
        )

    def test_above_boundary_021_no_flag(self):
        """cap_intensity > 0.20 must NOT trigger Asset-Light flag.
        Input must use 'fixed_assets' (not 'gross_fixed_assets') and 'net_block'
        is the alias. We use fixed_assets=25, revenue=100 -> cap_intensity=0.25 > 0.20.
        """
        result = self.AL.evaluate_capital_intensity({
            "fixed_assets": 25.0,   # cap_intensity = 25/100 = 0.25 (> 0.20, no flag)
            "revenue": 100.0,
            "roce": 50.0,
            "sales_growth_3yr": 5.0,
        })
        flags = result.get("flags", [])
        assert not any("Asset-Light" in f or "ASSET_LIGHT" in f for f in flags), (
            f"cap_intensity=0.25 must NOT trigger Asset-Light flag; flags={flags}"
        )

    def test_well_below_boundary_010_triggers_flag(self):
        """cap_intensity = 10/100 = 0.10 must also trigger the flag (deep asset-light)."""
        result = self.AL.evaluate_capital_intensity({
            "fixed_assets": 10.0,   # cap_intensity = 10/100 = 0.10
            "revenue": 100.0,
            "roce": 55.0,           # > 45.0
            "sales_growth_3yr": 4.0,  # < 10.0
        })
        flags = result.get("flags", [])
        assert any("Asset-Light" in f or "ASSET_LIGHT" in f for f in flags), (
            f"cap_intensity=0.10 must trigger Asset-Light Distortion flag; flags={flags}"
        )
