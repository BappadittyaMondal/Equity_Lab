"""Phase 139 Research API — MAP-Rank, β_geo Shock Matrix, Multimodal Watchlist Bridge.

Endpoints:
  POST /api/v1/research/rank-candidates          → MAP-Rank Pareto tournament
  GET  /api/v1/research/geopolitical-shock-sensitivity/{symbol}  → β_geo 5-shock vector
  POST /api/v1/research/multimodal-watchlist-audit              → Watchlist image/symbols → full audit
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional

from app.models.schemas import (
    MultiAssetRankRequest,
    MultiAssetRankResponse,
    GeoShockSensitivityResponse,
    MultimodalWatchlistRequest,
    MultimodalWatchlistResponse,
)
from app.services.market_data import create_meta_header, get_ist_now_str

router = APIRouter(prefix="/api/v1/research", tags=["Research Engines — Phase 139"])


@router.post(
    "/rank-candidates",
    response_model=MultiAssetRankResponse,
    summary="MAP-Rank: Multi-Asset Pareto Ranking Tournament (Phase 139)",
)
def rank_candidates_endpoint(request: MultiAssetRankRequest):
    """Cross-sectional Pareto 4-dimension ranking of N candidate stocks.

    Scores each stock simultaneously on:
    - Solvency (D/E, interest coverage)
    - Cash Quality (CAQI = CFO / PAT ≥ 0.80 gate)
    - Valuation Headroom (DEME-HR = sector P/E ceiling / trailing P/E)
    - Geopolitical Moat (aggregate β_geo from 5-shock sensitivity matrix)

    Returns ranked list sorted by intent-weighted composite score.
    """
    try:
        from app.services.research.map_rank_engine import build_map_rank_response
        result = build_map_rank_response(
            symbols=request.symbols,
            intent=request.intent,
            top_n=request.top_n,
        )
        # Validate and return via response model
        return MultiAssetRankResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MAP-Rank tournament failed: {str(exc)}",
        )


@router.get(
    "/geopolitical-shock-sensitivity/{symbol}",
    response_model=GeoShockSensitivityResponse,
    summary="β_geo Vectorized Geopolitical Shock Sensitivity (Phase 139)",
)
def get_geo_shock_sensitivity(
    symbol: str,
    sector: Optional[str] = Query(
        default=None,
        description="Sector key (e.g. DEFENSE, IT, METALS). Auto-detected from ticker overlays if omitted.",
    ),
):
    """Returns asset-level β_geo shock sensitivity vector across 5 global scenarios:

    1. Crude Oil Spike +30%
    2. Maritime Chokepoint (Red Sea / Hormuz)
    3. China Export Dumping
    4. Grid Hardware Deficit (transformers / semiconductors)
    5. US Interest Rate Hike +100bps

    Beta convention: positive = tailwind, negative = headwind (range: -1.0 to +1.0).
    """
    try:
        from app.services.research.geopolitical_engine import compute_geo_shock_sensitivity
        result = compute_geo_shock_sensitivity(symbol, sector=sector)
        return GeoShockSensitivityResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"β_geo shock sensitivity failed for {symbol}: {str(exc)}",
        )


@router.post(
    "/multimodal-watchlist-audit",
    response_model=MultimodalWatchlistResponse,
    summary="Multimodal Watchlist Bridge: Image/Symbols → Full Audit (Phase 139)",
)
def multimodal_watchlist_audit(request: MultimodalWatchlistRequest):
    """Full Multimodal Watchlist Audit Pipeline:

    1. (Optional) Gemini Vision OCR extracts ticker symbols from a brokerage screenshot.
    2. ScreenerCloudConnector fetches fundamentals for each symbol.
    3. InstitutionalMultibaggerEngine audits each symbol (CAQI gate, DEME-HR, risk flags).
    4. MAP-Rank Pareto tournament ranks all symbols cross-sectionally.

    Supply either `image_base64` (screenshot) or `raw_symbols` (pre-parsed list).
    If both supplied, `raw_symbols` takes precedence (skips OCR).
    """
    try:
        from app.services.research.multimodal_watchlist_bridge import audit_watchlist
        result = audit_watchlist(
            image_base64=request.image_base64,
            raw_symbols=request.raw_symbols,
            intent=request.intent,
        )
        return MultimodalWatchlistResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multimodal watchlist audit failed: {str(exc)}",
        )
