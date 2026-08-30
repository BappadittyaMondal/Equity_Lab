"""Multi-Agent AI Committee & Next-Gen GenAI API Router."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_committee.investment_committee import VirtualInvestmentCommittee
from app.services.research.footnote_rpt_auditor import FootnoteRPTAuditor
from app.services.research.supply_chain_graph import SupplyChainGraphEngine
from app.services.query.nl_quant_compiler import NLQuantCompiler
from app.services.ml.post_mortem_learning import PostMortemLearningEngine

router = APIRouter(prefix="/api/v1/research/ai-committee", tags=["Next-Gen AI Committee & Intelligence"])


class ICReviewRequest(BaseModel):
    symbol: str = Field(..., json_schema_extra={"example": "SHILCHAR"})
    stock_data: Optional[Dict[str, Any]] = None


class NLQueryRequest(BaseModel):
    user_query: str = Field(..., json_schema_extra={"example": "Find capital goods stocks under 2000Cr market cap with debt-free balance sheet and positive FCF"})


class PostMortemAuditRequest(BaseModel):
    symbol: str = Field(..., json_schema_extra={"example": "COFORGE"})
    initial_score: float = Field(88.5, json_schema_extra={"example": 88.5})
    forward_return_pct: float = Field(-18.0, json_schema_extra={"example": -18.0})
    actual_drawdown_pct: float = Field(22.5, json_schema_extra={"example": 22.5})


@router.post("/review", response_model=Dict[str, Any])
def run_ic_boardroom_review(payload: ICReviewRequest) -> Dict[str, Any]:
    """Run Multi-Agent Virtual Investment Committee debate and generate executive IC Memo."""
    return VirtualInvestmentCommittee.evaluate_investment_committee(
        symbol=payload.symbol,
        stock_data=payload.stock_data
    )


@router.get("/governance-audit/{symbol}", response_model=Dict[str, Any])
def audit_governance(symbol: str) -> Dict[str, Any]:
    """Audit Form AOC-2 RPTs, promoter pledging, and auditor report notes."""
    return FootnoteRPTAuditor.audit_governance_and_footnotes(symbol)


@router.get("/supply-chain/{symbol}", response_model=Dict[str, Any])
def get_supply_chain_graph(symbol: str) -> Dict[str, Any]:
    """Fetch customer-supplier graph and second-order catalyst chain."""
    return SupplyChainGraphEngine.get_supply_chain_profile(symbol)


@router.post("/nl-query", response_model=Dict[str, Any])
def compile_nl_query(payload: NLQueryRequest) -> Dict[str, Any]:
    """Compile plain English search query into quantitative engine constraints."""
    return NLQuantCompiler.compile_natural_language_query(payload.user_query)


from app.services.intelligence.financial_forensics import FinancialForensicsEngine
from app.services.ml.evt_gpd_engine import EVTGPDEngine
from app.services.market_data import get_history, normalize_symbol


@router.post("/post-mortem", response_model=Dict[str, Any])
def audit_post_mortem(payload: PostMortemAuditRequest) -> Dict[str, Any]:
    """Run continuous failure post-mortem audit on underperforming stocks."""
    return PostMortemLearningEngine.audit_stock_drawdown(
        symbol=payload.symbol,
        initial_score=payload.initial_score,
        forward_return_pct=payload.forward_return_pct,
        actual_drawdown_pct=payload.actual_drawdown_pct
    )


@router.get("/forensics/{symbol}", response_model=Dict[str, Any])
def get_company_forensics(symbol: str) -> Dict[str, Any]:
    """Fetch balance sheet forensic analysis (CWIP turn, working capital drag, Cash-PAT persistence)."""
    return FinancialForensicsEngine.analyze_company_forensics({"symbol": symbol})


@router.get("/evt-tail/{symbol}", response_model=Dict[str, Any])
def get_evt_tail_metrics(symbol: str) -> Dict[str, Any]:
    """Fetch Extreme Value Theory (EVT) GPD tail-fitting parameters and 99th percentile breakout VaR."""
    norm_sym = normalize_symbol(symbol)
    try:
        hist = get_history(norm_sym, period="3y")
        returns = hist["Close"].pct_change().dropna().values if hist is not None and not hist.empty else None
    except Exception:
        returns = None

    return EVTGPDEngine.fit_gpd_tail_exceedances(returns)

