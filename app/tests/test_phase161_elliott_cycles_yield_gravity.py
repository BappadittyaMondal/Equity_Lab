"""
Phase 161 Test Suite
====================
Institutional Multi-Optics Validation:
  1. TechnicalBaseQualityEngine Elliott Wave & Cycle Invalidation:
     - Explicit Wave 3 vs Wave 5 overrides with exact invalidation levels
     - 5-bar candle pattern: fresh early Wave 3 impulse vs late Wave 5 exhaustion
     - Stage 2 non-candle volume divergence detection (Wave 3 vs Wave 5)
     - Stage 4 / ABC corrective cycle detection
  2. TBQE Contract & Multiplicative Invariance:
     - Verifies backward compatibility of composite score (W_STAGE, W_VCP, W_BASE, W_OBV)
     - Verifies presence of elliott_wave_cycle and enriched institutional_footprint_score (0.30 SMC + 0.25 VSA + 0.25 VT + 0.20 EW)
  3. Reverse-DCF Macro Sovereign Yield Gravity:
     - PE ceiling compression when sovereign bond yield > 8.0%
     - Multiples compression comparison between high-yield and normal macro environments
  4. Dividend Yield Capital Erosion Trap Guard:
     - Flags high dividend yield (>= 10%) unbacked by cash flows (CFO/PAT < 0.50)
     - Disqualifies capital traps from multibagger candidacy
  5. SelfLearningEngine Phase 161 Knowledge Expansion:
     - KEDIANOMICS_WAVE_EQUILIBRIUM candidate gap detection
     - DIVIDEND_YIELD_CAPITAL_TRAP candidate gap detection
     - Epistemic entity verification and persistence
"""

import os
import pytest
from app.services.research.technical_base_quality import TechnicalBaseQualityEngine
from app.services.research.return_ceiling import compute_return_ceiling
from app.services.research.self_learning_engine import SelfLearningEngine


# =============================================================================
# 1. Elliott Wave & Cycle Detection Tests
# =============================================================================

def test_tbqe_elliott_wave_explicit_wave3():
    """Verifies explicit Wave 3 input produces EARLIEST_IMPULSE alert and maximum stage score."""
    data = {
        "current_price": 500.0,
        "wave_label": "WAVE_3_IMPULSE",
        "wave_invalidation_level": 460.0,
    }
    res = TechnicalBaseQualityEngine._detect_elliott_wave_and_cycles(data)
    assert res["wave_label"] == "WAVE_3_IMPULSE"
    assert res["wave_maturity_alert"] == "EARLIEST_IMPULSE"
    assert res["wave_invalidation_level"] == 460.0
    assert res["wave_stage_score"] == 1.0


def test_tbqe_elliott_wave_explicit_wave5():
    """Verifies explicit Wave 5 input produces LATE_CYCLE_EXHAUSTION_WARNING and discounted stage score."""
    data = {
        "current_price": 1000.0,
        "wave_label": "WAVE_5_TERMINATING",
    }
    res = TechnicalBaseQualityEngine._detect_elliott_wave_and_cycles(data)
    assert res["wave_label"] == "WAVE_5_TERMINATING"
    assert res["wave_maturity_alert"] == "LATE_CYCLE_EXHAUSTION_WARNING"
    assert res["wave_invalidation_level"] == 920.0  # Default 0.92 * price
    assert res["wave_stage_score"] == 0.40


def test_tbqe_elliott_wave_candles_wave3_impulse():
    """Verifies 5-bar candle sequence detects Wave 3 when recent highs expand on expanding volume."""
    # 5 bars:
    # Bars 0, 1: Highs 100, 102, Volume 1000, 1200 (prior vol ~ 1100)
    # Bars 2, 3, 4: Highs 105, 110, 115, Volume 2500, 3000, 3500 (recent vol ~ 3000 > prior vol)
    # lows: [95, 96, 101, 106, 111] -> min low[-5:] = 95.0
    data = {
        "current_price": 114.0,
        "dma_50": 100.0,
        "dma_200": 90.0,
        "candles": [
            {"open": 98.0, "high": 100.0, "low": 95.0, "close": 99.0, "volume": 1000},
            {"open": 99.0, "high": 102.0, "low": 96.0, "close": 101.0, "volume": 1200},
            {"open": 101.0, "high": 105.0, "low": 101.0, "close": 104.0, "volume": 2500},
            {"open": 104.0, "high": 110.0, "low": 106.0, "close": 109.0, "volume": 3000},
            {"open": 109.0, "high": 115.0, "low": 111.0, "close": 114.0, "volume": 3500},
        ],
    }
    res = TechnicalBaseQualityEngine._detect_elliott_wave_and_cycles(data)
    assert res["wave_label"] == "WAVE_3_IMPULSE"
    assert res["wave_maturity_alert"] == "EARLIEST_IMPULSE"
    assert res["wave_stage_score"] == 1.00
    assert res["wave_invalidation_level"] == 95.0


