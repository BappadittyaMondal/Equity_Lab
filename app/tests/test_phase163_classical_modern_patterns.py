"""Phase 163: Classical & Modern Technical Patterns, Market Mindset & Tape Reading Test Suite.

Validates:
1. Steve Nison Japanese Candlestick Reversal Triggers (Hammer, Bullish Engulfing, Morning Star, Shooting Star).
2. Richard Wyckoff Tape Reading Mechanics (Phase C Spring, Absorption, UTAD Upthrust).
3. Nicolas Darvas Box Theory & Classical Geometry (Box floor/ceiling, Stage 2 Box Breakout).
4. Stan Weinstein Mansfield Relative Strength (MRS) ratio calculation vs benchmark.
5. Jesse Livermore Pivotal Point & Bull Trap Exhaustion Guards (Overextension > 15% & Volume Collapse).
6. Technical Base Quality Engine Composite Math Invariance & Enriched Breakdown.
7. Single-Tick Structural Invalidation Stop Extraction.
8. Epistemic Self-Learning Dynamic Registration of Phase 163 Knowledge Entities.
"""

import pytest
from app.services.research.technical_base_quality import TechnicalBaseQualityEngine
from app.services.research.self_learning_engine import SelfLearningEngine


# -----------------------------------------------------------------------------
# 1. Steve Nison Japanese Candlestick Tests
# -----------------------------------------------------------------------------

def test_nison_explicit_patterns():
    # Explicit bullish override
    data_bull = {"candlestick_pattern": "BULLISH_ENGULFING"}
    _, bd_b = TechnicalBaseQualityEngine.score(data_bull)
    assert bd_b["nison_candlestick"]["is_bullish_reversal"] is True
    assert bd_b["nison_candlestick"]["is_bearish_reversal"] is False
    assert bd_b["nison_candlestick"]["candle_score"] >= 0.95

    # Explicit bearish override
    data_bear = {"candlestick_pattern": "SHOOTING_STAR"}
    _, bd_s = TechnicalBaseQualityEngine.score(data_bear)
    assert bd_s["nison_candlestick"]["is_bullish_reversal"] is False
    assert bd_s["nison_candlestick"]["is_bearish_reversal"] is True
    assert bd_s["nison_candlestick"]["candle_score"] <= 0.25


def test_nison_candle_geometry_hammer():
    # 1-bar Hammer: long lower shadow, tiny upper shadow
    data = {
        "current_price": 101.0,
        "candles": [
            {"open": 100.0, "high": 101.8, "low": 85.0, "close": 101.0}
        ]
    }
    _, bd = TechnicalBaseQualityEngine.score(data)
    candle = bd["nison_candlestick"]
    assert candle["pattern_name"] == "HAMMER"
    assert candle["is_bullish_reversal"] is True
    assert candle["candle_score"] == 0.95


def test_nison_candle_geometry_shooting_star():
    # 1-bar Shooting Star: long upper shadow, tiny lower shadow
    data = {
        "current_price": 99.5,
        "candles": [
            {"open": 100.0, "high": 115.0, "low": 99.2, "close": 99.5}
        ]
    }
    _, bd = TechnicalBaseQualityEngine.score(data)
    candle = bd["nison_candlestick"]
    assert candle["pattern_name"] == "SHOOTING_STAR"
    assert candle["is_bearish_reversal"] is True
    assert candle["candle_score"] == 0.20


def test_nison_candle_geometry_bullish_engulfing():
    # 2-bar Bullish Engulfing: bar 1 red, bar 2 completely engulfs bar 1
    data = {
        "current_price": 108.0,
        "candles": [
            {"open": 105.0, "high": 106.0, "low": 97.5, "close": 98.0},
            {"open": 97.0, "high": 109.0, "low": 96.5, "close": 108.0}
        ]
    }
    _, bd = TechnicalBaseQualityEngine.score(data)
    candle = bd["nison_candlestick"]
    assert candle["pattern_name"] == "BULLISH_ENGULFING"
    assert candle["is_bullish_reversal"] is True
    assert candle["candle_score"] == 1.0


def test_nison_candle_geometry_morning_star():
    # 3-bar Morning Star: bar 1 large red, bar 2 small body, bar 3 strong green
    data = {
        "current_price": 104.0,
        "candles": [
            {"open": 110.0, "high": 111.0, "low": 98.0, "close": 99.0},
            {"open": 96.0, "high": 97.0, "low": 94.0, "close": 96.5},
            {"open": 97.5, "high": 106.0, "low": 97.0, "close": 105.0}
        ]
    }
    _, bd = TechnicalBaseQualityEngine.score(data)
    candle = bd["nison_candlestick"]
    assert candle["pattern_name"] == "MORNING_STAR"
    assert candle["is_bullish_reversal"] is True
    assert candle["candle_score"] == 1.0


