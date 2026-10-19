"""Phase 167 Test Suite — Daily News Intelligence, Anti-Clickbait Forensic Guard & Epistemic Self-Learning.

Verifies:
  1. RSS Source Registry expansion (Trade Brains, BSE).
  2. Universal Canonical Entity Resolver (maps Indian mid/smallcaps to exact NSE tickers).
  3. Anti-Clickbait Forensic Guard (flags penny stock / upper circuit operator traps).
  4. Institutional News Capsule Synthesizer (multi-expert 3-bullet briefing + EMR order extraction).
  5. Integration with classify_headline() and generate_daily_digest().
  6. Epistemic Dynamic Self-Learning Loop (registers news catalyst patterns into knowledge registry).
"""

import pytest
from app.services.research.daily_news_engine import (
    RSS_SOURCES,
    CANONICAL_TICKER_MAP,
    resolve_ticker_entities,
    classify_headline_forensics,
    synthesize_news_capsule,
    classify_headline,
    feed_news_to_self_learning,
)
from app.services.research.self_learning_engine import SelfLearningEngine


# ─────────────────────────────────────────────────────────────────────────────
# 1. RSS Source Registry Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_rss_sources_expansion():
    """Verify that Trade Brains and BSE announcements feeds are properly registered."""
    source_names = [s["name"] for s in RSS_SOURCES]
    assert "TradeBrains_All" in source_names
    assert "BSE_Corp_Announcements" in source_names

    tb = next(s for s in RSS_SOURCES if s["name"] == "TradeBrains_All")
    assert tb["category"] == "EQUITY_IDEAS"
    assert "tradebrains.in" in tb["url"]

    bse = next(s for s in RSS_SOURCES if s["name"] == "BSE_Corp_Announcements")
    assert bse["category"] == "REGULATORY"
    assert "bseindia.com" in bse["url"]


# ─────────────────────────────────────────────────────────────────────────────
# 2. Universal Entity Resolution Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_entity_resolution_canonical_tickers():
    """Verify headline company name mapping to exact NSE/BSE tickers."""
    test_cases = [
        ("Anand Rathi Wealth Q2 PAT jumps 22% YoY on wealth management inflows", "ANANDRATHI"),
        ("KPI Green Energy bags Rs 120 cr solar order in Gujarat", "KPIGREEN"),
        ("Adani Green commissions massive 551 MW solar plant at Khavda", "ADANIGREEN"),
        ("Netweb Technologies posts 849% profit growth driven by AI data center demand", "NETWEB"),
        ("Dynamic Cables wins Rs 150 Cr order from Power Grid Corporation", "DYCL"),
        ("HAL and BEL receive fresh export orders from friendly nations", "HAL"),
        ("General market wrap: Nifty closes above 25,000 as FIIs remain net buyers", None),
    ]

    for title, expected_ticker in test_cases:
        resolved = resolve_ticker_entities(title)
        assert resolved == expected_ticker, f"Failed resolving '{title}' -> Expected {expected_ticker}, got {resolved}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Anti-Clickbait Forensic Guard & Catalyst Tier Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_anti_clickbait_forensic_classifier():
    """Verify detection of retail clickbait pump-and-dump headlines vs real catalysts."""
    # Test Clickbait / Upper-Circuit Operator Churn Trap
    hype_headline = "Penny stock under Rs 15 locked in upper circuit after bagging small deal"
    hype_res = classify_headline_forensics(hype_headline)
    assert hype_res["is_clickbait_hype"] is True
    assert hype_res["operator_risk_tier"] == "HIGH_SPECULATIVE_RISK"
    assert hype_res["catalyst_tier"] == "OPERATOR_HYPE_TRAP"
    assert "WARNING" in hype_res["forensic_warning"]
    assert "Promoter Pledge" in hype_res["forensic_warning"]

    # Test Real Mega Order Win (Tier 1 Catalyst)
    order_headline = "L&T bags mega order worth Rs 1,500 Cr for high-speed rail corridor"
    order_res = classify_headline_forensics(order_headline)
    assert order_res["is_clickbait_hype"] is False
    assert order_res["operator_risk_tier"] == "NORMAL_MONITORING"
    assert order_res["order_value_cr"] == 1500.0
    assert order_res["catalyst_tier"] == "TIER_1_MOMENTUM_CATALYST"

    # Test Moderate Catalyst
    mod_headline = "Dynamic Cables secures contract of Rs 120 Crore from Discom"
    mod_res = classify_headline_forensics(mod_headline)
    assert mod_res["is_clickbait_hype"] is False
    assert mod_res["order_value_cr"] == 120.0
    assert mod_res["catalyst_tier"] == "TIER_2_MODERATE_CATALYST"


