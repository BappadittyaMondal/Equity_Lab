"""Unit tests for Phase 2 QualitativeMultiplierEngine."""

import pytest
from app.services.intelligence.concall_evidence_extractor import QualitativeEvidencePayload
from app.services.intelligence.qualitative_multiplier_engine import QualitativeMultiplierEngine


def test_qualitative_multiplier_none_fallback():
    res = QualitativeMultiplierEngine.compute_multiplier(None)
    assert res["m_qual"] == 1.00


def test_qualitative_multiplier_positive_boosting():
    payload = QualitativeEvidencePayload(
        symbol="STRONG.NS",
        guidance_credibility_score=1.0,
        capacity_commitment_score=1.0,
        related_party_risk_flag=False,
        red_team_invalidation_risk=0.0
    )
    res = QualitativeMultiplierEngine.compute_multiplier(payload)
    assert res["m_qual"] == 1.10
    assert 0.85 <= res["m_qual"] <= 1.15


def test_qualitative_multiplier_clamping_upper_lower():
    # Severe negative payload
    bad_payload = QualitativeEvidencePayload(
        symbol="RISKY.NS",
        guidance_credibility_score=0.0,
        capacity_commitment_score=0.0,
        related_party_risk_flag=True,
        red_team_invalidation_risk=1.0
    )
    res_bad = QualitativeMultiplierEngine.compute_multiplier(bad_payload)
    assert res_bad["m_qual"] == 0.85  # Clamped to lower bound

    # Extreme positive payload
    good_payload = QualitativeEvidencePayload(
        symbol="PERFECT.NS",
        guidance_credibility_score=1.0,
        capacity_commitment_score=1.0,
        related_party_risk_flag=False,
        red_team_invalidation_risk=0.0
    )
    res_good = QualitativeMultiplierEngine.compute_multiplier(good_payload)
    assert res_good["m_qual"] <= 1.15
