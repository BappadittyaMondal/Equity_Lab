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
    PreEventEvaluationRequest,
    PreEventEvaluationResponse,
    PhysicalDisruptionGateRequest,
    PhysicalDisruptionGateResponse,
    GeopoliticalEventLogRequest,
    GeopoliticalEventLogResponse,
    GeopoliticalEventCalibrateRequest,
    GeopoliticalEventCalibrateResponse,
    IPOLookupRequest,
    IPOLookupResponse,
    IPOPipelineResponse,
    WeakSignalIngestRequest,
    WeakSignalIngestResponse,
    GeopoliticalAutoCollectRequest,
    GeopoliticalAutoCollectResponse,
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
    summary="β_geo Vectorized Geopolitical Shock Sensitivity (Phase 139/140)",
)
def get_geo_shock_sensitivity(
    symbol: str,
    sector: Optional[str] = Query(
        default=None,
        description="Sector key (e.g. DEFENSE, IT, METALS). Auto-detected from ticker overlays if omitted.",
    ),
    sub_segment: Optional[str] = Query(
        default=None,
        description="Optional specialized sub-segment (e.g. TANKERS, CONTAINER_CARGO).",
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
        result = compute_geo_shock_sensitivity(symbol, sector=sector, sub_segment=sub_segment)
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


# ── Phase 140: Geopolitical PEWS, PDLR Gate, & Event Self-Learning Endpoints ──

@router.post(
    "/geopolitical/pre-event-eval",
    response_model=PreEventEvaluationResponse,
    summary="PEWS: Pre-Event Weak Signal Bayesian Imminence Evaluator (Phase 140)",
)
def evaluate_pews_endpoint(request: PreEventEvaluationRequest):
    """Evaluates heterogeneous weak signals (NOTAMs, AIS dark transponders, diplomatic collapses,
    crude call option skews, leader signaling) using Bayesian log-odds updating.
    """
    try:
        from app.services.research.geopolitical_engine import PreEventSignal, evaluate_pre_event_weak_signals
        signals = [
            PreEventSignal(
                signal_type=s.signal_type,
                intensity=s.intensity,
                likelihood_ratio=s.likelihood_ratio,
                confidence=s.confidence,
                age_hours=s.age_hours,
                theater=s.theater,
                source_description=s.source_description,
            )
            for s in request.signals
        ]
        res = evaluate_pre_event_weak_signals(
            signals=signals,
            prior_probability=request.prior_probability,
            theater=request.theater,
        )
        return PreEventEvaluationResponse(**res)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PEWS evaluation failed: {str(exc)}",
        )


@router.post(
    "/geopolitical/pdlr-gate-eval",
    response_model=PhysicalDisruptionGateResponse,
    summary="PDLR Gate: Physical Disruption vs Political Theater Evaluator (Phase 140)",
)
def evaluate_pdlr_endpoint(request: PhysicalDisruptionGateRequest):
    """Physical Disruption Likelihood Ratio (PDLR) Gate.

    Distinguishes symbolic political rhetoric / posturing (PDLR < 0.40) from
    actual physical supply destruction / blockade (PDLR >= 0.40).
    """
    try:
        from app.services.research.geopolitical_engine import evaluate_physical_disruption_gate
        res = evaluate_physical_disruption_gate(
            pdlr=request.pdlr,
            raw_overlay_pct=request.raw_overlay_pct,
            sector=request.sector,
        )
        return PhysicalDisruptionGateResponse(**res)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDLR gate evaluation failed: {str(exc)}",
        )


@router.post(
    "/geopolitical/log-event",
    response_model=GeopoliticalEventLogResponse,
    summary="Log Pre-Event Prediction to Event Prediction Ledger (Phase 140)",
)
def log_geopolitical_event_endpoint(request: GeopoliticalEventLogRequest):
    """Persists a pre-event geopolitical prediction into the event prediction ledger."""
    try:
        from app.services.monitoring.event_prediction_ledger import EventPredictionLedgerService
        rec = EventPredictionLedgerService.log_geopolitical_event(
            event_id=request.event_id,
            title=request.title,
            event_type=request.event_type,
            theater=request.theater,
            pews_probability=request.pews_probability,
            pdlr_ratio=request.pdlr_ratio,
            pdlr_classification=request.pdlr_classification,
            shock_vector=request.shock_vector,
            predicted_betas=request.predicted_betas,
            notes=request.notes,
        )
        return GeopoliticalEventLogResponse(
            event_id=rec.event_id,
            title=rec.title,
            event_type=rec.event_type,
            theater=rec.theater,
            status=rec.status,
            pews_probability=rec.pews_probability,
            pdlr_ratio=rec.pdlr_ratio,
            pdlr_classification=rec.pdlr_classification,
            shock_vector=rec.shock_vector,
            predicted_betas=rec.predicted_betas,
            created_at=rec.created_at,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event logging failed: {str(exc)}",
        )


@router.post(
    "/geopolitical/calibrate-event",
    response_model=GeopoliticalEventCalibrateResponse,
    summary="Execute Bayesian Kalman Self-Learning Beta Calibration (Phase 140)",
)
def calibrate_geopolitical_event_endpoint(request: GeopoliticalEventCalibrateRequest):
    """Records empirical shock moves and triggers recursive Bayesian Kalman beta calibration."""
    try:
        from app.services.monitoring.event_prediction_ledger import EventPredictionLedgerService
        res = EventPredictionLedgerService.record_event_market_realization(
            event_id=request.event_id,
            realized_shock=request.realized_shock,
            empirical_asset_returns=request.empirical_asset_returns,
            event_occurred=request.event_occurred,
            benchmark_symbol=request.benchmark_symbol,
        )
        return GeopoliticalEventCalibrateResponse(**res)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event calibration failed: {str(exc)}",
        )


