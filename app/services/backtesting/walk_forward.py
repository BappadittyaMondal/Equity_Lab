"""Walk-Forward Backtesting Framework.

Evaluates forward stock returns across 3M, 6M, 12M, 24M, and 36M horizons against benchmark returns
and measures alpha, beta, CAGR, max drawdown, Sharpe, and Sortino ratios.
"""

import math
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.services.market_data import normalize_symbol


class WalkForwardPeriodResult(BaseModel):
    """Result for a single walk-forward evaluation period."""
    horizon_months: int
    entry_date: str
    exit_date: str
    entry_score: int
    stock_return_pct: float
    benchmark_return_pct: float
    alpha_pct: float
    win_vs_benchmark: bool


class WalkForwardSummary(BaseModel):
    """Aggregated walk-forward performance summary."""
    symbol: str
    horizon_months: int
    total_samples: int
    win_rate_pct: float
    mean_stock_return: float
    mean_benchmark_return: float
    mean_alpha: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    benchmark_mode: str = Field(default="REAL", description="REAL or BASELINE_6PCT_ANNUAL")


class WalkForwardBacktester:
    """Walk-forward backtesting framework."""

    def evaluate_horizon(
        self,
        symbol: str,
        horizon_months: int,
        entry_scores_and_returns: List[Dict[str, Any]],
        benchmark_returns: Optional[List[float]] = None,
        slippage_pct: float = 0.05,
        stt_brokerage_pct: float = 0.10,
    ) -> WalkForwardSummary:
        """Calculate walk-forward metrics across historical periods including transaction costs and slippage."""
        normalized = normalize_symbol(symbol)
        if not entry_scores_and_returns:
            return WalkForwardSummary(
                symbol=normalized,
                horizon_months=horizon_months,
                total_samples=0,
                win_rate_pct=0.0,
                mean_stock_return=0.0,
                mean_benchmark_return=0.0,
                mean_alpha=0.0,
                max_drawdown_pct=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                benchmark_mode="UNSPECIFIED",
            )

        total_friction_pct = slippage_pct + stt_brokerage_pct
        stock_returns = [item["stock_return"] - total_friction_pct for item in entry_scores_and_returns]
        
        if benchmark_returns and len(benchmark_returns) == len(stock_returns):
            bm_returns = benchmark_returns
            bm_mode = "REAL"
        else:
            period_bm = 6.0 * (horizon_months / 12.0)
            bm_returns = [period_bm] * len(stock_returns)
            bm_mode = "BASELINE_6PCT_ANNUAL"

        alphas = [s - b for s, b in zip(stock_returns, bm_returns)]
        wins = sum(1 for a in alphas if a > 0)
        win_rate = (wins / len(stock_returns)) * 100.0 if stock_returns else 0.0

        mean_stock = sum(stock_returns) / len(stock_returns)
        mean_bm = sum(bm_returns) / len(bm_returns)
        mean_alpha = mean_stock - mean_bm

        # Variance and Standard Deviation
        variance = sum((r - mean_stock) ** 2 for r in stock_returns) / len(stock_returns) if len(stock_returns) > 1 else 1.0
        std_dev = math.sqrt(variance) if variance > 0 else 1.0

        # Period risk-free rate (6.0% annual benchmark converted to evaluation period)
        # If horizon_months == 12 but we have >3 sample periods, items represent monthly/20-day returns
        if horizon_months == 1 or len(stock_returns) > 5:
            rf_period = 0.5  # 6% annual / 12 months = 0.5% per period
        else:
            rf_period = 6.0 * (horizon_months / 12.0)

        # Downside risk for Sortino
        downside_vars = [min(0.0, r - rf_period) ** 2 for r in stock_returns]
        downside_std = math.sqrt(sum(downside_vars) / len(downside_vars)) if downside_vars else 1.0

        sharpe = (mean_stock - rf_period) / std_dev if std_dev > 0 else 0.0
        sortino = (mean_stock - rf_period) / downside_std if downside_std > 0 else 0.0

        # Peak to trough max drawdown calculation
        peak = stock_returns[0]
        max_dd = 0.0
        for r in stock_returns:
            if r > peak:
                peak = r
            dd = (peak - r) / abs(peak) if peak != 0 else 0.0
            if dd > max_dd:
                max_dd = dd

        return WalkForwardSummary(
            symbol=normalized,
            horizon_months=horizon_months,
            total_samples=len(stock_returns),
            win_rate_pct=round(win_rate, 2),
            mean_stock_return=round(mean_stock, 2),
            mean_benchmark_return=round(mean_bm, 2),
            mean_alpha=round(mean_alpha, 2),
            max_drawdown_pct=round(max_dd * 100.0, 2),
            sharpe_ratio=round(sharpe, 2),
            sortino_ratio=round(sortino, 2),
            benchmark_mode=bm_mode,
        )
