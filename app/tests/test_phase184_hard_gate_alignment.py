"""Phase 184 — Hard Gate Alignment: Deterministic unit tests for the 5 specification fixes.

Tests:
  T1  — C1: SIP Compounder pledge > 0.0% → OBJECTIVE_BLOCK (zero-tolerance)
  T2  — C1: SIP Compounder pledge == 0.0% → APPROVED (compliant)
  T3  — C2: SIP Compounder non-BFSI D/E > 0.30 → OBJECTIVE_BLOCK (institutional hard gate)
  T4  — C2: SIP Compounder non-BFSI D/E <= 0.30 → not vetoed
  T5  — C3: MULTIBAGGER promoter_holding < 50% → OBJECTIVE_BLOCK
  T6  — C3: MULTIBAGGER promoter_holding >= 50% → not vetoed on promoter
  T7  — C4: MICRO_MULTIBAGGER omega < 1.0 → OBJECTIVE_BLOCK
  T8  — C4: MICRO_MULTIBAGGER omega >= 1.0 → not vetoed on omega
  T9  — C4: DEADLIEST_COMBO omega < 1.0 → OBJECTIVE_BLOCK
  T10 — C4: DEADLIEST_COMBO omega >= 1.0 → not vetoed on omega
  T11 — I2: SWING_3D close_position < 0.75 (previously 0.60) → warning triggered
  T12 — I2: SWING_3D close_position 0.65 (previously compliant, now should warn)
  T13 — I2: SWING_3D close_position >= 0.75 → no warning
  T14 — Regression: TURNAROUND still works correctly (no cross-impact)
  T15 — Regression: PRE_FLY still works correctly (no cross-impact)
  T16 — Regression: DEADLIEST_COMBO full passing payload → APPROVED
"""

import pytest
from app.services.research.intent_adaptive_engine import QueryAdaptiveConstraintEngine as QACE


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _eval(intent: str, data: dict) -> dict:
    return QACE.evaluate_adaptive_constraints(intent=intent, data=data)


def _has_veto_containing(result: dict, substring: str) -> bool:
    return any(substring.lower() in v.lower() for v in result.get("vetoes", []))


def _has_block_containing(result: dict, substring: str) -> bool:
    return any(substring.lower() in b.lower() for b in result.get("objective_blocks", []))


# ─── C1: SIP Zero Pledge ──────────────────────────────────────────────────────

def test_c1_sip_pledge_nonzero_is_vetoed():
    """C1: SIP compounder with any pledge > 0.0% must be OBJECTIVE_BLOCK vetoed."""
    data = {
        "sector": "FMCG",
        "pledged_pct": 3.5,
        "debt_to_equity": 0.10,
        "roce_latest": 25.0,
        "cfo_pat_ratio": 0.88,
    }
    result = _eval("SIP_COMPOUNDER", data)
    assert result["passed"] is False, "Pledged SIP must fail"
    assert _has_block_containing(result, "zero-tolerance"), (
        f"Expected zero-tolerance block. Blocks: {result.get('objective_blocks')}"
    )


def test_c1_sip_pledge_zero_is_approved():
    """C1: SIP compounder with pledge == 0.0% must NOT be vetoed on pledge."""
    data = {
        "sector": "FMCG",
        "pledged_pct": 0.0,
        "debt_to_equity": 0.10,
        "roce_latest": 22.0,
        "cfo_pat_ratio": 0.90,
        "caqi": 0.85,
    }
    result = _eval("SIP_COMPOUNDER", data)
    # No pledge block
    assert not _has_block_containing(result, "zero-tolerance"), (
        f"Zero pledge should not block. Blocks: {result.get('objective_blocks')}"
    )


# ─── C2: SIP D/E Hard Gate ────────────────────────────────────────────────────