# ─────────────────────────────────────────────────────────────────────────────
# 4. Institutional News Capsule Synthesizer Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_news_capsule_synthesis():
    """Verify structured news capsule generation with executive briefing."""
    classified_item = {
        "title": "KPI Green Energy bags Rs 550 Cr solar power order",
        "resolved_ticker": "KPIGREEN",
        "sectors": ["POWER_ENERGY"],
        "direction": "POSITIVE",
        "magnitude": "HIGH",
        "catalyst_tier": "TIER_1_MOMENTUM_CATALYST",
        "order_value_cr": 550.0,
        "is_clickbait_hype": False,
    }

    capsule = synthesize_news_capsule(classified_item)
    assert capsule["ticker"] == "KPIGREEN"
    assert capsule["sector"] == "POWER_ENERGY"
    assert capsule["catalyst_tier"] == "TIER_1_MOMENTUM_CATALYST"
    assert capsule["forensic_grade"] == "CLEAN_FUNDAMENTAL"
    assert len(capsule["executive_briefing"]) == 3
    assert "HIGH-IMPACT CATALYST" in capsule["actionable_verdict"]

    # Test Clickbait Capsule
    clickbait_item = {
        "title": "Top penny stock under Rs 20 hits upper circuit",
        "resolved_ticker": "UNRESOLVED",
        "sectors": ["GENERAL"],
        "direction": "POSITIVE",
        "magnitude": "LOW",
        "catalyst_tier": "OPERATOR_HYPE_TRAP",
        "is_clickbait_hype": True,
    }
    cb_capsule = synthesize_news_capsule(clickbait_item)
    assert cb_capsule["forensic_grade"] == "OPERATOR_HYPE_TRAP"
    assert "HIGH OPERATOR RISK" in cb_capsule["actionable_verdict"]


# ─────────────────────────────────────────────────────────────────────────────
# 5. classify_headline Integration & Backward Compatibility Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_classify_headline_integration():
    """Verify classify_headline retains backward compatibility while exposing Phase 167 features."""
    headline = "Anand Rathi Wealth Q2 net profit jumps 22% YoY"
    res = classify_headline(headline)

    # Backward-compatible keys
    assert "sectors" in res
    assert "direction" in res
    assert "magnitude" in res
    assert res["direction"] == "POSITIVE"

    # Phase 167 keys
    assert res["resolved_ticker"] == "ANANDRATHI"
    assert "catalyst_tier" in res
    assert "news_capsule" in res
    assert res["news_capsule"]["ticker"] == "ANANDRATHI"
    assert res["is_clickbait_hype"] is False


# ─────────────────────────────────────────────────────────────────────────────
# 6. Epistemic Dynamic Self-Learning News Feedback Loop Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_self_learning_loop_from_news(tmp_path):
    """Verify that news catalysts feed directly into SelfLearningEngine patterns."""
    # Use temporary registry file for isolated test verification
    reg_file = str(tmp_path / "learned_rules_registry.json")
    engine = SelfLearningEngine(registry_file=reg_file)

    # Verify that the 3 Phase 167 candidate patterns exist in UNMAPPED_CANDIDATE_PATTERNS
    assert "REG30_MEGA_ORDER_CATALYST" in engine.UNMAPPED_CANDIDATE_PATTERNS
    assert "OPERATOR_CHURN_PENNY_HYPE" in engine.UNMAPPED_CANDIDATE_PATTERNS
    assert "EARNINGS_SUE_DRIFT_CATALYST" in engine.UNMAPPED_CANDIDATE_PATTERNS

    # Simulate news headlines
    test_headlines = [
        {
            "title": "BEL bags mega order worth Rs 850 Cr from Ministry of Defence",
            "catalyst_tier": "TIER_1_MOMENTUM_CATALYST",
            "is_clickbait_hype": False,
        },
        {
            "title": "Penny stock under Rs 10 locked in upper circuit",
            "catalyst_tier": "OPERATOR_HYPE_TRAP",
            "is_clickbait_hype": True,
        },
        {
            "title": "Anand Rathi Wealth Q2 PAT jumps 22% YoY on record fees",
            "catalyst_tier": "TIER_1_MOMENTUM_CATALYST",
            "is_clickbait_hype": False,
        },
    ]

    learned = feed_news_to_self_learning(test_headlines, self_learning_engine=engine)
    assert len(learned) == 3

    learned_ids = [rec["entity_id"] for rec in learned]
    assert "REG30_MEGA_ORDER_CATALYST" in learned_ids
    assert "OPERATOR_CHURN_PENNY_HYPE" in learned_ids
    assert "EARNINGS_SUE_DRIFT_CATALYST" in learned_ids

    # Verify that the learned entities are persisted in the dynamic registry
    stats = engine.get_learning_stats()
    assert stats["total_entities"] == 3
    assert stats["certified_facts"] >= 2
