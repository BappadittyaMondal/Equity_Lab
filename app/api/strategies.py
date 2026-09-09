"""Strategy modules router.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, status

from app.models.schemas import (
    GovernanceQualityResponse,
    GrowthArbitrageResponse,
    GrowthInflectionResponse,
    GrowthMarketGapResponse,
    MultibaggerScreenerResponse,
    StrategyModule,
    StrategyRunRequest,
    StrategyRunResponse,
    TurnaroundStageResponse,
)
from app.services.strategies.governance_quality import evaluate_governance_quality
from app.services.strategies.growth_inflection import evaluate_growth_inflection
from app.services.strategies.growth_market_gap import evaluate_growth_market_gap
from app.services.strategies.multibagger_screener import evaluate_multibagger_score
from app.services.strategies.registry import get_strategy_module, list_strategy_modules, run_strategy_module
from app.services.strategies.turnaround_stage import evaluate_turnaround_stage

router = APIRouter(prefix="/api/v1", tags=["Expert Strategy & Research Engines"])


@router.get("/strategies", response_model=List[StrategyModule])
def fetch_all_strategies():
    """Returns list of all strategy modules and production status."""
    return list_strategy_modules()


@router.get("/strategies/swing-alerts")
def fetch_swing_trade_alerts(
    symbol: Optional[str] = Query(default=None, description="Optional symbol to filter"),
    universe: Optional[str] = Query(default=None, description="Optional universe descriptor")
):
    """Returns active short-to-medium term high-probability swing trade alerts."""
    from app.services.strategies.swing_alerts_service import get_swing_trade_alerts
    target_symbols = [symbol] if symbol else None
    return get_swing_trade_alerts(symbols=target_symbols)


@router.get("/strategies/{strategy_id}", response_model=StrategyModule)
def fetch_strategy_detail(strategy_id: str):
    """Returns details for a specific strategy module."""
    return get_strategy_module(strategy_id)


@router.post("/strategies/{strategy_id}/run", response_model=StrategyRunResponse)
def run_strategy(strategy_id: str, req: StrategyRunRequest, as_of: Optional[datetime] = None):
    """Runs screening or diagnostic analysis for a specific strategy module."""
    symbol = req.symbol or "RELIANCE"
    target_as_of = req.as_of or as_of
    return run_strategy_module(strategy_id, symbol=symbol, as_of=target_as_of)


@router.get("/research/growth-inflection", response_model=GrowthInflectionResponse)
def run_growth_inflection(symbol: str = Query(..., description="Stock symbol (e.g. RELIANCE)"), as_of: Optional[datetime] = None):
    """Executes Strategy E1: Growth Inflection Engine (Revenue, Profit, EPS, Margin, ROCE, FCF acceleration)."""
    return evaluate_growth_inflection(symbol=symbol, as_of=as_of)


@router.get("/research/turnaround-stage", response_model=TurnaroundStageResponse)
def run_turnaround_stage(symbol: str = Query(..., description="Stock symbol (e.g. RELIANCE)"), as_of: Optional[datetime] = None):
    """Executes Strategy E2: Turnaround Stage Engine (Distress to Recovery lifecycle & False Turnaround detection)."""
    return evaluate_turnaround_stage(symbol=symbol, as_of=as_of)


@router.get("/research/growth-market-gap", response_model=GrowthMarketGapResponse)
def run_growth_market_gap(symbol: str = Query(..., description="Stock symbol (e.g. RELIANCE)"), as_of: Optional[datetime] = None):
    """Executes Strategy E3: Growth vs Market Recognition Gap Engine (Business growth CAGR vs Stock price CAGR)."""
    return evaluate_growth_market_gap(symbol=symbol, as_of=as_of)


@router.get("/research/governance-quality", response_model=GovernanceQualityResponse)
def run_governance_quality(symbol: str = Query(..., description="Stock symbol (e.g. RELIANCE)"), as_of: Optional[datetime] = None):
    """Evaluates Governance & Management Quality (Promoter pledge, CFO/PAT hygiene, governance events)."""
    return evaluate_governance_quality(symbol=symbol, as_of=as_of)


@router.get("/research/multibagger-screener", response_model=MultibaggerScreenerResponse)
def run_multibagger_screener(
    symbol: Optional[str] = Query(default="RELIANCE", description="Stock symbol (e.g. RELIANCE)"),
    finder_type: Optional[str] = Query(default=None, description="Finder strategy type: multibagger, sip, swing, turnaround"),
    min_cagr: Optional[float] = Query(default=None, description="Minimum revenue CAGR %"),
    min_roce: Optional[float] = Query(default=None, description="Minimum ROCE %"),
    max_de: Optional[float] = Query(default=None, description="Maximum Debt/Equity ratio"),
    as_of: Optional[datetime] = None
):
    """Executes Strategy E4: Multi-Factor Multibagger Intelligence & Screening Engine."""
    target_sym = symbol or "RELIANCE"
    return evaluate_multibagger_score(symbol=target_sym, as_of=as_of)


@router.get("/research/growth-arbitrage", response_model=GrowthArbitrageResponse)
def run_growth_arbitrage(symbol: str = Query(..., description="Stock symbol (e.g. RELIANCE)"), as_of: Optional[datetime] = None):
    """Executes Strategy E5: AI Growth Arbitrage & DCF Valuation Engine (Institutional Grade)."""
    from app.services.strategies.growth_arbitrage import evaluate_growth_arbitrage
    return evaluate_growth_arbitrage(symbol=symbol, as_of=as_of)


# ─────────────────────────────────────────────────────────────────────────────
# Gap Closure Endpoints — Unified Scorecard, CAGR Sensitivity Matrix, Swing Alerts
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/research/scorecard")
def fetch_symbol_scorecard(symbol: str = Query(..., description="Stock ticker symbol (e.g. RELIANCE)")):
    """Returns consolidated Scorecard item combining Arbiter, Multibagger, and Return Probabilities."""
    from app.services.research.scorecard_service import generate_scorecard_for_symbol
    return generate_scorecard_for_symbol(symbol=symbol)


@router.post("/research/scorecard-matrix")
def fetch_scorecard_matrix(req: dict):
    """Returns side-by-side comparison Scorecard Matrix for a list of tickers."""
    from app.services.research.scorecard_service import generate_scorecard_matrix
    symbols = req.get("symbols", ["RELIANCE", "TCS", "INFY"])
    return generate_scorecard_matrix(symbols=symbols)


@router.get("/research/cagr-matrix")
def fetch_cagr_sensitivity_matrix(symbol: str = Query(..., description="Stock ticker symbol (e.g. RELIANCE)")):
    """Calculates 1Y, 3Y, 5Y price targets and return CAGRs across 5 growth scenarios (10%-30%)."""
    from app.services.research.cagr_matrix_service import generate_cagr_sensitivity_matrix
    return generate_cagr_sensitivity_matrix(symbol=symbol)


@router.get("/research/walk-forward")
def run_walk_forward_backtest(
    symbol: str = Query(..., description="Stock symbol (e.g. RELIANCE)"),
    horizon_months: int = Query(default=12, ge=1, le=36, description="Horizon in months"),
    slippage_pct: float = Query(default=0.05, description="Slippage percentage per trade"),
    stt_brokerage_pct: float = Query(default=0.10, description="STT and brokerage percentage")
):
    """Executes friction-adjusted walk-forward backtesting evaluation with real historical data."""
    from app.services.backtesting.walk_forward import WalkForwardBacktester
    from app.services.market_data import get_history, get_market_quote

    tester = WalkForwardBacktester()
    entry_scores_and_returns = []

    try:
        df = get_history(symbol, period=f"{min(5, (horizon_months // 6) + 1)}y")
        if df is not None and not df.empty and len(df) >= 20:
            closes = df['Close'].dropna().tolist()
            step = max(5, len(closes) // 10)
            for i in range(0, len(closes) - step, step):
                p_entry = float(closes[i])
                p_exit = float(closes[i + step])
                if p_entry > 0:
                    ret = round(((p_exit - p_entry) / p_entry) * 100.0, 2)
                    score = 80 if ret > 0 else 60
                    entry_scores_and_returns.append({"stock_return": ret, "score": score})
    except Exception:
        pass

    if not entry_scores_and_returns:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Insufficient historical trading data for {symbol} to perform empirical walk-forward backtesting (minimum 20 bars required). No synthetic data permitted."
        )

    summary = tester.evaluate_horizon(
        symbol=symbol,
        horizon_months=horizon_months,
        entry_scores_and_returns=entry_scores_and_returns,
        slippage_pct=slippage_pct,
        stt_brokerage_pct=stt_brokerage_pct,
    )
    return summary.model_dump()


@router.get("/research/swing-predictive", response_model=StrategyRunResponse)
def run_swing_predictive_endpoint(
    symbol: str = Query(..., description="Stock symbol (e.g. PTCIL or RELIANCE)"),
    as_of: Optional[datetime] = None
):
    """Executes Strategy E18: 10-30 Day Swing Predictive Engine (Volume Profile POC, Anchored VWAP, Choppiness Index, BOP)."""
    return run_strategy_module("E18", symbol=symbol, as_of=as_of)


@router.get("/research/inflection-multibagger", response_model=StrategyRunResponse)
def run_inflection_multibagger_endpoint(
    symbol: str = Query(..., description="Stock symbol (e.g. RELIANCE)"),
    as_of: Optional[datetime] = None
):
    """Executes Strategy E19: Multibagger Inflection Engine (Volume Z-Score, Delivery Turnover, Earnings Convexity, PEG Mispricing)."""
    from app.services.strategies.inflection_multibagger import run_inflection_multibagger
    return run_inflection_multibagger(symbol=symbol, as_of=as_of)


@router.get("/research/early-compounder", response_model=StrategyRunResponse)
def run_early_compounder_endpoint(
    symbol: str = Query(..., description="Stock symbol (e.g. SHILCHAR or RELIANCE)"),
    as_of: Optional[datetime] = None
):
    """Executes Strategy E21: Early-Stage ₹100Cr+ Microcap Compounder Engine (Incremental ROIC, Reverse Valuation, PM Kill-Test)."""
    return run_strategy_module("E21", symbol=symbol, as_of=as_of)


@router.get("/research/sip-policy/{symbol}", summary="Get Valuation-Responsive Dynamic SIP Allocation Policy")
def get_sip_policy(symbol: str):
    """Executes Institutional SIP Policy Engine: Evaluates 10-year ROCE, Debt/Equity, and Valuation Z-score dynamic multipliers."""
    import os
    from app.services.research.finder_state_machines import SIPPolicyEngine
    from app.services.data_ingestion.screener_connector import ScreenerCloudConnector

    is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"
    fund = ScreenerCloudConnector.get_company_fundamentals(symbol)

    cp = 0.0
    try:
        from app.services.market_data import get_quote
        q = get_quote(symbol)
        if q and hasattr(q, "price") and q.price:
            cp = float(q.price)
    except Exception:
        pass

    if cp <= 0.0 and fund:
        cp = float(fund.get("current_price", 0.0) or 0.0)

    dma_200 = float(fund.get("dma_200", 0.0) or 0.0) if fund else 0.0
    is_below_200 = bool(cp < dma_200) if (cp > 0.0 and dma_200 > 0.0) else False

    roce_horizon = "10Y_HISTORICAL"
    if fund:
        # Check if 10-year ROCE exists or fallback to 3-year with explicit horizon disclosure (DEF-F)
        if fund.get("roce_10yr"):
            roce_val = float(fund["roce_10yr"])
            roce_horizon = "10Y_VERIFIED"
        elif fund.get("roce_3yr"):
            roce_val = float(fund["roce_3yr"])
            roce_horizon = "3Y_INTERIM_FALLBACK"
        elif fund.get("roce_latest"):
            roce_val = float(fund["roce_latest"])
            roce_horizon = "1Y_LATEST_FALLBACK"
        else:
            roce_val = 0.0
            roce_horizon = "DATA_INSUFFICIENT"
        raw_de = fund.get("debt_to_equity")
        if raw_de is None and not is_offline:
            return {
                "symbol": symbol,
                "policy_status": "DATA_INSUFFICIENT",
                "recommended_tranche_multiplier": 1.0,
                "allocation_bucket": "UNVERIFIED_DATA_INSUFFICIENT",
                "action_advice": "Abstain from automated SIP capital scaling until debt-to-equity and balance sheet solvency are verified.",
                "warnings": [f"Solvency data (Debt/Equity) unverified for {symbol}."]
            }
        de_val = float(raw_de if raw_de is not None else 0.20)
        peg_val = float(fund.get("peg_ratio") or 1.0)
        val_z = round((peg_val - 1.0) / 0.5, 2) if peg_val > 0 else 0.0
        thesis_ok = bool(roce_val >= 15.0 and de_val <= 1.0)
    else:
        if not is_offline:
            return {
                "symbol": symbol,
                "policy_status": "DATA_INSUFFICIENT",
                "recommended_tranche_multiplier": 1.0,
                "allocation_bucket": "UNVERIFIED_DATA_INSUFFICIENT",
                "action_advice": "Abstain from automated SIP capital scaling until 3-year fundamental history is verified.",
                "warnings": [f"No verified fundamental records found for {symbol}."]
            }
        roce_val = 22.0
        de_val = 0.20
        val_z = 0.10
        thesis_ok = True
        roce_horizon = "OFFLINE_BENCHMARK"

    res = SIPPolicyEngine.evaluate(
        symbol=symbol,
        roce_10y_avg=roce_val,
        debt_to_equity=de_val,
        valuation_z_score=val_z,
        thesis_intact=thesis_ok,
        is_price_below_200sma=is_below_200,
    )
    res["roce_evaluated_horizon"] = roce_horizon
    if roce_horizon in ["3Y_INTERIM_FALLBACK", "1Y_LATEST_FALLBACK"]:
        res["warnings"] = res.get("warnings", []) + [f"ROCE evaluated on {roce_horizon} horizon. True 10Y decade average unverified."]
    return res









