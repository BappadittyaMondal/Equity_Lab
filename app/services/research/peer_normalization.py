"""Business-Model Peer Sets & Cross-Sector Normalization Engine (§44, §52).

Builds unit-economics business-model peer sets and converts raw fundamental scores into
sector-relative z-scores and percentile ranks to eliminate sector valuation and ratio bias.
"""

import math
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.market_data import normalize_symbol, create_meta_header


# Benchmark Sector Distributions (Mean, Std) for Cross-Sector Normalization
SECTOR_BENCHMARKS = {
    "FINANCIALS": {"roic_mean": 15.2, "roic_std": 3.5, "pe_mean": 18.5, "pe_std": 6.0},
    "PHARMA": {"roic_mean": 18.5, "roic_std": 5.2, "pe_mean": 28.0, "pe_std": 8.5},
    "IT_SERVICES": {"roic_mean": 28.0, "roic_std": 7.0, "pe_mean": 26.0, "pe_std": 7.0},
    "CONSUMER": {"roic_mean": 24.0, "roic_std": 8.0, "pe_mean": 45.0, "pe_std": 12.0},
    "REAL_ESTATE": {"roic_mean": 12.0, "roic_std": 4.0, "pe_mean": 32.0, "pe_std": 10.0},
    "MANUFACTURING": {"roic_mean": 16.0, "roic_std": 4.5, "pe_mean": 22.0, "pe_std": 6.5},
    "PSU": {"roic_mean": 14.0, "roic_std": 4.0, "pe_mean": 14.0, "pe_std": 4.5},
    "DEFAULT": {"roic_mean": 17.0, "roic_std": 5.0, "pe_mean": 24.0, "pe_std": 7.0}
}


def _norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function approximation."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def evaluate_peer_normalization(
    symbol: str,
    sector: str = "MANUFACTURING",
    raw_scores: Optional[Dict[str, float]] = None,
    as_of: Optional[datetime] = None
) -> Dict[str, Any]:
    """Computes sector-relative z-scores and percentile ranks for MIVS inputs."""
    norm_symbol = normalize_symbol(symbol)
    sector_upper = sector.upper().strip()
    scores = raw_scores or {}
    evidence = []

    if not scores:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Peer Normalization Engine: No raw score inputs provided for %s. Setting sector_relative_percentile to INSUFFICIENT_DATA.", norm_symbol)
        evidence.append("Sector-Relative Composite Percentile: INSUFFICIENT_DATA (No fundamental or valuation metrics available for normalization)")
        return {
            "symbol": norm_symbol,
            "sector": sector_upper,
            "executed_at": datetime.now().isoformat(),
            "sector_relative_percentile": None,
            "data_status": "INSUFFICIENT_DATA",
            "z_scores": {},
            "percentile_ranks": {},
            "evidence": evidence,
            "meta": create_meta_header(source="Peer Normalization Engine (§44, §52)")
        }

    bench = SECTOR_BENCHMARKS.get(sector_upper, SECTOR_BENCHMARKS["DEFAULT"])

    # Compute Z-Scores and Percentiles
    z_scores = {}
    percentile_ranks = {}

    for metric_key, raw_val in scores.items():
        if "roic" in metric_key.lower() or "quality" in metric_key.lower():
            mean, std = bench["roic_mean"], bench["roic_std"]
            z = (raw_val - mean) / std if std > 0 else 0.0
            p = round(_norm_cdf(z) * 100.0, 1)
        elif "pe" in metric_key.lower() or "valuation" in metric_key.lower():
            mean, std = bench["pe_mean"], bench["pe_std"]
            z = (mean - raw_val) / std if std > 0 else 0.0  # Lower PE = higher percentile
            p = round(_norm_cdf(z) * 100.0, 1)
        else:
            # Generic 0-100 score normalization
            z = (raw_val - 50.0) / 15.0
            p = round(_norm_cdf(z) * 100.0, 1)

        z_scores[metric_key] = round(z, 2)
        percentile_ranks[metric_key] = p

    # Overall Sector-Relative Percentile
    avg_percentile = round(sum(percentile_ranks.values()) / max(1, len(percentile_ranks)), 1) if percentile_ranks else 50.0

    evidence.append(f"Business-Model Peer Set Sector: {sector_upper}")
    evidence.append(f"Sector-Relative Composite Percentile: {avg_percentile}th Percentile (Z-Score Normalized)")

    return {
        "symbol": norm_symbol,
        "sector": sector_upper,
        "executed_at": datetime.now().isoformat(),
        "sector_relative_percentile": avg_percentile,
        "z_scores": z_scores,
        "percentile_ranks": percentile_ranks,
        "evidence": evidence,
        "meta": create_meta_header(source="Peer Normalization Engine (§44, §52)")
    }


def compute_5_stage_dupont_and_dol(
    net_income: float,
    ebt: float,
    ebit: float,
    revenue: float,
    total_assets: float,
    equity: float,
    prev_ebit: Optional[float] = None,
    prev_revenue: Optional[float] = None,
) -> Dict[str, Any]:
    """Computes 5-stage DuPont ROE decomposition and Degree of Operating Leverage (DOL).

    DuPont ROE = Tax Effect * Interest Burden * EBIT Margin * Asset Turnover * Leverage Factor
    DOL = (% Change in EBIT) / (% Change in Revenue)
    """
    if revenue <= 0 or total_assets <= 0 or equity <= 0 or ebit <= 0 or ebt <= 0:
        return {
            "dupont_roe_pct": 0.0,
            "tax_effect": 1.0,
            "interest_burden": 1.0,
            "ebit_margin_pct": 0.0,
            "asset_turnover": 0.0,
            "financial_leverage": 1.0,
            "degree_of_operating_leverage": 0.0,
            "operating_leverage_tier": "LOW",
        }

    tax_effect = round(net_income / ebt, 4)
    interest_burden = round(ebt / ebit, 4)
    ebit_margin = round((ebit / revenue) * 100.0, 2)
    asset_turnover = round(revenue / total_assets, 2)
    leverage = round(total_assets / equity, 2)

    dupont_roe = round((tax_effect * interest_burden * (ebit / revenue) * asset_turnover * leverage) * 100.0, 2)

    dol = 0.0
    if prev_ebit is not None and prev_revenue is not None and prev_ebit > 0 and prev_revenue > 0:
        pct_change_ebit = (ebit - prev_ebit) / prev_ebit
        pct_change_rev = (revenue - prev_revenue) / prev_revenue
        if abs(pct_change_rev) > 0.001:
            dol = round(pct_change_ebit / pct_change_rev, 2)

    if dol >= 2.5:
        dol_tier = "HIGH_CONVEXITY"
    elif dol >= 1.5:
        dol_tier = "MODERATE_CONVEXITY"
    else:
        dol_tier = "STABLE"

    return {
        "dupont_roe_pct": dupont_roe,
        "tax_effect": tax_effect,
        "interest_burden": interest_burden,
        "ebit_margin_pct": ebit_margin,
        "asset_turnover": asset_turnover,
        "financial_leverage": leverage,
        "degree_of_operating_leverage": dol,
        "operating_leverage_tier": dol_tier,
    }

