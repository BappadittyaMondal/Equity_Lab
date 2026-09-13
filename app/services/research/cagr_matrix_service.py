"""CAGR Target Sensitivity Matrix Service — Gap Closure Feature 2.

Calculates 1Y, 3Y, and 5Y price targets and target return CAGRs across multiple
revenue/earnings growth scenarios (10%, 15%, 20%, 25%, 30%).
"""

import os
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
    is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"
    
    quote = get_quote(norm)
    curr_price = float(getattr(quote, "price", 0.0) or (quote.get("price") if isinstance(quote, dict) else 0.0) or 0.0)
    curr_pe = float(getattr(quote, "pe_ratio", 0.0) or (quote.get("pe_ratio") if isinstance(quote, dict) else 0.0) or 0.0)

    # If missing from quote, attempt audited fundamentals resolution
    if curr_price <= 0 or curr_pe <= 0:
        try:
            from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
            fund = ScreenerCloudConnector.get_company_fundamentals(norm)
            if fund:
                if curr_price <= 0 and fund.get("current_price"):
                    curr_price = float(fund["current_price"])
                if curr_pe <= 0 and fund.get("pe_ratio"):
                    curr_pe = float(fund["pe_ratio"])
                elif curr_pe <= 0 and fund.get("market_cap") and fund.get("net_profit_last_year") and float(fund["net_profit_last_year"]) > 0:
                    curr_pe = round(float(fund["market_cap"]) / float(fund["net_profit_last_year"]), 1)
        except Exception:
            pass

    if curr_price <= 0:
        curr_price = 100.0 if is_offline else 0.0
    if curr_pe <= 0:
        curr_pe = 25.0 if is_offline else 0.0

    if curr_price <= 0 or curr_pe <= 0:
        meta = create_meta_header(source="CAGR Sensitivity Matrix Service")
        meta["data_status"] = "DATA_INSUFFICIENT"
        return CAGRSensitivityMatrixResponse(
            symbol=norm,
            current_price=0.0,
            current_pe=0.0,
            base_case_cagr_pct=0.0,
            scenario_matrix=[],
            key_takeaway="DATA_INSUFFICIENT: Audited market price and P/E ratio required to compute CAGR projection matrix.",
            meta=meta,
        )

    scenarios_growth = [0.10, 0.15, 0.20, 0.25, 0.30]
    matrix_rows: List[CAGRScenarioRow] = []

    base_cagr = 15.0

    for g in scenarios_growth:
        g_pct = round(g * 100.0, 1)
        label = f"{int(g_pct)}% CAGR Growth"
        
        # Price targets assuming terminal P/E scales with expected growth (1.5x multiplier, bounded [15.0, 60.0])
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

    # 3x3 Growth x Multiple Compression Scenario Grid
    growth_cases = [
        ("BEAR_70PCT_OF_BASE", 0.14, "14% EPS CAGR (Bear Trajectory)"),
        ("BASE_CASE", 0.20, "20% EPS CAGR (Base Trajectory)"),
        ("BULL_130PCT_OF_BASE", 0.26, "26% EPS CAGR (Bull Trajectory)"),
    ]
    multiple_cases = [
        ("MULTIPLE_DERATING_MINUS_25PCT", round(curr_pe * 0.75, 1), -25.0, "Multiple Compression (-25%)"),
        ("CONSTANT_MULTIPLE", round(curr_pe * 1.0, 1), 0.0, "Constant Multiple (0%)"),
        ("MULTIPLE_EXPANSION_PLUS_25PCT", round(curr_pe * 1.25, 1), 25.0, "Multiple Expansion (+25%)"),
    ]

    cells = []
    for g_id, g_val, g_lbl in growth_cases:
        for m_id, exit_pe, pe_delta_pct, m_lbl in multiple_cases:
            pe_mult = exit_pe / curr_pe if curr_pe > 0 else 1.0
            p3 = curr_price * ((1.0 + g_val) ** 3) * pe_mult
            p5 = curr_price * ((1.0 + g_val) ** 5) * pe_mult
            cagr3 = (((p3 / curr_price) ** (1/3)) - 1) * 100.0 if curr_price > 0 else 0.0
            cagr5 = (((p5 / curr_price) ** (1/5)) - 1) * 100.0 if curr_price > 0 else 0.0
            cells.append({
                "growth_scenario": g_id,
                "growth_label": g_lbl,
                "eps_cagr_pct": round(g_val * 100.0, 1),
                "multiple_scenario": m_id,
                "multiple_label": m_lbl,
                "exit_pe": exit_pe,
                "multiple_expansion_pct": pe_delta_pct,
                "target_price_3y": round(p3, 2),
                "investor_cagr_3y_pct": round(cagr3, 2),
                "target_price_5y": round(p5, 2),
                "investor_cagr_5y_pct": round(cagr5, 2),
            })

    scenario_grid_3x3 = {
        "methodology": "3x3_GROWTH_MULTIPLE_COMPRESSION_MATRIX",
        "entry_price": round(curr_price, 2),
        "entry_pe": round(curr_pe, 2),
        "grid_cells_count": len(cells),
        "cells": cells,
        "key_insight": (
            f"At entry P/E of {curr_pe:.1f}x, a -25% multiple de-rating to {curr_pe*0.75:.1f}x "
            f"yields {cells[0]['investor_cagr_3y_pct']}% 3Y CAGR under bear growth (14%), "
            f"and {cells[3]['investor_cagr_3y_pct']}% 3Y CAGR under base growth (20%)."
        )
    }

    takeaway = (
        f"{norm} trading at P/E {curr_pe:.1f}x (Price ₹{curr_price:.2f}). "
        f"Under base 20% scenario growth sensitivity, hypothetical 3-year level is ₹{matrix_rows[2].target_price_3y} "
        f"({matrix_rows[2].projected_return_cagr_3y_pct}% CAGR sensitivity). "
        f"Under 3x3 scenario matrix, -25% multiple de-rating produces {cells[3]['investor_cagr_3y_pct']}% 3Y CAGR."
    )

    meta = create_meta_header(source=f"IERL CAGR Matrix Engine ({norm})")
    meta["nature"] = "SCENARIO_GROWTH_SENSITIVITY"
    meta["methodology"] = "Scenario Growth Sensitivity Grid (PE Exit Multiple x Fundamental Earnings Trajectory). Not a point forecast or guaranteed directional return."

    return CAGRSensitivityMatrixResponse(
        symbol=norm,
        current_price=round(curr_price, 2),
        current_pe=round(curr_pe, 2),
        base_case_cagr_pct=base_cagr,
        scenario_matrix=matrix_rows,
        key_takeaway=takeaway,
        scenario_grid_3x3=scenario_grid_3x3,
        meta=meta,
    )

