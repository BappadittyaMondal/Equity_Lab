"""Point-in-Time Regulatory Filing Document Store.

Ingests, indexes, and retrieves BSE corporate disclosures, Annual Reports, DRHP prospectuses,
and Earnings Call Transcripts with SHA256 cryptographic provenance and strict point-in-time temporal boundaries.
"""

import os
import hashlib
import json
import sqlite3
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.core.config import settings


@dataclass
class FilingDocument:
    symbol: str
    doc_type: str  # "BSE_ANNOUNCEMENT", "ANNUAL_REPORT", "CONCALL_TRANSCRIPT", "DRHP"
    effective_date: str  # ISO format "YYYY-MM-DD"
    title: str
    content: str
    document_hash: str = ""
    section: Optional[str] = None
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.document_hash:
            raw = f"{self.symbol}:{self.doc_type}:{self.effective_date}:{self.title}:{self.content}"
            self.document_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()


class FilingDocumentStore:
    """SQLite-backed Point-in-Time Document Store for Regulatory Filings."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATA_STORE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        db_url = os.getenv("DATABASE_URL")
        if db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")):
            from app.services.db import get_connection
            return get_connection()
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS filing_documents (
                document_hash TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                effective_date TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                section TEXT,
                page_number INTEGER,
                metadata_json TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_filing_symbol_date ON filing_documents(symbol, effective_date)")
        conn.commit()
        conn.close()

    def add_document(self, doc: FilingDocument) -> str:
        """Add a regulatory document to the store."""
        conn = self._get_connection()
        conn.execute("""
            INSERT OR REPLACE INTO filing_documents 
            (document_hash, symbol, doc_type, effective_date, title, content, section, page_number, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc.document_hash,
            doc.symbol.upper(),
            doc.doc_type,
            doc.effective_date,
            doc.title,
            doc.content,
            doc.section,
            doc.page_number,
            json.dumps(doc.metadata),
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
        conn.close()
        return doc.document_hash

    def search_documents(
        self,
        symbol: str,
        query: str,
        as_of_date: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search regulatory documents with strict point-in-time filtering and term relevance scoring."""
        conn = self._get_connection()
        symbol_clean = symbol.upper()
        
        sql = "SELECT * FROM filing_documents WHERE symbol = ?"
        params = [symbol_clean]
        
        if as_of_date:
            sql += " AND effective_date <= ?"
            params.append(as_of_date)
            
        sql += " ORDER BY effective_date DESC LIMIT 100"
        
        rows = conn.execute(sql, params).fetchall()
        conn.close()

        if not rows:
            return []

        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        scored_results = []

        for row in rows:
            content = row["content"]
            title = row["title"]
            text_lower = f"{title} {content}".lower()

            # Compute term overlap score
            match_count = sum(1 for term in query_terms if term in text_lower)
            if match_count == 0 and query_terms:
                continue

            score = (match_count / max(1, len(query_terms))) if query_terms else 0.5
            
            scored_results.append({
                "document_hash": row["document_hash"],
                "symbol": row["symbol"],
                "doc_type": row["doc_type"],
                "effective_date": row["effective_date"],
                "title": row["title"],
                "content": content[:1000],  # Return snippet
                "section": row["section"],
                "page_number": row["page_number"],
                "relevance_score": round(score, 4),
                "metadata": json.loads(row["metadata_json"] or "{}")
            })

        scored_results.sort(key=lambda x: (x["relevance_score"], x["effective_date"]), reverse=True)
        return scored_results[:top_k]
