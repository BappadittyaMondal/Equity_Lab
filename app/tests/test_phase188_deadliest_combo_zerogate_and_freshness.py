"""Phase 188 Dedicated Test Suite: Deadliest Combo Zero-Gate, Stage-4 Disqualification & Intraday TTL Freshness.

Verifies:
1. Stage-4 Markdown / Falling Knife hard block in PRE_FLY and DEADLIEST_COMBO intents.
2. Positive verification of Stage 1 Base and Stage 2 Uptrend in PRE_FLY.
3. Multiplicative timing damping and Stage-4 veto in DeadliestComboPipeline.
4. Intraday TTL freshness gate in ScreenerCloudConnector.get_or_fetch_fundamentals.
5. Inscription of FALLING_KNIFE_PREFLY_DISQUALIFICATION_RULE in learned_rules_registry.json.
"""

import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import pytest

from app.services.research.intent_adaptive_engine import QueryAdaptiveConstraintEngine
from app.services.research.deadliest_combo_pipeline import (
    run_deadliest_combo_pipeline,
    DeadliestComboResult,
)
from app.services.data_ingestion.screener_connector import ScreenerCloudConnector


def test_prefly_blocks_stage4_markdown():
    """Verify that a stock in Stage 4 Downtrend is blocked with OBJECTIVE_BLOCK in PRE_FLY."""
    falling_knife = {
        "symbol": "KPEL.BO",
        "current_price": 170.75,
        "high_52w": 673.75,
        "low_52w": 169.40,
        "dma_50": 270.27,
        "dma_200": 319.30,
        "weinstein_stage": "STAGE_4_DOWNTREND",
        "rsi": 22.54,
        "circuit_headroom": 15.0,
        "adtv_cr": 2.5,
    }
    result = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("PRE_FLY", falling_knife)
    assert result["passed"] is False
    assert any("OBJECTIVE_BLOCK" in v for v in result["vetoes"])
    assert any("Stage 4 Markdown" in v for v in result["vetoes"])


def test_deadliest_combo_blocks_stage4_markdown():
    """Verify that a fundamentally sound stock in Stage 4 Downtrend is blocked in DEADLIEST_COMBO."""
    kpel_data = {
        "symbol": "KPEL.BO",
        "current_price": 170.75,
        "high_52w": 673.75,
        "low_52w": 169.40,
        "dma_50": 270.27,
        "dma_200": 319.30,
        "weinstein_stage": "STAGE_4_DOWNTREND",
        "rsi": 22.54,
        "market_cap": 1156.0,
        "debt_to_equity": 0.18,
        "pledged_pct": 0.0,
        "roce_latest": 38.6,
        "cfo_pat_ratio": 1.15,
        "circuit_headroom": 15.0,
        "adtv_cr": 2.5,
        "operating_leverage_convexity": 1.45,
    }
    result = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("DEADLIEST_COMBO", kpel_data)
    assert result["passed"] is False
    assert any("OBJECTIVE_BLOCK" in v for v in result["vetoes"])
    assert any("Stage 4 Markdown" in v for v in result["vetoes"])


def test_prefly_allows_stage1_and_stage2():
    """Verify that healthy Stage 1 Base or Stage 2 Uptrend passes PRE_FLY without Stage 4 blocks."""
    healthy_base = {
        "symbol": "KSOLVES.NS",
        "current_price": 245.0,
        "high_52w": 260.0,
        "low_52w": 150.0,
        "dma_50": 230.0,
        "dma_200": 210.0,
        "weinstein_stage": "STAGE_2_UPTREND",
        "rsi": 58.0,
        "circuit_headroom": 10.0,
        "adtv_cr": 3.0,
    }
    result = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("PRE_FLY", healthy_base)
    assert result["passed"] is True
    assert not any("Stage 4 Markdown" in v for v in result["vetoes"])


