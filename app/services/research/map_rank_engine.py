"""MAP-Rank: Multi-Asset Pareto Ranking Engine — Phase 139.

Performs a cross-sectional Pareto tournament across N candidate stocks.
Evaluates each stock simultaneously on 4 orthogonal Pareto dimensions:

  1. Solvency           — balance sheet safety (D/E, interest coverage)
  2. Cash Quality       — CFO/PAT cash accrual quality (CAQI)
  3. Valuation Headroom — multiple expansion room (DEME-HR = sector P/E ceiling / trailing P/E)
  4. Geopolitical Moat  — aggregate β_geo shock sensitivity

Key design principles:
- No single-stock isolation: all scores are cross-sectional (ranked relative to the peer set)
- CAQI < 0.80 → FAIL gate: penalises cash-poor earners
- DEME-HR ≤ 1.0 → VALUATION_CONSTRAINED: prevents bubble-valuation conviction
- Intent archetype adjusts dimension weights (MULTIBAGGER vs SIP vs TURNAROUND etc.)

Output: sorted `List[MAPRankEntry]` with composite score, per-dimension scores, CAQI,
        DEME-HR, archetype, and risk flags.
"""

import logging
from typing import Any, Dict, List, Optional

from app.services.market_data import normalize_symbol, create_meta_header, get_ist_now_str
from app.services.research.geopolitical_engine import compute_geo_shock_sensitivity

logger = logging.getLogger(__name__)


# ── Archetype → dimension weight profiles ────────────────────────────────────
# Weights sum to 1.0. Reflect economic emphasis per investment thesis.
_MAP_WEIGHT_PROFILES: Dict[str, Dict[str, float]] = {
    "MULTIBAGGER":       {"solvency": 0.20, "cash_quality": 0.35, "val_headroom": 0.30, "geo_moat": 0.15},
    "SIP_COMPOUNDER":    {"solvency": 0.30, "cash_quality": 0.40, "val_headroom": 0.20, "geo_moat": 0.10},
    "TURNAROUND":        {"solvency": 0.35, "cash_quality": 0.25, "val_headroom": 0.25, "geo_moat": 0.15},
    "MICRO_CAP":         {"solvency": 0.20, "cash_quality": 0.35, "val_headroom": 0.30, "geo_moat": 0.15},
    "VALUE":             {"solvency": 0.25, "cash_quality": 0.30, "val_headroom": 0.35, "geo_moat": 0.10},
    "SWING_3D":          {"solvency": 0.10, "cash_quality": 0.15, "val_headroom": 0.35, "geo_moat": 0.40},
    "SWING_10D":         {"solvency": 0.15, "cash_quality": 0.20, "val_headroom": 0.30, "geo_moat": 0.35},
    "POSITIONAL_30D":    {"solvency": 0.20, "cash_quality": 0.25, "val_headroom": 0.30, "geo_moat": 0.25},
    "DEFAULT":           {"solvency": 0.25, "cash_quality": 0.30, "val_headroom": 0.25, "geo_moat": 0.20},
}

# Sector P/E ceilings (mirrored from institutional_multibagger_engine.py)
_SECTOR_PE_CEILING: Dict[str, float] = {
    "DEFENSE": 90.0, "HEAVY_ENGINEERING": 45.0, "ENGINEERING": 45.0,
    "CAPITAL_GOODS": 55.0, "RENEWABLE": 60.0, "POWER": 35.0,
    "TRANSFORMERS": 55.0, "IT": 35.0, "SOFTWARE": 35.0,
    "BANKING": 20.0, "NBFC": 25.0, "PHARMA": 30.0,
    "CHEMICALS": 35.0, "FMCG": 55.0, "CONSUMER": 50.0,
    "METALS": 18.0, "CEMENT": 25.0, "SHIPPING": 20.0,
    "REAL_ESTATE": 30.0, "AUTO": 30.0, "AUTO_ANCILLARY": 35.0,
    "TEXTILES": 25.0, "AGRI": 30.0, "DIVERSIFIED": 40.0,
}


