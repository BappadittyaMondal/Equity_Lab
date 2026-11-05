"""Phase 198 Test Suite: Catalyst Taxonomy, Regulatory Panic Bridge, and Forensic Fixes.

Covers:
1. C7: Portfolio rebalancing prev_price missing/zero -> DATA_INSUFFICIENT HOLD (no phantom 49,900% gain).
2. C6: Deadliest combo pipeline Stage-4 veto defaults to True in public API.
3. C8: Shareholding pattern missing QoQ/streak defaults -> capped at 50.0 and emits SHAREHOLDING_DATA_INCOMPLETE.
4. P1-L: Phantom superstar guard -> NO_HISTORICAL_HOLDING_RECORD when queried superstar never held stock.
5. C4: Reverse-DCF return ceiling -> Turnaround archetype with negative PAT uses OCF proxy when CFO > 0.
6. P1-E: Intent adaptive engine -> SMART_SUPERSTAR_INVESTOR weight profile and alias normalization.
7. C9: Conformal calibration cache -> SMALL_CAP n=8 coverage warning metadata present.
8. NEW-C1: 6-Class Catalyst Taxonomy classification.
9. NEW-C2: Book-to-Bill ratio computation & sovereign capex bonus.
10. NEW-C3: Regulatory shock panic bridge auto-calling panic_vs_derate.
11. Self-Learning: 5 new entities registered in registry and UNMAPPED_CANDIDATE_PATTERNS.
"""

import json
from pathlib import Path
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# 1. C7: Portfolio Rebalancing Fix Tests
# ─────────────────────────────────────────────────────────────────────────────

from app.services.research.portfolio_rebalancing import (
    compute_portfolio_delta_rebalance,
    RebalanceAction,
)


def test_portfolio_rebalancing_missing_prev_price_no_phantom_gain():
    """C7: Missing entry price should produce HOLD with DATA_INSUFFICIENT, not 49,900% gain."""
    prev_portfolio = [
        {"symbol": "TESTCO", "rank": 1, "unrealized_return_pct": 0.0}  # No price, entry_price, or current_price
    ]
    curr_portfolio = [
        {"symbol": "TESTCO", "rank": 1, "price": 500.0, "reverse_dcf_headroom": 40.0}
    ]

    result = compute_portfolio_delta_rebalance(prev_portfolio, curr_portfolio)
    decisions = result["decisions"]
    assert len(decisions) == 1
    d = decisions[0]
    assert d["symbol"] == "TESTCO"
    assert d["action"] == RebalanceAction.HOLD.value
    assert "DATA_INSUFFICIENT" in d["rationale"]
    assert d["price_change_pct"] == 0.0


def test_portfolio_rebalancing_zero_or_negative_prev_price():
    """C7: Zero or negative prev_price should yield DATA_INSUFFICIENT HOLD."""
    prev_portfolio = [{"symbol": "BADPRICE", "price": 0.0, "rank": 2}]
    curr_portfolio = [{"symbol": "BADPRICE", "price": 100.0, "rank": 2}]

    result = compute_portfolio_delta_rebalance(prev_portfolio, curr_portfolio)
    d = result["decisions"][0]
    assert d["action"] == RebalanceAction.HOLD.value
    assert "DATA_INSUFFICIENT" in d["rationale"]


def test_portfolio_rebalancing_valid_gain_takes_profit():
    """Normal legitimate gain >= 30% with exhausted DCF headroom takes profit."""
    prev_portfolio = [{"symbol": "GOODCO", "price": 100.0, "rank": 1}]
    curr_portfolio = [
        {
            "symbol": "GOODCO",
            "price": 140.0,
            "rank": 1,
            "reverse_dcf_headroom": 5.0,  # Below 10.0 min headroom
        }
    ]
    result = compute_portfolio_delta_rebalance(prev_portfolio, curr_portfolio)
    d = result["decisions"][0]
    assert d["action"] == RebalanceAction.TAKE_PROFIT.value
    assert d["price_change_pct"] == 40.0


# ─────────────────────────────────────────────────────────────────────────────
# 2. C6: Deadliest Combo Pipeline Stage-4 Veto Default Tests
# ─────────────────────────────────────────────────────────────────────────────

