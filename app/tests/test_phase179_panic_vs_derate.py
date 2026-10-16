"""Phase 179 Tests: Panic-vs-Structural-De-Rating Classifier.

Covers:
  T1  – Clear panic scenario → PANIC_DISLOCATION_OPPORTUNITY
  T2  – Clear de-rating scenario → STRUCTURAL_DE_RATING_AVOID
  T3  – Empty item → AMBIGUOUS_AWAIT_NEXT_QUARTER, confidence LOW
  T4  – methodology_note always present (panic path)
  T5  – methodology_note always present (derate path)
  T6  – methodology_note always present (empty item)
  T7  – panic_signal_count / derate_signal_count types are int
  T8  – panic_signals / derate_signals are lists
  T9  – actionable_note always a non-empty string
  T10 – HIGH confidence for strong panic (≥3 panic, 0 derate)
  T11 – HIGH confidence for strong de-rate (≥3 derate, 0 panic)
  T12 – MEDIUM confidence for 2 panic + 1 derate
  T13 – RSI above 40 does NOT trigger panic signal
  T14 – price drop < 15% does NOT trigger panic drop signal
  T15 – P/E contraction triggers derate signal
  T16 – PAT growth ≥15% triggers panic signal
  T17 – PAT growth ≤ -10% triggers derate signal
  T18 – OPM below 5Y median by >3pp triggers derate signal
  T19 – ROCE QoQ improvement (+2pp) triggers panic signal
  T20 – Engine evaluate_company returns dict with 'panic_vs_derate' key
  T21 – Engine evaluate_company minimal item (no panic keys) → no crash
  T22 – Engine classmethod classify_panic_vs_derate matches standalone
  T23 – Invalid types (string fields) do not raise — graceful fallback
  T24 – Verdict is always one of the three valid strings
  T25 – confidence is always LOW | MEDIUM | HIGH
"""

import pytest
from typing import Dict, Any

from app.services.research.panic_vs_derate import classify_panic_vs_derate
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine

# ── Fixtures ──────────────────────────────────────────────────────────────────

PANIC_ITEM: Dict[str, Any] = {
    "symbol": "TEST_PANIC",
    "rsi_14": 32.0,
    "price_drop_3m_pct": 22.0,
    "roce_latest": 22.0,
    "roce_qoq_change": 1.0,   # flat — not an improvement signal
    "opm_latest": 18.0,
    "opm_5yr": 15.0,          # OPM above 5Y median → panic signal
    "pat_growth_latest": 20.0,
}

DERATE_ITEM: Dict[str, Any] = {
    "symbol": "TEST_DERATE",
    "rsi_14": 55.0,            # not oversold
    "price_drop_3m_pct": 8.0,  # drop < 15%
    "roce_latest": 8.0,        # < 10% → derate
    "roce_qoq_change": -5.0,   # declining ≥ 3pp → derate
    "opm_latest": 8.0,
    "opm_5yr": 14.0,           # OPM 6pp below 5Y → derate
    "pat_growth_latest": -15.0,
}

EMPTY_ITEM: Dict[str, Any] = {}

VALID_VERDICTS = {
    "PANIC_DISLOCATION_OPPORTUNITY",
    "STRUCTURAL_DE_RATING_AVOID",
    "AMBIGUOUS_AWAIT_NEXT_QUARTER",
}

VALID_CONFIDENCES = {"LOW", "MEDIUM", "HIGH"}

# ── Tests ─────────────────────────────────────────────────────────────────────


