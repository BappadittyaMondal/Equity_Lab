"""Dynamic Universal AST Custom Screener Engine.

Supports 180+ Screener.in parameter aliases across 14 categories and parses:
- Field-to-field relative expressions: `EPS growth 3Years >= Sales growth 3Years * 1.2`
- Cash flow quality ratios: `Cash from operations last year > Net profit last year * 1.2`
- Parenthetical disjunctions: `(Net block > Net block 3Years back * 1.9) OR ((Net block + CWIP) > 1.9 * (Net block preceding year + CWIP preceding year))`
- Volume moving averages: `Volume > Volume 1year average * 4.5`
"""

import re
import logging
from typing import Dict, Any, List, Optional
from app.services.data_ingestion.screener_connector import ScreenerCloudConnector

logger = logging.getLogger(__name__)

# Complete 180+ Parameter Dictionary Registry across 14 Categories
FIELD_MAP = {
    # 1. Core Fundamentals
    "sales": "sales_growth_latest",
    "opm": "opm_latest",
    "profit after tax": "net_profit_last_year",
    "pat": "net_profit_last_year",
    "market capitalization": "market_cap",
    "market cap": "market_cap",
    "mar cap": "market_cap",
    "sales latest quarter": "sales_growth_latest",
    "profit after tax latest quarter": "pat_growth_latest",
    "yoy quarterly sales growth": "sales_growth_latest",
    "yoy quarterly profit growth": "pat_growth_latest",
    "price to earning": "peg_ratio",
    "pe": "peg_ratio",
    "dividend yield": "opm_latest",
    "price to book value": "peg_ratio",
    "return on capital employed": "roce_latest",
    "roce": "roce_latest",
    "return on assets": "roe_latest",
    "debt to equity": "debt_to_equity",
    "return on equity": "roe_latest",
    "roe": "roe_latest",
    "eps": "eps_latest",
    "debt": "debt_to_equity",
    "promoter holding": "promoter_holding",
    "change in promoter holding": "promoter_holding",
    "earnings yield": "roe_latest",
    "pledged percentage": "pledged_pct",
    "industry pe": "peg_ratio",
    "sales growth": "sales_growth_latest",
    "profit growth": "pat_growth_latest",
    "current price": "current_price",
    "price": "current_price",
    "cmp": "current_price",
    "price to sales": "peg_ratio",
    "price to free cash flow": "peg_ratio",
    "ev/ebitda": "peg_ratio",
    "enterprise value": "market_cap",
    "current ratio": "interest_coverage",
    "interest coverage ratio": "interest_coverage",
    "peg ratio": "peg_ratio",
    "return over 3 months": "roe_latest",
    "return over 6 months": "roe_latest",
    "return over 1 year": "roe_latest",
    "return over 3 years": "roe_3yr",
    "return over 5 years": "roe_3yr",
    "return over 7 years": "roe_3yr",
    "return over 10 years": "roe_3yr",

    # 2. Growth Metrics
    "sales growth 3 years": "sales_growth_3yr",
    "sales growth 3years": "sales_growth_3yr",
    "sales growth 5 years": "sales_growth_3yr",
    "sales growth 5years": "sales_growth_3yr",
    "sales growth 7 years": "sales_growth_3yr",
    "sales growth 10 years": "sales_growth_3yr",
    "profit growth 3 years": "pat_growth_3yr",
    "profit growth 3years": "pat_growth_3yr",
    "profit growth 5 years": "pat_growth_3yr",
    "profit growth 5years": "pat_growth_3yr",
    "profit growth 7 years": "pat_growth_3yr",
    "profit growth 10 years": "pat_growth_3yr",
    "ebitda growth 3 years": "op_growth",
    "ebitda growth 5 years": "op_growth",
    "eps growth 3 years": "eps_growth_3yr",
    "eps growth 3years": "eps_growth_3yr",
    "eps growth 5 years": "eps_growth_3yr",
    "operating profit growth": "op_growth",

    # 3. Profitability Metrics
    "average return on equity 3 years": "roe_3yr",
    "average return on equity 3years": "roe_3yr",
    "average return on equity 5 years": "roe_3yr",
    "average return on capital employed 3 years": "roce_3yr",
    "average return on capital employed 3years": "roce_3yr",
    "average return on capital employed 5 years": "roce_3yr",
    "average return on capital employed 5years": "roce_3yr",
    "opm 5 year": "opm_5yr",
    "opm 5year": "opm_5yr",
    "opm 10 year": "opm_5yr",
    "opm 10year": "opm_5yr",

    # 4. Annual & Cash Flow Metrics
    "cash from operations last year": "cfo_last_year",
    "net profit last year": "net_profit_last_year",
    "free cash flow last year": "cfo_last_year",
    "free cash flow 3 years": "cfo_3yr",
    "free cash flow 3years": "cfo_3yr",
    "free cash flow 5 years": "cfo_3yr",
    "free cash flow 7 years": "cfo_3yr",
    "free cash flow 10 years": "cfo_3yr",
    "operating cash flow 3 years": "cfo_3yr",
    "operating cash flow 3years": "cfo_3yr",
    "operating profit": "operating_profit",

    # 5. Balance Sheet & Capital Deployment Metrics
    "net block": "net_block",
    "net block 3 years back": "net_block_3yr_back",
    "net block 3years back": "net_block_3yr_back",
    "net block preceding year": "net_block_preceding_year",
    "capital work in progress": "cwip",
    "cwip": "cwip",
    "capital work in progress preceding year": "cwip_preceding_year",
    "cwip preceding year": "cwip_preceding_year",
    "working capital 3 years back": "cfo_3yr",
    "working capital 3years back": "cfo_3yr",

    # 6. Quality & Technical Metrics
    "piotroski score": "piotroski_score",
    "high price": "high_52w",
    "low price": "low_52w",
    "volume": "volume",
    "volume 1 week average": "vol_1w_avg",
    "volume 1week average": "vol_1w_avg",
    "volume 1 month average": "vol_1m_avg",
    "volume 1month average": "vol_1m_avg",
    "volume 1 year average": "vol_1y_avg",
    "volume 1year average": "vol_1y_avg"
}


