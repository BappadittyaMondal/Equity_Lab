"""FastAPI Router for Technical Probability & Market-Structure Intelligence Framework.

Provides API endpoints:
  - GET /api/v1/technical/report/{symbol} : Full MachineReadableTechnicalReport (§113)
  - GET /api/v1/technical/regime : Current Market Regime Classification (R1–R6)
  - GET /api/v1/technical/screener : 3-Tier Technical Universe Screener Candidates
  - GET /api/v1/technical/probability/{symbol} : Calibrated Probability Ladder & Path Statistics
  - GET /api/v1/technical/trade_manager/{symbol} : Active In-Position Management Rules
  - GET /api/v1/technical/surveillance/{symbol} : ASM/GSM/T2T & Indian Transaction Cost Breakdown
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query

from app.services.decision_brain.arbiter import Arbiter
from app.services.research.market_regime import classify_market_regime
from app.services.research.universe_screener import run_technical_universe_screener
from app.services.research.technical_probability import calculate_calibrated_probability_ladder
from app.services.risk.trade_management import evaluate_in_position_management
from app.services.risk.surveillance_gate import evaluate_surveillance_and_cost_gate

router = APIRouter(prefix="/api/v1/technical", tags=["Institutional Technical Framework"])


@router.get("/report/{symbol}")
def get_technical_report(symbol: str) -> Dict[str, Any]:
    """Retrieves full standardized Machine-Readable Technical Report for a given ticker symbol."""
    try:
        arbiter = Arbiter()
        report = arbiter.generate_technical_report(symbol)
        return report.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate technical report for {symbol}: {str(e)}")


@router.get("/regime")
def get_market_regime() -> Dict[str, Any]:
    """Retrieves current market regime classification for Indian equities."""
    try:
        regime = classify_market_regime()
        return regime.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to classify market regime: {str(e)}")


@router.get("/screener")
def run_screener(
    min_tss_score: float = Query(65.0, ge=0.0, le=100.0),
    setup_filter: Optional[str] = None
) -> Dict[str, Any]:
    """Runs 3-tier technical universe screener and returns top setup candidates."""
    try:
        return run_technical_universe_screener(min_tss_score=min_tss_score, setup_filter=setup_filter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run technical screener: {str(e)}")


@router.get("/probability/{symbol}")
def get_probability_ladder(symbol: str) -> Dict[str, Any]:
    """Retrieves empirical probability ladder and MAE/MFE path statistics."""
    try:
        ladder = calculate_calibrated_probability_ladder(symbol=symbol)
        return ladder.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute probability ladder for {symbol}: {str(e)}")


@router.get("/trade_manager/{symbol}")
def get_trade_management(
    symbol: str,
    entry_price: float = Query(500.0, gt=0.0),
    current_price: float = Query(525.0, gt=0.0),
    highest_close: float = Query(530.0, gt=0.0),
    stop_price: float = Query(475.0, gt=0.0),
    days_in_trade: int = Query(6, ge=0)
) -> Dict[str, Any]:
    """Evaluates active in-position trade management rules for a live position."""
    try:
        state = evaluate_in_position_management(
            symbol=symbol,
            entry_price=entry_price,
            current_price=current_price,
            highest_close_since_entry=highest_close,
            initial_stop_price=stop_price,
            days_in_trade=days_in_trade
        )
        return state.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate trade management for {symbol}: {str(e)}")


@router.get("/surveillance/{symbol}")
def get_surveillance_gate(symbol: str) -> Dict[str, Any]:
    """Retrieves ASM/GSM/T2T regulatory surveillance status and roundtrip trade cost breakdown."""
    try:
        gate = evaluate_surveillance_and_cost_gate(symbol=symbol)
        return gate.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate surveillance gate for {symbol}: {str(e)}")
