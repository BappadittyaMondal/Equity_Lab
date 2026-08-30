"""Unit tests for Phase 2 Fundamental Convexity & Sector-Relative PEG Engine."""

from datetime import datetime
import pytest

from app.services.strategies.growth_inflection import evaluate_growth_inflection
from app.models.schemas import FinancialObservationResponse


def _make_obs(symbol, metric, value, period_end_str):
    return FinancialObservationResponse(
        id=1,
        symbol=symbol,
        metric=metric,
        value=value,
        unit="INR_CR",
        currency="INR",
        period_end=period_end_str,
        period_type="annual",
        statement_scope="consolidated",
        published_at=datetime.now(),
        source_name="BSE",
        source_url="http://bseindia.com",
        confidence=1.0,
        ingested_at=datetime.now()
    )


class MockResearchStore:
    def __init__(self, obs_list):
        self.obs_list = obs_list

    def get_timeline(self, symbol, as_of=None):
        return None, self.obs_list, [], [], [], []


def test_growth_inflection_turnaround_pat():
    """Verifies prev_pat <= 0 turnaround is correctly scored."""
    obs = [
        _make_obs("TURNAROUND.NS", "pat", -10.0, "2024-03-31"),
        _make_obs("TURNAROUND.NS", "pat", 15.0, "2025-03-31"),
        _make_obs("TURNAROUND.NS", "revenue", 100.0, "2024-03-31"),
        _make_obs("TURNAROUND.NS", "revenue", 140.0, "2025-03-31"),
    ]
    store = MockResearchStore(obs)
    res = evaluate_growth_inflection("TURNAROUND.NS", store=store)
    
    assert res.growth_inflection_score >= 45.0
    assert "pat_growth_pct" in res.metrics_summary
    assert any("TURNAROUND INFLECTION" in ev for ev in res.evidence)


def test_ebitda_convexity_calculation():
    """Verifies C_EBITDA convexity calculation on historical EBITDA observations."""
    # Growth rates: 10->12 (+20%), 12->16 (+33.3%), 16->32 (+100%) -> accelerating
    obs = [
        _make_obs("CONVEXITY.NS", "ebitda", 10.0, "2023-03-31"),
        _make_obs("CONVEXITY.NS", "ebitda", 12.0, "2024-03-31"),
        _make_obs("CONVEXITY.NS", "ebitda", 16.0, "2025-03-31"),
        _make_obs("CONVEXITY.NS", "ebitda", 32.0, "2026-03-31"),
    ]
    store = MockResearchStore(obs)
    res = evaluate_growth_inflection("CONVEXITY.NS", store=store)
    
    assert "c_ebitda" in res.metrics_summary
    assert res.metrics_summary["c_ebitda"] > 0.0
