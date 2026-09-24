"""Test suite for Phase 143: IPO Intelligence Engine & NSE Listing Gain Probability."""

import pytest
from app.services.research.ipo_intelligence_engine import (
    IPOIntelligenceEngine,
    IPOEvaluationInput,
    IPOSubscriptionData,
    IPOIssueStructure,
    IPOValuationMetrics,
)


def test_high_demand_listing_gain_model():
    """Test attractive IPO with strong QIB, high GMP, fresh capex, and fair valuation."""
    inp = IPOEvaluationInput(
        company_name="Alpha Tech Solutions Ltd",
        symbol="ALPHATECH",
        sector="TECHNOLOGY",
        gmp_inr=150.0,
        subscription=IPOSubscriptionData(
            qib_multiple=45.0,
            nii_multiple=30.0,
            rii_multiple=12.0,
            total_multiple=32.0,
        ),
        structure=IPOIssueStructure(
            total_issue_size_cr=1200.0,
            fresh_issue_cr=900.0,  # 75% fresh issue
            offer_for_sale_cr=300.0,
            price_band_lower=380.0,
            price_band_upper=400.0,
            post_issue_promoter_holding_pct=62.0,
            anchor_lockin_days=90,
        ),
        valuation=IPOValuationMetrics(
            implied_pe=28.0,
            peer_median_pe=38.0,  # ~26% valuation discount
            implied_pb=4.5,
            peer_median_pb=6.0,
            roe_pct=22.5,
            pat_cagr_3y_pct=35.0,
        ),
        market_regime_favorable=True,
        india_vix=12.8,
    )

    res = IPOIntelligenceEngine.evaluate_listing_gain(inp)

    assert res.listing_gain_probability >= 0.80
    assert res.expected_listing_pop_pct > 25.0
    assert res.verdict == "STRONG_SUBSCRIBE_FOR_LISTING_GAIN"
    assert res.conviction_tier == "HIGH_CONVICTION"
    assert res.sub_scores["qib_subscription_score"] > 0.90
    assert res.sub_scores["valuation_headroom_score"] >= 0.95
    assert len(res.risk_flags) == 0


def test_weak_ofs_heavy_ipo_avoid():
    """Test weak IPO with undersubscribed QIB, negative GMP, 90% OFS, and valuation bubble."""
    inp = IPOEvaluationInput(
        company_name="Legacy Promoter Cashout Ltd",
        symbol="LEGCASH",
        sector="RETAIL",
        gmp_inr=-25.0,  # Negative GMP
        subscription=IPOSubscriptionData(
            qib_multiple=0.65,  # Undersubscribed
            nii_multiple=0.40,
            rii_multiple=0.90,
            total_multiple=0.72,
        ),
        structure=IPOIssueStructure(
            total_issue_size_cr=2500.0,
            fresh_issue_cr=250.0,
            offer_for_sale_cr=2250.0,  # 90% OFS
            price_band_lower=480.0,
            price_band_upper=500.0,
            post_issue_promoter_holding_pct=24.0,  # Low promoter skin in game
            anchor_lockin_days=30,
        ),
        valuation=IPOValuationMetrics(
            implied_pe=65.0,
            peer_median_pe=32.0,  # Bubble valuation (>100% premium)
            roe_pct=8.5,
        ),
        market_regime_favorable=False,
        india_vix=21.5,
    )

    res = IPOIntelligenceEngine.evaluate_listing_gain(inp)

    assert res.listing_gain_probability < 0.40
    assert res.expected_listing_pop_pct < 0.0
    assert res.verdict == "AVOID_HIGH_LISTING_DISCOUNT_RISK"
    assert res.conviction_tier == "AVOID"
    assert any("OFS_DOMINANT" in flag for flag in res.risk_flags)
    assert any("QIB_UNDERSUBSCRIBED" in flag for flag in res.risk_flags)
    assert any("GMP_DISCOUNT_ALERT" in flag for flag in res.risk_flags)
    assert any("VALUATION_BUBBLE" in flag for flag in res.risk_flags)


def test_unlisted_ipo_pipeline_registry():
    """Test that pre-IPO / unlisted registry returns institutional candidates."""
    pipeline = IPOIntelligenceEngine.get_pipeline()
    assert len(pipeline) >= 6
    symbols = {item["symbol"] for item in pipeline}
    assert "NSE" in symbols
    assert "TATACAP" in symbols
    assert "HDBFS" in symbols
    assert "NSDL" in symbols
    assert "HEROFIN" in symbols
    assert "ATHER" in symbols

    nse = next(item for item in pipeline if item["symbol"] == "NSE")
    assert nse["operating_margin_pct"] > 70.0
    assert nse["listing_gain_prob_baseline"] >= 0.90
