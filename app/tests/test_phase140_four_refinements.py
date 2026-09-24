"""Phase 140 Unit Tests — Four Mathematical & Linkage Refinements:
1. Multi-Horizon Forward CAGR Share Dilution Velocity (CADR) Haircut
2. Standalone MAP-Rank Fundamentals Auto-Resolution
3. DEME-HR Observed P/E Precedence over Reconstructed PEG Proxy
4. Intent-Adaptive CAQI & DEME-HR Gate Integration
"""

import os
import pytest

os.environ.setdefault("OFFLINE_TEST_MODE", "true")


# ── 1. Multi-Horizon CAGR Share Dilution Velocity Tests ───────────────────────

class TestMultiHorizonCAGRWithCADR:
    """Verify that multi-horizon CAGR projections account for equity expansion velocity."""

    def test_cadr_haircut_deflates_forward_cagr(self):
        """When share count expands at 10% p.a., 25% growth should deflate to ~13.6%."""
        from app.services.research.multi_horizon_matrix_engine import MultiHorizonMatrixEngine

        # Setup company with 25% EPS growth, but 33.1% 3Y share expansion (10% CAGR)
        test_data = {
            "symbol": "DILUTE_CORP",
            "company_name": "Dilution Corp Ltd",
            "current_price": 100.0,
            "market_cap": 1000.0,
            "eps_growth_3yr": 25.0,
            "cfo_3yr": 300.0,
            "net_profit_last_year": 100.0,
            "debt_to_equity": 0.2,
            "pe_ratio": 20.0,
            "median_pe": 20.0,  # 1.0x multiple ratio to isolate growth component
            "shares_count": 133.1,
            "shares_count_10yr_back": 100.0,  # 3Y lookback proxy: 133.1 / 100 -> CADR = 10%
            "dilution_instrument_hint": "preferential warrants to promoters",
        }

        item = MultiHorizonMatrixEngine.calculate_single_symbol_matrix("DILUTE_CORP", override_data=test_data)

        # Expected: (1 + 0.25) / (1 + 0.10) - 1 = 13.64% per share growth
        # 1-Year CAGR should be close to 13.6%, NOT 25%
        assert item.cagr_1y_pct is not None
        assert item.cagr_1y_pct < 18.0, f"Expected deflated CAGR < 18%, got {item.cagr_1y_pct}%"
        assert item.cagr_1y_pct == pytest.approx(13.6, abs=2.0)

    def test_zero_or_low_cadr_preserves_growth(self):
        """When share count is stable (CADR < 2%), growth rate is not deflated."""
        from app.services.research.multi_horizon_matrix_engine import MultiHorizonMatrixEngine

        test_data = {
            "symbol": "STABLE_CORP",
            "company_name": "Stable Corp Ltd",
            "current_price": 100.0,
            "market_cap": 1000.0,
            "eps_growth_3yr": 25.0,
            "cfo_3yr": 300.0,
            "net_profit_last_year": 100.0,
            "debt_to_equity": 0.2,
            "pe_ratio": 20.0,
            "median_pe": 20.0,
            "shares_count": 101.0,
            "shares_count_10yr_back": 100.0,  # CADR ~ 0.33% < 2% threshold
        }

        item = MultiHorizonMatrixEngine.calculate_single_symbol_matrix("STABLE_CORP", override_data=test_data)
        assert item.cagr_1y_pct is not None
        assert item.cagr_1y_pct >= 20.0, f"Expected robust CAGR >= 20%, got {item.cagr_1y_pct}%"


# ── 2. Standalone MAP-Rank Fundamentals Auto-Resolution Tests ────────────────

class TestMAPRankAutoResolution:
    """Verify that standalone rank_candidates without pre-fetched fundamentals auto-resolves data."""

    def test_standalone_rank_populates_real_fundamentals(self):
        from app.services.research.map_rank_engine import rank_candidates

        # Pass symbols without fundamentals_lookup
        results = rank_candidates(["RELIANCE", "TCS"], fundamentals_lookup=None)

        assert len(results) == 2
        for entry in results:
            # Solvency, cash quality, or headroom must be populated, not empty stubs
            assert entry["composite_score"] > 0.0
            assert entry["solvency_score"] > 0.0
            assert entry["pareto_rank"] in (1, 2)


# ── 3. DEME-HR Observed P/E Precedence Tests ─────────────────────────────────

class TestDEMEHRPrecedence:
    """Verify that explicit pe_ratio takes precedence over PEG * growth reconstruction."""

    def test_observed_pe_prevents_false_valuation_constrained(self):
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine

        # High growth (40%) + PEG 1.5 would synthesize P/E = 60.0x (> CAPITAL_GOODS ceiling of 55x)
        # But true observed pe_ratio is 25.0x (< 55x -> DEME-HR = 2.2x -> UNDERVALUED)
        fund = {
            "symbol": "GROWTH_CO",
            "company_name": "Growth Co Ltd",
            "market_cap": 5000.0,
            "current_price": 100.0,
            "pe_ratio": 25.0,  # Explicit observed P/E
            "peg_ratio": 1.5,   # Would reconstruct 60.0x if precedence inverted
            "sales_growth_3yr": 40.0,
            "sector": "CAPITAL_GOODS",
            "cfo_last_year": 120.0,
            "net_profit_last_year": 100.0,
            "pledged_pct": 0.0,
            "debt_to_equity": 0.2,
            "piotroski_score": 8.0,
        }

        res = InstitutionalMultibaggerEngine.evaluate_company(fund)

        assert res["deme_hr"] == pytest.approx(2.2, abs=0.1)
        assert res["deme_hr_verdict"] == "UNDERVALUED"
        assert not any("VALUATION_CONSTRAINED" in f for f in res["risk_flags"])


# ── 4. Intent-Adaptive CAQI & DEME-HR Gate Tests ─────────────────────────────

class TestIntentAdaptiveGates:
    """Verify that CAQI and DEME-HR trigger appropriate adaptive gates."""

    def test_sip_compounder_blocks_on_caqi_fail(self):
        from app.services.research.intent_adaptive_engine import QueryAdaptiveConstraintEngine

        data = {
            "roce": 25.0,
            "cfo_pat_ratio": 0.85,
            "debt_to_equity": 0.2,
            "promoter_pledge_pct": 0.0,
            "caqi": 0.65,
            "caqi_gate": "FAIL",  # Cash Accrual Quality Index failed
        }

        res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("SIP_COMPOUNDER", data)

        assert res["passed"] is False
        assert any("CAQI" in block for block in res["objective_blocks"])

    def test_multibagger_flags_deme_hr_constrained(self):
        from app.services.research.intent_adaptive_engine import QueryAdaptiveConstraintEngine

        data = {
            "market_cap": 300.0,
            "implied_tam_share": 15.0,
            "deme_hr": 0.82,
            "deme_hr_verdict": "VALUATION_CONSTRAINED",
        }

        res = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("MULTIBAGGER", data)

        assert any("DEME-HR" in warn for warn in res["warnings"])
        assert any("DEME-HR" in t for t in res["tightened_parameters"])
