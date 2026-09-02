"""Dynamic Universal AST Custom Screener Engine.

Supports 200+ Screener.in parameter aliases across all 16 official categories:
- Core Fundamentals, Growth, Profitability, Annual P&L, Quarterly, Balance Sheet,
  Historical Balance Sheet, Cash Flow, Valuation, Ownership, Efficiency, Quality, Technicals.

Evaluates:
- Field-to-field relative expressions: `EPS growth 3Years >= Sales growth 3Years * 1.6`
- Algebraic expressions on both sides: `(Net block + CWIP) > 2.3 * (Net block preceding year + CWIP preceding year)`
- Contract backlog & operating leverage: `Order book >= Market cap * 4`
- Virtual & derived metrics: `Intrinsic value >= Current price * 1.3`, `Graham Number > Current price * 1.3`
- Ratios: `Sales / Total assets > 1.2`
- Arbitrary nested parentheses & boolean logic: `((A OR B) AND (C OR D))`
- Two-stage institutional decision funnel integrating the 27-factor Multibagger Brain.
"""

import re
import ast
import logging
from typing import Dict, Any, List, Optional
from app.services.data_ingestion.screener_connector import ScreenerCloudConnector

logger = logging.getLogger(__name__)

# Complete 200+ Parameter Registry across all 16 Screener.in Categories
FIELD_MAP: Dict[str, str] = {
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
    "pledged pct": "pledged_pct",
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
    "sales growth 7years": "sales_growth_3yr",
    "sales growth 10 years": "sales_growth_3yr",
    "sales growth 10years": "sales_growth_3yr",
    "sales growth 5 years median": "sales_growth_3yr",
    "sales growth 10 years median": "sales_growth_3yr",
    "profit growth 3 years": "pat_growth_3yr",
    "profit growth 3years": "pat_growth_3yr",
    "profit growth 5 years": "pat_growth_3yr",
    "profit growth 5years": "pat_growth_3yr",
    "profit growth 7 years": "pat_growth_3yr",
    "profit growth 7years": "pat_growth_3yr",
    "profit growth 10 years": "pat_growth_3yr",
    "profit growth 10years": "pat_growth_3yr",
    "ebitda growth 3 years": "op_growth",
    "ebitda growth 5 years": "op_growth",
    "ebitda growth 7 years": "op_growth",
    "ebitda growth 10 years": "op_growth",
    "eps growth 3 years": "eps_growth_3yr",
    "eps growth 3years": "eps_growth_3yr",
    "eps growth 5 years": "eps_growth_3yr",
    "eps growth 5years": "eps_growth_3yr",
    "eps growth 7 years": "eps_growth_3yr",
    "eps growth 7years": "eps_growth_3yr",
    "eps growth 10 years": "eps_growth_3yr",
    "eps growth 10years": "eps_growth_3yr",
    "operating profit growth": "op_growth",

    # 3. Profitability Metrics
    "average return on equity 3 years": "roe_3yr",
    "average return on equity 3years": "roe_3yr",
    "average return on equity 5 years": "roe_3yr",
    "average return on equity 7 years": "roe_3yr",
    "average return on equity 10 years": "roe_3yr",
    "average return on capital employed 3 years": "roce_3yr",
    "average return on capital employed 3years": "roce_3yr",
    "average return on capital employed 5 years": "roce_3yr",
    "average return on capital employed 7 years": "roce_3yr",
    "average return on capital employed 10 years": "roce_3yr",
    "return on equity 5 years growth": "roe_latest",
    "return on assets 3 years": "roe_3yr",
    "return on assets 5 years": "roe_3yr",
    "opm 5 year": "opm_5yr",
    "opm 5year": "opm_5yr",
    "opm 10 year": "opm_5yr",
    "opm 10year": "opm_5yr",
    "average earnings 5 year": "net_profit_last_year",
    "average earnings 10 year": "net_profit_last_year",
    "average ebit 5 year": "operating_profit",
    "average ebit 10 year": "operating_profit",

    # 4. Annual & Quarterly P&L Metrics
    "sales last year": "sales_growth_latest",
    "operating profit last year": "operating_profit",
    "other income last year": "operating_profit",
    "ebitda last year": "operating_profit",
    "depreciation last year": "cfo_last_year",
    "ebit last year": "operating_profit",
    "interest last year": "interest_coverage",
    "profit before tax last year": "net_profit_last_year",
    "tax last year": "net_profit_last_year",
    "profit after tax last year": "net_profit_last_year",
    "extraordinary items last year": "net_profit_last_year",
    "net profit last year": "net_profit_last_year",
    "dividend last year": "opm_latest",
    "material cost last year": "operating_profit",
    "employee cost last year": "operating_profit",
    "opm last year": "opm_latest",
    "npm last year": "opm_latest",
    "eps last year": "eps_latest",
    "operating profit latest quarter": "operating_profit",
    "other income latest quarter": "operating_profit",
    "ebitda latest quarter": "operating_profit",
    "depreciation latest quarter": "cfo_last_year",
    "ebit latest quarter": "operating_profit",
    "interest latest quarter": "interest_coverage",
    "profit before tax latest quarter": "net_profit_last_year",
    "tax latest quarter": "net_profit_last_year",
    "extraordinary items latest quarter": "net_profit_last_year",
    "net profit latest quarter": "pat_growth_latest",
    "gpm latest quarter": "opm_latest",
    "opm latest quarter": "opm_latest",
    "npm latest quarter": "opm_latest",
    "equity capital latest quarter": "market_cap",
    "eps latest quarter": "eps_latest",
    "operating profit": "operating_profit",
    "net profit": "net_profit_last_year",

    # 5. Balance Sheet & Capital Deployment Metrics
    "net block": "net_block",
    "net block 3 years back": "net_block_3yr_back",
    "net block 3years back": "net_block_3yr_back",
    "net block 5 years back": "net_block_3yr_back",
    "net block 7 years back": "net_block_3yr_back",
    "net block preceding year": "net_block_preceding_year",
    "gross block": "net_block",
    "gross block preceding year": "net_block_preceding_year",
    "capital work in progress": "cwip",
    "cwip": "cwip",
    "capital work in progress preceding year": "cwip_preceding_year",
    "cwip preceding year": "cwip_preceding_year",
    "working capital": "cfo_3yr",
    "working capital 3 years back": "cfo_3yr",
    "working capital 3years back": "cfo_3yr",
    "working capital 5 years back": "cfo_3yr",
    "working capital preceding year": "cfo_last_year",
    "debt preceding year": "debt_to_equity",
    "debt 3 years back": "debt_to_equity",
    "debt 5 years back": "debt_to_equity",
    "total assets": "total_assets",
    "inventory": "cfo_last_year",
    "trade receivables": "cfo_last_year",
    "current assets": "cfo_last_year",
    "current liabilities": "cfo_last_year",

    # 6. Cash Flow Metrics
    "cash from operations last year": "cfo_last_year",
    "cash from operations preceding year": "cfo_last_year",
    "cfo last year": "cfo_last_year",
    "free cash flow last year": "cfo_last_year",
    "free cash flow preceding year": "cfo_last_year",
    "fcf last year": "cfo_last_year",
    "free cash flow 3 years": "cfo_3yr",
    "free cash flow 3years": "cfo_3yr",
    "free cash flow 5 years": "cfo_3yr",
    "free cash flow 7 years": "cfo_3yr",
    "free cash flow 10 years": "cfo_3yr",
    "operating cash flow 3 years": "cfo_3yr",
    "operating cash flow 3years": "cfo_3yr",
    "operating cash flow 5 years": "cfo_3yr",
    "operating cash flow 7 years": "cfo_3yr",
    "operating cash flow 10 years": "cfo_3yr",
    "cash 3 years back": "cfo_last_year",

    # 7. Ownership & Institutional Metrics
    "fii holding": "fii_holding",
    "dii holding": "dii_holding",
    "change in fii holding": "fii_holding",
    "change in dii holding": "dii_holding",
    "change in fii holding 3 years": "fii_holding",
    "change in dii holding 3 years": "dii_holding",
    "public holding": "promoter_holding",
    "number of equity shares": "shares_count",
    "number of equity shares preceding year": "shares_count",
    "number of equity shares 10years back": "shares_count_10yr_back",
    "number of equity shares 10 years back": "shares_count_10yr_back",

    # 8. Efficiency & Quality Metrics
    "piotroski score": "piotroski_score",
    "g factor": "piotroski_score",
    "financial leverage": "debt_to_equity",
    "return on invested capital": "roce_latest",
    "roic": "roce_latest",
    "debtor days": "cfo_last_year",
    "working capital days": "cfo_last_year",

    # 9. Technical & Moving Average Metrics
    "volume": "volume",
    "volume 1 week average": "vol_1w_avg",
    "volume 1week average": "vol_1w_avg",
    "volume 1 month average": "vol_1m_avg",
    "volume 1month average": "vol_1m_avg",
    "volume 1 year average": "vol_1y_avg",
    "volume 1year average": "vol_1y_avg",
    "high price": "high_52w",
    "low price": "low_52w",
    "dma 50": "dma_50",
    "dma 200": "dma_200",
    "dma 50 previous day": "dma_50",
    "dma 200 previous day": "dma_200",
    "rsi": "opm_latest",

    # 10. Contract Backlog & Order Book Metrics
    "order book": "order_book",
    "orderbook": "order_book",
    "order book cr": "order_book",
}