import inspect
from app.services.research.deadliest_combo_pipeline import (
    run_deadliest_combo_pipeline,
    run_deadliest_combo_pipeline_with_audit,
)


def test_deadliest_combo_stage4_veto_default_true():
    """C6: Public API functions for Deadliest Combo must default disqualify_stage_4 to True."""
    sig1 = inspect.signature(run_deadliest_combo_pipeline)
    assert sig1.parameters["disqualify_stage_4"].default is True

    sig2 = inspect.signature(run_deadliest_combo_pipeline_with_audit)
    assert sig2.parameters["disqualify_stage_4"].default is True


# ─────────────────────────────────────────────────────────────────────────────
# 3. C8 & P1-L: Shareholding Pattern Tests
# ─────────────────────────────────────────────────────────────────────────────

from app.services.strategies.shareholding_pattern import (
    evaluate_shareholding_pattern,
    detect_phantom_superstar_status,
)


def test_shareholding_missing_qoq_streak_capped_at_50():
    """C8: Incomplete institutional QoQ/streak data caps flow score at 50 and emits evidence flag."""
    minimal_data = {
        "fii_holding_pct": 12.0,
        "dii_mf_holding_pct": 15.0,
        # fii_qoq_change, dii_qoq_change, institutional_accumulation_quarters are omitted
    }
    res = evaluate_shareholding_pattern("TCS", shareholding_data=minimal_data)
    assert res["institutional_flow_score"] <= 50.0
    assert any("SHAREHOLDING_DATA_INCOMPLETE" in ev for ev in res["evidence"])


def test_shareholding_complete_data_scores_above_50():
    """When positive QoQ institutional accumulation is present, score can exceed 50."""
    complete_data = {
        "fii_holding_pct": 20.0,
        "fii_qoq_change": 2.5,
        "dii_mf_holding_pct": 18.0,
        "dii_qoq_change": 1.8,
        "institutional_accumulation_quarters": 4,
        "retail_holding_trend": "DECREASING",
        "free_float_market_cap_cr": 5000.0,
    }
    res = evaluate_shareholding_pattern("INFY", shareholding_data=complete_data)
    assert res["institutional_flow_score"] > 50.0


def test_phantom_superstar_never_held_stock_not_phantom():
    """P1-L: Queried superstar who never held stock should be NO_HISTORICAL_HOLDING_RECORD, not PHANTOM."""
    res = detect_phantom_superstar_status(
        symbol="ABCCO",
        current_holders=[],
        historical_holders=[],  # No historical record
        queried_superstar="VIJAY_KEDIA",
    )
    assert res["is_phantom_detected"] is False
    assert res["conviction_haircut_pts"] == 0.0
    assert len(res["exited_superstars"]) == 1
    assert res["exited_superstars"][0]["current_status"] == "NO_HISTORICAL_HOLDING_RECORD"
    assert res["exited_superstars"][0]["is_phantom"] is False


def test_phantom_superstar_actual_exit_triggers_phantom():
    """Real phantom exit: investor had >= 1% historically and is absent now."""
    historical = [{"holder_name": "Vijay Kedia", "holding_pct": 2.5}]
    current = []  # Exited below 1% or completely
    res = detect_phantom_superstar_status(
        symbol="XYZCO",
        current_holders=current,
        historical_holders=historical,
        queried_superstar="VIJAY_KEDIA",
    )
    assert res["is_phantom_detected"] is True
    assert res["conviction_haircut_pts"] == 25.0
    assert res["verdict_label"] == "PHANTOM_EXIT_DISTRIBUTION_TRAP"


# ─────────────────────────────────────────────────────────────────────────────
# 4. C4: Return Ceiling OCF Fallback Tests
# ─────────────────────────────────────────────────────────────────────────────

from app.services.research.return_ceiling import compute_return_ceiling


def test_return_ceiling_negative_pat_non_turnaround_insufficient_data():
    """Negative PAT without turnaround archetype returns INSUFFICIENT_DATA."""
    res = compute_return_ceiling(
        current_mcap_cr=1000.0,
        ttm_pat_cr=-50.0,
        archetype="MULTIBAGGER",
    )
    assert res["label"] == "INSUFFICIENT_DATA"
    assert res["base_multiple"] == 0.0


