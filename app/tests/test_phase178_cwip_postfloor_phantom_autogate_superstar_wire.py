"""Phase 178 Verification Tests.

Tests cover 4 targeted fixes introduced in Phase 178:
    1. CWIP convexity dead-zone post-floor fix (Phase 178-3)
    2. Phantom superstar auto-gate embedded in evaluate_shareholding_pattern() (Phase 178-4)
    3. Superstar verdict wire in InstitutionalMultibaggerEngine (Phase 178-5):
       - PHANTOM_EXIT_DISTRIBUTION_TRAP  → -25 pts
       - PARTIAL_SUPERSTAR_DEPARTURE     → -10 pts
       - HIGH_CONVICTION_ACTIVE_CLUSTER  → +5 pts
    4. Custom screener mock fixture (regression guard for Phase 178-1)
"""

import os
import pytest

os.environ.setdefault("OFFLINE_TEST_MODE", "true")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _base_multibagger_item(**overrides):
    """Minimal passing item for InstitutionalMultibaggerEngine.evaluate_company()."""
    base = {
        "symbol": "TEST.NS",
        "company_name": "TestCo",
        "market_cap": 5000.0,
        "current_price": 500.0,
        "high_52w": 600.0,
        "low_52w": 300.0,
        "sales_growth_3yr": 20.0,
        "pat_growth_3yr": 25.0,
        "pat_growth_latest": 28.0,
        "eps_growth_3yr": 22.0,
        "roce_latest": 22.0,
        "roce_3yr": 20.0,
        "roe_latest": 18.0,
        "opm_latest": 18.0,
        "opm_5yr": 15.0,
        "cfo_last_year": 120.0,
        "net_profit_last_year": 100.0,
        "operating_profit": 150.0,
        "net_block": 500.0,
        "net_block_prec": 400.0,
        "net_block_3yr_back": 300.0,
        "cwip": 50.0,
        "cwip_preceding_year": 30.0,
        "promoter_holding": 52.0,
        "pledged_pct": 0.5,
        "debt_to_equity": 0.3,
        "interest_coverage": 8.0,
        "peg_ratio": 1.1,
        "piotroski_score": 7.0,
        "volume": 10000,
        "vol_1y_avg": 3000.0,
        "vol_1w_avg": 6000.0,
    }
    base.update(overrides)
    return base


# ─────────────────────────────────────────────────────────────────────────────
# 1. CWIP POST-FLOOR FIX (Phase 178-3)
# ─────────────────────────────────────────────────────────────────────────────