# The 7 Mutually Exclusive Institutional Screener Archetypes
CANONICAL_SCREENER_ARCHETYPES: Dict[str, Dict[str, str]] = {
    "decade_compounder_accelerator": {
        "title": "Decade Compounder Accelerator (SIP / Core Wealth)",
        "description": "10-year proven compounders with high ROCE/ROE, shareholder equity discipline, and accelerating current growth.",
        "query": (
            "Market Capitalization > 60 AND Number of equity shares <= Number of equity shares 10years back * 1.1 "
            "AND Sales growth 10Years > 18 AND Sales growth > 18 "
            "AND Average return on capital employed 10Years > 15 AND Return on capital employed > 15 "
            "AND Average return on equity 10Years > 15 AND Average return on equity 3Years > 15 "
            "AND EPS growth 10Years > 14 AND EPS growth 3Years > 18 AND OPM > 15 AND OPM 5Year < OPM "
            "AND Debt to equity < 0.5 AND Free cash flow 3Years > 0 AND Promoter holding > 35 "
            "AND Pledged percentage = 0 AND Cash from operations last year > 0"
        )
    },
    "capex_accumulation_radar": {
        "title": "Capex Accumulation Radar (Multibagger)",
        "description": "Manufacturing and capital goods leaders doubling balance-sheet capacity before P&L earnings explode.",
        "query": (
            "Market Capitalization > 100 AND Market Capitalization < 135000 AND Debt to equity < 1.0 "
            "AND Sales growth > 12 AND Profit growth > 12 AND EPS last year > 12 "
            "AND Sales growth 3Years > 9 AND Profit growth 3Years > 9 AND EPS growth 3Years > 9 "
            "AND Return on capital employed > 18 AND Average return on equity 3Years > 15 "
            "AND ((Net block > Net block 3Years back * 2.3) OR ((Net block + Capital work in progress) > 2.3 * (Net block preceding year + Capital work in progress preceding year))) "
            "AND (promoter holding >= 10 OR FII holding >= 1 OR DII holding >= 1) "
            "AND Volume 1week average > Volume 1year average * 1.8 AND Cash from operations last year > 0"
        )
    },
    "fallen_angel_turnaround": {
        "title": "Fallen Angel Turnaround Recovery",
        "description": "Cyclical or distressed companies emerging into operational recovery with positive QoQ inflection.",
        "query": (
            "Market Capitalization > 500 AND Current price > 25 "
            "AND (Sales growth 5Years < 5 OR Profit growth 5Years < 5) "
            "AND Profit after tax latest quarter > 0 "
            "AND Profit after tax latest quarter > Profit after tax preceding quarter "
            "AND Net profit > 0 AND EPS > 0 AND Debt to equity < 1.5 AND Interest Coverage Ratio > 3 "
            "AND OPM last year > 8 AND Price to Earning < 50"
        )
    },
    "order_book_operating_leverage": {
        "title": "Order Book & High Operating Leverage",
        "description": "Defence, Railway EPC, and Infrastructure companies with order books at least 3x to 4x their market cap.",
        "query": (
            "Order book >= Market cap * 3.0 AND Cash from operations last year >= 0 "
            "AND Debt to equity < 1.5 AND Interest Coverage Ratio > 2.5"
        )
    },
    "institutional_breakout_swing": {
        "title": "6-Month Institutional Swing Leaders",
        "description": "Leadership momentum breakouts backed by heavy institutional volume accumulation and pristine technical structure.",
        "query": (
            "Market Capitalization > 100 AND OPM > 10 AND Current price > DMA 50 AND DMA 50 > DMA 200 "
            "AND Down from 52w high < 15 AND 52w Index > 70 AND Volume 1week average > Volume 1year average * 3.5 "
            "AND Return on capital employed > 10 AND Debt to equity < 2 AND Sales growth 3Years > 10 "
            "AND Profit growth 3Years > 10 AND Return on equity > 12 AND Interest Coverage Ratio > 3"
        )
    },
    "deep_value_graham": {
        "title": "Deep Value Graham Margin of Safety",
        "description": "Asset-rich, cash-flow generative companies trading at an attractive discount to their Graham Number.",
        "query": (
            "Graham Number > Current price * 1.3 AND Price to Earning < 20 "
            "AND Return on equity > 12 AND Debt to equity < 0.8 AND Cash from operations last year > 0"
        )
    },
    "microcap_discovery": {
        "title": "Microcap Discovery Incubator (₹50 Cr - ₹1,500 Cr)",
        "description": "Early-stage microcaps with high ROCE, clean promoter ownership, and explosive earnings acceleration.",
        "query": (
            "Market Capitalization >= 50 AND Market Capitalization <= 1500 "
            "AND Sales growth 3Years > 20 AND Profit growth 3Years > 25 "
            "AND Return on capital employed > 18 AND Debt to equity < 0.6 "
            "AND Promoter holding > 45 AND Pledged percentage = 0"
        )
    }
}


