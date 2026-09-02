"""Financial Data Ingester — Pulls quarterly fundamentals via yfinance.

Extracts real financial data (Revenue, Net Income, EPS, Total Debt,
Total Equity, Cash Flow) from yfinance's financial statements and
stores each metric as a sourced, timestamped FinancialObservation
in the ResearchDataStore.

This replaces the empty-database problem: after running this ingester,
strategy engines E1/E2/E3/E4 will have real quarterly data to analyze.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.research_data import ResearchDataStore
from app.services.market_data import normalize_symbol

logger = logging.getLogger(__name__)

# Source credibility tier
_SOURCE_NAME = "yfinance"
_SOURCE_CONFIDENCE = 0.75  # yfinance is aggregated, not primary filing


class FinancialIngester:
    """Ingests quarterly financial statements from yfinance into ResearchDataStore."""

    def __init__(self, store: Optional[ResearchDataStore] = None):
        self.store = store or ResearchDataStore()

    def ingest_symbol(self, symbol: str) -> Dict[str, Any]:
        """Ingest all available quarterly financial data for a symbol.

        Returns a summary dict with counts of observations ingested.
        """
        import yfinance as yf

        norm = normalize_symbol(symbol)
        ticker_str = norm if norm.endswith(".NS") else norm + ".NS"
        ticker_str_clean = norm.replace(".NS", "")

        result = {
            "symbol": ticker_str_clean,
            "financials_ingested": 0,
            "ownership_ingested": 0,
            "errors": [],
        }

        try:
            ticker = yf.Ticker(ticker_str)
        except Exception as e:
            result["errors"].append(f"Failed to create yfinance ticker: {e}")
            return result

        # Ensure company record exists
        try:
            info = ticker.info or {}
            self.store.upsert_company({
                "symbol": ticker_str,
                "company_name": info.get("longName", ticker_str_clean),
                "legal_name": info.get("longName", ticker_str_clean),
                "isin": info.get("isin", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
            })
        except Exception as e:
            # Company may already exist, which is fine
            logger.debug("Company upsert note for %s: %s", ticker_str_clean, e)

        # --- Ingest quarterly income statement ---
        result["financials_ingested"] += self._ingest_income_statement(ticker, ticker_str)

        # --- Ingest quarterly balance sheet ---
        result["financials_ingested"] += self._ingest_balance_sheet(ticker, ticker_str)

        # --- Ingest quarterly cash flow ---
        result["financials_ingested"] += self._ingest_cash_flow(ticker, ticker_str)

        # --- Ingest institutional holders as ownership proxy ---
        result["ownership_ingested"] += self._ingest_ownership(ticker, ticker_str)

        logger.info(
            "Ingested %d financial observations + %d ownership records for %s",
            result["financials_ingested"],
            result["ownership_ingested"],
            ticker_str_clean,
        )
        return result

    def _ingest_income_statement(self, ticker: Any, symbol: str) -> int:
        """Extract quarterly income statement metrics."""
        count = 0
        try:
            quarterly_income = ticker.quarterly_income_stmt
            if quarterly_income is None or quarterly_income.empty:
                return 0

            for col_date in quarterly_income.columns:
                period_end = col_date.strftime("%Y-%m-%d") if hasattr(col_date, "strftime") else str(col_date)
                published_at = self._estimate_publication_date(period_end)

                metrics_map = {
                    "revenue": ["Total Revenue", "Operating Revenue"],
                    "net_income": ["Net Income", "Net Income Common Stockholders"],
                    "operating_income": ["Operating Income", "EBIT"],
                    "gross_profit": ["Gross Profit"],
                    "ebitda": ["EBITDA", "Normalized EBITDA"],
                    "basic_eps": ["Basic EPS"],
                    "diluted_eps": ["Diluted EPS"],
                    "total_expenses": ["Total Expenses"],
                    "interest_expense": ["Interest Expense"],
                    "tax_provision": ["Tax Provision"],
                }

                for metric_name, possible_keys in metrics_map.items():
                    value = self._extract_value(quarterly_income, col_date, possible_keys)
                    if value is not None:
                        count += self._store_observation(
                            symbol, metric_name, value, "INR", period_end,
                            "quarterly", published_at
                        )
        except Exception as e:
            logger.warning("Income statement ingestion error for %s: %s", symbol, e)
        return count

    def _ingest_balance_sheet(self, ticker: Any, symbol: str) -> int:
        """Extract quarterly balance sheet metrics."""
        count = 0
        try:
            quarterly_bs = ticker.quarterly_balance_sheet
            if quarterly_bs is None or quarterly_bs.empty:
                return 0

            for col_date in quarterly_bs.columns:
                period_end = col_date.strftime("%Y-%m-%d") if hasattr(col_date, "strftime") else str(col_date)
                published_at = self._estimate_publication_date(period_end)

                metrics_map = {
                    "total_assets": ["Total Assets"],
                    "total_debt": ["Total Debt", "Long Term Debt"],
                    "total_equity": ["Total Equity Gross Minority Interest", "Stockholders Equity"],
                    "cash_and_equivalents": ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"],
                    "total_liabilities": ["Total Liabilities Net Minority Interest"],
                    "net_debt": ["Net Debt"],
                    "working_capital": ["Working Capital"],
                    "retained_earnings": ["Retained Earnings"],
                }

                for metric_name, possible_keys in metrics_map.items():
                    value = self._extract_value(quarterly_bs, col_date, possible_keys)
                    if value is not None:
                        count += self._store_observation(
                            symbol, metric_name, value, "INR", period_end,
                            "quarterly", published_at
                        )
        except Exception as e:
            logger.warning("Balance sheet ingestion error for %s: %s", symbol, e)
        return count

    def _ingest_cash_flow(self, ticker: Any, symbol: str) -> int:
        """Extract quarterly cash flow metrics."""
        count = 0
        try:
            quarterly_cf = ticker.quarterly_cashflow
            if quarterly_cf is None or quarterly_cf.empty:
                return 0

            for col_date in quarterly_cf.columns:
                period_end = col_date.strftime("%Y-%m-%d") if hasattr(col_date, "strftime") else str(col_date)
                published_at = self._estimate_publication_date(period_end)

                metrics_map = {
                    "operating_cash_flow": ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"],
                    "free_cash_flow": ["Free Cash Flow"],
                    "capital_expenditure": ["Capital Expenditure"],
                    "investing_cash_flow": ["Investing Cash Flow", "Cash Flow From Continuing Investing Activities"],
                    "financing_cash_flow": ["Financing Cash Flow", "Cash Flow From Continuing Financing Activities"],
                }

                for metric_name, possible_keys in metrics_map.items():
                    value = self._extract_value(quarterly_cf, col_date, possible_keys)
                    if value is not None:
                        count += self._store_observation(
                            symbol, metric_name, value, "INR", period_end,
                            "quarterly", published_at
                        )
        except Exception as e:
            logger.warning("Cash flow ingestion error for %s: %s", symbol, e)
        return count

    def _ingest_ownership(self, ticker: Any, symbol: str) -> int:
        """Ingest real shareholding pattern (promoter, institutional, public) from ticker info/holders."""
        count = 0
        try:
            info = getattr(ticker, "info", {}) or {}
            promoter_pct = None
            inst_pct = None
            confidence = 0.55

            # 1. Try extracting primary insider & institutional holdings from info
            insiders_raw = info.get("heldPercentInsiders")
            inst_raw = info.get("heldPercentInstitutions")

            if insiders_raw is not None:
                promoter_pct = round(float(insiders_raw) * 100.0, 2)
            if inst_raw is not None:
                inst_pct = round(float(inst_raw) * 100.0, 2)

            # 2. Try parsing major_holders DataFrame if info fields missing
            if promoter_pct is None or inst_pct is None:
                try:
                    mh = ticker.major_holders
                    if mh is not None and not mh.empty:
                        for idx, row in mh.iterrows():
                            val_str = str(row.iloc[0]).replace("%", "").strip()
                            label_str = str(row.iloc[1]).lower()
                            try:
                                val_num = float(val_str)
                                if "insider" in label_str and promoter_pct is None:
                                    promoter_pct = round(val_num, 2)
                                elif "institution" in label_str and inst_pct is None:
                                    inst_pct = round(val_num, 2)
                            except ValueError:
                                pass
                except Exception:
                    pass

            # 3. Fallback aggregate calculation if institutional holders present
            if inst_pct is None:
                holders = getattr(ticker, "institutional_holders", None)
                total_shares = info.get("sharesOutstanding", None)
                if holders is not None and not holders.empty and total_shares and total_shares > 0:
                    inst_shares = holders["Shares"].sum() if "Shares" in holders.columns else 0
                    inst_pct = round(min((inst_shares / total_shares) * 100.0, 100.0), 2)

            if promoter_pct is not None or inst_pct is not None:
                promoter_final = promoter_pct if promoter_pct is not None else 0.0
                inst_final = inst_pct if inst_pct is not None else 0.0
                public_final = round(max(0.0, 100.0 - promoter_final - inst_final), 2)
                # Truth Gate: DO NOT fabricate FII/DII subcomponents with artificial 55/45 multipliers.
                # If sub-filings are not explicitly available, store None instead of inventing numbers.
                fii_final = None
                dii_final = None
                confidence = 0.88 if (promoter_pct is not None and inst_pct is not None) else 0.70

                now_iso = datetime.now(timezone.utc).isoformat()
                self.store.add_ownership_snapshot({
                    "symbol": symbol,
                    "period_end": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "promoter_pct": promoter_final,
                    "fii_pct": fii_final,
                    "dii_pct": dii_final,
                    "mutual_fund_pct": None,
                    "insurance_pct": None,
                    "public_pct": public_final,
                    "aif_pct": None,
                    "promoter_pledge_pct": None,  # Not observed in generic filings, do not assume 0.0!
                    "published_at": now_iso,
                    "source_name": _SOURCE_NAME,
                    "source_url": f"https://finance.yahoo.com/quote/{symbol}/holders/",
                    "confidence": confidence,
                })
                count = 1
        except Exception as e:
            logger.debug("Ownership ingestion skipped for %s: %s", symbol, e)
        return count

    # --- Private helpers ---

    def _extract_value(self, df: Any, col: Any, keys: List[str]) -> Optional[float]:
        """Try multiple row labels to extract a value from a financial statement DataFrame."""
        for key in keys:
            try:
                val = df.loc[key, col]
                if val is not None and str(val) != "nan":
                    return float(val)
            except (KeyError, TypeError, ValueError):
                continue
        return None

    def _estimate_publication_date(self, period_end: str) -> str:
        """Estimate when quarterly results were published (typically 45 days after period end)."""
        try:
            pe = datetime.strptime(period_end[:10], "%Y-%m-%d")
            from datetime import timedelta
            pub = pe + timedelta(days=45)
            return pub.replace(tzinfo=timezone.utc).isoformat()
        except Exception:
            return datetime.now(timezone.utc).isoformat()

    def _store_observation(
        self, symbol: str, metric: str, value: float, unit: str,
        period_end: str, period_type: str, published_at: str
    ) -> int:
        """Store a single financial observation. Returns 1 on success, 0 on failure."""
        try:
            self.store.add_financial_observation({
                "symbol": symbol,
                "metric": metric,
                "value": value,
                "unit": unit,
                "period_end": period_end,
                "period_type": period_type,
                "published_at": published_at,
                "source_name": _SOURCE_NAME,
                "source_url": f"https://finance.yahoo.com/quote/{symbol.replace('.NS', '')}/financials/",
                "confidence": _SOURCE_CONFIDENCE,
            })
            return 1
        except Exception as e:
            logger.debug("Store observation error for %s/%s: %s", symbol, metric, e)
            return 0