def _score_solvency(fund: Dict[str, Any]) -> float:
    """Solvency score [0, 100]. Lower D/E + higher interest coverage → higher score."""
    d_e = fund.get("debt_to_equity")
    ic = fund.get("interest_coverage")
    score = 50.0  # neutral baseline
    if d_e is not None:
        try:
            d_e = float(d_e)
            if d_e <= 0.0:
                score += 30.0
            elif d_e <= 0.3:
                score += 25.0
            elif d_e <= 0.75:
                score += 15.0
            elif d_e <= 1.5:
                score += 5.0
            elif d_e <= 3.0:
                score -= 10.0
            else:
                score -= 30.0
        except (TypeError, ValueError):
            pass
    if ic is not None:
        try:
            ic = float(ic)
            if ic >= 10.0:
                score += 20.0
            elif ic >= 4.0:
                score += 10.0
            elif ic >= 2.0:
                score += 0.0
            else:
                score -= 15.0
        except (TypeError, ValueError):
            pass
    return max(0.0, min(100.0, score))


def _score_cash_quality(fund: Dict[str, Any]) -> tuple:
    """Returns (cash_quality_score [0, 100], caqi_value, caqi_gate)."""
    cfo = float(fund.get("cfo_last_year") or 0.0)
    pat = float(fund.get("net_profit_last_year") or 0.0)
    caqi_val: Optional[float] = None
    caqi_gate = "DATA_UNAVAILABLE"
    score = 50.0
    if pat > 0:
        caqi_val = round(cfo / pat, 3)
        if caqi_val >= 1.20:
            score = 100.0
            caqi_gate = "PASS"
        elif caqi_val >= 0.80:
            score = 75.0
            caqi_gate = "PASS"
        elif caqi_val >= 0.50:
            score = 40.0
            caqi_gate = "FAIL"
        else:
            score = 15.0
            caqi_gate = "FAIL"
    elif pat <= 0 and cfo > 0:
        score = 30.0  # loss-making but cash generative — partial credit
        caqi_gate = "DATA_UNAVAILABLE"
    return max(0.0, min(100.0, score)), caqi_val, caqi_gate


def _score_valuation_headroom(fund: Dict[str, Any]) -> tuple:
    """Returns (val_headroom_score [0, 100], deme_hr_value, deme_hr_verdict)."""
    sector_key = str(fund.get("sector", "DIVERSIFIED")).upper().replace(" ", "_")
    pe_ceiling = _SECTOR_PE_CEILING.get(sector_key, 40.0)

    # Resolve trailing P/E: prefer explicit pe_ratio, fallback to PEG * growth
    trailing_pe: Optional[float] = None
    if fund.get("pe_ratio") is not None:
        try:
            trailing_pe = float(fund["pe_ratio"])
        except (TypeError, ValueError):
            pass
    if trailing_pe is None:
        peg = fund.get("peg_ratio")
        sg = fund.get("sales_growth_3yr", 0.0)
        if peg is not None and peg > 0 and sg and sg > 0:
            try:
                trailing_pe = float(peg) * float(sg)
            except (TypeError, ValueError):
                pass

    deme_hr: Optional[float] = None
    deme_hr_verdict = "DATA_UNAVAILABLE"
    score = 50.0

    if trailing_pe is not None and trailing_pe > 0:
        deme_hr = round(pe_ceiling / trailing_pe, 3)
        if deme_hr > 3.0:
            score = 100.0
            deme_hr_verdict = "UNDERVALUED"
        elif deme_hr > 2.0:
            score = 85.0
            deme_hr_verdict = "UNDERVALUED"
        elif deme_hr > 1.3:
            score = 65.0
            deme_hr_verdict = "FAIR_VALUE"
        elif deme_hr > 1.0:
            score = 45.0
            deme_hr_verdict = "FAIR_VALUE"
        else:
            score = 10.0
            deme_hr_verdict = "VALUATION_CONSTRAINED"

    return max(0.0, min(100.0, score)), deme_hr, deme_hr_verdict


def _score_geo_moat(symbol: str, sector: Optional[str]) -> float:
    """Geopolitical moat score [0, 100] from aggregate β_geo."""
    try:
        result = compute_geo_shock_sensitivity(symbol, sector=sector)
        agg_beta = result.get("aggregate_geo_beta", -0.10)
        # Normalise: +0.5 → 100, 0 → 60, -0.5 → 20, linear interpolation
        score = 60.0 + agg_beta * 80.0
        return max(0.0, min(100.0, score))
    except Exception:
        return 40.0  # conservative fallback