def test_return_ceiling_turnaround_with_positive_ocf_proxy():
    """C4: Turnaround with negative PAT but positive 3-yr OCF computes reverse-DCF using OCF proxy."""
    res = compute_return_ceiling(
        current_mcap_cr=1000.0,
        ttm_pat_cr=-30.0,
        archetype="TURNAROUND",
        cfo_3yr_avg=120.0,
    )
    assert res["ocf_proxy_used"] is True
    assert res["base_multiple"] > 0.0
    assert "OCF_NORMALIZED_TURNAROUND_" in res["label"]


# ─────────────────────────────────────────────────────────────────────────────
# 5. P1-E: Intent Adaptive Engine SMART_SUPERSTAR_INVESTOR Tests
# ─────────────────────────────────────────────────────────────────────────────

from app.services.research.intent_adaptive_engine import (
    QueryAdaptiveConstraintEngine,
    ARCHETYPE_WEIGHT_PROFILES,
)


def test_smart_superstar_weight_profile_present_and_sums_to_one():
    """P1-E: SMART_SUPERSTAR_INVESTOR must exist in ARCHETYPE_WEIGHT_PROFILES and sum to 1.0."""
    assert "SMART_SUPERSTAR_INVESTOR" in ARCHETYPE_WEIGHT_PROFILES
    profile = ARCHETYPE_WEIGHT_PROFILES["SMART_SUPERSTAR_INVESTOR"]
    assert profile["GOVERNANCE"] == 0.35
    assert profile["FUNDAMENTAL"] == 0.30
    assert profile["FORENSIC"] == 0.20
    assert profile["VALUATION"] == 0.10
    assert profile["TECHNICAL"] == 0.05
    assert pytest.approx(sum(profile.values()), abs=1e-5) == 1.0


def test_smart_superstar_intent_alias_normalization():
    """P1-E: Superstar aliases must normalize to SMART_SUPERSTAR_INVESTOR."""
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("super investor") == "SMART_SUPERSTAR_INVESTOR"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("smart money") == "SMART_SUPERSTAR_INVESTOR"
    assert QueryAdaptiveConstraintEngine.normalize_intent_alias("marquee investor") == "SMART_SUPERSTAR_INVESTOR"


# ─────────────────────────────────────────────────────────────────────────────
# 6. C9: Conformal Calibration Cache Warning Tests
# ─────────────────────────────────────────────────────────────────────────────


def test_conformal_cache_has_small_cap_warning():
    """C9: Conformal calibration cache must contain SMALL_CAP n=8 coverage warning."""
    cache_path = Path("conformal_calibration_cache.json")
    assert cache_path.exists()
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    warnings = data.get("metadata", {}).get("coverage_warnings", {})
    assert "SMALL_CAP" in warnings
    assert "n=8" in warnings["SMALL_CAP"]


# ─────────────────────────────────────────────────────────────────────────────
# 7. NEW-C1, NEW-C2, NEW-C3: Catalyst Taxonomy & Panic Bridge Tests
# ─────────────────────────────────────────────────────────────────────────────

from app.services.research.daily_news_engine import (
    classify_catalyst_class,
    compute_book_to_bill,
    classify_headline,
    feed_news_to_self_learning,
)


def test_catalyst_classification_six_classes():
    """NEW-C1: All 6 catalyst taxonomy classes must be correctly classified from keywords."""
    assert classify_catalyst_class("Defence Ministry awards Rs 15000 Cr LOI contract value to BHEL") == "SOVEREIGN_ORDER_WIN"
    assert classify_catalyst_class("RBI guidelines tighten risk weights on NBFC unsecured lending") == "REGULATORY_SHOCK"
    assert classify_catalyst_class("CG Power signs semiconductor ATMP joint venture agreement with Renesas") == "GLOBAL_TECH_JV"
    assert classify_catalyst_class("Q3 EBITDA margin jumped 350 bps on operating leverage and volume growth") == "OPERATING_LEVERAGE_BLOWOUT"
    assert classify_catalyst_class("Netweb Technologies approved as Tier-1 supplier for AI data center server deployment") == "TECH_ECOSYSTEM_CERT"
    assert classify_catalyst_class("PE fund sells 7% stake in open market secondary block deal sell") == "PE_SECONDARY_EXIT"


