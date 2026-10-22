"""Phase 189: Unit & Forensic Test Suite for Reliance Jio DRHP Intelligence,
Adjusted Sovereign Solvency & Cash Tax Cliff Runway Scorer.
"""

import pytest
from app.services.research.ipo_intelligence_engine import (
    IPOIntelligenceEngine,
    UNLISTED_IPO_PIPELINE,
)
from app.services.research.epv_and_shenanigans import (
    RegulatoryAndSovereignSolvencyScorer,
    CashTaxShieldRunwayScorer,
)


class TestPhase189JioDRHPAndSovereignSolvency:
    """Test suite validating Phase 189 deliverables."""

    def test_jio_present_in_unlisted_ipo_pipeline(self):
        """Validates that Reliance Jio Infocomm is canonically registered in UNLISTED_IPO_PIPELINE."""
        pipeline = IPOIntelligenceEngine.get_pipeline()
        jio_entries = [p for p in pipeline if p.get("symbol") == "JIO"]
        assert len(jio_entries) == 1, "JIO must be uniquely present in unlisted pipeline."

        jio = jio_entries[0]
        assert jio["company_name"] == "Reliance Jio Infocomm Ltd"
        assert jio["sector"] == "TELECOM_DIGITAL_INFRASTRUCTURE"
        assert jio["est_valuation_cr"] == 1000000.0
        assert jio["operating_margin_pct"] == 51.9
        assert jio["listing_gain_prob_baseline"] == 0.85
        assert "DoT deferred spectrum" in jio["key_risk"]
        assert "tax cliff" in jio["key_risk"]

    def test_adjusted_regulatory_solvency_telecom_spectrum_inclusion(self):
        """Validates that deferred spectrum dues & Ind AS 116 leases expand true leverage."""
        res = RegulatoryAndSovereignSolvencyScorer.calculate_adjusted_solvency(
            symbol="JIO",
            ebitda_cr=65000.0,
            financial_debt_cr=20000.0,
            cash_and_equivalents_cr=5000.0,
            deferred_spectrum_liabilities_cr=104000.0,
            lease_liabilities_cr=11000.0,
            annual_interest_expense_cr=2500.0,
            interest_accretion_cr=5500.0,
            sector="TELECOM",
        )

        assert res["standard_net_debt_cr"] == 15000.0
        assert res["total_regulatory_obligations_cr"] == 115000.0
        assert res["adjusted_net_debt_cr"] == 130000.0
        assert res["standard_leverage_ratio"] == 0.23
        assert res["adjusted_leverage_ratio"] == 2.0
        assert res["solvency_status"] == "HEALTHY_REGULATED_LEVERAGE"
        assert res["standard_interest_coverage"] == 26.0
        assert res["adjusted_interest_coverage"] == 8.12

        flags = res["regulatory_debt_burden_flags"]
        assert any("DEFERRED_SPECTRUM_OVERHANG" in f for f in flags)
        assert any("HIDDEN_REGULATORY_LEVERAGE_EXPANSION" in f for f in flags)

    def test_clean_firm_unaffected_by_regulatory_solvency(self):
        """Validates that a non-regulated firm with zero regulatory obligations remains clean."""
        res = RegulatoryAndSovereignSolvencyScorer.calculate_adjusted_solvency(
            symbol="TCS",
            ebitda_cr=30000.0,
            financial_debt_cr=0.0,
            cash_and_equivalents_cr=12000.0,
            deferred_spectrum_liabilities_cr=0.0,
            lease_liabilities_cr=0.0,
            sector="IT_SERVICES",
        )

        assert res["standard_net_debt_cr"] == -12000.0
        assert res["adjusted_net_debt_cr"] == -12000.0
        assert res["standard_leverage_ratio"] == -0.4
        assert res["adjusted_leverage_ratio"] == -0.4
        assert res["solvency_status"] == "PRISTINE_SOLVENCY"
        assert len(res["regulatory_debt_burden_flags"]) == 0

    def test_cash_tax_shield_runway_cliff_detection(self):
        """Validates detection of expiring accelerated depreciation tax shields (Jio-like parameters)."""
        res = CashTaxShieldRunwayScorer.evaluate_tax_shield_runway(
            symbol="JIO",
            unabsorbed_tax_depreciation_cr=17400.0,
            annual_accelerated_depreciation_claimed_cr=5000.0,
            annual_pbt_cr=30000.0,
            annual_fcf_cr=35000.0,
            statutory_tax_rate_pct=25.17,
            current_cash_tax_paid_cr=0.0,
        )

        assert res["tax_shield_runway_years"] == 3.48
        assert res["runway_classification"] == "MEDIUM_RUNWAY_MONITOR_EXPIRATION"
        assert res["projected_statutory_cash_tax_cr"] == 7551.0
        assert res["incremental_cash_tax_drag_cr"] == 7551.0
        assert res["cash_tax_drag_pct_of_fcf"] == 21.6

        flags = res["warning_flags"]
        assert len(flags) == 1
        assert "TAX_SHIELD_CLIFF_ALERT" in flags[0]
        assert "3.5 years" in flags[0]
        assert "21.6% of annual FCF" in flags[0]

    def test_secure_long_runway_tax_shield(self):
        """Validates that firms with ample tax shields (>6 years) receive secure status with zero alerts."""
        res = CashTaxShieldRunwayScorer.evaluate_tax_shield_runway(
            symbol="GREEN_CAPEX",
            unabsorbed_tax_depreciation_cr=80000.0,
            annual_accelerated_depreciation_claimed_cr=8000.0,
            annual_pbt_cr=10000.0,
            annual_fcf_cr=15000.0,
        )

        assert res["tax_shield_runway_years"] == 10.0
        assert res["runway_classification"] == "LONG_RUNWAY_SECURE_TAX_SHIELD"
        assert res["risk_level"] == "LOW"
        assert len(res["warning_flags"]) == 0

    def test_imminent_tax_cliff_detection(self):
        """Validates critical alert for companies with <1 year tax shield remaining."""
        res = CashTaxShieldRunwayScorer.evaluate_tax_shield_runway(
            symbol="EXHAUSTED_TAX_SHIELD",
            unabsorbed_tax_depreciation_cr=800.0,
            annual_accelerated_depreciation_claimed_cr=2000.0,
            annual_pbt_cr=5000.0,
            annual_fcf_cr=4000.0,
        )

        assert res["tax_shield_runway_years"] == 0.4
        assert res["runway_classification"] == "IMMINENT_TAX_CLIFF_FCF_CONTRACTION"
        assert res["risk_level"] == "CRITICAL"
        assert len(res["warning_flags"]) == 1
        assert "TAX_SHIELD_CLIFF_ALERT" in res["warning_flags"][0]