def test_tbqe_elliott_wave_candles_wave5_exhaustion():
    """Verifies 5-bar candle sequence detects Wave 5 exhaustion when recent highs occur on dry volume (<70% of prior)."""
    # Bars 0, 1: Highs 100, 105, Volume 4000, 5000 (prior vol ~ 4500)
    # Bars 2, 3, 4: Highs 106, 108, 110, Volume 1000, 900, 1100 (recent vol ~ 1000 < 0.70 * 4500)
    # lows: [95, 98, 102, 104, 107] -> min low[-3:] = 102.0
    data = {
        "current_price": 109.0,
        "dma_50": 98.0,
        "dma_200": 85.0,
        "candles": [
            {"open": 96.0, "high": 100.0, "low": 95.0, "close": 99.0, "volume": 4000},
            {"open": 99.0, "high": 105.0, "low": 98.0, "close": 104.0, "volume": 5000},
            {"open": 104.0, "high": 106.0, "low": 102.0, "close": 105.0, "volume": 1000},
            {"open": 105.0, "high": 108.0, "low": 104.0, "close": 107.0, "volume": 900},
            {"open": 107.0, "high": 110.0, "low": 107.0, "close": 109.0, "volume": 1100},
        ],
    }
    res = TechnicalBaseQualityEngine._detect_elliott_wave_and_cycles(data)
    assert res["wave_label"] == "WAVE_5_TERMINATING"
    assert res["wave_maturity_alert"] == "LATE_CYCLE_EXHAUSTION_WARNING"
    assert res["wave_stage_score"] == 0.40
    assert res["wave_invalidation_level"] == 102.0


def test_tbqe_elliott_wave_non_candle_stage2_indicators():
    """Verifies Stage 2 indicator logic when candles array is absent."""
    # Wave 3 impulse: Stage 2 + near 52W high (<5%) + high volume (vol_z >= 1.5)
    data_w3 = {
        "current_price": 195.0,
        "high_52w": 200.0,
        "low_52w": 110.0,
        "dma_50": 170.0,
        "dma_200": 140.0,
        "vol_z": 2.2,
    }
    res_w3 = TechnicalBaseQualityEngine._detect_elliott_wave_and_cycles(data_w3)
    assert res_w3["wave_label"] == "WAVE_3_IMPULSE"
    assert res_w3["wave_maturity_alert"] == "EARLIEST_IMPULSE"
    assert res_w3["wave_stage_score"] == 1.00
    assert res_w3["wave_invalidation_level"] == 170.0  # dma_50

    # Wave 5 exhaustion: Stage 2 + near 52W high (<5%) + volume drying up (vol_z < 0)
    data_w5 = {
        "current_price": 198.0,
        "high_52w": 200.0,
        "low_52w": 110.0,
        "dma_50": 170.0,
        "dma_200": 140.0,
        "vol_z": -0.8,
    }
    res_w5 = TechnicalBaseQualityEngine._detect_elliott_wave_and_cycles(data_w5)
    assert res_w5["wave_label"] == "WAVE_5_TERMINATING"
    assert res_w5["wave_maturity_alert"] == "LATE_CYCLE_EXHAUSTION_WARNING"
    assert res_w5["wave_stage_score"] == 0.40