# -----------------------------------------------------------------------------
# 2. Richard Wyckoff Tape Reading Tests
# -----------------------------------------------------------------------------

def test_wyckoff_explicit_flags():
    data_spring = {"wyckoff_spring": True}
    _, bd_sp = TechnicalBaseQualityEngine.score(data_spring)
    assert bd_sp["wyckoff_market_mechanics"]["wyckoff_state"] == "WYCKOFF_PHASE_C_SPRING"
    assert bd_sp["wyckoff_market_mechanics"]["wyckoff_score"] == 0.95

    data_utad = {"wyckoff_utad": True}
    _, bd_ut = TechnicalBaseQualityEngine.score(data_utad)
    assert bd_ut["wyckoff_market_mechanics"]["wyckoff_state"] == "WYCKOFF_UTAD_DISTRIBUTION_TRAP"
    assert bd_ut["wyckoff_market_mechanics"]["wyckoff_score"] == 0.20


def test_wyckoff_candle_spring_and_invalidation():
    # Candle 5 undercuts prior low 100.0 to 95.0 and recovers on light volume
    candles = [
        {"open": 105.0, "high": 108.0, "low": 100.0, "close": 104.0, "volume": 1000},
        {"open": 104.0, "high": 106.0, "low": 101.0, "close": 103.0, "volume": 1100},
        {"open": 103.0, "high": 105.0, "low": 100.5, "close": 101.5, "volume": 950},
        {"open": 102.0, "high": 103.0, "low": 100.0, "close": 101.0, "volume": 900},
        {"open": 99.0, "high": 103.0, "low": 95.0, "close": 102.0, "volume": 800},
    ]
    data = {"current_price": 102.0, "candles": candles}
    _, bd = TechnicalBaseQualityEngine.score(data)
    wyck = bd["wyckoff_market_mechanics"]
    assert wyck["spring_detected"] is True
    assert wyck["wyckoff_state"] == "WYCKOFF_PHASE_C_SPRING"
    assert wyck["spring_invalidation_level"] == round(95.0 * 0.995, 2)


def test_wyckoff_candle_utad_upthrust():
    # Candle 5 spikes above prior high 110.0 to 118.0 and dumps on heavy volume
    candles = [
        {"open": 105.0, "high": 110.0, "low": 102.0, "close": 108.0, "volume": 1000},
        {"open": 107.0, "high": 109.0, "low": 103.0, "close": 106.0, "volume": 1100},
        {"open": 106.0, "high": 110.0, "low": 104.0, "close": 107.0, "volume": 950},
        {"open": 107.0, "high": 109.5, "low": 105.0, "close": 108.0, "volume": 900},
        {"open": 109.0, "high": 118.0, "low": 105.0, "close": 107.0, "volume": 2500},
    ]
    data = {"current_price": 107.0, "candles": candles}
    _, bd = TechnicalBaseQualityEngine.score(data)
    wyck = bd["wyckoff_market_mechanics"]
    assert wyck["utad_warning"] is True
    assert wyck["wyckoff_state"] == "WYCKOFF_UTAD_DISTRIBUTION_TRAP"
    assert wyck["wyckoff_score"] == 0.20


# -----------------------------------------------------------------------------
# 3. Nicolas Darvas Box & Classical Geometry Tests
# -----------------------------------------------------------------------------

def test_darvas_box_consolidation_and_breakout():
    # Consolidating inside box
    data_cons = {
        "current_price": 460.0,
        "darvas_box_high": 480.0,
        "darvas_box_low": 440.0,
    }
    _, bd_c = TechnicalBaseQualityEngine.score(data_cons)
    assert bd_c["darvas_box_classical"]["darvas_state"] == "CONSOLIDATING_INSIDE_BOX"
    assert bd_c["darvas_box_classical"]["is_box_breakout"] is False

    # Breakout above box ceiling
    data_bo = {
        "current_price": 495.0,
        "darvas_box_high": 480.0,
        "darvas_box_low": 440.0,
    }
    _, bd_b = TechnicalBaseQualityEngine.score(data_bo)
    assert bd_b["darvas_box_classical"]["darvas_state"] == "DARVAS_BOX_BREAKOUT_STAGE2"
    assert bd_b["darvas_box_classical"]["is_box_breakout"] is True
    assert bd_b["darvas_box_classical"]["box_invalidation_level"] == round(480.0 * 0.99, 2)


# -----------------------------------------------------------------------------
# 4. Stan Weinstein Mansfield Relative Strength Tests
# -----------------------------------------------------------------------------