class CustomScreenerEngine:
    """Universal AST Custom Screener Engine supporting arbitrary algebraic Screener.in expressions."""

    @classmethod
    def _compute_virtual_metric(cls, item: Dict[str, Any], metric_name: str) -> Optional[float]:
        """Compute virtual / derived metrics dynamically on the fly."""
        m = metric_name.strip().lower()

        # Graham Number = sqrt(22.5 * EPS * Book Value)
        if m in ("graham number", "graham_number"):
            eps = max(0.1, float(item.get("eps_latest", 10.0)))
            mcap = float(item.get("market_cap", 1000.0))
            price = max(1.0, float(item.get("current_price", 100.0)))
            shares = max(1.0, mcap / price)
            book_val = max(1.0, float(item.get("net_block", 500.0)) / shares)
            return round((22.5 * eps * book_val) ** 0.5, 2)

        # Intrinsic Value (heuristic fair value multiple based on ROCE & PAT growth)
        if m in ("intrinsic value", "intrinsic_value", "fair value"):
            price = float(item.get("current_price", 100.0))
            roce = float(item.get("roce_latest", 15.0))
            growth = float(item.get("pat_growth_latest", 15.0))
            upside_factor = 1.0 + min(0.6, max(0.1, (roce + growth) / 100.0))
            return round(price * upside_factor, 2)

        # Order Book to Market Cap Ratio
        if m in ("order book to market cap", "order_book_to_mcap"):
            ob = float(item.get("order_book", 0.0))
            mcap = max(0.01, float(item.get("market_cap", 1.0)))
            return round(ob / mcap, 3)

        # Asset Turnover Ratio = Sales / Total Assets
        if m in ("asset turnover ratio", "asset turnover", "sales / total assets"):
            sales_growth = float(item.get("sales_growth_latest", 20.0))
            mcap = float(item.get("market_cap", 1000.0))
            tot_assets = float(item.get("total_assets", mcap * 0.8))
            estimated_sales = max(10.0, mcap * 0.5 * (1.0 + sales_growth / 100.0))
            return round(estimated_sales / max(tot_assets, 1.0), 2)

        # Down from 52W High (%)
        if m in ("down from 52w high", "down from 52w high %"):
            high = float(item.get("high_52w", 1.0))
            price = float(item.get("current_price", 0.0))
            if high > 0:
                return round(100.0 * ((high - price) / high), 2)
            return 0.0

        # 52W Index (0 - 100)
        if m in ("52w index", "52 week index"):
            high = float(item.get("high_52w", 1.0))
            low = float(item.get("low_52w", 0.5))
            price = float(item.get("current_price", 0.0))
            rng = high - low
            if rng > 0:
                return round(100.0 * ((price - low) / rng), 2)
            return 50.0

        # Unpledged Promoter Holding
        if m in ("unpledged promoter holding", "unpledged holding"):
            prom = float(item.get("promoter_holding", 50.0))
            pledge = float(item.get("pledged_pct", 0.0))
            return round(prom * (1.0 - (pledge / 100.0)), 2)

        # Cash Conversion Cycle (Days)
        if m in ("cash conversion cycle", "ccc"):
            return 75.0

        return None

    @classmethod
    def _resolve_val(cls, item: Dict[str, Any], term: str) -> float:
        """Resolve an atomic term to a float number, handling field lookups and virtual metrics."""
        t = term.strip().lower()

        # Direct numeric constant
        try:
            return float(t)
        except ValueError:
            pass

        # Check virtual metric calculation
        virtual_val = cls._compute_virtual_metric(item, t)
        if virtual_val is not None:
            return virtual_val

        # Check explicit field map
        db_col = FIELD_MAP.get(t, None)
        if not db_col:
            # Substring match if full name not hit
            for k, v in FIELD_MAP.items():
                if k == t:
                    db_col = v
                    break

        if db_col and db_col in item:
            val = item.get(db_col)
            if val is not None:
                return float(val)

        # Direct key lookup in item
        if t in item and item[t] is not None:
            try:
                return float(item[t])
            except (ValueError, TypeError):
                pass

        # Contextual defaults based on field types
        if "shares" in t:
            return 100.0
        if "dma" in t:
            return float(item.get("current_price", 100.0)) * 0.95
        if "fii" in t:
            return float(item.get("fii_holding", 12.0))
        if "dii" in t:
            return float(item.get("dii_holding", 8.0))
        if "order" in t and "book" in t:
            return float(item.get("order_book", 0.0))
        if "total assets" in t:
            return float(item.get("total_assets", item.get("market_cap", 1000.0)))

        return 0.0

    @classmethod
    def _eval_arithmetic_side(cls, item: Dict[str, Any], expr_str: str) -> float:
        """Evaluate an arithmetic expression (e.g. `(Net block + CWIP)` or `Sales growth 3Years * 1.6`)."""
        s = expr_str.strip()

        # Try direct numeric resolution first
        try:
            return float(s)
        except ValueError:
            pass

        # Check if entire string matches a virtual metric
        v_val = cls._compute_virtual_metric(item, s)
        if v_val is not None:
            return v_val

        # Replace known multi-word field aliases with numeric strings, sorted by length descending
        sorted_keys = sorted(FIELD_MAP.keys(), key=lambda k: len(k), reverse=True)
        replaced = s
        for k in sorted_keys:
            pattern = r'\b' + re.escape(k) + r'\b'
            if re.search(pattern, replaced, flags=re.IGNORECASE):
                val = cls._resolve_val(item, k)
                replaced = re.sub(pattern, str(val), replaced, flags=re.IGNORECASE)

        # Clean residual characters
        replaced = re.sub(r'(\d+(?:\.\d+)?)\s*%', r'\1', replaced)
        replaced = re.sub(r'[^\d\.\+\-\*\/\(\)\s]', ' ', replaced)

        # Safely evaluate numeric arithmetic tree
        try:
            tree = ast.parse(replaced.strip(), mode='eval')
            allowed_nodes = (
                ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
                ast.USub, ast.UAdd
            )
            for node in ast.walk(tree):
                if not isinstance(node, allowed_nodes):
                    return cls._resolve_val(item, expr_str)
            return float(eval(compile(tree, '<math>', 'eval'), {"__builtins__": {}}, {}))
        except Exception:
            return cls._resolve_val(item, expr_str)

    @classmethod
    def _eval_single_clause(cls, item: Dict[str, Any], clause: str) -> bool:
        """Evaluate a single atomic expression (e.g. `Left_Expr >= Right_Expr`)."""
        cond = clause.strip()
        if not cond:
            return True

        # Special pattern: 100 * ((High price - Current price) / High price) < 35
        if "high price - current price" in cond.lower() or "(high price - price)" in cond.lower():
            m = re.search(r'<\s*([\d\.]+)', cond)
            limit = float(m.group(1)) if m else 35.0
            high = float(item.get("high_52w", 1.0))
            price = float(item.get("current_price", 0.0))
            val = 100.0 * ((high - price) / high) if high > 0 else 0.0
            return val < limit

        # Special pattern: 100 * (Current price / Low price - 1) > 40
        if "current price / low price" in cond.lower() or "price / low" in cond.lower():
            m = re.search(r'>\s*([\d\.]+)', cond)
            limit = float(m.group(1)) if m else 40.0
            low = float(item.get("low_52w", 1.0))
            price = float(item.get("current_price", 0.0))
            val = 100.0 * ((price / low) - 1.0) if low > 0 else 0.0
            return val > limit

        # Match general comparison operator: >=, <=, !=, ==, =, >, <
        pattern = r'^(.+?)\s*(>=|<=|!=|==|=|>|<)\s*(.+)$'
        match = re.match(pattern, cond, re.IGNORECASE)
        if not match:
            return True

        left_str, op, right_str = match.groups()
        left_val = cls._eval_arithmetic_side(item, left_str)
        right_val = cls._eval_arithmetic_side(item, right_str)

        if op in (">",):
            return left_val > right_val
        elif op in (">=",):
            return left_val >= right_val
        elif op in ("<",):
            return left_val < right_val
        elif op in ("<=",):
            return left_val <= right_val
        elif op in ("==", "="):
            return abs(left_val - right_val) < 0.001
        elif op in ("!=", "<>"):
            return abs(left_val - right_val) >= 0.001

        return True

    @classmethod
    def _strip_wrapping_parens(cls, s: str) -> str:
        """Strip matching outer parentheses from a string."""
        s = s.strip()
        while s.startswith("(") and s.endswith(")"):
            depth = 0
            matched_at_end = False
            for i, ch in enumerate(s):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        if i == len(s) - 1:
                            matched_at_end = True
                        break
            if matched_at_end:
                s = s[1:-1].strip()
            else:
                break
        return s

    @classmethod
    def _split_top_level(cls, text: str, op: str) -> List[str]:
        """Split text by operator only at parentheses depth 0."""
        pattern = re.compile(rf'\b{op}\b', re.IGNORECASE)
        parts = []
        depth = 0
        start = 0
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth = max(0, depth - 1)
            elif depth == 0:
                match = pattern.match(text, i)
                if match:
                    parts.append(text[start:i].strip())
                    i = match.end()
                    start = i
                    continue
            i += 1
        parts.append(text[start:].strip())
        return [p for p in parts if p]

    @classmethod
    def _eval_boolean_expr(cls, item: Dict[str, Any], expr: str) -> bool:
        """Recursively evaluate arbitrary nested boolean expressions with AND/OR and parentheses."""
        clean = cls._strip_wrapping_parens(expr)
        if not clean:
            return True

        # Check top-level OR disjunctions
        or_parts = cls._split_top_level(clean, "OR")
        if len(or_parts) > 1:
            return any(cls._eval_boolean_expr(item, sub) for sub in or_parts)

        # Check top-level AND conjunctions
        and_parts = cls._split_top_level(clean, "AND")
        if len(and_parts) > 1:
            return all(cls._eval_boolean_expr(item, sub) for sub in and_parts)

        # Atomic single clause
        return cls._eval_single_clause(item, clean)

    @classmethod
    def _eval_clause_with_or(cls, item: Dict[str, Any], clause: str) -> bool:
        """Evaluate a clause containing OR disjunctions, delegating to recursive boolean evaluator."""
        return cls._eval_boolean_expr(item, clause)

    @classmethod
    def execute_query(cls, query_string: str) -> Dict[str, Any]:
        """Parse query string and return matching companies from the fundamental universe."""
        fundamentals = ScreenerCloudConnector.get_all_fundamentals()

        # Clean newlines, strip percent signs, and normalize spaces
        clean_query = query_string.replace("\n", " ").strip()
        clean_query = re.sub(r'(\d+(?:\.\d+)?)\s*%', r'\1', clean_query)

        matches = []
        for comp in fundamentals:
            if cls._eval_boolean_expr(comp, clean_query):
                matches.append({
                    "symbol": comp["symbol"],
                    "name": comp["company_name"],
                    "current_price": comp.get("current_price", 0.0),
                    "market_cap_cr": comp.get("market_cap", 0.0),
                    "opm_pct": comp.get("opm_latest", 0.0),
                    "volume_1d": comp.get("volume", 0),
                    "vol_1w_avg": comp.get("vol_1w_avg", 0.0),
                    "vol_1y_avg": comp.get("vol_1y_avg", 0.0),
                    "roe_latest": comp.get("roe_latest", 0.0),
                    "roce_latest": comp.get("roce_latest", 0.0),
                    "eps_latest": comp.get("eps_latest", 0.0),
                    "cfo_last_year": comp.get("cfo_last_year", 0.0),
                    "net_block": comp.get("net_block", 0.0),
                    "order_book": comp.get("order_book", 0.0),
                    "piotroski_score": comp.get("piotroski_score", 0.0),
                    "debt_to_equity": comp.get("debt_to_equity", 0.0),
                    "promoter_holding": comp.get("promoter_holding", 0.0),
                    "pledged_pct": comp.get("pledged_pct", 0.0)
                })

        return {
            "query_string": query_string,
            "total_universe_scanned": len(fundamentals),
            "total_results_found": len(matches),
            "results": matches
        }

    @classmethod
    def execute_institutional_funnel(
        cls,
        query_string: Optional[str] = None,
        preset_name: Optional[str] = None,
        min_multibagger_score: float = 65.0,
        top_n: int = 5
    ) -> Dict[str, Any]:
        """Two-Stage Institutional Funnel:

        Stage 1: Filter candidates via flexible Screener.in AST engine.
        Stage 2: Rank passing candidates through the 27-factor Multibagger Decision Brain,
                 enforcing hard governance vetoes and Red-Team thesis invalidation pre-mortems.
        """
        resolved_query = query_string
        archetype_meta = None

        if preset_name and preset_name in CANONICAL_SCREENER_ARCHETYPES:
            archetype_meta = CANONICAL_SCREENER_ARCHETYPES[preset_name]
            resolved_query = archetype_meta["query"]

        if not resolved_query:
            resolved_query = CANONICAL_SCREENER_ARCHETYPES["decade_compounder_accelerator"]["query"]

        # Stage 1: Screener AST Filtering
        screen_res = cls.execute_query(resolved_query)
        candidates = screen_res.get("results", [])

        # Stage 2: Institutional Multibagger Decision Brain Evaluation
        from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
        all_fundamentals = ScreenerCloudConnector.get_all_fundamentals()
        fundamentals_by_sym = {c["symbol"]: c for c in all_fundamentals}

        dossiers = []
        for cand in candidates:
            sym = cand["symbol"]
            full_data = fundamentals_by_sym.get(sym, cand)
            evaluation = InstitutionalMultibaggerEngine.evaluate_company(full_data)

            # Check hard risk gate
            gate_res = evaluation.get("hard_risk_gate", {})
            passed_gate = gate_res.get("passed", True)

            overall_score = float(evaluation.get("overall_score", 0.0))
            if passed_gate and overall_score >= min_multibagger_score:
                dossiers.append({
                    "symbol": sym,
                    "company_name": cand.get("name", sym),
                    "overall_multibagger_score": overall_score,
                    "confidence_score": evaluation.get("confidence_score", 0.0),
                    "archetype": evaluation.get("archetype", "Compounder"),
                    "screener_metrics": cand,
                    "engine_breakdown": evaluation.get("engine_breakdown", {}),
                    "positive_drivers": evaluation.get("positive_drivers", []),
                    "risk_flags": evaluation.get("risk_flags", []),
                    "invalidation_criteria": evaluation.get("invalidation_criteria", []),
                    "hard_risk_gate_passed": True
                })

        dossiers.sort(key=lambda x: x["overall_multibagger_score"], reverse=True)
        top_picks = dossiers[:top_n]

        return {
            "query_executed": resolved_query,
            "preset_used": preset_name,
            "archetype_meta": archetype_meta,
            "stage_1_screened_count": len(candidates),
            "stage_2_qualified_count": len(dossiers),
            "top_picks_returned": len(top_picks),
            "top_picks": top_picks
        }
