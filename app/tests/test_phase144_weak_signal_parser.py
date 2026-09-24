"""Test suite for Phase 144: Weak Signal Parser and Ingestion Service."""

import pytest
from app.services.research.weak_signal_parser import WeakSignalParserService


def test_leader_signalling_anomaly_parsing():
    """Verify that leader symbolic attire (e.g. Trump white cap / Modi black vest / war room photo)
    is accurately parsed into LEADER_SIGNALLING_ANOMALY with boosted Likelihood Ratio.
    """
    dispatch = (
        "Breaking OSINT: U.S. President spotted wearing a white cap during emergency military inspection. "
        "Situation room briefing broadcasted late night concerning rising tensions in the Gulf."
    )

    signals = WeakSignalParserService.parse_text_to_signals(dispatch)
    assert len(signals) >= 1
    leader_sig = next(s for s in signals if s.signal_type == "LEADER_SIGNALLING_ANOMALY")
    assert leader_sig.theater == "MIDDLE_EAST"
    assert leader_sig.likelihood_ratio >= 2.8
    assert any("white cap" in trig or "situation room" in trig for trig in leader_sig.matched_triggers)


def test_multi_signal_chokepoint_parsing():
    """Verify simultaneous parsing of NOTAM closures and dark AIS transponders."""
    dispatch = (
        "Tehran issues emergency NOTAM airspace closure over western corridor for 48 hours. "
        "Multiple oil tankers in Strait of Hormuz reported transponder silent with AIS dark navigation."
    )

    signals = WeakSignalParserService.parse_text_to_signals(dispatch)
    types = {s.signal_type for s in signals}
    assert "AIRSPACE_NOTAM_CLOSURE" in types
    assert "AIS_TRANSPONDER_DARK" in types

    notam = next(s for s in signals if s.signal_type == "AIRSPACE_NOTAM_CLOSURE")
    assert notam.likelihood_ratio == 8.5
    assert notam.theater == "MIDDLE_EAST"


def test_full_pipeline_ingest_and_evaluate():
    """Verify end-to-end ingestion and Bayesian imminence calculation."""
    dispatch = (
        "Urgent: U.S. embassy staff departure confirmed in Middle East. "
        "Civil aviation issues notice to airmen regarding missile launch window. "
        "Brent crude call skew spikes as traders buy 25-delta upside protection."
    )

    result = WeakSignalParserService.ingest_and_evaluate(
        text=dispatch,
        source="REUTERS_OSINT_WIRE",
        prior_probability=0.08,
        age_hours=2.0,
    )

    assert result["status"] == "SUCCESS"
    assert result["theater"] == "MIDDLE_EAST"
    assert result["parsed_signals_count"] >= 3
    assert result["evaluation"] is not None
    # With 3 strong signals (embassy evacuation, NOTAM, crude skew), posterior must rise significantly above prior 0.08
    assert result["evaluation"]["pews_probability"] > 0.40
    assert result["evaluation"]["imminence_rating"] in ["WATCHLIST_STAGE_TENSION", "ELEVATED_PRE_STRIKE_PROBABILITY", "CRITICAL_IMMINENT_INTERVENTION"]
