"""Phase 186 Tests: Ashish Kacholia Capital Scalability Engine.

Covers:
  T1  - calculate_core_operating_ex_cwip_roce: Strips uncommissioned CWIP & cash from denominator
  T2  - calculate_core_operating_ex_cwip_roce: Zero CWIP returns is_cwip_adjusted=False
  T3  - calculate_core_operating_ex_cwip_roce: Graceful empty / missing input handling
  T4  - calculate_core_operating_ex_cwip_roce: Derives EBIT from PAT + Interest + Tax
  T5  - calculate_core_operating_ex_cwip_roce: Derives Capital Employed from Debt + Equity
  T6  - intent_adaptive: KACHOLIA_SCALABILITY passes high-CWIP company via Core ROCE
  T7  - intent_adaptive: KACHOLIA_SCALABILITY vetoes poor ROCE (< 18%) even after CWIP adjustment
  T8  - intent_adaptive: Order Book-to-Bill >= 2.0x with healthy margin (>= 12%) passes with backlog finding
  T9  - intent_adaptive: Order Book-to-Bill >= 2.0x with thin margin (< 12%) flags L1 margin risk warning
  T10 - preferential_allotment: Tier 1 institutional / marquee subscriber classified correctly (+15 pts)
  T11 - preferential_allotment: Tier 2 promoter infusion at/above ICDR floor classified correctly (+8 pts)
  T12 - preferential_allotment: Tier 2 promoter warrants below ICDR floor flagged as discounted
  T13 - preferential_allotment: Tier 3 unverified corporate entities flagged as operator risk (0 pts)
  T14 - preferential_allotment: No preferential issue returns NO_RECENT_PREFERENTIAL_ISSUE
  T15 - shareholding_pattern: evaluate_shareholding_pattern returns preferential_allotment_quality
  T16 - investment_committee: kacholia_scalability_vector adds Ex-CWIP Core ROCE finding
  T17 - investment_committee: kacholia_scalability_vector flags L1 margin risk concern
  T18 - investment_committee: kacholia_scalability_vector flags operator risk concern
  T19 - dynamic_knowledge: ASHISH_KACHOLIA_CAPITAL_SCALABILITY_RULE exists and is CERTIFIED_FACT
  T20 - backward compatibility: Standard inputs continue to work seamlessly
"""

import json
from pathlib import Path
import pytest

from app.services.research.intent_adaptive_engine import (
    calculate_core_operating_ex_cwip_roce,
    QueryAdaptiveConstraintEngine,
)
from app.services.strategies.shareholding_pattern import (
    evaluate_preferential_allotment_quality,
    evaluate_shareholding_pattern,
)
from app.services.ai_committee.investment_committee import VirtualInvestmentCommittee


