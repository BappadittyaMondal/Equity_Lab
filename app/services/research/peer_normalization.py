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
