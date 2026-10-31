"""Phase 192 Test Suite: J.M. Hurst FLD Cycle Projection, Two-Candle Confirmation,
and Neo Wave Diametric Consolidation Engine in Technical Base Quality.
"""

import json
import os
import pytest
from app.services.research.technical_base_quality import TechnicalBaseQualityEngine


def test_hurst_fld_calculation_and_crossover():
    """Verify Hurst FLD displacement, crossover detection, and price projection."""
    # Generate 40 synthetic candles where price bounces off a trough and crosses above FLD
    candles = []
    base_p = 100.0
    for i in range(35):
        # Gradual decline to trough at index 25 (price = 85.0), then recovery
        if i <= 25:
            p = base_p - (i * 0.6)
        else:
            p = 85.0 + ((i - 25) * 1.5)
        candles.append({
            "open": p - 0.5,
            "high": p + 1.0,
            "low": p - 1.0,
            "close": p,
            "volume": 10000 + i * 200,
        })

    # Last candle pushes strongly above FLD
    candles.append({
        "open": 100.0,
        "high": 106.0,
        "low": 99.5,
        "close": 105.0,
        "volume": 35000,
    })

    data = {
        "current_price": 105.0,
        "cycle_length": 20,
        "candles": candles,
    }

    res = TechnicalBaseQualityEngine._evaluate_hurst_cycle_and_fld(data)
    assert res["cycle_length"] == 20
    assert res["half_cycle_displacement"] == 10
    assert res["fld_level"] > 0.0
    assert res["cycle_trough_price"] <= 86.0
    assert res["fld_price_target"] >= 105.0
    assert res["hurst_cycle_score"] >= 0.80
    assert res["cycle_invalidation_level"] > 0.0


def test_hurst_cycle_accumulation_zone():
    """Verify cyclical accumulation inflection window identification."""
    data = {
        "current_price": 120.0,
        "cycle_length": 54,
        "days_since_cycle_trough": 50,
        "cycle_trough_price": 110.0,
    }
    res = TechnicalBaseQualityEngine._evaluate_hurst_cycle_and_fld(data)
    assert res["is_cyclical_accumulation_zone"] is True
    assert res["cycle_phase"] == "CYCLICAL_ACCUMULATION_INFLECTION"
    assert res["hurst_cycle_score"] >= 0.85
    assert res["fld_price_target"] == round(120.0 + (120.0 - 110.0), 2)


def test_two_candle_bullish_confirmation():
    """Verify 2-candle confirmation when current close exceeds prior high."""
    candles = [
        {"open": 102.0, "high": 105.0, "low": 98.0, "close": 100.0, "volume": 1000},
        {"open": 100.5, "high": 109.0, "low": 100.0, "close": 108.0, "volume": 3000},
    ]
    data = {
        "current_price": 108.0,
        "candles": candles,
    }
    res = TechnicalBaseQualityEngine._evaluate_two_candle_confirmation(data)
    assert res["two_candle_confirmed"] is True
    assert res["is_wick_trap"] is False
    assert res["confirmation_state"] == "CONFIRMED_BULLISH_FOLLOWTHROUGH"
    assert res["prior_candle_high"] == 105.0
    assert res["two_candle_confirmation_score"] == 1.00


def test_two_candle_wick_trap_detection():
    """Verify wick trap detection when candle spikes above prior high but closes below."""
    candles = [
        {"open": 102.0, "high": 105.0, "low": 98.0, "close": 100.0, "volume": 1000},
        {"open": 101.0, "high": 107.0, "low": 100.0, "close": 103.5, "volume": 2500},
    ]
    data = {
        "current_price": 103.5,
        "candles": candles,
    }
    res = TechnicalBaseQualityEngine._evaluate_two_candle_confirmation(data)
    assert res["two_candle_confirmed"] is False
    assert res["is_wick_trap"] is True
    assert res["confirmation_state"] == "UNCONFIRMED_PREMATURE_BREAKOUT"
    assert res["two_candle_confirmation_score"] == 0.35


