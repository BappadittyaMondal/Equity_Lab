"""Phase 3: Generative AI Red-Team & Geopolitical Overlay API Router."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.research.geopolitical_engine import evaluate_geopolitical_risk
from app.services.research.genai_redteam_service import GenAIRedTeamService

router = APIRouter(prefix="/api/v1/research/genai-redteam", tags=["Phase 3 GenAI & Red-Team"])


class ConcallAuditRequest(BaseModel):
    symbol: str = Field(..., json_schema_extra={"example": "COFORGE"})
    transcript_text: Optional[str] = None


class StressTestRequest(BaseModel):
    symbol: str = Field(..., json_schema_extra={"example": "COFORGE"})
    scenario: str = Field("US_IT_BUDGET_CUT_15PCT", json_schema_extra={"example": "US_IT_BUDGET_CUT_15PCT"})


class RedTeamRequest(BaseModel):
    symbol: str = Field(..., json_schema_extra={"example": "SHILCHAR"})
    primary_bull_thesis: str = Field("High-growth grid transformer compounder", json_schema_extra={"example": "High-growth grid transformer compounder"})


@router.get("/geopolitical-overlay/{symbol}", response_model=Dict[str, Any])
def get_geopolitical_overlay(symbol: str) -> Dict[str, Any]:
    """Fetch Phase 3 MacroGeopoliticalOverlay (+15% Defense, +10% Renewables, -20% IT Exporters)."""
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol parameter is required.")
    return evaluate_geopolitical_risk(symbol)


@router.post("/concall-audit", response_model=Dict[str, Any])
def audit_concall_transcript(payload: ConcallAuditRequest) -> Dict[str, Any]:
    """Run Automated Earnings Call Analyst to extract qualitative concall risks."""
    return GenAIRedTeamService.audit_earnings_call_transcript(
        symbol=payload.symbol,
        transcript_text=payload.transcript_text
    )


@router.post("/stress-test", response_model=Dict[str, Any])
def run_stress_test(payload: StressTestRequest) -> Dict[str, Any]:
    """Run Automated Geopolitical Stress Tester."""
    return GenAIRedTeamService.run_geopolitical_stress_test(
        symbol=payload.symbol,
        scenario=payload.scenario
    )


@router.post("/red-team-review", response_model=Dict[str, Any])
def generate_red_team_review(payload: RedTeamRequest) -> Dict[str, Any]:
    """Run Automated Counter-Thesis Bot / GenAI Red-Team Bear Case."""
    return GenAIRedTeamService.generate_counter_thesis_redteam(
        symbol=payload.symbol,
        primary_bull_thesis=payload.primary_bull_thesis
    )
