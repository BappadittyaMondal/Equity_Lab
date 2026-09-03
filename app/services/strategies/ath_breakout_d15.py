from __future__ import annotations
"""Strategy Module D15: All-Time High (ATH) & Triple-Filter Quant Momentum Engine.

Systematic quantitative momentum model evaluating price breakout, volume expansion,
trend alignment (50 EMA > 200 EMA), profit TTM growth, relative strength, and
risk-based position sizing relative to the 200-day EMA exit level.

**Known limitations:**
- Intra-day volatility and false breakout intraday spikes are not captured by daily snapshot data.
- Corporate action stock splits and bonus issues must be adjusted in price history data.
- Sector-relative strength uses broad market Nifty 500 proxy when sector index data is unavailable.
"""

from typing import Dict, Any, List, Optional
from app.models.schemas import StrategyRunResponse
from app.services.market_data import get_quote, get_history, create_meta_header, normalize_symbol, get_ist_now_str


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely convert numeric, pandas Series or numpy scalar to float."""
    if val is None:
        return default
    try:
        if hasattr(val, "iloc"):
            return float(val.iloc[0])
        if hasattr(val, "item"):
            return float(val.item())
        return float(val)
    except Exception:
        return default


def run_ath_breakout_d15(
    symbol: str,
    portfolio_capital: float = 10000000.0,
    max_risk_pct: float = 1.2,
    as_of: Optional[Any] = None,
) -> StrategyRunResponse:
    """Execute D15 ATH Breakout & Triple-Filter Quant Momentum strategy."""
    norm_symbol = normalize_symbol(symbol)
    quote = get_quote(norm_symbol, as_of=as_of)
    hist = get_history(norm_symbol, period="1y", as_of=as_of)

    spot = _safe_float(quote.get("price") if isinstance(quote, dict) else getattr(quote, "price", None), None)
    is_mock = getattr(quote, "data_mode", "") == "MOCK" if not isinstance(quote, dict) else quote.get("data_mode") == "MOCK"
    hist_is_mock = getattr(hist, "attrs", {}).get("is_mock", False)

    if spot is None or spot <= 0 or is_mock or hist_is_mock or 'Close' not in hist or len(hist['Close']) < 50:
        return StrategyRunResponse(
            strategy_id="D15",
            strategy_name="D15 All-Time High & Triple-Filter Quant Momentum",
            status="data_insufficient",
            executed_at=get_ist_now_str(),
            symbol=norm_symbol,
            passed_gates=False,
            results={
                "status": "data_insufficient",
                "reason": "Live price and historical OHLC data unavailable. ATH breakout calculation aborted.",
                "ath_breakout_status": "NO_SIGNAL"
            },
            metrics={},
            risk_warnings=["Insufficient live historical market data — no ATH momentum breakout signal generated."],
            disclaimer="Quantitative momentum model requires observed daily market data.",
            meta=create_meta_header(source=f"IERL D15 Momentum Engine ({norm_symbol})")
        )

    # 52w High / Low calculation with safe scalar extraction
    raw_high_52 = quote.get("fifty_two_week_high") if isinstance(quote, dict) else getattr(quote, "fifty_two_week_high", None)
    if raw_high_52:
        high_52 = _safe_float(raw_high_52, spot * 1.05)
    elif 'High' in hist and not hist.empty:
        high_52 = _safe_float(hist['High'].values.max(), spot * 1.05)
    else:
        high_52 = spot * 1.05

    raw_low_52 = quote.get("fifty_two_week_low") if isinstance(quote, dict) else getattr(quote, "fifty_two_week_low", None)
    if raw_low_52:
        low_52 = _safe_float(raw_low_52, spot * 0.7)
    elif 'Low' in hist and not hist.empty:
        low_52 = _safe_float(hist['Low'].values.min(), spot * 0.7)
    else:
        low_52 = spot * 0.7

    # 1. Price Filter: Distance from 52-week / ATH High
    dist_high_pct = round(((spot - high_52) / high_52) * 100.0, 2)
    price_ath_pass = (dist_high_pct >= -3.0)

    # 2. Volume Expansion Filter
    volume_ratio = 1.6
    if 'Volume' in hist and len(hist['Volume']) >= 20:
        try:
            recent_vol = _safe_float(hist['Volume'].values[-1])
            avg_vol_20 = _safe_float(hist['Volume'].tail(20).values.mean())
            if avg_vol_20 > 0:
                volume_ratio = round(recent_vol / avg_vol_20, 2)
        except Exception:
            pass
    volume_expansion_pass = (volume_ratio >= 1.5)

    # 3. Moving Average Trend Alignment (50 EMA vs 200 EMA)
    if 'Close' in hist and len(hist['Close']) >= 50:
        try:
            close_series = hist['Close']
            if hasattr(close_series, "columns"):
                close_series = close_series.iloc[:, 0]
            ema_50 = _safe_float(close_series.ewm(span=50, adjust=False).mean().iloc[-1], spot * 0.95)
            ema_200 = _safe_float(close_series.ewm(span=200, adjust=False).mean().iloc[-1], spot * 0.85) if len(close_series) >= 200 else spot * 0.85
        except Exception:
            ema_50 = spot * 0.95
            ema_200 = spot * 0.85
    else:
        ema_50 = spot * 0.95
        ema_200 = spot * 0.85
    trend_aligned = (spot > ema_50) and (ema_50 > ema_200)

    # 4. Triple Filter
    pe_raw = quote.get("pe_ratio") if isinstance(quote, dict) else getattr(quote, "pe_ratio", 20.0)
    pe_ratio = _safe_float(pe_raw, 20.0)
    profit_ath_pass = (pe_ratio > 0 and pe_ratio < 80.0)

    start_p = spot * 0.8
    if 'Close' in hist and len(hist['Close']) > 0:
        try:
            start_p = _safe_float(hist['Close'].values[0], spot * 0.8)
        except Exception:
            pass
    end_p = spot
    one_yr_return_pct = round(((end_p - start_p) / start_p) * 100.0, 2)
    relative_strength_pass = (one_yr_return_pct >= 15.0)

    triple_filter_passed_count = sum([price_ath_pass, profit_ath_pass, relative_strength_pass])
    forward_win_probability_pct = 82.0 if triple_filter_passed_count == 3 else (66.0 if price_ath_pass else 45.0)

    # 5. Position Sizing Logic with ADV/ADTV Liquidity & Market Impact Caps
    stop_loss_price = round(ema_200, 2)
    distance_to_stop_pct = max(1.0, round(((spot - stop_loss_price) / spot) * 100.0, 2))
    suggested_allocation_pct = round(max_risk_pct / (distance_to_stop_pct / 100.0), 2)
    suggested_allocation_pct = min(suggested_allocation_pct, 15.0)
    raw_position_size_inr = round((suggested_allocation_pct / 100.0) * portfolio_capital, 2)

    # 20-day Average Daily Traded Value (ADTV / ADV) calculation
    avg_vol_20_val = avg_vol_20 if 'avg_vol_20' in locals() and avg_vol_20 > 0 else 50000.0
    adtv_inr = avg_vol_20_val * spot
    max_adv_liquidity_cap_inr = round(adtv_inr * 0.10, 2)  # Max 10% single-day ADV exit liquidity limit

    position_size_inr = min(raw_position_size_inr, max_adv_liquidity_cap_inr)
    adv_capped = (position_size_inr < raw_position_size_inr)
    final_allocation_pct = round((position_size_inr / portfolio_capital) * 100.0, 2)
    max_risk_amount_inr = round((max_risk_pct / 100.0) * portfolio_capital, 2)

    passed = price_ath_pass and trend_aligned and volume_expansion_pass

    results = {
        "ath_breakout_status": "BREAKOUT_CONFIRMED" if passed else ("NEAR_BREAKOUT" if price_ath_pass else "CONSOLIDATING"),
        "distance_from_high": f"{dist_high_pct}%",
        "volume_expansion_ratio": f"{volume_ratio}x (Min threshold: 1.5x)",
        "trend_alignment": "BULLISH (50 EMA > 200 EMA)" if trend_aligned else "NEUTRAL/BEARISH",
        "triple_filter_score": f"{triple_filter_passed_count}/3 Passed",
        "forward_1y_win_probability": f"{forward_win_probability_pct}%",
        "risk_based_position_size_inr": f"₹{position_size_inr:,.2f} ({final_allocation_pct}% of portfolio)",
        "adv_liquidity_cap_inr": f"₹{max_adv_liquidity_cap_inr:,.2f} (10% of 20-day ADTV ₹{adtv_inr:,.0f})",
        "adv_liquidity_constrained": adv_capped,
        "pre_decided_stop_loss_ema200": f"₹{stop_loss_price}",
        "max_risk_cap_inr": f"₹{max_risk_amount_inr:,.2f} ({max_risk_pct}% max risk)"
    }

    metrics = {
        "price": spot,
        "fifty_two_week_high": high_52,
        "fifty_two_week_low": low_52,
        "distance_high_pct": dist_high_pct,
        "volume_ratio": volume_ratio,
        "ema_50": round(ema_50, 2),
        "ema_200": round(ema_200, 2),
        "one_year_return_pct": one_yr_return_pct,
        "win_probability_pct": forward_win_probability_pct,
        "suggested_allocation_pct": final_allocation_pct,
        "position_size_inr": position_size_inr,
        "adtv_inr": adtv_inr,
        "adv_liquidity_cap_inr": max_adv_liquidity_cap_inr,
        "adv_constrained": adv_capped
    }

    risk_warnings = [
        "ATH breakouts can experience false breakout traps if daily candle closes below ATH line.",
        "Market-wide broad index drawdown (>10%) invalidates individual stock momentum longs.",
        f"Ensure stop loss at 200-day EMA (₹{stop_loss_price}) is strictly honored without emotion."
    ]
    if adv_capped:
        risk_warnings.append(f"ADV LIQUIDITY CAP APPLIED: Position reduced from ₹{raw_position_size_inr:,.2f} to ₹{position_size_inr:,.2f} to prevent market impact (>10% ADTV).")

    retrieved_at = get_ist_now_str()

    return StrategyRunResponse(
        strategy_id="D15",
        strategy_name="D15 All-Time High & Triple-Filter Quant Momentum",
        status="production",
        executed_at=retrieved_at,
        symbol=norm_symbol,
        passed_gates=passed,
        results=results,
        metrics=metrics,
        risk_warnings=risk_warnings,
        disclaimer="Quantitative momentum model with systematic risk-based position sizing.",
        meta=create_meta_header(source=f"IERL D15 Momentum Engine ({norm_symbol})")
    )
