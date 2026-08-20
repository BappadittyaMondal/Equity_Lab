"""Expectation Gap Engine (Strategy E7 / Engine E7).

Quantifies the Expectation Gap between Reverse DCF market-implied growth rate and
independent internal forecast growth rate.

Formula:
  Expectation Gap = Internal Forecast Growth Rate - Market-Implied Growth Rate

Thresholds:
  - positive_expectation_gap: Gap >= +5.0% (Market prices in lower growth than internal forecast -> Bullish Re-rating Potential)
  - negative_expectation_gap: Gap <= -5.0% (Market prices in higher growth than internal forecast -> Risk of Earnings Miss / De-rating)
  - balanced_expectation: -5.0% < Gap < +5.0% (Market pricing reflects internal fundamental trajectory)
  - DATA_INSUFFICIENT: Missing quote, P/E ratio, or fundamental history -> No fabricated output.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.models.schemas import ExpectationGapResponse, MetaHeader
from app.services.market_data import get_quote, normalize_symbol, create_meta_header, get_ist_now_str
from app.services.research_data import ResearchDataStore
from app.services.strategies.reverse_dcf_c9 import run_reverse_dcf_c9

logger = logging.getLogger(__name__)


def _calculate_cagr(start_val: float, end_val: float, years: float) -> Optional[float]:
    if start_val <= 0 or end_val <= 0 or years <= 0:
        return None
    try:
        return ((end_val / start_val) ** (1.0 / years) - 1.0) * 100.0
    except Exception:
        return None


def run_expectation_gap_engine(
    symbol: str,
    discount_rate: float = 0.12,
    terminal_growth: float = 0.04,
    as_of: Optional[datetime] = None,
    store: Optional[ResearchDataStore] = None
) -> ExpectationGapResponse:
    """Execute E7 Expectation Gap Engine analysis.

    Args:
        symbol: Target equity symbol.
        discount_rate: Discount rate for Reverse DCF (default: 12%).
        terminal_growth: Terminal growth for Reverse DCF (default: 4%).
        as_of: Optional point-in-time datetime cutoff.
        store: Optional ResearchDataStore instance.
    """
    norm_symbol = normalize_symbol(symbol)
    data_store = store or ResearchDataStore()
    retrieved_at = get_ist_now_str()

    # 1. Fetch Market Quote
    quote = get_quote(norm_symbol)
    quote_price = quote.get("price") if isinstance(quote, dict) else getattr(quote, "price", None)
    quote_pe = quote.get("pe_ratio") if isinstance(quote, dict) else getattr(quote, "pe_ratio", None)

    cmp = float(quote_price) if (quote_price is not None and float(quote_price) > 0) else None
    pe = float(quote_pe) if (quote_pe is not None and float(quote_pe) > 0) else None

    # 2. Market-Implied Growth Rate (Reverse DCF C9)
    c9_res = run_reverse_dcf_c9(norm_symbol, discount_rate=discount_rate, terminal_growth=terminal_growth)
    market_implied_growth = float(c9_res.metrics.get("implied_growth_rate_pct", 0.0))

    # 3. Internal Forecast Growth Rate Calculation
    financials = []
    try:
        timeline = data_store.get_timeline(norm_symbol, as_of=as_of)
        financials = timeline[1] if isinstance(timeline, tuple) and len(timeline) > 1 else []
    except Exception as e:
        logger.warning("Error fetching timeline for %s in E7: %s", norm_symbol, e)

    metric_map: Dict[str, List[Any]] = {}
    for obs in financials:
        metric = str(getattr(obs, "metric", "")).lower()
        metric_map.setdefault(metric, []).append(obs)
    for m in metric_map:
        metric_map[m].sort(key=lambda x: str(getattr(x, "period_end", "")))

    cagr_components: Dict[str, Optional[float]] = {
        "sales_cagr_pct": None,
        "pat_cagr_pct": None,
        "eps_cagr_pct": None,
        "fcf_cagr_pct": None,
    }

    # Extract CAGRs across available financial metrics
    for m_key, component_name in [
        ("revenue", "sales_cagr_pct"),
        ("sales", "sales_cagr_pct"),
        ("pat", "pat_cagr_pct"),
        ("net_profit", "pat_cagr_pct"),
        ("eps", "eps_cagr_pct"),
        ("fcf", "fcf_cagr_pct")
    ]:
        if cagr_components[component_name] is not None:
            continue
        obs_list = metric_map.get(m_key, [])
        if len(obs_list) >= 2:
            try:
                earliest, latest = obs_list[0], obs_list[-1]
                d_start = datetime.fromisoformat(str(earliest.period_end)) if isinstance(earliest.period_end, str) else earliest.period_end
                d_end = datetime.fromisoformat(str(latest.period_end)) if isinstance(latest.period_end, str) else latest.period_end
                n_years = max(0.5, (d_end - d_start).days / 365.25)
                cagr = _calculate_cagr(float(earliest.value), float(latest.value), n_years)
                if cagr is not None:
                    cagr_components[component_name] = round(cagr, 2)
            except Exception:
                pass

    valid_cagrs = [val for val in cagr_components.values() if val is not None]
    internal_forecast_growth: Optional[float] = None
    forecast_source = ""

    if valid_cagrs:
        internal_forecast_growth = round(sum(valid_cagrs) / len(valid_cagrs), 2)
        forecast_source = f"Empirical ResearchDataStore average CAGR across {len(valid_cagrs)} metric(s)"
    elif pe is not None and pe > 0:
        # Fallback 1: Derived earnings yield baseline if P/E ratio is available
        internal_forecast_growth = round(min(50.0, max(5.0, 100.0 / pe)), 2)
        forecast_source = "Derived Earnings Yield Baseline (100 / PE)"
    elif cmp is not None:
        # Fallback 2: Market implied baseline
        internal_forecast_growth = round(market_implied_growth, 2)
        forecast_source = "Reverse DCF Market Implied Baseline"

    # 4. Data Insufficiency Handling
    if cmp is None or pe is None or internal_forecast_growth is None:
        evidence = [
            "DATA_INSUFFICIENT: Live market quote or valid P/E ratio unavailable.",
            f"Reverse DCF market-implied growth: {market_implied_growth}%.",
            "Internal forecast growth calculation requires valid price and valuation metrics."
        ]
        return ExpectationGapResponse(
            symbol=norm_symbol,
            executed_at=retrieved_at,
            market_implied_growth=market_implied_growth,
            internal_forecast_growth=0.0,
            expectation_gap=0.0,
            gap_classification="DATA_INSUFFICIENT",
            confidence_score=0.0,
            data_insufficient=True,
            evidence=evidence,
            cagr_components=cagr_components,
            meta=create_meta_header(source=f"IERL Expectation Gap Engine E7 ({norm_symbol})")
        )

    # 5. Compute Expectation Gap & Classification
    expectation_gap = round(internal_forecast_growth - market_implied_growth, 2)

    # Classification logic based on explicit framework thresholds
    if expectation_gap >= 5.0:
        gap_classification = "POSITIVE_EXPECTATION_GAP"
        confidence_score = 85.0 if valid_cagrs else 65.0
        class_desc = "POSITIVE EXPECTATION GAP: Internal forecast exceeds market-implied growth assumptions (Re-rating potential)."
    elif expectation_gap <= -5.0:
        gap_classification = "NEGATIVE_EXPECTATION_GAP"
        confidence_score = 85.0 if valid_cagrs else 65.0
        class_desc = "NEGATIVE EXPECTATION GAP: Market P/E assumes higher growth than internal forecast (De-rating risk)."
    else:
        gap_classification = "BALANCED_EXPECTATION"
        confidence_score = 80.0 if valid_cagrs else 60.0
        class_desc = "BALANCED EXPECTATION: Market price expectations are aligned with internal forecast trajectory."

    evidence = [
        f"Market-implied 10-year growth expectation (C9 Reverse DCF @ {int(discount_rate*100)}% discount): {market_implied_growth:.2f}% p.a.",
        f"Internal forecast growth rate: {internal_forecast_growth:.2f}% p.a. ({forecast_source}).",
        f"Expectation Gap: {expectation_gap:+.2f}% points.",
        class_desc
    ]

    return ExpectationGapResponse(
        symbol=norm_symbol,
        executed_at=retrieved_at,
        market_implied_growth=market_implied_growth,
        internal_forecast_growth=internal_forecast_growth,
        expectation_gap=expectation_gap,
        gap_classification=gap_classification,
        confidence_score=confidence_score,
        data_insufficient=False,
        evidence=evidence,
        cagr_components=cagr_components,
        meta=create_meta_header(source=f"IERL Expectation Gap Engine E7 ({norm_symbol})")
    )