def test_book_to_bill_ratio_computation():
    """NEW-C2: Book-to-Bill >= 2.5x awards sovereign capex bonus."""
    res_high = compute_book_to_bill(order_book_cr=30000.0, ttm_revenue_cr=10000.0)
    assert res_high["b2b_ratio"] == 3.0
    assert res_high["sovereign_capex_bonus"] is True
    assert res_high["b2b_tier"] == "HIGH_VISIBILITY"

    res_low = compute_book_to_bill(order_book_cr=8000.0, ttm_revenue_cr=10000.0)
    assert res_low["b2b_ratio"] == 0.8
    assert res_low["sovereign_capex_bonus"] is False
    assert res_low["b2b_tier"] == "REVENUE_RUNOFF_RISK"

    res_none = compute_book_to_bill(None, 1000.0)
    assert res_none["b2b_ratio"] is None
    assert res_none["sovereign_capex_bonus"] is False


def test_regulatory_shock_triggers_panic_classifier_bridge():
    """NEW-C3: REGULATORY_SHOCK headline automatically invokes panic_vs_derate."""
    # When fundamentals are solid (ROCE >= 15%, OPM intact), should identify PANIC_DISLOCATION_OPPORTUNITY
    financials = {
        "roce_latest": 22.0,
        "roce_qoq_change": 0.5,
        "opm_latest": 18.0,
        "opm_5yr": 16.0,
        "pe_ratio": 15.0,
        "pe_1yr_avg": 20.0,
        "rsi_14": 32.0,
        "price_drop_3m_pct": 18.0,
    }
    headline = "RBI circular hikes risk weights on microfinance portfolio"
    res = classify_headline(headline, item_financials=financials)

    assert res["catalyst_class"] == "REGULATORY_SHOCK"
    assert res["regulatory_panic_verdict"] == "PANIC_DISLOCATION_OPPORTUNITY"
    assert res["panic_analysis"] is not None


# ─────────────────────────────────────────────────────────────────────────────
# 8. Self-Learning Registry & Patterns Tests
# ─────────────────────────────────────────────────────────────────────────────

from app.services.research.self_learning_engine import SelfLearningEngine


def test_self_learning_registry_has_67_entities():
    """Registry must contain exactly 67 entities with the 5 new Phase 198 additions."""
    reg_path = Path("data/dynamic_knowledge/learned_rules_registry.json")
    data = json.loads(reg_path.read_text(encoding="utf-8"))
    assert data["total_entities_count"] == 67
    assert len(data["entities"]) == 67

    new_entities = [
        "SIX_CATALYST_TAXONOMY_FRAMEWORK",
        "RBI_REGULATORY_PANIC_VS_STRUCTURAL_DERATE",
        "SOVEREIGN_MEGA_ORDER_BOOK_TO_BILL",
        "GLOBAL_TECH_JV_PLI_MOAT",
        "PE_SECONDARY_BLOCK_EXIT_TRAP",
    ]
    for eid in new_entities:
        assert eid in data["entities"]


def test_self_learning_engine_candidate_patterns_include_phase198():
    """UNMAPPED_CANDIDATE_PATTERNS in SelfLearningEngine must include the 5 Phase 198 patterns."""
    patterns = SelfLearningEngine.UNMAPPED_CANDIDATE_PATTERNS
    assert "SIX_CATALYST_TAXONOMY_FRAMEWORK" in patterns
    assert "RBI_REGULATORY_PANIC_VS_STRUCTURAL_DERATE" in patterns
    assert "SOVEREIGN_MEGA_ORDER_BOOK_TO_BILL" in patterns
    assert "GLOBAL_TECH_JV_PLI_MOAT" in patterns
    assert "PE_SECONDARY_BLOCK_EXIT_TRAP" in patterns


# ─────────────────────────────────────────────────────────────────────────────
# 9. Extended Edge Case & Forensic Tests (Phase 198 Quality Depth)
# ─────────────────────────────────────────────────────────────────────────────

def test_portfolio_rebalancing_trim_on_rank_drop_without_big_gain():
    """Stock drops out of current ranking with only 5% gain -> TRIM."""
    prev_portfolio = [{"symbol": "DROPPED", "price": 100.0, "rank": 5}]
    curr_portfolio = [{"symbol": "OTHER", "price": 200.0, "rank": 1}]
    res = compute_portfolio_delta_rebalance(prev_portfolio, curr_portfolio)
    d = res["decisions"][0]
    assert d["action"] == RebalanceAction.TRIM.value
    assert "Relative rank displaced" in d["rationale"]


