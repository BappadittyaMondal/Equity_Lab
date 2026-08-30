"""Integration test for Qualitative Evidence M_Qual integration into MIVS Brain."""

import pytest
from app.services.decision_brain.mivs_engine import MIVSEngine
from app.services.intelligence.concall_evidence_extractor import QualitativeEvidencePayload


def test_mivs_with_qualitative_multiplier_boosting():
    engine = MIVSEngine()
    outputs = [
        {"engine_name": "growth_inflection", "confidence_score": 8.0, "positive_drivers": ["Turnaround"]},
        {"engine_name": "vpa_b4", "confidence_score": 8.5, "positive_drivers": ["Volume Spike"]}
    ]
    fin_snapshot = {
        "piotroski_score": 8.0,
        "promoter_holding": 60.0,
        "pledged_pct": 0.0,
        "debt_to_equity": 0.2,
        "interest_coverage": 12.0
    }
    
    # 1. Without qualitative payload (neutral 1.00)
    res_base = engine.compute_mivs("TEST.NS", outputs, financial_snapshot=fin_snapshot)
    
    # 2. With positive qualitative payload (M_Qual = 1.10)
    good_payload = QualitativeEvidencePayload(
        symbol="TEST.NS",
        guidance_credibility_score=1.0,
        capacity_commitment_score=1.0,
        related_party_risk_flag=False,
        red_team_invalidation_risk=0.0
    )
    res_boosted = engine.compute_mivs("TEST.NS", outputs, financial_snapshot=fin_snapshot, qualitative_payload=good_payload)
    
    assert res_boosted.mivs_score > res_base.mivs_score
    assert res_boosted.metadata["m_qual"] == 1.10
