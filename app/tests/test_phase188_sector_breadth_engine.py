"""Phase 188 Dedicated Unit Tests: Synthetic Micro-Sector Breadth Engine & Institutional Holding Fail-Closed.

Verifies:
1. SectorConstituent properties and zero-division/None robustness.
2. SectorBreadthEngine regime classification across all 5 states (IGNITION, ACCUMULATION, CONSOLIDATION, DISTRIBUTION, EXHAUSTION).
3. Monotonicity and bounds of the Sector Rotation Composite Score.
4. Multi-sector aggregation, delta momentum, and leader ranking.
5. Database ingestion from data/ierl_equity.sqlite3.
6. Stock-sector alignment tailwind/headwind scoring.
7. Remediation of silent 15.0% institutional holding defaults in InstitutionalMultibaggerEngine.
"""

import pytest
from app.services.research.sector_breadth_engine import (
    SectorConstituent,
    SectorBreadthSnapshot,
    SectorBreadthEngine,
)
from app.services.research.institutional_multibagger_engine import (
    InstitutionalMultibaggerEngine,
)


def test_sector_constituent_properties():
    """Verify constituent indicators handle None, zero, and positive comparisons accurately."""
    c1 = SectorConstituent(
        symbol="BEL.NS",
        sector="Defence",
        current_price=300.0,
        dma_50=280.0,
        dma_200=250.0,
        volume=500000.0,
        volume_avg=400000.0,
    )
    assert c1.is_above_50dma is True
    assert c1.is_above_200dma is True
    assert c1.is_volume_expanding is True

    # None and zero edge cases
    c2 = SectorConstituent(
        symbol="EMPTY.NS",
        sector="Defence",
        current_price=100.0,
        dma_50=0.0,
        dma_200=None,
        volume=None,
        volume_avg=0.0,
    )
    assert c2.is_above_50dma is False
    assert c2.is_above_200dma is False
    assert c2.is_volume_expanding is False


def test_sector_breadth_regime_classification():
    """Verify regime classifications across market cycles."""
    # 1. Ignition via trough surge (prior < 0.35, current >= 0.60)
    reg_ign_trough = SectorBreadthEngine.classify_regime(
        breadth_50=0.62,
        breadth_200=0.55,
        volume_expansion=0.45,
        delta=0.30,
        prior_breadth=0.32,
    )
    assert reg_ign_trough == SectorBreadthEngine.REGIME_IGNITION

    # 2. Ignition via volume thrust (breadth_50 >= 0.65, vol_exp >= 0.50, delta >= 0.15)
    reg_ign_vol = SectorBreadthEngine.classify_regime(
        breadth_50=0.68,
        breadth_200=0.60,
        volume_expansion=0.55,
        delta=0.18,
        prior_breadth=0.50,
    )
    assert reg_ign_vol == SectorBreadthEngine.REGIME_IGNITION

    # 3. Exhaustion / Overbought Guard (breadth_50 >= 0.85)
    reg_exh = SectorBreadthEngine.classify_regime(
        breadth_50=0.88,
        breadth_200=0.85,
        volume_expansion=0.60,
        delta=0.05,
    )
    assert reg_exh == SectorBreadthEngine.REGIME_EXHAUSTION

    # 4. Sustained Accumulation (0.50 <= breadth_50 < 0.85)
    reg_acc = SectorBreadthEngine.classify_regime(
        breadth_50=0.55,
        breadth_200=0.52,
        volume_expansion=0.40,
        delta=0.02,
        prior_breadth=0.53,
    )
    assert reg_acc == SectorBreadthEngine.REGIME_ACCUMULATION

    # 5. Distribution (< 0.35)
    reg_dist = SectorBreadthEngine.classify_regime(
        breadth_50=0.25,
        breadth_200=0.30,
        volume_expansion=0.20,
        delta=-0.10,
    )
    assert reg_dist == SectorBreadthEngine.REGIME_DISTRIBUTION

    # 6. Neutral Consolidation (0.35 <= breadth_50 < 0.50)
    reg_cons = SectorBreadthEngine.classify_regime(
        breadth_50=0.42,
        breadth_200=0.45,
        volume_expansion=0.30,
        delta=0.01,
        prior_breadth=0.41,
    )
    assert reg_cons == SectorBreadthEngine.REGIME_CONSOLIDATION


def test_rotation_score_monotonicity_and_bounds():
    """Verify rotation score is bounded between 0 and 100 and scales with participation."""
    # Strongest setup
    score_max = SectorBreadthEngine.compute_rotation_score(
        breadth_50=1.0, breadth_200=1.0, volume_expansion=1.0, delta=0.50
    )
    assert score_max == 100.0

    # Weakest setup
    score_min = SectorBreadthEngine.compute_rotation_score(
        breadth_50=0.0, breadth_200=0.0, volume_expansion=0.0, delta=-0.50
    )
    assert score_min == 0.0

    # Monotonicity test
    score_mid = SectorBreadthEngine.compute_rotation_score(
        breadth_50=0.50, breadth_200=0.50, volume_expansion=0.50, delta=0.0
    )
    assert score_min < score_mid < score_max


