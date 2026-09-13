"""Stock comparison service.

Performs deterministic multi-symbol side-by-side metric comparison, calculating price returns, annualized volatility, max drawdown, relative benchmark return, and fundamental valuation metrics.
"""

import math
import logging
from typing import List
from fastapi import HTTPException, status
import numpy as np
import pandas as pd
from app.models.schemas import ComparisonRequest, ComparisonResponse
from app.services.market_data import normalize_symbol, get_history, get_quote, create_meta_header

logger = logging.getLogger(__name__)


def compare_stocks(req: ComparisonRequest) -> ComparisonResponse:
    """Compares 2 to 5 stocks against each other and a benchmark index."""
    # Deduplicate & validate symbol count
    raw_symbols = req.symbols
    unique_symbols = []
    for s in raw_symbols:
        norm = normalize_symbol(s)
        if norm not in unique_symbols:
            unique_symbols.append(norm)

    if len(unique_symbols) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comparison requires at least 2 distinct ticker symbols."
        )
    if len(unique_symbols) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comparison supports a maximum of 5 ticker symbols simultaneously."
        )

    period = req.period or "1y"
    benchmark_norm = normalize_symbol(req.benchmark or "^NSEI")
    as_of = getattr(req, "as_of", None)

    # Fetch benchmark history
    bm_total_return = None
    bm_returns = None
    try:
        bm_hist = get_history(benchmark_norm, period=period, as_of=as_of)
        if bm_hist is not None and not bm_hist.empty and len(bm_hist) > 1:
            bm_returns = bm_hist['Close'].pct_change().dropna()
            bm_total_return = round(float((bm_hist['Close'].iloc[-1] / bm_hist['Close'].iloc[0] - 1) * 100), 2)
    except Exception as e:
        bm_total_return = None
        bm_returns = None

    metrics_data = {}
    returns_by_sym = {}

    for sym in unique_symbols:
        sym_metrics = {}
        try:
            # 1. Quote fundamentals
            quote = get_quote(sym, as_of=as_of)
            sym_metrics["price"] = quote.price
            sym_metrics["change_percent"] = quote.change_percent
            sym_metrics["pe_ratio"] = quote.pe_ratio
            sym_metrics["market_cap_inr"] = quote.market_cap
            sym_metrics["fifty_two_week_high"] = quote.fifty_two_week_high
            sym_metrics["fifty_two_week_low"] = quote.fifty_two_week_low
            
            # Distance from 52W High (%)
            if quote.fifty_two_week_high and quote.price:
                dist_high = round(((quote.price - quote.fifty_two_week_high) / quote.fifty_two_week_high) * 100, 2)
                sym_metrics["distance_from_52w_high_pct"] = dist_high
            else:
                sym_metrics["distance_from_52w_high_pct"] = None

            # 2. Historical price metrics
            hist = get_history(sym, period=period, as_of=as_of)
            closes = hist['Close']
            
            # Period Price Return
            start_price = float(closes.iloc[0])
            end_price = float(closes.iloc[-1])
            price_return = round(((end_price - start_price) / start_price) * 100, 2)
            sym_metrics["price_return_pct"] = price_return
            
            # Relative Return vs Benchmark
            if bm_total_return is not None and price_return is not None:
                sym_metrics["relative_return_vs_benchmark_pct"] = round(price_return - bm_total_return, 2)
            else:
                sym_metrics["relative_return_vs_benchmark_pct"] = None

            # Annualized Volatility
            daily_returns = closes.pct_change().dropna()
            returns_by_sym[sym] = daily_returns
            if len(daily_returns) > 1:
                ann_vol = round(float(daily_returns.std() * math.sqrt(252) * 100), 2)
            else:
                ann_vol = 0.0
            sym_metrics["annualized_volatility_pct"] = ann_vol

            # Maximum Drawdown
            cummax = closes.cummax()
            drawdown = (closes - cummax) / cummax
            max_dd = round(float(drawdown.min() * 100), 2)
            # Beta calculation vs benchmark
            beta = None
            try:
                if len(daily_returns) > 5 and bm_returns is not None and len(bm_returns) > 5:
                    aligned = pd.concat([daily_returns, bm_returns], axis=1).dropna()
                    if len(aligned) > 5:
                        cov = float(np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])[0, 1])
                        bm_var = float(np.var(aligned.iloc[:, 1]))
                        if bm_var > 0:
                            beta = round(cov / bm_var, 2)
            except Exception as e:
                logger.warning("Beta calculation failed for %s: %s", sym, e)
            sym_metrics["beta"] = beta

            # 30D ADTV in ₹ Cr
            adtv_30d_cr = None
            try:
                if "Volume" in hist.columns and len(hist) > 0:
                    adtv_30d_cr = round(float((hist["Close"] * hist["Volume"]).tail(30).mean()) / 1e7, 2)
            except Exception as e:
                logger.warning("ADTV calculation failed for %s: %s", sym, e)
            sym_metrics["adtv_30d_cr"] = adtv_30d_cr

            # 3. Fundamental Quality & DuPont Metrics
            roce = None
            roe = None
            debt_to_equity = None
            cfo_last_year = None
            try:
                from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
                fund = ScreenerCloudConnector.get_company_fundamentals(sym)
                if fund:
                    roce = fund.get("roce_latest")
                    roe = fund.get("roe_latest")
                    debt_to_equity = fund.get("debt_to_equity")
                    cfo_last_year = fund.get("cfo_last_year")
            except Exception as e:
                logger.warning("Fundamental extraction failed for %s: %s", sym, e)
            sym_metrics["roce_latest"] = roce
            sym_metrics["roe_latest"] = roe
            sym_metrics["debt_to_equity"] = debt_to_equity
            sym_metrics["cfo_last_year"] = cfo_last_year

            # 4. Engine C9 Reverse DCF Market-Implied Growth
            implied_growth_pct = None
            dcf_verdict = None
            try:
                from app.services.strategies.reverse_dcf_c9 import run_reverse_dcf_c9
                dcf_res = run_reverse_dcf_c9(sym, as_of=as_of)
                if dcf_res and dcf_res.metrics:
                    implied_growth_pct = dcf_res.metrics.get("implied_growth_rate_pct")
                if dcf_res and dcf_res.results:
                    dcf_verdict = dcf_res.results.get("market_expectations_verdict")
            except Exception as e:
                logger.warning("Reverse DCF execution failed for %s: %s", sym, e)
            sym_metrics["reverse_dcf_implied_growth_pct"] = implied_growth_pct
            sym_metrics["reverse_dcf_market_expectations"] = dcf_verdict

            # 3-Vector Comparative Analytics Representation
            sym_metrics["vectors"] = {
                "vector_1_market_dynamics": {
                    "price_return_pct": price_return,
                    "relative_return_vs_benchmark_pct": sym_metrics.get("relative_return_vs_benchmark_pct"),
                    "annualized_volatility_pct": ann_vol,
                    "max_drawdown_pct": max_dd,
                    "beta": beta,
                    "adtv_30d_cr": adtv_30d_cr,
                },
                "vector_2_fundamental_quality": {
                    "roce_pct": roce,
                    "roe_pct": roe,
                    "debt_to_equity": debt_to_equity,
                    "cfo_last_year_cr": cfo_last_year,
                },
                "vector_3_valuation_implied_growth": {
                    "pe_ratio": quote.pe_ratio,
                    "reverse_dcf_implied_growth_pct": implied_growth_pct,
                    "reverse_dcf_market_expectations": dcf_verdict,
                    "distance_from_52w_high_pct": sym_metrics.get("distance_from_52w_high_pct"),
                },
            }

            sym_metrics["status"] = "OK"

        except Exception as e:
            sym_metrics["status"] = f"PARTIAL_ERROR: {str(e)}"
            sym_metrics["price_return_pct"] = None
            sym_metrics["relative_return_vs_benchmark_pct"] = None
            sym_metrics["annualized_volatility_pct"] = None
            sym_metrics["max_drawdown_pct"] = None
            sym_metrics["beta"] = None

        metrics_data[sym] = sym_metrics

    # Explanations of mathematical formulas used
    explanations = {
        "price_return_pct": "Percentage change from start price to end price over period: ((End_Price - Start_Price) / Start_Price) * 100",
        "annualized_volatility_pct": "Standard deviation of daily log/simple returns scaled to 252 trading days: std(daily_returns) * sqrt(252) * 100",
        "max_drawdown_pct": "Maximum peak-to-trough decline over the selected period: min((Price - Peak) / Peak) * 100",
        "relative_return_vs_benchmark_pct": "Stock Price Return minus Benchmark Index Return over period.",
        "beta": "Sensitivity of stock returns to benchmark returns: cov(r_stock, r_benchmark) / var(r_benchmark)",
        "reverse_dcf_implied_growth_pct": "Market-implied steady-state growth rate solving inverse Gordon Growth: ((r * PE - (1 - b)) / (PE + (1 - b))) * 100 via Engine C9",
        "pairwise_return_correlation": "Pearson correlation coefficient between daily return series of compared stocks: cov(r1, r2) / (std1 * std2)"
    }

    # Pairwise 60-Day / Period Return Correlation Matrix with Degrees of Freedom Guard
    pairwise_correlations: Dict[str, float] = {}
    correlation_degrees_of_freedom: Dict[str, Any] = {}
    for i in range(len(unique_symbols)):
        for j in range(i + 1, len(unique_symbols)):
            s1 = unique_symbols[i]
            s2 = unique_symbols[j]
            r1 = returns_by_sym.get(s1)
            r2 = returns_by_sym.get(s2)
            if r1 is not None and r2 is not None and len(r1) > 5 and len(r2) > 5:
                aligned = pd.concat([r1, r2], axis=1, join="inner").dropna()
                n_samples = len(aligned)
                if n_samples > 5:
                    c_val = float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1]))
                    if not math.isnan(c_val):
                        pair_key = f"{s1}_vs_{s2}"
                        pairwise_correlations[pair_key] = round(c_val, 3)
                        correlation_degrees_of_freedom[pair_key] = {
                            "sample_sessions": n_samples,
                            "correlation_significance": "STATISTICALLY_ROBUST" if n_samples >= 30 else "SAMPLE_TOO_SMALL_HIGH_VARIANCE",
                            "degrees_of_freedom": max(0, n_samples - 2)
                        }

    # Transparent scoring breakdown (composite metric ranking)
    score_breakdown = {}
    for sym in unique_symbols:
        d = metrics_data[sym]
        ret = d.get("price_return_pct")
        vol = d.get("annualized_volatility_pct")
        dd = d.get("max_drawdown_pct")

        # Risk-adjusted return proxy (Sharpe ratio proxy: return / volatility)
        # Avoid falsifying risk metrics with arbitrary 30% fallbacks
        if vol is not None and vol > 0 and ret is not None:
            sharpe_proxy = round(ret / vol, 2)
            data_status = "VERIFIED_PRICE_SERIES"
        else:
            sharpe_proxy = None
            data_status = "DATA_INSUFFICIENT_FOR_SHARPE"

        score_breakdown[sym] = {
            "return_score": ret if ret is not None else 0.0,
            "volatility_penalty": vol,
            "max_drawdown_penalty": dd,
            "sharpe_ratio_proxy": sharpe_proxy,
            "data_completeness": data_status,
            "scoring_methodology": "Equal-weight metric ranking. High returns with lower volatility & drawdown yield higher Sharpe proxy."
        }

    # Intent-Conditioned Ranking Evaluation
    intent_ranking = None
    target_intent = (req.intent or "").upper().strip() if req.intent else None
    if target_intent:
        ranked_items = []
        for sym in unique_symbols:
            m = metrics_data.get(sym, {})
            v1 = m.get("vectors", {}).get("vector_1_market_dynamics", {})
            v2 = m.get("vectors", {}).get("vector_2_fundamental_quality", {})
            v3 = m.get("vectors", {}).get("vector_3_valuation_implied_growth", {})
            
            drivers = []

            if "SIP" in target_intent or "COMPOUNDER" in target_intent:
                roce_val = v2.get("roce_pct") or 0.0
                roe_val = v2.get("roe_pct") or 0.0
                dte_val = v2.get("debt_to_equity") if v2.get("debt_to_equity") is not None else 1.0
                dd_val = abs(v1.get("max_drawdown_pct") or 30.0)
                cfo_val = v2.get("cfo_last_year_cr") or 0.0

                roce_pts = min(40.0, max(0.0, roce_val * 1.5))
                roe_pts = min(25.0, max(0.0, roe_val * 1.25))
                debt_pts = 20.0 if dte_val <= 0.3 else (10.0 if dte_val <= 0.8 else 0.0)
                dd_pts = max(0.0, min(15.0, (40.0 - dd_val) * 0.375))
                score = round(roce_pts + roe_pts + debt_pts + dd_pts, 1)

                drivers.append(f"ROCE: {roce_val}% (+{roce_pts:.1f} pts)")
                drivers.append(f"D/E: {dte_val} (+{debt_pts:.1f} pts)")
                if cfo_val > 0:
                    drivers.append(f"Positive CFO: ₹{cfo_val} Cr")

            elif "SWING" in target_intent or "MOMENTUM" in target_intent:
                ret_val = v1.get("price_return_pct") or 0.0
                dist_high = v3.get("distance_from_52w_high_pct") if v3.get("distance_from_52w_high_pct") is not None else -30.0
                adtv_val = v1.get("adtv_30d_cr") or 0.0
                vol_val = v1.get("annualized_volatility_pct") or 35.0

                ret_pts = min(40.0, max(0.0, (ret_val + 20.0) * 0.8))
                high_pts = min(30.0, max(0.0, (30.0 + dist_high) * 1.0))
                liq_pts = 20.0 if adtv_val >= 25.0 else (10.0 if adtv_val >= 5.0 else 0.0)
                vol_pts = max(0.0, min(10.0, (50.0 - vol_val) * 0.25))
                score = round(ret_pts + high_pts + liq_pts + vol_pts, 1)

                drivers.append(f"Period Return: {ret_val}% (+{ret_pts:.1f} pts)")
                drivers.append(f"Distance to 52W High: {dist_high}% (+{high_pts:.1f} pts)")
                drivers.append(f"ADTV 30D: ₹{adtv_val} Cr (+{liq_pts:.1f} pts)")

            elif "TURNAROUND" in target_intent:
                cfo_val = v2.get("cfo_last_year_cr") or 0.0
                cfo_pts = 35.0 if cfo_val > 0 else 0.0
                dte_val = v2.get("debt_to_equity") if v2.get("debt_to_equity") is not None else 2.0
                debt_pts = 25.0 if dte_val <= 1.0 else (15.0 if dte_val <= 1.5 else 0.0)
                ret_val = v1.get("price_return_pct") or 0.0
                ret_pts = min(25.0, max(0.0, (ret_val + 10.0) * 0.7))
                dcf_growth = v3.get("reverse_dcf_implied_growth_pct")
                dcf_pts = 15.0 if (dcf_growth is not None and dcf_growth <= 12.0) else 5.0
                score = round(cfo_pts + debt_pts + ret_pts + dcf_pts, 1)

                drivers.append(f"CFO Inflection: {'Positive (₹' + str(cfo_val) + ' Cr)' if cfo_val > 0 else 'Distressed'} (+{cfo_pts:.1f} pts)")
                drivers.append(f"Solvency D/E: {dte_val} (+{debt_pts:.1f} pts)")
                drivers.append(f"Price Stabilization: {ret_val}% (+{ret_pts:.1f} pts)")
                if dcf_growth is not None:
                    drivers.append(f"Implied Growth Discount: {dcf_growth}% (+{dcf_pts:.1f} pts)")

            elif "MULTIBAGGER" in target_intent or "MICROCAP" in target_intent:
                ret_val = v1.get("price_return_pct") or 0.0
                ret_pts = min(35.0, max(0.0, (ret_val + 20.0) * 0.7))
                roce_val = v2.get("roce_pct") or 0.0
                roce_pts = min(25.0, max(0.0, roce_val * 1.0))
                dte_val = v2.get("debt_to_equity") if v2.get("debt_to_equity") is not None else 1.0
                debt_pts = 20.0 if dte_val <= 0.5 else (10.0 if dte_val <= 1.0 else 0.0)
                cfo_val = v2.get("cfo_last_year_cr") or 0.0
                cfo_pts = 20.0 if cfo_val > 0 else 0.0
                score = round(ret_pts + roce_pts + debt_pts + cfo_pts, 1)

                drivers.append(f"Expansion Velocity: {ret_val}% (+{ret_pts:.1f} pts)")
                drivers.append(f"ROCE Capital Efficiency: {roce_val}% (+{roce_pts:.1f} pts)")
                drivers.append(f"Balance Sheet Strength: D/E {dte_val} (+{debt_pts:.1f} pts)")
                if cfo_val > 0:
                    drivers.append(f"Operational Cash: ₹{cfo_val} Cr (+{cfo_pts:.1f} pts)")

            elif "VALUE" in target_intent or "ASSET" in target_intent:
                pe_val = v3.get("pe_ratio")
                pe_pts = 35.0 if (pe_val and 0 < pe_val <= 15.0) else (20.0 if (pe_val and pe_val <= 25.0) else 5.0)
                dte_val = v2.get("debt_to_equity") if v2.get("debt_to_equity") is not None else 1.0
                debt_pts = 25.0 if dte_val <= 0.5 else (15.0 if dte_val <= 1.0 else 0.0)
                cfo_val = v2.get("cfo_last_year_cr") or 0.0
                cfo_pts = 25.0 if cfo_val > 0 else 0.0
                dist_high = v3.get("distance_from_52w_high_pct") if v3.get("distance_from_52w_high_pct") is not None else -20.0
                discount_pts = min(15.0, max(0.0, abs(dist_high) * 0.5))
                score = round(pe_pts + debt_pts + cfo_pts + discount_pts, 1)

                drivers.append(f"Valuation Multiplier: P/E {pe_val if pe_val else 'N/A'} (+{pe_pts:.1f} pts)")
                drivers.append(f"Solvency Moat: D/E {dte_val} (+{debt_pts:.1f} pts)")
                drivers.append(f"Positive CFO: ₹{cfo_val} Cr (+{cfo_pts:.1f} pts)")
                drivers.append(f"Margin of Safety: {abs(dist_high):.1f}% from peak (+{discount_pts:.1f} pts)")

            else:
                ret_val = v1.get("price_return_pct") or 0.0
                vol_val = v1.get("annualized_volatility_pct") or 25.0
                score = round(max(0.0, min(100.0, 50.0 + (ret_val / max(5.0, vol_val)) * 25.0)), 1)
                drivers.append(f"Sharpe Proxy Score: {score}")

            ranked_items.append({
                "symbol": sym,
                "intent_score": score,
                "key_drivers": drivers
            })

        ranked_items.sort(key=lambda x: x["intent_score"], reverse=True)
        for idx, item in enumerate(ranked_items):
            item["rank"] = idx + 1

        winner_sym = ranked_items[0]["symbol"]
        winner_score = ranked_items[0]["intent_score"]
        runner_up = ranked_items[1]["symbol"] if len(ranked_items) > 1 else None

        intent_ranking = {
            "intent": target_intent,
            "winner": winner_sym,
            "winner_intent_score": winner_score,
            "ranked_symbols": ranked_items,
            "institutional_justification": (
                f"{winner_sym} is declared the intent-conditioned winner for archetype '{target_intent}' "
                f"with a composite score of {winner_score}/100"
                + (f" surpassing {runner_up} ({ranked_items[1]['intent_score']}/100)." if runner_up else ".")
            )
        }

    # Cross-Sector Normalization Intelligence
    cross_sector_notes = []
    is_financial_map = {}
    for sym in unique_symbols:
        clean = sym.upper()
        is_fin = ("BANK" in clean or "HDFC" in clean or "ICICI" in clean or "AXIS" in clean or "KOTAK" in clean or "FINANCE" in clean or "FINSERV" in clean)
        is_financial_map[sym] = is_fin

    fin_count = sum(1 for v in is_financial_map.values() if v)
    non_fin_count = len(is_financial_map) - fin_count
    if fin_count > 0 and non_fin_count > 0:
        cross_sector_notes.append(
            "Fiduciary Cross-Sector Advisory: Comparison contains both Financial/Lending institutions and Operating entities. "
            "Metrics such as ROCE, Operating Cash Flow, and Debt/Equity cannot be directly compared between banks and non-banks. "
            "For lending entities, evaluate Price-to-Book (P/B), Net Interest Margin (NIM), and Gross NPA ratios."
        )

    return ComparisonResponse(
        symbols=unique_symbols,
        period=period,
        benchmark=benchmark_norm,
        benchmark_return_pct=bm_total_return,
        metrics_data=metrics_data,
        formula_explanations=explanations,
        score_breakdown=score_breakdown,
        pairwise_correlations=pairwise_correlations if pairwise_correlations else None,
        correlation_degrees_of_freedom=correlation_degrees_of_freedom if correlation_degrees_of_freedom else None,
        intent_conditioned_ranking=intent_ranking,
        cross_sector_comparison_notes=cross_sector_notes if cross_sector_notes else None,
        disclaimer="Quantitative financial metrics presented for comparative research. Past performance does not guarantee future results. Not investment advice.",
        meta=create_meta_header(source=f"yfinance ({period} daily OHLCV series)", as_of=as_of)
    )

