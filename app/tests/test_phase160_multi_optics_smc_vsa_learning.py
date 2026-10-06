"""
Phase 160 Test Suite
====================
Tests for:
  1. TechnicalBaseQualityEngine Multi-Optics SMC Detection:
     - Fair Value Gap (FVG) 3-bar detection
     - Institutional Order Block (OB) identification
     - Liquidity Sweep verification
  2. Volume Spread Analysis (VSA) Detection:
     - Absorption Volume detection
     - Volume Dry-Up (Supply Exhaustion)
     - Climax Distribution warnings
  3. Vijay Thakkar Stage 2 Pure Price-Volume Momentum System:
     - Within 15% of 52W High constraint
     - Price > 50 DMA > 200 DMA Stage 2 moving average structure
     - Breakout volume expansion (>= 2.0x) & Relative Strength outperformance
  4. Institutional Footprint Score & Breakdown Contract:
     - Verifies backward compatibility of composite score and all 7 legacy keys
     - Verifies presence of smc_signals, vsa_signals, vijay_thakkar_momentum, institutional_footprint_score
  5. SelfLearningEngine Phase 160 Pattern Recognition:
     - AI_DATACENTER_OPTICAL_FIBER
     - EMS_DEFENSE_CAPEX_INFLECTION
     - SOVEREIGN_DEBT_FISCAL_DOMINANCE
     - VIJAY_THAKKAR_STAGE2_MOMENTUM
     - SMC_ORDER_BLOCK_FVG_CONFLUENCE
"""

import pytest
from app.services.research.technical_base_quality import TechnicalBaseQualityEngine
from app.services.research.self_learning_engine import SelfLearningEngine


# =============================================================================
# 1. SMC Detection Tests
# =============================================================================

def test_tbqe_smc_fvg_detection():
    """Verifies that 3-bar Bullish Fair Value Gap (FVG) is detected correctly."""
    # Synthetic candles:
    # Bar 0: high = 100.0, low = 95.0
    # Bar 1: high = 106.0, low = 101.0 (displacement bar)
    # Bar 2: low = 103.0, high = 108.0 (gap between Bar 0 high 100.0 and Bar 2 low 103.0 is 3.0)
    data = {
        "candles": [
            {"open": 96.0, "high": 100.0, "low": 95.0, "close": 98.0, "volume": 1000},
            {"open": 98.0, "high": 106.0, "low": 101.0, "close": 105.0, "volume": 5000},
            {"open": 105.0, "high": 108.0, "low": 103.0, "close": 107.0, "volume": 2000},
        ]
    }
    res = TechnicalBaseQualityEngine._detect_smc_order_block_and_fvg(data)
    assert res["fvg_detected"] is True
    assert res["fvg_gap_size"] == 3.0
    assert res["smc_score"] >= 0.70


def test_tbqe_smc_order_block_and_sweep():
    """Verifies that Institutional Order Block and Liquidity Sweep are detected."""
    # Bar 0: Bearish down-candle (open 100, close 92, low 90, vol 1000)
    # Bar 1: Bullish engulfing expansion bar (low 89 < 90 sweep, open 91, close 102 > 100, vol 2500 > 1.5x)
    data = {
        "candles": [
            {"open": 100.0, "high": 101.0, "low": 90.0, "close": 92.0, "volume": 1000},
            {"open": 91.0, "high": 103.0, "low": 89.0, "close": 102.0, "volume": 2500},
        ]
    }
    res = TechnicalBaseQualityEngine._detect_smc_order_block_and_fvg(data)
    assert res["order_block_detected"] is True
    assert res["liquidity_sweep_detected"] is True
    assert res["smc_score"] >= 0.80


def test_tbqe_smc_explicit_flags():
    """Verifies explicit flags are honored even without raw candle arrays."""
    data = {
        "fvg_present": True,
        "fvg_gap_size": 4.5,
        "order_block_retest": True,
        "liquidity_sweep": True,
    }
    res = TechnicalBaseQualityEngine._detect_smc_order_block_and_fvg(data)
    assert res["fvg_detected"] is True
    assert res["fvg_gap_size"] == 4.5
    assert res["order_block_detected"] is True
    assert res["liquidity_sweep_detected"] is True
    assert res["smc_score"] == 1.0


