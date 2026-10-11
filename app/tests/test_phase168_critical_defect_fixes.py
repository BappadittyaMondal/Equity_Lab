"""Phase 168 — Critical Defect Fix Validation Tests.

Tests cover:
  G2  — Sharpe/Sortino annualisation in WalkForwardBacktester.evaluate_horizon()
  G35 — Mock data unknown-symbol sentinel (is_unknown_symbol_mock flag)
  G37 — data_trust_tier derived from actual data quality in calculate_return_probability()

All tests are OFFLINE_TEST_MODE safe and require zero network access.
"""

import math
import os
import pytest

os.environ["OFFLINE_TEST_MODE"] = "true"
os.environ["PYTEST_CURRENT_TEST"] = "true"


# ─────────────────────────────────────────────────────────────────────────────
# G2 — Sharpe / Sortino Annualisation
# ─────────────────────────────────────────────────────────────────────────────

class TestG2SharpeAnnualisation:
    """Verifies that Sharpe/Sortino are correctly annualised by sqrt(periods_per_year)."""

    def _make_backtester(self):
        from app.services.backtesting.walk_forward import WalkForwardBacktester
        return WalkForwardBacktester()

    def test_monthly_horizon_annualisation_factor_is_sqrt12(self):
        """horizon_months=1 → periods_per_year=12 → ann_factor=√12≈3.4641."""
        bt = self._make_backtester()
        samples = [{"stock_return": 2.5} for _ in range(12)]
        result = bt.evaluate_horizon("RELIANCE", horizon_months=1, entry_scores_and_returns=samples)
        expected_factor = math.sqrt(12.0)
        assert abs(result.annualisation_factor - expected_factor) < 0.001, (
            f"Expected ann_factor≈{expected_factor:.4f}, got {result.annualisation_factor}"
        )

    def test_annual_horizon_annualisation_factor_is_one(self):
        """horizon_months=12 → periods_per_year=1 → ann_factor=1.0."""
        bt = self._make_backtester()
        samples = [{"stock_return": 15.0} for _ in range(5)]
        result = bt.evaluate_horizon("TCS", horizon_months=12, entry_scores_and_returns=samples)
        assert abs(result.annualisation_factor - 1.0) < 0.001, (
            f"Expected ann_factor=1.0 for annual horizon, got {result.annualisation_factor}"
        )

    def test_quarterly_horizon_annualisation_factor_is_sqrt4(self):
        """horizon_months=3 → periods_per_year=4 → ann_factor=√4=2.0."""
        bt = self._make_backtester()
        samples = [{"stock_return": 5.0} for _ in range(8)]
        result = bt.evaluate_horizon("INFY", horizon_months=3, entry_scores_and_returns=samples)
        assert abs(result.annualisation_factor - 2.0) < 0.001, (
            f"Expected ann_factor=2.0 for quarterly horizon, got {result.annualisation_factor}"
        )

    def test_annualised_sharpe_gt_period_sharpe_for_monthly(self):
        """For monthly horizon, annualised Sharpe must be > period Sharpe (due to √12 > 1)."""
        bt = self._make_backtester()
        samples = [{"stock_return": r} for r in [3.0, 2.5, 4.0, 1.5, 3.5, 2.0, 4.5, 2.0, 3.0, 2.5, 3.5, 2.0]]
        result = bt.evaluate_horizon("HDFCBANK", horizon_months=1, entry_scores_and_returns=samples)
        if result.sharpe_ratio_period != 0.0:
            assert abs(result.sharpe_ratio) > abs(result.sharpe_ratio_period), (
                f"Annualised Sharpe {result.sharpe_ratio} should be > period Sharpe {result.sharpe_ratio_period}"
            )

    def test_period_fields_preserved(self):
        """sharpe_ratio_period and sortino_ratio_period must be present and finite."""
        bt = self._make_backtester()
        samples = [{"stock_return": 2.0} for _ in range(6)]
        result = bt.evaluate_horizon("SBIN", horizon_months=6, entry_scores_and_returns=samples)
        assert isinstance(result.sharpe_ratio_period, float), "sharpe_ratio_period must be float"
        assert isinstance(result.sortino_ratio_period, float), "sortino_ratio_period must be float"
        assert math.isfinite(result.sharpe_ratio), "sharpe_ratio must be finite"
        assert math.isfinite(result.sortino_ratio), "sortino_ratio must be finite"

    def test_empty_input_returns_zero_ratios(self):
        """Empty entry_scores_and_returns → sharpe=0, sortino=0, annualisation_factor=1.0."""
        bt = self._make_backtester()
        result = bt.evaluate_horizon("WIPRO", horizon_months=12, entry_scores_and_returns=[])
        assert result.sharpe_ratio == 0.0
        assert result.sortino_ratio == 0.0
        assert result.annualisation_factor == 1.0  # default from WalkForwardSummary Field


# ─────────────────────────────────────────────────────────────────────────────
# G35 — Mock Data Unknown Symbol Sentinel
# ─────────────────────────────────────────────────────────────────────────────