def test_tbqe_elliott_wave_abc_correction():
    """Verifies downtrend below 50 & 200 DMA is classified as ABC_CORRECTIVE_CYCLE."""
    data_abc = {
        "current_price": 80.0,
        "dma_50": 95.0,
        "dma_200": 110.0,
        "high_52w": 150.0,
        "low_52w": 75.0,
    }
    res_abc = TechnicalBaseQualityEngine._detect_elliott_wave_and_cycles(data_abc)
    assert res_abc["wave_label"] == "ABC_CORRECTIVE_CYCLE"
    assert res_abc["wave_maturity_alert"] == "CORRECTION_RISK"
    assert res_abc["wave_stage_score"] == 0.20
    assert res_abc["wave_invalidation_level"] == 110.0  # dma_200


# =============================================================================
# 2. TBQE Contract & Multi-Optics Footprint Tests
# =============================================================================

def test_tbqe_score_contract_and_breakdown():
    """Verifies all 12 keys exist in breakdown and composite/footprint calculations are exact."""
    data = {
        "current_price": 250.0,
        "dma_50": 230.0,
        "dma_200": 200.0,
        "high_52w": 260.0,
        "low_52w": 140.0,
        "base_length_weeks": 12,
        "vol_z": 1.8,
        "delivery_turnover_5d": 1.4,
        "order_block_retest": True,
        "absorption_volume": True,
        "rs_rating": 85.0,
        "volume_expansion_ratio": 2.5,
    }
    composite, bd = TechnicalBaseQualityEngine.score(data)

    # 1. Verify all required keys
    expected_keys = [
        "weinstein_stage",
        "stage_score",
        "vcp_score",
        "base_length_score",
        "obv_divergence_score",
        "composite_base_quality",
        "readiness_label",
        "smc_signals",
        "vsa_signals",
        "vijay_thakkar_momentum",
        "elliott_wave_cycle",
        "institutional_footprint_score",
    ]
    for k in expected_keys:
        assert k in bd, f"Missing key in breakdown: {k}"

    # 2. Verify legacy composite formula preservation
    expected_composite = round(
        TechnicalBaseQualityEngine.W_STAGE * bd["stage_score"]
        + TechnicalBaseQualityEngine.W_VCP * bd["vcp_score"]
        + TechnicalBaseQualityEngine.W_BASE * bd["base_length_score"]
        + TechnicalBaseQualityEngine.W_OBV * bd["obv_divergence_score"],
        4,
    )
    assert composite == expected_composite
    assert bd["composite_base_quality"] == composite

    # 3. Verify institutional footprint score formula: 0.30 SMC + 0.25 VSA + 0.25 VT + 0.20 EW
    smc_s = bd["smc_signals"]["smc_score"]
    vsa_s = bd["vsa_signals"]["vsa_score"]
    vt_s = bd["vijay_thakkar_momentum"]["vt_momentum_score"]
    ew_s = bd["elliott_wave_cycle"]["wave_stage_score"]
    expected_footprint = round(0.30 * smc_s + 0.25 * vsa_s + 0.25 * vt_s + 0.20 * ew_s, 4)
    assert bd["institutional_footprint_score"] == expected_footprint


# =============================================================================
# 3. Sovereign Yield Gravity Tests
# =============================================================================

def test_return_ceiling_normal_sovereign_yield():
    """Verifies sovereign yield <= 8.0% does not trigger gravity compression."""
    res = compute_return_ceiling(
        current_mcap_cr=2000.0,
        ttm_pat_cr=100.0,
        sovereign_yield_pct=7.1,
    )
    assert res["yield_compression_applied"] is False
    assert res["sovereign_yield_pct"] == 7.1
    # Base case uses default 18.0 terminal PE
    # Future PAT = 100 * (1.18^3) = 164.303 -> Future Mcap = 164.303 * 18.0 = 2957.46 -> multiple = 1.48
    assert res["base_multiple"] == 1.48


def test_return_ceiling_high_sovereign_yield_gravity():
    """Verifies sovereign yield > 8.0% triggers PE multiple ceiling compression."""
    # Under 9.5% sovereign yield, pe_ceiling = 100 / (9.5 + 3.0) = 8.0
    # base terminal PE compressed from 18.0 to 8.0!
    res_high_yield = compute_return_ceiling(
        current_mcap_cr=2000.0,
        ttm_pat_cr=100.0,
        sovereign_yield_pct=9.5,
    )
    assert res_high_yield["yield_compression_applied"] is True
    # Future PAT = 164.303 -> Future Mcap = 164.303 * 8.0 = 1314.43 -> multiple = 0.66
    assert res_high_yield["base_multiple"] == 0.66
    assert res_high_yield["base_multiple"] < 1.48


