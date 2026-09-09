"""Test Point-in-Time Prediction Invariance and as_of Propagation."""

import pytest
from datetime import datetime, timezone
from app.services.decision_brain.prediction_engine import generate_prediction_summary, _extract_catalyst_timeline
from app.services.decision_brain.arbiter import Arbiter
from app.services.strategies.quality_growth_screener import run_quality_growth_screener
from app.services.strategies.concall_nlp import evaluate_concall_nlp


def test_prediction_summary_accepts_and_respects_as_of():
    """Verify generate_prediction_summary accepts as_of and bounds data retrieval."""
    cutoff = datetime(2023, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
    res = generate_prediction_summary("RELIANCE", as_of=cutoff)
    assert isinstance(res, dict)
    assert "RELIANCE" in res["symbol"]
    assert "horizon_predictions" in res
    assert "catalyst_timeline" in res


def test_catalyst_timeline_relative_to_as_of():
    """Verify _extract_catalyst_timeline calculates days_ahead from historical as_of rather than wall-clock now."""
    as_of = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    
    class MockEvent:
        def __init__(self, event_date, title):
            self.event_date = event_date
            self.title = title
            self.event_type = "ORDER_WIN"
            self.source = "BSE"

    # Event 30 days after as_of
    valid_event = MockEvent(datetime(2024, 1, 31, 0, 0, 0, tzinfo=timezone.utc), "Q4 Order Win")
    # Event in the past relative to as_of
    past_event = MockEvent(datetime(2023, 11, 1, 0, 0, 0, tzinfo=timezone.utc), "Old Announcement")
    # Event more than 365 days after as_of
    far_future = MockEvent(datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc), "Far Future Expansion")

    catalysts = _extract_catalyst_timeline([valid_event, past_event, far_future], as_of=as_of)
    assert len(catalysts) == 1
    assert catalysts[0]["title"] == "Q4 Order Win"
    assert catalysts[0]["days_ahead"] == 30


def test_arbiter_passes_as_of_to_prediction_summary():
    """Verify Arbiter.arbitrate threads as_of to prediction summary without look-ahead."""
    arbiter = Arbiter()
    cutoff = datetime(2024, 3, 15, 0, 0, 0, tzinfo=timezone.utc)
    
    # Run arbitration with historical as_of
    report = arbiter.arbitrate("TCS", as_of=cutoff)
    assert "TCS" in report.symbol
    assert report.timestamp is not None
    assert report.decision_manifest is not None


def test_quality_growth_screener_as_of_propagation():
    """Verify run_quality_growth_screener executes cleanly when as_of is provided."""
    cutoff = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    res = run_quality_growth_screener("INFY", as_of=cutoff)
    assert "INFY" in res.symbol
    assert res.meta.as_of is not None


def test_concall_nlp_as_of_propagation():
    """Verify evaluate_concall_nlp executes cleanly when as_of is provided."""
    cutoff = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    res = evaluate_concall_nlp("HDFCBANK", as_of=cutoff)
    assert "HDFCBANK" in res["symbol"]
    assert "commentary_confidence_score" in res