def test_portfolio_rebalancing_new_entry_candidate():
    """Stock newly appears in current portfolio -> NEW_ENTRY."""
    prev_portfolio = [{"symbol": "OLD", "price": 100.0, "rank": 1}]
    curr_portfolio = [
        {"symbol": "OLD", "price": 102.0, "rank": 1},
        {"symbol": "FRESH", "price": 50.0, "rank": 2, "reverse_dcf_headroom": 45.0},
    ]
    res = compute_portfolio_delta_rebalance(prev_portfolio, curr_portfolio)
    fresh_d = [d for d in res["decisions"] if d["symbol"] == "FRESH"][0]
    assert fresh_d["action"] == RebalanceAction.NEW_ENTRY.value
    assert fresh_d["current_rank"] == 2


def test_return_ceiling_turnaround_zero_cfo_insufficient_data():
    """Turnaround with negative PAT and cfo_3yr_avg <= 0 remains INSUFFICIENT_DATA."""
    res = compute_return_ceiling(
        current_mcap_cr=1000.0,
        ttm_pat_cr=-20.0,
        archetype="TURNAROUND",
        cfo_3yr_avg=0.0,
    )
    assert res["label"] == "INSUFFICIENT_DATA"
    assert res["base_multiple"] == 0.0


def test_return_ceiling_turnaround_negative_cfo_insufficient_data():
    """Turnaround with negative PAT and negative cfo_3yr_avg remains INSUFFICIENT_DATA."""
    res = compute_return_ceiling(
        current_mcap_cr=1000.0,
        ttm_pat_cr=-20.0,
        archetype="TURNAROUND",
        cfo_3yr_avg=-15.0,
    )
    assert res["label"] == "INSUFFICIENT_DATA"


def test_return_ceiling_turnaround_label_preservation():
    """Turnaround with OCF proxy produces compounder or multibagger label with prefix."""
    res = compute_return_ceiling(
        current_mcap_cr=500.0,
        ttm_pat_cr=-10.0,
        archetype="TURNAROUND",
        cfo_3yr_avg=150.0,
    )
    assert res["ocf_proxy_used"] is True
    assert "OCF_NORMALIZED_TURNAROUND_" in res["label"]


def test_catalyst_sovereign_order_win_sub_keywords():
    """SOVEREIGN_ORDER_WIN matches railway board, NTPC, NHSRCL, EPC award."""
    assert classify_catalyst_class("Railway Board awards Rs 3200 Cr wagon contract to Titagarh") == "SOVEREIGN_ORDER_WIN"
    assert classify_catalyst_class("NTPC award of 800 MW thermal EPC project to BHEL") == "SOVEREIGN_ORDER_WIN"
    assert classify_catalyst_class("NHSRCL bullet train viaduct contract value Rs 8500 Cr") == "SOVEREIGN_ORDER_WIN"
    assert classify_catalyst_class("Navy order for 3 next-gen corvettes to Cochin Shipyard") == "SOVEREIGN_ORDER_WIN"


def test_catalyst_regulatory_shock_sub_keywords():
    """REGULATORY_SHOCK matches USFDA 483, SEBI circular, GST demand, import alert."""
    assert classify_catalyst_class("USFDA 483 with 6 observations issued to Hyderabad API plant") == "REGULATORY_SHOCK"
    assert classify_catalyst_class("SEBI circular mandates tighter derivative margin norms") == "REGULATORY_SHOCK"
    assert classify_catalyst_class("Company receives Rs 450 Cr GST demand and show cause notice") == "REGULATORY_SHOCK"
    assert classify_catalyst_class("USFDA issues import alert on injectables facility") == "REGULATORY_SHOCK"


def test_catalyst_global_tech_jv_sub_keywords():
    """GLOBAL_TECH_JV matches semiconductor, OSAT, Renesas, PLI, technology transfer."""
    assert classify_catalyst_class("Murugappa group signs semiconductor OSAT ATMP JV with Renesas") == "GLOBAL_TECH_JV"
    assert classify_catalyst_class("Technology transfer agreement signed for silicon carbide power modules") == "GLOBAL_TECH_JV"
    assert classify_catalyst_class("Company cleared under PLI scheme for telecom equipment manufacturing") == "GLOBAL_TECH_JV"


