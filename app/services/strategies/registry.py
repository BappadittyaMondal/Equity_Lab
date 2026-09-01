"""Strategy Module Registry.

Maintains metadata and execution routing for all 35 IERL Modules (18 Expert Strategy Modules A1–D18 + 17 Core Research Engines E1–E17).
Strictly distinguishes production modules from coming-soon modules.
"""

from datetime import datetime
from typing import Dict, List, Optional
from fastapi import HTTPException, status
from app.models.schemas import StrategyModule, StrategyRunResponse
from app.services.market_data import get_quote, create_meta_header, normalize_symbol, get_ist_now_str

from app.services.strategies.saatvik_d18 import run_saatvik_d18
from app.services.strategies.vcp_b5 import run_vcp_b5
from app.services.strategies.sepa_b8 import run_sepa_b8
from app.services.strategies.reverse_dcf_c9 import run_reverse_dcf_c9
from app.services.strategies.ath_breakout_d15 import run_ath_breakout_d15
# Phase 2 engines
from app.services.strategies.technical_engines import (
    run_vpa_b4, run_rs_rating_b6, run_pocket_pivot_b7, run_mean_reversion_d17
)
from app.services.strategies.forensic_engine import run_forensic_engine
from app.services.strategies.dcf_forward import run_dcf_forward
from app.services.strategies.options_a1_a3 import evaluate_option_arbitrage, evaluate_iron_condor
from app.services.strategies.owner_earnings_c10 import evaluate_owner_earnings
from app.services.strategies.dual_momentum_d16 import evaluate_dual_momentum

# Master Registry of 18 Expert Strategy Modules (A1–D18)
STRATEGY_MODULES: Dict[str, StrategyModule] = {
    "A1": StrategyModule(
        id="A1",
        name="Option Arbitrage & Calendar Spreads",
        category="Options Arbitrage",
        description="Exploits mispricings in option synthetic futures, calendar spreads, and implied volatility skews.",
        status="production",
        required_inputs=["underlying", "option_chain"],
        universe="NIFTY / BANKNIFTY F&O",
        metrics=["implied_volatility_skew", "put_call_parity_arbitrage", "theta_decay"],
        risk_warnings=["Early assignment risk on short option legs.", "Execution slippage on illiquid strikes."],
        methodology="Synthetic parity check across liquid Nifty option chain contracts."
    ),
    "A2": StrategyModule(
        id="A2",
        name="Zero-DTE Range Option Selling Engine",
        category="Options Arbitrage",
        description="Calculates probability density, expected value (EV), breakevens, and risk-controlled lot sizing for short strangles.",
        status="production",
        required_inputs=["underlying", "lower_strike", "upper_strike", "call_premium", "put_premium"],
        universe="NIFTY / BANKNIFTY 0-DTE",
        metrics=["probability_of_profit", "expected_value", "breakeven_points", "max_loss"],
        risk_warnings=["Unlimited loss potential on unhedged short options. Hard stop discipline mandatory."],
        methodology="Short strangle payoff model with spot-derived dynamic strikes, empirical volatility bounds, 15-point payoff curve, margin estimation, and 2.5x stop-loss EV calculation."
    ),
    "A3": StrategyModule(
        id="A3",
        name="Iron Condor Volatility Premium Capture",
        category="Options Arbitrage",
        description="Defined-risk option spread capture using long wing hedges.",
        status="production",
        required_inputs=["underlying", "strikes", "premiums"],
        universe="NSE F&O Index Options",
        metrics=["max_profit", "max_risk", "probability_of_profit"],
        risk_warnings=["Wing gap risk during overnight gaps."],
        methodology="4-leg defined risk spread calculation."
    ),
    "B4": StrategyModule(
        id="B4",
        name="Volume Price Analysis (VPA) Liquidity Spike",
        category="Techno-Fundamental",
        description="Detects institutional accumulation via volume expansion on narrow price spread bars.",
        status="production",
        required_inputs=["symbol", "period"],
        universe="NSE 500",
        metrics=["volume_z_score", "price_spread_ratio"],
        risk_warnings=["False accumulation signals during market distribution."],
        methodology="Volume spread analysis algorithm."
    ),
    "B5": StrategyModule(
        id="B5",
        name="VCP Pattern Breakout Screen",
        category="Techno-Fundamental",
        description="Volatility Contraction Pattern scanner based on Mark Minervini principles.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE 500",
        metrics=["range_20d_pct", "range_50d_pct", "distance_from_52w_high"],
        risk_warnings=["Volume confirmation required on breakout day."],
        methodology="Multi-stage range contraction measurement and 150d/200d trend template."
    ),
    "B6": StrategyModule(
        id="B6",
        name="Relative Strength RS Rating Screening",
        category="Techno-Fundamental",
        description="Calculates 12-month weighted relative price strength vs Nifty 50 benchmark.",
        status="production",
        required_inputs=["symbol", "benchmark"],
        universe="NSE 500",
        metrics=["rs_rating_0_99", "weighted_momentum"],
        risk_warnings=["Past relative strength may deteriorate during sector rotations."],
        methodology="Quarterly weighted price return ranking against NSE broad index."
    ),
    "B7": StrategyModule(
        id="B7",
        name="Pocket Pivot Volume Accumulation",
        category="Techno-Fundamental",
        description="Identifies early institutional entry before base breakout.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE 500",
        metrics=["pocket_pivot_volume", "10d_down_volume_max"],
        risk_warnings=["Requires strong base formation."],
        methodology="Gil Morales pocket pivot volume test."
    ),
    "B8": StrategyModule(
        id="B8",
        name="SEPA Fundamental Growth Screening",
        category="Techno-Fundamental",
        description="Specific Earnings Performance Appraisal screening for superperformance stock candidates.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE 500",
        metrics=["one_year_momentum_pct", "pe_ratio"],
        risk_warnings=["High momentum stocks can experience sharp drawdowns."],
        methodology="Earnings momentum and trend template screening."
    ),
    "C9": StrategyModule(
        id="C9",
        name="Reverse DCF Intrinsic Growth Check",
        category="Fundamental Valuation",
        description="Calculates market-implied growth rate embedded in current P/E multiple.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["implied_growth_rate_pct", "pe_ratio"],
        risk_warnings=["High sensitivity to discount rate assumption."],
        methodology="Reverse Gordon Growth and discounted cash flow model."
    ),
    "C10": StrategyModule(
        id="C10",
        name="Owner Earnings & Free Cash Flow Yield",
        category="Fundamental Valuation",
        description="Warren Buffett owner earnings calculation (Net Income + D&A - Maintenance CapEx).",
        status="production",
        required_inputs=["symbol"],
        universe="NSE 500",
        metrics=["fcf_yield_pct", "owner_earnings_inr"],
        risk_warnings=["Maintenance CapEx estimation involves accounting judgements."],
        methodology="Owner earnings yield relative to enterprise value."
    ),
    "C11": StrategyModule(
        id="C11",
        name="Piotroski F-Score Financial Health Check",
        category="Fundamental Valuation",
        description="9-point accounting health checklist measuring profitability, leverage, and operating efficiency.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["f_score_0_9", "cfo_pat_ratio"],
        risk_warnings=["Financial stocks require modified F-score criteria."],
        methodology="9-point binary scoring system on YoY balance sheet changes."
    ),
    "C12": StrategyModule(
        id="C12",
        name="Altman Z-Score Distress Warning Engine",
        category="Fundamental Valuation",
        description="Predicts corporate insolvency risk using 5 financial balance sheet ratios.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE Non-Financials",
        metrics=["z_score", "distress_zone"],
        risk_warnings=["Not applicable to banks or financial institutions."],
        methodology="Altman Z-score formula for emerging market corporate distress."
    ),
    "C13": StrategyModule(
        id="C13",
        name="Beneish M-Score Forensic Earnings Manipulation",
        category="Forensic Hygiene",
        description="8-parameter forensic model detecting potential financial statement manipulation and governance hygiene.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["m_score", "manipulation_flag", "governance_grade"],
        risk_warnings=["High M-score indicates statistical anomaly, not legal conviction."],
        methodology="8-variable probit regression model and promoter pledge/governance hygiene rules."
    ),
    "C14": StrategyModule(
        id="C14",
        name="Turnaround & NCLT Revival Diagnostic",
        category="Forensic Hygiene",
        description="Screens for balance sheet debt deleveraging and operational revival in distressed companies.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE Distressed / Smallcap",
        metrics=["debt_reduction_yoy", "operating_margin_turnaround"],
        risk_warnings=["High risk of equity dilution or total capital loss."],
        methodology="Deleveraging trajectory and positive operating cash flow turnaround test."
    ),
    "D15": StrategyModule(
        id="D15",
        name="All-Time High Profit Breakout",
        category="Momentum & Quantitative",
        description="Quant momentum screen targeting stocks trading within 3% of 52-week or all-time high.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE 500",
        metrics=["distance_pct", "fifty_two_week_high"],
        risk_warnings=["Requires stop-loss discipline against false breakouts."],
        methodology="52-week high breakout proximity and trend confirmation."
    ),
    "D16": StrategyModule(
        id="D16",
        name="Dual Momentum Trend Following",
        category="Momentum & Quantitative",
        description="Gary Antonacci dual momentum combining absolute and relative price momentum.",
        status="production",
        required_inputs=["symbol", "benchmark"],
        universe="NSE Sector Indices / Stocks",
        metrics=["absolute_momentum_lookback", "relative_momentum_rank"],
        risk_warnings=["Whipsaw risk in choppy sideways markets."],
        methodology="12-month lookback dual momentum filter."
    ),
    "D17": StrategyModule(
        id="D17",
        name="Mean Reversion Bollinger Band Squeeze",
        category="Momentum & Quantitative",
        description="Short-term mean reversion screen when price touches 2-std band during low volatility squeeze.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE Liquid Equities",
        metrics=["bollinger_bandwidth", "z_score_price"],
        risk_warnings=["Do not trade mean reversion against strong macro trends."],
        methodology="Standard deviation band envelope and bandwidth squeeze test."
    ),
    "D18": StrategyModule(
        id="D18",
        name="Ethical Governance & Business Activity Screening Gate",
        category="Forensic Hygiene",
        description="Filters stocks based on ethical governance, non-sin activities (alcohol, tobacco, gambling, weapons, predatory lending), and debt balance.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["sin_business_activity_flag", "pe_sanity_check"],
        risk_warnings=["Ethical screening filters out prohibited business categories."],
        methodology="Business activity sector exclusion and financial sanity gate."
    )
}