# =============================================================================
# 2. VSA Detection Tests
# =============================================================================

def test_tbqe_vsa_absorption_volume():
    """Verifies Absorption Volume detection from high vol_z or explicit flag."""
    data = {"vol_z": 2.2, "absorption_volume": True}
    res = TechnicalBaseQualityEngine._detect_vsa_absorption(data)
    assert res["vsa_state"] == "ABSORPTION"
    assert res["absorption_volume"] is True
    assert res["vsa_score"] == 0.90


def test_tbqe_vsa_volume_dry_up():
    """Verifies Volume Dry-Up (Supply Exhaustion) detection."""
    data = {"volume_z_score": -0.8}
    res = TechnicalBaseQualityEngine._detect_vsa_absorption(data)
    assert res["vsa_state"] == "DRY_UP"
    assert res["volume_dry_up"] is True
    assert res["vsa_score"] == 0.85


def test_tbqe_vsa_climax_distribution():
    """Verifies Climax Distribution warning when extreme volume meets warning flag."""
    data = {"vol_z": 4.0, "climax_warning": True}
    res = TechnicalBaseQualityEngine._detect_vsa_absorption(data)
    assert res["vsa_state"] == "CLIMAX_DISTRIBUTION"
    assert res["climax_distribution_warning"] is True
    assert res["vsa_score"] == 0.20


def test_tbqe_vsa_neutral_default():
    """Verifies neutral fallback when no volume anomalies exist."""
    data = {"vol_z": 0.1}
    res = TechnicalBaseQualityEngine._detect_vsa_absorption(data)
    assert res["vsa_state"] == "NEUTRAL"
    assert res["vsa_score"] == 0.50


# =============================================================================
# 3. Vijay Thakkar Momentum Tests
# =============================================================================

def test_tbqe_vijay_thakkar_momentum_full_pass():
    """Verifies full pass for Vijay Thakkar Stage 2 criteria."""
    data = {
        "current_price": 490.0,
        "high_52w": 500.0,        # 2% from 52W High (<= 15%)
        "dma_50": 450.0,
        "dma_200": 400.0,         # Price (490) > DMA50 (450) > DMA200 (400)
        "breakout_volume_mult": 2.8,  # >= 2.0x
        "mansfield_rs": 2.4,      # RS outperforming
    }
    res = TechnicalBaseQualityEngine._detect_vijay_thakkar_momentum(data)
    assert res["within_52w_high_15pct"] is True
    assert res["stage2_ma_aligned"] is True
    assert res["volume_expansion_confirmed"] is True
    assert res["relative_strength_outperforming"] is True
    assert res["vijay_thakkar_momentum_pass"] is True
    assert res["vt_momentum_score"] == 1.0


def test_tbqe_vijay_thakkar_momentum_fail_distance():
    """Verifies that stocks deeper than 15% from 52W high fail Vijay Thakkar momentum."""
    data = {
        "current_price": 380.0,
        "high_52w": 500.0,        # 24% from 52W High (> 15%)
        "dma_50": 360.0,
        "dma_200": 330.0,
        "breakout_volume_mult": 3.0,
    }
    res = TechnicalBaseQualityEngine._detect_vijay_thakkar_momentum(data)
    assert res["within_52w_high_15pct"] is False
    assert res["vijay_thakkar_momentum_pass"] is False
    assert res["vt_momentum_score"] == 0.50


# =============================================================================
# 4. Composite Score & Breakdown Contract Tests
# =============================================================================