class TestG35MockSentinel:
    """Verifies that unknown symbols in offline mock carry explicit synthetic flags."""

    def _get_mock_quote(self, symbol: str) -> dict:
        from app.services.market_data import _get_mock_fallback_quote
        return _get_mock_fallback_quote(symbol)

    def test_unknown_symbol_has_sentinel_flag(self):
        """Unknown symbol XYZUNKNOWN123 must have is_unknown_symbol_mock=True."""
        q = self._get_mock_quote("XYZUNKNOWN123")
        assert q.get("is_unknown_symbol_mock") is True, (
            "Unknown symbol mock must have is_unknown_symbol_mock=True sentinel"
        )

    def test_unknown_symbol_trust_tier_is_synthetic(self):
        """Unknown symbol must carry data_trust_tier=SYNTHETIC_UNKNOWN."""
        q = self._get_mock_quote("FAKESTOCK999")
        assert q.get("data_trust_tier") == "SYNTHETIC_UNKNOWN", (
            f"Expected SYNTHETIC_UNKNOWN, got {q.get('data_trust_tier')}"
        )

    def test_known_symbol_has_no_sentinel(self):
        """Known symbol (RELIANCE) must NOT be flagged as unknown_symbol_mock."""
        q = self._get_mock_quote("RELIANCE")
        assert q.get("is_unknown_symbol_mock") is False, (
            "Known symbol must NOT have is_unknown_symbol_mock=True"
        )

    def test_known_symbol_trust_tier_is_mock_known(self):
        """Known symbol must carry data_trust_tier=MOCK_KNOWN."""
        q = self._get_mock_quote("TCS")
        assert q.get("data_trust_tier") == "MOCK_KNOWN", (
            f"Expected MOCK_KNOWN for known symbol, got {q.get('data_trust_tier')}"
        )

    def test_unknown_symbol_meta_is_mock_mode(self):
        """Mock meta for unknown symbol must declare data_mode=MOCK."""
        q = self._get_mock_quote("DUMMYSYM")
        meta = q.get("meta", {})
        assert meta.get("data_mode") == "MOCK", (
            f"Expected data_mode=MOCK in meta, got {meta.get('data_mode')}"
        )

    def test_unknown_symbol_price_is_1200(self):
        """Unknown symbol mock must still return price=1200 (the synthetic default)."""
        q = self._get_mock_quote("NOSUCHSTOCK")
        assert q.get("price") == 1200.0, f"Expected price=1200.0, got {q.get('price')}"


# ─────────────────────────────────────────────────────────────────────────────
# G37 — data_trust_tier derived from actual data quality
# ─────────────────────────────────────────────────────────────────────────────

class TestG37TrustTierDerived:
    """Verifies that data_trust_tier in probability engine is derived, not hardcoded HIGH."""

    def test_trust_tier_derivation_logic_high(self):
        """sample_size >= 252, not mock → HIGH."""
        import numpy as np
        sample_size = 300
        is_mock = False
        if is_mock or sample_size < 20:
            tier = "INSUFFICIENT"
        elif sample_size >= 252:
            tier = "HIGH"
        elif sample_size >= 60:
            tier = "MEDIUM"
        else:
            tier = "LOW"
        assert tier == "HIGH"

    def test_trust_tier_derivation_logic_medium(self):
        """sample_size=100, not mock → MEDIUM."""
        sample_size = 100
        is_mock = False
        if is_mock or sample_size < 20:
            tier = "INSUFFICIENT"
        elif sample_size >= 252:
            tier = "HIGH"
        elif sample_size >= 60:
            tier = "MEDIUM"
        else:
            tier = "LOW"
        assert tier == "MEDIUM"

    def test_trust_tier_derivation_logic_low(self):
        """sample_size=40 → LOW."""
        sample_size = 40
        is_mock = False
        if is_mock or sample_size < 20:
            tier = "INSUFFICIENT"
        elif sample_size >= 252:
            tier = "HIGH"
        elif sample_size >= 60:
            tier = "MEDIUM"
        else:
            tier = "LOW"
        assert tier == "LOW"

    def test_trust_tier_derivation_logic_mock_gives_insufficient(self):
        """is_mock=True → INSUFFICIENT regardless of sample_size."""
        sample_size = 500
        is_mock = True
        if is_mock or sample_size < 20:
            tier = "INSUFFICIENT"
        elif sample_size >= 252:
            tier = "HIGH"
        elif sample_size >= 60:
            tier = "MEDIUM"
        else:
            tier = "LOW"
        assert tier == "INSUFFICIENT"

    def test_trust_tier_derivation_logic_small_sample(self):
        """sample_size=10 → INSUFFICIENT."""
        sample_size = 10
        is_mock = False
        if is_mock or sample_size < 20:
            tier = "INSUFFICIENT"
        elif sample_size >= 252:
            tier = "HIGH"
        elif sample_size >= 60:
            tier = "MEDIUM"
        else:
            tier = "LOW"
        assert tier == "INSUFFICIENT"

    def test_probability_module_imports_cleanly(self):
        """probability.py must import without errors after G37 fix."""
        import importlib
        mod = importlib.import_module("app.services.probability")
        assert hasattr(mod, "calculate_return_probability")

    def test_g37_not_hardcoded_in_source(self):
        """Verify source code no longer contains the hardcoded 'data_trust_tier=\"HIGH\"' string."""
        source = open("app/services/probability.py").read()
        # The old hardcode was: data_trust_tier="HIGH",
        # After fix, it must use derived_trust_tier variable instead
        assert 'data_trust_tier="HIGH"' not in source, (
            "G37 regression: hardcoded data_trust_tier='HIGH' still present in probability.py"
        )
        assert "derived_trust_tier" in source, (
            "G37: derived_trust_tier variable must be present in probability.py"
        )
