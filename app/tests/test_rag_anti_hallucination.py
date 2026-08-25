"""Test Suite for Corrective Hybrid RAG & Anti-Hallucination Engine."""

import pytest
import tempfile
from pathlib import Path
from app.services.rag.document_store import FilingDocumentStore, FilingDocument
from app.services.rag.claim_verifier import ClaimVerifier
from app.services.llm import process_llm_query
from app.models.schemas import QueryRequest


def test_document_store_sha256_provenance_and_pit():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = str(Path(tmp_dir) / "test_filings.db")
        store = FilingDocumentStore(db_path=db_file)

        doc1 = FilingDocument(
            symbol="POLYCAB",
            doc_type="ANNUAL_REPORT",
            effective_date="2024-03-31",
            title="FY24 Annual Report - Financial Statements",
            content="Revenue from operations reached INR 18,039 Cr with EBITDA margin expanding 120 bps."
        )
        hash1 = store.add_document(doc1)

        assert len(hash1) == 64  # Valid SHA256 hex string
        assert doc1.document_hash == hash1

        # Point-in-time test: query as_of_date = 2023-12-31 should return no FY24 document
        pit_docs = store.search_documents("POLYCAB", "revenue EBITDA", as_of_date="2023-12-31")
        assert len(pit_docs) == 0

        # Query as_of_date = 2024-04-01 should return FY24 document
        valid_docs = store.search_documents("POLYCAB", "revenue EBITDA", as_of_date="2024-04-01")
        assert len(valid_docs) == 1
        assert valid_docs[0]["document_hash"] == hash1


def test_claim_verifier_abstention_policy():
    verifier = ClaimVerifier(min_confidence_threshold=0.70)
    
    # Low relevance score document
    low_confidence_docs = [{
        "document_hash": "a" * 64,
        "effective_date": "2024-01-01",
        "doc_type": "NEWS",
        "content": "Unrelated macro article",
        "relevance_score": 0.35
    }]

    result = verifier.verify_ai_response("POLYCAB revenue grew 25%", low_confidence_docs)
    assert not result.is_verified
    assert result.status_code == "INSUFFICIENT_FILING_EVIDENCE"
    assert result.confidence_score == 0.35


def test_process_llm_query_rag_integration():
    req = QueryRequest(query="Analyze POLYCAB revenue and growth", mode="Quick")
    resp = process_llm_query(req)
    assert resp.reply is not None
    assert "DETERMINISTIC RESEARCH SUMMARY" in resp.reply or "KEY FINDINGS" in resp.reply
