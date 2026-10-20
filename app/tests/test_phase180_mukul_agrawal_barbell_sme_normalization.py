"""Phase 180 Tests: Mukul Agrawal Barbell Architecture, M&A Accounting Normalization, and SME Separation.

Covers:
  T1  - panic_vs_derate: M&A deal cost dislocation with EBITDA growth >= 15% avoids de-rating
  T2  - panic_vs_derate: Genuine negative PAT growth without M&A cost triggers de-rating
  T3  - panic_vs_derate: Normal PAT growth >= 15% continues to trigger standard panic signal
  T4  - panic_vs_derate: Returns valid keys including methodology_note
  T5  - shareholding_pattern: calculate_free_float_squeeze calculates liquid retail float correctly
  T6  - shareholding_pattern: strong hands >= 75% triggers is_float_squeezed=True
  T7  - shareholding_pattern: strong hands >= 85% classified as EXTREME_FLOAT_LOCKUP
  T8  - shareholding_pattern: retail float > 40% classified as DIFFUSE_RETAIL_FLOAT
  T9  - shareholding_pattern: calculate_free_float_squeeze handles empty dict gracefully
  T10 - shareholding_pattern: evaluate_sme_liquidity_guard identifies SME platform correctly
  T11 - shareholding_pattern: evaluate_sme_liquidity_guard calculates minimum ticket size in INR
  T12 - shareholding_pattern: evaluate_sme_liquidity_guard identifies mainboard stocks as 1-share lot
  T13 - shareholding_pattern: evaluate_shareholding_pattern returns free_float_squeeze and sme_liquidity_guard
  T14 - intent_adaptive: AGRAWAL_INFLECTION accepts SME half-yearly (H1/H2) growth >= 15%
  T15 - intent_adaptive: AGRAWAL_INFLECTION accepts M&A EBITDA growth >= 15% despite headline PAT
  T16 - intent_adaptive: AGRAWAL_INFLECTION vetoes when growth is below 15% without M&A/SME relief
  T17 - intent_adaptive: AGRAWAL_INFLECTION standard quarterly PAT growth >= 15% continues to pass
  T18 - dynamic_knowledge: MUKUL_AGRAWAL_BARBELL_MA_SME_RULE is present in learned_rules_registry.json
  T19 - dynamic_knowledge: MUKUL_AGRAWAL rule has CERTIFIED_FACT verification status
  T20 - backward compatibility: InstitutionalMultibaggerEngine returns panic_vs_derate cleanly
"""

import json
from pathlib import Path
from typing import Dict, Any

from app.services.research.panic_vs_derate import classify_panic_vs_derate
from app.services.strategies.shareholding_pattern import (
    calculate_free_float_squeeze,
    evaluate_sme_liquidity_guard,
    evaluate_shareholding_pattern,
)
from app.services.research.intent_adaptive_engine import QueryAdaptiveConstraintEngine
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine


