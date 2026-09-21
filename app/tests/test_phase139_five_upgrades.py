"""Phase 139 Tests — MAP-Rank, CAQI Gate, DEME-HR, β_geo Shock Matrix, Multimodal Watchlist Bridge."""

import os
import pytest

os.environ.setdefault("OFFLINE_TEST_MODE", "true")


# ─────────────────────────────────────────────────────────────────────────────
# 1. CAQI Gate tests (institutional_multibagger_engine.evaluate_company)
# ─────────────────────────────────────────────────────────────────────────────

def _make_fund(**overrides):
    """Minimal fund dict that passes hard risk gate for CAQI/DEME-HR testing."""
    base = {
        "symbol": "TEST",
        "company_name": "Test Co",
        "market_cap": 5000.0,
        "current_price": 100.0,
        "high_52w": 150.0,
        "low_52w": 80.0,
        "volume": 100000,
        "vol_1w_avg": 80000.0,
        "vol_1y_avg": 70000.0,
        "roe_3yr": 15.0,
        "roe_latest": 18.0,
        "roce_3yr": 18.0,
        "roce_latest": 22.0,
        "opm_5yr": 10.0,
        "opm_latest": 14.0,
        "operating_profit": 80.0,
        "op_growth": 20.0,
        "pat_growth_3yr": 22.0,
        "pat_growth_latest": 25.0,
        "sales_growth_3yr": 18.0,
        "sales_growth_latest": 22.0,
        "eps_growth_3yr": 22.0,
        "eps_latest": 12.0,
        "cfo_3yr": 240.0,
        "cfo_last_year": 90.0,
        "net_profit_last_year": 80.0,
        "net_block": 500.0,
        "net_block_3yr_back": 300.0,
        "net_block_preceding_year": 420.0,
        "cwip": 50.0,
        "cwip_preceding_year": 30.0,
        "piotroski_score": 7.5,
        "promoter_holding": 55.0,
        "pledged_pct": 0.0,
        "debt_to_equity": 0.4,
        "interest_coverage": 8.0,
        "peg_ratio": 1.1,
        "sector": "CAPITAL_GOODS",
    }
    base.update(overrides)
    return base


class TestCAQIGate:
    """CAQI = CFO_TTM / PAT_TTM; threshold = 0.80."""

    def test_caqi_pass_when_cfo_exceeds_pat(self):
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        fund = _make_fund(cfo_last_year=100.0, net_profit_last_year=80.0)
        result = InstitutionalMultibaggerEngine.evaluate_company(fund)
        assert result["caqi_gate"] == "PASS"
        assert result["caqi"] == pytest.approx(1.25, abs=0.01)

    def test_caqi_pass_exactly_at_threshold(self):
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        fund = _make_fund(cfo_last_year=80.0, net_profit_last_year=100.0)
        result = InstitutionalMultibaggerEngine.evaluate_company(fund)
        assert result["caqi_gate"] == "PASS"
        assert result["caqi"] == pytest.approx(0.80, abs=0.01)

    def test_caqi_fail_when_cfo_below_threshold(self):
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        fund = _make_fund(cfo_last_year=50.0, net_profit_last_year=100.0)
        result = InstitutionalMultibaggerEngine.evaluate_company(fund)
        assert result["caqi_gate"] == "FAIL"
        assert result["caqi"] == pytest.approx(0.50, abs=0.01)
        assert any("CAQI" in f for f in result["risk_flags"])

    def test_caqi_data_unavailable_when_pat_zero(self):
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        fund = _make_fund(cfo_last_year=50.0, net_profit_last_year=0.0)
        result = InstitutionalMultibaggerEngine.evaluate_company(fund)
        assert result["caqi_gate"] == "DATA_UNAVAILABLE"
        assert result["caqi"] is None

    def test_caqi_in_return_dict(self):
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        fund = _make_fund()
        result = InstitutionalMultibaggerEngine.evaluate_company(fund)
        assert "caqi" in result
        assert "caqi_gate" in result


# ─────────────────────────────────────────────────────────────────────────────
# 2. DEME-HR tests
# ─────────────────────────────────────────────────────────────────────────────

