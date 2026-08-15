from datetime import date, datetime, timezone
import pandas as pd
import pytest
from fastapi import HTTPException

from app.models.schemas import (
    BusinessEventIn,
    CompanyUpsertRequest,
    CorporateActionIn,
    DocumentMetadataIn,
    FinancialObservationIn,
    OwnershipSnapshotIn,
)
from app.services.market_data import (
    adjust_price_series,
    calculate_corporate_action_adjustment_factors,
)
from app.services.research_data import ResearchDataStore


def test_append_only_timeline_respects_publication_date(tmp_path):
    store = ResearchDataStore(str(tmp_path / "research.sqlite3"))
    store.upsert_company(CompanyUpsertRequest(symbol="DEMO", legal_name="Demo Industries Limited", sector="Industrials"))

    first = store.add_financial_observation(FinancialObservationIn(
        symbol="DEMO", metric="revenue", value=100.0, unit="INR_CRORE", period_end=date(2024, 3, 31),
        period_type="annual", published_at=datetime(2024, 5, 1, tzinfo=timezone.utc),
        source_name="Annual report", source_url="https://example.com/ar-2024", source_reference="p. 42",
    ))
    corrected = store.add_financial_observation(FinancialObservationIn(
        symbol="DEMO", metric="revenue", value=102.0, unit="INR_CRORE", period_end=date(2024, 3, 31),
        period_type="annual", published_at=datetime(2024, 6, 1, tzinfo=timezone.utc),
        source_name="Exchange correction", source_url="https://example.com/correction", source_reference="p. 2",
    ))
    store.add_business_event(BusinessEventIn(
        symbol="DEMO", event_type="capacity_expansion", announced_at=datetime(2024, 6, 15, tzinfo=timezone.utc),
        title="New plant approval", summary="The board approved a new manufacturing facility with phased commissioning.",
        source_name="Exchange filing", source_url="https://example.com/plant",
    ))

    _, before_revision, before_event, _, _, _ = store.get_timeline("DEMO", as_of=datetime(2024, 5, 15, tzinfo=timezone.utc))
    _, after_revision, after_event, _, _, _ = store.get_timeline("DEMO", as_of=datetime(2024, 6, 20, tzinfo=timezone.utc))

    assert [item.id for item in before_revision] == [first.id]
    assert before_event == []
    assert [item.id for item in after_revision] == [first.id, corrected.id]
    assert len(after_event) == 1


def test_observations_require_a_known_company(tmp_path):
    store = ResearchDataStore(str(tmp_path / "research.sqlite3"))
    with pytest.raises(HTTPException) as exc_info:
        store.add_financial_observation(FinancialObservationIn(
            symbol="MISSING", metric="pat", value=10, unit="INR_CRORE", period_end=date(2024, 3, 31),
            period_type="annual", published_at=datetime(2024, 5, 1, tzinfo=timezone.utc),
            source_name="Annual report", source_url="https://example.com/ar",
        ))
    assert exc_info.value.status_code == 404


def test_corporate_actions_ownership_and_documents_point_in_time(tmp_path):
    store = ResearchDataStore(str(tmp_path / "research.sqlite3"))
    store.upsert_company(CompanyUpsertRequest(symbol="ABC", legal_name="ABC Infra Limited", sector="Infrastructure"))

    corp = store.add_corporate_action(CorporateActionIn(
        symbol="ABC", action_type="split", ratio_numerator=5.0, ratio_denominator=1.0,
        ex_date=date(2024, 4, 10), announced_at=datetime(2024, 3, 1, tzinfo=timezone.utc),
        source_name="BSE Announcement", source_url="https://example.com/split",
    ))

    own = store.add_ownership_snapshot(OwnershipSnapshotIn(
        symbol="ABC", period_end=date(2024, 3, 31), promoter_pct=55.0, fii_pct=15.0, dii_pct=10.0,
        public_pct=20.0, published_at=datetime(2024, 4, 15, tzinfo=timezone.utc),
        source_name="NSE Shareholding Pattern", source_url="https://example.com/shp",
    ))

    doc = store.add_document_metadata(DocumentMetadataIn(
        symbol="ABC", document_type="annual_report", title="Annual Report FY24",
        financial_period="FY2024", document_date=date(2024, 3, 31),
        publication_date=datetime(2024, 5, 20, tzinfo=timezone.utc),
        source_name="Company Site", source_url="https://example.com/ar24",
    ))

    # Query before ownership and document publication
    _, _, _, corp_list, own_list, doc_list = store.get_timeline("ABC", as_of=datetime(2024, 3, 15, tzinfo=timezone.utc))
    assert len(corp_list) == 1
    assert corp_list[0].id == corp.id
    assert len(own_list) == 0
    assert len(doc_list) == 0

    # Query after all published
    _, _, _, corp_list2, own_list2, doc_list2 = store.get_timeline("ABC", as_of=datetime(2024, 6, 1, tzinfo=timezone.utc))
    assert len(corp_list2) == 1
    assert len(own_list2) == 1
    assert len(doc_list2) == 1
    assert own_list2[0].id == own.id
    assert doc_list2[0].id == doc.id


def test_corporate_action_adjustment_calculation(tmp_path):
    store = ResearchDataStore(str(tmp_path / "research.sqlite3"))
    store.upsert_company(CompanyUpsertRequest(symbol="TEST", legal_name="Test Stock Limited"))

    action1 = store.add_corporate_action(CorporateActionIn(
        symbol="TEST", action_type="split", ratio_numerator=5.0, ratio_denominator=1.0,
        ex_date=date(2024, 6, 1), announced_at=datetime(2024, 5, 1, tzinfo=timezone.utc),
        source_name="BSE", source_url="https://example.com/split",
    ))

    action2 = store.add_corporate_action(CorporateActionIn(
        symbol="TEST", action_type="bonus", ratio_numerator=1.0, ratio_denominator=1.0,
        ex_date=date(2023, 6, 1), announced_at=datetime(2023, 5, 1, tzinfo=timezone.utc),
        source_name="BSE", source_url="https://example.com/bonus",
    ))

    actions = [action1, action2]
    factors = calculate_corporate_action_adjustment_factors(actions)

    # 1:1 Bonus factor multiplier = 1/2 = 0.5
    # 5:1 Split factor multiplier = 1/5 = 0.2
    # Cumulative factor prior to 2023-06-01 is 0.5 * 0.2 = 0.1
    assert factors["2024-06-01"] == 0.2
    assert pytest.approx(factors["2023-06-01"], 0.001) == 0.1

    dates = pd.date_range(start="2023-01-01", periods=3, freq="6ME")
    df = pd.DataFrame({
        "Open": [1000.0, 500.0, 100.0],
        "High": [1050.0, 520.0, 105.0],
        "Low": [950.0, 480.0, 95.0],
        "Close": [1000.0, 500.0, 100.0],
        "Volume": [10000, 20000, 100000]
    }, index=dates)

    adjusted_df = adjust_price_series(df, actions)
    assert not adjusted_df.empty