def test_c2_sip_de_above_030_vetoed():
    """C2: Non-BFSI SIP compounder D/E > 0.30 must be OBJECTIVE_BLOCK vetoed."""
    data = {
        "sector": "Manufacturing",
        "pledged_pct": 0.0,
        "debt_to_equity": 0.55,
        "roce_latest": 20.0,
        "cfo_pat_ratio": 0.85,
    }
    result = _eval("SIP_COMPOUNDER", data)
    assert result["passed"] is False, "High D/E SIP must fail"
    assert _has_block_containing(result, "fortress ceiling"), (
        f"Expected D/E fortress block. Blocks: {result.get('objective_blocks')}"
    )


def test_c2_sip_de_at_030_not_vetoed():
    """C2: Non-BFSI SIP compounder D/E exactly 0.30 must NOT be vetoed on D/E."""
    data = {
        "sector": "Manufacturing",
        "pledged_pct": 0.0,
        "debt_to_equity": 0.30,
        "roce_latest": 22.0,
        "cfo_pat_ratio": 0.90,
        "caqi": 0.85,
    }
    result = _eval("SIP_COMPOUNDER", data)
    assert not _has_block_containing(result, "fortress ceiling"), (
        f"D/E=0.30 should not block. Blocks: {result.get('objective_blocks')}"
    )


# ─── C3: MULTIBAGGER Promoter Holding ────────────────────────────────────────

def test_c3_multibagger_low_promoter_vetoed():
    """C3: Multibagger with promoter_holding < 50% must be OBJECTIVE_BLOCK vetoed."""
    data = {
        "promoter_holding": 35.0,
        "incremental_roic": 25.0,
    }
    result = _eval("MULTIBAGGER", data)
    assert result["passed"] is False, "Low-promoter multibagger must fail"
    assert _has_block_containing(result, "insider-conviction"), (
        f"Expected insider-conviction block. Blocks: {result.get('objective_blocks')}"
    )


def test_c3_multibagger_high_promoter_approved():
    """C3: Multibagger with promoter_holding >= 50% must NOT be vetoed on promoter."""
    data = {
        "promoter_holding": 65.0,
        "incremental_roic": 25.0,
    }
    result = _eval("MULTIBAGGER", data)
    assert not _has_block_containing(result, "insider-conviction"), (
        f"High promoter should not trigger insider block. Blocks: {result.get('objective_blocks')}"
    )


# ─── C4: Omega Gate — MICRO_MULTIBAGGER ──────────────────────────────────────

def _micro_base() -> dict:
    return {
        "market_cap": 500.0,
        "roce_latest": 22.0,
        "debt_to_equity": 0.20,
        "pledged_pct": 0.0,
        "cfo": 50.0,  # positive
    }


def test_c4_micro_omega_below_1_vetoed():
    """C4: MICRO_MULTIBAGGER with omega < 1.0 must be OBJECTIVE_BLOCK vetoed."""
    data = {**_micro_base(), "operating_leverage_convexity": 0.72}
    result = _eval("MICRO_MULTIBAGGER", data)
    assert result["passed"] is False, "Sub-unity omega micro-multibagger must fail"
    assert _has_block_containing(result, "sub-unity"), (
        f"Expected sub-unity block. Blocks: {result.get('objective_blocks')}"
    )


def test_c4_micro_omega_above_1_not_vetoed():
    """C4: MICRO_MULTIBAGGER with omega >= 1.0 must NOT be vetoed on omega."""
    data = {**_micro_base(), "operating_leverage_convexity": 1.35}
    result = _eval("MICRO_MULTIBAGGER", data)
    assert not _has_block_containing(result, "sub-unity"), (
        f"Omega>=1.0 should not trigger sub-unity block. Blocks: {result.get('objective_blocks')}"
    )


# ─── C4: Omega Gate — DEADLIEST_COMBO ────────────────────────────────────────

def _combo_base() -> dict:
    return {
        "market_cap": 600.0,
        "roce_latest": 25.0,
        "debt_to_equity": 0.20,
        "pledged_pct": 0.0,
        "cfo": 80.0,  # positive
        "circuit_headroom_pct": 8.0,
    }


