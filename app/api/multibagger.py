"""FastAPI Router for Institutional Fundamental Early-Multibagger Framework (§58).

Exposes machine-readable stock report, 100-point MIVS distribution, and individual institutional engine signals.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.models.schemas import (
    MachineReadableStockReport,
    MultiHorizonMatrixRequest,
    MultiHorizonMatrixResponse,
)
from app.services.decision_brain.arbiter import Arbiter
from app.services.decision_brain.mivs_engine import MIVSEngine
from app.services.strategies.promoter_behaviour import evaluate_promoter_behaviour
from app.services.strategies.shareholding_pattern import evaluate_shareholding_pattern
from app.services.strategies.alternative_data import evaluate_alternative_data
from app.services.strategies.concall_nlp import evaluate_concall_nlp
from app.services.strategies.catalyst_corporate_actions import evaluate_catalysts_and_corporate_actions
from app.services.research.portfolio_construction import evaluate_portfolio_construction

router = APIRouter(prefix="/api/v1/multibagger", tags=["Institutional Multibagger Framework"])


@router.get("/report/{symbol}", response_model=MachineReadableStockReport, summary="Get Machine-Readable Stock Report (§58)")
def get_machine_readable_report(symbol: str):
    """Generates complete Machine-Readable Stock Report incorporating all 18 institutional modules."""
    try:
        arbiter = Arbiter()
        return arbiter.generate_machine_readable_report(symbol)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate report for {symbol}: {str(e)}")


@router.get("/mivs/{symbol}", summary="Get MIVS 100-Point Score & 7 Hard Gates (§51, §52)")
def get_mivs_score(symbol: str, sector: str = Query("MANUFACTURING")):
    """Calculates 100-point MIVS composite vector across 9 components and 7 Hard Gates."""
    try:
        arbiter = Arbiter()
        outputs = arbiter._collect_engine_outputs(symbol)
        mivs_res = MIVSEngine().compute_mivs(symbol, outputs, sector=sector)
        return mivs_res.model_dump()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"MIVS calculation failed: {str(e)}")


@router.get("/promoter/{symbol}", summary="Get Promoter & Insider Behaviour Signal (§29)")
def get_promoter_behaviour(symbol: str):
    """Returns promoter skin-in-the-game, pledge trajectory, and insider conviction score."""
    return evaluate_promoter_behaviour(symbol)


@router.get("/shareholding/{symbol}", summary="Get Shareholding Pattern Intelligence Signal (§28)")
def get_shareholding_pattern(symbol: str):
    """Returns institutional flow momentum, accumulation streaks, and index catalyst indicators."""
    return evaluate_shareholding_pattern(symbol)


@router.get("/altdata/{symbol}", summary="Get Indian Alt-Data & Scuttlebutt Signal (§26, §27)")
def get_alternative_data(symbol: str):
    """Returns GST e-way bills, EPFO payroll growth, Vahan portal registrations, and channel check results."""
    return evaluate_alternative_data(symbol)


@router.get("/concall/{symbol}", summary="Get Management Commentary Concall NLP Signal (§30)")
def get_concall_nlp(symbol: str):
    """Returns management tone shifts, guidance specificity, and Q&A deflection analysis."""
    return evaluate_concall_nlp(symbol)


@router.get("/catalysts/{symbol}", summary="Get Policy Catalysts & Corporate Actions Signal (§47, §48)")
def get_catalysts(symbol: str):
    """Returns PLI eligibility, tariff protection, buyback accretiveness, and credit rating agency actions."""
    return evaluate_catalysts_and_corporate_actions(symbol)


@router.get("/portfolio/{symbol}", summary="Get Position Sizing & Drawdown Discipline Signal (§35, §36, §37)")
def get_portfolio_sizing(symbol: str, mivs_score: float = Query(75.0), archetype: str = Query("EARLY_GROWTH")):
    """Returns fractional-Kelly position size, liquidity caps, scaling ladders, and drawdown tolerance bands."""
    return evaluate_portfolio_construction(symbol, mivs_score=mivs_score, archetype=archetype)


@router.post("/institutional-rank", summary="Rank Universe via 27-Engine Multibagger Framework")
def get_institutional_universe_rank(min_score: float = Query(50.0)):
    """Executes 27-Engine scoring, archetype classification, risk penalty audit, and thesis generation."""
    try:
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        results = InstitutionalMultibaggerEngine.rank_universe(min_score=min_score)
        return {
            "total_candidates": len(results),
            "min_score_filter": min_score,
            "rankings": results
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Multibagger ranking failed: {str(e)}")


@router.get("/institutional-score/{symbol}", summary="Get Single Stock 27-Engine Scorecard & Archetype")
def get_single_stock_institutional_score(symbol: str):
    """Returns single-stock 100-point breakdown, archetype, causal chain, and thesis invalidation rules."""
    try:
        from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        universe = ScreenerCloudConnector.get_all_fundamentals()
        target = next((item for item in universe if item["symbol"].lower() == symbol.lower() or item["symbol"].split(".")[0].lower() == symbol.lower()), None)
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Symbol {symbol} not found in fundamentals database.")
        return InstitutionalMultibaggerEngine.evaluate_company(target)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Scoring failed for {symbol}: {str(e)}")


@router.post("/multi-horizon-matrix", response_model=MultiHorizonMatrixResponse, summary="Generate Multi-Horizon CAGR & Conformal Return Probability Matrix")
def generate_multi_horizon_matrix(request: MultiHorizonMatrixRequest):
    """Generates 6M to 5Y CAGRs, conformal return probabilities, confidence labels, M0-M4 stages, and strategy buckets."""
    try:
        from app.services.research.multi_horizon_matrix_engine import MultiHorizonMatrixEngine
        return MultiHorizonMatrixEngine.analyze_universe_matrix(request.symbols)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Multi-horizon matrix analysis failed: {str(e)}")


