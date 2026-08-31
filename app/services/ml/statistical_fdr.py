"""Benjamini-Hochberg False Discovery Rate (FDR) Multi-Testing Control.

Guards against statistical data dredging and false positives when 46+ strategy
and screening engines run hypothesis tests simultaneously.
"""

from typing import List, Dict, Any, Tuple
import numpy as np


def benjamini_hochberg_fdr(p_values: List[float], alpha: float = 0.05) -> List[Dict[str, Any]]:
    """Applies the Benjamini-Hochberg procedure to control False Discovery Rate (FDR).

    Args:
        p_values: List of raw p-values from multi-engine screenings.
        alpha: Target False Discovery Rate threshold (default: 0.05).

    Returns:
        List of dicts containing original index, raw p-value, adjusted p-value, and discovery status.
    """
    m = len(p_values)
    if m == 0:
        return []

    # Sort p-values while preserving original indices
    indexed_p = sorted(enumerate(p_values), key=lambda x: x[1])
    
    adjusted_p_values = [1.0] * m
    # Step-up adjustment: p_adj = min(1.0, p_(i) * m / i)
    # Ensure monotonicity from largest to smallest
    min_adj = 1.0
    for rank_1indexed, (orig_idx, p) in reversed(list(enumerate(indexed_p, start=1))):
        adj = min(1.0, p * m / rank_1indexed)
        min_adj = min(min_adj, adj)
        adjusted_p_values[orig_idx] = round(float(min_adj), 6)

    results = []
    for orig_idx, p in enumerate(p_values):
        adj_p = adjusted_p_values[orig_idx]
        results.append({
            "index": orig_idx,
            "raw_p_value": round(float(p), 6),
            "adjusted_p_value": adj_p,
            "is_significant": adj_p <= alpha,
            "fdr_threshold": alpha
        })

    return results
