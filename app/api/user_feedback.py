"""User Feedback & Counter-Question API Endpoint (§Phase 2)."""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.research.user_feedback_engine import UserFeedbackEngine

router = APIRouter(prefix="/api/v1/research/user-feedback", tags=["Phase 2 User Feedback"])


class CounterQuestionRequest(BaseModel):
    user_query: str = Field(..., json_schema_extra={"example": "Why is Shilchar ranked differently from Waaree on Free Cash Flow?"})
    stock_context: Optional[List[Dict[str, Any]]] = None


@router.post("", response_model=Dict[str, Any])
def submit_counter_question(payload: CounterQuestionRequest) -> Dict[str, Any]:
    """Process user counter-questions and generate evidence-based analytical feedback."""
    if not payload.user_query or len(payload.user_query.strip()) < 3:
        raise HTTPException(status_code=400, detail="user_query cannot be empty.")
    
    engine = UserFeedbackEngine()
    result = engine.process_counter_question(
        user_query=payload.user_query,
        stock_context=payload.stock_context
    )
    return result
