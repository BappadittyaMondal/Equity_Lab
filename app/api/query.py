"""AI Research Query router.
"""

from fastapi import APIRouter, Request
from app.core.config import settings
from app.core.security import rate_limiter, get_client_ip
from app.models.schemas import QueryRequest, QueryResponse, YouTubeAnalyzeRequest, YouTubeAnalyzeResponse
from app.services.llm import process_llm_query
from app.services.research.video_intelligence_engine import VideoIntelligenceEngine

router = APIRouter(prefix="/api/v1", tags=["AI Strategy Assistant"])


@router.post("/query", response_model=QueryResponse)
def handle_ai_query(req: QueryRequest, request: Request):
    """Processes research queries through verified LLM or deterministic analytical engine."""
    client_ip = get_client_ip(request)
    # Apply rate limiting (e.g. 10 requests / minute)
    rate_limiter.check_rate_limit(client_ip, max_requests=settings.RATE_LIMIT_LLM_RPM, window_seconds=60)
    
    return process_llm_query(req)


@router.post("/youtube-analyze", response_model=YouTubeAnalyzeResponse)
@router.post("/research/youtube-analyze", response_model=YouTubeAnalyzeResponse)
def handle_youtube_analyze(req: YouTubeAnalyzeRequest, request: Request):
    """Processes a YouTube video link: extracts transcript, fact-checks against audited financials, synthesizes Q&A, and activates the Innovation Radar."""
    client_ip = get_client_ip(request)
    rate_limiter.check_rate_limit(client_ip, max_requests=settings.RATE_LIMIT_LLM_RPM, window_seconds=60)
    
    res = VideoIntelligenceEngine.analyze_youtube_video(
        url_or_video_id=req.url,
        user_query=req.query,
        symbol=req.symbol,
        language_pref=req.language_pref or "en",
        title=req.title or "Corporate Management Analysis"
    )
    return YouTubeAnalyzeResponse(**res)

