"""Strategy Module Registry.

Maintains metadata and execution routing for all 18 IERL Expert Strategy Modules.
Strictly distinguishes production modules from coming-soon modules.
"""

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

# Master Registry of 18 Expert Strategy Modules
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
        status="suspended",
        required_inputs=["underlying", "lower_strike", "upper_strike", "call_premium", "put_premium"],
        universe="NIFTY / BANKNIFTY 0-DTE",
        metrics=["probability_of_profit", "expected_value", "breakeven_points", "max_loss"],
        risk_warnings=["Unlimited loss potential on unhedged short options. Hard stop discipline mandatory."],
        methodology="Suspended pending validated option-chain data, margin data, and backtesting."
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
    )
}



def list_strategy_modules() -> List[StrategyModule]:
    """Returns list of all 18 master strategy modules with status."""
    return list(STRATEGY_MODULES.values())


def get_strategy_module(strategy_id: str) -> StrategyModule:
    clean_id = strategy_id.upper().strip()
    if clean_id in STRATEGY_MODULES:
        return STRATEGY_MODULES[clean_id]
    if clean_id in RESEARCH_ENGINES:
        return RESEARCH_ENGINES[clean_id]
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Strategy module '{strategy_id}' not found. Valid IDs: {list(STRATEGY_MODULES.keys()) + list(RESEARCH_ENGINES.keys())}"
    )



def run_strategy_module(strategy_id: str, symbol: str = "RELIANCE") -> StrategyRunResponse:
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
        res1 = evaluate_growth_inflection(symbol)
        return StrategyRunResponse(
            strategy_id="E1",
            strategy_name=module.name,
            status="production",
            executed_at=res1.executed_at,
            symbol=res1.symbol,
            passed_gates=(res1.growth_inflection_score >= 50.0),
            results={
                "stage": res1.stage,
                "confidence": res1.confidence,
                "evidence": res1.evidence
            },
            metrics=res1.metrics_summary,
            risk_warnings=module.risk_warnings,
            disclaimer="Growth Inflection Engine assessment.",
            meta=res1.meta
        )
    elif module.id in ["E2", "C14"]:
        from app.services.strategies.turnaround_stage import evaluate_turnaround_stage
        res2 = evaluate_turnaround_stage(symbol)
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
        res3 = evaluate_growth_market_gap(symbol)
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
        res4 = evaluate_multibagger_score(symbol)
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
        res5 = evaluate_growth_arbitrage(symbol)
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
        res6 = run_quality_growth_screener(symbol)
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
        res7 = run_expectation_gap_engine(symbol)
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
                "confidence_score": res7.confidence_score,
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
    elif module.id == "C13":
        from app.services.strategies.governance_quality import evaluate_governance_quality
        res_c13 = evaluate_governance_quality(symbol)
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

    elif module.id == "A2":
        from app.services.strategies.options_a2 import calculate_a2_payoff
        from app.models.schemas import OptionsA2Request
        a2_res = calculate_a2_payoff(OptionsA2Request(
            underlying=symbol,
            lower_strike=22200.0,
            upper_strike=22700.0,
            call_premium=45.0,
            put_premium=55.0
        ))
        warnings = list(a2_res.risk_warnings or [])
        warnings.append(
            "STRATEGY SUSPENDED: Option chain data pipeline inactive. "
            "Option strike prices (22200/22700) and premiums are placeholder inputs for testing only."
        )
        return StrategyRunResponse(
            strategy_id="A2",
            strategy_name=module.name,
            status=module.status,
            executed_at=a2_res.meta.retrieved_at,
            symbol=a2_res.underlying,
            passed_gates=False,
            results={
                "total_credit_per_lot": a2_res.total_credit_per_lot,
                "breakevens": f"{a2_res.breakeven_lower} - {a2_res.breakeven_upper}",
                "expected_value_per_lot": a2_res.expected_value_per_lot,
                "placeholder_notice": "Strikes 22200/22700 are synthetic inputs"
            },
            metrics={
                "spot_price": a2_res.spot_price,
                "win_probability_pct": a2_res.probability_of_profit_empirical_pct,
                "max_profit": a2_res.max_profit,
                "max_loss": a2_res.max_loss
            },
            risk_warnings=warnings,
            disclaimer="A2 Short Strangle options strategy payoff model (SUSPENDED - Placeholder Strike Inputs).",
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
        return run_forensic_engine(symbol)
    elif module.id == "DCF_FWD":
        return run_dcf_forward(symbol)
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
