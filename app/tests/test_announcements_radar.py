"""Unit tests for BSE/NSE Regulation 30 Corporate Announcements Radar."""

import pytest
from datetime import datetime, timezone
from app.models.schemas import BusinessEventResponse, EventType
from app.services.ingestion.announcements_radar import CorporateAnnouncementsRadar


def test_announcements_radar_classification():
    """Test text classification and Event Materiality Ratio."""
    res = CorporateAnnouncementsRadar.classify_announcement_text(
        headline="Company bagged mega order worth Rs. 500 Crore from Indian Railways",
        details="Commercial supply order executed over 18 months",
        ttm_revenue_cr=1000.0
    )
    assert res["primary_category"] == "MEGA_ORDER_WIN"
    assert res["is_material_event"] is True
    assert res["extracted_value_cr"] == 500.0
    assert res["event_materiality_ratio_pct"] == 50.0
    assert res["event_tier"] == "TIER_1_MOMENTUM_CATALYST"


def test_announcements_radar_schema_compatibility(monkeypatch):
    """Test that announcements radar correctly extracts from BusinessEventResponse schemas."""
    fake_event = BusinessEventResponse(
        id=101,
        symbol="TESTCO",
        event_type="acquisition",
        announced_at=datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc),
        title="Scheme of Arrangement for Amalgamation with SubCo",
        summary="Board approved merger under Regulation 30 of SEBI LODR",
        source_name="BSE",
        source_url="https://bseindia.com/filing/101",
        ingested_at=datetime(2024, 6, 1, 10, 5, tzinfo=timezone.utc),
    )

    class FakeStore:
        def get_timeline(self, norm, as_of=None):
            return ([], [], [fake_event], [], [], [])

    monkeypatch.setattr("app.services.ingestion.announcements_radar.ResearchDataStore", FakeStore)

    radar_res = CorporateAnnouncementsRadar.get_company_instant_announcements("TESTCO")
    assert "derived_catalyst_inputs" in radar_res
    cat_inputs = radar_res["derived_catalyst_inputs"]
    assert cat_inputs.get("has_merger_acquisition") is True
    assert radar_res["material_catalysts"]["mergers_acquisitions_count"] == 1


def test_announcements_radar_sue_and_creeping_acquisition():
    """Test Standardized Unexpected Earnings (SUE) and SEBI SAST creeping acquisitions."""
    # 1. Test SUE Positive Drift
    sue_res = CorporateAnnouncementsRadar.compute_sue_earnings_drift(reported_eps=12.5, prior_eps=8.0, eps_surprise_std=1.5)
    assert sue_res["standardized_unexpected_earnings"] == 3.0
    assert sue_res["pead_verdict"] == "STRONG_POSITIVE_PEAD_DRIFT"

    # 2. Test SUE Negative Drift
    sue_neg = CorporateAnnouncementsRadar.compute_sue_earnings_drift(reported_eps=5.0, prior_eps=9.0, eps_surprise_std=1.0)
    assert sue_neg["standardized_unexpected_earnings"] == -4.0
    assert sue_neg["pead_verdict"] == "STRONG_NEGATIVE_PEAD_DRIFT"

    # 3. Test SAST Creeping Acquisition text classification
    sast_res = CorporateAnnouncementsRadar.classify_announcement_text(
        headline="Disclosure under Regulation 29(2) of SEBI SAST: Promoter acquisition of shares",
        details="Promoter group bought 150,000 shares via open market purchase"
    )
    assert sast_res["primary_category"] == "PROMOTER_CREEPING_ACQUISITION"
    assert sast_res["is_material_event"] is True


