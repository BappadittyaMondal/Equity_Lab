"""Financial Statement Parser for Equity Lab Data Pipelines.

Parses quarterly BSE/NSE financial filings, computes YoY and QoQ growth metrics,
calculates margin profiles, and validates data completeness.
"""

from typing import Any, Dict, List, Optional


class FinancialStatementParser:
    """Parses raw quarterly statements and calculates fundamental financial ratios."""

    def parse_quarterly_statement(self, raw_statement: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw quarterly financial inputs into normalized schema."""
        symbol = str(raw_statement.get("symbol", "")).strip().upper()
        period_ended = str(raw_statement.get("period_ended", ""))

        revenue = raw_statement.get("revenue")
        operating_profit = raw_statement.get("operating_profit")
        net_profit = raw_statement.get("net_profit")
        eps = raw_statement.get("eps")

        # Calculate Margins if revenue and profit numbers are present
        op_margin = None
        net_margin = None
        if revenue and revenue > 0:
            if operating_profit is not None:
                op_margin = round((operating_profit / revenue) * 100.0, 2)
            if net_profit is not None:
                net_margin = round((net_profit / revenue) * 100.0, 2)

        data_insufficient = not bool(symbol and period_ended and revenue and net_profit)

        return {
            "symbol": symbol,
            "period_ended": period_ended,
            "revenue": revenue,
            "operating_profit": operating_profit,
            "net_profit": net_profit,
            "eps": eps,
            "operating_margin_pct": op_margin,
            "net_margin_pct": net_margin,
            "roce_pct": raw_statement.get("roce_pct"),
            "roe_pct": raw_statement.get("roe_pct"),
            "data_insufficient": data_insufficient,
            "as_of_date": raw_statement.get("as_of_date"),
            "source": raw_statement.get("source", "statement_parser"),
        }

    def compute_growth_rates(self, quarters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute YoY and QoQ growth rates across sorted quarterly statements.

        Assumes quarters are ordered from newest to oldest.
        """
        if len(quarters) < 2:
            return {
                "yoy_revenue_growth": None,
                "qoq_revenue_growth": None,
                "yoy_pat_growth": None,
                "qoq_pat_growth": None,
                "data_insufficient": True,
            }

        latest = quarters[0]
        prev_qtr = quarters[1]
        year_ago_qtr = quarters[4] if len(quarters) >= 5 else None

        # QoQ Growth Calculations
        qoq_rev_growth = None
        if latest.get("revenue") and prev_qtr.get("revenue") and prev_qtr["revenue"] > 0:
            qoq_rev_growth = round(((latest["revenue"] - prev_qtr["revenue"]) / prev_qtr["revenue"]) * 100.0, 2)

        qoq_pat_growth = None
        if latest.get("net_profit") and prev_qtr.get("net_profit") and prev_qtr["net_profit"] > 0:
            qoq_pat_growth = round(((latest["net_profit"] - prev_qtr["net_profit"]) / prev_qtr["net_profit"]) * 100.0, 2)

        # YoY Growth Calculations (Comparing latest quarter against quarter 4 periods ago)
        yoy_rev_growth = None
        yoy_pat_growth = None
        if year_ago_qtr:
            if latest.get("revenue") and year_ago_qtr.get("revenue") and year_ago_qtr["revenue"] > 0:
                yoy_rev_growth = round(((latest["revenue"] - year_ago_qtr["revenue"]) / year_ago_qtr["revenue"]) * 100.0, 2)
            if latest.get("net_profit") and year_ago_qtr.get("net_profit") and year_ago_qtr["net_profit"] > 0:
                yoy_pat_growth = round(((latest["net_profit"] - year_ago_qtr["net_profit"]) / year_ago_qtr["net_profit"]) * 100.0, 2)

        return {
            "symbol": latest.get("symbol"),
            "latest_period": latest.get("period_ended"),
            "yoy_revenue_growth": yoy_rev_growth,
            "qoq_revenue_growth": qoq_rev_growth,
            "yoy_pat_growth": yoy_pat_growth,
            "qoq_pat_growth": qoq_pat_growth,
            "data_insufficient": False,
        }
