"""Health and diagnostic status router.
"""

import os
from fastapi import APIRouter
from app.core.config import settings
from app.services.market_data import get_ist_now_str
import yfinance as yf

router = APIRouter(prefix="/api/v1", tags=["Health & Diagnostics"])


@router.get("/health")
def get_health_status():
    """Runs actual connectivity verification across data feeds and LLM providers."""
    providers_status = {}
    
    # 1. Live market data provider test
    try:
        t = yf.Ticker("^NSEI")
        hist = t.history(period="1d")
        if not hist.empty:
            providers_status["yfinance_nse"] = "ONLINE"
        else:
            providers_status["yfinance_nse"] = "DEGRADED (Empty Data)"
    except Exception as e:
        providers_status["yfinance_nse"] = f"OFFLINE ({str(e)})"
        
    # 2. LLM Provider Status
    gemini_key = settings.GEMINI_API_KEY
    providers_status["gemini_llm"] = "CONFIGURED" if (gemini_key and "your_" not in gemini_key.lower()) else "UNCONFIGURED"
    
    groq_key = settings.GROQ_API_KEY
    providers_status["groq_llm"] = "CONFIGURED" if (groq_key and "your_" not in groq_key.lower()) else "UNCONFIGURED"

    return {
        "status": "ONLINE",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp_ist": get_ist_now_str(),
        "providers_status": providers_status,
        "active_llm": settings.ACTIVE_LLM_PROVIDER
    }
