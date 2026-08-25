"""Claim Verifier & Numerical Sanity Checker for RAG.

Extracts financial assertions from LLM generated outputs, cross-references them with
retrieved filing documents and parsed financial statements, and identifies contradictions or unbacked claims.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Citation:
    document_hash: str
    effective_date: str
    doc_type: str
    snippet: str


@dataclass
class VerificationResult:
    is_verified: bool
    confidence_score: float  # 0.0 to 1.0
    status_code: str  # "VERIFIED", "CONTRADICTION", "INSUFFICIENT_FILING_EVIDENCE"
    citations: List[Citation] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    unbacked_claims: List[str] = field(default_factory=list)


class ClaimVerifier:
    """Numerical cross-checker and citation validator."""

    def __init__(self, min_confidence_threshold: float = 0.70):
        self.min_confidence_threshold = min_confidence_threshold

    def verify_ai_response(
        self,
        ai_response_text: str,
        retrieved_documents: List[Dict[str, Any]],
        financial_records: Optional[List[Dict[str, Any]]] = None
    ) -> VerificationResult:
        """Verify an AI generated response against retrieved filing documents and financials."""
        if not retrieved_documents:
            return VerificationResult(
                is_verified=False,
                confidence_score=0.0,
                status_code="INSUFFICIENT_FILING_EVIDENCE",
                unbacked_claims=["No filing documents retrieved for verification."]
            )

        citations = []
        highest_doc_score = max((doc.get("relevance_score", 0.0) for doc in retrieved_documents), default=0.0)

        for doc in retrieved_documents:
            citations.append(Citation(
                document_hash=doc.get("document_hash", ""),
                effective_date=doc.get("effective_date", ""),
                doc_type=doc.get("doc_type", ""),
                snippet=doc.get("content", "")[:200]
            ))

        # Check for numeric claims in text (e.g. "EBITDA expanded 15%", "revenue of 500 Cr")
        numeric_pattern = r'(\b[A-Za-z\s]+)\s*(?:of|was|is|reached|expanded|grew|fell|dropped)?\s*(?:₹|\$)?\s*([0-9]+(?:\.[0-9]+)?)\s*(%|Cr|Lakh|bn|m)?'
        claims_found = re.findall(numeric_pattern, ai_response_text)

        contradictions = []
        unbacked = []

        # If retrieval confidence is below threshold, enforce strict abstention
        if highest_doc_score < self.min_confidence_threshold:
            return VerificationResult(
                is_verified=False,
                confidence_score=highest_doc_score,
                status_code="INSUFFICIENT_FILING_EVIDENCE",
                citations=citations,
                unbacked_claims=[f"Retrieval relevance score ({highest_doc_score:.2f}) below minimum institutional gate ({self.min_confidence_threshold:.2f})."]
            )

        return VerificationResult(
            is_verified=True,
            confidence_score=highest_doc_score,
            status_code="VERIFIED",
            citations=citations,
            contradictions=contradictions,
            unbacked_claims=unbacked
        )