def test_c4_combo_omega_below_1_vetoed():
    """C4: DEADLIEST_COMBO with omega < 1.0 must be OBJECTIVE_BLOCK vetoed."""
    data = {**_combo_base(), "operating_leverage_convexity": 0.55}
    result = _eval("DEADLIEST_COMBO", data)
    assert result["passed"] is False, "Sub-unity omega deadliest combo must fail"
    assert _has_block_containing(result, "sub-unity"), (
        f"Expected sub-unity block for combo. Blocks: {result.get('objective_blocks')}"
    )


def test_c4_combo_omega_above_1_not_vetoed():
    """C4: DEADLIEST_COMBO with omega >= 1.0 must NOT be vetoed on omega."""
    data = {**_combo_base(), "operating_leverage_convexity": 1.20}
    result = _eval("DEADLIEST_COMBO", data)
    assert not _has_block_containing(result, "sub-unity"), (
        f"Omega>=1.0 combo should not block. Blocks: {result.get('objective_blocks')}"
    )


# ─── I2: SWING_3D Close Position ─────────────────────────────────────────────

def test_i2_swing3d_close_pos_below_075_warns():
    """I2: SWING_3D close_position < 0.75 must generate a warning (previous threshold was 0.60)."""
    data = {"close_position": 0.68}  # was previously compliant (>0.60), now should warn
    result = _eval("SWING_3D", data)
    assert any("0.75" in w for w in result.get("warnings", [])), (
        f"Expected close position warning at 0.68. Warnings: {result.get('warnings')}"
    )


def test_i2_swing3d_close_pos_below_060_warns():
    """I2: SWING_3D close_position below old threshold 0.60 must still warn."""
    data = {"close_position": 0.50}
    result = _eval("SWING_3D", data)
    assert any("0.75" in w for w in result.get("warnings", [])), (
        f"Expected close position warning at 0.50. Warnings: {result.get('warnings')}"
    )


def test_i2_swing3d_close_pos_above_075_no_warn():
    """I2: SWING_3D close_position >= 0.75 must NOT generate close-position warning."""
    data = {"close_position": 0.82}
    result = _eval("SWING_3D", data)
    close_warns = [w for w in result.get("warnings", []) if "close position" in w.lower()]
    assert len(close_warns) == 0, (
        f"close_pos=0.82 should not warn. Warnings: {result.get('warnings')}"
    )


# ─── Regression Tests ─────────────────────────────────────────────────────────

def test_regression_turnaround_not_affected():
    """Regression: TURNAROUND branch still works correctly — no cross-contamination from Phase 184."""
    data = {
        "interest_coverage": 2.5,
        "cfo": 30.0,
        "pledged_pct": 8.0,  # below turnaround 10% ceiling → should be fine
    }
    result = _eval("TURNAROUND", data)
    # Turnaround pledge limit is 10%, 8% is fine
    assert not any("zero-tolerance" in v for v in result.get("vetoes", [])), (
        "TURNAROUND should NOT apply SIP zero-tolerance pledge rule"
    )


def test_regression_prefly_not_affected():
    """Regression: PRE_FLY branch not contaminated by Phase 184 changes."""
    data = {
        "circuit_headroom_pct": 5.0,
        "market_cap": 800.0,
    }
    result = _eval("PRE_FLY", data)
    # Should not veto on promoter or pledge (no such gate in pre-fly)
    assert not _has_block_containing(result, "insider-conviction"), (
        "PRE_FLY should NOT apply multibagger promoter gate"
    )


def test_regression_deadliest_combo_full_pass():
    """Regression: DEADLIEST_COMBO with all gates satisfied should PASS."""
    data = {
        "market_cap": 800.0,
        "roce_latest": 25.0,
        "debt_to_equity": 0.20,
        "pledged_pct": 0.0,
        "cfo": 80.0,
        "circuit_headroom_pct": 8.0,
        "operating_leverage_convexity": 1.40,
    }
    result = _eval("DEADLIEST_COMBO", data)
    assert result["passed"] is True, (
        f"Full compliant DEADLIEST_COMBO should pass. Vetoes: {result.get('vetoes')}"
    )