def test_two_candle_bearish_breakdown():
    """Verify bearish breakdown when current close drops below prior low."""
    candles = [
        {"open": 101.0, "high": 105.0, "low": 99.0, "close": 102.0, "volume": 1000},
        {"open": 101.5, "high": 102.0, "low": 94.0, "close": 96.0, "volume": 2000},
    ]
    data = {
        "current_price": 96.0,
        "candles": candles,
    }
    res = TechnicalBaseQualityEngine._evaluate_two_candle_confirmation(data)
    assert res["two_candle_confirmed"] is False
    assert res["confirmation_state"] == "CONFIRMED_BEARISH_FOLLOWTHROUGH"
    assert res["two_candle_confirmation_score"] == 0.15


def test_neowave_diametric_detection():
    """Verify 7-legged Neo Wave Diametric base maturation scoring."""
    data = {
        "current_price": 250.0,
        "diametric_legs_count": 7,
        "base_length_weeks": 10.0,
    }
    res = TechnicalBaseQualityEngine._detect_neowave_diametric_consolidation(data)
    assert res["neowave_pattern"] == "7_LEGGED_DIAMETRIC"
    assert res["is_diametric_mature"] is True
    assert res["diametric_coil_stage"] == "LEG_G_TERMINATION_COIL"
    assert res["neowave_score"] == 0.95
    assert res["diametric_invalidation_level"] == round(250.0 * 0.94, 2)


def test_tbqe_score_integration_and_precision():
    """Verify full integration into TechnicalBaseQualityEngine.score() with structural stops."""
    candles = [
        {"open": 100.0, "high": 103.0, "low": 97.0, "close": 99.0, "volume": 1000},
        {"open": 99.5, "high": 107.0, "low": 99.0, "close": 106.0, "volume": 5000},
    ]
    data = {
        "current_price": 106.0,
        "dma_50": 98.0,
        "dma_200": 90.0,
        "high_52w": 110.0,
        "low_52w": 75.0,
        "base_length_weeks": 12.0,
        "volume_z_score": 2.1,
        "delivery_turnover_5d": 2.4,
        "candles": candles,
        "cycle_length": 54,
        "days_since_cycle_trough": 51,
        "cycle_trough_price": 95.0,
        "diametric_legs_count": 7,
    }

    composite, breakdown = TechnicalBaseQualityEngine.score(data)

    assert 0.0 <= composite <= 1.0
    assert "hurst_cycle_fld" in breakdown
    assert "two_candle_confirmation" in breakdown
    assert "neowave_diametric" in breakdown
    assert "timing_precision_score" in breakdown

    assert breakdown["two_candle_confirmation"]["two_candle_confirmed"] is True
    assert breakdown["hurst_cycle_fld"]["is_cyclical_accumulation_zone"] is True
    assert breakdown["neowave_diametric"]["is_diametric_mature"] is True
    assert 0.0 <= breakdown["timing_precision_score"] <= 1.0
    assert breakdown["structural_invalidation_stop"] < 106.0
    assert breakdown["structural_invalidation_stop"] > 0.0


def test_dynamic_knowledge_entities_phase192():
    """Verify Entities #54 and #55 are certified in learned_rules_registry.json."""
    registry_path = os.path.join("data", "dynamic_knowledge", "learned_rules_registry.json")
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    entities = registry.get("entities", {})
    assert "HURST_FLD_CYCLE_PROJECTION_RULE" in entities
    assert "TWO_CANDLE_CONFIRMATION_RULE" in entities

    hurst_rule = entities["HURST_FLD_CYCLE_PROJECTION_RULE"]
    assert hurst_rule["verification_status"] == "CERTIFIED_FACT"
    assert hurst_rule["confidence_score"] == 0.98

    two_candle_rule = entities["TWO_CANDLE_CONFIRMATION_RULE"]
    assert two_candle_rule["verification_status"] == "CERTIFIED_FACT"
    assert two_candle_rule["confidence_score"] == 0.99

    assert registry.get("total_entities_count") >= 55
