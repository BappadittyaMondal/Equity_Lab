"""IPO Intelligence Engine — NSE/BSE Listing Gain Probability & Unlisted Pipeline.

Mathematical Formulation:
    P(Gain) = w1 * S_QIB + w2 * GMP_% + w3 * Delta_Val + w4 * M_trend + w5 * I_structure

Where:
    w1 = 0.35 : QIB Subscription Multiplier (institutional demand discovery)
    w2 = 0.30 : Grey Market Premium (GMP) relative to upper band
    w3 = 0.15 : Valuation discount / headroom vs listed sector peers
    w4 = 0.10 : Broader market regime multiplier (Nifty trend / VIX)
    w5 = 0.10 : Issue structure score (Fresh Issue vs OFS, Anchor Lock-in, Promoter Retention)
"""

import math
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class IPOSubscriptionData(BaseModel):
    """Subscription bidding multiples across categories."""
    qib_multiple: float = Field(0.0, ge=0.0, description="Qualified Institutional Buyers subscription multiple (x)")
    nii_multiple: float = Field(0.0, ge=0.0, description="Non-Institutional Investors / HNI subscription multiple (x)")
    rii_multiple: float = Field(0.0, ge=0.0, description="Retail Individual Investors subscription multiple (x)")
    total_multiple: float = Field(0.0, ge=0.0, description="Overall book subscription multiple (x)")


class IPOIssueStructure(BaseModel):
    """Capital structure and offer composition."""
    total_issue_size_cr: float = Field(..., gt=0.0, description="Total issue size in ₹ Cr")
    fresh_issue_cr: float = Field(0.0, ge=0.0, description="Fresh capital infusion into company in ₹ Cr")
    offer_for_sale_cr: float = Field(0.0, ge=0.0, description="OFS by existing promoters/PE investors in ₹ Cr")
    price_band_lower: float = Field(..., gt=0.0, description="Floor price in ₹")
    price_band_upper: float = Field(..., gt=0.0, description="Cap price in ₹")
    post_issue_promoter_holding_pct: float = Field(50.0, ge=0.0, le=100.0, description="Promoter equity holding % post-listing")
    anchor_lockin_days: int = Field(90, ge=0, description="Anchor investor lock-in duration (30 or 90 days)")


class IPOValuationMetrics(BaseModel):
    """Fundamental and relative valuation metrics."""
    implied_pe: Optional[float] = Field(None, description="P/E multiple at upper price band")
    peer_median_pe: Optional[float] = Field(None, description="Median trailing P/E of listed comparable peers")
    implied_pb: Optional[float] = Field(None, description="P/B multiple at upper price band")
    peer_median_pb: Optional[float] = Field(None, description="Median P/B of listed peers")
    roe_pct: Optional[float] = Field(None, description="Return on Equity % (latest FY)")
    pat_cagr_3y_pct: Optional[float] = Field(None, description="3-Year PAT CAGR %")


class IPOEvaluationInput(BaseModel):
    """Input payload for IPO Listing Gain analysis."""
    company_name: str
    symbol: Optional[str] = None
    sector: str = "GENERAL"
    gmp_inr: float = Field(0.0, description="Current Grey Market Premium in ₹")
    subscription: IPOSubscriptionData = Field(default_factory=IPOSubscriptionData)
    structure: IPOIssueStructure
    valuation: IPOValuationMetrics = Field(default_factory=IPOValuationMetrics)
    market_regime_favorable: bool = Field(True, description="Broader equity market uptrend (Nifty > 50EMA)")
    india_vix: float = Field(13.5, ge=0.0, description="Current India VIX level")


class IPOListingGainResult(BaseModel):
    """Output evaluation with listing gain probability and risk audit."""
    company_name: str
    symbol: Optional[str]
    sector: str
    listing_gain_probability: float = Field(..., ge=0.0, le=1.0, description="Calculated listing gain probability [0.0 - 1.0]")
    expected_listing_pop_pct: float = Field(..., description="Estimated % listing day gain over upper band")
    verdict: str = Field(..., description="Actionable IPO verdict")
    conviction_tier: str = Field(..., description="HIGH_CONVICTION, MODERATE_CONVICTION, SPECULATIVE, or AVOID")
    sub_scores: Dict[str, float] = Field(default_factory=dict, description="Component scores [0.0 - 1.0]")
    risk_flags: List[str] = Field(default_factory=list, description="Forensic and market risk cautions")
    methodology_note: str


