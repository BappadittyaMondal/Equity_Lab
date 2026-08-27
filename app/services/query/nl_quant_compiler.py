"""Natural-Language Quant Query Compiler Engine.

Translates plain-English user queries into structured quantitative execution filters
across Equity Lab's scoring engines.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from app.services.market_data import create_meta_header, get_ist_now_str

logger = logging.getLogger(__name__)


class NLQuantCompiler:
    """Natural-Language Query Compiler for Quantitative Filters."""

    @classmethod
    def compile_natural_language_query(cls, user_query: str) -> Dict[str, Any]:
        """Translates plain English query into explicit engine parameter constraints."""
        text = user_query.lower()
        extracted_filters = {}

        # 1. Market Cap Constraints
        mcap_match = re.search(r'(under|below|less than)\s*(?:₹|rs\.?|inr)?\s*(\d+)\s*(cr|crore|k crore)?', text)
        if mcap_match:
            val = float(mcap_match.group(2))
            unit = mcap_match.group(3) or "cr"
            if "k" in unit or val < 100:  # e.g., 2k crore
                val *= 1000
            extracted_filters["max_market_cap_cr"] = val

        # 2. Free Cash Flow Constraints
        if "fcf" in text or "free cash flow" in text:
            if "positive" in text or "good" in text or "> 0" in text:
                extracted_filters["min_fcf_cr"] = 0.0
            fcf_match = re.search(r'fcf\s*(?:>|greater than|above)\s*(\d+)', text)
            if fcf_match:
                extracted_filters["min_fcf_cr"] = float(fcf_match.group(1))

        # 3. Leverage / Debt Constraints
        if "debt-free" in text or "zero debt" in text:
            extracted_filters["max_debt_to_equity"] = 0.1
        elif "low debt" in text:
            extracted_filters["max_debt_to_equity"] = 0.5

        # 4. Growth & ROCE Constraints
        if "high growth" in text or "fast growth" in text:
            extracted_filters["min_sales_growth_3yr"] = 25.0
            extracted_filters["min_pat_growth_3yr"] = 25.0
        if "high roce" in text or "capital efficient" in text:
            extracted_filters["min_roce_3yr"] = 20.0

        # 5. Sector Targeting
        sectors = []
        if "defense" in text or "defence" in text:
            sectors.append("DEFENSE")
        if "capital goods" in text or "engineering" in text:
            sectors.append("HEAVY_ENGINEERING")
        if "transformer" in text or "power" in text or "renewable" in text:
            sectors.append("RENEWABLE")
        if "it" in text or "software" in text:
            sectors.append("IT")

        if sectors:
            extracted_filters["target_sectors"] = sectors

        return {
            "user_query": user_query,
            "compiled_filters": extracted_filters,
            "interpretation": f"Compiled query into {len(extracted_filters)} quantitative engine constraints.",
            "executed_at": get_ist_now_str(),
            "meta": create_meta_header(source="NL Quant Query Compiler")
        }
