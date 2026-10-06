"""
Phase 149: Technical Base Quality Engine
=========================================
Formally scores the quality of a technical base/consolidation pattern for
early-stage multibagger detection.

Architecture Position
---------------------
This module is a *sub-signal enricher* for the existing TECHNICAL weight
category inside ``ARCHETYPE_WEIGHT_PROFILES`` in ``intent_adaptive_engine.py``.

It does NOT:
  - Create a new parallel scoring pipeline (that would conflict with the
    Central Decision Brain Arbiter).
  - Replace or override any of the 40 canonical engines (A1–D18, E1–E22).
  - Alter any weight profile, threshold, gate, or formula.

It DOES:
  - Formalize Weinstein Stage classification (previously implicit).
  - Score VCP (Volatility Contraction Pattern) compression mathematically.
  - Score base length in weeks (longer base = more supply absorbed).
  - Score OBV-proxy divergence (institutional accumulation footprint).
  - Return a composite score [0.0, 1.0] + explainable breakdown dict.

Zero regression risk. All existing engine logic is untouched.
"""

from typing import Any, Dict, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Composite Base Quality Score formula:
#
#   BQ = (W_stage × stage_score)
#      + (W_vcp   × vcp_score)
#      + (W_base  × base_length_score)
#      + (W_obv   × obv_score)
#
# Weights (sum = 1.0):
#   W_stage = 0.30  — Weinstein stage classification
#   W_vcp   = 0.25  — VCP compression depth
#   W_base  = 0.25  — Base length in weeks
#   W_obv   = 0.20  — OBV-proxy divergence
# ─────────────────────────────────────────────────────────────────────────────


