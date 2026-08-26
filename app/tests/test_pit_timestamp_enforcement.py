"""Automated tests for Point-In-Time (PIT) timestamp enforcement and ABSTAIN decision gating.

Phase B & Phase C Cycle N Hardening Verification.
"""

from datetime import datetime, timezone, timedelta
import pytest
from app.services.research_data import ResearchDataStore, FinancialObservationIn
from app.services.decision_brain.arbiter import Arbiter
from app.models.schemas import ConvictionCall, SynthesizedEquitySnapshot, MetaHeader


def test_pit_timestamp_filtering_prevents_lookahead(tmp_path):
    """Test that ResearchDataStore.get_timeline strictly excludes observations published after as_of."""
    db_file = tmp_path / "pit_test.db"
    store = ResearchDataStore(database_path=str(db_file))

    # Setup company
    store.upsert_company({"symbol": "TESTPIT", "legal_name": "Test PIT Corp"})

    # Ingest past observation (published 2025-01-01)
    obs_past = FinancialObservationIn(
        symbol="TESTPIT",
        metric="revenue",
        value=100.0,
        unit="INR_CRORE",
        currency="INR",
        period_end="2024-12-31",
        period_type="quarterly",
        statement_scope="consolidated",
        published_at=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
        source_name="BSE Statutory Filing",
        source_url="https://bseindia.com/filing/1",
        confidence=0.98
    )
    store.add_financial_observation(obs_past)

    # Ingest future observation (published 2025-06-01)
    obs_future = FinancialObservationIn(
        symbol="TESTPIT",
        metric="revenue",
        value=250.0,
        unit="INR_CRORE",
        currency="INR",
        period_end="2025-03-31",
        period_type="quarterly",
        statement_scope="consolidated",
        published_at=datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc),
        source_name="BSE Statutory Filing",
        source_url="https://bseindia.com/filing/2",
        confidence=0.98
    )
    store.add_financial_observation(obs_future)

    # Query with as_of = 2025-03-01 (should include past, exclude future)
    cutoff = datetime(2025, 3, 1, 0, 0, tzinfo=timezone.utc)
    _, financials, _, _, _, _ = store.get_timeline("TESTPIT", as_of=cutoff)

    assert len(financials) == 1
    assert financials[0].value == 100.0
    assert financials[0].published_at <= cutoff


def test_arbiter_abstain_trigger_on_low_confidence():
    """Test that Arbiter triggers ABSTAIN state when data_confidence_score is below threshold."""
    arbiter = Arbiter()

    # Mock snapshot with low data confidence (< 0.25)
    meta = MetaHeader(
        source="DataSynthesizer",
        as_of="2026-08-26T10:00:00+05:30",
        retrieved_at="2026-08-26T10:00:00+05:30",
        market_data_type="synthetic",
        stale=False,
        limitations=[]
    )
    low_conf_snap = SynthesizedEquitySnapshot(
        symbol="LOWCONF",
        consensus_price=100.0,
        consensus_pe=15.0,
        data_confidence_score=0.15,
        meta=meta
    )

    reason = arbiter._check_abstention_triggers(
        outputs=[{"engine_id": "E1", "score_0_100": 70, "verdict": "Buy"}],
        snap=low_conf_snap,
        regime="CALM",
        vix_level=15.0
    )

    assert reason is not None
    assert "low data confidence" in reason.lower()


def test_arbiter_abstain_trigger_on_high_variance():
    """Test that Arbiter triggers ABSTAIN state when engine score variance is high and split buy/avoid."""
    arbiter = Arbiter()

    meta = MetaHeader(
        source="DataSynthesizer",
        as_of="2026-08-26T10:00:00+05:30",
        retrieved_at="2026-08-26T10:00:00+05:30",
        market_data_type="synthetic",
        stale=False,
        limitations=[]
    )
    snap = SynthesizedEquitySnapshot(
        symbol="SPLIT",
        consensus_price=100.0,
        consensus_pe=15.0,
        data_confidence_score=0.85,
        meta=meta
    )

    conflicting_outputs = [
        {"engine_id": "E1", "score_0_100": 95, "verdict": "Buy"},
        {"engine_id": "E2", "score_0_100": 90, "verdict": "Buy"},
        {"engine_id": "E3", "score_0_100": 10, "verdict": "Avoid"},
        {"engine_id": "E4", "score_0_100": 15, "verdict": "Avoid"},
    ]

    reason = arbiter._check_abstention_triggers(
        outputs=conflicting_outputs,
        snap=snap,
        regime="CALM",
        vix_level=15.0
    )

    assert reason is not None
    assert "engine score variance" in reason.lower()
