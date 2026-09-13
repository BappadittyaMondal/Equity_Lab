"""Multimodal Technical Chart Image & Data-Truth Reconciliation Protocol (§Visual-Quant Alignment Plane).

Reconciles visual chart pattern interpretations (pixels, trendlines, breakout flags)
against underlying ground-truth numerical OHLCV tick bars.
Ensures the system never hallucinates breakouts, misidentifies false pivots,
or overrides exchange-confirmed price and volume data.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
try:
    from scipy.stats import gaussian_kde
except ImportError:
    gaussian_kde = None


class GeometricPatternDetector:
    """Algorithmic Geometric OHLCV Pattern Detection Engine.
    
    Implements Mark Minervini's Volatility Contraction Pattern (VCP),
    William O'Neil's Cup & Handle structural geometry, and
    Gaussian Kernel Density Estimation (KDE) Support/Resistance shelf clustering.
    100% deterministic mathematical execution directly on numerical bar data.
    """

    @classmethod
    def detect_kde_support_resistance(cls, df: pd.DataFrame, top_n: int = 3) -> Dict[str, Any]:
        """Calculates volume-weighted price density modes using Gaussian KDE."""
        if df is None or len(df) < 15:
            return {"support_levels": [], "resistance_levels": [], "status": "INSUFFICIENT_DATA"}

        # Normalize column names
        close_col = "close" if "close" in df.columns else "Close"
        vol_col = "volume" if "volume" in df.columns else "Volume"

        closes = df[close_col].values.astype(np.float64)
        volumes = df[vol_col].values.astype(np.float64)
        latest_close = float(closes[-1])

        if gaussian_kde is None:
            return {"support_levels": [], "resistance_levels": [], "status": "SCIPY_UNAVAILABLE"}

        try:
            kde = gaussian_kde(closes, weights=np.maximum(volumes, 1.0))
            price_grid = np.linspace(float(closes.min()) * 0.95, float(closes.max()) * 1.05, 200)
            densities = kde(price_grid)

            peaks = []
            for i in range(1, len(densities) - 1):
                if densities[i] > densities[i - 1] and densities[i] > densities[i + 1]:
                    peaks.append((price_grid[i], densities[i]))

            peaks.sort(key=lambda x: x[1], reverse=True)
            top_peaks = [round(float(p[0]), 2) for p in peaks[:top_n * 2]]

            supports = sorted([p for p in top_peaks if p < latest_close], reverse=True)[:top_n]
            resistances = sorted([p for p in top_peaks if p >= latest_close])[:top_n]

            return {
                "support_levels": supports,
                "resistance_levels": resistances,
                "primary_support": supports[0] if supports else None,
                "primary_resistance": resistances[0] if resistances else None,
                "status": "SUCCESS"
            }
        except Exception as e:
            return {"support_levels": [], "resistance_levels": [], "status": f"KDE_ERROR: {e}"}

    @classmethod
    def detect_vcp_pattern(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Detects Mark Minervini Volatility Contraction Pattern (VCP)."""
        if df is None or len(df) < 25:
            return {"is_vcp_detected": False, "reason": "Insufficient bars (minimum 25 required)"}

        close_col = "close" if "close" in df.columns else "Close"
        high_col = "high" if "high" in df.columns else "High"
        low_col = "low" if "low" in df.columns else "Low"
        vol_col = "volume" if "volume" in df.columns else "Volume"

        closes = df[close_col].values.astype(np.float64)
        highs = df[high_col].values.astype(np.float64)
        lows = df[low_col].values.astype(np.float64)
        vols = df[vol_col].values.astype(np.float64)
        latest_close = float(closes[-1])

        n = len(df)
        w1_h = float(np.max(highs[: int(n * 0.5)]))
        w1_l = float(np.min(lows[: int(n * 0.5)]))
        d1 = round((w1_h - w1_l) / max(1.0, w1_h) * 100.0, 2)

        w2_h = float(np.max(highs[int(n * 0.5): int(n * 0.8)]))
        w2_l = float(np.min(lows[int(n * 0.5): int(n * 0.8)]))
        d2 = round((w2_h - w2_l) / max(1.0, w2_h) * 100.0, 2)

        w3_h = float(np.max(highs[int(n * 0.8):]))
        w3_l = float(np.min(lows[int(n * 0.8):]))
        d3 = round((w3_h - w3_l) / max(1.0, w3_h) * 100.0, 2)

        is_contracting = (d1 > d2) and (d2 > d3 or d3 <= 10.0)

        adtv_50 = float(np.mean(vols))
        recent_vol = float(np.mean(vols[int(n * 0.8):]))
        vol_dryup = recent_vol <= (adtv_50 * 0.75)

        is_vcp = bool(is_contracting and (d1 <= 40.0) and (d3 <= 12.0))
        pivot_resistance = round(float(w3_h), 2)

        return {
            "is_vcp_detected": is_vcp,
            "contractions_count": 3,
            "contraction_depths_pct": [d1, d2, d3],
            "volume_dryup_confirmed": vol_dryup,
            "pivot_resistance": pivot_resistance,
            "volatility_decay_ratio": round(d3 / max(0.1, d1), 2),
            "status": "VCP_CONFIRMED" if (is_vcp and vol_dryup) else ("VCP_FORMING" if is_vcp else "NO_VCP")
        }

    @classmethod
    def detect_cup_and_handle(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Detects William O'Neil Cup & Handle structural geometry."""
        if df is None or len(df) < 30:
            return {"is_cup_and_handle": False, "reason": "Insufficient bars"}

        close_col = "close" if "close" in df.columns else "Close"
        closes = df[close_col].values.astype(np.float64)
        n = len(df)

        cup_part = closes[: int(n * 0.8)]
        handle_part = closes[int(n * 0.8):]

        cup_high = float(np.max(cup_part))
        cup_low = float(np.min(cup_part))
        cup_depth_pct = round((cup_high - cup_low) / max(1.0, cup_high) * 100.0, 2)

        handle_high = float(np.max(handle_part))
        handle_low = float(np.min(handle_part))
        handle_depth_pct = round((handle_high - handle_low) / max(1.0, handle_high) * 100.0, 2)

        is_valid_cup = 12.0 <= cup_depth_pct <= 38.0
        is_valid_handle = handle_depth_pct <= 12.0 and handle_low >= (cup_low + 0.45 * (cup_high - cup_low))
        is_ch = bool(is_valid_cup and is_valid_handle)

        return {
            "is_cup_and_handle": is_ch,
            "cup_depth_pct": cup_depth_pct,
            "handle_depth_pct": handle_depth_pct,
            "breakout_pivot": round(cup_high, 2),
            "status": "CUP_AND_HANDLE_CONFIRMED" if is_ch else "NO_CUP_AND_HANDLE"
        }


class MultimodalChartReconciliationEngine:
    """Master service for cross-reconciling visual chart features against numerical OHLCV truth."""

    @classmethod
    def extract_visual_features_from_payload(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Parses and standardizes incoming multimodal vision payloads from vision models/OCR."""
        if not isinstance(payload, dict):
            return {}
        features: Dict[str, Any] = {}
        features["visual_price"] = payload.get("visual_price") or payload.get("spot_price") or payload.get("price")
        features["visual_breakout_level"] = payload.get("visual_breakout_level") or payload.get("breakout_level") or payload.get("resistance")
        features["visual_support"] = payload.get("visual_support") or payload.get("support_level") or payload.get("support")
        features["visual_pattern"] = payload.get("visual_pattern") or payload.get("pattern") or "UNSPECIFIED"
        features["timeframe"] = payload.get("timeframe", "DAILY")
        features["pattern_confidence"] = payload.get("pattern_confidence") or payload.get("confidence") or 0.0
        return features

    @classmethod
    def parse_chart_image_or_mock(
        cls,
        image_bytes: Optional[bytes] = None,
        base64_str: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Parses an input chart image (bytes or base64) into structured visual features.
        
        If metadata dictionary is provided directly, it extracts visual features.
        If raw image/base64 is provided, it handles payload normalization and attaches
        diagnostic tracking.
        """
        if metadata and isinstance(metadata, dict):
            return cls.extract_visual_features_from_payload(metadata)

        if not image_bytes and not base64_str:
            return {}

        raw_b64 = base64_str
        if not raw_b64 and image_bytes:
            import base64
            raw_b64 = base64.b64encode(image_bytes).decode("utf-8")

        if raw_b64 and "," in raw_b64:
            raw_b64 = raw_b64.split(",", 1)[1]

        import os
        from app.core.config import settings
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)

        if gemini_key and raw_b64 and "your_" not in str(gemini_key).lower():
            try:
                from app.services.llm import analyze_chart_image_with_vision
                vision_res = analyze_chart_image_with_vision(raw_b64)
                if vision_res.get("status") == "SUCCESS":
                    return {
                        "image_received": True,
                        "image_payload_len": len(raw_b64),
                        "extraction_status": "GEMINI_VISION_EXTRACTED",
                        "provenance": "Extracted via Gemini Vision perception API.",
                        "is_mock_fallback": False,
                        "visual_price": vision_res.get("visual_price"),
                        "visual_breakout_level": vision_res.get("visual_breakout_level"),
                        "visual_support": vision_res.get("visual_support"),
                        "visual_pattern": vision_res.get("visual_pattern", "UNSPECIFIED"),
                        "pattern_confidence": vision_res.get("pattern_confidence", 0.0),
                    }
            except Exception:
                pass

        return {
            "image_received": True,
            "image_payload_len": len(image_bytes) if image_bytes else (len(raw_b64) if raw_b64 else 0),
            "extraction_status": "VISION_PROVIDER_CONFIGURED" if gemini_key else "STRUCTURED_METADATA_REQUIRED",
            "provenance": "Raw chart image received. Computer vision pattern inference requires external ViT annotations or Gemini Vision API.",
            "is_mock_fallback": False,
            "visual_price": None,
            "visual_breakout_level": None,
            "visual_support": None,
            "visual_pattern": "UNSPECIFIED",
            "pattern_confidence": 0.0,
        }

    @classmethod
    def parse_chart_image_features(
        cls,
        image_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parses upstream Vision Transformer (ViT) annotations into structured pattern features.
        
        Supports bounding boxes, detected geometric pivots, trendline slopes, and candlestick patterns:
          - Bounding boxes: [ymin, xmin, ymax, xmax] mapped against y-axis price bounds [y_min, y_max].
          - Pattern classifications: 'VCP_CONTRACTION', 'CUP_AND_HANDLE', 'DOUBLE_BOTTOM', 'POCKET_PIVOT'.
          - Price level extraction: automatically resolves visual_breakout_level, visual_support, and spot_price.
        """
        if not isinstance(image_payload, dict):
            return {}

        boxes = image_payload.get("bounding_boxes", [])
        y_min = float(image_payload.get("y_axis_min", 0.0))
        y_max = float(image_payload.get("y_axis_max", 0.0))
        detected_pattern = str(image_payload.get("pattern", "UNSPECIFIED")).upper()
        confidence = float(image_payload.get("confidence", 0.0))

        visual_breakout = image_payload.get("breakout_level")
        visual_support = image_payload.get("support_level")
        visual_price = image_payload.get("spot_price") or image_payload.get("current_price")

        # Coordinate-to-Price Mapping for Bounding Boxes
        if y_max > y_min and boxes:
            for box in boxes:
                label = str(box.get("label", "")).upper()
                ymin = float(box.get("ymin", 0.0))
                ymax = float(box.get("ymax", 0.0))
                # Normalized coordinate (0 = bottom, 1 = top)
                box_price_high = y_min + ((1.0 - ymin) * (y_max - y_min))
                box_price_low = y_min + ((1.0 - ymax) * (y_max - y_min))

                if "RESISTANCE" in label or "BREAKOUT" in label:
                    visual_breakout = visual_breakout or round(box_price_high, 2)
                elif "SUPPORT" in label:
                    visual_support = visual_support or round(box_price_low, 2)
                elif "PRICE" in label or "CANDLE" in label:
                    visual_price = visual_price or round((box_price_high + box_price_low) / 2.0, 2)

        return {
            "visual_price": float(visual_price) if visual_price is not None else None,
            "visual_breakout_level": float(visual_breakout) if visual_breakout is not None else None,
            "visual_support": float(visual_support) if visual_support is not None else None,
            "visual_pattern": detected_pattern,
            "pattern_confidence": confidence,
            "bounding_boxes_count": len(boxes),
            "vision_adapter": "ViT_CHART_TRANSFORMER_V1",
            "timeframe": image_payload.get("timeframe", "DAILY"),
        }


    @classmethod
    def reconcile_chart_features(
        cls,
        symbol: str,
        visual_features: Dict[str, Any],
        df: Optional[pd.DataFrame] = None,
        tolerance_pct: float = 2.0
    ) -> Dict[str, Any]:
        """Cross-validates visual chart perceptions with numerical exchange data.

        Fail-closed rules:
          1. If visual breakout has < 1.5x 20-day ADTV in numerical data -> BULL_TRAP_FAILED_BREAKOUT.
          2. If visual level diverges > tolerance_pct from true exchange close -> PIXEL_DISCREPANCY_OVERRIDDEN.
          3. Numerical exchange data is ALWAYS the ultimate truth authority over image pixels.
        """
        norm_sym = symbol.upper()
        if df is None or df.empty or len(df) < 20:
            return {
                "symbol": norm_sym,
                "status": "DATA_INSUFFICIENT",
                "alignment_verdict": "UNVERIFIED_INSUFFICIENT_OHLCV",
                "alignment_score_0_100": 0.0,
                "numerical_price": None,
                "numerical_close": None,
                "is_breakout_confirmed": False,
                "data_authority": "NUMERIC_EXCHANGE_OHLCV_AUTHORITATIVE",
                "discrepancies": ["Historical OHLCV data insufficient to cross-verify chart image pixels."],
                "actionable_signal": "ABSTAIN_PENDING_CONFIRMED_DATA"
            }

        # Normalize column names
        for col in ('close', 'high', 'low', 'open', 'volume'):
            if col not in df.columns and col.capitalize() in df.columns:
                df[col] = df[col.capitalize()]

        latest_close = float(df['close'].iloc[-1])
        latest_vol = float(df['volume'].iloc[-1])
        adtv_20 = float(df['volume'].rolling(20).mean().iloc[-1]) if len(df) >= 20 else latest_vol
        vol_multiple = round(latest_vol / max(1.0, adtv_20), 2)

        if not visual_features or all(v is None for v in visual_features.values()):
            return {
                "symbol": norm_sym,
                "status": "DATA_INSUFFICIENT",
                "alignment_verdict": "NO_VISUAL_PAYLOAD_PROVIDED",
                "alignment_score_0_100": 0.0,
                "numerical_close": latest_close,
                "numerical_price": latest_close,
                "is_breakout_confirmed": False,
                "data_authority": "NUMERIC_EXCHANGE_OHLCV_AUTHORITATIVE",
                "discrepancies": ["No visual chart payload provided for cross-reconciliation."],
                "actionable_signal": "ABSTAIN_PENDING_CONFIRMED_DATA"
            }

        # 1. Price Discrepancy Check (Strict Invariant: Numeric OHLCV trumps visual pixels)
        discrepancies: List[str] = []
        visual_price = visual_features.get("visual_price") or visual_features.get("spot_price")
        price_discrepancy_pct = 0.0
        pixel_discrepancy_overridden = False

        if visual_price is not None:
            try:
                vp = float(visual_price)
                price_discrepancy_pct = round(abs(vp - latest_close) / latest_close * 100.0, 2)
                if price_discrepancy_pct > tolerance_pct:
                    pixel_discrepancy_overridden = True
                    discrepancies.append(
                        f"PIXEL_DISCREPANCY_OVERRIDDEN: Visual chart price (Rs {vp:.2f}) diverges by {price_discrepancy_pct:.2f}% "
                        f"from official exchange close (Rs {latest_close:.2f}). Numerical exchange close strictly enforced."
                    )
            except (ValueError, TypeError):
                pass

        # 2. Breakout Verification Gate
        visual_breakout_level = visual_features.get("visual_breakout_level")
        is_breakout_confirmed = False
        alignment_verdict = "IN_RANGE_CONSOLIDATION"
        alignment_score = 70.0
        unconfirmed_bull_trap = False

        if visual_breakout_level is not None:
            try:
                breakout_lvl = float(visual_breakout_level)
                if latest_close >= breakout_lvl:
                    # Confirmed above breakout level - now verify volume expansion
                    if vol_multiple >= 1.5:
                        is_breakout_confirmed = True
                        alignment_verdict = "CONFIRMED_HIGH_VOLUME_BREAKOUT"
                        alignment_score = 95.0
                    else:
                        is_breakout_confirmed = False
                        unconfirmed_bull_trap = True
                        alignment_verdict = "BULL_TRAP_LOW_VOLUME"
                        alignment_score = 35.0
                        discrepancies.append(
                            f"UNCONFIRMED_BULL_TRAP: Visual breakout above Rs {breakout_lvl:.2f} lacks institutional volume confirmation: "
                            f"volume is only {vol_multiple:.2f}x of 20D ADTV (minimum 1.5x required). High bull-trap risk."
                        )
                else:
                    is_breakout_confirmed = False
                    alignment_verdict = "PRE_BREAKOUT_CONSOLIDATION"
                    alignment_score = 65.0
            except (ValueError, TypeError):
                pass

        # 3. Support & Resistance Reconciliations
        visual_support = visual_features.get("visual_support")
        if visual_support is not None:
            try:
                supp = float(visual_support)
                if latest_close < supp:
                    discrepancies.append(f"Visual support (Rs {supp:.2f}) has been breached numerically (Close: Rs {latest_close:.2f}).")
                    alignment_verdict = "BREAKDOWN_SUPPORT_BREACHED"
                    alignment_score = min(alignment_score, 40.0)
            except (ValueError, TypeError):
                pass

        return {
            "symbol": norm_sym,
            "status": "SUCCESS",
            "alignment_verdict": alignment_verdict,
            "alignment_score_0_100": alignment_score,
            "numerical_close": latest_close,
            "numerical_volume": latest_vol,
            "volume_vs_adtv_20": vol_multiple,
            "price_discrepancy_pct": price_discrepancy_pct,
            "pixel_discrepancy_overridden": pixel_discrepancy_overridden,
            "unconfirmed_bull_trap": unconfirmed_bull_trap,
            "is_breakout_confirmed": is_breakout_confirmed,
            "data_authority": "NUMERIC_EXCHANGE_OHLCV_AUTHORITATIVE",
            "discrepancies": discrepancies,
            "actionable_signal": "ABSTAIN_DATA_MISMATCH" if pixel_discrepancy_overridden else ("EXECUTE_ENTRY" if is_breakout_confirmed else ("AVOID_BULL_TRAP" if alignment_verdict == "BULL_TRAP_LOW_VOLUME" else "MONITOR_SETUP"))
        }

    @classmethod
    def analyze_geometric_chart_patterns(
        cls,
        symbol: str,
        df: pd.DataFrame,
        visual_features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Performs full mathematical geometric chart analysis and anchors vision interpretations.
        
        Evaluates Minervini VCP, Cup & Handle, and Gaussian KDE Support/Resistance density.
        When visual_features are provided, cross-verifies visual levels against mathematical anchors.
        """
        norm_sym = symbol.upper()
        if df is None or df.empty or len(df) < 15:
            return {
                "symbol": norm_sym,
                "status": "DATA_INSUFFICIENT",
                "message": "Insufficient OHLCV bars for geometric pattern analysis (minimum 15 required).",
                "vcp": {"is_vcp_detected": False},
                "cup_and_handle": {"is_cup_and_handle": False},
                "kde_levels": {"status": "INSUFFICIENT_DATA"}
            }

        # Normalize column names
        for col in ('close', 'high', 'low', 'open', 'volume'):
            if col not in df.columns and col.capitalize() in df.columns:
                df[col] = df[col.capitalize()]

        vcp_res = GeometricPatternDetector.detect_vcp_pattern(df)
        ch_res = GeometricPatternDetector.detect_cup_and_handle(df)
        kde_res = GeometricPatternDetector.detect_kde_support_resistance(df)

        latest_close = float(df['close'].iloc[-1])

        # Vision Anchor Cross-Verification
        anchor_verified = False
        anchor_discrepancy_pct = None
        if visual_features and any(v is not None for v in visual_features.values()):
            vis_breakout = visual_features.get("visual_breakout_level")
            num_breakout = vcp_res.get("pivot_resistance") or ch_res.get("breakout_pivot") or kde_res.get("primary_resistance")
            if vis_breakout is not None and num_breakout is not None:
                vb = float(vis_breakout)
                nb = float(num_breakout)
                anchor_discrepancy_pct = round(abs(vb - nb) / max(0.1, nb) * 100.0, 2)
                anchor_verified = anchor_discrepancy_pct <= 2.0

        pattern_identified = "UNSPECIFIED"
        if vcp_res.get("is_vcp_detected"):
            pattern_identified = "MINERVINI_VCP"
        elif ch_res.get("is_cup_and_handle"):
            pattern_identified = "CUP_AND_HANDLE"
        elif kde_res.get("status") == "SUCCESS":
            pattern_identified = "KDE_RANGE_SHELVES"

        return {
            "symbol": norm_sym,
            "status": "SUCCESS",
            "pattern_type": "GEOMETRIC_OHLCV_VERIFIED",
            "pattern_identified": pattern_identified,
            "latest_close": latest_close,
            "vcp_analysis": vcp_res,
            "cup_and_handle_analysis": ch_res,
            "kde_support_resistance": kde_res,
            "visual_anchor_verified": anchor_verified,
            "anchor_discrepancy_pct": anchor_discrepancy_pct,
            "data_authority": "NUMERIC_EXCHANGE_OHLCV_AUTHORITATIVE"
        }