# =============================================================================
# 4. Dividend Yield Capital Trap Tests
# =============================================================================

def test_return_ceiling_dividend_yield_capital_trap_triggered():
    """Verifies that high dividend yield (>= 10%) with poor cash flow (CFO/PAT < 0.50) triggers trap guard."""
    res = compute_return_ceiling(
        current_mcap_cr=500.0,
        ttm_pat_cr=100.0,
        dividend_yield_pct=11.5,
        cfo_pat_ratio=0.32,
    )
    assert res["dividend_trap_warning"] is True
    assert res["label"] == "DIVIDEND_YIELD_CAPITAL_TRAP"
    assert res["multibagger_eligible"] is False


def test_return_ceiling_high_dividend_healthy_cfo_safe():
    """Verifies that high dividend backed by solid operating cash flow does NOT trigger trap."""
    res = compute_return_ceiling(
        current_mcap_cr=500.0,
        ttm_pat_cr=100.0,
        dividend_yield_pct=10.5,
        cfo_pat_ratio=0.95,  # Strong cash generation
    )
    assert res["dividend_trap_warning"] is False
    assert res["label"] != "DIVIDEND_YIELD_CAPITAL_TRAP"
    assert res["multibagger_eligible"] is True


def test_return_ceiling_low_dividend_poor_cfo_not_dividend_trap():
    """Verifies that low dividend yield with poor CFO does not get mislabeled as DIVIDEND_YIELD_CAPITAL_TRAP."""
    res = compute_return_ceiling(
        current_mcap_cr=1000.0,
        ttm_pat_cr=100.0,
        dividend_yield_pct=1.2,
        cfo_pat_ratio=0.20,
    )
    assert res["dividend_trap_warning"] is False
    assert res["label"] != "DIVIDEND_YIELD_CAPITAL_TRAP"


# =============================================================================
# 5. Self-Learning Engine Knowledge Expansion Tests
# =============================================================================

def test_self_learning_detects_phase161_candidate_patterns(tmp_path):
    """Verifies SelfLearningEngine detects Kedianomics wave equilibrium and Dividend capital trap."""
    custom_reg = os.path.join(tmp_path, "test_learned_rules.json")
    engine = SelfLearningEngine(registry_file=custom_reg)

    # 1. Kedianomics detection
    sample_text_kedia = (
        "Sushil Kedia Kedianomics framework emphasizes Elliott wave fractal hierarchy, "
        "distinguishing fresh wave 3 impulse from late wave 5 exhaustion with precise invalidation levels."
    )
    gaps_kedia = engine.detect_knowledge_gaps(sample_text_kedia)
    assert any(g["entity_id"] == "KEDIANOMICS_WAVE_EQUILIBRIUM" for g in gaps_kedia)

    # 2. Dividend Trap detection
    sample_text_div = (
        "Beware of the dividend yield trap where optically high payouts cause capital erosion trap "
        "due to unbacked dividend distributions from debt."
    )
    gaps_div = engine.detect_knowledge_gaps(sample_text_div)
    assert any(g["entity_id"] == "DIVIDEND_YIELD_CAPITAL_TRAP" for g in gaps_div)


def test_self_learning_epistemic_validation_of_phase161_concept(tmp_path):
    """Verifies zero-trust epistemic validation and registry persistence for Kedianomics concept."""
    custom_reg = os.path.join(tmp_path, "test_learned_rules.json")
    engine = SelfLearningEngine(registry_file=custom_reg)

    entity = engine.evaluate_and_learn_entity(
        entity_id="KEDIANOMICS_WAVE_EQUILIBRIUM",
        text_context="Rigorous Elliott Wave multi-fractal degree analysis by Sushil Kedia with invalidation levels.",
        source_origin="EXPERT_SESSION",
        provenance_score=0.95,
        corroboration_count=3,
    )
    assert entity.entity_id == "KEDIANOMICS_WAVE_EQUILIBRIUM"
    assert entity.verification_status == "CERTIFIED_FACT"
    assert entity.confidence_score >= 0.80
    assert "swing_10d" in entity.relevance_vector
    assert entity.bayesian_prior_modifier.get("metric") == "elliott_wave_structural_integrity"