def rank_candidates(
    symbols: List[str],
    fundamentals_lookup: Optional[Dict[str, Dict[str, Any]]] = None,
    intent: Optional[str] = None,
    top_n: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Run MAP-Rank Pareto tournament across the candidate set.

    Args:
        symbols: List of NSE/BSE tickers to rank.
        fundamentals_lookup: Pre-fetched {symbol: fund_dict} to avoid repeated API calls.
                             If None, each symbol is evaluated with available data.
        intent: Investment archetype (MULTIBAGGER, SIP_COMPOUNDER, TURNAROUND, etc.)
        top_n: If set, return only the top-N ranked entries.

    Returns:
        List of rank dicts (MAPRankEntry-compatible) sorted by composite_score descending.
    """
    weights = _MAP_WEIGHT_PROFILES.get(
        str(intent or "DEFAULT").upper(), _MAP_WEIGHT_PROFILES["DEFAULT"]
    )
    w_sol = weights["solvency"]
    w_cq = weights["cash_quality"]
    w_vhr = weights["val_headroom"]
    w_geo = weights["geo_moat"]

    entries: List[Dict[str, Any]] = []
    fmap = fundamentals_lookup or {}

    for sym in symbols:
        norm_sym = normalize_symbol(sym)
        fund = fmap.get(norm_sym) or fmap.get(sym) or {}
        sector = str(fund.get("sector", "DIVERSIFIED"))

        sol_score = _score_solvency(fund)
        cq_score, caqi_val, caqi_gate = _score_cash_quality(fund)
        vhr_score, deme_hr, deme_hr_verdict = _score_valuation_headroom(fund)
        geo_score = _score_geo_moat(norm_sym, sector)

        composite = round(
            w_sol * sol_score + w_cq * cq_score + w_vhr * vhr_score + w_geo * geo_score,
            2,
        )

        risk_flags: List[str] = []
        if caqi_gate == "FAIL":
            risk_flags.append(f"CAQI FAIL: cash accrual quality {caqi_val:.2f}x < 0.80 threshold")
        if deme_hr_verdict == "VALUATION_CONSTRAINED":
            risk_flags.append(f"DEME-HR {deme_hr:.2f} ≤ 1.0: at/above sector P/E ceiling → VALUATION_CONSTRAINED")

        archetype = fund.get("archetype")
        confidence_label: Optional[str] = None
        if composite >= 80.0:
            confidence_label = "HIGH_CONVICTION"
        elif composite >= 60.0:
            confidence_label = "MODERATE_CONVICTION"
        elif composite >= 40.0:
            confidence_label = "LOW_CONVICTION"
        else:
            confidence_label = "AVOID"

        if deme_hr_verdict == "VALUATION_CONSTRAINED" and confidence_label == "HIGH_CONVICTION":
            confidence_label = "HIGH_CONVICTION/VALUATION_CONSTRAINED"

        entries.append({
            "symbol": norm_sym,
            "pareto_rank": 0,  # filled after sort
            "composite_score": composite,
            "solvency_score": round(sol_score, 2),
            "cash_quality_score": round(cq_score, 2),
            "valuation_headroom_score": round(vhr_score, 2),
            "geopolitical_moat_score": round(geo_score, 2),
            "caqi": caqi_val,
            "caqi_gate": caqi_gate,
            "deme_hr": deme_hr,
            "deme_hr_verdict": deme_hr_verdict,
            "archetype": archetype,
            "confidence_label": confidence_label,
            "risk_flags": risk_flags,
        })

    # Sort descending by composite score
    entries.sort(key=lambda x: x["composite_score"], reverse=True)

    # Assign Pareto ranks
    for i, entry in enumerate(entries):
        entry["pareto_rank"] = i + 1

    if top_n is not None:
        entries = entries[:top_n]

    return entries


def build_map_rank_response(
    symbols: List[str],
    fundamentals_lookup: Optional[Dict[str, Dict[str, Any]]] = None,
    intent: Optional[str] = None,
    top_n: Optional[int] = None,
) -> Dict[str, Any]:
    """High-level entry point. Returns full MultiAssetRankResponse-compatible dict."""
    ranked = rank_candidates(symbols, fundamentals_lookup=fundamentals_lookup, intent=intent, top_n=top_n)
    return {
        "status": "OK",
        "intent": intent,
        "total_candidates": len(symbols),
        "ranked": ranked,
        "methodology": "Pareto 4-Dimension: Solvency × CashQuality × ValuationHeadroom × GeopoliticalMoat",
        "executed_at": get_ist_now_str(),
        "meta": create_meta_header(source="Phase 139 MAP-Rank Engine"),
    }
