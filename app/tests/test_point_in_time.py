"""Unit tests for Point-in-Time Data Integrity & Lookahead Bias Prevention (Phase 9)."""

from datetime import datetime, timezone
import pytest
from app.services.research_data import ResearchDataStore
from app.models.schemas import CompanyUpsertRequest, FinancialObservationIn


def test_point_in_time_timeline_filtering(tmp_path):
    db_file = tmp_path / "pit_test_research.db"
    store = ResearchDataStore(database_path=str(db_file))

    # 1. Register company
    store.upsert_company(CompanyUpsertRequest(
        symbol="PIT_TEST",
        legal_name="Point In Time Test Corp",
        sector="Technology"
    ))

    # 2. Add Q1 observation published on 2024-06-30
    store.add_financial_observation(FinancialObservationIn(
        symbol="PIT_TEST",
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

    # 3. Add Q2 observation published on 2024-09-30
    store.add_financial_observation(FinancialObservationIn(
        symbol="PIT_TEST",
        metric="revenue",
        value=1200.0,
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

    # 4. As of July 15, 2024 (Before Q2 was published): MUST ONLY RETURN Q1
    as_of_july = datetime(2024, 7, 15, 0, 0, tzinfo=timezone.utc)
    _, financials_july, _, _, _, _ = store.get_timeline("PIT_TEST", as_of=as_of_july)

    assert len(financials_july) == 1
    assert financials_july[0].value == 1000.0
    assert str(financials_july[0].period_end) == "2024-03-31"

    # 5. As of October 15, 2024 (After Q2 was published): MUST RETURN BOTH Q1 and Q2
    as_of_oct = datetime(2024, 10, 15, 0, 0, tzinfo=timezone.utc)
    _, financials_oct, _, _, _, _ = store.get_timeline("PIT_TEST", as_of=as_of_oct)

    assert len(financials_oct) == 2
    assert financials_oct[0].value == 1000.0
    assert financials_oct[1].value == 1200.0
