"""Stock return probability service.

Performs empirical distribution analysis and rolling historical return calculations to determine return probabilities, percentiles, median returns, and fat-tail risk characteristics without relying on unrealistic normal-distribution assumptions.
"""

from datetime import datetime
from typing import List, Dict, Any
from fastapi import HTTPException, status
import numpy as np
import pandas as pd
from app.models.schemas import ReturnProbabilityRequest, ReturnProbabilityResponse
from app.services.market_data import normalize_symbol, get_history, create_meta_header


def calculate_return_probability(req: ReturnProbabilityRequest) -> ReturnProbabilityResponse:
    """Calculates empirical return probability distribution over a specified horizon."""
    symbol = normalize_symbol(req.symbol)
    horizon = req.horizon_days
    threshold = req.return_threshold_pct
    method = req.method or "historical_empirical"

    # Fetch 3 years of daily data for statistical sampling
    try:
        hist = get_history(symbol, period="3y", interval="1d")
        if len(hist) < horizon + 10:
            raise ValueError(f"Insufficient historical data ({len(hist)} rows) for horizon {horizon} days.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch market data for return probability analysis of '{symbol}': {str(e)}"
        )

    closes = hist['Close'].values
    dates = hist.index

    # Calculate rolling horizon returns (%)
    # Return over horizon = (Price[t + horizon] - Price[t]) / Price[t] * 100
    horizon_returns = []
    
    if method == "bootstrap":
        # Block-bootstrap or random sampling of daily returns
        daily_rets = pd.Series(closes).pct_change().dropna().values
        np.random.seed(42)  # Deterministic seed for reproducible tests
        num_simulations = 1000
        for _ in range(num_simulations):
            sampled_rets = np.random.choice(daily_rets, size=horizon, replace=True)
            compounded = float((np.prod(1 + sampled_rets) - 1) * 100)
            horizon_returns.append(compounded)
    else:
        # Overlapping rolling N-day horizon returns
        for i in range(len(closes) - horizon):
            start_p = closes[i]
            end_p = closes[i + horizon]
            ret_pct = ((end_p - start_p) / start_p) * 100.0
            horizon_returns.append(ret_pct)

    rets_arr = np.array(horizon_returns)
    sample_size = len(rets_arr)

    if sample_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sample size is zero for selected horizon and data range."
        )

    # Empirical probability of return >= threshold
    succ_count = np.sum(rets_arr >= threshold)
    prob_above = round(float((succ_count / sample_size) * 100.0), 2)

    # Empirical probability of negative return
    neg_count = np.sum(rets_arr < 0.0)
    prob_neg = round(float((neg_count / sample_size) * 100.0), 2)

    # Percentiles P5, P25, P50, P75, P95
    p5 = round(float(np.percentile(rets_arr, 5)), 2)
    p25 = round(float(np.percentile(rets_arr, 25)), 2)
    p50 = round(float(np.percentile(rets_arr, 50)), 2)  # Median
    p75 = round(float(np.percentile(rets_arr, 75)), 2)
    p95 = round(float(np.percentile(rets_arr, 95)), 2)

    start_date = dates[0].strftime("%Y-%m-%d")
    end_date = dates[-1].strftime("%Y-%m-%d")

    assumptions = [
        f"Analysis based on {sample_size} empirical {horizon}-day holding periods between {start_date} and {end_date}.",
        "Reinvestment of dividends and transaction costs are excluded.",
        "Methodology uses empirical non-parametric distribution (no Gaussian bell curve assumption)."
    ]

    warnings = [
        "Historical return frequencies do NOT guarantee future market outcomes.",
        "Financial markets exhibit regime shifts, volatility clustering, and fat-tail risk.",
        "This calculation is a historical statistical sample, NOT a forecast or recommendation."
    ]

    return ReturnProbabilityResponse(
        symbol=symbol,
        horizon_days=horizon,
        return_threshold_pct=threshold,
        method=method,
        probability_above_threshold_pct=prob_above,
        probability_negative_return_pct=prob_neg,
        median_return_pct=p50,
        percentiles={
            "P5": p5,
            "P25": p25,
            "P50": p50,
            "P75": p75,
            "P95": p95
        },
        sample_size=sample_size,
        observation_window={
            "start_date": start_date,
            "end_date": end_date
        },
        assumptions=assumptions,
        warnings=warnings,
        meta=create_meta_header(source=f"yfinance ({symbol} 3y historical empirical series)")
    )