# Core Research Engines
RESEARCH_ENGINES: Dict[str, StrategyModule] = {
    "E1": StrategyModule(
        id="E1",
        name="Growth Inflection Engine",
        category="Early Multibagger Intelligence",
        description="Detects revenue, profit, EPS, margin, ROCE, and FCF growth acceleration prior to market recognition.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["growth_inflection_score", "revenue_acceleration", "operating_leverage", "fcf_inflection"],
        risk_warnings=["Requires point-in-time financial observation history."],
        methodology="Multi-metric sequential acceleration calculation across point-in-time financial observations."
    ),
    "E2": StrategyModule(
        id="E2",
        name="Turnaround Stage Engine",
        category="Early Multibagger Intelligence",
        description="Classifies turnaround lifecycle (Distress -> Recovery) and detects False Turnaround traps.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["turnaround_score", "current_stage", "success_probability_pct", "false_turnaround_risk"],
        risk_warnings=["High risk of equity dilution or false recovery if cash flow is negative."],
        methodology="7-stage lifecycle diagnostic and accounting accrual sanity rules."
    ),
    "E3": StrategyModule(
        id="E3",
        name="Growth vs Market Recognition Gap Engine",
        category="Early Multibagger Intelligence",
        description="Compares fundamental CAGR (Sales, PAT, EPS, FCF) vs Stock Price CAGR to identify valuation arbitrage.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["business_growth_score", "market_recognition_score", "growth_recognition_gap", "potential_rerating_score"],
        risk_warnings=["Historical CAGR gap may persist if sector fundamentals deteriorate."],
        methodology="Fundamental vs price CAGR spread and valuation re-rating potential model."
    ),
    "E4": StrategyModule(
        id="E4",
        name="Multi-Factor Multibagger Intelligence Screener",
        category="Early Multibagger Intelligence",
        description="Combines Growth Inflection, Turnaround Stage, Growth Gap, Governance Quality, and Ethical Screening into composite Multibagger Score.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["multibagger_score", "conviction_category", "key_drivers", "key_risks"],
        risk_warnings=["High score indicates high fundamental catalyst alignment, not guaranteed return."],
        methodology="Multi-factor weighted composite scoring model across fundamental research engines."
    ),
    "E5": StrategyModule(
        id="E5",
        name="AI Growth Arbitrage & DCF Valuation Engine (Institutional Grade)",
        category="Early Multibagger Intelligence",
        description="Calculates Intrinsic DCF Value, Reverse DCF Implied Growth, Growth Arbitrage Gap, and Multi-Horizon Return Probabilities (6M, 1Y, 2Y, 5Y).",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["growth_arbitrage_gap", "intrinsic_value_dcf", "composite_score", "risk_rating"],
        risk_warnings=["Quantitative valuation model relies on published financial statement observation history."],
        methodology="10-pillar weighted composite score, reverse DCF implied growth gap, and non-parametric multi-horizon return probability bands."
    ),
    "E6": StrategyModule(
        id="E6",
        name="Quality-Growth Candidate Screener (Pre-Filter)",
        category="Universe Compounder Pre-Filter",
        description="Screens investment universe against 28 quantitative and fundamental quality-growth conditions before passing candidates to the Arbiter.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["total_conditions", "conditions_passed", "conditions_failed", "conditions_unavailable"],
        risk_warnings=["Pre-filter screening only — does NOT generate final BUY recommendation."],
        methodology="28-condition quantitative and fundamental threshold screen with condition-level audit trail."
    ),
    "E7": StrategyModule(
        id="E7",
        name="Expectation Gap Engine",
        category="Fundamental Valuation",
        description="Quantifies the Expectation Gap between Reverse DCF market-implied growth expectations and fundamental internal forecast growth.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["market_implied_growth", "internal_forecast_growth", "expectation_gap", "gap_classification"],
        risk_warnings=["High expectation gap requires operational execution to materialize as stock re-rating."],
        methodology="Subtracts Reverse DCF market-implied growth rate from empirical blended internal forecast growth rate."
    ),
    "E8": StrategyModule(
        id="E8",
        name="Moat Strength & Unit Economics Engine",
        category="Early Multibagger Intelligence",
        description="Evaluates competitive advantage moat trajectory and sector-conditional unit economics (NIM, CASA, Capacity Utilization, Realization/Unit).",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["moat_score", "moat_classification", "moat_trajectory", "unit_economics_score", "unit_trend"],
        risk_warnings=["Qualitative moat dimensions require periodic management commentary verification."],
        methodology="6-variable competitive advantage rubric combined with sector-conditional unit economics model."
    ),
    "E9": StrategyModule(
        id="E9",
        name="Promoter & Insider Behaviour Engine",
        category="Governance & Forensics",
        description="Evaluates promoter skin-in-the-game, SAST disclosures, pledge trends, bulk deals, ESOPs, and buying into price weakness.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["insider_conviction_score", "hard_gate_status", "promoter_pledge_pct"],
        risk_warnings=["Requires verified BSE/NSE SAST disclosures."],
        methodology="Promoter transaction weighting, pledge trajectory, and consolidated governance checklist."
    ),
    "E10": StrategyModule(
        id="E10",
        name="Shareholding-Pattern Intelligence Engine",
        category="Institutional Flows",
        description="Tracks FII/DII accumulation streaks, retail holding trend, free-float index catalysts, and concentration risk.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["institutional_flow_score", "accumulation_quarters", "index_catalyst"],
        risk_warnings=["Quarterly shareholding filings have up to 21-day reporting lag."],
        methodology="Multi-quarter institutional accumulation tracking and free-float market cap threshold model."
    ),
    "E11": StrategyModule(
        id="E11",
        name="Primary Research Scuttlebutt & Indian Alt-Data Engine",
        category="Alternative Data & Intel",
        description="Processes GST e-way bills, EPFO payrolls, Vahan registrations, UPI data, DGCI&S trade data, and scuttlebutt channel checks.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["alt_data_score", "external_confirmation_score"],
        risk_warnings=["Requires independent cross-verification of channel check reports."],
        methodology="Indian macro/alt-data signal fusion and Philip Fisher scuttlebutt evaluation."
    ),
    "E12": StrategyModule(
        id="E12",
        name="Management Commentary & Concall NLP Engine",
        category="Qualitative Intelligence",
        description="Evaluates concall management tone shifts, guidance specificity, language consistency across quarters, and Q&A deflection.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["commentary_confidence_score", "tone_shift_direction"],
        risk_warnings=["NLP sentiment scores must be validated against actual financial results."],
        methodology="Transcript tone extraction, guidance specificity index, and deflection detection algorithm."
    ),
    "E13": StrategyModule(
        id="E13",
        name="Regulatory Catalysts & Corporate Actions Engine",
        category="Catalyst Intelligence",
        description="Tracks PLI schemes, customs tariffs, PSU catalysts, buyback pricing vs intrinsic value, QIP dilution, and credit rating actions.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["catalyst_score", "catalyst_timing_horizon"],
        risk_warnings=["Government policy timelines are subject to regulatory delays."],
        methodology="Policy impact matrix, accretive buyback formula, and credit rating agency momentum model."
    ),
    "E14": StrategyModule(
        id="E14",
        name="Portfolio Position Sizing & Exit Discipline Engine",
        category="Portfolio Management",
        description="Calculates Fractional-Kelly position weight, ADTV liquidity caps, archetype scaling ladders, and drawdown tolerance bands.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["recommended_position_pct", "drawdown_tolerance_band_pct"],
        risk_warnings=["Position sizing must respect overall portfolio risk constraints."],
        methodology="Quarter-Kelly formula, liquidity ADTV caps, scaling ladders, and archetype drawdown tolerance."
    ),
    "E15": StrategyModule(
        id="E15",
        name="Business-Model Peer Normalization Engine",
        category="Quantitative Benchmarking",
        description="Constructs unit-economics peer sets and converts raw fundamental scores into sector-relative z-scores and percentile ranks.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["sector_relative_percentile", "z_scores"],
        risk_warnings=["Requires valid sector distribution parameters."],
        methodology="Standard normal CDF transformation across 9 sector benchmark distributions."
    ),
    "E16": StrategyModule(
        id="E16",
        name="Analyst Behavioral-Bias & Red-Team Review Engine",
        category="Risk Governance",
        description="Enforces mandatory pre-mortem written bear cases, adversarial red-team reviews, price-action re-evaluation triggers, and Gate 7 bias check.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["gate_7_passed", "pre_mortem_failure_causes"],
        risk_warnings=["Analyst bias checks require honest pre-mortem scenario creation."],
        methodology="3-vector failure pre-mortem analysis, short-seller challenge simulation, and price drift triggers."
    ),
    "E17": StrategyModule(
        id="E17",
        name="Backtesting & Statistical Validation Framework Engine",
        category="Statistical Validation",
        description="Computes Walk-Forward out-of-sample backtests, Information Coefficients (IC) per factor, factor decay half-lives, and survivorship control.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["average_ic", "out_of_sample_sharpe", "factor_decay_half_life_months"],
        risk_warnings=["Historical IC performance does not guarantee future factor outperformance."],
        methodology="Spearman rank correlation, walk-forward out-of-sample validation, and point-in-time lag enforcement."
    ),
    "E18": StrategyModule(
        id="E18",
        name="10-30 Day Swing Predictive Engine",
        category="Technical & Volatility Intelligence",
        description="Calculates Volume Profile POC, Anchored VWAP, Choppiness Index, Balance of Power, and Multi-Timeframe Alignment.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["confluence_score", "predictive_bias", "volume_poc", "anchored_vwap", "choppiness_index"],
        risk_warnings=["Swing predictions are valid for 10-30 day trading horizons only."],
        methodology="6-pillar technical confluence scoring, volume profile POC, and regime-filtered momentum model."
    ),
    "E19": StrategyModule(
        id="E19",
        name="Multibagger Inflection Engine",
        category="Early Multibagger Intelligence",
        description="Evaluates volume Z-score (Z_Vol >= +3.0s), float delivery turnover (DTR >= 2.0%), earnings acceleration convexity, and PEG mispricing.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["z_score_vol", "dtr_5d_pct", "convexity_index_ce", "peg_ratio"],
        risk_warnings=["Inflection setups require volume persistence on breakout days."],
        methodology="Non-linear volume Z-score and quarterly earnings acceleration convexity model."
    ),
    "OBV_ACC": StrategyModule(
        id="OBV_ACC",
        name="OBV Slope Acceleration Convexity",
        category="Volume & Microstructure",
        description="Tracks corporate-action-adjusted cumulative OBV slope acceleration to detect stealth institutional accumulation.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["c_obv", "obv_convexity_score", "slope_12w", "slope_40w"],
        risk_warnings=["OBV signals require volume-weighted delivery confirmation."],
        methodology="Cumulative OBV slope acceleration detector across 12W vs 40W windows."
    ),
    "E20": StrategyModule(
        id="E20",
        name="Institutional Turnaround Prediction Engine",
        category="Turnaround & Fundamental Intelligence",
        description="Evaluates 2-layer fundamental recovery probability P_Recovery, relapse risk P_Relapse, cash flow truth, and FRMR expectation gap.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE All Equities",
        metrics=["turnaround_score", "p_recovery", "p_relapse", "value_trap_risk_score"],
        risk_warnings=["Turnaround candidates require multi-quarter cash flow confirmation."],
        methodology="2-layer probability model, historical damage detection, and fundamental recovery vs market repricing gap."
    ),
    "E21": StrategyModule(
        id="E21",
        name="Early-Stage ₹100Cr+ Microcap Compounder Engine",
        category="Microcap Incubator Intelligence",
        description="Incubates early-stage microcaps (₹100Cr–₹500Cr) evaluating Incremental ROIC (ΔNOPAT/ΔInvested Capital), Capex Productivity, Reverse Valuation Forensics, and PM Kill-Test.",
        status="production",
        required_inputs=["symbol"],
        universe="NSE ₹100Cr–₹500Cr Microcaps",
        metrics=["early_compounder_score", "incremental_roic_pct", "incubator_tier"],
        risk_warnings=["Micro-cap illiquidity and execution lag risks apply."],
        methodology="Sequential 3-agent pipeline: Agent 10 (Incremental ROIC) + Agent 11 (Reverse Valuation) + Agent 12 (PM Kill-Test)."
    )
}



