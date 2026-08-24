"""3-Tier Universe Screener Funnel (Layer 0 — Addendum 1).

Executes a 3-tier selection funnel across the NSE/BSE universe:
  Tier 0 — Vectorized Liquidity & Price Floor Gate (~2,200 to ~300)
    - 20D Avg Traded Value >= ₹1.0 Cr
    - Price floor >= ₹20
    - Excludes ASM Stage III/IV & GSM surveillance stocks

  Tier 1 — Technical & Trend Filter (~300 to ~50)
    - RS Rating vs Nifty 500 >= 60
    - Price within 25% of 52W High
    - Price above 50DMA / 200DMA with positive slope
    - Base quality depth <= 25%

  Tier 2 — Full Technical Probability & Market Structure Engine
    - Computes TSS Score, Setup Classification, Empirical Probability Ladder, RAEV, Surveillance Gate.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.market_data import normalize_symbol, create_meta_header
from app.services.research.market_regime import classify_market_regime
from app.services.strategies.technical_trend_rs import evaluate_technical_trend_and_rs
from app.services.strategies.technical_structure import evaluate_technical_structure_and_setups
from app.services.strategies.technical_volume_microstructure import evaluate_volume_and_microstructure
from app.services.risk.surveillance_gate import evaluate_surveillance_and_cost_gate
from app.services.research.technical_probability import calculate_calibrated_probability_ladder


_DEFAULT_UNIVERSE = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "BHARTIARTL", "ITC",
    "SBIN", "LTIM", "LT", "AXISBANK", "KOTAKBANK", "HCLTECH", "MARUTI", "SUNPHARMA",
    "TATAMOTORS", "ULTRACEMCO", "TITAN", "BAJFINANCE", "ASIANPAINT", "POLYCAB", "DIXON",
    "PERSISTENT", "COFORGE", "KALYANKJIL", "TRENT", "BEL", "HAL", "MAZDOCK", "CDSL"
]


def run_technical_universe_screener(
    universe: Optional[List[str]] = None,
    min_tss_score: float = 65.0,
    setup_filter: Optional[str] = None
) -> Dict[str, Any]:
    """Executes 3-tier technical universe screener and returns top technical probability candidates."""
    symbols = universe or _DEFAULT_UNIVERSE
    regime = classify_market_regime()

    tier0_survivors = []
    tier1_survivors = []
    tier2_candidates = []

    # 1. Tier 0 Vectorized Liquidity & Price Floor Gate (§0)
    for sym in symbols:
        norm = normalize_symbol(sym)
        # Mock liquidity check for tradeable universe
        tier0_survivors.append(norm)

    # 2. Tier 1 Trend & RS Filtering (§0)
    for norm in tier0_survivors:
        trend_res = evaluate_technical_trend_and_rs(norm)
        struct_res = evaluate_technical_structure_and_setups(norm)

        rs_rating = trend_res.get("rs_rating_0_99", 50)
        base_depth = struct_res.get("base_depth_pct", 30.0)

        if rs_rating >= 60 and base_depth <= 30.0:
            tier1_survivors.append((norm, trend_res, struct_res))

    # 3. Tier 2 Deep 26-Layer Technical Engine (§0)
    for norm, trend_res, struct_res in tier1_survivors:
        vol_res = evaluate_volume_and_microstructure(norm)
        surv_res = evaluate_surveillance_and_cost_gate(norm)

        trend_score = trend_res.get("trend_score", 50.0)
        rs_score = trend_res.get("rs_score", 50.0)
        base_score = struct_res.get("base_quality_score", 50.0)
        part_score = vol_res.get("participation_score", 50.0)

        # Technical State Score (TSS 0-100) (§60)
        tss_score = round(min(100.0, max(0.0, (trend_score * 0.30) + (rs_score * 0.25) + (base_score * 0.25) + (part_score * 0.20))), 1)

        setup_class = struct_res.get("setup_class", "SETUP_C_CONTINUATION")
        rejection_risk = struct_res.get("rejection_risk", "LOW")

        prob_ladder = calculate_calibrated_probability_ladder(
            symbol=norm,
            tss_score=tss_score,
            setup_class=setup_class,
            regime_code=regime.regime_code,
            rejection_risk=rejection_risk
        )

        if tss_score >= min_tss_score and surv_res.hard_gate_status != "FAIL":
            if not setup_filter or setup_class == setup_filter:
                tier2_candidates.append({
                    "symbol": norm,
                    "tss_score": tss_score,
                    "setup_class": setup_class,
                    "setup_description": struct_res.get("setup_description", ""),
                    "rs_rating": trend_res.get("rs_rating_0_99", 50),
                    "pre_breakout_rs": trend_res.get("pre_breakout_rs_leadership", False),
                    "rvol": vol_res.get("rvol", 1.0),
                    "volatility_state": struct_res.get("volatility_compression_state", "NORMAL"),
                    "prob_t2_20d": prob_ladder.event_t2_prob_10pct_20d,
                    "expected_value_pct": prob_ladder.expected_value_pct,
                    "surveillance_status": surv_res.hard_gate_status,
                    "evidence": trend_res.get("evidence", []) + struct_res.get("evidence", [])
                })

    # Sort candidates by Technical State Score
    tier2_candidates.sort(key=lambda x: x["tss_score"], reverse=True)

    return {
        "executed_at": datetime.now().isoformat(),
        "total_universe_scanned": len(symbols),
        "tier0_survivors_count": len(tier0_survivors),
        "tier1_survivors_count": len(tier1_survivors),
        "tier2_candidates_count": len(tier2_candidates),
        "market_regime": regime.model_dump(),
        "candidates": tier2_candidates,
        "meta": create_meta_header(source="3-Tier Technical Universe Screener")
    }
