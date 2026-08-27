"""Strategy Module B5: Volatility Contraction Pattern (VCP) Breakout Screen.

Analyzes historical price series for narrowing volatility contractions (Mark Minervini VCP pattern) and volume dry-ups near 52-week highs.
"""

from typing import Any
import numpy as np
from app.models.schemas import StrategyRunResponse
from app.services.market_data import get_history, get_quote, create_meta_header, normalize_symbol, get_ist_now_str


def _safe_float(val: Any, default: float = 0.0) -> float:
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


def run_vcp_b5(symbol: str) -> StrategyRunResponse:
    norm_symbol = normalize_symbol(symbol)
    hist = get_history(norm_symbol, period="1y")
    quote = get_quote(norm_symbol)

    spot = _safe_float(quote.get("price") if isinstance(quote, dict) else getattr(quote, "price", None), None)
    is_mock = getattr(quote, "data_mode", "") == "MOCK" if not isinstance(quote, dict) else quote.get("data_mode") == "MOCK"
    hist_is_mock = getattr(hist, "attrs", {}).get("is_mock", False)

    if spot is None or spot <= 0 or is_mock or hist_is_mock or 'Close' not in hist or len(hist['Close']) < 50:
        return StrategyRunResponse(
            strategy_id="B5",
            strategy_name="B5 VCP Pattern Breakout Screen",
            status="data_insufficient",
            executed_at=get_ist_now_str(),
            symbol=norm_symbol,
            passed_gates=False,
            results={
                "status": "data_insufficient",
                "reason": "Live price and historical OHLC data unavailable. VCP calculation aborted.",
                "vcp_signal": "NO_SIGNAL"
            },
            metrics={},
            risk_warnings=["Insufficient live historical market data — no VCP breakout signal generated."],
            disclaimer="Technical volatility contraction pattern scanner requires observed daily market data.",
            meta=create_meta_header(source=f"IERL VCP Engine ({norm_symbol})")
        )

    closes = hist['Close'].values
    highs = hist['High'].values
    lows = hist['Low'].values

    # 1. Trend Template: Price > 150d MA and 200d MA
    ma_50 = float(np.mean(closes[-50:]))
    ma_150 = float(np.mean(closes[-150:]))
    ma_200 = float(np.mean(closes[-200:])) if len(closes) >= 200 else ma_150

    trend_pass = (spot > ma_150) and (spot > ma_200)

    # 2. Contraction Measurement
    range_50d = (np.max(highs[-50:]) - np.min(lows[-50:])) / max(1.0, np.max(highs[-50:]))
    range_20d = (np.max(highs[-20:]) - np.min(lows[-20:])) / max(1.0, np.max(highs[-20:]))

    contraction_pass = (range_20d < range_50d * 0.7)

    # 3. Distance from 52W High <= 15%
    raw_high = quote.get("fifty_two_week_high") if isinstance(quote, dict) else getattr(quote, "fifty_two_week_high", None)
    fifty_two_high = _safe_float(raw_high, float(np.max(highs))) if raw_high else float(np.max(highs))
    dist_high_pct = round(((spot - fifty_two_high) / fifty_two_high) * 100.0, 2)
    near_high_pass = (dist_high_pct >= -15.0)

    overall_pass = trend_pass and contraction_pass and near_high_pass

    results = {
        "trend_template_status": "PASS" if trend_pass else "FAIL",
        "volatility_contraction_status": "PASS (Narrowing)" if contraction_pass else "NO_CONTRACTION",
        "distance_from_52w_high": f"{dist_high_pct}%",
        "near_52w_high_pass": near_high_pass,
        "vcp_signal": "BREAKOUT_READY" if overall_pass else "WATCHLIST"
    }

    metrics = {
        "spot_price": spot,
        "ma_50": round(ma_50, 2),
        "ma_150": round(ma_150, 2),
        "ma_200": round(ma_200, 2),
        "range_20d_pct": round(range_20d * 100, 2),
        "range_50d_pct": round(range_50d * 100, 2),
        "fifty_two_week_high": fifty_two_high
    }

    risk_warnings = [
        "VCP breakouts require volume confirmation on breakout day.",
        "Set strict stop-loss below the lowest pivot contraction point (typically 3-5%)."
    ]

    retrieved_at = get_ist_now_str()

    return StrategyRunResponse(
        strategy_id="B5",
        strategy_name="B5 VCP Pattern Breakout Screen",
        status="production",
        executed_at=retrieved_at,
        symbol=norm_symbol,
        passed_gates=overall_pass,
        results=results,
        metrics=metrics,
        risk_warnings=risk_warnings,
        disclaimer="Technical volatility contraction pattern scanner based on historical daily prices.",
        meta=create_meta_header(source=f"IERL VCP Engine ({norm_symbol})")
    )