class TestDEMEHR:
    """DEME-HR = Sector P/E Ceiling / Trailing P/E. ≤ 1.0 → VALUATION_CONSTRAINED."""

    def test_deme_hr_undervalued_when_pe_far_below_ceiling(self):
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        # CAPITAL_GOODS ceiling = 55x; pe_ratio = 10x → DEME-HR = 5.5 → UNDERVALUED
        fund = _make_fund(pe_ratio=10.0, peg_ratio=None, sector="CAPITAL_GOODS")
        result = InstitutionalMultibaggerEngine.evaluate_company(fund)
        assert result["deme_hr_verdict"] == "UNDERVALUED"
        assert result["deme_hr"] == pytest.approx(5.5, abs=0.1)

    def test_deme_hr_valuation_constrained_above_ceiling(self):
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        # CAPITAL_GOODS ceiling = 55x; pe_ratio = 260x → DEME-HR = 0.21 → VALUATION_CONSTRAINED
        fund = _make_fund(pe_ratio=260.0, peg_ratio=None, sector="CAPITAL_GOODS")
        result = InstitutionalMultibaggerEngine.evaluate_company(fund)
        assert result["deme_hr_verdict"] == "VALUATION_CONSTRAINED"
        assert result["deme_hr"] is not None and result["deme_hr"] < 1.0
        assert any("DEME-HR" in f for f in result["risk_flags"])

    def test_deme_hr_data_unavailable_no_pe(self):
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        fund = _make_fund(pe_ratio=None, peg_ratio=None, sector="CAPITAL_GOODS")
        result = InstitutionalMultibaggerEngine.evaluate_company(fund)
        assert result["deme_hr_verdict"] == "DATA_UNAVAILABLE"
        assert result["deme_hr"] is None

    def test_deme_hr_in_return_dict(self):
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        fund = _make_fund()
        result = InstitutionalMultibaggerEngine.evaluate_company(fund)
        assert "deme_hr" in result
        assert "deme_hr_verdict" in result


# ─────────────────────────────────────────────────────────────────────────────
# 3. β_geo Shock Matrix tests
# ─────────────────────────────────────────────────────────────────────────────

class TestGeoShockSensitivity:
    """compute_geo_shock_sensitivity returns correct 5-vector betas."""

    def test_transformer_has_high_grid_beta(self):
        from app.services.research.geopolitical_engine import compute_geo_shock_sensitivity
        result = compute_geo_shock_sensitivity("SHILCHAR", sector="TRANSFORMERS")
        assert result["beta_grid_hardware_deficit"] >= 0.70
        assert result["dominant_shock"] == "GRID_HARDWARE_DEFICIT"
        # Aggregate = (+0.85 - 0.05 - 0.05 - 0.15 - 0.05) / 5 = 0.11 → GEO_NEUTRAL (≥ -0.05, < 0.15)
        assert result["verdict"] in ("GEO_TAILWIND", "GEO_NEUTRAL")

    def test_shipping_has_critical_maritime_beta(self):
        from app.services.research.geopolitical_engine import compute_geo_shock_sensitivity
        result = compute_geo_shock_sensitivity("GESHIP", sector="SHIPPING")
        assert result["beta_maritime_chokepoint"] <= -0.80
        assert result["verdict"] in ("GEO_HEADWIND", "GEO_CRITICAL")

    def test_defense_has_positive_grid_and_maritime_betas(self):
        from app.services.research.geopolitical_engine import compute_geo_shock_sensitivity
        result = compute_geo_shock_sensitivity("HBLPOWER", sector="DEFENSE")
        assert result["beta_grid_hardware_deficit"] > 0.0
        assert result["beta_maritime_chokepoint"] >= 0.0

    def test_it_has_negative_us_rate_beta(self):
        from app.services.research.geopolitical_engine import compute_geo_shock_sensitivity
        result = compute_geo_shock_sensitivity("TCS", sector="IT")
        assert result["beta_us_rate_hike"] <= -0.35

    def test_all_5_betas_present(self):
        from app.services.research.geopolitical_engine import compute_geo_shock_sensitivity
        result = compute_geo_shock_sensitivity("RELIANCE", sector="OIL_GAS")
        for key in [
            "beta_crude_spike", "beta_maritime_chokepoint", "beta_china_dumping",
            "beta_grid_hardware_deficit", "beta_us_rate_hike"
        ]:
            assert key in result, f"Missing key: {key}"

    def test_aggregate_beta_is_average_of_five(self):
        from app.services.research.geopolitical_engine import compute_geo_shock_sensitivity
        result = compute_geo_shock_sensitivity("RELIANCE", sector="OIL_GAS")
        expected = round((
            result["beta_crude_spike"]
            + result["beta_maritime_chokepoint"]
            + result["beta_china_dumping"]
            + result["beta_grid_hardware_deficit"]
            + result["beta_us_rate_hike"]
        ) / 5.0, 4)
        assert result["aggregate_geo_beta"] == pytest.approx(expected, abs=1e-4)

    def test_unknown_sector_falls_back_to_default(self):
        from app.services.research.geopolitical_engine import compute_geo_shock_sensitivity
        result = compute_geo_shock_sensitivity("XYZ", sector="UNKNOWN_SECTOR_XYZ")
        assert result["aggregate_geo_beta"] is not None
        assert result["verdict"] in ("GEO_TAILWIND", "GEO_NEUTRAL", "GEO_HEADWIND", "GEO_CRITICAL")

    def test_dominant_shock_matches_max_abs_beta(self):
        from app.services.research.geopolitical_engine import compute_geo_shock_sensitivity
        result = compute_geo_shock_sensitivity("SHILCHAR", sector="TRANSFORMERS")
        betas = {
            "CRUDE_SPIKE_30PCT": abs(result["beta_crude_spike"]),
            "MARITIME_CHOKEPOINT": abs(result["beta_maritime_chokepoint"]),
            "CHINA_DUMPING": abs(result["beta_china_dumping"]),
            "GRID_HARDWARE_DEFICIT": abs(result["beta_grid_hardware_deficit"]),
            "US_RATE_HIKE_100BPS": abs(result["beta_us_rate_hike"]),
        }
        expected_dominant = max(betas, key=betas.get)
        assert result["dominant_shock"] == expected_dominant


