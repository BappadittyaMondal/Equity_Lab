"""Test suite for Phase 145: Geopolitical Outcome Collector and Self-Learning Daemon."""

import pytest
from app.services.monitoring.event_prediction_ledger import EventPredictionLedgerService
from app.services.monitoring.geopolitical_outcome_collector import GeopoliticalOutcomeCollector


def test_geopolitical_outcome_collector_end_to_end():
    """Verify autonomous scan, maturity check, and Kalman calibration of a logged event."""
    event_id = "TEST_EVENT_AUTOCONV_145"

    # 1. Log a pre-event prediction into ledger
    rec = EventPredictionLedgerService.log_geopolitical_event(
        event_id=event_id,
        title="Test Simulated Gulf Chokepoint Flare-up",
        event_type="MARITIME_CHOKEPOINT",
        theater="MIDDLE_EAST",
        pews_probability=0.75,
        pdlr_ratio=0.82,
        pdlr_classification="PHYSICAL_DISRUPTION_CONFIRMED",
        shock_vector={"maritime": 0.35, "crude": 0.20},
        predicted_betas={"SHIPPING_TANKERS": 0.85, "OIL_MARKETING": -0.65},
        notes="Automated test fixture for Phase 145 outcome collector",
    )
    assert rec.status == "PENDING_OUTCOME"

    # 2. Execute outcome collector daemon forcing this event
    custom_returns = {
        "^NSEI": -1.2,
        "SHIPPING_TANKERS": 6.8,  # Outperformed during chokepoint
        "OIL_MARKETING": -4.5,    # Underperformed
    }
    result = GeopoliticalOutcomeCollector.collect_and_calibrate(
        force_event_id=event_id,
        custom_realized_shock={"maritime": 0.30},
        custom_empirical_returns=custom_returns,
        event_occurred=True,
    )

    assert result.events_matured >= 1
    assert result.calibrations_executed >= 1
    assert result.average_brier_score is not None
    assert 0.0 <= result.average_brier_score <= 1.0

    # 3. Verify event record in ledger is now CALIBRATED
    history = EventPredictionLedgerService.get_event_history(limit=10)
    matched = next((e for e in history if e.event_id == event_id), None)
    assert matched is not None
    assert matched.status == "CALIBRATED"
    assert matched.brier_score is not None
    assert matched.calibrated_betas is not None
    assert "SHIPPING_TANKERS" in matched.calibrated_betas