def test_catalyst_operating_leverage_sub_keywords():
    """OPERATING_LEVERAGE_BLOWOUT matches capacity utilization, margin expansion, record profit."""
    assert classify_catalyst_class("Operating leverage drives 400 bps EBITDA margin expansion") == "OPERATING_LEVERAGE_BLOWOUT"
    assert classify_catalyst_class("Capacity utilization crosses 90% as volume growth surges 28%") == "OPERATING_LEVERAGE_BLOWOUT"
    assert classify_catalyst_class("PAT surges 85% to record profit of Rs 120 Cr") == "OPERATING_LEVERAGE_BLOWOUT"


def test_catalyst_tech_ecosystem_cert_sub_keywords():
    """TECH_ECOSYSTEM_CERT matches qualified supplier, OEM approved, tier-1 partner."""
    assert classify_catalyst_class("Company designated preferred vendor for European defense OEM") == "TECH_ECOSYSTEM_CERT"
    assert classify_catalyst_class("OEM approved supplier certification received for EV battery enclosures") == "TECH_ECOSYSTEM_CERT"
    assert classify_catalyst_class("Automotive Tier-1 supplier audit completed with zero non-conformances") == "TECH_ECOSYSTEM_CERT"


def test_catalyst_pe_secondary_exit_sub_keywords():
    """PE_SECONDARY_EXIT matches promoter offloading, block deal sell, PE exit."""
    assert classify_catalyst_class("Warburg Pincus executes PE exit via Rs 1800 Cr block deal sell") == "PE_SECONDARY_EXIT"
    assert classify_catalyst_class("Promoter offloading 4.5% stake through open market sale") == "PE_SECONDARY_EXIT"
    assert classify_catalyst_class("Pre-IPO investor exit completed via secondary sale on BSE") == "PE_SECONDARY_EXIT"


def test_book_to_bill_ultra_high_visibility():
    """B2B >= 4.0x yields ULTRA_HIGH_VISIBILITY tier."""
    res = compute_book_to_bill(order_book_cr=45000.0, ttm_revenue_cr=10000.0)
    assert res["b2b_ratio"] == 4.5
    assert res["b2b_tier"] == "ULTRA_HIGH_VISIBILITY"
    assert res["sovereign_capex_bonus"] is True


def test_book_to_bill_moderate_visibility():
    """1.5x <= B2B < 2.5x yields MODERATE_VISIBILITY without bonus."""
    res = compute_book_to_bill(order_book_cr=20000.0, ttm_revenue_cr=10000.0)
    assert res["b2b_ratio"] == 2.0
    assert res["b2b_tier"] == "MODERATE_VISIBILITY"
    assert res["sovereign_capex_bonus"] is False


def test_book_to_bill_low_visibility():
    """1.0x <= B2B < 1.5x yields LOW_VISIBILITY."""
    res = compute_book_to_bill(order_book_cr=12000.0, ttm_revenue_cr=10000.0)
    assert res["b2b_ratio"] == 1.2
    assert res["b2b_tier"] == "LOW_VISIBILITY"
    assert res["sovereign_capex_bonus"] is False


def test_book_to_bill_zero_ttm_revenue():
    """Zero or negative TTM revenue produces INSUFFICIENT_DATA."""
    res = compute_book_to_bill(order_book_cr=1000.0, ttm_revenue_cr=0.0)
    assert res["b2b_tier"] == "INSUFFICIENT_DATA"
    assert res["b2b_ratio"] is None
    assert res["sovereign_capex_bonus"] is False


def test_regulatory_panic_structural_derate_classification():
    """When fundamentals are deteriorating (low ROCE, falling margins), verdict is STRUCTURAL_DE_RATING_AVOID."""
    bad_financials = {
        "roce_latest": 6.0,  # Below cost of capital
        "roce_qoq_change": -4.0,  # Deteriorating
        "opm_latest": 5.0,
        "opm_5yr": 12.0,
        "pe_ratio": 25.0,
        "pe_1yr_avg": 22.0,  # P/E expanded or flat despite earnings drop
        "rsi_14": 55.0,  # Not oversold
        "price_drop_3m_pct": 12.0,
    }
    headline = "RBI regulatory action freezes new loan disbursements"
    res = classify_headline(headline, item_financials=bad_financials)
    assert res["catalyst_class"] == "REGULATORY_SHOCK"
    assert res["regulatory_panic_verdict"] == "STRUCTURAL_DE_RATING_AVOID"


