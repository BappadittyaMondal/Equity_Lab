"""Unit tests for DataSanitizer utility (Skill 01).
"""

import pytest
from app.services.utils.data_sanitizer import DataSanitizer


@pytest.fixture
def sanitizer():
    return DataSanitizer()


def test_mad_outlier_detection(sanitizer):
    series = [100.0, 102.0, 101.0, 100.5, 500.0, 101.5]
    outliers = sanitizer.calculate_mad_outliers(series, threshold=4.0)
    assert outliers[4] is True
    assert outliers[0] is False


def test_pit_timestamp_verification(sanitizer):
    assert sanitizer.verify_pit_timestamp("2026-03-31T00:00:00Z", "2026-04-01T00:00:00Z") is True
    assert sanitizer.verify_pit_timestamp("2026-04-05T00:00:00Z", "2026-04-01T00:00:00Z") is False


def test_cross_provider_agreement(sanitizer):
    quotes_agree = [
        {"provider": "P1", "price": 100.0},
        {"provider": "P2", "price": 100.3},
    ]
    quotes_disagree = [
        {"provider": "P1", "price": 100.0},
        {"provider": "P2", "price": 120.0},
    ]
    assert sanitizer.verify_cross_provider_agreement(quotes_agree, tolerance_pct=0.5) is True
    assert sanitizer.verify_cross_provider_agreement(quotes_disagree, tolerance_pct=0.5) is False


def test_compute_data_trust_vector_high(sanitizer):
    quotes = [
        {"provider": "P1", "price": 100.0},
        {"provider": "P2", "price": 100.2},
    ]
    financials = [{"published_at": "2026-03-15T00:00:00Z"}]
    res = sanitizer.compute_data_trust_vector(quotes, financials, as_of_date="2026-03-20T00:00:00Z")
    assert res["overall_trust_tier"] == "HIGH"
    assert res["is_trusted"] is True


def test_compute_data_trust_vector_untrusted(sanitizer):
    quotes = [{"provider": "P1", "price": None}]
    res = sanitizer.compute_data_trust_vector(quotes)
    assert res["overall_trust_tier"] == "UNTRUSTED"
    assert res["is_trusted"] is False
