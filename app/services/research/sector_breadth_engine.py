"""Sector Breadth & Thematic Rotation Engine (§Phase 188).

Calculates Synthetic Micro-Sector Breadth Ratios and identifies Institutional Sector Rotation
Ignitions across Indian equity market micro-domains.

Institutional Thesis:
1. "Don't fight the sector tide": Stocks in sectors experiencing SECTOR_ROTATION_IGNITION have a
   substantially higher breakout win-rate due to coordinated institutional asset allocation.
2. Conversely, even strong fundamental compounders struggle to produce multi-bagger momentum when
   their host sector is undergoing structural SECTOR_DISTRIBUTION (< 35% breadth).
3. Extreme breadth (> 85%) warns of crowding and impending cyclical exhaustion (SECTOR_EXHAUSTION_OVERBOUGHT).

Mathematical Specification:
- Breadth 50-DMA: B_50 = N(Price > 50-DMA) / N_total
- Breadth 200-DMA: B_200 = N(Price > 200-DMA) / N_total
- Volume Expansion Ratio: V_exp = N(Volume >= Vol_1M_Avg) / N_total
- Breadth Delta: ΔB = B_50 - B_50_prior
- Composite Rotation Score (0 - 100):
    Score = 45 * B_50 + 25 * B_200 + 20 * V_exp + 10 * clamp((ΔB + 0.25) / 0.50, 0, 1)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SectorConstituent:
    """Individual stock constituent within a sector breadth pool."""
    symbol: str
    sector: str
    current_price: float
    dma_50: float
    dma_200: Optional[float] = None
    volume: Optional[float] = None
    volume_avg: Optional[float] = None
    market_cap: Optional[float] = None
    returns_1m: Optional[float] = None

    @property
    def is_above_50dma(self) -> bool:
        if self.dma_50 is None or self.dma_50 <= 0:
            return False
        return self.current_price > self.dma_50

    @property
    def is_above_200dma(self) -> bool:
        if self.dma_200 is None or self.dma_200 <= 0:
            return False
        return self.current_price > self.dma_200

    @property
    def is_volume_expanding(self) -> bool:
        if self.volume is None or self.volume_avg is None or self.volume_avg <= 0:
            return False
        return self.volume >= self.volume_avg


@dataclass
class SectorBreadthSnapshot:
    """Consolidated breadth snapshot and rotation regime for a sector."""
    sector: str
    total_constituents: int
    constituents_above_50dma: int
    breadth_50dma_ratio: float
    constituents_above_200dma: int
    breadth_200dma_ratio: float
    volume_expansion_ratio: float
    prior_breadth_50dma_ratio: Optional[float] = None
    breadth_delta: float = 0.0
    regime: str = "SECTOR_CONSOLIDATION"
    rotation_score: float = 50.0
    signals: List[str] = field(default_factory=list)
    leaders: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sector": self.sector,
            "total_constituents": self.total_constituents,
            "constituents_above_50dma": self.constituents_above_50dma,
            "breadth_50dma_ratio": round(self.breadth_50dma_ratio, 4),
            "constituents_above_200dma": self.constituents_above_200dma,
            "breadth_200dma_ratio": round(self.breadth_200dma_ratio, 4),
            "volume_expansion_ratio": round(self.volume_expansion_ratio, 4),
            "prior_breadth_50dma_ratio": round(self.prior_breadth_50dma_ratio, 4) if self.prior_breadth_50dma_ratio is not None else None,
            "breadth_delta": round(self.breadth_delta, 4),
            "regime": self.regime,
            "rotation_score": round(self.rotation_score, 1),
            "signals": self.signals,
            "leaders": self.leaders,
        }


class SectorBreadthEngine:
    """Institutional Sector Breadth & Thematic Rotation Engine."""

    # Canonical Regimes
    REGIME_IGNITION = "SECTOR_ROTATION_IGNITION"
    REGIME_ACCUMULATION = "SECTOR_ACCUMULATION"
    REGIME_CONSOLIDATION = "SECTOR_CONSOLIDATION"
    REGIME_DISTRIBUTION = "SECTOR_DISTRIBUTION"
    REGIME_EXHAUSTION = "SECTOR_EXHAUSTION_OVERBOUGHT"

    @classmethod
    def classify_regime(
        cls,
        breadth_50: float,
        breadth_200: float,
        volume_expansion: float,
        delta: float,
        prior_breadth: Optional[float] = None,
        total_constituents: int = 5,
    ) -> str:
        """Classify sector regime based on multi-timeframe breadth and thrust metrics."""
        # 1. Sector Rotation Ignition (Thrust from bottom or explosive breakout with volume)
        is_surge_from_trough = prior_breadth is not None and prior_breadth < 0.35 and breadth_50 >= 0.60
        is_thrust_with_volume = breadth_50 >= 0.65 and volume_expansion >= 0.50 and delta >= 0.15
        is_large_momentum_thrust = breadth_50 >= 0.70 and delta >= 0.20
        if is_surge_from_trough or is_thrust_with_volume or is_large_momentum_thrust:
            return cls.REGIME_IGNITION

        # 2. Exhaustion / Overbought Guard: applies when breadth is ultra-high (>= 0.85) without a fresh breakout thrust
        if breadth_50 >= 0.85 and total_constituents >= 4 and delta <= 0.10:
            return cls.REGIME_EXHAUSTION

        # 3. Sustained Accumulation
        if breadth_50 >= 0.50:
            return cls.REGIME_ACCUMULATION

        # 4. Distribution / Structural Breakdown
        if breadth_50 < 0.35 or (breadth_50 < 0.40 and delta <= -0.15):
            return cls.REGIME_DISTRIBUTION

        # 5. Default Neutral Consolidation
        return cls.REGIME_CONSOLIDATION

    @classmethod
    def compute_rotation_score(
        cls,
        breadth_50: float,
        breadth_200: float,
        volume_expansion: float,
        delta: float,
    ) -> float:
        """Calculate normalized sector rotation composite score (0.0 to 100.0)."""
        clamped_delta_norm = min(1.0, max(0.0, (delta + 0.25) / 0.50))
        raw_score = (
            45.0 * breadth_50
            + 25.0 * breadth_200
            + 20.0 * volume_expansion
            + 10.0 * clamped_delta_norm
        )
        return round(min(100.0, max(0.0, raw_score)), 1)

    @classmethod
    def compute_sector_breadth_from_constituents(
        cls,
        constituents: List[SectorConstituent],
        prior_breadth_map: Optional[Dict[str, float]] = None,
    ) -> Dict[str, SectorBreadthSnapshot]:
        """Aggregate constituents into sector breadth snapshots."""
        if not constituents:
            return {}

        prior_map = prior_breadth_map or {}
        by_sector: Dict[str, List[SectorConstituent]] = {}
        for c in constituents:
            sec = c.sector.strip() if c.sector else "General / Unclassified"
            by_sector.setdefault(sec, []).append(c)

        results: Dict[str, SectorBreadthSnapshot] = {}

        for sec, items in by_sector.items():
            total = len(items)
            if total == 0:
                continue

            above_50 = sum(1 for x in items if x.is_above_50dma)
            above_200 = sum(1 for x in items if x.is_above_200dma)
            vol_exp = sum(1 for x in items if x.is_volume_expanding)

            b_50 = above_50 / float(total)
            b_200 = above_200 / float(total)
            v_ratio = vol_exp / float(total)

            prior_b = prior_map.get(sec)
            delta = (b_50 - prior_b) if prior_b is not None else 0.0

            regime = cls.classify_regime(
                breadth_50=b_50,
                breadth_200=b_200,
                volume_expansion=v_ratio,
                delta=delta,
                prior_breadth=prior_b,
                total_constituents=total,
            )

            score = cls.compute_rotation_score(
                breadth_50=b_50,
                breadth_200=b_200,
                volume_expansion=v_ratio,
                delta=delta,
            )

            signals: List[str] = []
            if regime == cls.REGIME_IGNITION:
                signals.append(f"Institutional Breadth Thrust: {above_50}/{total} stocks ({b_50*100:.1f}%) above 50-DMA with ΔB = +{delta*100:.1f}%.")
            elif regime == cls.REGIME_EXHAUSTION:
                signals.append(f"Overbought Warning: Breadth at extreme {b_50*100:.1f}%; heightened risk of sector mean-reversion.")
            elif regime == cls.REGIME_DISTRIBUTION:
                signals.append(f"Sector Distribution: Only {above_50}/{total} stocks ({b_50*100:.1f}%) above 50-DMA; macro headwind.")
            elif regime == cls.REGIME_ACCUMULATION:
                signals.append(f"Steady Institutional Accumulation: {b_50*100:.1f}% breadth above 50-DMA.")

            # Identify leaders: stocks above 50 DMA sorted by returns or price/50dma ratio
            leaders = [
                x.symbol
                for x in sorted(
                    items,
                    key=lambda s: (s.current_price / s.dma_50 if s.dma_50 > 0 else 0.0),
                    reverse=True,
                )
                if x.is_above_50dma
            ][:3]

            results[sec] = SectorBreadthSnapshot(
                sector=sec,
                total_constituents=total,
                constituents_above_50dma=above_50,
                breadth_50dma_ratio=b_50,
                constituents_above_200dma=above_200,
                breadth_200dma_ratio=b_200,
                volume_expansion_ratio=v_ratio,
                prior_breadth_50dma_ratio=prior_b,
                breadth_delta=delta,
                regime=regime,
                rotation_score=score,
                signals=signals,
                leaders=leaders,
            )

        return results

    @classmethod
    def compute_sector_breadth_from_db(
        cls,
        db_path: str = "data/ierl_equity.sqlite3",
        prior_breadth_map: Optional[Dict[str, float]] = None,
    ) -> Dict[str, SectorBreadthSnapshot]:
        """Load constituents from SQLite database and compute breadth snapshots."""
        db_file = Path(db_path)
        if not db_file.exists():
            logger.warning("Database file not found at %s. Returning empty breadth map.", db_path)
            return {}

        constituents: List[SectorConstituent] = []
        try:
            conn = sqlite3.connect(str(db_file))
            cur = conn.cursor()

            # Query joining companies and company_fundamentals
            cur.execute("""
                SELECT 
                    c.symbol, 
                    COALESCE(c.sector, 'General') as sector,
                    f.current_price,
                    f.dma_50,
                    f.dma_200,
                    f.volume,
                    f.vol_1m_avg,
                    f.market_cap
                FROM companies c
                JOIN company_fundamentals f ON (
                    c.symbol = f.symbol 
                    OR replace(replace(c.symbol, '.NS', ''), '.BO', '') = replace(replace(f.symbol, '.NS', ''), '.BO', '')
                )
                WHERE f.current_price IS NOT NULL 
                  AND f.dma_50 IS NOT NULL 
                  AND f.dma_50 > 0
            """)
            rows = cur.fetchall()
            for r in rows:
                sym, sec, price, d50, d200, vol, v_avg, mcap = r
                constituents.append(
                    SectorConstituent(
                        symbol=sym,
                        sector=sec,
                        current_price=float(price or 0.0),
                        dma_50=float(d50 or 0.0),
                        dma_200=float(d200) if d200 is not None else None,
                        volume=float(vol) if vol is not None else None,
                        volume_avg=float(v_avg) if v_avg is not None else None,
                        market_cap=float(mcap) if mcap is not None else None,
                    )
                )
            conn.close()
        except Exception as exc:
            logger.warning("Error reading sector breadth from DB %s: %s", db_path, exc)
            return {}

        return cls.compute_sector_breadth_from_constituents(constituents, prior_breadth_map)

    @classmethod
    def get_top_rotating_sectors(
        cls,
        snapshots: Dict[str, SectorBreadthSnapshot],
        top_n: int = 5,
    ) -> List[SectorBreadthSnapshot]:
        """Rank sectors by rotation score in descending order."""
        sorted_sectors = sorted(
            snapshots.values(),
            key=lambda x: (x.rotation_score, x.breadth_50dma_ratio),
            reverse=True,
        )
        return sorted_sectors[:top_n]

    @classmethod
    def evaluate_stock_sector_alignment(
        cls,
        symbol: str,
        sector: str,
        snapshots: Dict[str, SectorBreadthSnapshot],
    ) -> Dict[str, Any]:
        """Evaluate whether an individual stock has sector institutional tailwind or headwind."""
        snapshot = snapshots.get(sector)
        if not snapshot:
            return {
                "symbol": symbol,
                "sector": sector,
                "sector_observed": False,
                "alignment_status": "NEUTRAL",
                "tailwind_bonus": 0.0,
                "regime": "UNKNOWN",
                "note": f"Sector '{sector}' not found in active breadth snapshots.",
            }

        if snapshot.regime == cls.REGIME_IGNITION:
            status = "STRONG_TAILWIND"
            bonus = 10.0
            note = f"Sector '{sector}' is in SECTOR_ROTATION_IGNITION (Breadth {snapshot.breadth_50dma_ratio*100:.1f}%, Score: {snapshot.rotation_score})."
        elif snapshot.regime == cls.REGIME_ACCUMULATION:
            status = "MODERATE_TAILWIND"
            bonus = 5.0
            note = f"Sector '{sector}' is in healthy institutional accumulation (Breadth {snapshot.breadth_50dma_ratio*100:.1f}%)."
        elif snapshot.regime == cls.REGIME_DISTRIBUTION:
            status = "STRUCTURAL_HEADWIND"
            bonus = -15.0
            note = f"CAUTION: Sector '{sector}' is in distribution (Breadth {snapshot.breadth_50dma_ratio*100:.1f}% < 35%). High failure rate."
        elif snapshot.regime == cls.REGIME_EXHAUSTION:
            status = "OVERBOUGHT_TAILWIND"
            bonus = 3.0
            note = f"Sector '{sector}' is overbought ({snapshot.breadth_50dma_ratio*100:.1f}% breadth); strong tailwind but watch for mean-reverting pullbacks."
        else:
            status = "NEUTRAL"
            bonus = 0.0
            note = f"Sector '{sector}' is consolidating ({snapshot.breadth_50dma_ratio*100:.1f}% breadth)."

        return {
            "symbol": symbol,
            "sector": sector,
            "sector_observed": True,
            "alignment_status": status,
            "tailwind_bonus": bonus,
            "regime": snapshot.regime,
            "rotation_score": snapshot.rotation_score,
            "breadth_50dma_ratio": snapshot.breadth_50dma_ratio,
            "is_sector_leader": symbol in snapshot.leaders,
            "note": note,
        }
