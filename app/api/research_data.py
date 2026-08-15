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