# ── UNLISTED / PRE-IPO PIPELINE REGISTRY ──
UNLISTED_IPO_PIPELINE: List[Dict[str, Any]] = [
    {
        "company_name": "National Stock Exchange of India Ltd",
        "symbol": "NSE",
        "sector": "FINANCIAL_EXCHANGES",
        "status": "AWAITING_SEBI_APPROVAL",
        "expected_timeline": "Q3-Q4 FY27",
        "est_valuation_cr": 220000.0,
        "operating_margin_pct": 72.5,
        "roe_pct": 34.2,
        "unlisted_price_inr": 1785.0,
        "listing_gain_prob_baseline": 0.92,
        "investment_thesis": "Absolute domestic monopoly with >93% derivatives & >72% cash market share. Secular tailwind from financialization of Indian household savings.",
        "key_risk": "Regulatory fee caps and SEBI co-location legal clearances.",
    },
    {
        "company_name": "Tata Capital Ltd",
        "symbol": "TATACAP",
        "sector": "BFSI_NBFC",
        "status": "MANDATORY_RBI_SCALE_BASED_LISTING",
        "expected_timeline": "H2 FY27",
        "est_valuation_cr": 135000.0,
        "operating_margin_pct": 42.0,
        "roe_pct": 18.5,
        "unlisted_price_inr": 920.0,
        "listing_gain_prob_baseline": 0.90,
        "investment_thesis": "Diversified retail and corporate NBFC backed by Tata Sons brand halo. Low cost of funds and pristine asset quality (Gross NPA < 1.4%).",
        "key_risk": "Margin compression under high interest rate cycles.",
    },
    {
        "company_name": "HDB Financial Services Ltd",
        "symbol": "HDBFS",
        "sector": "BFSI_RETAIL_LENDING",
        "status": "DRHP_FILED",
        "expected_timeline": "Q3 FY27",
        "est_valuation_cr": 95000.0,
        "operating_margin_pct": 38.0,
        "roe_pct": 16.8,
        "unlisted_price_inr": 1150.0,
        "listing_gain_prob_baseline": 0.88,
        "investment_thesis": "HDFC Bank subsidiary (>94% promoter holding). Deep distribution with 1,600+ branches focusing on consumer and vehicle financing.",
        "key_risk": "Substantial OFS dilution from HDFC Bank to comply with RBI scale-based regulation.",
    },
    {
        "company_name": "National Securities Depository Ltd",
        "symbol": "NSDL",
        "sector": "FINANCIAL_DEPOSITORY",
        "status": "SEBI_APPROVED",
        "expected_timeline": "Q3 FY27",
        "est_valuation_cr": 24000.0,
        "operating_margin_pct": 61.0,
        "roe_pct": 22.4,
        "unlisted_price_inr": 850.0,
        "listing_gain_prob_baseline": 0.86,
        "investment_thesis": "Duopoly depository in India alongside listed CDSL. Dominates institutional demat accounts with sticky annuity fee income.",
        "key_risk": "100% OFS issue structure by IDBI Bank, NSE, and SBI (zero fresh capital infusion into NSDL).",
    },
    {
        "company_name": "Hero FinCorp Ltd",
        "symbol": "HEROFIN",
        "sector": "BFSI_VEHICLE_FINANCE",
        "status": "DRHP_FILED",
        "expected_timeline": "Q4 FY27",
        "est_valuation_cr": 28000.0,
        "operating_margin_pct": 29.5,
        "roe_pct": 14.2,
        "unlisted_price_inr": 1450.0,
        "listing_gain_prob_baseline": 0.74,
        "investment_thesis": "Two-wheeler financing capture of Hero MotoCorp ecosystem, expanding into SME and LAP loans.",
        "key_risk": "High credit cost sensitivity to rural economic downcycles.",
    },
    {
        "company_name": "Ather Energy Ltd",
        "symbol": "ATHER",
        "sector": "AUTOMOBILE_EV",
        "status": "DRHP_FILED",
        "expected_timeline": "Q4 FY27",
        "est_valuation_cr": 16000.0,
        "operating_margin_pct": -18.0,
        "roe_pct": -28.0,
        "unlisted_price_inr": 380.0,
        "listing_gain_prob_baseline": 0.55,
        "investment_thesis": "Top-tier premium electric two-wheeler OEM in India with proprietary battery pack and charging network.",
        "key_risk": "Persistent operating EBITDA losses, subsidy cuts (FAME/EMPS), and cut-throat pricing competition from Ola Electric & TVS.",
    },
]


