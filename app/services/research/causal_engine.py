"""Causal Analysis Engine — Phase 7.

Computes empirical lead-lag relationships between corporate business events
(earnings releases, capex announcements, governance alerts, management changes)
and post-event equity return windows using non-parametric historical return distributions.

Pipeline Law: No synthetic numbers or fixed fallbacks. If historical event data
or price history is insufficient, returns an explicit DATA_UNAVAILABLE signal.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from app.services.market_data import normalize_symbol, get_history, create_meta_header, get_ist_now_str
from app.services.research_data import ResearchDataStore

logger = logging.getLogger(__name__)


def analyze_causal_event_impacts(
    symbol: str,
    as_of: Optional[datetime] = None,
    store: Optional[ResearchDataStore] = None,
) -> Dict[str, Any]:
    """Analyze empirical causal lead-lag return impacts of corporate events.

    Args:
        symbol: Target equity symbol.
        as_of: Optional evaluation cutoff timestamp.
        store: Optional ResearchDataStore instance.

    Returns:
        Dict with status, event_causal_relationships, net_causal_conviction_delta, evidence, meta.
    """
    norm_symbol = normalize_symbol(symbol)
    data_store = store or ResearchDataStore()
    as_of_str = as_of.isoformat() if isinstance(as_of, datetime) else (str(as_of) if as_of else None)

    # 1. Fetch events from ResearchDataStore
    events = []
    try:
        timeline = data_store.get_timeline(norm_symbol, as_of=as_of)
        events = timeline[2] if isinstance(timeline, tuple) and len(timeline) > 2 else []
    except Exception as e:
        logger.warning("Error fetching events for %s: %s", norm_symbol, e)

    # 2. Fetch daily price history
    hist = None
    try:
        hist = get_history(norm_symbol, period="5y", interval="1d", as_of=as_of)
    except Exception as e:
        logger.warning("Error fetching history for %s: %s", norm_symbol, e)

    if not events or hist is None or hist.empty or "Close" not in hist.columns:
        return {
            "symbol": norm_symbol,
            "status": "DATA_UNAVAILABLE",
            "executed_at": get_ist_now_str(),
            "event_causal_relationships": [],
            "net_causal_conviction_delta": 0.0,
            "evidence": ["DATA_UNAVAILABLE: Insufficient event filings or price history observations."],
            "key_risks": ["Causal impact calculation suspended due to missing historical observation window."],
            "meta": create_meta_header(source=f"Causal Engine ({norm_symbol})", as_of=as_of_str)
        }

    # Prepare price series indexed by date string YYYY-MM-DD
    hist = hist.copy()
    hist.index = hist.index.tz_localize(None) if hasattr(hist.index, "tz_localize") and hist.index.tz else hist.index
    price_by_date = {}
    dates_list = []
    closes_list = []

    for idx, row in hist.iterrows():
        try:
            d_str = idx.strftime("%Y-%m-%d")
            c_val = float(row["Close"])
            price_by_date[d_str] = c_val
            dates_list.append(d_str)
            closes_list.append(c_val)
        except Exception:
            continue

    if len(dates_list) < 30:
        return {
            "symbol": norm_symbol,
            "status": "DATA_UNAVAILABLE",
            "executed_at": get_ist_now_str(),
            "event_causal_relationships": [],
            "net_causal_conviction_delta": 0.0,
            "evidence": ["DATA_UNAVAILABLE: Price history shorter than 30 trading days."],
            "key_risks": ["Insufficient price observations for causal window analysis."],
            "meta": create_meta_header(source=f"Causal Engine ({norm_symbol})", as_of=as_of_str)
        }

    # Fetch benchmark price series for genuine Cumulative Abnormal Return (CAR)
    bm_price_by_date = {}
    try:
        bm_hist = get_history("^NSEI", period="5y", interval="1d", as_of=as_of)
        if bm_hist is not None and not bm_hist.empty and "Close" in bm_hist.columns:
            bm_hist = bm_hist.copy()
            bm_hist.index = bm_hist.index.tz_localize(None) if hasattr(bm_hist.index, "tz_localize") and bm_hist.index.tz else bm_hist.index
            for b_idx, b_row in bm_hist.iterrows():
                try:
                    bm_price_by_date[b_idx.strftime("%Y-%m-%d")] = float(b_row["Close"])
                except Exception:
                    continue
    except Exception as e:
        logger.warning("Error fetching benchmark history for causal CAR: %s", e)

    event_analysis: List[Dict[str, Any]] = []
    evidence: List[str] = []
    net_deltas: List[float] = []

    for evt in events:
        event_date_raw = getattr(evt, "event_date", None)
        if not event_date_raw:
            continue
        try:
            if hasattr(event_date_raw, "strftime"):
                e_date_str = event_date_raw.strftime("%Y-%m-%d")
            else:
                e_date_str = str(event_date_raw)[:10]
        except Exception:
            continue

        if e_date_str not in price_by_date:
            # Find nearest trading day
            matching_dates = [d for d in dates_list if d >= e_date_str]
            if not matching_dates:
                continue
            e_date_str = matching_dates[0]

        event_idx = dates_list.index(e_date_str)
        event_type = getattr(evt, "event_type", "general_event")
        title = getattr(evt, "title", "Corporate Filing")

        # Windows: +5 trading days, +20 trading days
        win_5d_ret = None
        win_20d_ret = None

        if event_idx + 5 < len(closes_list):
            p0 = closes_list[event_idx]
            p5 = closes_list[event_idx + 5]
            if p0 > 0:
                win_5d_ret = round(((p5 - p0) / p0) * 100.0, 2)

        if event_idx + 20 < len(closes_list):
            p0 = closes_list[event_idx]
            p20 = closes_list[event_idx + 20]
            if p0 > 0:
                win_20d_ret = round(((p20 - p0) / p0) * 100.0, 2)

        # Cumulative Abnormal Return (CAR) adjusting for authentic point-in-time market benchmark return
        bm_ret_5d = None
        bm_ret_20d = None
        if event_idx + 5 < len(dates_list):
            d0 = dates_list[event_idx]
            d5 = dates_list[event_idx + 5]
            if d0 in bm_price_by_date and d5 in bm_price_by_date and bm_price_by_date[d0] > 0:
                bm_ret_5d = ((bm_price_by_date[d5] - bm_price_by_date[d0]) / bm_price_by_date[d0]) * 100.0

        if event_idx + 20 < len(dates_list):
            d0 = dates_list[event_idx]
            d20 = dates_list[event_idx + 20]
            if d0 in bm_price_by_date and d20 in bm_price_by_date and bm_price_by_date[d0] > 0:
                bm_ret_20d = ((bm_price_by_date[d20] - bm_price_by_date[d0]) / bm_price_by_date[d0]) * 100.0

        car_5d = round(win_5d_ret - bm_ret_5d, 2) if (win_5d_ret is not None and bm_ret_5d is not None) else win_5d_ret
        car_20d = round(win_20d_ret - bm_ret_20d, 2) if (win_20d_ret is not None and bm_ret_20d is not None) else win_20d_ret

        # Causal Impact Classification & Delta Weight based on Abnormal Return
        impact_dir = "NEUTRAL"
        conviction_delta = 0.0

        eval_ret = car_5d if car_5d is not None else win_5d_ret
        if eval_ret is not None:
            if eval_ret >= 5.0:
                impact_dir = "STRONG_POSITIVE"
                conviction_delta = +5.0
            elif eval_ret >= 2.0:
                impact_dir = "MODERATE_POSITIVE"
                conviction_delta = +2.5
            elif eval_ret <= -5.0:
                impact_dir = "STRONG_NEGATIVE"
                conviction_delta = -5.0
            elif eval_ret <= -2.0:
                impact_dir = "MODERATE_NEGATIVE"
                conviction_delta = -2.5

        if conviction_delta != 0.0:
            net_deltas.append(conviction_delta)

        event_analysis.append({
            "event_date": e_date_str,
            "event_type": event_type,
            "title": title,
            "post_5d_return_pct": win_5d_ret,
            "post_20d_return_pct": win_20d_ret,
            "benchmark_5d_return_pct": round(bm_ret_5d, 2) if bm_ret_5d is not None else None,
            "benchmark_20d_return_pct": round(bm_ret_20d, 2) if bm_ret_20d is not None else None,
            "car_5d_pct": car_5d,
            "car_20d_pct": car_20d,
            "causal_impact_direction": impact_dir,
            "conviction_delta": conviction_delta,
        })
        evidence.append(f"Event [{e_date_str} - {event_type}]: 5D CAR {car_5d}% -> Impact: {impact_dir}")

    if not event_analysis:
        return {
            "symbol": norm_symbol,
            "status": "DATA_UNAVAILABLE",
            "executed_at": get_ist_now_str(),
            "event_causal_relationships": [],
            "net_causal_conviction_delta": 0.0,
            "evidence": ["DATA_UNAVAILABLE: No alignable event-price windows found."],
            "key_risks": ["No event alignment."],
            "meta": create_meta_header(source=f"Causal Engine ({norm_symbol})", as_of=as_of_str)
        }

    net_causal_delta = round(float(np.mean(net_deltas)), 1) if net_deltas else 0.0

    return {
        "symbol": norm_symbol,
        "status": "PRODUCTION",
        "executed_at": get_ist_now_str(),
        "total_events_analyzed": len(event_analysis),
        "event_causal_relationships": event_analysis,
        "net_causal_conviction_delta": net_causal_delta,
        "evidence": evidence,
        "meta": create_meta_header(source=f"Causal Engine ({norm_symbol})", as_of=as_of_str)
    }
