"""Append-only, point-in-time research data storage.

STORAGE_ROLE = "PRODUCTION_PERSISTENCE"

This module intentionally stores sourced observations rather than a mutable
"latest financials" record. Analyses can therefore ask what was known on a
given date and avoid silently introducing look-ahead bias.
"""

from __future__ import annotations

import os
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


from fastapi import HTTPException, status

from app.core.config import settings
from app.models.schemas import (
    BusinessEventIn,
    BusinessEventResponse,
    CompanyResponse,
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
from app.services.market_data import normalize_symbol


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def get_source_tier(source_name: str, confidence: float) -> str:
    """Assign data provenance Tier A-D based on source name and confidence level.

    Tier A (0.95–1.00): Regulatory exchange filings (BSE/NSE statutory disclosures, annual reports).
    Tier B (0.85–0.94): Primary market data APIs (yfinance, verified data feeds).
    Tier C (0.70–0.84): Aggregated financial research portals / news disclosures.
    Tier D (< 0.70): Unverified or estimated data.
    """
    name_upper = (source_name or "").upper()
    if "BSE" in name_upper or "NSE" in name_upper or "ANNUAL" in name_upper or confidence >= 0.95:
        return "Tier A"
    elif "YFINANCE" in name_upper or "PROPRIETARY" in name_upper or confidence >= 0.85:
        return "Tier B"
    elif "NEWS" in name_upper or confidence >= 0.70:
        return "Tier C"
    return "Tier D"


class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def __enter__(self):
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            try:
                self._conn.commit()
            except Exception:
                pass
        else:
            try:
                self._conn.rollback()
            except Exception:
                pass
        try:
            self._conn.close()
        except Exception:
            pass

    def __getattr__(self, attr):
        return getattr(self._conn, attr)


class ResearchDataStore:
    def __init__(self, database_path: Optional[str] = None):
        self.database_path = Path(database_path or settings.DATA_STORE_PATH)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        db_url = os.getenv("DATABASE_URL")
        if db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")):
            from app.services.db import get_connection
            return get_connection()
        connection = sqlite3.connect(self.database_path, timeout=30.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            connection.execute("PRAGMA journal_mode = WAL")
        except Exception:
            pass
        return SQLiteConnectionWrapper(connection)


    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    symbol TEXT PRIMARY KEY,
                    legal_name TEXT NOT NULL,
                    sector TEXT,
                    industry TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS financial_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL REFERENCES companies(symbol),
                    metric TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    currency TEXT,
                    period_end TEXT NOT NULL,
                    period_type TEXT NOT NULL,
                    statement_scope TEXT NOT NULL,
                    published_at TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    source_reference TEXT,
                    confidence REAL NOT NULL,
                    notes TEXT,
                    ingested_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_financial_lookup
                    ON financial_observations(symbol, metric, period_end, published_at);

                CREATE TABLE IF NOT EXISTS business_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL REFERENCES companies(symbol),
                    event_type TEXT NOT NULL,
                    announced_at TEXT NOT NULL,
                    effective_date TEXT,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    value REAL,
                    unit TEXT,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    source_reference TEXT,
                    confidence REAL NOT NULL,
                    ingested_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_event_lookup
                    ON business_events(symbol, announced_at);

                CREATE TABLE IF NOT EXISTS corporate_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL REFERENCES companies(symbol),
                    action_type TEXT NOT NULL,
                    ratio_numerator REAL,
                    ratio_denominator REAL,
                    amount_per_share REAL,
                    ex_date TEXT NOT NULL,
                    record_date TEXT,
                    announced_at TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    ingested_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_corporate_action_lookup
                    ON corporate_actions(symbol, ex_date, announced_at);

                CREATE TABLE IF NOT EXISTS ownership_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL REFERENCES companies(symbol),
                    period_end TEXT NOT NULL,
                    promoter_pct REAL NOT NULL,
                    fii_pct REAL NOT NULL,
                    dii_pct REAL NOT NULL,
                    mutual_fund_pct REAL,
                    insurance_pct REAL,
                    public_pct REAL NOT NULL,
                    aif_pct REAL,
                    promoter_pledge_pct REAL,
                    published_at TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    ingested_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_ownership_lookup
                    ON ownership_snapshots(symbol, period_end, published_at);

                CREATE TABLE IF NOT EXISTS document_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL REFERENCES companies(symbol),
                    document_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    financial_period TEXT,
                    document_date TEXT NOT NULL,
                    publication_date TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    metadata_json TEXT,
                    ingested_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_document_lookup
                    ON document_metadata(symbol, publication_date);

                CREATE TABLE IF NOT EXISTS market_daily_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL REFERENCES companies(symbol),
                    trading_date TEXT NOT NULL,
                    open_price REAL NOT NULL,
                    high_price REAL NOT NULL,
                    low_price REAL NOT NULL,
                    close_price REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    delivery_volume INTEGER,
                    delivery_pct REAL,
                    market_cap REAL,
                    published_at TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    ingested_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_market_daily_lookup
                    ON market_daily_snapshots(symbol, trading_date, published_at);

                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    company_name TEXT,
                    target_price REAL DEFAULT 0.0,
                    notes TEXT,
                    added_at TEXT NOT NULL
                );
                """
            )
        # Ensure universe discovery is seeded
        with self._connect() as conn:
            cnt = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        if cnt < 200:
            from app.services.ingestion.universe_discovery import seed_universe_companies
            seed_universe_companies(self)


    def upsert_company(self, request: Any) -> CompanyResponse:
        if isinstance(request, dict):
            if not request.get("symbol") or not request.get("legal_name"):
                raise HTTPException(status_code=400, detail="Missing required company fields")
            request = CompanyUpsertRequest(**request)
        symbol = normalize_symbol(request.symbol)
        now = _utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO companies(symbol, legal_name, sector, industry, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET
                    legal_name=excluded.legal_name,
                    sector=excluded.sector,
                    industry=excluded.industry
                """,
                (symbol, request.legal_name, request.sector, request.industry, now),
            )
        return self.get_company(symbol)

    def get_company(self, symbol: str) -> CompanyResponse:
        normalized = normalize_symbol(symbol)
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM companies WHERE symbol = ?", (normalized,)).fetchone()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No research-data company record for '{normalized}'.")
        return CompanyResponse(
            symbol=row["symbol"], legal_name=row["legal_name"], sector=row["sector"],
            industry=row["industry"], created_at=_parse_datetime(row["created_at"]),
        )

    def list_companies(self) -> list[CompanyResponse]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM companies ORDER BY symbol").fetchall()
        return [
            CompanyResponse(
                symbol=row["symbol"], legal_name=row["legal_name"], sector=row["sector"],
                industry=row["industry"], created_at=_parse_datetime(row["created_at"]),
            ) for row in rows
        ]


    def add_financial_observation(self, request: Any) -> FinancialObservationResponse:
        if isinstance(request, dict):
            try:
                request = FinancialObservationIn(**request)
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Invalid financial observation fields: {exc}")
        symbol = normalize_symbol(request.symbol)
        self.get_company(symbol)
        now = _utc_now().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO financial_observations(
                    symbol, metric, value, unit, currency, period_end, period_type, statement_scope,
                    published_at, source_name, source_url, source_reference, confidence, notes, ingested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol, request.metric, request.value, request.unit, request.currency,
                    request.period_end.isoformat(), request.period_type, request.statement_scope,
                    _as_utc(request.published_at).isoformat(), request.source_name, str(request.source_url),
                    request.source_reference, request.confidence, request.notes, now,
                ),
            )
            observation_id = cursor.lastrowid
        if not request.source_tier:
            request.source_tier = get_source_tier(request.source_name, request.confidence)
        return FinancialObservationResponse(id=observation_id, ingested_at=_parse_datetime(now), **request.model_dump())

    upsert_financial_observation = add_financial_observation

    def add_business_event(self, request: Any) -> BusinessEventResponse:
        if isinstance(request, dict):
            try:
                request = BusinessEventIn(**request)
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Invalid business event fields: {exc}")
        symbol = normalize_symbol(request.symbol)
        self.get_company(symbol)
        now = _utc_now().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO business_events(
                    symbol, event_type, announced_at, effective_date, title, summary, value, unit,
                    source_name, source_url, source_reference, confidence, ingested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol, request.event_type, _as_utc(request.announced_at).isoformat(),
                    request.effective_date.isoformat() if request.effective_date else None,
                    request.title, request.summary, request.value, request.unit, request.source_name,
                    str(request.source_url), request.source_reference, request.confidence, now,
                ),
            )
            event_id = cursor.lastrowid
        return BusinessEventResponse(id=event_id, ingested_at=_parse_datetime(now), **request.model_dump())

    def add_corporate_action(self, request: Any) -> CorporateActionResponse:
        if isinstance(request, dict):
            try:
                request = CorporateActionIn(**request)
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Invalid corporate action fields: {exc}")
        symbol = normalize_symbol(request.symbol)
        self.get_company(symbol)
        now = _utc_now().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO corporate_actions(
                    symbol, action_type, ratio_numerator, ratio_denominator, amount_per_share,
                    ex_date, record_date, announced_at, source_name, source_url, confidence, ingested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol, request.action_type, request.ratio_numerator, request.ratio_denominator,
                    request.amount_per_share, request.ex_date.isoformat(),
                    request.record_date.isoformat() if request.record_date else None,
                    _as_utc(request.announced_at).isoformat(), request.source_name, str(request.source_url),
                    request.confidence, now,
                ),
            )
            action_id = cursor.lastrowid
        return CorporateActionResponse(
            id=action_id, ingested_at=_parse_datetime(now), adjustment_factor=1.0, **request.model_dump()
        )

    def add_ownership_snapshot(self, request: Any) -> OwnershipSnapshotResponse:
        if isinstance(request, dict):
            try:
                request = OwnershipSnapshotIn(**request)
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Invalid ownership snapshot fields: {exc}")
        symbol = normalize_symbol(request.symbol)
        self.get_company(symbol)
        now = _utc_now().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO ownership_snapshots(
                    symbol, period_end, promoter_pct, fii_pct, dii_pct, mutual_fund_pct,
                    insurance_pct, public_pct, aif_pct, promoter_pledge_pct, published_at,
                    source_name, source_url, confidence, ingested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol, request.period_end.isoformat(), request.promoter_pct, request.fii_pct,
                    request.dii_pct, request.mutual_fund_pct, request.insurance_pct, request.public_pct,
                    request.aif_pct, request.promoter_pledge_pct, _as_utc(request.published_at).isoformat(),
                    request.source_name, str(request.source_url), request.confidence, now,
                ),
            )
            snapshot_id = cursor.lastrowid
        return OwnershipSnapshotResponse(id=snapshot_id, ingested_at=_parse_datetime(now), **request.model_dump())

    def add_document_metadata(self, request: Any) -> DocumentMetadataResponse:
        if isinstance(request, dict):
            try:
                request = DocumentMetadataIn(**request)
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Invalid document metadata fields: {exc}")
        symbol = normalize_symbol(request.symbol)
        self.get_company(symbol)
        now = _utc_now().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO document_metadata(
                    symbol, document_type, title, financial_period, document_date, publication_date,
                    source_name, source_url, confidence, metadata_json, ingested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol, request.document_type, request.title, request.financial_period,
                    request.document_date.isoformat(), _as_utc(request.publication_date).isoformat(),
                    request.source_name, str(request.source_url), request.confidence,
                    json.dumps(request.metadata_json or {}), now,
                ),
            )
            doc_id = cursor.lastrowid
        return DocumentMetadataResponse(id=doc_id, ingested_at=_parse_datetime(now), **request.model_dump())

    def add_market_daily_snapshot(self, request: Any) -> MarketDailySnapshotResponse:
        if isinstance(request, dict):
            try:
                request = MarketDailySnapshotIn(**request)
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Invalid market snapshot fields: {exc}")
        symbol = normalize_symbol(request.symbol)
        self.get_company(symbol)
        now = _utc_now().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO market_daily_snapshots(
                    symbol, trading_date, open_price, high_price, low_price, close_price,
                    volume, delivery_volume, delivery_pct, market_cap, published_at,
                    source_name, source_url, ingested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol, request.trading_date.isoformat(), request.open_price, request.high_price,
                    request.low_price, request.close_price, request.volume, request.delivery_volume,
                    request.delivery_pct, request.market_cap, _as_utc(request.published_at).isoformat(),
                    request.source_name, str(request.source_url), now,
                ),
            )
            snap_id = cursor.lastrowid
        return MarketDailySnapshotResponse(
            id=snap_id, adj_close_price=request.close_price, adjustment_factor=1.0,
            ingested_at=_parse_datetime(now), **request.model_dump()
        )

    def get_timeline(
        self, symbol: str, as_of: Optional[datetime] = None
    ) -> tuple[
        CompanyResponse,
        list[FinancialObservationResponse],
        list[BusinessEventResponse],
        list[CorporateActionResponse],
        list[OwnershipSnapshotResponse],
        list[DocumentMetadataResponse],
    ]:
        company = self.get_company(symbol)
        cutoff = _as_utc(as_of or _utc_now()).isoformat()
        with self._connect() as conn:
            financial_rows = conn.execute(
                "SELECT * FROM financial_observations WHERE symbol = ? AND published_at <= ? ORDER BY period_end, published_at, id",
                (company.symbol, cutoff),
            ).fetchall()
            event_rows = conn.execute(
                "SELECT * FROM business_events WHERE symbol = ? AND announced_at <= ? ORDER BY announced_at, id",
                (company.symbol, cutoff),
            ).fetchall()
            corp_rows = conn.execute(
                "SELECT * FROM corporate_actions WHERE symbol = ? AND announced_at <= ? ORDER BY ex_date, announced_at, id",
                (company.symbol, cutoff),
            ).fetchall()
            ownership_rows = conn.execute(
                "SELECT * FROM ownership_snapshots WHERE symbol = ? AND published_at <= ? ORDER BY period_end, published_at, id",
                (company.symbol, cutoff),
            ).fetchall()
            doc_rows = conn.execute(
                "SELECT * FROM document_metadata WHERE symbol = ? AND publication_date <= ? ORDER BY publication_date, id",
                (company.symbol, cutoff),
            ).fetchall()

        financials = [
            FinancialObservationResponse(
                id=row["id"], symbol=row["symbol"], metric=row["metric"], value=row["value"], unit=row["unit"],
                currency=row["currency"], period_end=row["period_end"], period_type=row["period_type"],
                statement_scope=row["statement_scope"], published_at=_parse_datetime(row["published_at"]),
                source_name=row["source_name"], source_url=row["source_url"], source_reference=row["source_reference"],
                confidence=row["confidence"], source_tier=get_source_tier(row["source_name"], row["confidence"]),
                notes=row["notes"], ingested_at=_parse_datetime(row["ingested_at"]),
            ) for row in financial_rows
        ]
        events = [
            BusinessEventResponse(
                id=row["id"], symbol=row["symbol"], event_type=row["event_type"],
                announced_at=_parse_datetime(row["announced_at"]), effective_date=row["effective_date"],
                title=row["title"], summary=row["summary"], value=row["value"], unit=row["unit"],
                source_name=row["source_name"], source_url=row["source_url"], source_reference=row["source_reference"],
                confidence=row["confidence"], ingested_at=_parse_datetime(row["ingested_at"]),
            ) for row in event_rows
        ]
        corp_actions = [
            CorporateActionResponse(
                id=row["id"], symbol=row["symbol"], action_type=row["action_type"],
                ratio_numerator=row["ratio_numerator"], ratio_denominator=row["ratio_denominator"],
                amount_per_share=row["amount_per_share"], ex_date=row["ex_date"], record_date=row["record_date"],
                announced_at=_parse_datetime(row["announced_at"]), source_name=row["source_name"],
                source_url=row["source_url"], confidence=row["confidence"],
                ingested_at=_parse_datetime(row["ingested_at"]), adjustment_factor=1.0,
            ) for row in corp_rows
        ]
        ownership = [
            OwnershipSnapshotResponse(
                id=row["id"], symbol=row["symbol"], period_end=row["period_end"],
                promoter_pct=row["promoter_pct"], fii_pct=row["fii_pct"], dii_pct=row["dii_pct"],
                mutual_fund_pct=row["mutual_fund_pct"], insurance_pct=row["insurance_pct"],
                public_pct=row["public_pct"], aif_pct=row["aif_pct"], promoter_pledge_pct=row["promoter_pledge_pct"],
                published_at=_parse_datetime(row["published_at"]), source_name=row["source_name"],
                source_url=row["source_url"], confidence=row["confidence"],
                ingested_at=_parse_datetime(row["ingested_at"]),
            ) for row in ownership_rows
        ]
        documents = [
            DocumentMetadataResponse(
                id=row["id"], symbol=row["symbol"], document_type=row["document_type"],
                title=row["title"], financial_period=row["financial_period"], document_date=row["document_date"],
                publication_date=_parse_datetime(row["publication_date"]), source_name=row["source_name"],
                source_url=row["source_url"], confidence=row["confidence"],
                metadata_json=json.loads(row["metadata_json"]) if row["metadata_json"] else {},
                ingested_at=_parse_datetime(row["ingested_at"]),
            ) for row in doc_rows
        ]

        return company, financials, events, corp_actions, ownership, documents

    def get_watchlist(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM watchlist ORDER BY added_at DESC").fetchall()
        return [dict(r) for r in rows]

    def add_to_watchlist(self, symbol: str, company_name: str = "", target_price: float = 0.0, notes: str = "") -> dict:
        norm_symbol = normalize_symbol(symbol)
        now = _utc_now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO watchlist(symbol, company_name, target_price, notes, added_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET
                    company_name=excluded.company_name,
                    target_price=excluded.target_price,
                    notes=excluded.notes
                """,
                (norm_symbol, company_name, target_price, notes, now)
            )
            row = conn.execute("SELECT * FROM watchlist WHERE symbol = ?", (norm_symbol,)).fetchone()
        return dict(row)

    def remove_from_watchlist(self, symbol: str) -> bool:
        norm_symbol = normalize_symbol(symbol)
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM watchlist WHERE symbol = ?", (norm_symbol,))
        return cursor.rowcount > 0

    def get_point_in_time_snapshot(self, symbol: str, as_of: Optional[datetime] = None) -> Dict[str, Any]:
        """Returns point-in-time financial and event snapshot filtered strictly by published_at <= cutoff."""
        timeline = self.get_timeline(symbol, as_of=as_of)
        company, financials, events, corp_actions, ownership, docs = timeline
        return {
            "symbol": company.symbol,
            "company_name": company.company_name,
            "as_of_cutoff": (as_of or _utc_now()).isoformat(),
            "financial_count": len(financials),
            "event_count": len(events),
            "corporate_action_count": len(corp_actions),
            "ownership_count": len(ownership),
            "document_count": len(docs),
            "latest_financials": [f.model_dump() for f in financials[-10:]]
        }

    def get_market_daily_snapshot(self, symbol: str, as_of_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve the nearest historical daily snapshot on or before as_of_date."""
        norm_symbol = normalize_symbol(symbol)
        with self._connect() as conn:
            if as_of_date:
                cutoff = str(as_of_date)[:10]
                row = conn.execute(
                    "SELECT * FROM market_daily_snapshots WHERE symbol = ? AND trading_date <= ? ORDER BY trading_date DESC LIMIT 1",
                    (norm_symbol, cutoff),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM market_daily_snapshots WHERE symbol = ? ORDER BY trading_date DESC LIMIT 1",
                    (norm_symbol,),
                ).fetchone()
            if row:
                return dict(row)
        return None


