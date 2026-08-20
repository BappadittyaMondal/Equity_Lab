"""Unit tests for Variant Perception schema fields in ConvictionCall.

Tests:
1. Direct schema instantiation with variant perception fields.
2. Backward compatibility when variant perception fields are omitted (None defaults).
3. JSON serialization / deserialization round-trip.
4. Arbiter arbitrate() populates variant perception fields on generated ConvictionCall.
"""

import pytest
from app.models.schemas import ConvictionCall
from app.services.decision_brain.arbiter import Arbiter


def test_variant_perception_schema_populated():
    call = ConvictionCall(
        symbol="RELIANCE",
        verdict="Buy",
        conviction_score=75,
        primary_thesis="Strong refining margin expansion and retail growth.",
        consensus_view="Consensus expects flat margins over FY25.",
        variant_view="Independent research models 150 bps EBITDA margin expansion driven by O2C optimization.",
        supporting_evidence=["E1 Growth Inflection 78/100", "E7 Expectation Gap +8.5%"],
        invalidation_condition="Singapore GRM falls below $4.0/bbl for 2 consecutive quarters.",
        catalyst_timing="6-12 Months"
    )

    assert call.consensus_view == "Consensus expects flat margins over FY25."
    assert call.variant_view.startswith("Independent research models")
    assert len(call.supporting_evidence) == 2
    assert call.invalidation_condition.startswith("Singapore GRM")
    assert call.catalyst_timing == "6-12 Months"


def test_variant_perception_backward_compatibility():
    call = ConvictionCall(
        symbol="TCS",
        verdict="Watch",
        conviction_score=50,
        primary_thesis="Neutral growth outlook."
    )

    assert call.consensus_view is None
    assert call.variant_view is None
    assert call.supporting_evidence is None
    assert call.invalidation_condition is None
    assert call.catalyst_timing is None


def test_variant_perception_json_roundtrip():
    call = ConvictionCall(
        symbol="INFY",
        verdict="Buy",
        conviction_score=80,
        primary_thesis="Large deal wins acceleration.",
        variant_view="Digital transformation revenue upside not priced in.",
        catalyst_timing="12 Months"
    )

    json_data = call.model_dump_json() if hasattr(call, "model_dump_json") else call.json()
    reconstructed = ConvictionCall.model_validate_json(json_data) if hasattr(ConvictionCall, "model_validate_json") else ConvictionCall.parse_raw(json_data)

    assert reconstructed.symbol == "INFY"
    assert reconstructed.variant_view == "Digital transformation revenue upside not priced in."
    assert reconstructed.catalyst_timing == "12 Months"


def test_arbiter_populates_variant_perception():
    arbiter = Arbiter()
    call = arbiter.arbitrate("RELIANCE")

    assert call.consensus_view is not None
    assert call.variant_view is not None
    assert call.invalidation_condition is not None
    assert call.catalyst_timing is not None