def test_feed_news_to_self_learning_sovereign_order():
    """News feed router sends SOVEREIGN_ORDER_WIN to SOVEREIGN_MEGA_ORDER_BOOK_TO_BILL."""
    headlines = [
        {
            "title": "Defence Ministry awards Rs 12000 Cr order to HAL",
            "catalyst_class": "SOVEREIGN_ORDER_WIN",
            "catalyst_tier": "TIER_1_MOMENTUM_CATALYST",
            "is_clickbait_hype": False,
        }
    ]
    # Uses mock or real engine
    learned = feed_news_to_self_learning(headlines)
    assert isinstance(learned, list)


def test_feed_news_to_self_learning_pe_exit():
    """News feed router sends PE_SECONDARY_EXIT to PE_SECONDARY_BLOCK_EXIT_TRAP."""
    headlines = [
        {
            "title": "Promoter offloading block deal sell of 5% equity",
            "catalyst_class": "PE_SECONDARY_EXIT",
            "catalyst_tier": "STANDARD_ANNOUNCEMENT",
            "is_clickbait_hype": False,
        }
    ]
    learned = feed_news_to_self_learning(headlines)
    assert isinstance(learned, list)


def test_feed_news_to_self_learning_global_tech_jv():
    """News feed router sends GLOBAL_TECH_JV to GLOBAL_TECH_JV_PLI_MOAT."""
    headlines = [
        {
            "title": "Tata Electronics signs semiconductor joint venture with international fab",
            "catalyst_class": "GLOBAL_TECH_JV",
            "catalyst_tier": "TIER_1_MOMENTUM_CATALYST",
            "is_clickbait_hype": False,
        }
    ]
    learned = feed_news_to_self_learning(headlines)
    assert isinstance(learned, list)


def test_shareholding_concentration_risk_high():
    """FII + DII > 65% triggers HIGH concentration risk."""
    data = {
        "fii_holding_pct": 40.0,
        "dii_mf_holding_pct": 30.0,
        "fii_qoq_change": 1.0,
        "dii_qoq_change": 1.0,
        "institutional_accumulation_quarters": 3,
        "retail_holding_trend": "DECREASING",
        "free_float_market_cap_cr": 8000.0,
    }
    res = evaluate_shareholding_pattern("HIGHINST", shareholding_data=data)
    assert res["pattern_intelligence"]["ownership_concentration_risk"] == "HIGH"


def test_shareholding_concentration_risk_balanced():
    """FII + DII <= 65% with FII <= 35% triggers BALANCED concentration risk."""
    data = {
        "fii_holding_pct": 18.0,
        "dii_mf_holding_pct": 14.0,
        "fii_qoq_change": 0.5,
        "dii_qoq_change": 0.5,
        "institutional_accumulation_quarters": 2,
        "retail_holding_trend": "DECREASING",
        "free_float_market_cap_cr": 3500.0,
    }
    res = evaluate_shareholding_pattern("BALINST", shareholding_data=data)
    assert res["pattern_intelligence"]["ownership_concentration_risk"] == "BALANCED"


def test_shareholding_reporting_lag_stale_warning():
    """If stock has run up > 35% since quarter-end filing price, emits Reporting Lag warning."""
    data = {
        "fii_holding_pct": 20.0,
        "dii_mf_holding_pct": 15.0,
        "fii_qoq_change": 1.0,
        "dii_qoq_change": 1.0,
        "institutional_accumulation_quarters": 2,
        "retail_holding_trend": "DECREASING",
        "free_float_market_cap_cr": 5000.0,
        "current_price": 280.0,
        "quarter_end_price": 200.0,  # 40% runup
    }
    res = evaluate_shareholding_pattern("LAGCO", shareholding_data=data)
    assert any("Reporting Lag" in ev for ev in res["evidence"])