def test_sector_breadth_aggregation_and_leaders():
    """Verify aggregation across multiple sectors with leaders extraction."""
    constituents = [
        # Capital Goods (Strong)
        SectorConstituent("HAL.NS", "Capital Goods", 4500.0, 4200.0, 3800.0, 1000, 800),
        SectorConstituent("BEL.NS", "Capital Goods", 320.0, 300.0, 270.0, 2000, 1500),
        SectorConstituent("BEML.NS", "Capital Goods", 3800.0, 3500.0, 3100.0, 500, 400),
        SectorConstituent("SIEMENS.NS", "Capital Goods", 6500.0, 6800.0, 6200.0, 200, 300),  # Below 50 DMA
        # FMCG (Weak Distribution)
        SectorConstituent("HINDUNILVR.NS", "FMCG", 2300.0, 2450.0, 2550.0, 1000, 1200),
        SectorConstituent("ITC.NS", "FMCG", 470.0, 485.0, 460.0, 3000, 3500),
        SectorConstituent("NESTLEIND.NS", "FMCG", 2150.0, 2300.0, 2400.0, 400, 500),
    ]

    prior_breadth = {"Capital Goods": 0.50, "FMCG": 0.35}

    snapshots = SectorBreadthEngine.compute_sector_breadth_from_constituents(
        constituents=constituents, prior_breadth_map=prior_breadth
    )

    assert "Capital Goods" in snapshots
    assert "FMCG" in snapshots

    cg = snapshots["Capital Goods"]
    assert cg.total_constituents == 4
    assert cg.constituents_above_50dma == 3
    assert cg.breadth_50dma_ratio == 0.75
    assert cg.breadth_delta == 0.25  # 0.75 - 0.50
    assert cg.regime == SectorBreadthEngine.REGIME_IGNITION
    assert len(cg.leaders) > 0
    assert "HAL.NS" in cg.leaders

    fmcg = snapshots["FMCG"]
    assert fmcg.total_constituents == 3
    assert fmcg.constituents_above_50dma == 0
    assert fmcg.breadth_50dma_ratio == 0.0
    assert fmcg.regime == SectorBreadthEngine.REGIME_DISTRIBUTION


def test_sector_ranking_and_alignment():
    """Verify top rotating sectors ranking and individual stock alignment."""
    constituents = [
        SectorConstituent("TITAGARH.NS", "Railways", 1200.0, 1000.0, 900.0, 1000, 800),
        SectorConstituent("JWL.NS", "Railways", 450.0, 400.0, 350.0, 1000, 800),
        SectorConstituent("HDFCBANK.NS", "Banking", 1600.0, 1650.0, 1620.0, 1000, 1500),
    ]
    snapshots = SectorBreadthEngine.compute_sector_breadth_from_constituents(constituents)
    top_sectors = SectorBreadthEngine.get_top_rotating_sectors(snapshots, top_n=2)
    assert len(top_sectors) == 2
    assert top_sectors[0].sector == "Railways"

    # Alignment evaluation for a stock in leading sector
    align_rail = SectorBreadthEngine.evaluate_stock_sector_alignment("TITAGARH.NS", "Railways", snapshots)
    assert align_rail["sector_observed"] is True
    assert align_rail["tailwind_bonus"] > 0

    # Alignment evaluation for unobserved sector
    align_unobs = SectorBreadthEngine.evaluate_stock_sector_alignment("UNKNOWN.NS", "Crypto", snapshots)
    assert align_unobs["sector_observed"] is False
    assert align_unobs["tailwind_bonus"] == 0.0


def test_sector_breadth_db_ingestion():
    """Verify compute_sector_breadth_from_db runs safely against data/ierl_equity.sqlite3."""
    snapshots = SectorBreadthEngine.compute_sector_breadth_from_db("data/ierl_equity.sqlite3")
    assert isinstance(snapshots, dict)
    # The DB contains live fundamentals data; ensure it loads without exception
    if len(snapshots) > 0:
        first_sec = list(snapshots.values())[0]
        assert first_sec.total_constituents > 0
        assert 0.0 <= first_sec.breadth_50dma_ratio <= 1.0


def test_institutional_multibagger_unobserved_holding_remediation():
    """Verify InstitutionalMultibaggerEngine explicitly flags unobserved institutional holding."""
    # Case 1: Unobserved institutional holding
    unobserved_comp = {
        "symbol": "TINY.NS",
        "analyst_coverage_count": 1,
        # fii_dii_holding and institutional_holding omitted
    }
    disc = InstitutionalMultibaggerEngine.get_discovery_status(unobserved_comp)
    assert disc["is_institutional_holding_observed"] is False
    assert disc["institutional_holding_pct"] == 0.0
    assert "Unobserved" in disc["discovery_label"]

    lag = InstitutionalMultibaggerEngine.compute_regulatory_discovery_lag_score(unobserved_comp)
    assert lag["is_institutional_holding_observed"] is False
    assert any("unobserved" in s.lower() for s in lag["discovery_signals"])

    # Case 2: Observed institutional holding
    observed_comp = {
        "symbol": "FOUND.NS",
        "analyst_coverage_count": 2,
        "fii_dii_holding": 8.5,
    }
    disc2 = InstitutionalMultibaggerEngine.get_discovery_status(observed_comp)
    assert disc2["is_institutional_holding_observed"] is True
    assert disc2["institutional_holding_pct"] == 8.5
    assert disc2["discovery_label"] == "Lightly Covered"


def test_phase188_learned_rules_inscribed():
    """Verify Phase 188 rules are inscribed in data/dynamic_knowledge/learned_rules_registry.json."""
    import json
    with open("data/dynamic_knowledge/learned_rules_registry.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    entities = data.get("entities", {})
    assert "SYNTHETIC_SECTOR_BREADTH_IGNITION_RULE" in entities
    assert "INSTITUTIONAL_HOLDING_FAIL_CLOSED_RULE" in entities
    assert entities["SYNTHETIC_SECTOR_BREADTH_IGNITION_RULE"]["verification_status"] == "CERTIFIED_FACT"
    assert entities["INSTITUTIONAL_HOLDING_FAIL_CLOSED_RULE"]["verification_status"] == "CERTIFIED_FACT"

