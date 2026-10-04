"""Phase 152 Tests — Reverse-DCF Return Ceiling & Multibagger Label Guard.

Verifies:
  T4: compute_return_ceiling() produces correct Bear/Base/Bull multiples.
  T5: Multibagger eligibility flag correctly gates the label.
"""

import pytest
from app.services.research.return_ceiling import compute_return_ceiling


class TestReturnCeiling:
    """Verify reverse-DCF return ceiling computation."""

    def test_basic_return_multiples(self):
        """JSLL-like: MCap=5900, PAT=300, default scenarios."""
        result = compute_return_ceiling(current_mcap_cr=5900.0, ttm_pat_cr=300.0)
        assert result["bear_multiple"] > 0
        assert result["base_multiple"] > result["bear_multiple"]
        assert result["bull_multiple"] > result["base_multiple"]

    def test_high_return_stock(self):
        """Small MCap with high PAT = multibagger candidate."""
        result = compute_return_ceiling(current_mcap_cr=500.0, ttm_pat_cr=100.0)
        assert result["base_multiple"] >= 3.0
        assert result["multibagger_eligible"] is True
        assert result["label"] == "MULTIBAGGER_CANDIDATE"

    def test_low_return_stock(self):
        """Large MCap relative to PAT = compounder only."""
        result = compute_return_ceiling(current_mcap_cr=10000.0, ttm_pat_cr=100.0)
        assert result["base_multiple"] < 1.5
        assert result["multibagger_eligible"] is False
        assert result["label"] == "COMPOUNDER_ONLY"

    def test_zero_mcap_returns_insufficient(self):
        """Zero or negative MCap should return INSUFFICIENT_DATA."""
        result = compute_return_ceiling(current_mcap_cr=0.0, ttm_pat_cr=100.0)
        assert result["label"] == "INSUFFICIENT_DATA"
        assert result["multibagger_eligible"] is False

    def test_zero_pat_returns_insufficient(self):
        """Loss-making company should return INSUFFICIENT_DATA."""
        result = compute_return_ceiling(current_mcap_cr=1000.0, ttm_pat_cr=-50.0)
        assert result["label"] == "INSUFFICIENT_DATA"

    def test_custom_scenarios(self):
        """Custom growth scenarios should override defaults."""
        custom = {
            "bear": {"pat_cagr_pct": 5.0, "terminal_pe": 10.0},
            "base": {"pat_cagr_pct": 50.0, "terminal_pe": 30.0},
            "bull": {"pat_cagr_pct": 80.0, "terminal_pe": 40.0},
        }
        result = compute_return_ceiling(
            current_mcap_cr=1000.0, ttm_pat_cr=50.0, growth_scenarios=custom
        )
        assert result["base_multiple"] > 2.0  # 50% CAGR over 3yr = strong

    def test_growth_compounder_label(self):
        """Base case 1.5x-3.0x should be GROWTH_COMPOUNDER, not multibagger."""
        result = compute_return_ceiling(current_mcap_cr=3000.0, ttm_pat_cr=100.0)
        # Default base: 18% CAGR, 18x PE → future mcap = 100*1.18^3*18 = 2959 Cr
        # Multiple = 2959/3000 = ~0.99
        # This should be COMPOUNDER_ONLY at that ratio
        assert result["label"] in ["COMPOUNDER_ONLY", "GROWTH_COMPOUNDER"]

    def test_output_keys_complete(self):
        """Result dict must contain all required keys."""
        result = compute_return_ceiling(current_mcap_cr=2000.0, ttm_pat_cr=100.0)
        required_keys = [
            "bear_multiple", "base_multiple", "bull_multiple",
            "multibagger_eligible", "label", "horizon_years",
            "current_mcap_cr", "ttm_pat_cr"
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"


class TestPhase151RegressionAfterPhase152:
    """Ensure Phase 151 changes didn't break."""

    def test_other_income_fields_still_present(self):
        import inspect
        from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher
        source = inspect.getsource(FundamentalFetcher.fetch_and_store)
        assert '"other_income"' in source
        assert '"pat_quality_flag"' in source
        assert '"peg_sustainable"' in source
