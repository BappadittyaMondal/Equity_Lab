"""Strategy modules router.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Query

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
def fetch_swing_trade_alerts(universe: Optional[str] = Query(default=None, description="Optional universe descriptor")):
    """Returns active short-to-medium term high-probability swing trade alerts."""
    from app.services.strategies.swing_alerts_service import get_swing_trade_alerts
    return get_swing_trade_alerts()


@router.get("/strategies/{strategy_id}", response_model=StrategyModule)
def fetch_strategy_detail(strategy_id: str):
    """Returns details for a specific strategy module."""
    return get_strategy_module(strategy_id)


@router.post("/strategies/{strategy_id}/run", response_model=StrategyRunResponse)
def run_strategy(strategy_id: str, req: StrategyRunRequest):
    """Runs screening or diagnostic analysis for a specific strategy module."""
    symbol = req.symbol or "RELIANCE"
    return run_strategy_module(strategy_id, symbol=symbol)


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



