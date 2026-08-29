"""Central mathematical and financial utility functions for Equity Lab.
"""

from typing import Optional


def calculate_cagr(start_val: Optional[float], end_val: Optional[float], num_years: Optional[float]) -> Optional[float]:
    """Calculate Compound Annual Growth Rate (CAGR) percentage.

    Args:
        start_val: Initial positive value (e.g. revenue, EPS)
        end_val: Final positive value
        num_years: Number of elapsed years (> 0)

    Returns:
        CAGR as a percentage float rounded to 2 decimals (e.g., 18.5 for 18.5%),
        or None if inputs are invalid/non-positive.
    """
    if start_val is None or end_val is None or num_years is None:
        return None
    try:
        start_f = float(start_val)
        end_f = float(end_val)
        years_f = float(num_years)
    except (ValueError, TypeError):
        return None

    if start_f <= 0.0 or end_f <= 0.0 or years_f <= 0.0:
        return None

    cagr_pct = ((end_f / start_f) ** (1.0 / years_f) - 1.0) * 100.0
    return round(cagr_pct, 2)
