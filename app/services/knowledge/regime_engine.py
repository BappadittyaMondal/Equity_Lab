"""Deterministic Market Regime Classification Engine.

Classifies the current Indian equity market regime using India VIX level,
Nifty 50 distance from 200-DMA, and optionally FII flow direction. Every
strategy engine should receive the current RegimeClassification and adapt
its thresholds accordingly.

Regime Definitions:
  CALM     — VIX < 15, Nifty above 200DMA  → Normal conviction thresholds
  ELEVATED — VIX 15–20 or Nifty within 5% of 200DMA → Slightly tighter
  VOLATILE — VIX 20–30 or Nifty below 200DMA → Require higher evidence
  CRISIS   — VIX > 30 and Nifty > 10% below 200DMA → Maximum conservatism
"""

import logging
from typing import Optional

from app.models.schemas import RegimeClassification, MacroContext, MetaHeader
from app.services.market_data import get_quote, get_history, normalize_symbol, create_meta_header

logger = logging.getLogger(__name__)

# VIX thresholds for regime classification
_VIX_CALM_MAX = 15.0
_VIX_ELEVATED_MAX = 20.0
_VIX_VOLATILE_MAX = 30.0

# Nifty 200DMA distance thresholds
_DMA_ELEVATED_PCT = -5.0  # within 5% below 200DMA
_DMA_CRISIS_PCT = -10.0    # more than 10% below 200DMA


class RegimeEngine:
    """Deterministic regime classifier for Indian equity markets."""

    def classify(
        self,
        vix_level: Optional[float] = None,
        nifty_spot: Optional[float] = None,
        nifty_200dma: Optional[float] = None,
        fii_net_flow_direction: Optional[str] = None,
    ) -> RegimeClassification:
        """Classify market regime from provided or live-fetched inputs.

        Args:
            vix_level: Current India VIX. If None, attempts live fetch.
            nifty_spot: Current Nifty 50 spot price. If None, attempts live fetch.
            nifty_200dma: Nifty 50 200-day moving average. If None, computed from history.
            fii_net_flow_direction: "INFLOW", "OUTFLOW", or "NEUTRAL". Optional context.

        Returns:
            RegimeClassification with regime, evidence, and confidence.
        """
        evidence = []

        # --- Fetch VIX if not provided ---
        if vix_level is None:
            vix_level = self._fetch_vix()
        if vix_level is not None:
            evidence.append(f"India VIX: {vix_level:.1f}")

        # --- Fetch Nifty spot if not provided ---
        if nifty_spot is None:
            nifty_spot = self._fetch_nifty_spot()
        if nifty_spot is not None:
            evidence.append(f"Nifty 50 Spot: {nifty_spot:.0f}")

        # --- Compute 200DMA if not provided ---
        dma_distance_pct = None
        if nifty_200dma is None and nifty_spot is not None:
            nifty_200dma = self._compute_nifty_200dma()
        if nifty_200dma is not None and nifty_spot is not None and nifty_200dma > 0:
            dma_distance_pct = ((nifty_spot - nifty_200dma) / nifty_200dma) * 100.0
            evidence.append(f"Nifty vs 200DMA: {dma_distance_pct:+.1f}%")

        # --- Classify regime ---
        regime = self._determine_regime(vix_level, dma_distance_pct)
        confidence = self._compute_confidence(vix_level, dma_distance_pct)

        if fii_net_flow_direction:
            evidence.append(f"FII Flow: {fii_net_flow_direction}")
            # FII outflow in volatile market increases severity
            if fii_net_flow_direction == "OUTFLOW" and regime in ("ELEVATED", "VOLATILE"):
                regime = "VOLATILE" if regime == "ELEVATED" else "CRISIS"
                evidence.append("FII outflow escalated regime severity")

        return RegimeClassification(
            regime=regime,
            vix_level=vix_level,
            nifty_200dma_distance_pct=round(dma_distance_pct, 2) if dma_distance_pct is not None else None,
            fii_net_flow_direction=fii_net_flow_direction,
            confidence=round(confidence, 2),
            evidence=evidence,
        )

    def get_macro_context(self) -> MacroContext:
        """Build a full MacroContext with live data where available."""
        regime = self.classify()
        nifty_quote = self._try_quote("^NSEI")
        return MacroContext(
            regime=regime,
            nifty_level=nifty_quote.get("price") if nifty_quote else None,
            india_vix=regime.vix_level,
        )

    # --- Private helpers ---

    def _determine_regime(
        self, vix: Optional[float], dma_pct: Optional[float]
    ) -> str:
        """Pure deterministic regime rules."""
        # Default to CALM if no data
        if vix is None and dma_pct is None:
            return "CALM"

        # Crisis: VIX > 30 AND significant DMA breach
        if vix is not None and vix > _VIX_VOLATILE_MAX:
            if dma_pct is not None and dma_pct < _DMA_CRISIS_PCT:
                return "CRISIS"
            return "VOLATILE"

        # Volatile: VIX 20-30 OR Nifty below 200DMA
        if vix is not None and vix > _VIX_ELEVATED_MAX:
            return "VOLATILE"
        if dma_pct is not None and dma_pct < _DMA_ELEVATED_PCT:
            return "VOLATILE"

        # Elevated: VIX 15-20 OR Nifty near 200DMA
        if vix is not None and vix > _VIX_CALM_MAX:
            return "ELEVATED"
        if dma_pct is not None and _DMA_ELEVATED_PCT <= dma_pct < 0:
            return "ELEVATED"

        return "CALM"

    def _compute_confidence(
        self, vix: Optional[float], dma_pct: Optional[float]
    ) -> float:
        """Confidence based on how many inputs we actually have."""
        inputs_available = sum([
            vix is not None,
            dma_pct is not None,
        ])
        if inputs_available == 0:
            return 0.3  # No data — low confidence default
        elif inputs_available == 1:
            return 0.65
        return 0.9  # Both VIX and DMA available

    def _fetch_vix(self) -> Optional[float]:
        """Try to fetch India VIX from live quote."""
        try:
            quote = get_quote("^INDIAVIX")
            if isinstance(quote, dict):
                return quote.get("price")
            return getattr(quote, "price", None)
        except Exception as e:
            logger.debug("Could not fetch India VIX: %s", e)
            return None

    def _fetch_nifty_spot(self) -> Optional[float]:
        """Try to fetch Nifty 50 spot price."""
        try:
            quote = get_quote("^NSEI")
            if isinstance(quote, dict):
                return quote.get("price")
            return getattr(quote, "price", None)
        except Exception as e:
            logger.debug("Could not fetch Nifty 50: %s", e)
            return None

    def _compute_nifty_200dma(self) -> Optional[float]:
        """Compute 200-day moving average of Nifty 50 from historical data."""
        try:
            hist = get_history("^NSEI", period="1y", interval="1d")
            if hist is not None and len(hist) >= 200:
                return float(hist['Close'].tail(200).mean())
            elif hist is not None and len(hist) >= 50:
                # Fallback: use available data
                return float(hist['Close'].mean())
            return None
        except Exception as e:
            logger.debug("Could not compute Nifty 200DMA: %s", e)
            return None

    def _try_quote(self, symbol: str) -> Optional[dict]:
        """Safely try to fetch a quote."""
        try:
            q = get_quote(symbol)
            return q if isinstance(q, dict) else None
        except Exception:
            return None