def test_mansfield_relative_strength_ratio():
    # Direct ratio series
    stock_prices = [100.0, 102.0, 105.0, 108.0, 115.0]
    bench_prices = [100.0, 100.5, 101.0, 101.2, 102.0]
    data = {
        "stock_prices": stock_prices,
        "benchmark_prices": bench_prices,
    }
    _, bd = TechnicalBaseQualityEngine.score(data)
    mrs = bd["mansfield_relative_strength"]
    assert mrs["is_outperforming"] is True
    assert mrs["mansfield_rs"] > 0.0
    assert mrs["rs_regime"] == "OUTPERFORMING_BENCHMARK"


# -----------------------------------------------------------------------------
# 5. Jesse Livermore Pivotal Point & Bull Trap Tests
# -----------------------------------------------------------------------------

def test_livermore_pivot_bull_trap_overextended():
    # Price > 15% above 20 DMA
    data = {
        "current_price": 125.0,
        "dma_20": 100.0,
        "high_52w": 126.0,
        "breakout_volume_mult": 2.5,
    }
    _, bd = TechnicalBaseQualityEngine.score(data)
    guard = bd["livermore_pivot_guard"]
    assert guard["is_overextended"] is True
    assert guard["bull_trap_warning"] is True
    assert "OVEREXTENDED_PIVOT_EXHAUSTION" in guard["trap_reason"]
    assert guard["livermore_score"] == 0.25


def test_livermore_pivot_bull_trap_volume_collapse():
    # Breaking out near 52W high on pathetic 0.7x volume
    data = {
        "current_price": 105.0,
        "dma_20": 100.0,
        "high_52w": 106.0,
        "breakout_volume_mult": 0.7,
        "volume_z_score": -0.5,
    }
    _, bd = TechnicalBaseQualityEngine.score(data)
    guard = bd["livermore_pivot_guard"]
    assert guard["is_low_volume_trap"] is True
    assert guard["bull_trap_warning"] is True
    assert "LOW_VOLUME_BULL_TRAP" in guard["trap_reason"]


def test_livermore_clean_institutional_pivot():
    # Clean breakout: near 52W high, not overextended (+6%), volume expanded 2.2x
    data = {
        "current_price": 106.0,
        "dma_20": 100.0,
        "high_52w": 108.0,
        "breakout_volume_mult": 2.2,
        "volume_z_score": 1.8,
    }
    _, bd = TechnicalBaseQualityEngine.score(data)
    guard = bd["livermore_pivot_guard"]
    assert guard["bull_trap_warning"] is False
    assert guard["livermore_score"] == 1.00


# -----------------------------------------------------------------------------
# 6. Composite Formula Invariance & Enriched Breakdown
# -----------------------------------------------------------------------------

def test_tbqe_composite_backwards_compatibility():
    data = {
        "current_price": 100.0,
        "dma_50": 90.0,
        "dma_200": 80.0,
        "high_52w": 102.0,
        "low_52w": 60.0,
        "base_length_weeks": 20,
        "volume_z_score": 1.5,
        "delivery_turnover_5d": 2.0,
    }
    comp, bd = TechnicalBaseQualityEngine.score(data)
    assert 0.0 <= comp <= 1.0
    assert 0.0 <= bd["institutional_footprint_score"] <= 1.0
    # Check all Phase 163 keys exist in breakdown
    assert "nison_candlestick" in bd
    assert "wyckoff_market_mechanics" in bd
    assert "darvas_box_classical" in bd
    assert "mansfield_relative_strength" in bd
    assert "livermore_pivot_guard" in bd
    assert "master_pattern_score" in bd
    assert 0.0 <= bd["master_pattern_score"] <= 1.0
    assert "structural_invalidation_stop" in bd
    assert bd["structural_invalidation_stop"] < data["current_price"]


# -----------------------------------------------------------------------------
# 7. Self-Learning Engine Dynamic Registry Tests
# -----------------------------------------------------------------------------

def test_self_learning_phase163_candidate_patterns():
    engine = SelfLearningEngine()
    gaps = engine.detect_knowledge_gaps(
        "Stan Weinstein Mansfield relative strength Stage 2 breakout with Wyckoff spring and Darvas box"
    )
    eids = [g["entity_id"] for g in gaps]
    assert "WEINSTEIN_MANSFIELD_RS" in eids
    assert "WYCKOFF_SPRING_ABSORPTION" in eids
    assert "DARVAS_BOX_GEOMETRY" in eids


def test_self_learning_phase163_certified_facts():
    engine = SelfLearningEngine()
    priors = engine.query_learned_priors(category="MARKET_MICROSTRUCTURE", min_confidence=0.70)
    p_names = [p["entity_id"] for p in priors]
    assert "WYCKOFF_SPRING_ABSORPTION" in p_names
    assert "NISON_CANDLESTICK_CONFLUENCE" in p_names
    assert "WEINSTEIN_MANSFIELD_RS" in p_names
    assert "LIVERMORE_PIVOT_EXHAUSTION_GUARD" in p_names
    assert "DARVAS_BOX_GEOMETRY" in p_names