class TestPhase180MukulAgrawalBarbellSME:

    def test_t1_panic_vs_derate_ma_dislocation_avoids_derating(self):
        """T1: Headline PAT collapsed due to one-time M&A expenses, but core EBITDA growth >= 15%."""
        item = {
            "symbol": "TEGA",
            "rsi_14": 35.0,
            "price_drop_3m_pct": 18.0,
            "roce_latest": 20.0,
            "pat_growth_latest": -120.0,  # Headline loss
            "ebitda_growth_latest": 28.0, # Core business booming
            "one_time_deal_costs": 191.0, # One-time M&A fee
            "is_m_and_a_dislocation": True,
        }
        res = classify_panic_vs_derate(item)
        assert res["verdict"] == "PANIC_DISLOCATION_OPPORTUNITY"
        assert res["derate_signal_count"] == 0
        assert any("Normalized operating inflection" in s for s in res["panic_signals"])

    def test_t2_panic_vs_derate_genuine_decay_triggers_derate(self):
        """T2: Genuine negative PAT growth without M&A cost triggers de-rating signal."""
        item = {
            "symbol": "DECAY_CORP",
            "rsi_14": 55.0,
            "roce_latest": 8.0,
            "pat_growth_latest": -25.0,
            "op_growth": -20.0,
        }
        res = classify_panic_vs_derate(item)
        assert res["derate_signal_count"] >= 1
        assert any("PAT growth=-25.0%" in s for s in res["derate_signals"])

    def test_t3_panic_vs_derate_normal_pat_growth_panics(self):
        """T3: Standard PAT growth >= 15% continues to trigger standard panic signal."""
        item = {
            "symbol": "GROWTH_CO",
            "pat_growth_latest": 35.0,
        }
        res = classify_panic_vs_derate(item)
        assert any("PAT growth=35.0%" in s for s in res["panic_signals"])

    def test_t4_panic_vs_derate_contract_keys(self):
        """T4: Return dict has all required contract keys."""
        res = classify_panic_vs_derate({})
        for k in ("verdict", "panic_signals", "derate_signals", "confidence", "methodology_note"):
            assert k in res

    def test_t5_free_float_squeeze_calculation(self):
        """T5: Calculates liquid retail float correctly."""
        data = {
            "promoter_holding_pct": 55.0,
            "fii_holding_pct": 15.0,
            "dii_mf_holding_pct": 10.0,
            "superstar_holding_pct": 2.5,
        }
        res = calculate_free_float_squeeze(data)
        assert res["strong_hands_pct"] == 82.5
        assert res["liquid_retail_float_pct"] == 17.5
        assert res["is_float_squeezed"] is True

    def test_t6_float_squeezed_threshold(self):
        """T6: Strong hands >= 75% triggers is_float_squeezed=True."""
        data = {
            "promoter_pct": 60.0,
            "fii_pct": 10.0,
            "dii_pct": 6.0,
        }
        res = calculate_free_float_squeeze(data)
        assert res["strong_hands_pct"] == 76.0
        assert res["is_float_squeezed"] is True
        assert res["squeeze_tier"] == "HIGH_FLOAT_LOCKUP"

    def test_t7_extreme_float_lockup(self):
        """T7: Strong hands >= 85% triggers EXTREME_FLOAT_LOCKUP."""
        data = {
            "promoter_pct": 72.0,
            "fii_pct": 10.0,
            "dii_pct": 6.0,
        }
        res = calculate_free_float_squeeze(data)
        assert res["liquid_retail_float_pct"] == 12.0
        assert res["squeeze_tier"] == "EXTREME_FLOAT_LOCKUP"

    def test_t8_diffuse_retail_float(self):
        """T8: Retail float > 40% triggers DIFFUSE_RETAIL_FLOAT."""
        data = {
            "promoter_pct": 40.0,
            "fii_pct": 5.0,
            "dii_pct": 5.0,
        }
        res = calculate_free_float_squeeze(data)
        assert res["liquid_retail_float_pct"] == 50.0
        assert res["is_float_squeezed"] is False
        assert res["squeeze_tier"] == "DIFFUSE_RETAIL_FLOAT"

    def test_t9_free_float_squeeze_empty_graceful(self):
        """T9: calculate_free_float_squeeze handles empty dict gracefully without crash."""
        res = calculate_free_float_squeeze({})
        assert isinstance(res, dict)
        assert "liquid_retail_float_pct" in res

    def test_t10_sme_liquidity_guard_identifies_sme(self):
        """T10: Identifies SME platform correctly."""
        item = {
            "symbol": "APSIS",
            "is_sme": True,
            "lot_size": 1200,
            "current_price": 150.0,
        }
        res = evaluate_sme_liquidity_guard(item)
        assert res["is_sme"] is True
        assert res["liquidity_risk_grade"] == "HIGH_LIQUIDITY_RISK_SME_LOT"

    def test_t11_sme_liquidity_guard_ticket_size(self):
        """T11: Calculates minimum ticket size in INR."""
        item = {
            "symbol": "APSIS",
            "exchange": "NSE_EMERGE",
            "lot_size": 1000,
            "current_price": 140.0,
        }
        res = evaluate_sme_liquidity_guard(item)
        assert res["minimum_ticket_size_inr"] == 140000.0
        assert "Rs 140,000" in res["liquidity_warning"]

    def test_t12_sme_liquidity_guard_mainboard(self):
        """T12: Identifies mainboard stocks as 1-share lot."""
        item = {
            "symbol": "RELIANCE",
            "current_price": 2800.0,
        }
        res = evaluate_sme_liquidity_guard(item)
        assert res["is_sme"] is False
        assert res["lot_size"] == 1
        assert res["liquidity_risk_grade"] == "NORMAL_MAINBOARD_LIQUIDITY"

    def test_t13_evaluate_shareholding_pattern_includes_new_keys(self):
        """T13: evaluate_shareholding_pattern returns free_float_squeeze and sme_liquidity_guard."""
        res = evaluate_shareholding_pattern("TEST_CO", shareholding_data={"promoter_holding_pct": 60.0, "is_sme": True, "lot_size": 1000, "current_price": 50.0})
        assert "free_float_squeeze" in res
        assert "sme_liquidity_guard" in res
        assert res["sme_liquidity_guard"]["is_sme"] is True

    def test_t14_intent_adaptive_sme_half_yearly_cadence(self):
        """T14: AGRAWAL_INFLECTION accepts SME half-yearly (H1/H2) growth >= 15%."""
        data = {
            "is_sme_platform": True,
            "pat_growth_latest": None,  # Missing quarterly
            "half_yearly_pat_growth": 35.0,  # Robust H1/H2 filing
            "volume_z_score": 1.5,
            "promoter_pledge_pct": 0.0,
        }
        res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("AGRAWAL_INFLECTION", data)
        assert not res.get("objective_blocks")
        assert any("SME semi-annual earnings inflection verified" in t for t in res.get("tightened_parameters", []))

    def test_t15_intent_adaptive_ma_dislocation_relief(self):
        """T15: AGRAWAL_INFLECTION accepts M&A EBITDA growth >= 15% despite headline PAT loss."""
        data = {
            "symbol": "TEGA",
            "pat_growth_latest": -50.0,  # Depressed by deal costs
            "ebitda_growth_latest": 25.0,
            "one_time_deal_costs": 150.0,
            "is_m_and_a_dislocation": True,
            "volume_z_score": 1.2,
            "promoter_pledge_pct": 0.0,
        }
        res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("AGRAWAL_INFLECTION", data)
        assert not res.get("objective_blocks")
        assert any("Normalized operating inflection verified" in t for t in res.get("tightened_parameters", []))

    def test_t16_intent_adaptive_agrawal_veto_low_growth(self):
        """T16: AGRAWAL_INFLECTION vetoes when growth is below 15% without M&A/SME relief."""
        data = {
            "pat_growth_latest": 5.0,  # Below 15% threshold
            "volume_z_score": 0.2,
            "promoter_pledge_pct": 0.0,
        }
        res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("AGRAWAL_INFLECTION", data)
        assert any("OBJECTIVE_BLOCK" in b for b in res.get("objective_blocks", []))

    def test_t17_intent_adaptive_agrawal_standard_growth_pass(self):
        """T17: AGRAWAL_INFLECTION standard quarterly PAT growth >= 15% continues to pass."""
        data = {
            "pat_growth_latest": 22.0,
            "volume_z_score": 1.8,
            "promoter_pledge_pct": 0.0,
        }
        res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("AGRAWAL_INFLECTION", data)
        assert not res.get("objective_blocks")
        assert any("Explosive earnings inflection strictly verified" in t for t in res.get("tightened_parameters", []))

    def test_t18_dynamic_knowledge_rule_present(self):
        """T18: MUKUL_AGRAWAL_BARBELL_MA_SME_RULE is present in learned_rules_registry.json."""
        p = Path("data/dynamic_knowledge/learned_rules_registry.json")
        with open(p, "r", encoding="utf-8") as f:
            registry = json.load(f)
        assert "MUKUL_AGRAWAL_BARBELL_MA_SME_RULE" in registry["entities"]

    def test_t19_dynamic_knowledge_rule_certified(self):
        """T19: MUKUL_AGRAWAL rule has CERTIFIED_FACT verification status."""
        p = Path("data/dynamic_knowledge/learned_rules_registry.json")
        with open(p, "r", encoding="utf-8") as f:
            registry = json.load(f)
        entity = registry["entities"]["MUKUL_AGRAWAL_BARBELL_MA_SME_RULE"]
        assert entity["verification_status"] == "CERTIFIED_FACT"
        assert entity["confidence_score"] >= 0.90

    def test_t20_engine_backward_compatibility(self):
        """T20: InstitutionalMultibaggerEngine returns panic_vs_derate cleanly on minimal item."""
        res = InstitutionalMultibaggerEngine.evaluate_company({"symbol": "COMPAT_TEST"})
        assert "panic_vs_derate" in res
        assert isinstance(res["panic_vs_derate"], dict)
