"""Phase 170: Kelly Sizing Edge Protection, Altman Z'' EM Model, and Unified Pledge Hierarchy Tests.

Validates:
  1. Fractional-Kelly fails closed to 0.0% when expected edge is non-positive (fixes the 1% floor bug).
  2. Fractional-Kelly allocates quarter-Kelly when expected edge is positive.
  3. Altman Z'' Emerging Market (1993/2002) formula: 3.25 + 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4.
  4. Altman Z'' zone categorization: Safe (>5.85), Grey (4.15-5.85), Distress (<4.15).
  5. Altman Z'' financial sector / banking exemption returns NOT_APPLICABLE.
  6. Altman Z backward compatibility: compute_altman_zscore still returns z_score, z_prime_score, and z_double_prime_score.
  7. Unified 5-tier promoter pledge hierarchy constants in app.core.constants.
"""

import os
import pytest
from types import SimpleNamespace

os.environ["OFFLINE_TEST_MODE"] = "true"
os.environ["PYTEST_CURRENT_TEST"] = "true"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Kelly Sizing Negative-Edge Fail-Closed Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestKellySizingNegativeEdgeFailClosed:

    def test_negative_edge_fails_closed_to_zero(self):
        """When win_prob is low (e.g. mivs_score=20, conf=20 -> win_prob=0.20),
        full_kelly = (0.20 * 3.0 - 0.80) / 3.0 = -0.20 / 3.0 < 0.
        Fractional-Kelly MUST fail closed to 0.0% (not 1.0%).
        """
        from app.services.research.portfolio_construction import evaluate_portfolio_construction

        data = {
            "fund_aum_cr": 500.0,
            "adtv_cr": 25.0,
            "archetype": "GENERAL",
            "market_cap": 2500.0,
            "stop_loss_pct": 6.5,
        }
        res = evaluate_portfolio_construction(
            "TEST_NEG_EDGE",
            mivs_score=20.0,
            evidence_confidence_pct=20.0,
            portfolio_inputs=data,
        )
        signal = res["portfolio_signal"]

        # Crucial check: fractional_kelly_weight must be 0.0, NOT 0.01
        assert signal["fractional_kelly_weight"] == 0.0, (
            f"Expected 0.0 fractional Kelly for negative edge, got {signal['fractional_kelly_weight']}"
        )
        assert any("Negative/Zero Expected Edge" in ev for ev in res["evidence"])

    def test_positive_edge_allocates_quarter_kelly(self):
        """When win_prob is high (e.g. mivs_score=80, conf=80 -> win_prob=0.64),
        payoff=3.0, full_kelly = (0.64 * 3.0 - 0.36) / 3.0 = 1.56 / 3.0 = 0.52.
        quarter_kelly = 0.52 * 0.25 = 0.13 (13.0%).
        Must allocate positive percentage.
        """
        from app.services.research.portfolio_construction import evaluate_portfolio_construction

        data = {
            "fund_aum_cr": 500.0,
            "adtv_cr": 25.0,
            "archetype": "GENERAL",
            "market_cap": 2500.0,
            "stop_loss_pct": 6.5,
        }
        res = evaluate_portfolio_construction(
            "TEST_POS_EDGE",
            mivs_score=80.0,
            evidence_confidence_pct=80.0,
            portfolio_inputs=data,
        )
        signal = res["portfolio_signal"]

        assert signal["fractional_kelly_weight"] > 0.05, (
            f"Expected positive fractional Kelly, got {signal['fractional_kelly_weight']}"
        )
        assert any("Fractional-Kelly (Quarter-Kelly)" in ev for ev in res["evidence"])