class TestPhase186KacholiaScalabilityEngine:

    def test_t1_ex_cwip_roce_calculation(self):
        """T1: Strips uncommissioned CWIP & cash from denominator, lifting ROCE."""
        data = {
            "ebit": 40.0,
            "capital_employed": 300.0,  # Reported includes Rs 150 Cr uncommissioned CWIP
            "cwip": 150.0,
            "cash": 0.0,
        }
        res = calculate_core_operating_ex_cwip_roce(data)
        assert res["is_cwip_adjusted"] is True
        assert res["reported_roce"] == pytest.approx(13.33, rel=0.01)
        assert res["core_roce"] == pytest.approx(26.67, rel=0.01)
        assert res["expansion_lift_pts"] > 13.0
        assert "Ex-CWIP Core ROCE" in res["methodology_note"]

    def test_t2_ex_cwip_roce_zero_cwip(self):
        """T2: Zero CWIP returns is_cwip_adjusted=False without artificial lift."""
        data = {
            "ebit": 50.0,
            "capital_employed": 200.0,
            "cwip": 0.0,
            "cash": 10.0,
        }
        res = calculate_core_operating_ex_cwip_roce(data)
        assert res["is_cwip_adjusted"] is False
        assert res["core_roce"] == pytest.approx(25.0, rel=0.01)
        assert res["expansion_lift_pts"] == 0.0

    def test_t3_ex_cwip_roce_empty_dict(self):
        """T3: Empty dict handled gracefully without crashing."""
        res = calculate_core_operating_ex_cwip_roce({})
        assert res["is_cwip_adjusted"] is False
        assert res["core_roce"] is None

    def test_t4_ex_cwip_roce_derived_ebit(self):
        """T4: Accurately derives EBIT from PAT + Interest + Tax."""
        data = {
            "pat": 30.0,
            "interest_expense": 5.0,
            "tax": 10.0,  # EBIT = 45.0
            "capital_employed": 250.0,
            "cwip": 100.0,
        }
        res = calculate_core_operating_ex_cwip_roce(data)
        assert res["is_cwip_adjusted"] is True
        assert res["core_roce"] == pytest.approx(30.0, rel=0.01)  # 45 / (250 - 100) = 30.0%

    def test_t5_ex_cwip_roce_derived_cap_employed(self):
        """T5: Accurately derives Capital Employed from Debt + Equity."""
        data = {
            "ebit": 40.0,
            "total_debt": 50.0,
            "net_worth": 150.0,  # Total CE = 200.0
            "cwip": 50.0,
            "cash": 10.0,  # Adjusted CE = 200 - 50 - 10 = 140.0
        }
        res = calculate_core_operating_ex_cwip_roce(data)
        assert res["is_cwip_adjusted"] is True
        assert res["core_roce"] == pytest.approx(28.57, rel=0.01)  # 40 / 140 = 28.57%

    def test_t6_kacholia_gate_passes_high_cwip(self):
        """T6: Company with reported ROCE 14% (<18% hurdle) passes via Core Ex-CWIP ROCE."""
        item = {
            "symbol": "HIGH_CWIP_CORP",
            "sales_growth_3yr": 20.0,
            "roce_latest": 14.0,  # Trailing ROCE below 18% hurdle
            "ebit": 45.0,
            "capital_employed": 300.0,
            "cwip": 120.0,  # Core ROCE = 45 / 180 = 25.0% >= 18%
            "cfo_pat_ratio": 0.85,
            "debt_to_equity": 0.35,
        }
        eval_res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("KACHOLIA_SCALABILITY", item)
        assert not any("Incremental capital productivity" in b for b in eval_res.get("objective_blocks", []))
        assert any("High Core Ex-CWIP capital productivity verified" in t for t in eval_res.get("tightened_parameters", []))

    def test_t7_kacholia_gate_vetoes_poor_roce(self):
        """T7: Truly poor capital productivity (<18% even after CWIP adjustment) fails gate."""
        item = {
            "symbol": "WEAK_CAPITAL_CORP",
            "sales_growth_3yr": 20.0,
            "roce_latest": 11.0,
            "ebit": 15.0,
            "capital_employed": 150.0,
            "cwip": 10.0,  # Core ROCE = 15 / 140 = 10.7% < 18%
            "cfo_pat_ratio": 0.85,
            "debt_to_equity": 0.35,
        }
        eval_res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("KACHOLIA_SCALABILITY", item)
        assert any("Incremental capital productivity" in b for b in eval_res.get("objective_blocks", []))

    def test_t8_order_book_b2b_healthy_margin(self):
        """T8: High Book-to-Bill >= 2.0x with healthy margin (>= 12%) passes with backlog finding."""
        item = {
            "symbol": "HEALTHY_EPC",
            "sales_growth_3yr": 18.0,
            "roce_latest": 22.0,
            "order_book_cr": 600.0,
            "total_revenue": 200.0,  # B2B = 3.0x
            "opm": 18.0,  # Healthy margin >= 12%
        }
        eval_res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("KACHOLIA_SCALABILITY", item)
        assert any("High-visibility order backlog verified" in t for t in eval_res.get("tightened_parameters", []))
        assert not any("L1 margin risk" in w for w in eval_res.get("warnings", []))

    def test_t9_order_book_b2b_thin_margin_l1_risk(self):
        """T9: High Book-to-Bill >= 2.0x with thin margin (< 12%) flags L1 margin risk warning."""
        item = {
            "symbol": "RISKY_L1_EPC",
            "sales_growth_3yr": 18.0,
            "roce_latest": 22.0,
            "order_book_cr": 800.0,
            "total_revenue": 200.0,  # B2B = 4.0x
            "opm": 8.0,  # Thin margin < 12%
        }
        eval_res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("KACHOLIA_SCALABILITY", item)
        assert any("L1 margin risk" in w for w in eval_res.get("warnings", []))

    def test_t10_preferential_allotment_tier1_institutional(self):
        """T10: Tier 1 institutional / marquee subscriber classified correctly (+15 pts)."""
        data = {
            "has_preferential_issue": True,
            "preferential_issue_subscribers": ["HDFC Mutual Fund", "Lucky Investment Managers", "Ashish Kacholia"],
            "preferential_price": 250.0,
            "sebi_icdr_floor_price": 240.0,
        }
        res = evaluate_preferential_allotment_quality(data)
        assert res["subscriber_tier"] == "INSTITUTIONAL_MARQUEE_CO_INVESTMENT"
        assert res["score_boost_pts"] == 15.0
        assert res["is_positive_catalyst"] is True
        assert res["operator_risk_flag"] is False

    def test_t11_preferential_allotment_tier2_promoter_fair(self):
        """T11: Tier 2 promoter infusion at/above ICDR floor classified correctly (+8 pts)."""
        data = {
            "has_preferential_issue": True,
            "preferential_issue_subscribers": ["Promoter Group", "Founders"],
            "preferential_price": 105.0,
            "sebi_icdr_floor_price": 100.0,
        }
        res = evaluate_preferential_allotment_quality(data)
        assert res["subscriber_tier"] == "PROMOTER_SKIN_IN_GAME"
        assert res["score_boost_pts"] == 8.0
        assert res["is_positive_catalyst"] is True
        assert res["operator_risk_flag"] is False

    def test_t12_preferential_allotment_tier2_promoter_discount(self):
        """T12: Tier 2 promoter warrants below ICDR floor flagged as discounted."""
        data = {
            "has_preferential_issue": True,
            "preferential_issue_subscribers": ["Promoter Group"],
            "preferential_price": 85.0,
            "sebi_icdr_floor_price": 100.0,
        }
        res = evaluate_preferential_allotment_quality(data)
        assert res["subscriber_tier"] == "PROMOTER_DISCOUNTED_WARRANTS"
        assert res["operator_risk_flag"] is True

    def test_t13_preferential_allotment_tier3_operator(self):
        """T13: Tier 3 unverified corporate entities flagged as operator risk (0 pts)."""
        data = {
            "has_preferential_issue": True,
            "preferential_issue_subscribers": ["Apex Finvest Pvt Ltd", "Sunrise Mercantile LLP"],
            "preferential_price": 50.0,
        }
        res = evaluate_preferential_allotment_quality(data)
        assert res["subscriber_tier"] == "UNVERIFIED_OPERATOR_RISK"
        assert res["score_boost_pts"] == 0.0
        assert res["operator_risk_flag"] is True

    def test_t14_preferential_allotment_none(self):
        """T14: No preferential issue returns NO_RECENT_PREFERENTIAL_ISSUE."""
        res = evaluate_preferential_allotment_quality({})
        assert res["has_preferential_issue"] is False
        assert res["subscriber_tier"] == "NO_RECENT_PREFERENTIAL_ISSUE"

    def test_t15_shareholding_pattern_incorporates_preferential(self):
        """T15: evaluate_shareholding_pattern returns preferential_allotment_quality key."""
        shp_data = {
            "promoter_holding_pct": 55.0,
            "fii_holding_pct": 10.0,
            "dii_mf_holding_pct": 10.0,
            "has_preferential_issue": True,
            "preferential_issue_subscribers": ["Lucky Investment Managers"],
        }
        res = evaluate_shareholding_pattern("TEST_CO", shareholding_data=shp_data)
        assert "preferential_allotment_quality" in res
        assert res["preferential_allotment_quality"]["subscriber_tier"] == "INSTITUTIONAL_MARQUEE_CO_INVESTMENT"
        assert any("INSTITUTIONAL_MARQUEE_CO_INVESTMENT" in e for e in res["evidence"])

    def test_t16_investment_committee_ex_cwip_lift(self):
        """T16: kacholia_scalability_vector adds Ex-CWIP Core ROCE finding."""
        stock = {
            "roce_latest": 14.0,
            "ebit": 40.0,
            "capital_employed": 300.0,
            "cwip": 150.0,  # Core ROCE = 40 / 150 = 26.7%
            "asset_turnover": 1.6,
            "sales_growth_3yr": 20.0,
            "pat_growth_3yr": 25.0,
            "debt_to_equity": 0.25,
        }
        op = VirtualInvestmentCommittee.kacholia_scalability_vector("EXPANDING_CO", stock)
        assert op.vote == "APPROVE"
        assert any("Ex-CWIP Core ROCE Inflection" in f for f in op.key_findings)

    def test_t17_investment_committee_l1_risk(self):
        """T17: kacholia_scalability_vector flags L1 margin risk concern."""
        stock = {
            "roce_latest": 22.0,
            "order_book": 900.0,
            "total_revenue": 250.0,
            "opm": 8.0,  # Thin margin < 12%
        }
        op = VirtualInvestmentCommittee.kacholia_scalability_vector("L1_CO", stock)
        assert any("L1 Margin Risk" in c for c in op.risk_concerns)

    def test_t18_investment_committee_operator_risk(self):
        """T18: kacholia_scalability_vector flags operator risk concern on Tier 3 preferential."""
        stock = {
            "roce_latest": 22.0,
            "has_preferential_issue": True,
            "preferential_issue_subscribers": ["Shadow Finvest Pvt Ltd"],
        }
        op = VirtualInvestmentCommittee.kacholia_scalability_vector("OPERATOR_CO", stock)
        assert any("Operator Risk" in c for c in op.risk_concerns)

    def test_t19_dynamic_knowledge_rule_exists(self):
        """T19: ASHISH_KACHOLIA_CAPITAL_SCALABILITY_RULE exists and is CERTIFIED_FACT."""
        reg_file = Path("data/dynamic_knowledge/learned_rules_registry.json")
        assert reg_file.exists()
        with open(reg_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        entities = data.get("entities", {})
        assert "ASHISH_KACHOLIA_CAPITAL_SCALABILITY_RULE" in entities
        rule = entities["ASHISH_KACHOLIA_CAPITAL_SCALABILITY_RULE"]
        assert rule["verification_status"] == "CERTIFIED_FACT"
        assert rule["shadow_status"] == "PROD"

    def test_t20_backward_compatibility(self):
        """T20: Standard inputs without CWIP or preferential issue continue to work seamlessly."""
        stock = {
            "roce_latest": 24.0,
            "sales_growth_3yr": 22.0,
            "pat_growth_3yr": 28.0,
            "debt_to_equity": 0.20,
        }
        op = VirtualInvestmentCommittee.kacholia_scalability_vector("STANDARD_CO", stock)
        assert op.vote == "APPROVE"
        assert op.conviction_weight == 90.0
