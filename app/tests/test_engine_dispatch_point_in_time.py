"""Integration test for Point-in-Time Arbiter Strategy Engine Dispatching.

Asserts that calling Arbiter._collect_engine_outputs / arbitrate(symbol, as_of=earlier_date) without mocking
correctly routes the as_of parameter down to research engines, ensuring that engine
outputs (metrics and results) reflect ONLY data published on or before as_of.
"""

from datetime import datetime, timezone
import pytest

from app.models.schemas import CompanyUpsertRequest, FinancialObservationIn
from app.services.decision_brain.arbiter import Arbiter
from app.services.research_data import ResearchDataStore


def test_unmocked_arbiter_engine_dispatch_point_in_time():
    """Verify Arbiter passes as_of down to engines and engines respect the point-in-time cutoff."""
    store = ResearchDataStore()
    symbol = "PIT_DISPATCH_TEST"

    # 1. Register company
    store.upsert_company(CompanyUpsertRequest(
        symbol=symbol,
        legal_name="PIT Dispatch Test Corp",
        sector="Technology"
    ))

    # 2. Seed Q0 financial observation published on 2024-03-31
    store.add_financial_observation(FinancialObservationIn(
        symbol=symbol,
        metric="revenue",
        value=800.0,
        unit="INR_CRORES",
        currency="INR",
        period_end="2023-12-31",
        period_type="quarterly",
        statement_scope="standalone",
        published_at=datetime(2024, 3, 31, 12, 0, tzinfo=timezone.utc),
        source_name="BSE_FILING",
        source_url="https://bseindia.com/filings/0",
        confidence=0.98
    ))

    # 3. Seed Q1 financial observation published on 2024-06-30
    store.add_financial_observation(FinancialObservationIn(
        symbol=symbol,
        metric="revenue",
        value=1000.0,
        unit="INR_CRORES",
        currency="INR",
        period_end="2024-03-31",
        period_type="quarterly",
        statement_scope="standalone",
        published_at=datetime(2024, 6, 30, 12, 0, tzinfo=timezone.utc),
        source_name="BSE_FILING",
        source_url="https://bseindia.com/filings/1",
        confidence=0.98
    ))

    # 4. Seed Q2 financial observation published on 2024-09-30 (significantly higher numbers)
    store.add_financial_observation(FinancialObservationIn(
        symbol=symbol,
        metric="revenue",
        value=5000.0,
        unit="INR_CRORES",
        currency="INR",
        period_end="2024-06-30",
        period_type="quarterly",
        statement_scope="standalone",
        published_at=datetime(2024, 9, 30, 12, 0, tzinfo=timezone.utc),
        source_name="BSE_FILING",
        source_url="https://bseindia.com/filings/2",
        confidence=0.98
    ))

    arbiter = Arbiter()

    # 5. Collect engine outputs AS OF 2024-07-15 (BEFORE Q2 publication)
    as_of_july = datetime(2024, 7, 15, 0, 0, tzinfo=timezone.utc)
    outputs_july = arbiter._collect_engine_outputs(symbol, as_of=as_of_july)

    e1_july = next((out for out in outputs_july if out["engine_id"] == "E1"), None)
    assert e1_july is not None, "E1 engine output must exist"

    raw_july = e1_july["raw"]
    latest_rev_july = raw_july.metrics.get("latest_revenue")
    assert latest_rev_july == 1000.0, f"Expected latest_revenue to be 1000.0 (Q1) as of July 2024, but got {latest_rev_july}"

    # 6. Collect engine outputs AS OF 2024-10-15 (AFTER Q2 publication)
    as_of_oct = datetime(2024, 10, 15, 0, 0, tzinfo=timezone.utc)
    outputs_oct = arbiter._collect_engine_outputs(symbol, as_of=as_of_oct)

    e1_oct = next((out for out in outputs_oct if out["engine_id"] == "E1"), None)
    assert e1_oct is not None

    raw_oct = e1_oct["raw"]
    latest_rev_oct = raw_oct.metrics.get("latest_revenue")
    assert latest_rev_oct == 5000.0, f"Expected latest_revenue to be 5000.0 (Q2) as of October 2024, but got {latest_rev_oct}"

    # 7. Verify full arbitration run as of July 2024 completes successfully
    call_july = arbiter.arbitrate(symbol, as_of=as_of_july)
    assert call_july is not None
    assert call_july.symbol == "PIT_DISPATCH_TEST.NS" or call_july.symbol == "PIT_DISPATCH_TEST"
