"""Unit tests for Expectation Gap Engine (Strategy E7).

Tests:
1. Positive expectation gap classification.
2. Negative expectation gap classification.
3. Balanced expectation classification.
4. Data insufficient handling when inputs are missing.
5. Strategy registry routing & lookup.
6. Arbiter conviction call reachability.
"""

from unittest.mock import patch, MagicMock
import pytest

from app.services.strategies.expectation_gap import run_expectation_gap_engine
from app.services.strategies.registry import get_strategy_module, run_strategy_module
from app.services.decision_brain.arbiter import Arbiter
from app.models.schemas import ExpectationGapResponse, StrategyRunResponse


def test_positive_expectation_gap():
    """Test positive expectation gap when internal forecast > market implied growth."""
    with patch("app.services.strategies.expectation_gap.get_quote") as mock_quote, \
         patch("app.services.strategies.expectation_gap.run_reverse_dcf_c9") as mock_c9, \
         patch("app.services.strategies.expectation_gap.ResearchDataStore") as mock_store_cls:
        
        mock_quote.return_value = {"price": 1000.0, "pe_ratio": 20.0}
        mock_c9_resp = MagicMock()
        mock_c9_resp.metrics = {"implied_growth_rate_pct": 10.0}
        mock_c9.return_value = mock_c9_resp

        # Mock timeline with 25% CAGR
        mock_obs1 = MagicMock(metric="revenue", period_end="2022-03-31", value=100.0)
        mock_obs2 = MagicMock(metric="revenue", period_end="2025-03-31", value=195.3)  # ~25% CAGR over 3Y
        mock_store = MagicMock()
        mock_store.get_timeline.return_value = (None, [mock_obs1, mock_obs2], [], [], [], [])
        mock_store_cls.return_value = mock_store

        res = run_expectation_gap_engine("RELIANCE", store=mock_store)

        assert isinstance(res, ExpectationGapResponse)
        assert res.data_insufficient is False
        assert res.market_implied_growth == 10.0
        assert res.internal_forecast_growth >= 20.0
        assert res.expectation_gap >= 10.0
        assert res.gap_classification == "POSITIVE_EXPECTATION_GAP"


def test_negative_expectation_gap():
    """Test negative expectation gap when market implied growth > internal forecast."""
    with patch("app.services.strategies.expectation_gap.get_quote") as mock_quote, \
         patch("app.services.strategies.expectation_gap.run_reverse_dcf_c9") as mock_c9, \
         patch("app.services.strategies.expectation_gap.ResearchDataStore") as mock_store_cls:
        
        mock_quote.return_value = {"price": 1000.0, "pe_ratio": 60.0}
        mock_c9_resp = MagicMock()
        mock_c9_resp.metrics = {"implied_growth_rate_pct": 30.0}
        mock_c9.return_value = mock_c9_resp

        # Mock timeline with 5% CAGR
        mock_obs1 = MagicMock(metric="revenue", period_end="2022-03-31", value=100.0)
        mock_obs2 = MagicMock(metric="revenue", period_end="2025-03-31", value=115.76)  # ~5% CAGR over 3Y
        mock_store = MagicMock()
        mock_store.get_timeline.return_value = (None, [mock_obs1, mock_obs2], [], [], [], [])
        mock_store_cls.return_value = mock_store

        res = run_expectation_gap_engine("RELIANCE", store=mock_store)

        assert isinstance(res, ExpectationGapResponse)
        assert res.data_insufficient is False
        assert res.market_implied_growth == 30.0
        assert res.internal_forecast_growth <= 10.0
        assert res.expectation_gap <= -15.0
        assert res.gap_classification == "NEGATIVE_EXPECTATION_GAP"


def test_balanced_expectation_gap():
    """Test balanced expectation gap when internal forecast matches market implied growth."""
    with patch("app.services.strategies.expectation_gap.get_quote") as mock_quote, \
         patch("app.services.strategies.expectation_gap.run_reverse_dcf_c9") as mock_c9, \
         patch("app.services.strategies.expectation_gap.ResearchDataStore") as mock_store_cls:
        
        mock_quote.return_value = {"price": 1000.0, "pe_ratio": 25.0}
        mock_c9_resp = MagicMock()
        mock_c9_resp.metrics = {"implied_growth_rate_pct": 15.0}
        mock_c9.return_value = mock_c9_resp

        # Mock timeline with ~15% CAGR
        mock_obs1 = MagicMock(metric="revenue", period_end="2022-03-31", value=100.0)
        mock_obs2 = MagicMock(metric="revenue", period_end="2025-03-31", value=152.09)  # ~15% CAGR over 3Y
        mock_store = MagicMock()
        mock_store.get_timeline.return_value = (None, [mock_obs1, mock_obs2], [], [], [], [])
        mock_store_cls.return_value = mock_store

        res = run_expectation_gap_engine("RELIANCE", store=mock_store)

        assert isinstance(res, ExpectationGapResponse)
        assert res.data_insufficient is False
        assert res.expectation_gap >= -5.0 and res.expectation_gap <= 5.0
        assert res.gap_classification == "BALANCED_EXPECTATION"


def test_expectation_gap_data_insufficient():
    """Test data_insufficient handling when quote or price is invalid/missing."""
    with patch("app.services.strategies.expectation_gap.get_quote") as mock_quote, \
         patch("app.services.strategies.expectation_gap.run_reverse_dcf_c9") as mock_c9:
        
        mock_quote.return_value = {"price": 0.0, "pe_ratio": None}
        mock_c9_resp = MagicMock()
        mock_c9_resp.metrics = {"implied_growth_rate_pct": 0.0}
        mock_c9.return_value = mock_c9_resp

        res = run_expectation_gap_engine("INVALID_SYMBOL")

        assert isinstance(res, ExpectationGapResponse)
        assert res.data_insufficient is True
        assert res.gap_classification == "DATA_INSUFFICIENT"
        assert res.confidence_score == 0.0


def test_expectation_gap_registry_integration():
    """Test E7 registration and execution via strategy module registry."""
    module = get_strategy_module("E7")
    assert module.id == "E7"
    assert module.name == "Expectation Gap Engine"
    assert module.status == "production"

    run_res = run_strategy_module("E7", "RELIANCE")
    assert isinstance(run_res, StrategyRunResponse)
    assert run_res.strategy_id == "E7"
    assert "expectation_gap" in run_res.results


def test_expectation_gap_arbiter_reachability():
    """Test that Arbiter collects E7 output as part of conviction analysis."""
    arbiter = Arbiter()
    outputs = arbiter._collect_engine_outputs("RELIANCE")
    e7_output = next((o for o in outputs if o.get("engine_id") == "E7"), None)
    
    assert e7_output is not None
    assert e7_output["engine_id"] == "E7"
    assert "raw" in e7_output