class TestClassifyPanicVsDerate:

    def test_t1_clear_panic_verdict(self):
        """T1: Strong panic item → PANIC_DISLOCATION_OPPORTUNITY."""
        result = classify_panic_vs_derate(PANIC_ITEM)
        assert result["verdict"] == "PANIC_DISLOCATION_OPPORTUNITY", (
            f"Expected PANIC_DISLOCATION_OPPORTUNITY, got {result['verdict']}\n"
            f"panic_signals={result['panic_signals']}\nderate_signals={result['derate_signals']}"
        )

    def test_t2_clear_derate_verdict(self):
        """T2: Strong de-rating item → STRUCTURAL_DE_RATING_AVOID."""
        result = classify_panic_vs_derate(DERATE_ITEM)
        assert result["verdict"] == "STRUCTURAL_DE_RATING_AVOID", (
            f"Expected STRUCTURAL_DE_RATING_AVOID, got {result['verdict']}\n"
            f"panic_signals={result['panic_signals']}\nderate_signals={result['derate_signals']}"
        )

    def test_t3_empty_item_ambiguous(self):
        """T3: Empty item → AMBIGUOUS_AWAIT_NEXT_QUARTER, confidence LOW."""
        result = classify_panic_vs_derate(EMPTY_ITEM)
        assert result["verdict"] == "AMBIGUOUS_AWAIT_NEXT_QUARTER"
        assert result["confidence"] == "LOW"

    def test_t4_methodology_note_panic(self):
        """T4: methodology_note always present in panic result."""
        result = classify_panic_vs_derate(PANIC_ITEM)
        assert "methodology_note" in result
        assert isinstance(result["methodology_note"], str) and len(result["methodology_note"]) > 10

    def test_t5_methodology_note_derate(self):
        """T5: methodology_note always present in de-rate result."""
        result = classify_panic_vs_derate(DERATE_ITEM)
        assert "methodology_note" in result
        assert len(result["methodology_note"]) > 10

    def test_t6_methodology_note_empty(self):
        """T6: methodology_note always present even for empty item."""
        result = classify_panic_vs_derate(EMPTY_ITEM)
        assert "methodology_note" in result
        assert len(result["methodology_note"]) > 10

    def test_t7_signal_counts_are_int(self):
        """T7: panic_signal_count and derate_signal_count are ints."""
        result = classify_panic_vs_derate(PANIC_ITEM)
        assert isinstance(result["panic_signal_count"], int)
        assert isinstance(result["derate_signal_count"], int)

    def test_t8_signals_are_lists(self):
        """T8: panic_signals and derate_signals are lists of strings."""
        result = classify_panic_vs_derate(PANIC_ITEM)
        assert isinstance(result["panic_signals"], list)
        assert isinstance(result["derate_signals"], list)
        for sig in result["panic_signals"]:
            assert isinstance(sig, str)

    def test_t9_actionable_note_non_empty(self):
        """T9: actionable_note is always a non-empty string."""
        for item in [PANIC_ITEM, DERATE_ITEM, EMPTY_ITEM]:
            result = classify_panic_vs_derate(item)
            assert isinstance(result.get("actionable_note"), str)
            assert len(result["actionable_note"]) > 5

    def test_t10_high_confidence_strong_panic(self):
        """T10: ≥3 panic signals, 0 derate → HIGH confidence."""
        # RSI, price drop, ROCE high, OPM above 5Y, PAT growth
        item = {
            "rsi_14": 30.0,           # panic: RSI oversold
            "price_drop_3m_pct": 20.0, # panic: 3M drop ≥15%
            "roce_latest": 18.0,       # panic: ROCE≥15
            "opm_latest": 20.0,
            "opm_5yr": 15.0,           # panic: OPM above 5Y
            "pat_growth_latest": 20.0, # panic: PAT ≥15%
            # No derate signals
        }
        result = classify_panic_vs_derate(item)
        assert result["panic_signal_count"] >= 3
        assert result["derate_signal_count"] == 0
        assert result["confidence"] == "HIGH"

    def test_t11_high_confidence_strong_derate(self):
        """T11: ≥3 derate signals, 0 panic → HIGH confidence."""
        item = {
            "rsi_14": 65.0,            # derate: RSI ≥60 (no oversold)
            "roce_latest": 7.0,        # derate: ROCE <10
            "roce_qoq_change": -4.0,   # derate: QoQ decline ≥3pp
            "opm_latest": 7.0,
            "opm_5yr": 14.0,           # derate: OPM compression
            "pat_growth_latest": -12.0, # derate: PAT ≤-10%
        }
        result = classify_panic_vs_derate(item)
        assert result["derate_signal_count"] >= 3
        assert result["panic_signal_count"] == 0
        assert result["confidence"] == "HIGH"

    def test_t12_medium_confidence_mixed(self):
        """T12: 2 panic + 1 derate → PANIC with MEDIUM confidence."""
        item = {
            "rsi_14": 35.0,            # panic: RSI oversold
            "price_drop_3m_pct": 18.0, # panic: 3M drop
            "roce_qoq_change": -4.0,   # derate: QoQ ROCE decline
        }
        result = classify_panic_vs_derate(item)
        assert result["panic_signal_count"] == 2
        assert result["derate_signal_count"] == 1
        assert result["verdict"] == "PANIC_DISLOCATION_OPPORTUNITY"
        assert result["confidence"] == "MEDIUM"

    def test_t13_rsi_above_40_no_panic_signal(self):
        """T13: RSI=55 should NOT trigger RSI panic signal."""
        item = {"rsi_14": 55.0}
        result = classify_panic_vs_derate(item)
        assert not any("RSI" in s and "oversold" in s for s in result["panic_signals"])

    def test_t14_price_drop_below_15_no_panic_signal(self):
        """T14: price_drop_3m_pct=10 (< 15%) should NOT trigger drop panic signal."""
        item = {"price_drop_3m_pct": 10.0}
        result = classify_panic_vs_derate(item)
        assert not any("3M" in s for s in result["panic_signals"])

    def test_t15_pe_contraction_triggers_derate(self):
        """T15: P/E contracted to 80% of 1Y avg → de-rating signal."""
        item = {
            "pe_ratio": 16.0,
            "pe_1yr_avg": 20.0,  # 16/20 = 0.80 ≤ 0.85
        }
        result = classify_panic_vs_derate(item)
        assert result["derate_signal_count"] >= 1
        assert any("P/E" in s for s in result["derate_signals"])

    def test_t16_pat_growth_triggers_panic(self):
        """T16: PAT growth = 20% → panic signal (earnings growing)."""
        item = {"pat_growth_latest": 20.0}
        result = classify_panic_vs_derate(item)
        assert any("PAT" in s for s in result["panic_signals"])

    def test_t17_pat_decline_triggers_derate(self):
        """T17: PAT growth = -15% → de-rating signal."""
        item = {"pat_growth_latest": -15.0}
        result = classify_panic_vs_derate(item)
        assert any("PAT" in s for s in result["derate_signals"])

    def test_t18_opm_compression_triggers_derate(self):
        """T18: OPM 6pp below 5Y median → de-rating signal."""
        item = {
            "opm_latest": 8.0,
            "opm_5yr": 14.0,  # 8 < 14-3 = 11 → derate
        }
        result = classify_panic_vs_derate(item)
        assert any("OPM" in s for s in result["derate_signals"])

    def test_t19_roce_improvement_triggers_panic(self):
        """T19: ROCE QoQ +3pp → panic signal (fundamentals strengthening)."""
        item = {"roce_qoq_change": 3.0}
        result = classify_panic_vs_derate(item)
        assert any("ROCE improved" in s for s in result["panic_signals"])

    def test_t20_engine_returns_panic_vs_derate_key(self):
        """T20: evaluate_company() return dict must contain 'panic_vs_derate' key."""
        minimal_item = {"symbol": "TEST", "company_name": "Test Co"}
        result = InstitutionalMultibaggerEngine.evaluate_company(minimal_item)
        assert "panic_vs_derate" in result, (
            f"'panic_vs_derate' key missing from evaluate_company() result. Keys: {list(result.keys())}"
        )

    def test_t21_engine_minimal_item_no_crash(self):
        """T21: evaluate_company() with no panic keys → must not raise."""
        minimal_item = {"symbol": "SAFE_TEST"}
        try:
            result = InstitutionalMultibaggerEngine.evaluate_company(minimal_item)
            assert isinstance(result, dict)
        except Exception as exc:
            pytest.fail(f"evaluate_company() crashed on minimal item: {exc}")

    def test_t22_engine_classmethod_matches_standalone(self):
        """T22: Engine classmethod and standalone function return same verdict."""
        result_engine = InstitutionalMultibaggerEngine.classify_panic_vs_derate(PANIC_ITEM)
        result_standalone = classify_panic_vs_derate(PANIC_ITEM)
        assert result_engine["verdict"] == result_standalone["verdict"]
        assert result_engine["panic_signal_count"] == result_standalone["panic_signal_count"]

    def test_t23_invalid_string_types_no_crash(self):
        """T23: String values for numeric fields must not raise — graceful fallback."""
        bad_item = {
            "rsi_14": "not_a_number",
            "price_drop_3m_pct": "bad",
            "roce_latest": None,
            "pat_growth_latest": "N/A",
        }
        try:
            result = classify_panic_vs_derate(bad_item)
            assert isinstance(result, dict)
        except Exception as exc:
            pytest.fail(f"classify_panic_vs_derate raised on invalid input: {exc}")

    def test_t24_verdict_is_valid_string(self):
        """T24: Verdict is always one of the three valid strings."""
        for item in [PANIC_ITEM, DERATE_ITEM, EMPTY_ITEM]:
            result = classify_panic_vs_derate(item)
            assert result["verdict"] in VALID_VERDICTS, (
                f"Invalid verdict: {result['verdict']}"
            )

    def test_t25_confidence_is_valid_string(self):
        """T25: Confidence is always LOW | MEDIUM | HIGH."""
        for item in [PANIC_ITEM, DERATE_ITEM, EMPTY_ITEM]:
            result = classify_panic_vs_derate(item)
            assert result["confidence"] in VALID_CONFIDENCES, (
                f"Invalid confidence: {result['confidence']}"
            )