# ── Phase 143: IPO Intelligence & Listing Gain Probability Endpoints ──

@router.post(
    "/ipo/listing-gain-eval",
    response_model=IPOLookupResponse,
    summary="IPO Listing Gain Probability Evaluator (Phase 143)",
)
def evaluate_ipo_listing_gain_endpoint(request: IPOLookupRequest):
    """Evaluates 5-factor quantitative listing gain probability for an upcoming NSE/BSE IPO:
    P(Gain) = 0.35*QIB + 0.30*GMP + 0.15*ValuationHeadroom + 0.10*MarketTrend + 0.10*IssueStructure.
    """
    try:
        from app.services.research.ipo_intelligence_engine import (
            IPOIntelligenceEngine,
            IPOEvaluationInput,
            IPOSubscriptionData,
            IPOIssueStructure,
            IPOValuationMetrics,
        )

        inp = IPOEvaluationInput(
            company_name=request.company_name,
            symbol=request.symbol,
            sector=request.sector,
            gmp_inr=request.gmp_inr,
            subscription=IPOSubscriptionData(
                qib_multiple=request.qib_multiple,
                nii_multiple=request.nii_multiple,
                rii_multiple=request.rii_multiple,
                total_multiple=request.total_multiple,
            ),
            structure=IPOIssueStructure(
                total_issue_size_cr=request.total_issue_size_cr,
                fresh_issue_cr=request.fresh_issue_cr,
                offer_for_sale_cr=request.offer_for_sale_cr,
                price_band_lower=request.price_band_lower,
                price_band_upper=request.price_band_upper,
                post_issue_promoter_holding_pct=request.post_issue_promoter_holding_pct,
                anchor_lockin_days=request.anchor_lockin_days,
            ),
            valuation=IPOValuationMetrics(
                implied_pe=request.implied_pe,
                peer_median_pe=request.peer_median_pe,
                implied_pb=request.implied_pb,
                peer_median_pb=request.peer_median_pb,
                roe_pct=request.roe_pct,
                pat_cagr_3y_pct=request.pat_cagr_3y_pct,
            ),
            market_regime_favorable=request.market_regime_favorable,
            india_vix=request.india_vix,
        )

        res = IPOIntelligenceEngine.evaluate_listing_gain(inp)
        res_dict = res.model_dump()
        res_dict["meta"] = create_meta_header(source=f"Phase 143 IPOIntelligenceEngine ({request.company_name})")
        return IPOLookupResponse(**res_dict)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"IPO listing gain evaluation failed: {str(exc)}",
        )


@router.get(
    "/ipo/pipeline",
    response_model=IPOPipelineResponse,
    summary="Pre-IPO & Unlisted Indian Company Pipeline (Phase 143)",
)
def get_ipo_pipeline_endpoint():
    """Returns verified pipeline of top upcoming unlisted Indian companies (NSE, Tata Capital, HDB, NSDL, etc.)."""
    try:
        from app.services.research.ipo_intelligence_engine import IPOIntelligenceEngine
        pipeline = IPOIntelligenceEngine.get_pipeline()
        return IPOPipelineResponse(
            pipeline=pipeline,
            count=len(pipeline),
            summary=f"Retrieved {len(pipeline)} institutional pre-IPO/unlisted candidate profiles.",
            meta=create_meta_header(source="Phase 143 IPO Pipeline Registry"),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch IPO pipeline: {str(exc)}",
        )


# ── Phase 144: Weak Signal Automated Ingestion Endpoint ──

@router.post(
    "/geopolitical/ingest-weak-signal",
    response_model=WeakSignalIngestResponse,
    summary="Ingest & Parse Weak Geopolitical Signals (Phase 144)",
)
def ingest_weak_signal_endpoint(request: WeakSignalIngestRequest):
    """Parses raw text/OSINT headlines for leader symbolic anomalies, NOTAMs, AIS transponders,
    and calculates posterior imminence probability.
    """
    try:
        from app.services.research.weak_signal_parser import WeakSignalParserService
        res = WeakSignalParserService.ingest_and_evaluate(
            text=request.text,
            source=request.source,
            prior_probability=request.prior_probability,
            age_hours=request.age_hours,
        )
        res["meta"] = create_meta_header(source="Phase 144 WeakSignalParserService")
        return WeakSignalIngestResponse(**res)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Weak signal ingestion failed: {str(exc)}",
        )


# ── Phase 145: Closed-Loop Geopolitical Outcome Collector Endpoint ──

@router.post(
    "/geopolitical/auto-collect-outcomes",
    response_model=GeopoliticalAutoCollectResponse,
    summary="Trigger Autonomous Geopolitical Outcome Collection Cycle (Phase 145)",
)
def auto_collect_geopolitical_outcomes_endpoint(request: GeopoliticalAutoCollectRequest):
    """Scans pending predictions, derives market realizations, and executes Bayesian Kalman updates."""
    try:
        from app.services.monitoring.geopolitical_outcome_collector import GeopoliticalOutcomeCollector
        res = GeopoliticalOutcomeCollector.collect_and_calibrate(
            min_age_hours=request.min_age_hours,
            force_event_id=request.force_event_id,
            custom_realized_shock=request.custom_realized_shock,
            custom_empirical_returns=request.custom_empirical_returns,
            event_occurred=request.event_occurred,
            benchmark_symbol=request.benchmark_symbol,
        )
        return GeopoliticalAutoCollectResponse(**res.model_dump())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Autonomous outcome collection failed: {str(exc)}",
        )

