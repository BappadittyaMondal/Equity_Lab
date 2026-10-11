"""Walk-Forward Backtesting Framework.

Evaluates forward stock returns across 3M, 6M, 12M, 24M, and 36M horizons against benchmark returns
and measures alpha, beta, CAGR, max drawdown, Sharpe, and Sortino ratios.
"""

import math
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.services.market_data import normalize_symbol
from app.services.backtesting.cost_model import CostModel, cost_model as _default_cost_model


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
    sharpe_ratio: float          # Annualised Sharpe ratio (multiplied by √periods_per_year)
    sortino_ratio: float         # Annualised Sortino ratio (multiplied by √periods_per_year)
    sharpe_ratio_period: float = Field(default=0.0, description="Raw per-period Sharpe (before annualisation)")
    sortino_ratio_period: float = Field(default=0.0, description="Raw per-period Sortino (before annualisation)")
    annualisation_factor: float = Field(default=1.0, description="sqrt(periods_per_year) used for Sharpe/Sortino annualisation")
    benchmark_mode: str = Field(default="REAL", description="REAL or BASELINE_6PCT_ANNUAL")
    capital_allocated_pct: float = Field(default=10.0, description="Portfolio position sizing weight percentage")
    portfolio_contribution_alpha: float = Field(default=0.0, description="Alpha scaled by capital allocation weight")


class WalkForwardBacktester:
    """Walk-forward backtesting framework."""

    def evaluate_horizon(
        self,
        symbol: str,
        horizon_months: int,
        entry_scores_and_returns: List[Dict[str, Any]],
        benchmark_returns: Optional[List[float]] = None,
        trade_value_inr: Optional[float] = None,      # P3: position-size-aware CostModel input
        slippage_pct: float = 0.05,                   # LEGACY — use trade_value_inr instead
        stt_brokerage_pct: float = 0.10,              # LEGACY — use trade_value_inr instead
        capital_allocated_pct: float = 10.0,
    ) -> WalkForwardSummary:
        """Calculate walk-forward metrics across historical periods.

        Transaction cost:
          - If trade_value_inr is provided: uses CostModel (realistic Indian equity
            all-in cost: STT+exchange+SEBI+stamp+GST+DP, ~0.35–0.55% round-trip).
          - If trade_value_inr is None: falls back to legacy flat rate
            (slippage_pct + stt_brokerage_pct). This understates costs for delivery
            trades — provide trade_value_inr for accurate net-return computation.
        """
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
                capital_allocated_pct=capital_allocated_pct,
                portfolio_contribution_alpha=0.0,
            )

        # P3: Transaction cost — use CostModel when trade_value_inr provided
        if trade_value_inr is not None and trade_value_inr > 0:
            total_friction_pct = _default_cost_model.cost_pct(trade_value_inr)
            friction_source = f"CostModel_Indian_Equity ({total_friction_pct:.4f}%)"
        else:
            total_friction_pct = slippage_pct + stt_brokerage_pct
            friction_source = f"LEGACY_FLAT ({total_friction_pct:.2f}% — understates real cost; provide trade_value_inr)"

        stock_returns = [item["stock_return"] - total_friction_pct for item in entry_scores_and_returns]
        
        if benchmark_returns and len(benchmark_returns) == len(stock_returns):
            bm_returns = benchmark_returns
            bm_mode = "REAL"
        else:
            # Dynamic Nifty 50 fetch or institutional Indian market benchmark
            fetched_bm = None
            try:
                from app.services.market_data import get_history, is_live_data
                nifty_hist = get_history("^NSEI", period=f"{max(1, horizon_months // 12)}y", interval="1mo")
                if nifty_hist is not None and not nifty_hist.empty and "Close" in nifty_hist.columns and len(nifty_hist) > 1 and is_live_data(nifty_hist):
                    pct_changes = nifty_hist["Close"].pct_change().dropna().tolist()
                    if len(pct_changes) >= len(stock_returns):
                        fetched_bm = [r * 100.0 for r in pct_changes[-len(stock_returns):]]
            except Exception:
                fetched_bm = None

            if fetched_bm and len(fetched_bm) == len(stock_returns):
                bm_returns = fetched_bm
                bm_mode = "REAL_NIFTY50"
            else:
                # Scaled baseline: 12.0% annual historical Nifty baseline scaled to horizon
                default_rate = 12.0 * (horizon_months / 12.0)
                bm_returns = [default_rate] * len(stock_returns)
                bm_mode = "BASELINE_12PCT_ANNUAL"

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

        sharpe_period = (mean_stock - rf_period) / std_dev if std_dev > 0 else 0.0
        sortino_period = (mean_stock - rf_period) / downside_std if downside_std > 0 else 0.0

        # Cumulative NAV wealth curve for max drawdown: NAV_0 = 1.0, NAV_t = NAV_{t-1} * (1 + r_t/100)
        nav = 1.0
        peak_nav = 1.0
        max_dd = 0.0
        for r in stock_returns:
            nav = max(0.0, nav * (1.0 + (r / 100.0)))
            if nav > peak_nav:
                peak_nav = nav
            dd = (peak_nav - nav) / peak_nav if peak_nav > 0 else 0.0
            if dd > max_dd:
                max_dd = dd

        # Annualise Sharpe and Sortino: multiply by sqrt(periods_per_year)
        # Each observation in stock_returns represents one horizon_months-length period.
        # periods_per_year = 12 / horizon_months (e.g. monthly → 12, quarterly → 4, annual → 1)
        # Edge case: if horizon_months == 0 or > 12, cap sensibly.
        periods_per_year = max(1.0, 12.0 / max(1, horizon_months))
        ann_factor = math.sqrt(periods_per_year)
        sharpe = round(sharpe_period * ann_factor, 2)
        sortino = round(sortino_period * ann_factor, 2)

        portfolio_alpha = round(mean_alpha * (capital_allocated_pct / 100.0), 2)

        return WalkForwardSummary(
            symbol=normalized,
            horizon_months=horizon_months,
            total_samples=len(stock_returns),
            win_rate_pct=round(win_rate, 2),
            mean_stock_return=round(mean_stock, 2),
            mean_benchmark_return=round(mean_bm, 2),
            mean_alpha=round(mean_alpha, 2),
            max_drawdown_pct=round(max_dd * 100.0, 2),
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            sharpe_ratio_period=round(sharpe_period, 2),
            sortino_ratio_period=round(sortino_period, 2),
            annualisation_factor=round(ann_factor, 4),
            benchmark_mode=bm_mode,
            capital_allocated_pct=capital_allocated_pct,
            portfolio_contribution_alpha=portfolio_alpha,
        )