class IPOIntelligenceEngine:
    """Quantitative evaluation engine for IPO listing gain probability and pre-IPO pipeline analysis."""

    @classmethod
    def evaluate_listing_gain(cls, inp: IPOEvaluationInput) -> IPOListingGainResult:
        """Computes the 5-factor mathematical listing gain probability model:

        P(Gain) = 0.35 * S_QIB + 0.30 * GMP_% + 0.15 * Delta_Val + 0.10 * M_trend + 0.10 * I_structure
        """
        risk_flags = []
        upper_price = max(inp.structure.price_band_upper, 1.0)

        # ── 1. Factor 1: QIB Subscription Score (Weight: 0.35) ──
        # QIB demand discovery is the single strongest institutional predictor of day-1 pops
        qib_x = inp.subscription.qib_multiple
        if qib_x <= 0.0:
            # If QIB has not yet bid (e.g. Day 1 morning), use a neutral baseline with a warning
            s_qib = 0.50
            risk_flags.append("QIB_BIDDING_UNOBSERVED: Subscription bidding still open or data pending.")
        else:
            # Logarithmic compression: 1x -> 0.18, 5x -> 0.46, 20x -> 0.77, 50x+ -> 1.0
            s_qib = min(1.0, max(0.0, math.log(1.0 + qib_x) / math.log(1.0 + 50.0)))
            if qib_x < 1.0:
                risk_flags.append(f"QIB_UNDERSUBSCRIBED: QIB book at {qib_x:.2f}x — severe institutional coldness.")

        # ── 2. Factor 2: Grey Market Premium (GMP %) Score (Weight: 0.30) ──
        # GMP % = (GMP / Upper Band)
        gmp_pct = inp.gmp_inr / upper_price
        # Map GMP: -20% -> 0.0, 0% -> 0.35, +30% -> 0.80, >= +50% -> 1.0
        if gmp_pct < 0.0:
            risk_flags.append(f"GMP_DISCOUNT_ALERT: Negative GMP of ₹{inp.gmp_inr:.1f} ({gmp_pct*100:.1f}%) signals high listing discount risk.")
            if gmp_pct <= -0.10:
                s_gmp = 0.0
            else:
                s_gmp = max(0.05, 0.20 + (gmp_pct + 0.10) * 1.5)  # 0.05 to 0.20
        elif gmp_pct <= 0.50:
            s_gmp = 0.35 + (gmp_pct / 0.50) * 0.55  # 0.35 to 0.90
        else:
            s_gmp = 0.90 + min(0.10, (gmp_pct - 0.50) * 0.20)  # up to 1.0

        if gmp_pct > 0.70:
            risk_flags.append("GMP_SPECULATIVE_FRENZY: GMP > 70% may reflect artificial circular street syndication.")

        # ── 3. Factor 3: Valuation Headroom vs Listed Peers (Weight: 0.15) ──
        implied_pe = inp.valuation.implied_pe
        peer_pe = inp.valuation.peer_median_pe

        if implied_pe is not None and peer_pe is not None and implied_pe > 0 and peer_pe > 0:
            discount_pct = (peer_pe - implied_pe) / peer_pe
            if discount_pct >= 0.25:
                # 25%+ discount to peers -> attractive headroom
                s_val = 1.0
            elif discount_pct >= 0.0:
                s_val = 0.60 + (discount_pct / 0.25) * 0.40  # 0.60 to 1.0
            elif discount_pct >= -0.30:
                # Up to 30% premium to peers -> demanding but survivable if high growth
                s_val = 0.30 + ((discount_pct + 0.30) / 0.30) * 0.30  # 0.30 to 0.60
                risk_flags.append(f"VALUATION_PREMIUM: Issue P/E ({implied_pe:.1f}x) at premium to peer median ({peer_pe:.1f}x).")
            else:
                # >30% premium -> severe overvaluation
                s_val = max(0.05, 0.30 + (discount_pct + 0.30) * 0.5)
                risk_flags.append(f"VALUATION_BUBBLE: Issue P/E ({implied_pe:.1f}x) > 30% above peers ({peer_pe:.1f}x).")
        else:
            # Valuation unobserved or loss-making
            if inp.valuation.roe_pct is not None and inp.valuation.roe_pct < 0:
                s_val = 0.30
                risk_flags.append("UNPROFITABLE_ISSUER: Loss-making company issuing equity at premium.")
            else:
                s_val = 0.50

        # ── 4. Factor 4: Market Trend & Volatility (Weight: 0.10) ──
        # IPOs listed in high VIX or falling markets frequently witness listing pop decay
        if inp.market_regime_favorable and inp.india_vix <= 16.0:
            s_mkt = 1.0
        elif inp.market_regime_favorable and inp.india_vix <= 22.0:
            s_mkt = 0.75
        elif not inp.market_regime_favorable and inp.india_vix <= 18.0:
            s_mkt = 0.45
            risk_flags.append("BROADER_MARKET_CORRECTION: Benchmark in downtrend; listing day sentiment fragile.")
        else:
            s_mkt = 0.20
            risk_flags.append(f"HIGH_VOLATILITY_HAZARD: India VIX elevated at {inp.india_vix:.1f}; high gap risk.")

        # ── 5. Factor 5: Issue Structure & Governance (Weight: 0.10) ──
        total_cr = inp.structure.total_issue_size_cr
        ofs_cr = inp.structure.offer_for_sale_cr
        fresh_cr = inp.structure.fresh_issue_cr
        ofs_ratio = ofs_cr / total_cr if total_cr > 0 else 0.0

        s_struct = 0.50
        if ofs_ratio > 0.80:
            s_struct -= 0.30
            risk_flags.append(f"OFS_DOMINANT_ISSUE: {ofs_ratio*100:.1f}% of issue is Offer For Sale (promoter cash-out; ₹0 into company).")
        elif fresh_cr / total_cr >= 0.60 if total_cr > 0 else False:
            s_struct += 0.25

        if inp.structure.post_issue_promoter_holding_pct < 30.0:
            s_struct -= 0.15
            risk_flags.append(f"LOW_PROMOTER_SKIN_IN_GAME: Post-issue promoter holding drops to {inp.structure.post_issue_promoter_holding_pct:.1f}%.")
        elif inp.structure.post_issue_promoter_holding_pct >= 55.0:
            s_struct += 0.15

        if inp.structure.anchor_lockin_days >= 90:
            s_struct += 0.10

        s_struct = min(1.0, max(0.05, s_struct))

        # ── COMPOSITE PROBABILITY CALCULATION ──
        prob = (
            0.35 * s_qib +
            0.30 * s_gmp +
            0.15 * s_val +
            0.10 * s_mkt +
            0.10 * s_struct
        )
        prob = round(min(0.99, max(0.01, prob)), 3)

        # Expected Listing Pop (%)
        # Anchor expected pop around GMP % with risk haircuts
        if gmp_pct > 0:
            expected_pop = round(gmp_pct * 100.0 * (0.65 + 0.35 * prob), 1)
        else:
            expected_pop = round(gmp_pct * 100.0 * (1.20 - 0.20 * prob), 1)

        # ── VERDICT & CONVICTION ──
        if prob >= 0.80:
            verdict = "STRONG_SUBSCRIBE_FOR_LISTING_GAIN"
            conviction_tier = "HIGH_CONVICTION"
        elif prob >= 0.65:
            verdict = "SUBSCRIBE_MODERATE_LISTING_GAIN"
            conviction_tier = "MODERATE_CONVICTION"
        elif prob >= 0.45:
            verdict = "LONG_TERM_SUBSCRIBE_ONLY_LISTING_GAIN_UNCERTAIN"
            conviction_tier = "SPECULATIVE"
        else:
            verdict = "AVOID_HIGH_LISTING_DISCOUNT_RISK"
            conviction_tier = "AVOID"

        sub_scores = {
            "qib_subscription_score": round(s_qib, 3),
            "gmp_premium_score": round(s_gmp, 3),
            "valuation_headroom_score": round(s_val, 3),
            "market_regime_score": round(s_mkt, 3),
            "issue_structure_score": round(s_struct, 3),
        }

        note = (
            f"Evaluated 5-Factor quantitative IPO listing model: QIB Demand ({s_qib:.2f}), "
            f"GMP ({s_gmp:.2f}, {gmp_pct*100:.1f}%), Valuation Headroom ({s_val:.2f}), "
            f"Macro/VIX ({s_mkt:.2f}), Issue Structure ({s_struct:.2f})."
        )

        return IPOListingGainResult(
            company_name=inp.company_name,
            symbol=inp.symbol,
            sector=inp.sector,
            listing_gain_probability=prob,
            expected_listing_pop_pct=expected_pop,
            verdict=verdict,
            conviction_tier=conviction_tier,
            sub_scores=sub_scores,
            risk_flags=risk_flags,
            methodology_note=note,
        )

    @classmethod
    def get_pipeline(cls) -> List[Dict[str, Any]]:
        """Returns the pre-IPO and unlisted Indian company pipeline."""
        return UNLISTED_IPO_PIPELINE