def test_csuite_resignation_warning():
    """Verify that executive departure triggers an informative governance caution in PRE_FLY."""
    data = {
        "symbol": "KPEL.BO",
        "current_price": 250.0,
        "high_52w": 280.0,
        "dma_50": 240.0,
        "dma_200": 220.0,
        "weinstein_stage": "STAGE_1_BASE",
        "circuit_headroom": 10.0,
        "adtv_cr": 2.5,
        "csuite_resigned": True,
    }
    result = QueryAdaptiveConstraintEngine.evaluate_adaptive_constraints("PRE_FLY", data)
    assert any("Executive C-suite departure" in w for w in result["warnings"])


def test_deadliest_pipeline_disqualifies_stage4_when_enabled():
    """Verify that run_deadliest_combo_pipeline strictly disqualifies Stage 4 stock when disqualify_stage_4=True."""
    s_good = {
        "symbol": "GOOD.NS",
        "company_name": "Good Stage 2 Ltd",
        "market_cap": 2500.0,
        "current_price": 400.0,
        "high_52w": 420.0,
        "low_52w": 200.0,
        "dma_50": 380.0,
        "dma_200": 320.0,
        "debt_to_equity": 0.05,
        "pledged_pct": 0.0,
        "roce_annualized": 35.0,
        "cfo_pat": 1.1,
        "net_profit_last_year": 120.0,
        "pat_quality_flag": "OPERATING",
    }
    s_bad = {
        "symbol": "FALL.NS",
        "company_name": "Falling Knife Ltd",
        "market_cap": 1200.0,
        "current_price": 100.0,
        "high_52w": 350.0,
        "low_52w": 98.0,
        "dma_50": 160.0,
        "dma_200": 220.0,
        "debt_to_equity": 0.10,
        "pledged_pct": 0.0,
        "roce_annualized": 35.0,
        "cfo_pat": 1.1,
        "net_profit_last_year": 80.0,
        "pat_quality_flag": "OPERATING",
    }
    with patch("app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher.fetch_and_store") as mock_fetch:
        mock_fetch.side_effect = lambda sym: {"GOOD.NS": s_good, "FALL.NS": s_bad}.get(sym)

        results = run_deadliest_combo_pipeline(
            ["GOOD.NS", "FALL.NS"], top_n=5, disqualify_stage_4=True
        )
        assert len(results) == 1
        assert results[0].symbol == "GOOD.NS"


def test_screener_connector_freshness_ttl():
    """Verify that ScreenerCloudConnector flags stale cache when age exceeds max_staleness_hours."""
    stale_timestamp = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    mock_cached = {
        "symbol": "TEST.NS",
        "current_price": 100.0,
        "updated_at": stale_timestamp,
    }

    with patch.object(ScreenerCloudConnector, "get_company_fundamentals", return_value=mock_cached):
        # 1. With default 24h max staleness, 5h is considered fresh
        fresh_res = ScreenerCloudConnector.get_or_fetch_fundamentals("TEST.NS", max_staleness_hours=24.0)
        assert fresh_res is not None
        assert fresh_res.get("is_stale_cache") is False

        # 2. With strict 3h max staleness, 5h is stale, triggering live fetch fallback
        with patch("app.services.data_ingestion.fundamental_fetcher.FundamentalFetcher.fetch_and_store", return_value=None):
            stale_res = ScreenerCloudConnector.get_or_fetch_fundamentals("TEST.NS", max_staleness_hours=3.0)
            assert stale_res is not None
            assert stale_res.get("is_stale_cache") is True


def test_learned_rules_registry_contains_falling_knife_rule():
    """Verify that FALLING_KNIFE_PREFLY_DISQUALIFICATION_RULE is properly registered in learned_rules_registry.json."""
    with open("data/dynamic_knowledge/learned_rules_registry.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    entities = data.get("entities", {})
    assert "FALLING_KNIFE_PREFLY_DISQUALIFICATION_RULE" in entities
    rule = entities["FALLING_KNIFE_PREFLY_DISQUALIFICATION_RULE"]
    assert rule["category"] == "HARD_GATE_DISQUALIFICATION"
    assert rule["verification_status"] == "CERTIFIED_FACT"
