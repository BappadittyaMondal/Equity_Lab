import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import yfinance as yf

from app.services.db import get_connection
try:
    from app.services.market_data import normalize_symbol
except ImportError:
    def normalize_symbol(symbol: str) -> str:
        """Fallback normalize_symbol if import fails."""
        symbol = symbol.strip().upper()
        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            symbol += ".NS"
        return symbol

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Phase 149: Corporate Action Normalizer
# Purpose: Adjust raw historical EPS and share-count for stock splits, bonus
#          issues, rights issues, and face-value changes before computing any
#          multi-year CAGR or price-return arithmetic.
# Conflict: ZERO — operates purely upstream as a data quality layer.
#           Does NOT touch any engine algorithm, weight, threshold, or formula.
# ─────────────────────────────────────────────────────────────────────────────

def normalize_corporate_actions(
    ticker: "yf.Ticker",
    current_shares: float,
    current_eps: float,
    lookback_years: int = 5,
) -> Dict[str, Any]:
    """
    Computes a cumulative corporate-action adjustment factor from yfinance
    splits data covering the past `lookback_years` years.

    Returns a dict with:
      - ``cumulative_split_factor``: product of all split ratios in window (e.g. 5.0 for a 5:1 bonus)
      - ``corporate_action_normalized_shares``: current_shares / cumulative_split_factor
        (i.e., how many shares existed BEFORE the actions — for point-in-time comparison)
      - ``corporate_action_normalized_eps``: current_eps * cumulative_split_factor
        (i.e., what EPS *would have been reported* on the old share count)
      - ``actions_detected``: number of split/bonus events found in window
      - ``data_integrity_flag``: "CLEAN" | "ADJUSTED" | "UNVERIFIABLE"

    Mathematical basis:
      If a company did a 5:1 bonus, shares outstanding increased 5x.
      Historic EPS (on old share count) = current EPS × 5.
      Historic share count (old base)   = current shares ÷ 5.
      A raw historical chart comparing old EPS to new EPS would show a
      spurious 80% earnings collapse that never happened. This corrects it.
    """
    result: Dict[str, Any] = {
        "cumulative_split_factor": 1.0,
        "corporate_action_normalized_shares": current_shares,
        "corporate_action_normalized_eps": current_eps,
        "actions_detected": 0,
        "data_integrity_flag": "CLEAN",
    }

    try:
        splits = ticker.splits
        if splits is None or splits.empty:
            return result

        cutoff = datetime.now(timezone.utc).timestamp() - lookback_years * 365.25 * 86400
        recent_splits = splits[splits.index.astype("int64") // 10**9 >= cutoff]

        if recent_splits.empty:
            return result

        cumulative_factor = 1.0
        for ratio in recent_splits:
            if ratio and not math.isnan(ratio) and ratio > 0:
                cumulative_factor *= float(ratio)

        actions_count = int((recent_splits != 1.0).sum())

        result["cumulative_split_factor"] = round(cumulative_factor, 6)
        result["corporate_action_normalized_shares"] = (
            round(current_shares / cumulative_factor, 0) if cumulative_factor else current_shares
        )
        result["corporate_action_normalized_eps"] = (
            round(current_eps * cumulative_factor, 4) if cumulative_factor else current_eps
        )
        result["actions_detected"] = actions_count
        result["data_integrity_flag"] = "ADJUSTED" if actions_count > 0 else "CLEAN"

    except Exception as exc:
        logger.warning(f"Corporate action normalization failed: {exc}")
        result["data_integrity_flag"] = "UNVERIFIABLE"

    return result

class FundamentalFetcher:
    """Live fundamental data fetcher using yfinance."""

    @classmethod
    def _safe_get(cls, series, default=0.0):
        if series is None or len(series) == 0:
            return default
        # Get the first available (most recent) value that is not NaN
        try:
            import math
            for val in series:
                if val is not None and not (isinstance(val, float) and math.isnan(val)):
                    return float(val)
        except Exception:
            pass
        return default

    @classmethod
    def _safe_get_historical(cls, series, periods_back=1, default=0.0):
        if series is None or len(series) <= periods_back:
            return default
        try:
            import math
            val = series.iloc[periods_back] if hasattr(series, 'iloc') else series[periods_back]
            if val is not None and not (isinstance(val, float) and math.isnan(val)):
                return float(val)
        except Exception:
            pass
        return default

    @classmethod
    def fetch_batch(cls, symbols: List[str]) -> List[Optional[Dict[str, Any]]]:
        results = []
        for sym in symbols:
            results.append(cls.fetch_and_store(sym))
        return results

    @classmethod
    def fetch_and_store(cls, symbol: str) -> Optional[Dict[str, Any]]:
        normalized_sym = normalize_symbol(symbol)
        logger.info(f"Fetching fundamentals for {normalized_sym}")
        
        try:
            ticker = yf.Ticker(normalized_sym)
            info = ticker.info
            
            # If info is completely empty or has no currentPrice, it's likely a bad symbol or data missing
            if not info or ('currentPrice' not in info and 'regularMarketPrice' not in info):
                logger.warning(f"No info data for {normalized_sym}")
                return None

            q_fin = ticker.quarterly_financials
            q_bs = ticker.quarterly_balance_sheet
            q_cf = ticker.quarterly_cashflow
            
            def get_fin(key, periods_back=0):
                if q_fin is not None and key in q_fin.index:
                    return cls._safe_get_historical(q_fin.loc[key], periods_back)
                return 0.0

            def get_bs(key, periods_back=0):
                if q_bs is not None and key in q_bs.index:
                    return cls._safe_get_historical(q_bs.loc[key], periods_back)
                return 0.0
                
            def get_cf(key, periods_back=0):
                if q_cf is not None and key in q_cf.index:
                    return cls._safe_get_historical(q_cf.loc[key], periods_back)
                return 0.0

            # --- Derived Metrics Calculation ---
            # Most recent quarter
            ebit = get_fin('EBIT')
            total_assets = get_bs('Total Assets')
            current_liabilities = get_bs('Current Liabilities')
            net_income = get_fin('Net Income')
            stockholders_equity = get_bs('Stockholders Equity')
            total_debt = get_bs('Total Debt')
            interest_expense = get_fin('Interest Expense')
            operating_income = get_fin('Operating Income')
            total_revenue = get_fin('Total Revenue')
            operating_cash_flow = get_cf('Operating Cash Flow')

            # RoCE = EBIT / (Total Assets - Current Liabilities) * 100 (Single-quarter run-rate)
            capital_employed = (total_assets - current_liabilities)
            roce_latest = (ebit / capital_employed * 100) if capital_employed else 0.0

            # RoE = Net Income / Shareholder Equity * 100 (Single-quarter run-rate)
            roe_latest = (net_income / stockholders_equity * 100) if stockholders_equity else 0.0

            # Annualized / TTM RoCE & RoE (§Phase 148 Dual Normalization)
            # Sum up to 4 recent quarters if available, otherwise annualize latest quarter (* 4.0)
            ebit_4q = 0.0
            ni_4q = 0.0
            quarters_found = 0
            for q_idx in range(4):
                val_e = get_fin('EBIT', q_idx)
                val_ni = get_fin('Net Income', q_idx)
                if val_e != 0.0 or val_ni != 0.0:
                    ebit_4q += val_e
                    ni_4q += val_ni
                    quarters_found += 1

            if quarters_found >= 4:
                roce_annualized = (ebit_4q / capital_employed * 100) if capital_employed else 0.0
                roe_annualized = (ni_4q / stockholders_equity * 100) if stockholders_equity else 0.0
            else:
                roce_annualized = (ebit * 4.0 / capital_employed * 100) if capital_employed else 0.0
                roe_annualized = (net_income * 4.0 / stockholders_equity * 100) if stockholders_equity else 0.0

            # D/E = Total Debt / Shareholder Equity
            debt_to_equity = (total_debt / stockholders_equity) if stockholders_equity else 0.0

            # Interest Coverage = EBIT / Interest Expense
            interest_coverage = (ebit / interest_expense) if interest_expense else 0.0

            # OPM = Operating Income / Total Revenue * 100
            opm_latest = (operating_income / total_revenue * 100) if total_revenue else 0.0

            # CFO/PAT (Approximated using single quarter for "latest" fallback or trailing if available)
            cfo_pat = (operating_cash_flow / net_income) if net_income else 0.0

            # 3yr metrics (simplified logic based on periods_back in quarterly data: index 12 is approx 3 years ago if available)
            ebit_3yr = get_fin('EBIT', 12) or get_fin('EBIT', 3) # fallback to 1 yr back if 3yr missing
            ce_3yr = get_bs('Total Assets', 12) - get_bs('Current Liabilities', 12)
            if not ce_3yr:
                ce_3yr = get_bs('Total Assets', 3) - get_bs('Current Liabilities', 3)
            roce_3yr = (ebit_3yr / ce_3yr * 100) if ce_3yr else 0.0

            ni_3yr = get_fin('Net Income', 12) or get_fin('Net Income', 3)
            se_3yr = get_bs('Stockholders Equity', 12) or get_bs('Stockholders Equity', 3)
            roe_3yr = (ni_3yr / se_3yr * 100) if se_3yr else 0.0
            
            oi_3yr = get_fin('Operating Income', 12) or get_fin('Operating Income', 3)
            tr_3yr = get_fin('Total Revenue', 12) or get_fin('Total Revenue', 3)
            opm_5yr = (oi_3yr / tr_3yr * 100) if tr_3yr else 0.0 # Just mapped 5yr to oldest available

            # Net Block (Net PPE)
            net_block = get_bs('Net PPE')
            net_block_preceding_year = get_bs('Net PPE', 4)
            net_block_3yr_back = get_bs('Net PPE', 12)
            
            # Growth metrics (comparing latest 4 quarters vs previous 4 quarters if we had full TTM data. For now, comparing latest quarter vs year-ago quarter)
            ni_1yr_ago = get_fin('Net Income', 4)
            pat_growth_latest = ((net_income - ni_1yr_ago) / abs(ni_1yr_ago) * 100) if ni_1yr_ago else 0.0
            
            tr_1yr_ago = get_fin('Total Revenue', 4)
            sales_growth_latest = ((total_revenue - tr_1yr_ago) / abs(tr_1yr_ago) * 100) if tr_1yr_ago else 0.0

            eps_latest = info.get('trailingEps', 0.0) or 0.0
            shares_outstanding = info.get("sharesOutstanding", 0.0) or 0.0

            # ── Phase 149: Corporate Action Normalization ─────────────────────
            # Adjusts EPS and share-count for splits, bonuses, rights issues.
            # Prevents spurious CAGR distortions from raw unadjusted history.
            # Zero conflict: purely an upstream data-quality layer.
            ca_norm = normalize_corporate_actions(
                ticker=ticker,
                current_shares=shares_outstanding,
                current_eps=eps_latest,
                lookback_years=5,
            )

            # Assemble dict
            now_iso = datetime.now(timezone.utc).isoformat()
            
            data = {
                "symbol": normalized_sym,
                "company_name": info.get("shortName") or info.get("longName") or normalized_sym,
                "market_cap": info.get("marketCap", 0.0),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice", 0.0),
                "volume": info.get("volume", 0),
                "high_52w": info.get("fiftyTwoWeekHigh", 0.0),
                "low_52w": info.get("fiftyTwoWeekLow", 0.0),
                "roe_3yr": roe_3yr,
                "roe_latest": roe_latest,
                "roe_annualized": round(roe_annualized, 2),
                "roce_3yr": roce_3yr,
                "roce_latest": roce_latest,
                "roce_annualized": round(roce_annualized, 2),
                "opm_5yr": opm_5yr,
                "opm_latest": opm_latest,
                "operating_profit": operating_income,
                "op_growth": 0.0, # Placeholder
                "pat_growth_3yr": 0.0,
                "pat_growth_latest": pat_growth_latest,
                "sales_growth_3yr": 0.0,
                "sales_growth_latest": sales_growth_latest,
                "eps_growth_3yr": 0.0,
                "eps_latest": eps_latest,
                # ── Phase 149: Corporate Action Normalized Fields ─────────────
                "cumulative_split_factor": ca_norm["cumulative_split_factor"],
                "corporate_action_normalized_eps": ca_norm["corporate_action_normalized_eps"],
                "corporate_action_normalized_shares": ca_norm["corporate_action_normalized_shares"],
                "ca_actions_detected": ca_norm["actions_detected"],
                "data_integrity_flag": ca_norm["data_integrity_flag"],
                # ─────────────────────────────────────────────────────────────
                "cfo_3yr": get_cf('Operating Cash Flow', 12) or get_cf('Operating Cash Flow', 3),
                "net_block": net_block,
                "net_block_3yr_back": net_block_3yr_back,
                "net_block_preceding_year": net_block_preceding_year,
                "cwip": 0.0, # Usually part of Net PPE or not cleanly exposed in standard yf
                "cwip_preceding_year": 0.0,
                "cfo_last_year": get_cf('Operating Cash Flow', 4),
                "net_profit_last_year": ni_1yr_ago,
                "vol_1w_avg": info.get("averageVolume10days", 0.0),
                "vol_1m_avg": info.get("averageVolume", 0.0),
                "vol_1y_avg": info.get("averageVolume", 0.0),
                "piotroski_score": 0.0, # Not trivially available from yf without much more computation
                "promoter_holding": info.get("heldPercentInsiders", 0.0) * 100 if info.get("heldPercentInsiders") else 0.0,
                "pledged_pct": 0.0,
                "pledge_provenance": "UNVERIFIED_IN_YFINANCE_FEED",
                "debt_to_equity": debt_to_equity,
                "interest_coverage": interest_coverage,
                "peg_ratio": info.get("pegRatio", 0.0),
                "order_book": 0.0,
                "fii_holding": info.get("heldPercentInstitutions", 0.0) * 100 if info.get("heldPercentInstitutions") else 0.0,
                "dii_holding": 0.0,
                "total_assets": total_assets,
                "dma_50": info.get("fiftyDayAverage", 0.0),
                "dma_200": info.get("twoHundredDayAverage", 0.0),
                "shares_count": info.get("sharesOutstanding", 0.0),
                "shares_count_10yr_back": 0.0,
                "updated_at": now_iso
            }

            # Insert into database
            cls._store_in_db(data)
            return data

        except Exception as e:
            logger.error(f"Error fetching fundamental data for {normalized_sym}: {e}", exc_info=True)
            return None

    @classmethod
    def _store_in_db(cls, data: Dict[str, Any]):
        conn = get_connection()
        try:
            conn.execute(
                """INSERT OR REPLACE INTO company_fundamentals 
                   (symbol, company_name, market_cap, current_price, volume, high_52w, low_52w, 
                    roe_3yr, roe_latest, roce_3yr, roce_latest, opm_5yr, opm_latest, 
                    operating_profit, op_growth, pat_growth_3yr, pat_growth_latest, 
                    sales_growth_3yr, sales_growth_latest, eps_growth_3yr, eps_latest, 
                    cfo_3yr, net_block, net_block_3yr_back, net_block_preceding_year, 
                    cwip, cwip_preceding_year, cfo_last_year, net_profit_last_year, 
                    vol_1w_avg, vol_1m_avg, vol_1y_avg, piotroski_score, promoter_holding, 
                    pledged_pct, debt_to_equity, interest_coverage, peg_ratio, order_book, 
                    fii_holding, dii_holding, total_assets, dma_50, dma_200, shares_count, 
                    shares_count_10yr_back, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data["symbol"], data["company_name"], data["market_cap"], data["current_price"],
                    data["volume"], data["high_52w"], data["low_52w"], data["roe_3yr"],
                    data["roe_latest"], data["roce_3yr"], data["roce_latest"], data["opm_5yr"],
                    data["opm_latest"], data["operating_profit"], data["op_growth"],
                    data["pat_growth_3yr"], data["pat_growth_latest"], data["sales_growth_3yr"],
                    data["sales_growth_latest"], data["eps_growth_3yr"], data["eps_latest"],
                    data["cfo_3yr"], data["net_block"], data["net_block_3yr_back"],
                    data["net_block_preceding_year"], data["cwip"], data["cwip_preceding_year"],
                    data["cfo_last_year"], data["net_profit_last_year"], data["vol_1w_avg"],
                    data["vol_1m_avg"], data["vol_1y_avg"], data["piotroski_score"],
                    data["promoter_holding"], data["pledged_pct"], data["debt_to_equity"],
                    data["interest_coverage"], data["peg_ratio"], data["order_book"],
                    data["fii_holding"], data["dii_holding"], data["total_assets"],
                    data["dma_50"], data["dma_200"], data["shares_count"],
                    data["shares_count_10yr_back"], data["updated_at"]
                )
            )
            conn.commit()
        finally:
            conn.close()