# ─────────────────────────────────────────────────────────────────────────────
# 4. MAP-Rank tests
# ─────────────────────────────────────────────────────────────────────────────

class TestMAPRank:
    """MAP-Rank cross-sectional Pareto tournament."""

    def _make_funds(self):
        """Minimal fund stubs for 3 symbols with known differentiation."""
        return {
            "TCS": {
                "symbol": "TCS", "sector": "IT",
                "debt_to_equity": 0.0, "interest_coverage": 50.0,
                "cfo_last_year": 45000.0, "net_profit_last_year": 40000.0,
                "pe_ratio": 28.0, "peg_ratio": None, "sales_growth_3yr": 12.0,
            },
            "HBLPOWER": {
                "symbol": "HBLPOWER", "sector": "DEFENSE",
                "debt_to_equity": 0.2, "interest_coverage": 12.0,
                "cfo_last_year": 300.0, "net_profit_last_year": 200.0,
                "pe_ratio": 30.0, "peg_ratio": None, "sales_growth_3yr": 25.0,
            },
            "GESHIP": {
                "symbol": "GESHIP", "sector": "SHIPPING",
                "debt_to_equity": 1.5, "interest_coverage": 2.5,
                "cfo_last_year": 80.0, "net_profit_last_year": 150.0,
                "pe_ratio": 15.0, "peg_ratio": None, "sales_growth_3yr": 8.0,
            },
        }

    def test_rank_returns_correct_count(self):
        from app.services.research.map_rank_engine import rank_candidates
        funds = self._make_funds()
        result = rank_candidates(["TCS", "HBLPOWER", "GESHIP"], fundamentals_lookup=funds)
        assert len(result) == 3

    def test_rank_1_has_highest_composite_score(self):
        from app.services.research.map_rank_engine import rank_candidates
        funds = self._make_funds()
        result = rank_candidates(["TCS", "HBLPOWER", "GESHIP"], fundamentals_lookup=funds)
        assert result[0]["pareto_rank"] == 1
        for i in range(1, len(result)):
            assert result[i - 1]["composite_score"] >= result[i]["composite_score"]

    def test_pareto_ranks_are_sequential(self):
        from app.services.research.map_rank_engine import rank_candidates
        funds = self._make_funds()
        result = rank_candidates(["TCS", "HBLPOWER", "GESHIP"], fundamentals_lookup=funds)
        ranks = [r["pareto_rank"] for r in result]
        assert ranks == list(range(1, len(result) + 1))

    def test_top_n_truncates_result(self):
        from app.services.research.map_rank_engine import rank_candidates
        funds = self._make_funds()
        result = rank_candidates(["TCS", "HBLPOWER", "GESHIP"], fundamentals_lookup=funds, top_n=2)
        assert len(result) == 2

    def test_caqi_fail_generates_risk_flag(self):
        from app.services.research.map_rank_engine import rank_candidates
        # GESHIP: CFO 80 / PAT 150 = 0.53x → CAQI FAIL
        funds = self._make_funds()
        result = rank_candidates(["GESHIP"], fundamentals_lookup=funds)
        geship_entry = result[0]
        assert geship_entry["caqi_gate"] == "FAIL"
        assert any("CAQI" in f for f in geship_entry["risk_flags"])

    def test_high_pe_generates_valuation_constrained(self):
        from app.services.research.map_rank_engine import rank_candidates
        # pe_ratio=500 vs DEFENSE ceiling=90x → DEME-HR = 0.18 → VALUATION_CONSTRAINED
        funds = {
            "HBLPOWER": {
                "symbol": "HBLPOWER", "sector": "DEFENSE",
                "debt_to_equity": 0.1, "interest_coverage": 20.0,
                "cfo_last_year": 200.0, "net_profit_last_year": 150.0,
                "pe_ratio": 500.0, "peg_ratio": None, "sales_growth_3yr": 30.0,
            }
        }
        result = rank_candidates(["HBLPOWER"], fundamentals_lookup=funds)
        assert result[0]["deme_hr_verdict"] == "VALUATION_CONSTRAINED"

    def test_intent_weights_affect_scores(self):
        """Different intents should produce different composite scores."""
        from app.services.research.map_rank_engine import rank_candidates
        funds = self._make_funds()
        result_mb = rank_candidates(["TCS", "HBLPOWER", "GESHIP"], fundamentals_lookup=funds, intent="MULTIBAGGER")
        result_swing = rank_candidates(["TCS", "HBLPOWER", "GESHIP"], fundamentals_lookup=funds, intent="SWING_3D")
        # Scores must be non-identical due to different weight profiles
        mb_scores = {r["symbol"]: r["composite_score"] for r in result_mb}
        sw_scores = {r["symbol"]: r["composite_score"] for r in result_swing}
        assert mb_scores != sw_scores

    def test_build_map_rank_response_has_correct_keys(self):
        from app.services.research.map_rank_engine import build_map_rank_response
        funds = self._make_funds()
        result = build_map_rank_response(["TCS", "HBLPOWER"], fundamentals_lookup=funds, intent="MULTIBAGGER")
        assert result["status"] == "OK"
        assert "ranked" in result
        assert "methodology" in result
        assert "executed_at" in result
        assert result["total_candidates"] == 2


