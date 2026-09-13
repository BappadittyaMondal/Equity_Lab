"""Unit tests for Geopolitical Engine (Phase 8)."""

import pytest
from app.services.research.geopolitical_engine import evaluate_geopolitical_risk


def test_geopolitical_engine_data_unavailable():
    res = evaluate_geopolitical_risk("UNKNOWN_TICKER_XYZ99")
    assert res["status"] == "DATA_UNAVAILABLE"
    assert res["conviction_penalty_pct"] == 0.0
    assert "DATA_UNAVAILABLE" in res["evidence"][0]


def test_geopolitical_engine_reliance():
    res = evaluate_geopolitical_risk("RELIANCE")
    assert "status" in res
    assert "macro_risk_rating" in res
    assert "conviction_penalty_pct" in res
    assert "meta" in res


def test_geopolitical_engine_dynamic_geographic_overlay():
    """Verify dynamic weighted overlay when empirical geographic splits are provided."""
    # IT company with high US/EU exposure
    res_it = evaluate_geopolitical_risk(
        "INFY",
        geographic_split={"domestic": 0.05, "us_na": 0.65, "eu": 0.25, "apac": 0.05}
    )
    assert res_it["overlay_type"] == "MACRO_RISK_PENALTY"
    assert res_it["overlay_pct"] < -15.0
    assert "geographic_exposure_breakdown" in res_it
    assert res_it["geographic_exposure_breakdown"] is not None

    # Defense company with high domestic exposure
    res_def = evaluate_geopolitical_risk(
        "HAL",
        geographic_split={"domestic": 0.90, "row": 0.10}
    )
    assert res_def["overlay_type"] == "TAILWIND_PREMIUM"
    assert res_def["overlay_pct"] > 10.0
    assert res_def["conviction_penalty_pct"] == 0.0