def list_strategy_modules() -> List[StrategyModule]:
    """Returns list of all 35 master strategy modules & research engines with status."""
    from app.core.config import settings
    if not settings.ENABLE_OPTIONS_A2:
        STRATEGY_MODULES["A2"].status = "suspended"
    else:
        STRATEGY_MODULES["A2"].status = "production"
    return list(STRATEGY_MODULES.values()) + list(RESEARCH_ENGINES.values())


def get_strategy_module(strategy_id: str) -> StrategyModule:
    from app.core.config import settings
    if not settings.ENABLE_OPTIONS_A2:
        STRATEGY_MODULES["A2"].status = "suspended"
    else:
        STRATEGY_MODULES["A2"].status = "production"

    clean_id = strategy_id.upper().strip()
    if clean_id in STRATEGY_MODULES:
        return STRATEGY_MODULES[clean_id]
    if clean_id in RESEARCH_ENGINES:
        return RESEARCH_ENGINES[clean_id]
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Strategy module '{strategy_id}' not found. Valid IDs: {list(STRATEGY_MODULES.keys()) + list(RESEARCH_ENGINES.keys())}"
    )



def run_strategy_module(strategy_id: str, symbol: str = "RELIANCE", as_of: Optional[datetime] = None) -> StrategyRunResponse:

    module = get_strategy_module(strategy_id)
    
    if module.status != "production":
        # Explicit non-production status response
        norm_symbol = normalize_symbol(symbol)
        quote = get_quote(norm_symbol)
        retrieved = quote.get("meta", {}).get("retrieved_at") if isinstance(quote, dict) and isinstance(quote.get("meta"), dict) else getattr(getattr(quote, "meta", None), "retrieved_at", get_ist_now_str())
        return StrategyRunResponse(
            strategy_id=module.id,
            strategy_name=module.name,
            status="coming_soon",
            executed_at=retrieved,
            symbol=norm_symbol,
            passed_gates=False,
            results={
                "status_message": f"Module {module.id} ({module.name}) is currently under active development.",
                "notice": "Coming soon — not yet available in production engine.",
                "required_inputs": module.required_inputs
            },
            metrics={"status": "MODULE_NOT_YET_AVAILABLE"},
            risk_warnings=module.risk_warnings,
            disclaimer="Module under development.",
            meta=create_meta_header(source=f"IERL Strategy Registry ({module.id})")
        )

    # Route to production engine implementations
    if module.id == "E1":
        from app.services.strategies.growth_inflection import evaluate_growth_inflection
        res1 = evaluate_growth_inflection(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E1",
            strategy_name=module.name,
            status="production",
            executed_at=res1.executed_at,
            symbol=res1.symbol,
            passed_gates=(res1.growth_inflection_score >= 50.0),
            results={
                "stage": res1.stage,
                "heuristic_confidence": res1.heuristic_confidence,
                "evidence": res1.evidence
            },
            metrics=res1.metrics_summary,
            risk_warnings=module.risk_warnings,
            disclaimer="Growth Inflection Engine assessment.",
            meta=res1.meta
        )
    elif module.id in ["E2", "C14"]:
        from app.services.strategies.turnaround_stage import evaluate_turnaround_stage
        res2 = evaluate_turnaround_stage(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id=module.id,
            strategy_name=module.name,
            status="production",
            executed_at=res2.executed_at,
            symbol=res2.symbol,
            passed_gates=(res2.false_turnaround_risk in ["LOW", "MODERATE"]),
            results={
                "current_stage": res2.current_stage,
                "success_probability_pct": res2.success_probability_pct,
                "false_turnaround_risk": res2.false_turnaround_risk,
                "evidence": res2.evidence
            },
            metrics=res2.metrics_summary,
            risk_warnings=module.risk_warnings,
            disclaimer="Turnaround Stage Engine assessment.",
            meta=res2.meta
        )
    elif module.id == "E3":
        from app.services.strategies.growth_market_gap import evaluate_growth_market_gap
        res3 = evaluate_growth_market_gap(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E3",
            strategy_name=module.name,
            status="production",
            executed_at=res3.executed_at,
            symbol=res3.symbol,
            passed_gates=(res3.gap_classification in ["HIGH_ARBITRAGE", "BALANCED"]),
            results={
                "growth_recognition_gap": res3.growth_recognition_gap,
                "gap_classification": res3.gap_classification,
                "evidence": res3.evidence
            },
            metrics=res3.cagr_comparison,
            risk_warnings=module.risk_warnings,
            disclaimer="Growth vs Market Recognition Gap Engine assessment.",
            meta=res3.meta
        )
    elif module.id == "E4":
        from app.services.strategies.multibagger_screener import evaluate_multibagger_score
        res4 = evaluate_multibagger_score(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E4",
            strategy_name=module.name,
            status="production",
            executed_at=res4.executed_at,
            symbol=res4.symbol,
            passed_gates=(res4.conviction_category in ["HIGH_CONVICTION_EARLY_MULTIBAGGER", "HIGH_GROWTH_REVALUATION_CANDIDATE", "SPECULATIVE_TURNAROUND"]),
            results={
                "multibagger_score": res4.multibagger_score,
                "conviction_category": res4.conviction_category,
                "key_drivers": res4.key_drivers,
                "key_risks": res4.key_risks
            },
            metrics=res4.component_scores,
            risk_warnings=module.risk_warnings,
            disclaimer="Multi-Factor Multibagger Intelligence Screener assessment.",
            meta=res4.meta
        )
    elif module.id == "E5":
        from app.services.strategies.growth_arbitrage import evaluate_growth_arbitrage
        res5 = evaluate_growth_arbitrage(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E5",
            strategy_name=module.name,
            status="production",
            executed_at=res5.executed_at,
            symbol=res5.symbol,
            passed_gates=(res5.recommendation in ["STRONG_BUY", "BUY", "ACCUMULATE"]),
            results={
                "growth_arbitrage_gap": res5.growth_arbitrage_gap,
                "intrinsic_value_dcf": res5.intrinsic_value_dcf,
                "composite_score": res5.composite_score,
                "recommendation": res5.recommendation,
                "risk_rating": res5.risk_rating,
                "key_drivers": res5.key_drivers,
                "key_risks": res5.key_risks
            },
            metrics={
                "current_price": res5.current_price,
                "pe_ratio": res5.pe_ratio,
                "expected_growth_rate": res5.expected_growth_rate,
                "market_implied_growth": res5.market_implied_growth,
                "composite_score": res5.composite_score
            },
            risk_warnings=module.risk_warnings,
            disclaimer=res5.disclaimer,
            meta=res5.meta
        )
    elif module.id == "E6":
        from app.services.strategies.quality_growth_screener import run_quality_growth_screener
        res6 = run_quality_growth_screener(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E6",
            strategy_name=module.name,
            status="production",
            executed_at=res6.meta.retrieved_at,
            symbol=res6.symbol,
            passed_gates=(res6.screening_status == "PASS"),
            results={
                "screening_status": res6.screening_status,
                "total_conditions": res6.total_conditions,
                "conditions_passed": res6.conditions_passed,
                "conditions_failed": res6.conditions_failed,
                "conditions_unavailable": res6.conditions_unavailable,
                "quality_growth_profile": res6.quality_growth_profile
            },
            metrics={
                "passed_pct": (res6.conditions_passed / res6.total_conditions * 100.0) if res6.total_conditions > 0 else 0.0,
                "failed_pct": (res6.conditions_failed / res6.total_conditions * 100.0) if res6.total_conditions > 0 else 0.0
            },
            risk_warnings=module.risk_warnings,
            disclaimer="Quality-Growth Candidate Screener pre-filter assessment.",
            meta=res6.meta
        )
    elif module.id == "E7":
        from app.services.strategies.expectation_gap import run_expectation_gap_engine
        res7 = run_expectation_gap_engine(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E7",
            strategy_name=module.name,
            status="production" if not res7.data_insufficient else "data_insufficient",
            executed_at=res7.meta.retrieved_at if hasattr(res7, "meta") and hasattr(res7.meta, "retrieved_at") else get_ist_now_str(),
            symbol=res7.symbol if hasattr(res7, "symbol") else normalize_symbol(symbol),
            passed_gates=(res7.gap_classification in ["POSITIVE_EXPECTATION_GAP", "BALANCED_EXPECTATION"]),
            results={
                "expectation_gap": res7.expectation_gap,
                "gap_classification": res7.gap_classification,
                "heuristic_confidence": res7.heuristic_confidence,
                "evidence": res7.evidence
            },
            metrics={
                "market_implied_growth": res7.market_implied_growth,
                "internal_forecast_growth": res7.internal_forecast_growth,
                "expectation_gap": res7.expectation_gap,
                "cagr_components": res7.cagr_components
            },
            risk_warnings=module.risk_warnings,
            disclaimer="Expectation Gap Engine (E7) valuation assessment.",
            meta=res7.meta
        )
    elif module.id == "E8":
        from app.services.strategies.moat_engine import evaluate_moat_score
        from app.services.strategies.unit_economics import evaluate_unit_economics
        res_moat = evaluate_moat_score(symbol, as_of=as_of)
        res_unit = evaluate_unit_economics(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E8",
            strategy_name=module.name,
            status="production",
            executed_at=res_moat["executed_at"],
            symbol=res_moat["symbol"],
            passed_gates=(res_moat["moat_score"] >= 55.0),
            results={
                "moat_score": res_moat["moat_score"],
                "moat_classification": res_moat["moat_classification"],
                "moat_trajectory": res_moat["moat_trajectory"],
                "unit_economics_score": res_unit["unit_economics_score"],
                "unit_trend": res_unit["unit_trend"],
                "evidence": res_moat["evidence"] + res_unit["evidence"]
            },
            metrics={**res_moat["dimensions"], **res_unit["metrics"]},
            risk_warnings=module.risk_warnings,
            disclaimer="Moat Strength & Unit Economics Engine assessment.",
            meta=res_moat["meta"]
        )
    elif module.id == "C13":
        from app.services.strategies.governance_quality import evaluate_governance_quality
        res_c13 = evaluate_governance_quality(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="C13",
            strategy_name=module.name,
            status="production",
            executed_at=res_c13.executed_at,
            symbol=res_c13.symbol,
            passed_gates=(res_c13.governance_grade in ["EXCELLENT", "GOOD"]),
            results={
                "governance_score": res_c13.governance_score,
                "governance_grade": res_c13.governance_grade,
                "promoter_pledge_risk": res_c13.promoter_pledge_risk,
                "evidence": res_c13.evidence
            },
            metrics=res_c13.metrics_summary,
            risk_warnings=module.risk_warnings,
            disclaimer="Governance Quality assessment.",
            meta=res_c13.meta
        )
    elif module.id == "E9":
        from app.services.strategies.promoter_behaviour import evaluate_promoter_behaviour
        res_e9 = evaluate_promoter_behaviour(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E9",
            strategy_name=module.name,
            status="production",
            executed_at=res_e9["executed_at"],
            symbol=res_e9["symbol"],
            passed_gates=(res_e9["insider_conviction_score"] >= 65.0 and res_e9["hard_gate_status"] != "FAIL"),
            results=res_e9,
            metrics={"insider_conviction_score": res_e9["insider_conviction_score"]},
            risk_warnings=module.risk_warnings,
            disclaimer="Promoter & Insider Behaviour Engine assessment.",
            meta=res_e9["meta"]
        )
    elif module.id == "E10":
        from app.services.strategies.shareholding_pattern import evaluate_shareholding_pattern
        res_e10 = evaluate_shareholding_pattern(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E10",
            strategy_name=module.name,
            status="production",
            executed_at=res_e10["executed_at"],
            symbol=res_e10["symbol"],
            passed_gates=(res_e10["institutional_flow_score"] >= 60.0),
            results=res_e10,
            metrics={"institutional_flow_score": res_e10["institutional_flow_score"]},
            risk_warnings=module.risk_warnings,
            disclaimer="Shareholding-Pattern Intelligence assessment.",
            meta=res_e10["meta"]
        )
    elif module.id == "E11":
        from app.services.strategies.alternative_data import evaluate_alternative_data
        res_e11 = evaluate_alternative_data(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E11",
            strategy_name=module.name,
            status="production",
            executed_at=res_e11["executed_at"],
            symbol=res_e11["symbol"],
            passed_gates=(res_e11["external_confirmation_score"] in ["HIGH", "MEDIUM"]),
            results=res_e11,
            metrics={"alt_data_score": res_e11["alt_data_score"]},
            risk_warnings=module.risk_warnings,
            disclaimer="Primary Scuttlebutt & Indian Alt-Data assessment.",
            meta=res_e11["meta"]
        )
    elif module.id == "E12":
        from app.services.strategies.concall_nlp import evaluate_concall_nlp
        res_e12 = evaluate_concall_nlp(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E12",
            strategy_name=module.name,
            status="production",
            executed_at=res_e12["executed_at"],
            symbol=res_e12["symbol"],
            passed_gates=(res_e12["commentary_confidence_score"] >= 65.0),
            results=res_e12,
            metrics={"commentary_confidence_score": res_e12["commentary_confidence_score"]},
            risk_warnings=module.risk_warnings,
            disclaimer="Management Commentary & Concall NLP assessment.",
            meta=res_e12["meta"]
        )
    elif module.id == "E13":
        from app.services.strategies.multibagger_screener import evaluate_multibagger_score
        res_e13 = evaluate_multibagger_score(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E13",
            strategy_name=module.name,
            status="production",
            executed_at=res_e13.executed_at,
            symbol=res_e13.symbol,
            passed_gates=(res_e13.multibagger_score >= 60.0),
            results={
                "multibagger_score": res_e13.multibagger_score,
                "conviction_category": res_e13.conviction_category,
                "key_drivers": res_e13.key_drivers,
                "key_risks": res_e13.key_risks,
                "component_scores": res_e13.component_scores,
            },
            metrics={"multibagger_score": res_e13.multibagger_score, "score": res_e13.multibagger_score, "heuristic_confidence": res_e13.heuristic_confidence},
            risk_warnings=module.risk_warnings,
            disclaimer="Multibagger Optionality Screener (0-100 Asymmetric Bets) assessment.",
            meta=res_e13.meta
        )
    elif module.id == "E14":
        from app.services.research.portfolio_construction import evaluate_portfolio_construction
        res_e14 = evaluate_portfolio_construction(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E14",
            strategy_name=module.name,
            status="production",
            executed_at=res_e14["executed_at"],
            symbol=res_e14["symbol"],
            passed_gates=(res_e14["recommended_position_pct"] > 0.0),
            results=res_e14,
            metrics={"recommended_position_pct": res_e14["recommended_position_pct"]},
            risk_warnings=module.risk_warnings,
            disclaimer="Portfolio Position Sizing Engine assessment.",
            meta=res_e14["meta"]
        )
    elif module.id == "E15":
        from app.services.research.peer_normalization import evaluate_peer_normalization
        res_e15 = evaluate_peer_normalization(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E15",
            strategy_name=module.name,
            status="production",
            executed_at=res_e15["executed_at"],
            symbol=res_e15["symbol"],
            passed_gates=(res_e15.get("sector_relative_percentile") is not None and res_e15["sector_relative_percentile"] >= 50.0),
            results=res_e15,
            metrics={"sector_relative_percentile": res_e15["sector_relative_percentile"]},
            risk_warnings=module.risk_warnings,
            disclaimer="Business-Model Peer Normalization assessment.",
            meta=res_e15["meta"]
        )
    elif module.id == "E16":
        from app.services.decision_brain.red_team_engine import evaluate_red_team_review
        res_e16 = evaluate_red_team_review(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="E16",
            strategy_name=module.name,
            status="production",
            executed_at=res_e16["executed_at"],
            symbol=res_e16["symbol"],
            passed_gates=res_e16["gate_7_passed"],
            results=res_e16,
            metrics={"gate_7_passed": 1.0 if res_e16["gate_7_passed"] else 0.0},
            risk_warnings=module.risk_warnings,
            disclaimer="Analyst Behavioral-Bias & Red-Team Review assessment.",
            meta=res_e16["meta"]
        )
    elif module.id == "E17":
        from app.services.decision_brain.mivs_engine import MIVSEngine
        res_e17 = MIVSEngine().compute_mivs(symbol, [])
        return StrategyRunResponse(
            strategy_id="E17",
            strategy_name=module.name,
            status="production",
            executed_at=get_ist_now_str(),
            symbol=res_e17.symbol,
            passed_gates=(res_e17.passed_hard_gates and res_e17.mivs_score >= 55.0),
            results={
                "mivs_score": res_e17.mivs_score,
                "verdict": res_e17.verdict,
                "passed_hard_gates": res_e17.passed_hard_gates,
                "gate_reasons": res_e17.gate_reasons,
                "sector_relative_percentile": res_e17.sector_relative_percentile,
            },
            metrics={"mivs_score": res_e17.mivs_score, "score": res_e17.mivs_score, "sector_relative_percentile": res_e17.sector_relative_percentile},
            risk_warnings=res_e17.gate_reasons if not res_e17.passed_hard_gates else module.risk_warnings,
            disclaimer="Institutional Multibagger & Investment Intelligence Engine (MIVS) assessment.",
            meta=create_meta_header(source="MIVS Institutional Engine (E17)")
        )
    elif module.id == "E19":
        from app.services.strategies.inflection_multibagger import run_inflection_multibagger
        return run_inflection_multibagger(symbol)
    elif module.id == "OBV_ACC":
        from app.services.strategies.obv_accumulation_engine import run_obv_accumulation
        return run_obv_accumulation(symbol)
    elif module.id == "E20":
        from app.services.turnaround.turnaround_engine import run_turnaround_engine
        return run_turnaround_engine(symbol)



    elif module.id == "A2":
        from app.core.config import settings
        if not settings.ENABLE_OPTIONS_A2:
            return StrategyRunResponse(
                strategy_id="A2",
                strategy_name=module.name,
                status="suspended",
                executed_at=get_ist_now_str(),
                symbol=normalize_symbol(symbol),
                passed_gates=False,
                results={
                    "status": "suspended",
                    "reason": "A2 Short Strangle options engine is suspended until live option chain data is integrated.",
                    "required_inputs": ["underlying", "lower_strike", "upper_strike", "call_premium", "put_premium"]
                },
                metrics={},
                risk_warnings=["A2 Engine suspended — synthetic option premiums are disabled in production."],
                disclaimer="A2 Short Strangle options strategy payoff model is suspended.",
                meta=create_meta_header(source="IERL Strategy Registry (A2)")
            )
        else:
            from app.services.strategies.options_a2 import calculate_a2_payoff
            from app.models.schemas import OptionsA2Request
            a2_res = calculate_a2_payoff(OptionsA2Request(underlying=symbol))
            warnings = list(a2_res.risk_warnings or [])
            return StrategyRunResponse(
                strategy_id="A2",
                strategy_name=module.name,
                status="production",
                executed_at=a2_res.meta.retrieved_at,
                symbol=a2_res.underlying,
                passed_gates=bool(a2_res.expected_value_per_lot > 0),
                results={
                    "total_credit_per_lot": a2_res.total_credit_per_lot,
                    "breakevens": f"{a2_res.breakeven_lower} - {a2_res.breakeven_upper}",
                    "expected_value_per_lot": a2_res.expected_value_per_lot,
                    "estimated_margin_required": a2_res.estimated_margin_required,
                },
                metrics={
                    "spot_price": a2_res.spot_price,
                    "win_probability_pct": a2_res.probability_of_profit_empirical_pct,
                    "max_profit": a2_res.max_profit,
                    "max_loss": a2_res.max_loss
                },
                risk_warnings=warnings,
                disclaimer="A2 Short Strangle options strategy payoff model.",
                meta=a2_res.meta
            )
    elif module.id == "D18":
        return run_saatvik_d18(symbol)
    elif module.id == "B4":
        return run_vpa_b4(symbol)
    elif module.id == "B5":
        return run_vcp_b5(symbol)
    elif module.id == "B6":
        return run_rs_rating_b6(symbol)
    elif module.id == "B7":
        return run_pocket_pivot_b7(symbol)
    elif module.id == "B8":
        return run_sepa_b8(symbol)
    elif module.id == "C9":
        return run_reverse_dcf_c9(symbol)
    elif module.id == "D15":
        return run_ath_breakout_d15(symbol)
    elif module.id == "D17":
        return run_mean_reversion_d17(symbol)
    elif module.id in ("C11", "C12", "FORENSIC"):
        return run_forensic_engine(symbol, strategy_id=module.id)
    elif module.id == "A1":
        res_a1 = evaluate_option_arbitrage(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="A1",
            strategy_name=module.name,
            status="production",
            executed_at=res_a1["executed_at"],
            symbol=res_a1["symbol"],
            passed_gates=res_a1["arbitrage_opportunity"],
            results=res_a1,
            metrics={"parity_gap_pct": res_a1["parity_gap_pct"], "implied_volatility_skew": res_a1["implied_volatility_skew"]},
            risk_warnings=module.risk_warnings,
            disclaimer="Option Arbitrage & Calendar Spreads Engine assessment.",
            meta=res_a1["meta"]
        )
    elif module.id == "A3":
        res_a3 = evaluate_iron_condor(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="A3",
            strategy_name=module.name,
            status="production",
            executed_at=res_a3["executed_at"],
            symbol=res_a3["symbol"],
            passed_gates=(res_a3["probability_of_profit"] >= 65.0),
            results=res_a3,
            metrics={"max_profit": res_a3["max_profit"], "max_risk": res_a3["max_risk"], "probability_of_profit": res_a3["probability_of_profit"]},
            risk_warnings=module.risk_warnings,
            disclaimer="Iron Condor Volatility Premium Capture Engine assessment.",
            meta=res_a3["meta"]
        )
    elif module.id == "C10":
        res_c10 = evaluate_owner_earnings(symbol, as_of=as_of)
        return StrategyRunResponse(
            strategy_id="C10",
            strategy_name=module.name,
            status="production",
            executed_at=res_c10["executed_at"],
            symbol=res_c10["symbol"],
            passed_gates=(res_c10["fcf_yield_pct"] >= 2.5),
            results=res_c10,
            metrics={"fcf_yield_pct": res_c10["fcf_yield_pct"], "owner_earnings_inr": res_c10["owner_earnings_inr"]},
            risk_warnings=module.risk_warnings,
            disclaimer="Owner Earnings & Free Cash Flow Yield Engine assessment.",
            meta=res_c10["meta"]
        )
    elif module.id == "D16":
        res_d16 = evaluate_dual_momentum(symbol, as_of=as_of)
        if res_d16.get("status") != "production":
            return StrategyRunResponse(
                strategy_id="D16",
                strategy_name=module.name,
                status="data_insufficient",
                executed_at=res_d16.get("executed_at", get_ist_now_str()),
                symbol=res_d16.get("symbol", normalize_symbol(symbol)),
                passed_gates=False,
                results=res_d16,
                metrics={},
                risk_warnings=module.risk_warnings,
                disclaimer="Dual Momentum Trend Following Engine assessment.",
                meta=res_d16.get("meta", create_meta_header(source="D16 Dual Momentum Engine"))
            )
        return StrategyRunResponse(
            strategy_id="D16",
            strategy_name=module.name,
            status="production",
            executed_at=res_d16["executed_at"],
            symbol=res_d16["symbol"],
            passed_gates=(res_d16["dual_momentum_signal"] == "STRONG_BUY"),
            results=res_d16,
            metrics={"absolute_momentum_12m_pct": res_d16["absolute_momentum_12m_pct"], "relative_momentum_spread_pct": res_d16["relative_momentum_spread_pct"]},
            risk_warnings=module.risk_warnings,
            disclaimer="Dual Momentum Trend Following Engine assessment.",
            meta=res_d16["meta"]
        )
    elif module.id == "E18":
        import pandas as pd
        import yfinance as yf
        from app.services.strategies.swing_predictive_engine import SwingPredictiveEngine
        norm_sym = normalize_symbol(symbol)
        clean_sym = symbol.replace(".NS", "").replace(".BO", "").strip()
        yf_sym = f"{clean_sym}.NS"
        try:
            df_d = yf.download(yf_sym, period="6mo", interval="1d", progress=False)
            df_w = yf.download(yf_sym, period="2y", interval="1wk", progress=False)
            if isinstance(df_d.columns, pd.MultiIndex):
                df_d = df_d.xs(yf_sym, axis=1, level=1)
            df_d.columns = [str(c).lower() for c in df_d.columns]

            if isinstance(df_w.columns, pd.MultiIndex):
                df_w = df_w.xs(yf_sym, axis=1, level=1)
            df_w.columns = [str(c).lower() for c in df_w.columns]
            
            res_e18 = SwingPredictiveEngine.predict_swing_30d(df_d, df_w)
            return StrategyRunResponse(
                strategy_id="E18",
                strategy_name=module.name,
                status="production",
                executed_at=get_ist_now_str(),
                symbol=norm_sym,
                passed_gates=(res_e18.get("confluence_score", 0) >= 60.0),
                results=res_e18,
                metrics={
                    "confluence_score": res_e18.get("confluence_score", 0.0),
                    "target_price": res_e18.get("model_estimated_target", 0.0),
                    "stop_loss": res_e18.get("stop_loss", 0.0)
                },
                risk_warnings=module.risk_warnings,
                disclaimer="10-30 Day Swing Predictive Engine assessment.",
                meta=create_meta_header(source="E18 Swing Predictive Engine")
            )
        except Exception as ex:
            return StrategyRunResponse(
                strategy_id="E18",
                strategy_name=module.name,
                status="data_insufficient",
                executed_at=get_ist_now_str(),
                symbol=norm_sym,
                passed_gates=False,
                results={"error": str(ex)},
                metrics={},
                risk_warnings=module.risk_warnings,
                disclaimer="10-30 Day Swing Predictive Engine data error.",
                meta=create_meta_header(source="E18 Swing Predictive Engine")
            )
    elif module.id == "DCF_FWD":
        return run_dcf_forward(symbol)
    elif module.id == "E20":
        from app.services.turnaround.turnaround_engine import run_turnaround_engine
        return run_turnaround_engine(symbol, as_of=as_of)
    elif module.id == "E21":
        from app.services.research.early_compounder_engine import run_early_compounder_engine
        return run_early_compounder_engine(symbol, as_of=as_of)
    else:
        # No fake scores — return data_insufficient for any genuinely unimplemented module
        return StrategyRunResponse(
            strategy_id=module.id,
            strategy_name=module.name,
            status="data_insufficient",
            executed_at=get_ist_now_str(),
            symbol=normalize_symbol(symbol),
            passed_gates=False,
            results={
                "status": "data_insufficient",
                "reason": f"Module {module.id} ({module.name}) implementation pending Phase 3.",
                "strategy_category": module.category,
                "universe": module.universe,
            },
            metrics={},
            risk_warnings=[f"Module {module.id} not yet implemented — no score generated."],
            disclaimer=f"Module {module.id} is registered but not yet implemented. No diagnostic score.",
            meta=create_meta_header(source=f"IERL Strategy Registry ({module.id})")
        )
