"""Protected ingest and read-only timeline endpoints for sourced research data."""

import hmac
from datetime import datetime

from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import settings
from app.models.schemas import (
    BusinessEventIn,
    BusinessEventResponse,
    CompanyResponse,
    CompanyTimelineResponse,
    CompanyUpsertRequest,
    CorporateActionIn,
    CorporateActionResponse,
    DocumentMetadataIn,
    DocumentMetadataResponse,
    FinancialObservationIn,
    FinancialObservationResponse,
    MarketDailySnapshotIn,
    MarketDailySnapshotResponse,
    OwnershipSnapshotIn,
    OwnershipSnapshotResponse,
)
from app.services.market_data import create_meta_header
from app.services.research_data import ResearchDataStore

router = APIRouter(prefix="/api/v1/data", tags=["Point-in-Time Research Data"])


def _require_write_key(x_data_write_key: str = Header(default="")) -> None:
    if not settings.DATA_WRITE_API_KEY:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Data ingestion is disabled until DATA_WRITE_API_KEY is configured.")
    if not hmac.compare_digest(x_data_write_key, settings.DATA_WRITE_API_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Valid data-write authentication is required.")


@router.post("/companies", response_model=CompanyResponse, dependencies=[])
def upsert_company(request: CompanyUpsertRequest, x_data_write_key: str = Header(default="")):
    _require_write_key(x_data_write_key)
    return ResearchDataStore().upsert_company(request)


@router.post("/financial-observations", response_model=FinancialObservationResponse)
def add_financial_observation(request: FinancialObservationIn, x_data_write_key: str = Header(default="")):
    _require_write_key(x_data_write_key)
    return ResearchDataStore().add_financial_observation(request)


@router.post("/business-events", response_model=BusinessEventResponse)
def add_business_event(request: BusinessEventIn, x_data_write_key: str = Header(default="")):
    _require_write_key(x_data_write_key)
    return ResearchDataStore().add_business_event(request)


@router.post("/corporate-actions", response_model=CorporateActionResponse)
def add_corporate_action(request: CorporateActionIn, x_data_write_key: str = Header(default="")):
    _require_write_key(x_data_write_key)
    return ResearchDataStore().add_corporate_action(request)


@router.post("/ownership-snapshots", response_model=OwnershipSnapshotResponse)
def add_ownership_snapshot(request: OwnershipSnapshotIn, x_data_write_key: str = Header(default="")):
    _require_write_key(x_data_write_key)
    return ResearchDataStore().add_ownership_snapshot(request)


@router.post("/document-metadata", response_model=DocumentMetadataResponse)
def add_document_metadata(request: DocumentMetadataIn, x_data_write_key: str = Header(default="")):
    _require_write_key(x_data_write_key)
    return ResearchDataStore().add_document_metadata(request)


@router.post("/market-snapshots", response_model=MarketDailySnapshotResponse)
def add_market_daily_snapshot(request: MarketDailySnapshotIn, x_data_write_key: str = Header(default="")):
    _require_write_key(x_data_write_key)
    return ResearchDataStore().add_market_daily_snapshot(request)


@router.get("/companies/{symbol}/timeline", response_model=CompanyTimelineResponse)
def get_company_timeline(symbol: str, as_of: datetime | None = None):
    company, financials, events, corp_actions, ownership, documents = ResearchDataStore().get_timeline(symbol, as_of=as_of)
    return CompanyTimelineResponse(
        company=company,
        as_of=as_of,
        financial_observations=financials,
        business_events=events,
        corporate_actions=corp_actions,
        ownership_snapshots=ownership,
        document_metadata=documents,
        meta=create_meta_header(source="IERL append-only research data store"),
    )


@router.get("/lifecycle/{symbol}")
def get_lifecycle_state(symbol: str):
    from app.services.longitudinal.lifecycle_engine import LifecycleEngine
    from app.services.decision_brain.arbiter import Arbiter
    arbiter = Arbiter()
    call = arbiter.arbitrate(symbol)
    engine_outputs = arbiter._collect_engine_outputs(symbol)
    lifecycle = LifecycleEngine().evaluate_lifecycle(symbol, engine_outputs, call.conviction_score)
    return lifecycle


@router.get("/thesis/{symbol}")
def get_thesis_state(symbol: str):
    from app.services.longitudinal.thesis_monitor import ThesisMonitorEngine
    from app.services.decision_brain.arbiter import Arbiter
    arbiter = Arbiter()
    call = arbiter.arbitrate(symbol)
    thesis = ThesisMonitorEngine().evaluate_thesis_state(
        symbol=symbol,
        conviction_score=call.conviction_score,
        verdict=call.verdict,
        contradictions=call.contradicting_engines,
        primary_thesis=call.primary_thesis,
    )
    return thesis


@router.get("/alerts")
def get_alerts(limit: int = 50, symbol: str | None = None):
    from app.services.longitudinal.alert_engine import AlertEngine
    return AlertEngine().get_recent_alerts(limit=limit, symbol=symbol)


@router.post("/custom-screen")
def run_custom_screen(payload: dict):
    """Execute custom Screener.in query or preset, with optional 27-factor Multibagger Brain ranking."""
    from app.services.research.custom_screener import CustomScreenerEngine, CANONICAL_SCREENER_ARCHETYPES

    if payload.get("get_archetypes") or payload.get("action") == "get_archetypes":
        return {
            "total_archetypes": len(CANONICAL_SCREENER_ARCHETYPES),
            "archetypes": CANONICAL_SCREENER_ARCHETYPES
        }

    query_str = payload.get("query", "")
    preset = payload.get("preset")
    rank_with_brain = payload.get("rank_with_multibagger_brain", False)
    min_score = float(payload.get("min_multibagger_score", 65.0))
    top_n = int(payload.get("top_n", 5))

    if rank_with_brain:
        return CustomScreenerEngine.execute_institutional_funnel(
            query_string=query_str or None,
            preset_name=preset,
            min_multibagger_score=min_score,
            top_n=top_n
        )

    if preset:
        if preset in CANONICAL_SCREENER_ARCHETYPES:
            query_str = CANONICAL_SCREENER_ARCHETYPES[preset]["query"]

    return CustomScreenerEngine.execute_query(query_str)


@router.post("/causal-inference")
def run_causal_inference(payload: dict):
    from app.services.research.causal_engine import analyze_causal_event_impacts
    symbol = payload.get("symbol", "RELIANCE")
    return analyze_causal_event_impacts(symbol=symbol)


@router.get("/thesis-tracker/{symbol}")
def get_thesis_tracker(symbol: str):
    from app.services.research.thesis_tracker import ThesisTracker
    tracker = ThesisTracker()
    thesis = tracker.create_thesis(
        symbol=symbol,
        primary_thesis="High-growth fundamental compounder with expanding return on capital",
        confidence_score=80.0
    )
    evaluated = tracker.evaluate_thesis(
        thesis.thesis_id,
        {"cfo_ebitda_ratio": 0.85, "promoter_pledge_pct": 2.5, "quarterly_revenue_growth_pct": 18.5}
    )
    return evaluated