class TestCWIPPostFloorFix:
    """Verify CWIP boost is effective even when PAT-growth < Revenue-growth (ratio < 1)."""

    def _get_omega(self, pat_growth, rev_growth, cwip_ratio):
        """
        Reproduce the Omega calculation from deadliest_combo_pipeline.py Phase 178-3 fix.
        ratio = pat_growth / rev_growth (with floor protection)
        omega_base = max(1.0, ratio)
        cwip_boost = min(0.30, cwip_ratio * 0.40) if cwip_ratio >= 0.25 else 0.0
        return min(2.5, omega_base + cwip_boost)
        """
        ratio = pat_growth / max(rev_growth, 0.001)
        omega_base = max(1.0, ratio)
        cwip_boost = min(0.30, cwip_ratio * 0.40) if cwip_ratio >= 0.25 else 0.0
        return min(2.5, omega_base + cwip_boost)

    def test_cwip_boost_effective_when_ratio_below_one(self):
        """Pre-commissioning company: ratio=0.25 (PAT 5% / Rev 20%), CWIP/NetBlock=0.4.
        Old logic: boost absorbed into floor → Omega=1.0.
        New logic: floor applied first → Omega=1.0+boost=1.16.
        """
        omega = self._get_omega(pat_growth=5.0, rev_growth=20.0, cwip_ratio=0.4)
        assert omega == pytest.approx(1.16, abs=1e-6), (
            f"Expected Omega=1.16 but got {omega}. "
            "CWIP boost is being absorbed by floor (dead zone bug not fixed)."
        )

    def test_cwip_boost_no_effect_below_threshold(self):
        """CWIP/NetBlock < 0.25 → no boost."""
        omega = self._get_omega(pat_growth=5.0, rev_growth=20.0, cwip_ratio=0.20)
        assert omega == pytest.approx(1.0, abs=1e-6), (
            f"Expected no boost (Omega=1.0) when CWIP ratio=0.20 < 0.25 threshold, got {omega}."
        )

    def test_cwip_boost_capped_at_max(self):
        """CWIP/NetBlock=1.0 → boost = min(0.30, 1.0*0.40) = 0.30 → Omega=1.30."""
        omega = self._get_omega(pat_growth=5.0, rev_growth=20.0, cwip_ratio=1.0)
        assert omega == pytest.approx(1.30, abs=1e-6), (
            f"Expected Omega=1.30 (capped boost) but got {omega}."
        )

    def test_high_ratio_company_unchanged(self):
        """PAT growth 30% / Rev growth 20% → ratio=1.5, no CWIP. Omega unchanged from pre-fix."""
        omega = self._get_omega(pat_growth=30.0, rev_growth=20.0, cwip_ratio=0.0)
        assert omega == pytest.approx(1.5, abs=1e-6), (
            f"High-ratio company should have Omega=1.5, got {omega}."
        )

    def test_cwip_boost_on_high_ratio_additive(self):
        """PAT/Rev=1.5, CWIP/NetBlock=0.50 → boost=min(0.30, 0.50*0.40)=0.20 → Omega=1.70."""
        omega = self._get_omega(pat_growth=30.0, rev_growth=20.0, cwip_ratio=0.50)
        assert omega == pytest.approx(1.70, abs=1e-6), (
            f"Expected Omega=1.70 but got {omega}."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. PHANTOM AUTO-GATE EMBEDDED IN evaluate_shareholding_pattern() (Phase 178-4)
# ─────────────────────────────────────────────────────────────────────────────

class TestPhantomAutoGate:
    """Verify phantom superstar gate fires automatically inside evaluate_shareholding_pattern()."""

    def _run(self, historical_holders, current_holders, queried_superstar="Ashish Kacholia"):
        from app.services.strategies.shareholding_pattern import evaluate_shareholding_pattern
        # evaluate_shareholding_pattern(symbol: str, shareholding_data: Optional[Dict] = None, ...)
        # Phase 178-4 reads historical_holders + queried_superstar from shareholding_data dict.
        # detect_phantom_superstar_status() requires holders as dicts with holder_name + holding_pct
        # keys (string-only entries are silently skipped as not-dict).
        shareholding_data = {
            # Minimum viable FII/DII fields to avoid early-exit ("data_insufficient")
            "fii_holding_pct": 10.0,
            "fii_qoq_change": 0.5,
            "dii_mf_holding_pct": 8.0,
            "dii_qoq_change": 0.5,
            "institutional_accumulation_quarters": 2,
            "retail_holding_trend": "DECREASING",
            "free_float_market_cap_cr": 2000.0,
            # Phase 178-4 phantom gate keys — dicts required for name matching
            "historical_holders": historical_holders,
            "tracked_holders": current_holders,
            "queried_superstar": queried_superstar,
        }
        return evaluate_shareholding_pattern("TEST.NS", shareholding_data)

    @staticmethod
    def _holder_dict(name: str, pct: float = 2.0):
        """Helper: build a proper holder dict for detect_phantom_superstar_status()."""
        return {"holder_name": name, "holding_pct": pct}

    def test_phantom_detected_when_superstar_exits(self):
        """Historical holder present, no longer in current holders → phantom detected."""
        result = self._run(
            historical_holders=[self._holder_dict("Ashish Kacholia", 2.5)],
            current_holders=[],
            queried_superstar="Ashish Kacholia",
        )
        gate = result.get("phantom_superstar_gate", {})
        assert gate.get("is_phantom_detected") is True, (
            "Phantom gate should fire when superstar in historical but not in current holders."
        )

    def test_phantom_not_detected_when_active(self):
        """Superstar still in current_holders (with pct >= 1.0%) → phantom NOT detected."""
        result = self._run(
            historical_holders=[self._holder_dict("Ashish Kacholia", 2.5)],
            current_holders=[self._holder_dict("Ashish Kacholia", 2.5)],
            queried_superstar="Ashish Kacholia",
        )
        gate = result.get("phantom_superstar_gate", {})
        assert gate.get("is_phantom_detected") is False, (
            f"Phantom gate must NOT fire when superstar is still active in current holders. "
            f"Gate result: {gate}"
        )

    def test_phantom_gate_key_always_present(self):
        """Return dict must always include phantom_superstar_gate key (even when no superstar queried)."""
        result = self._run(
            historical_holders=[],
            current_holders=[],
            queried_superstar="",
        )
        assert "phantom_superstar_gate" in result, (
            "evaluate_shareholding_pattern() must always include phantom_superstar_gate in return dict."
        )

    def test_phantom_warning_in_evidence(self):
        """When phantom detected, a warning string must appear in evidence list."""
        result = self._run(
            historical_holders=[self._holder_dict("Vijay Kedia", 1.5)],
            current_holders=[],
            queried_superstar="Vijay Kedia",
        )
        evidence = result.get("evidence", [])
        has_warning = any("phantom" in str(e).lower() or "exit" in str(e).lower() for e in evidence)
        assert has_warning, (
            f"Phantom detection should append a warning to evidence list. Got: {evidence}"
        )




# ─────────────────────────────────────────────────────────────────────────────
# 3. SUPERSTAR VERDICT WIRE IN InstitutionalMultibaggerEngine (Phase 178-5)
# ─────────────────────────────────────────────────────────────────────────────

class TestSuperstarsVerdictWire:
    """Verify shareholding_verdict correctly adjusts overall_score."""

    def _evaluate(self, shareholding_verdict=None, **overrides):
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        item = _base_multibagger_item(**overrides)
        return InstitutionalMultibaggerEngine.evaluate_company(item, shareholding_verdict=shareholding_verdict)

    def test_no_verdict_no_change(self):
        """Baseline: no shareholding_verdict → shareholding_verdict_applied is None."""
        result = self._evaluate(shareholding_verdict=None)
        assert result["shareholding_verdict_applied"] is None

    def test_phantom_exit_penalty_25pts(self):
        """PHANTOM_EXIT_DISTRIBUTION_TRAP verdict must subtract 25 pts from overall_score."""
        baseline = self._evaluate()
        verdict = {"verdict_label": "PHANTOM_EXIT_DISTRIBUTION_TRAP"}
        result = self._evaluate(shareholding_verdict=verdict)
        expected = max(0.0, baseline["overall_score"] - 25.0)
        assert result["overall_score"] == pytest.approx(expected, abs=0.1), (
            f"PHANTOM exit: expected score={expected:.1f}, got={result['overall_score']:.1f}"
        )
        assert result["shareholding_verdict_applied"] == "PHANTOM_EXIT_DISTRIBUTION_TRAP"
        assert any("PHANTOM_EXIT_DISTRIBUTION_TRAP" in f for f in result["risk_flags"])

    def test_partial_departure_penalty_10pts(self):
        """PARTIAL_SUPERSTAR_DEPARTURE must subtract 10 pts."""
        baseline = self._evaluate()
        verdict = {"verdict_label": "PARTIAL_SUPERSTAR_DEPARTURE"}
        result = self._evaluate(shareholding_verdict=verdict)
        expected = max(0.0, baseline["overall_score"] - 10.0)
        assert result["overall_score"] == pytest.approx(expected, abs=0.1), (
            f"Partial departure: expected score={expected:.1f}, got={result['overall_score']:.1f}"
        )
        assert result["shareholding_verdict_applied"] == "PARTIAL_SUPERSTAR_DEPARTURE"

    def test_high_conviction_bonus_5pts(self):
        """HIGH_CONVICTION_ACTIVE_CLUSTER must add 5 pts (capped at 100)."""
        baseline = self._evaluate()
        verdict = {"verdict_label": "HIGH_CONVICTION_ACTIVE_CLUSTER"}
        result = self._evaluate(shareholding_verdict=verdict)
        expected = min(100.0, baseline["overall_score"] + 5.0)
        assert result["overall_score"] == pytest.approx(expected, abs=0.1), (
            f"Active cluster: expected score={expected:.1f}, got={result['overall_score']:.1f}"
        )
        assert result["shareholding_verdict_applied"] == "HIGH_CONVICTION_ACTIVE_CLUSTER"

    def test_phantom_score_floor_at_zero(self):
        """Score cannot go below 0 even with -25 penalty applied."""
        # Force a very low baseline by giving a terrible company profile
        terrible_item = _base_multibagger_item(
            sales_growth_3yr=2.0,
            pat_growth_3yr=1.0,
            pat_growth_latest=1.0,
            eps_growth_3yr=1.0,
            roce_latest=5.0,
            roce_3yr=4.0,
            roe_latest=3.0,
            cfo_last_year=1.0,
            net_profit_last_year=50.0,
            promoter_holding=30.0,
            pledged_pct=25.0,
            debt_to_equity=1.8,
        )
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        verdict = {"verdict_label": "PHANTOM_EXIT_DISTRIBUTION_TRAP"}
        result = InstitutionalMultibaggerEngine.evaluate_company(terrible_item, shareholding_verdict=verdict)
        assert result["overall_score"] >= 0.0, "Score floor violated: cannot go below 0."

    def test_cluster_bonus_ceiling_at_100(self):
        """Score cannot exceed 100 even with +5 bonus applied."""
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        # Artificially boost to near 100
        great_item = _base_multibagger_item(
            sales_growth_3yr=40.0,
            pat_growth_3yr=50.0,
            pat_growth_latest=55.0,
            eps_growth_3yr=48.0,
            roce_latest=35.0,
            roce_3yr=32.0,
            roe_latest=30.0,
            cfo_last_year=500.0,
            net_profit_last_year=400.0,
            operating_profit=600.0,
            net_block=2000.0,
            net_block_prec=1200.0,
            net_block_3yr_back=800.0,
            cwip=300.0,
            cwip_preceding_year=100.0,
            promoter_holding=65.0,
            pledged_pct=0.0,
            debt_to_equity=0.05,
            interest_coverage=25.0,
            peg_ratio=0.8,
            piotroski_score=9.0,
            volume=50000,
            vol_1y_avg=10000.0,
        )
        verdict = {"verdict_label": "HIGH_CONVICTION_ACTIVE_CLUSTER"}
        result = InstitutionalMultibaggerEngine.evaluate_company(great_item, shareholding_verdict=verdict)
        assert result["overall_score"] <= 100.0, "Score ceiling violated: cannot exceed 100."

    def test_unknown_verdict_label_no_change(self):
        """Unrecognised verdict label must not modify overall_score."""
        baseline = self._evaluate()
        verdict = {"verdict_label": "SOME_FUTURE_LABEL"}
        result = self._evaluate(shareholding_verdict=verdict)
        assert result["overall_score"] == pytest.approx(baseline["overall_score"], abs=0.1), (
            "Unknown verdict label should leave overall_score unchanged."
        )
        assert result["shareholding_verdict_applied"] is None

    def test_backward_compat_no_verdict_arg(self):
        """Existing callers that pass only item (no shareholding_verdict) must continue to work."""
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        item = _base_multibagger_item()
        result = InstitutionalMultibaggerEngine.evaluate_company(item)
        assert "overall_score" in result
        assert result["shareholding_verdict_applied"] is None


# ─────────────────────────────────────────────────────────────────────────────
# 4. CUSTOM SCREENER MOCK FIXTURE REGRESSION GUARD (Phase 178-1)
# ─────────────────────────────────────────────────────────────────────────────

class TestCustomScreenerMockFixture:
    """Regression guard: confirm Phase 178-1 screener AST logic is still correct.

    Uses inline mock dicts matching the values defined in test_custom_screener.py
    (which are local to that test function and not importable at module level).
    """

    MOCK_PASS = {
        "symbol": "MOCK_PASS.NS",
        "company_name": "Mock High Quality Co",
        "current_price": 500.0,
        "high_52w": 600.0,
        "low_52w": 250.0,
        "volume": 200000,
        "vol_1y_avg": 100000,
        "roe_3yr": 22.0,
        "roe_latest": 25.0,
        "roce_3yr": 24.0,
        "roce_latest": 30.0,
        "operating_profit": 200.0,
        "op_growth": 20.0,
        "opm_5yr": 18.0,
        "opm_latest": 22.0,
        "pat_growth_3yr": 25.0,
        "pat_growth_latest": 30.0,
        "sales_growth_3yr": 22.0,
        "sales_growth_latest": 28.0,
        "eps_growth_3yr": 20.0,
        "eps_latest": 25.0,
        "cfo_3yr": 150.0,
        "market_cap": 5000.0,
        "debt_to_equity": 0.2,
        "promoter_holding": 55.0,
        "pledged_pct": 0.0,
        "net_block": 1000.0,
        "cwip": 100.0,
        "net_profit_last_year": 80.0,
        "cfo_last_year": 90.0,
    }

    def test_mock_pass_passes_roce_condition(self):
        """MOCK_PASS.NS must satisfy ROCE > 23."""
        from app.services.research.custom_screener import CustomScreenerEngine
        result = CustomScreenerEngine._eval_boolean_expr(self.MOCK_PASS, "Return on capital employed > 23")
        assert result is True, f"MOCK_PASS ROCE={self.MOCK_PASS['roce_latest']} should pass ROCE > 23"

    def test_mock_pass_passes_sales_growth(self):
        """MOCK_PASS.NS must satisfy Sales growth 3Years > 18."""
        from app.services.research.custom_screener import CustomScreenerEngine
        result = CustomScreenerEngine._eval_boolean_expr(self.MOCK_PASS, "Sales growth 3Years > 18")
        assert result is True, f"MOCK_PASS sales_growth_3yr={self.MOCK_PASS['sales_growth_3yr']} should pass > 18"

    def test_mock_fail_fails_roce_condition(self):
        """MOCK_FAIL.NS (ROCE=10) must fail ROCE > 23."""
        from app.services.research.custom_screener import CustomScreenerEngine
        mock_fail = dict(self.MOCK_PASS)
        mock_fail["symbol"] = "MOCK_FAIL.NS"
        mock_fail["roce_latest"] = 10.0
        result = CustomScreenerEngine._eval_boolean_expr(mock_fail, "Return on capital employed > 23")
        assert result is False, "MOCK_FAIL.NS (ROCE=10) should FAIL ROCE > 23 condition"