class TechnicalBaseQualityEngine:
    """
    Scores quality of a technical base/consolidation pattern.

    Usage::

        from app.services.research.technical_base_quality import TechnicalBaseQualityEngine

        score, breakdown = TechnicalBaseQualityEngine.score(stock_data_dict)
        # score: float in [0.0, 1.0]
        # breakdown: dict with per-component scores + readiness_label

    ``score`` feeds into the existing TECHNICAL weight bucket of the intent-
    adaptive engine. It does NOT create a competing scoring system.
    """

    W_STAGE: float = 0.30
    W_VCP:   float = 0.25
    W_BASE:  float = 0.25
    W_OBV:   float = 0.20

    # Weinstein Stage → score mapping
    STAGE_SCORES: Dict[str, float] = {
        "STAGE_1_BASE":        0.85,  # Flat accumulation — ideal early setup
        "STAGE_2_EARLY":       0.90,  # Just breaking out of Stage 1
        "STAGE_2_UPTREND":     1.00,  # Confirmed markup — strongest technical
        "STAGE_3_TOPPING":     0.30,  # Distribution zone — caution
        "STAGE_4_DOWNTREND":   0.00,  # Markdown — hard technical block
        "UNKNOWN":             0.50,  # Neutral when data insufficient
    }

    @classmethod
    def _classify_weinstein_stage(cls, data: Dict[str, Any]) -> str:
        """
        Classify Weinstein Stage from price/MA data.

        Stage 1 (Base):   Price near 52W low, MA flat, tight range.
        Stage 2 (Up):     Price > 50DMA > 200DMA, MAs sloping up.
        Stage 3 (Top):    Price under 50DMA, 200DMA still elevated.
        Stage 4 (Down):   Price < 200DMA, MAs declining.

        Returns one of: STAGE_1_BASE | STAGE_2_EARLY | STAGE_2_UPTREND |
                        STAGE_3_TOPPING | STAGE_4_DOWNTREND | UNKNOWN
        """
        price    = float(data.get("current_price") or 0.0)
        dma50    = float(data.get("dma_50") or 0.0)
        dma200   = float(data.get("dma_200") or 0.0)
        high_52w = float(data.get("high_52w") or 0.0)
        low_52w  = float(data.get("low_52w") or 0.0)

        if not all([price, dma50, dma200, high_52w, low_52w]):
            return "UNKNOWN"

        range_52w = high_52w - low_52w
        if range_52w <= 0:
            return "UNKNOWN"

        price_pos = (price - low_52w) / range_52w  # 0.0 = at low, 1.0 = at high

        # Stage 2: price above both MAs in correct order
        if price > dma50 > dma200:
            return "STAGE_2_UPTREND" if price_pos >= 0.60 else "STAGE_2_EARLY"

        # Stage 1: price hugging 200DMA from below, in lower 40% of range
        if dma200 > 0 and abs(price - dma200) / dma200 < 0.08 and price_pos <= 0.40:
            return "STAGE_1_BASE"

        # Stage 4: below both MAs
        if price < dma200 and price < dma50:
            return "STAGE_4_DOWNTREND"

        # Stage 3: below 50DMA but 200DMA still elevated
        if price < dma50:
            return "STAGE_3_TOPPING"

        return "UNKNOWN"

    @classmethod
    def _score_vcp(cls, data: Dict[str, Any]) -> float:
        """
        VCP (Volatility Contraction Pattern) score: 0.0 – 1.0.

        Measures price proximity to 52W high.
        A tight VCP = price is within 0–15% of 52W high.

        Formula:
            dist_from_high = (high_52w - price) / high_52w
            vcp_score = max(0, 1.0 - dist_from_high / 0.40)

        Interpretation:
            0–5% below 52W high  → score ≈ 0.875–1.00  (very tight VCP)
            15% below 52W high   → score ≈ 0.625        (standard base)
            40%+ below 52W high  → score = 0.0          (deep correction)
        """
        price    = float(data.get("current_price") or 0.0)
        high_52w = float(data.get("high_52w") or 0.0)

        if not (price and high_52w > 0):
            return 0.50  # Neutral when data unavailable

        dist = (high_52w - price) / high_52w
        return round(max(0.0, min(1.0, 1.0 - dist / 0.40)), 4)

    @classmethod
    def _score_base_length(cls, data: Dict[str, Any]) -> float:
        """
        Base length score: 0.0 – 1.0.

        Longer flat bases → more supply absorbed → more violent eventual breakout.

        If ``base_length_weeks`` is directly provided in data:
            score = max(0, min(1, (weeks - 4) / 48))
            → 0 at 4 weeks, 1.0 at 52 weeks+

        If not available, infers from 52W range compression:
            compression = (high_52w - low_52w) / high_52w
            → tight range (<25%) suggests a long flat base
            inferred_score = max(0, 1 - compression / 0.60)
        """
        base_weeks = data.get("base_length_weeks") or data.get("base_length_w")
        if base_weeks is not None:
            return round(max(0.0, min(1.0, (float(base_weeks) - 4.0) / 48.0)), 4)

        high_52w = float(data.get("high_52w") or 0.0)
        low_52w  = float(data.get("low_52w") or 0.0)
        if high_52w > 0:
            compression = (high_52w - low_52w) / high_52w
            return round(max(0.0, 1.0 - compression / 0.60), 4)

        return 0.50  # Neutral when data unavailable

    @classmethod
    def _score_obv_divergence(cls, data: Dict[str, Any]) -> float:
        """
        OBV Divergence score: 0.0 – 1.0.

        The most reliable accumulation signal: OBV rising while price is
        flat or slightly declining. Proxy uses vol_z and delivery_turnover.

        Score breakdown:
            Base score                               = 0.50 (neutral)
            + 0.25 if vol_z >= 1.0 AND price in lower 50% of 52W range
                    (volume surge inside a base = institutional accumulation)
            + 0.25 if delivery_turnover >= 1.5%
                    (India-specific: high delivery % = real buying, not churning)
            - 0.25 if vol_z < 0.0 (volume collapse = distribution warning)

        Keys used from data:
            volume_z_score / vol_z          — volume Z-score vs 90D average
            delivery_turnover_5d / delivery_turnover — delivery % (India NSE)
            current_price, high_52w, low_52w
        """
        vol_z    = data.get("volume_z_score") or data.get("vol_z")
        delivery = data.get("delivery_turnover_5d") or data.get("delivery_turnover")
        price    = float(data.get("current_price") or 0.0)
        high_52w = float(data.get("high_52w") or 0.0)
        low_52w  = float(data.get("low_52w") or 0.0)

        score = 0.50
        if vol_z is not None:
            vol_z_f   = float(vol_z)
            range_52w = (high_52w - low_52w) if high_52w else 0.0
            price_pos = ((price - low_52w) / range_52w) if range_52w > 0 else 0.5
            if vol_z_f >= 1.0 and price_pos <= 0.50:
                score += 0.25   # Accumulation signal
            elif vol_z_f < 0.0:
                score -= 0.25   # Distribution warning
        if delivery is not None and float(delivery) >= 1.5:
            score += 0.25       # India delivery-based accumulation confirmed

        return round(max(0.0, min(1.0, score)), 4)

    @classmethod
    def _detect_smc_order_block_and_fvg(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detects Smart Money Concepts (SMC) features: Fair Value Gaps (FVG),
        Institutional Order Blocks (OB), and Liquidity Sweeps.
        """
        fvg_detected = bool(data.get("fvg_detected") or data.get("fvg_present"))
        fvg_gap_size = float(data.get("fvg_gap_size") or 0.0)
        ob_detected = bool(data.get("order_block_detected") or data.get("order_block_present") or data.get("order_block_retest"))
        sweep_detected = bool(data.get("liquidity_sweep_detected") or data.get("liquidity_sweep_present") or data.get("liquidity_sweep"))

        candles = data.get("candles") or data.get("bars") or data.get("recent_candles") or []
        if isinstance(candles, list) and len(candles) >= 2:
            # 1. 3-bar Fair Value Gap (Bullish)
            if len(candles) >= 3:
                for i in range(2, len(candles)):
                    c0 = candles[i-2]
                    c2 = candles[i]
                    if isinstance(c0, dict) and isinstance(c2, dict):
                        h0 = float(c0.get("high") or 0.0)
                        l2 = float(c2.get("low") or 0.0)
                        if l2 > h0 and h0 > 0:
                            fvg_detected = True
                            fvg_gap_size = max(fvg_gap_size, round(l2 - h0, 2))

            # 2. Institutional Order Block (last down-candle before expansion)
            for i in range(1, len(candles)):
                prev = candles[i-1]
                curr = candles[i]
                if isinstance(prev, dict) and isinstance(curr, dict):
                    prev_c = float(prev.get("close") or 0.0)
                    prev_o = float(prev.get("open") or 0.0)
                    curr_c = float(curr.get("close") or 0.0)
                    curr_o = float(curr.get("open") or 0.0)
                    curr_v = float(curr.get("volume") or 0.0)
                    prev_v = float(prev.get("volume") or 1.0)
                    if prev_c < prev_o and curr_c > curr_o and curr_c > prev_o and (curr_v > 1.5 * prev_v or curr_v > 0):
                        ob_detected = True

            # 3. Liquidity Sweep (sweep below prior low, close back above)
            for i in range(1, len(candles)):
                prev = candles[i-1]
                curr = candles[i]
                if isinstance(prev, dict) and isinstance(curr, dict):
                    prev_l = float(prev.get("low") or 0.0)
                    curr_l = float(curr.get("low") or 0.0)
                    curr_c = float(curr.get("close") or 0.0)
                    if curr_l < prev_l and curr_c > prev_l and prev_l > 0:
                        sweep_detected = True

        smc_score = 0.50
        if fvg_detected:
            smc_score += 0.20
        if ob_detected:
            smc_score += 0.20
        if sweep_detected:
            smc_score += 0.10
        smc_score = min(1.0, smc_score)

        return {
            "fvg_detected": fvg_detected,
            "fvg_gap_size": fvg_gap_size,
            "order_block_detected": ob_detected,
            "liquidity_sweep_detected": sweep_detected,
            "smc_score": round(smc_score, 4),
        }

    @classmethod
    def _detect_vsa_absorption(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detects Volume Spread Analysis (VSA) states: Absorption Volume,
        Volume Dry-Up (Supply Exhaustion), and Climax Distribution warnings.
        """
        vol_z = data.get("volume_z_score") or data.get("vol_z")
        vol_z_f = float(vol_z) if vol_z is not None else 0.0

        is_dry_up = bool(data.get("volume_dry_up") or (vol_z is not None and vol_z_f <= -0.5))
        is_absorption = bool(data.get("absorption_volume") or (vol_z is not None and vol_z_f >= 1.5))
        is_climax = bool(vol_z is not None and vol_z_f >= 3.5 and data.get("climax_warning"))

        if is_climax:
            vsa_state = "CLIMAX_DISTRIBUTION"
            vsa_score = 0.20
        elif is_absorption:
            vsa_state = "ABSORPTION"
            vsa_score = 0.90
        elif is_dry_up:
            vsa_state = "DRY_UP"
            vsa_score = 0.85
        else:
            vsa_state = "NEUTRAL"
            vsa_score = 0.50

        return {
            "volume_dry_up": is_dry_up,
            "absorption_volume": is_absorption,
            "climax_distribution_warning": is_climax,
            "vsa_state": vsa_state,
            "vsa_score": round(vsa_score, 4),
        }

    @classmethod
    def _detect_vijay_thakkar_momentum(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates Vijay Thakkar Stage 2 Pure Price-Volume Momentum criteria:
        1. Within 15% of 52W High (buying market leaders, zero bottom fishing).
        2. Price > 50 DMA > 200 DMA (Stage 2 alignment).
        3. Breakout volume expansion >= 2.0x 20-day average volume.
        4. Relative Strength outperformance vs benchmark.
        """
        price = float(data.get("current_price") or 0.0)
        high_52w = float(data.get("high_52w") or 0.0)
        dma50 = float(data.get("dma_50") or 0.0)
        dma200 = float(data.get("dma_200") or 0.0)
        vol_mult = float(data.get("breakout_volume_mult") or data.get("volume_multiple") or 1.0)
        vol_z = float(data.get("volume_z_score") or data.get("vol_z") or 0.0)

        within_15pct = False
        if price > 0 and high_52w > 0:
            within_15pct = ((high_52w - price) / high_52w) <= 0.15

        stage2_ma = (price > dma50 > dma200) if (price > 0 and dma50 > 0 and dma200 > 0) else False
        vol_expanded = (vol_mult >= 2.0 or vol_z >= 1.5)
        rs_outperforming = bool(data.get("rs_outperforming") or float(data.get("rs_rating") or 50.0) >= 70.0 or float(data.get("mansfield_rs") or 0.0) > 0.0)

        vt_pass = within_15pct and stage2_ma and (vol_expanded or rs_outperforming)
        vt_score = 0.50
        if vt_pass:
            vt_score = 1.00
        elif within_15pct and stage2_ma:
            vt_score = 0.80
        elif within_15pct:
            vt_score = 0.65

        return {
            "within_52w_high_15pct": within_15pct,
            "stage2_ma_aligned": stage2_ma,
            "volume_expansion_confirmed": vol_expanded,
            "relative_strength_outperforming": rs_outperforming,
            "vijay_thakkar_momentum_pass": vt_pass,
            "vt_momentum_score": round(vt_score, 4),
        }

    @classmethod
    def score(cls, data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Main entry point.

        Args:
            data: dict containing any subset of: current_price, dma_50,
                  dma_200, high_52w, low_52w, base_length_weeks,
                  volume_z_score / vol_z, delivery_turnover_5d.
                  Missing fields default to neutral (0.50 sub-score).

        Returns:
            Tuple of:
              - composite (float): Base Quality Score in [0.0, 1.0]
              - breakdown (dict): per-component scores + readiness_label
        """
        stage_label = cls._classify_weinstein_stage(data)
        stage_score = cls.STAGE_SCORES.get(stage_label, 0.50)
        vcp_score   = cls._score_vcp(data)
        base_score  = cls._score_base_length(data)
        obv_score   = cls._score_obv_divergence(data)

        composite = round(
            cls.W_STAGE * stage_score
            + cls.W_VCP  * vcp_score
            + cls.W_BASE * base_score
            + cls.W_OBV  * obv_score,
            4,
        )

        # Enriched Multi-Optics sub-detectors
        smc_res = cls._detect_smc_order_block_and_fvg(data)
        vsa_res = cls._detect_vsa_absorption(data)
        vt_res  = cls._detect_vijay_thakkar_momentum(data)

        footprint_score = round(
            0.40 * smc_res["smc_score"]
            + 0.30 * vsa_res["vsa_score"]
            + 0.30 * vt_res["vt_momentum_score"],
            4,
        )

        if composite >= 0.80:
            readiness = "STRONG_BASE_SETUP"
        elif composite >= 0.65:
            readiness = "FORMING_BASE"
        elif composite >= 0.50:
            readiness = "NEUTRAL"
        elif composite >= 0.35:
            readiness = "WEAK_STRUCTURE"
        else:
            readiness = "DISTRIBUTION_OR_DOWNTREND"

        breakdown: Dict[str, Any] = {
            "weinstein_stage":              stage_label,
            "stage_score":                  stage_score,
            "vcp_score":                    vcp_score,
            "base_length_score":            base_score,
            "obv_divergence_score":         obv_score,
            "composite_base_quality":       composite,
            "readiness_label":              readiness,
            "smc_signals":                  smc_res,
            "vsa_signals":                  vsa_res,
            "vijay_thakkar_momentum":       vt_res,
            "institutional_footprint_score": footprint_score,
        }
        return composite, breakdown
