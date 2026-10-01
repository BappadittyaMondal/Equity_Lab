"""
Phase 149 Test Suite
====================
Tests for:
  1. Corporate Action Normalizer (normalize_corporate_actions) in fundamental_fetcher.py
  2. Technical Base Quality Engine (TechnicalBaseQualityEngine) in technical_base_quality.py

All tests use deterministic synthetic data only. Zero network calls. Zero yfinance live calls.
"""

import math
import types
import pytest

# ─── Import targets ───────────────────────────────────────────────────────────
from app.services.data_ingestion.fundamental_fetcher import normalize_corporate_actions
from app.services.research.technical_base_quality import TechnicalBaseQualityEngine


# ═════════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════════

class _MockSplits:
    """Minimal pandas Series mock for ticker.splits."""
    def __init__(self, data: dict):
        # data: {timestamp_ns: ratio}
        self._data = data
        self.empty = (len(data) == 0)

    def __iter__(self):
        return iter(self._data.values())

    def __ne__(self, other):
        return _MockBoolSeries([v != other for v in self._data.values()])

    @property
    def index(self):
        return _MockIndex(list(self._data.keys()))


class _MockIndex:
    def __init__(self, values):
        self._values = values

    def astype(self, dtype):
        return _MockAsTyped(self._values)


