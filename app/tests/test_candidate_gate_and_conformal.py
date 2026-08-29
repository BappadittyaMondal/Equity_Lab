"""Unit tests for Dynamic Candidate Gate & Conformal Risk Tiering.
"""

import pytest
from app.services.intelligence.candidate_gate import DynamicCandidateGate
from app.services.intelligence.conformal_tiering import ConformalTieringEngine


def test_dynamic_candidate_gate():
    gate = DynamicCandidateGate()
    pool = [
        {
            "symbol": "GOOD1",
            "inflection_score": 75.0,
            "quotes": [{"price": 100.0}, {"price": 100.1}],
        },
        {
            "symbol": "LOW_SCORE",
            "inflection_score": 40.0,
            "quotes": [{"price": 50.0}],
        },
        {
            "symbol": "BAD_DATA",
            "inflection_score": 85.0,
            "quotes": [{"price": None}],
        },
    ]

    accepted, rejected = gate.evaluate_candidates(pool, min_inflection_score=60.0)

    assert len(accepted) == 1
    assert accepted[0]["symbol"] == "GOOD1"
    assert len(rejected) == 2


def test_conformal_risk_tiering_confirmed_high():
    engine = ConformalTieringEngine()
    res = engine.assign_confidence_tier(
        score=85.0,
        current_price=100.0,
        lower_bound=90.0,
        upper_bound=105.0,
        data_trust_tier="HIGH",
    )
    assert res["confidence_tier"] == "CONFIRMED_HIGH"
    assert res["interval_width_pct"] == 15.0


def test_conformal_risk_tiering_abstain():
    engine = ConformalTieringEngine()
    res = engine.assign_confidence_tier(
        score=85.0,
        current_price=100.0,
        lower_bound=90.0,
        upper_bound=105.0,
        data_trust_tier="UNTRUSTED",
    )
    assert res["confidence_tier"] == "ABSTAIN"
