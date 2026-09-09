"""Adversarial Absence-of-Evidence Hardening Verification Suite.

Asserts that all 9 audited modules strictly fail closed without fabricated defaults,
synthetic passes, or phantom scores when inputs or empirical filings are absent.
"""

import pytest
import pandas as pd
from app.services.strategies.saatvik_d18 import run_saatvik_d18
from app.services.strategies.reverse_dcf_c9 import run_reverse_dcf_c9
from app.services.strategies.alternative_data import evaluate_alternative_data
from app.services.strategies.moat_engine import evaluate_moat_score
from app.services.strategies.unit_economics import evaluate_unit_economics
from app.services.strategies.shareholding_pattern import evaluate_shareholding_pattern
from app.services.research.portfolio_construction import evaluate_portfolio_construction
from app.services.intelligence.financial_forensics import FinancialForensicsEngine
from app.services.strategies.mtf_context_engine import MTFContextEngine


def test_saatvik_d18_fails_closed_on_unobserved_data():
    """Verify D18 fails closed with DATA_INSUFFICIENT when financial hygiene cannot be verified."""
    res = run_saatvik_d18("ZZZ_INVALID")
    assert res.passed_gates is False
    assert res.status == "data_insufficient"
    assert res.results["ethical_gate_verdict"] == "REJECTED_INSUFFICIENT_DATA"
    assert res.results["data_status"] == "DATA_INSUFFICIENT"


def test_reverse_dcf_c9_fails_closed_on_missing_or_negative_pe():
    """Verify C9 returns mathematically undefined / data_insufficient when PE <= 0."""
    res = run_reverse_dcf_c9("ZZZ_INVALID")
    assert res.passed_gates is False
    assert res.status == "data_insufficient"
    assert res.metrics["implied_growth_rate_pct"] is None
    assert res.results["implied_10y_cagr"] == "N/A"
    assert "DATA_INSUFFICIENT" in res.results["market_expectations_verdict"]


def test_alternative_data_fails_closed_without_inputs():
    """Verify E19 does not fabricate EPFO growth or E-Way bills when no inputs provided."""
    res = evaluate_alternative_data("ZZZ_INVALID")
    assert res["status"] == "data_insufficient"
    assert res["alt_data_score"] is None
    assert res["external_confirmation_score"] == "LOW"
    assert res["alt_data_signal"] is None


def test_moat_engine_fails_closed_without_inputs_or_fundamentals():
    """Verify E7 does not assign artificial NARROW_MOAT when inputs are absent."""
    res = evaluate_moat_score("ZZZ_INVALID")
    assert res["status"] == "data_insufficient"
    assert res["moat_score"] is None
    assert res["moat_classification"] == "UNASSESSED"


def test_unit_economics_fails_closed_without_data():
    """Verify E8 does not fabricate capacity utilization or NRR when data is absent."""
    res = evaluate_unit_economics("ZZZ_INVALID")
    assert res["status"] == "data_insufficient"
    assert res["unit_economics_score"] is None
    assert res["unit_trend"] == "UNASSESSED"


def test_shareholding_pattern_fails_closed_without_data():
    """Verify E9 does not fabricate FII/DII accumulation streaks when unobserved."""
    res = evaluate_shareholding_pattern("ZZZ_INVALID")
    assert res["status"] == "data_insufficient"
    assert res["institutional_flow_score"] is None
    assert res["pattern_intelligence"] is None


def test_portfolio_construction_fails_closed_without_conviction():
    """Verify sizing engine never allocates capital (0.0 pct) when conviction is unobserved."""
    res = evaluate_portfolio_construction("ZZZ_INVALID")
    assert res["status"] == "data_insufficient"
    assert res["recommended_position_pct"] == 0.0
    assert res["portfolio_signal"] is None


def test_financial_forensics_fails_closed_on_empty_financials():
    """Verify forensics engine marks risk as DATA_UNAVAILABLE rather than CLEAN when empty."""
    res = FinancialForensicsEngine.analyze_company_forensics(None)
    assert res["forensic_risk_level"] == "DATA_UNAVAILABLE"
    assert res["cwip_analysis"]["capacity_expansion_signal"] == "DATA_UNAVAILABLE"
    assert res["cash_pat_divergence"]["forensic_risk_severity"] == "DATA_UNAVAILABLE"


def test_mtf_weekly_tide_fails_closed_on_insufficient_bars():
    """Verify MTF context engine does not default to bullish macro tide when bars < 15."""
    res_none = MTFContextEngine.calculate_weekly_tide(None)
    assert res_none["is_bullish_tide"] is False
    assert res_none["is_bearish_tide"] is False
    assert res_none["confidence"] == 0.0
    assert res_none["tide_state"] == "NEUTRAL_INSUFFICIENT_DATA"

    short_df = pd.DataFrame({"close": [100.0, 101.0, 102.0]})
    res_short = MTFContextEngine.calculate_weekly_tide(short_df)
    assert res_short["is_bullish_tide"] is False
    assert res_short["confidence"] == 0.0