class _MockAsTyped:
    def __init__(self, values):
        self._values = values

    def __floordiv__(self, other):
        return _MockDivided([v // other for v in self._values])


class _MockDivided:
    def __ge__(self, cutoff):
        return _MockBoolMask(self._values, cutoff)

    def __init__(self, values):
        self._values = values


class _MockBoolMask:
    def __init__(self, values, cutoff):
        self._mask = [v >= cutoff for v in values]


class _MockBoolSeries:
    def __init__(self, mask):
        self._mask = mask

    def sum(self):
        return sum(self._mask)


class _FakeTicker:
    """Minimal ticker mock — no network calls."""
    def __init__(self, splits_data: dict):
        self.splits = _FakeSplitsSeries(splits_data)


class _FakeSplitsSeries:
    """Mimics a pandas Series with .empty and index timestamp filtering."""
    def __init__(self, data: dict):
        self._data = data
        self.empty = (len(data) == 0)

    def __iter__(self):
        return iter(self._data.values())


def _make_ticker_with_splits(ratios_ns: dict) -> "_FakeTicker":
    """Build a mock ticker with specified splits {timestamp_ns: ratio}."""
    ticker = types.SimpleNamespace()

    class _Series:
        def __init__(self, d):
            self._d = d
            self.empty = not bool(d)

        def __iter__(self):
            return iter(self._d.values())

        @property
        def index(self):
            ns = _Idx(list(self._d.keys()))
            return ns

        def __getitem__(self, mask):
            # mask is a boolean list; return filtered sub-series
            items = list(self._d.items())
            sub = {k: v for (k, v), m in zip(items, mask._bools) if m}
            s = _Series(sub)
            return s

        def __ne__(self, val):
            bools = [v != val for v in self._d.values()]
            return _BoolSeries(bools)

    class _Idx:
        def __init__(self, vals):
            self._vals = vals

        def astype(self, t):
            return _IdxAsType(self._vals)

    class _IdxAsType:
        def __init__(self, vals):
            self._vals = vals

        def __floordiv__(self, denom):
            return _DivResult([v // denom for v in self._vals])

    class _DivResult:
        def __init__(self, vals):
            self._vals = vals

        def __ge__(self, cutoff):
            bools = [v >= cutoff for v in self._vals]
            return _BoolMask(bools)

    class _BoolMask:
        def __init__(self, bools):
            self._bools = bools

    class _BoolSeries:
        def __init__(self, bools):
            self._bools = bools

        def sum(self):
            return sum(self._bools)

    ticker.splits = _Series(ratios_ns)
    return ticker


# ═════════════════════════════════════════════════════════════════════════════
# Part 1: Corporate Action Normalizer Tests
# ═════════════════════════════════════════════════════════════════════════════

class TestCorporateActionNormalizer:
    """Tests for normalize_corporate_actions() in fundamental_fetcher.py"""

    def test_no_splits_returns_clean(self):
        """When no splits exist, flag must be CLEAN and factor must be 1.0."""
        ticker = _make_ticker_with_splits({})
        result = normalize_corporate_actions(ticker, current_shares=1_000_000, current_eps=10.0)
        assert result["data_integrity_flag"] == "CLEAN"
        assert result["cumulative_split_factor"] == 1.0
        assert result["corporate_action_normalized_eps"] == 10.0
        assert result["corporate_action_normalized_shares"] == 1_000_000

    def test_5x_bonus_adjusts_eps_correctly(self):
        """A 5:1 bonus issue should multiply EPS by 5 and divide shares by 5."""
        import time
        recent_ns = int(time.time() * 1e9) - int(1e9 * 60 * 60 * 24 * 30)  # 30 days ago
        ticker = _make_ticker_with_splits({recent_ns: 5.0})
        result = normalize_corporate_actions(ticker, current_shares=5_000_000, current_eps=2.0, lookback_years=5)
        assert result["data_integrity_flag"] == "ADJUSTED"
        assert math.isclose(result["cumulative_split_factor"], 5.0, rel_tol=1e-4)
        # After 5:1 bonus: historical EPS = 2.0 * 5 = 10.0
        assert math.isclose(result["corporate_action_normalized_eps"], 10.0, rel_tol=1e-4)
        # Historical shares = 5_000_000 / 5 = 1_000_000
        assert math.isclose(result["corporate_action_normalized_shares"], 1_000_000, rel_tol=1e-4)

    def test_2x_split_adjusts_correctly(self):
        """A 2:1 split should produce cumulative_factor=2, EPS*2, shares/2."""
        import time
        recent_ns = int(time.time() * 1e9) - int(1e9 * 60 * 60 * 24 * 100)  # 100 days ago
        ticker = _make_ticker_with_splits({recent_ns: 2.0})
        result = normalize_corporate_actions(ticker, current_shares=2_000_000, current_eps=5.0, lookback_years=5)
        assert math.isclose(result["cumulative_split_factor"], 2.0, rel_tol=1e-4)
        assert math.isclose(result["corporate_action_normalized_eps"], 10.0, rel_tol=1e-4)
        assert math.isclose(result["corporate_action_normalized_shares"], 1_000_000, rel_tol=1e-4)

    def test_exception_returns_unverifiable(self):
        """If ticker.splits raises, flag must be UNVERIFIABLE, values unchanged."""
        class _BadTicker:
            @property
            def splits(self):
                raise RuntimeError("network error")

        result = normalize_corporate_actions(_BadTicker(), current_shares=500_000, current_eps=8.0)
        assert result["data_integrity_flag"] == "UNVERIFIABLE"
        assert result["corporate_action_normalized_eps"] == 8.0
        assert result["corporate_action_normalized_shares"] == 500_000


# ═════════════════════════════════════════════════════════════════════════════
# Part 2: TechnicalBaseQualityEngine Tests
# ═════════════════════════════════════════════════════════════════════════════

class TestWeinSteinStageClassification:
    """Tests for _classify_weinstein_stage()"""

    def test_stage2_uptrend_detected(self):
        data = {"current_price": 180.0, "dma_50": 160.0, "dma_200": 140.0,
                "high_52w": 200.0, "low_52w": 100.0}
        stage = TechnicalBaseQualityEngine._classify_weinstein_stage(data)
        assert stage == "STAGE_2_UPTREND"

    def test_stage2_early_detected(self):
        """Price > dma50 > dma200 but in lower half of 52W range → STAGE_2_EARLY."""
        data = {"current_price": 130.0, "dma_50": 125.0, "dma_200": 120.0,
                "high_52w": 200.0, "low_52w": 100.0}
        stage = TechnicalBaseQualityEngine._classify_weinstein_stage(data)
        assert stage == "STAGE_2_EARLY"

    def test_stage1_base_detected(self):
        """Price hugging 200DMA from below in lower 40% of range → STAGE_1_BASE."""
        data = {"current_price": 105.0, "dma_50": 108.0, "dma_200": 104.0,
                "high_52w": 200.0, "low_52w": 90.0}
        stage = TechnicalBaseQualityEngine._classify_weinstein_stage(data)
        assert stage == "STAGE_1_BASE"

    def test_stage4_downtrend_detected(self):
        data = {"current_price": 80.0, "dma_50": 100.0, "dma_200": 120.0,
                "high_52w": 200.0, "low_52w": 70.0}
        stage = TechnicalBaseQualityEngine._classify_weinstein_stage(data)
        assert stage == "STAGE_4_DOWNTREND"

    def test_unknown_when_missing_data(self):
        data = {"current_price": 100.0}  # Missing dma_50, dma_200, high/low
        stage = TechnicalBaseQualityEngine._classify_weinstein_stage(data)
        assert stage == "UNKNOWN"


class TestVCPScore:
    """Tests for _score_vcp()"""

    def test_at_52w_high_score_is_1(self):
        data = {"current_price": 200.0, "high_52w": 200.0, "low_52w": 100.0}
        s = TechnicalBaseQualityEngine._score_vcp(data)
        assert math.isclose(s, 1.0, rel_tol=1e-4)

    def test_40pct_below_high_score_is_0(self):
        """40% below 52W high → score = 0.0."""
        data = {"current_price": 120.0, "high_52w": 200.0, "low_52w": 50.0}
        # dist = (200-120)/200 = 0.40 → score = max(0, 1 - 0.40/0.40) = 0.0
        s = TechnicalBaseQualityEngine._score_vcp(data)
        assert s == 0.0

    def test_15pct_below_high_gives_expected_score(self):
        """15% below 52W high → score = 1 - 0.15/0.40 = 0.625."""
        data = {"current_price": 170.0, "high_52w": 200.0, "low_52w": 50.0}
        s = TechnicalBaseQualityEngine._score_vcp(data)
        assert math.isclose(s, 0.625, rel_tol=1e-3)

    def test_missing_data_returns_neutral(self):
        data = {}
        s = TechnicalBaseQualityEngine._score_vcp(data)
        assert s == 0.50


class TestBaseLengthScore:
    """Tests for _score_base_length()"""

    def test_52_weeks_base_gives_score_1(self):
        data = {"base_length_weeks": 52}
        s = TechnicalBaseQualityEngine._score_base_length(data)
        assert math.isclose(s, 1.0, rel_tol=1e-4)

    def test_4_weeks_base_gives_score_0(self):
        data = {"base_length_weeks": 4}
        s = TechnicalBaseQualityEngine._score_base_length(data)
        assert math.isclose(s, 0.0, abs_tol=1e-4)

    def test_28_weeks_midpoint(self):
        """28 weeks → (28-4)/48 = 0.50."""
        data = {"base_length_weeks": 28}
        s = TechnicalBaseQualityEngine._score_base_length(data)
        assert math.isclose(s, 0.50, rel_tol=1e-3)

    def test_inference_from_tight_52w_range(self):
        """When base_length_weeks not provided, tight 52W range should give high score."""
        # high=110, low=100 → compression=10/110≈0.091 → score = 1-0.091/0.60 ≈ 0.848
        data = {"high_52w": 110.0, "low_52w": 100.0}
        s = TechnicalBaseQualityEngine._score_base_length(data)
        assert s > 0.70  # Tight range implies long base

    def test_wide_range_gives_low_score(self):
        """Wide 52W range (volatile) → low inferred base score."""
        # high=200, low=50 → compression=150/200=0.75 → score = max(0, 1-0.75/0.60) = 0
        data = {"high_52w": 200.0, "low_52w": 50.0}
        s = TechnicalBaseQualityEngine._score_base_length(data)
        assert s == 0.0


class TestOBVDivergenceScore:
    """Tests for _score_obv_divergence()"""

    def test_high_vol_z_in_base_with_delivery_gives_max(self):
        """vol_z >= 1.0 in lower half + delivery >= 1.5 → 0.50 + 0.25 + 0.25 = 1.00."""
        data = {"vol_z": 2.0, "delivery_turnover": 2.5,
                "current_price": 110.0, "high_52w": 200.0, "low_52w": 100.0}
        # price_pos = (110-100)/100 = 0.10 → in lower half
        s = TechnicalBaseQualityEngine._score_obv_divergence(data)
        assert math.isclose(s, 1.0, rel_tol=1e-4)

    def test_negative_vol_z_reduces_score(self):
        """vol_z < 0 → 0.50 - 0.25 = 0.25."""
        data = {"vol_z": -1.5, "current_price": 150.0, "high_52w": 200.0, "low_52w": 100.0}
        s = TechnicalBaseQualityEngine._score_obv_divergence(data)
        assert math.isclose(s, 0.25, rel_tol=1e-4)

    def test_no_data_returns_neutral(self):
        s = TechnicalBaseQualityEngine._score_obv_divergence({})
        assert s == 0.50


class TestCompositeScore:
    """Integration tests for TechnicalBaseQualityEngine.score()"""

    def test_strong_base_setup_label(self):
        """
        Stage 2 uptrend + tight VCP + long base + accumulation volume
        → should yield STRONG_BASE_SETUP (>= 0.80).
        """
        data = {
            "current_price": 180.0,
            "dma_50": 160.0,
            "dma_200": 140.0,
            "high_52w": 200.0,
            "low_52w": 160.0,       # tight range → long base inferred
            "base_length_weeks": 52,
            "vol_z": 2.0,
            "delivery_turnover": 2.0,
        }
        score, breakdown = TechnicalBaseQualityEngine.score(data)
        assert breakdown["readiness_label"] == "STRONG_BASE_SETUP"
        assert score >= 0.80

    def test_downtrend_gives_low_score(self):
        """Stage 4 downtrend should produce very low composite score."""
        data = {
            "current_price": 70.0,
            "dma_50": 100.0,
            "dma_200": 130.0,
            "high_52w": 200.0,
            "low_52w": 60.0,
            "base_length_weeks": 4,
            "vol_z": -2.0,
        }
        score, breakdown = TechnicalBaseQualityEngine.score(data)
        assert breakdown["weinstein_stage"] == "STAGE_4_DOWNTREND"
        assert score < 0.40

    def test_breakdown_keys_always_present(self):
        """score() must always return all 7 breakdown keys, even with empty data."""
        score, breakdown = TechnicalBaseQualityEngine.score({})
        required_keys = {
            "weinstein_stage", "stage_score", "vcp_score",
            "base_length_score", "obv_divergence_score",
            "composite_base_quality", "readiness_label"
        }
        assert required_keys.issubset(set(breakdown.keys()))
        assert 0.0 <= score <= 1.0

    def test_score_in_valid_range(self):
        """Composite score must always be in [0.0, 1.0] regardless of input."""
        import random
        random.seed(42)
        for _ in range(50):
            data = {
                "current_price": random.uniform(10, 500),
                "dma_50": random.uniform(10, 500),
                "dma_200": random.uniform(10, 500),
                "high_52w": random.uniform(100, 600),
                "low_52w": random.uniform(10, 100),
                "base_length_weeks": random.uniform(0, 100),
                "vol_z": random.uniform(-3, 5),
                "delivery_turnover": random.uniform(0, 5),
            }
            score, _ = TechnicalBaseQualityEngine.score(data)
            assert 0.0 <= score <= 1.0, f"Score out of range: {score} for data: {data}"

    def test_weights_sum_to_one(self):
        """Architecture check: component weights must sum to exactly 1.0."""
        total = (
            TechnicalBaseQualityEngine.W_STAGE
            + TechnicalBaseQualityEngine.W_VCP
            + TechnicalBaseQualityEngine.W_BASE
            + TechnicalBaseQualityEngine.W_OBV
        )
        assert math.isclose(total, 1.0, rel_tol=1e-9), f"Weights sum to {total}, not 1.0"

    def test_no_new_scoring_pipeline_created(self):
        """
        Architecture guard: TechnicalBaseQualityEngine must NOT produce a
        'passed' / 'status' / 'vetoes' key — those are the Central Arbiter's
        output contract. This engine only enriches the TECHNICAL sub-signal.
        """
        _, breakdown = TechnicalBaseQualityEngine.score({"current_price": 100.0})
        arbiter_keys = {"passed", "status", "vetoes", "fatal_vetoes"}
        assert not arbiter_keys.intersection(set(breakdown.keys())), (
            "TechnicalBaseQualityEngine must not produce Arbiter contract keys. "
            "It is a sub-signal enricher, not a parallel scoring pipeline."
        )