# ─────────────────────────────────────────────────────────────────────────────
# 5. Multimodal Watchlist Bridge tests
# ─────────────────────────────────────────────────────────────────────────────

class TestMultimodalWatchlistBridge:
    """audit_watchlist with raw_symbols (no OCR needed in offline mode)."""

    def test_raw_symbols_audit_returns_ok(self):
        from app.services.research.multimodal_watchlist_bridge import audit_watchlist
        result = audit_watchlist(raw_symbols=["RELIANCE", "TCS"], intent="MULTIBAGGER")
        assert result["status"] == "OK"
        assert result["total_audited"] == 2

    def test_audit_results_have_required_keys(self):
        from app.services.research.multimodal_watchlist_bridge import audit_watchlist
        result = audit_watchlist(raw_symbols=["HBLPOWER"], intent="MULTIBAGGER")
        entry = result["audit_results"][0]
        for key in ["symbol", "verdict", "caqi_gate", "deme_hr_verdict", "pareto_rank", "risk_flags"]:
            assert key in entry, f"Missing key: {key}"

    def test_pareto_rank_injected_into_audit_results(self):
        from app.services.research.multimodal_watchlist_bridge import audit_watchlist
        result = audit_watchlist(raw_symbols=["RELIANCE", "TCS", "GESHIP"])
        for entry in result["audit_results"]:
            assert entry["pareto_rank"] is not None

    def test_empty_input_returns_no_symbols_found(self):
        from app.services.research.multimodal_watchlist_bridge import audit_watchlist
        result = audit_watchlist(raw_symbols=[], image_base64=None)
        assert result["status"] == "NO_SYMBOLS_FOUND"
        assert result["total_audited"] == 0

    def test_map_rank_summary_present(self):
        from app.services.research.multimodal_watchlist_bridge import audit_watchlist
        result = audit_watchlist(raw_symbols=["RELIANCE", "TCS"])
        assert result["map_rank_summary"] is not None
        assert len(result["map_rank_summary"]) == 2

    def test_single_failed_symbol_does_not_abort_audit(self):
        """Even if one symbol triggers an error, others should complete."""
        from app.services.research.multimodal_watchlist_bridge import audit_watchlist
        # INVALIDSYMBOL_XYZ999 will have empty fundamentals → error path
        result = audit_watchlist(raw_symbols=["RELIANCE", "INVALIDSYMBOL_XYZ999"])
        assert result["total_audited"] == 2
        assert result["status"] == "OK"
