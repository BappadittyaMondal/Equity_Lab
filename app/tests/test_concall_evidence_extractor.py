"""Unit tests for Phase 1 ConCallEvidenceExtractor."""

import pytest
from app.services.intelligence.concall_evidence_extractor import ConCallEvidenceExtractor


def test_concall_evidence_extractor_defaults():
    payload = ConCallEvidenceExtractor.extract_evidence("NEUTRAL.NS")
    assert payload.symbol == "NEUTRAL.NS"
    assert payload.guidance_credibility_score == 0.5
    assert payload.capacity_commitment_score == 0.5
    assert payload.related_party_risk_flag is False
    assert payload.red_team_invalidation_risk == 0.0


def test_concall_evidence_extractor_positive_capacity():
    concall_text = "We are pleased to state that commercial production from our new plant trial run starts next week."
    payload = ConCallEvidenceExtractor.extract_evidence(
        "GROWTH.NS",
        concall_transcript_text=concall_text,
        historical_guidance_met_count=4,
        historical_guidance_total_count=5
    )
    assert payload.guidance_credibility_score == 0.8
    assert payload.capacity_commitment_score == 0.85
    assert payload.related_party_risk_flag is False


def test_concall_evidence_extractor_footnote_risk():
    footnote = "Note 32: Unsecured loan to promoter entity granted during the financial year."
    payload = ConCallEvidenceExtractor.extract_evidence("RISKY.NS", footnote_text=footnote)
    assert payload.related_party_risk_flag is True
    assert any("Related-Party" in note for note in payload.evidence_notes)
