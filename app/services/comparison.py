"""Stock comparison service.

Performs deterministic multi-symbol side-by-side metric comparison, calculating price returns, annualized volatility, max drawdown, relative benchmark return, and fundamental valuation metrics.
"""

import math
from typing import List
from fastapi import HTTPException, status
import numpy as np
import pandas as pd
from app.models.schemas import ComparisonRequest, ComparisonResponse
from app.services.market_data import normalize_symbol, get_history, get_quote, create_meta_header


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

    # Fetch benchmark history
    try:
        bm_hist = get_history(benchmark_norm, period=period)
        bm_returns = bm_hist['Close'].pct_change().dropna()
        bm_total_return = round(float((bm_hist['Close'].iloc[-1] / bm_hist['Close'].iloc[0] - 1) * 100), 2)
    except Exception as e:
        bm_total_return = 0.0

    metrics_data = {}

    for sym in unique_symbols:
        sym_metrics = {}
        try:
            # 1. Quote fundamentals
            quote = get_quote(sym)
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
            hist = get_history(sym, period=period)
            closes = hist['Close']
            
            # Period Price Return
            start_price = float(closes.iloc[0])
            end_price = float(closes.iloc[-1])
            price_return = round(((end_price - start_price) / start_price) * 100, 2)
            sym_metrics["price_return_pct"] = price_return
            
            # Relative Return vs Benchmark
            sym_metrics["relative_return_vs_benchmark_pct"] = round(price_return - bm_total_return, 2)

            # Annualized Volatility
            daily_returns = closes.pct_change().dropna()
            if len(daily_returns) > 1:
                ann_vol = round(float(daily_returns.std() * math.sqrt(252) * 100), 2)
            else:
                ann_vol = 0.0
            sym_metrics["annualized_volatility_pct"] = ann_vol

            # Maximum Drawdown
            cummax = closes.cummax()
            drawdown = (closes - cummax) / cummax
            max_dd = round(float(drawdown.min() * 100), 2)
            sym_metrics["max_drawdown_pct"] = max_dd
            
            sym_metrics["status"] = "OK"

        except Exception as e:
            sym_metrics["status"] = f"PARTIAL_ERROR: {str(e)}"
            sym_metrics["price_return_pct"] = None
            sym_metrics["annualized_volatility_pct"] = None
            sym_metrics["max_drawdown_pct"] = None

        metrics_data[sym] = sym_metrics

    # Explanations of mathematical formulas used
    explanations = {
        "price_return_pct": "Percentage change from start price to end price over period: ((End_Price - Start_Price) / Start_Price) * 100",
        "annualized_volatility_pct": "Standard deviation of daily log/simple returns scaled to 252 trading days: std(daily_returns) * sqrt(252) * 100",
        "max_drawdown_pct": "Maximum peak-to-trough decline over the selected period: min((Price - Peak) / Peak) * 100",
        "relative_return_vs_benchmark_pct": "Stock Price Return minus Benchmark Index Return over period."
    }

    # Transparent scoring breakdown (composite metric ranking)
    score_breakdown = {}
    for sym in unique_symbols:
        d = metrics_data[sym]
        ret = d.get("price_return_pct") or 0.0
        vol = d.get("annualized_volatility_pct") or 30.0
        dd = d.get("max_drawdown_pct") or -30.0
        
        # Risk-adjusted return proxy (Sharpe ratio proxy: return / volatility)
        sharpe_proxy = round(ret / vol, 2) if vol > 0 else 0.0
        
        score_breakdown[sym] = {
            "return_score": ret,
            "volatility_penalty": vol,
            "max_drawdown_penalty": dd,
            "sharpe_ratio_proxy": sharpe_proxy,
            "scoring_methodology": "Equal-weight metric ranking. High returns with lower volatility & drawdown yield higher Sharpe proxy."
        }

    return ComparisonResponse(
        symbols=unique_symbols,
        period=period,
        benchmark=benchmark_norm,
        benchmark_return_pct=bm_total_return,
        metrics_data=metrics_data,
        formula_explanations=explanations,
        score_breakdown=score_breakdown,
        disclaimer="Quantitative financial metrics presented for comparative research. Past performance does not guarantee future results. Not investment advice.",
        meta=create_meta_header(source=f"yfinance ({period} daily OHLCV series)")
    )
