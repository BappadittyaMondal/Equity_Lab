"""CAGR Target Sensitivity Matrix Service — Gap Closure Feature 2.

Calculates 1Y, 3Y, and 5Y price targets and target return CAGRs across multiple
revenue/earnings growth scenarios (10%, 15%, 20%, 25%, 30%).
"""

import logging
from typing import List, Optional

from app.models.schemas import (
    CAGRScenarioRow,
    CAGRSensitivityMatrixResponse,
)
from app.services.market_data import (
    normalize_symbol, get_quote, create_meta_header
)

logger = logging.getLogger(__name__)


def generate_cagr_sensitivity_matrix(symbol: str) -> CAGRSensitivityMatrixResponse:
    """Generate 5-scenario CAGR sensitivity matrix for a symbol."""
    norm = normalize_symbol(symbol)
    
    quote = get_quote(norm)
    curr_price = float(getattr(quote, "price", 100.0) or 100.0)
    curr_pe = float(getattr(quote, "pe_ratio", 25.0) or 25.0)
    if curr_price <= 0:
        curr_price = 100.0
    if curr_pe <= 0:
        curr_pe = 25.0

    scenarios_growth = [0.10, 0.15, 0.20, 0.25, 0.30]
    matrix_rows: List[CAGRScenarioRow] = []

    base_cagr = 15.0

    for g in scenarios_growth:
        g_pct = round(g * 100.0, 1)
        label = f"{int(g_pct)}% CAGR Growth"
        
        # Price targets assuming terminal P/E rating scales modestly with growth
        # Target PE = min(curr_pe, g_pct * 1.2)
        target_pe = max(15.0, min(60.0, g_pct * 1.5))
        pe_expansion_factor = target_pe / curr_pe if curr_pe > 0 else 1.0

        p1 = curr_price * (1.0 + g) * (1.0 + (pe_expansion_factor - 1.0) * 0.3)
        p3 = curr_price * ((1.0 + g) ** 3) * (1.0 + (pe_expansion_factor - 1.0) * 0.7)
        p5 = curr_price * ((1.0 + g) ** 5) * pe_expansion_factor

        ret_3y_cagr = (((p3 / curr_price) ** (1/3)) - 1) * 100.0
        ret_5y_cagr = (((p5 / curr_price) ** (1/5)) - 1) * 100.0
        
        # Margin of safety = difference between growth rate and implied P/E PEG ratio
        peg = curr_pe / g_pct if g_pct > 0 else 2.0
        mos = max(0.0, min(50.0, round((1.5 - peg) * 33.3, 1)))

        matrix_rows.append(CAGRScenarioRow(
            growth_scenario_label=label,
            revenue_eps_cagr_pct=g_pct,
            target_price_1y=round(p1, 2),
            target_price_3y=round(p3, 2),
            target_price_5y=round(p5, 2),
            projected_return_cagr_3y_pct=round(ret_3y_cagr, 2),
            projected_return_cagr_5y_pct=round(ret_5y_cagr, 2),
            margin_of_safety_pct=mos,
        ))

    takeaway = (
        f"{norm} trading at P/E {curr_pe:.1f}x (Price ₹{curr_price:.2f}). "
        f"At base 20% EPS growth, projected 3-year target is ₹{matrix_rows[2].target_price_3y} "
        f"({matrix_rows[2].projected_return_cagr_3y_pct}% return CAGR)."
    )

    return CAGRSensitivityMatrixResponse(
        symbol=norm,
        current_price=round(curr_price, 2),
        current_pe=round(curr_pe, 2),
        base_case_cagr_pct=base_cagr,
        scenario_matrix=matrix_rows,
        key_takeaway=takeaway,
        meta=create_meta_header(source=f"IERL CAGR Matrix Engine ({norm})"),
    )