# ─────────────────────────────────────────────────────────────────────────────
# 2. Altman Z'' Emerging Market (1993/2002) Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestAltmanZDoublePrimeEM:

    def _obs(self, metric: str, period: str, value: float):
        return SimpleNamespace(metric=metric, period_end=period, value=value)

    def _make_sample_financials(self, wc=150.0, re=200.0, ebit=100.0, equity=400.0, debt=200.0, assets=1000.0, rev=1200.0):
        p = "2024-03-31"
        return [
            self._obs("working_capital", p, wc),
            self._obs("retained_earnings", p, re),
            self._obs("operating_income", p, ebit),
            self._obs("total_assets", p, assets),
            self._obs("total_equity", p, equity),
            self._obs("total_debt", p, debt),
            self._obs("revenue", p, rev),
        ]

    def test_altman_z_double_prime_exact_formula(self):
        """Test Z'' = 3.25 + 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4.
        Assets = 1000.
        X1 = 150 / 1000 = 0.15
        X2 = 200 / 1000 = 0.20
        X3 = 100 / 1000 = 0.10
        X4 = 400 / 200 = 2.00
        Expected Z'' = 3.25 + 6.56*(0.15) + 3.26*(0.20) + 6.72*(0.10) + 1.05*(2.0)
                     = 3.25 + 0.984 + 0.652 + 0.672 + 2.10 = 7.658.
        """
        from app.services.strategies.forensic_engine import compute_altman_zscore, compute_altman_zscore_em

        financials = self._make_sample_financials()
        res_em = compute_altman_zscore_em(financials, sector="HEALTHCARE")

        assert res_em["status"] == "success"
        z_dp = res_em["z_double_prime_score"]
        expected = round(3.25 + 6.56*0.15 + 3.26*0.20 + 6.72*0.10 + 1.05*2.0, 3)
        assert abs(z_dp - expected) < 0.05, f"Expected {expected}, got {z_dp}"
        assert res_em["zone"] == "SAFE"

    def test_altman_z_double_prime_distress_zone(self):
        """Negative working capital, negative retained earnings, low EBIT -> DISTRESS (< 4.15)."""
        from app.services.strategies.forensic_engine import compute_altman_zscore_em

        # WC = -100, RE = -150, EBIT = 10, Equity = 50, Debt = 500, Assets = 1000
        # X1 = -0.10, X2 = -0.15, X3 = 0.01, X4 = 0.10
        # Z'' = 3.25 + 6.56*(-0.10) + 3.26*(-0.15) + 6.72*(0.01) + 1.05*(0.10)
        #     = 3.25 - 0.656 - 0.489 + 0.067 + 0.105 = 2.277 (< 4.15)
        financials = self._make_sample_financials(wc=-100.0, re=-150.0, ebit=10.0, equity=50.0, debt=500.0)
        res_em = compute_altman_zscore_em(financials, sector="SERVICES")

        assert res_em["status"] == "success"
        assert res_em["z_double_prime_score"] < 4.15
        assert res_em["zone"] == "DISTRESS"

    def test_altman_z_em_financial_sector_not_applicable(self):
        """Financial institutions, banks, NBFCs must return NOT_APPLICABLE."""
        from app.services.strategies.forensic_engine import compute_altman_zscore_em

        financials = self._make_sample_financials()
        for sec in ["BANKING", "Banks", "Financial Services", "NBFC", "Insurance"]:
            res = compute_altman_zscore_em(financials, sector=sec)
            assert res["status"] == "not_applicable", f"Expected not_applicable for sector {sec}"
            assert "Altman distress models do not apply" in res["reason"]

    def test_altman_z_backward_compatibility(self):
        """compute_altman_zscore must continue returning original fields plus z_double_prime_score."""
        from app.services.strategies.forensic_engine import compute_altman_zscore

        financials = self._make_sample_financials()
        res = compute_altman_zscore(financials)

        assert "z_score" in res, "Original 1968 z_score must be present"
        assert "z_prime_score" in res, "1983 z_prime_score must be present"
        assert "z_double_prime_score" in res, "New Phase 170 z_double_prime_score must be present"
        assert "z_double_prime_zone" in res, "New Phase 170 z_double_prime_zone must be present"
        assert res["zone"] in ("SAFE", "GREY", "DISTRESS")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Unified Promoter Pledge Hierarchy Constants Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestPledgeHierarchyConstants:

    def test_pledge_constants_strictly_ordered(self):
        """The unified 5-tier pledge constants must be strictly monotonically increasing."""
        from app.core.constants import (
            PLEDGE_PRISTINE_MAX,
            PLEDGE_QUALITY_PASS_MAX,
            PLEDGE_WARNING_MIN,
            PLEDGE_DISQUALIFY_MIN,
            PLEDGE_VETO_THRESHOLD,
        )

        assert PLEDGE_PRISTINE_MAX == 2.0
        assert PLEDGE_QUALITY_PASS_MAX == 5.0
        assert PLEDGE_WARNING_MIN == 10.0
        assert PLEDGE_DISQUALIFY_MIN == 25.0
        assert PLEDGE_VETO_THRESHOLD == 40.0

        assert PLEDGE_PRISTINE_MAX < PLEDGE_QUALITY_PASS_MAX < PLEDGE_WARNING_MIN < PLEDGE_DISQUALIFY_MIN < PLEDGE_VETO_THRESHOLD