def test_tbqe_composite_contract_preservation():
    """Verifies that score() returns composite and all legacy + Phase 160 keys."""
    data = {
        "current_price": 500.0,
        "dma_50": 460.0,
        "dma_200": 420.0,
        "high_52w": 510.0,
        "low_52w": 350.0,
        "base_length_weeks": 24,
        "vol_z": 1.8,
        "delivery_turnover": 2.0,
    }
    composite, breakdown = TechnicalBaseQualityEngine.score(data)

    # 1. Check legacy keys
    legacy_keys = [
        "weinstein_stage",
        "stage_score",
        "vcp_score",
        "base_length_score",
        "obv_divergence_score",
        "composite_base_quality",
        "readiness_label",
    ]
    for k in legacy_keys:
        assert k in breakdown, f"Missing legacy key: {k}"

    # 2. Check Phase 160 keys
    p160_keys = [
        "smc_signals",
        "vsa_signals",
        "vijay_thakkar_momentum",
        "institutional_footprint_score",
    ]
    for k in p160_keys:
        assert k in breakdown, f"Missing Phase 160 key: {k}"

    # 3. Check values & bounds
    assert 0.0 <= composite <= 1.0
    assert 0.0 <= breakdown["institutional_footprint_score"] <= 1.0
    assert breakdown["weinstein_stage"] == "STAGE_2_UPTREND"
    assert composite == breakdown["composite_base_quality"]


# =============================================================================
# 5. SelfLearningEngine Pattern Recognition Tests
# =============================================================================

def test_self_learning_engine_phase160_patterns_exist():
    """Verifies that all 5 new candidate patterns exist in SelfLearningEngine."""
    expected_patterns = [
        "AI_DATACENTER_OPTICAL_FIBER",
        "EMS_DEFENSE_CAPEX_INFLECTION",
        "SOVEREIGN_DEBT_FISCAL_DOMINANCE",
        "VIJAY_THAKKAR_STAGE2_MOMENTUM",
        "SMC_ORDER_BLOCK_FVG_CONFLUENCE",
    ]
    for pat in expected_patterns:
        assert pat in SelfLearningEngine.UNMAPPED_CANDIDATE_PATTERNS, f"Missing pattern: {pat}"


def test_self_learning_engine_detects_optical_fiber():
    """Verifies matching of AI_DATACENTER_OPTICAL_FIBER."""
    engine = SelfLearningEngine()
    text = "The exponential buildout of AI data center clusters is creating an optical fiber and transceiver supercycle."
    gaps = engine.detect_knowledge_gaps(text)
    matched_ids = [g["entity_id"] for g in gaps]
    assert "AI_DATACENTER_OPTICAL_FIBER" in matched_ids


def test_self_learning_engine_detects_ems_defense():
    """Verifies matching of EMS_DEFENSE_CAPEX_INFLECTION."""
    engine = SelfLearningEngine()
    text = "Significant CWIP expansion and order book-to-bill acceleration across defense indigenization players."
    gaps = engine.detect_knowledge_gaps(text)
    matched_ids = [g["entity_id"] for g in gaps]
    assert "EMS_DEFENSE_CAPEX_INFLECTION" in matched_ids


def test_self_learning_engine_detects_sovereign_debt():
    """Verifies matching of SOVEREIGN_DEBT_FISCAL_DOMINANCE."""
    engine = SelfLearningEngine()
    text = "Macro risk escalating due to sovereign debt to GDP exceeding sustainability thresholds under fiscal dominance."
    gaps = engine.detect_knowledge_gaps(text)
    matched_ids = [g["entity_id"] for g in gaps]
    assert "SOVEREIGN_DEBT_FISCAL_DOMINANCE" in matched_ids


def test_self_learning_engine_detects_vijay_thakkar():
    """Verifies matching of VIJAY_THAKKAR_STAGE2_MOMENTUM."""
    engine = SelfLearningEngine()
    text = "Focusing on Vijay Thakkar price is god volume is priest methodology with 52 week high momentum."
    gaps = engine.detect_knowledge_gaps(text)
    matched_ids = [g["entity_id"] for g in gaps]
    assert "VIJAY_THAKKAR_STAGE2_MOMENTUM" in matched_ids


def test_self_learning_engine_detects_smc_confluence():
    """Verifies matching of SMC_ORDER_BLOCK_FVG_CONFLUENCE."""
    engine = SelfLearningEngine()
    text = "Notice the fair value gap mitigation and order block liquidity sweep on the daily chart."
    gaps = engine.detect_knowledge_gaps(text)
    matched_ids = [g["entity_id"] for g in gaps]
    assert "SMC_ORDER_BLOCK_FVG_CONFLUENCE" in matched_ids

