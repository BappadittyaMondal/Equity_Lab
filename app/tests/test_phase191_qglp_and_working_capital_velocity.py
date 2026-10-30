# -*- coding: utf-8 -*-
"""Unit tests for Phase 191: Raamdeo Agrawal QGLP Multibagger Engine & Dr. Anil Lamba Working Capital Velocity Guard."""

import pytest
import json
from pathlib import Path

from app.services.research.institutional_multibagger_engine import (
    InstitutionalMultibaggerEngine,
    RaamdeoAgrawalQGLPScorer,
)
from app.services.research.epv_and_shenanigans import WorkingCapitalVelocityScorer
from app.services.strategies.shareholding_pattern import (
    match_smart_money_entity,
    get_superstar_portfolio_symbols,
    detect_smart_money_clustering,
)


class TestPhase191QGLPAndWorkingCapitalVelocity:
    """Test suite validating Phase 191 QGLP 100x compounding framework, working capital velocity, and Motilal Oswal tracking."""

    def test_pristine_qglp_100x_candidate(self):
        """Test a pristine multibagger candidate passing all QGLP pillars with high score."""
        candidate = {
            "symbol": "COMPOUNDER_X",
            "roce_latest": 26.0,
            "cfo_last_year": 180.0,
            "net_profit_last_year": 140.0,
            "promoter_holding": 62.0,
            "pledged_pct": 0.0,
            "debt_to_equity": 0.08,
            "sales_growth_3yr": 24.0,
            "pat_growth_3yr": 32.0,  # Jaw effect: PAT > Sales
            "market_cap_cr": 4200.0,  # Extreme 100x headroom (< 5000 Cr)
            "pe_ratio": 25.0,  # PEG = 25 / 32 = 0.78 (< 1.0)
        }
        res = RaamdeoAgrawalQGLPScorer.evaluate_qglp(candidate)
        assert res["qglp_total_score"] >= 80.0
        assert res["qglp_verdict"] == "PRISTINE_QGLP_100X_CANDIDATE"
        assert res["recommendation"] == "HIGH_CONVICTION_MULTIBAGGER_ACCUMULATE"
        assert "PRISTINE_ROCE_OVER_20" in res["signals"]
        assert "HIGH_CASH_CONVERSION_CFO_PAT" in res["signals"]
        assert "POSITIVE_JAW_OPERATING_LEVERAGE" in res["signals"]
        assert "EXTREME_100X_MCAP_HEADROOM" in res["signals"]
        assert "PRISTINE_QGLP_PEG_UNDER_1" in res["signals"]

        # Verify class method on InstitutionalMultibaggerEngine
        eng_call = InstitutionalMultibaggerEngine.evaluate_raamdeo_agrawal_qglp(candidate)
        assert eng_call["qglp_verdict"] == "PRISTINE_QGLP_100X_CANDIDATE"

    def test_fails_qglp_criteria(self):
        """Test a low-quality, leveraged, slow-growth, expensive scrip rejected by QGLP."""
        bad_stock = {
            "symbol": "WEAK_CO",
            "roce_latest": 8.0,
            "cfo_last_year": 20.0,
            "net_profit_last_year": 80.0,
            "promoter_holding": 35.0,
            "pledged_pct": 28.0,
            "debt_to_equity": 1.4,
            "sales_growth_3yr": 4.0,
            "pat_growth_3yr": 2.0,
            "market_cap_cr": 65000.0,
            "pe_ratio": 45.0,
        }
        res = RaamdeoAgrawalQGLPScorer.evaluate_qglp(bad_stock)
        assert res["qglp_total_score"] < 45.0
        assert res["qglp_verdict"] == "REJECTED_FAILS_QGLP_CRITERIA"
        assert res["recommendation"] == "DO_NOT_CHASE"

    def test_lamba_negative_working_capital_float(self):
        """Test Dr. Anil Lamba's pristine negative working capital machine (e.g. DMart / FMCG)."""
        res = WorkingCapitalVelocityScorer.evaluate_working_capital_velocity(
            symbol="CASH_FLOAT_CO",
            debtor_days=8.0,
            inventory_days=25.0,
            creditor_days=45.0,  # 8 + 25 - 45 = -12 days
        )
        assert res["cash_to_cash_cycle_days"] == -12.0
        assert res["velocity_tier"] == "NEGATIVE_WORKING_CAPITAL_FLOAT"
        assert res["risk_score"] == 0.0
        assert res["conviction_boost"] == 15.0
        assert "PRISTINE_NEGATIVE_WORKING_CAPITAL_FLOAT" in res["signals"]

    def test_lamba_working_capital_suffocation_paper_profit_trap(self):
        """Test Dr. Anil Lamba's paper profit trap where PAT grows while CCC expands by >30 days."""
        res = WorkingCapitalVelocityScorer.evaluate_working_capital_velocity(
            symbol="PAPER_TRAP_CO",
            debtor_days=110.0,
            inventory_days=95.0,
            creditor_days=40.0,  # CCC = 165 days
            prior_debtor_days=70.0,
            prior_inventory_days=65.0,
            prior_creditor_days=45.0,  # Prior CCC = 90 days. Delta = +75 days
            pat_growth_pct=25.0,
            cfo_cr=15.0,
            pat_cr=85.0,  # CFO/PAT = 0.18 (< 0.50)
        )
        assert res["cash_to_cash_cycle_days"] == 165.0
        assert res["delta_ccc_days"] == 75.0
        assert res["velocity_tier"] == "CRITICAL_WORKING_CAPITAL_SUFFOCATION"
        assert res["risk_score"] == 30.0
        assert res["conviction_boost"] <= -25.0
        assert "WORKING_CAPITAL_SUFFOCATION_TRAP" in res["signals"]
        assert "LAMBA_PAPER_PROFIT_SUFFOCATION_ALERT" in res["alerts"]
        assert "CFO_PAT_DIVERGENCE_WORKING_CAPITAL_ABSORPTION" in res["alerts"]

    def test_raamdeo_agrawal_smart_money_tracking(self):
        """Test tracking and clustering detection of Raamdeo Agrawal / Motilal Oswal."""
        assert match_smart_money_entity("Raamdeo Agrawal") == "RAAMDEO_AGRAWAL"
        assert match_smart_money_entity("Motilal Oswal Financial Services") == "RAAMDEO_AGRAWAL"
        assert match_smart_money_entity("Ramdeo Agarwal") == "RAAMDEO_AGRAWAL"

        holdings = get_superstar_portfolio_symbols("RAAMDEO_AGRAWAL")
        assert "MOTILALOFS" in holdings
        assert "APARINDS" in holdings
        assert len(holdings) >= 5

        # Test multi-investor clustering with Raamdeo Agrawal
        filings = [
            {"name": "Raamdeo Agrawal", "holding_pct": 2.1, "quarter": "Q2FY26"},
            {"name": "Mukul Agrawal", "holding_pct": 1.8, "quarter": "Q2FY26"},
        ]
        clustering = detect_smart_money_clustering(filings)
        assert clustering["is_smart_money_clustered"] is True
        assert "RAAMDEO_AGRAWAL" in clustering["tracked_entities"]
        assert "MUKUL_AGRAWAL" in clustering["tracked_entities"]

    def test_dynamic_knowledge_registry_53_entities(self):
        """Test that dynamic knowledge registry contains 53 certified entities including Phase 191 rules."""
        base_dir = Path(__file__).resolve().parent.parent.parent
        reg_file = base_dir / "data" / "dynamic_knowledge" / "learned_rules_registry.json"
        with open(reg_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["total_entities_count"] == 53
        assert "RAAMDEO_AGRAWAL_QGLP_FRAMEWORK_RULE" in data["entities"]
        assert "LAMBA_WORKING_CAPITAL_VELOCITY_RULE" in data["entities"]

        qglp = data["entities"]["RAAMDEO_AGRAWAL_QGLP_FRAMEWORK_RULE"]
        assert qglp["confidence_score"] == 0.99
        assert qglp["verification_status"] == "CERTIFIED_FACT"

        lamba = data["entities"]["LAMBA_WORKING_CAPITAL_VELOCITY_RULE"]
        assert lamba["confidence_score"] == 0.98
        assert lamba["verification_status"] == "CERTIFIED_FACT"
