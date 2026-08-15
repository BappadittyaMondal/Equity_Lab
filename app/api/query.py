"""AI Research Query router.
"""

from fastapi import APIRouter, Request
from app.core.config import settings
from app.core.security import rate_limiter, get_client_ip
from app.models.schemas import QueryRequest, QueryResponse
from app.services.llm import process_llm_query

router = APIRouter(prefix="/api/v1", tags=["AI Strategy Assistant"])


@router.post("/query", response_model=QueryResponse)
def handle_ai_query(req: QueryRequest, request: Request):
    """Processes research queries through verified LLM or deterministic analytical engine."""
    client_ip = get_client_ip(request)
    # Apply rate limiting (e.g. 10 requests / minute)
    rate_limiter.check_rate_limit(client_ip, max_requests=settings.RATE_LIMIT_LLM_RPM, window_seconds=60)
    
    return process_llm_query(req)