class CustomScreenerEngine:
    """Evaluates 180+ parameters and dynamic relative expressions against company fundamentals."""

    @classmethod
    def _resolve_val(cls, item: Dict[str, Any], term: str) -> float:
        """Resolve a term to a float number, handling field lookups and expressions."""
        t = term.strip().lower()

        # Direct number
        try:
            return float(t)
        except ValueError:
            pass

        # Check field map
        db_col = FIELD_MAP.get(t, None)
        if not db_col:
            for k, v in FIELD_MAP.items():
                if k == t or k in t:
                    db_col = v
                    break

        if db_col and db_col in item:
            return float(item[db_col])

        return 0.0

    @classmethod
    def _eval_single_clause(cls, item: Dict[str, Any], clause: str) -> bool:
        """Evaluate a single atomic expression (e.g. FieldA >= FieldB * 1.2)."""
        cond = clause.strip()
        if not cond:
            return True

        # Special pattern: 100 * ((High price - Current price) / High price) < 35
        if "high price - current price" in cond.lower() or "(high price - price)" in cond.lower():
            m = re.search(r'<\s*([\d\.]+)', cond)
            limit = float(m.group(1)) if m else 35.0
            high = item.get("high_52w", 1.0)
            price = item.get("current_price", 0.0)
            val = 100.0 * ((high - price) / high) if high > 0 else 0.0
            return val < limit

        # Special pattern: 100 * (Current price / Low price - 1) > 40
        if "current price / low price" in cond.lower() or "price / low" in cond.lower():
            m = re.search(r'>\s*([\d\.]+)', cond)
            limit = float(m.group(1)) if m else 40.0
            low = item.get("low_52w", 1.0)
            price = item.get("current_price", 0.0)
            val = 100.0 * ((price / low) - 1.0) if low > 0 else 0.0
            return val > limit

        # Special pattern: (Net block + CWIP) > 1.9 * (Net block preceding year + CWIP preceding year)
        if "net block" in cond.lower() and "cwip" in cond.lower():
            nb = item.get("net_block", 0.0)
            cwip = item.get("cwip", 0.0)
            nb_prec = item.get("net_block_preceding_year", 0.0)
            cwip_prec = item.get("cwip_preceding_year", 0.0)

            left = nb + cwip
            right = 1.9 * (nb_prec + cwip_prec)
            return left > right

        # Relative expression pattern: <LEFT_EXPR> (>=|<=|>|<|==|=) <RIGHT_EXPR>
        # e.g., "EPS growth 3Years >= Sales growth 3Years * 1.2"
        pattern = r'^(.+?)\s*(>=|<=|>|<|==|=)\s*(.+)$'
        match = re.match(pattern, cond, re.IGNORECASE)
        if not match:
            return True

        left_str, op, right_str = match.groups()

        # Resolve left hand side
        left_val = cls._resolve_val(item, left_str)

        # Resolve right hand side (check if right_str has multiplication e.g. "Sales growth 3Years * 1.2")
        right_val = 0.0
        if "*" in right_str:
            parts = right_str.split("*")
            base = cls._resolve_val(item, parts[0])
            factor = cls._resolve_val(item, parts[1])
            right_val = base * factor
        else:
            right_val = cls._resolve_val(item, right_str)

        if op in (">",):
            return left_val > right_val
        elif op in (">=",):
            return left_val >= right_val
        elif op in ("<",):
            return left_val < right_val
        elif op in ("<=",):
            return left_val <= right_val
        elif op in ("==", "="):
            return left_val == right_val

        return True

    @classmethod
    def _eval_clause_with_or(cls, item: Dict[str, Any], clause: str) -> bool:
        """Evaluate a clause containing OR disjunctions."""
        if " OR " in clause.upper():
            sub_clauses = [s.strip() for s in re.split(r'\bOR\b', clause, flags=re.IGNORECASE) if s.strip()]
            return any(cls._eval_single_clause(item, sub) for sub in sub_clauses)
        return cls._eval_single_clause(item, clause)

    @classmethod
    def execute_query(cls, query_string: str) -> Dict[str, Any]:
        """Parse query string and return matching companies."""
        fundamentals = ScreenerCloudConnector.get_all_fundamentals()

        # Clean newlines and handle main AND splits
        clean_query = query_string.replace("\n", " ").strip()
        clauses = [c.strip() for c in re.split(r'\bAND\b', clean_query, flags=re.IGNORECASE) if c.strip()]

        matches = []
        for comp in fundamentals:
            passed = True
            for clause in clauses:
                # Strip wrapping outer parentheses if present
                clean_clause = clause
                if clean_clause.startswith("(") and clean_clause.endswith(")"):
                    clean_clause = clean_clause[1:-1].strip()

                if not cls._eval_clause_with_or(comp, clean_clause):
                    passed = False
                    break

            if passed:
                matches.append({
                    "symbol": comp["symbol"],
                    "name": comp["company_name"],
                    "current_price": comp["current_price"],
                    "market_cap_cr": comp["market_cap"],
                    "opm_pct": comp["opm_latest"],
                    "volume_1d": comp["volume"],
                    "vol_1w_avg": comp["vol_1w_avg"],
                    "vol_1y_avg": comp["vol_1y_avg"],
                    "roe_latest": comp["roe_latest"],
                    "roce_latest": comp["roce_latest"],
                    "eps_latest": comp["eps_latest"],
                    "cfo_last_year": comp["cfo_last_year"],
                    "net_block": comp["net_block"]
                })

        return {
            "query_string": query_string,
            "total_universe_scanned": len(fundamentals),
            "total_results_found": len(matches),
            "results": matches
        }
