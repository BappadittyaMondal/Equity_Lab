"""Automated Swing Trade Alert Feed Service — Gap Closure Feature 3.

Scans candidates using B4 (VPA), B6 (RS Rating), B7 (Pocket Pivot), and D17 (Weinstein Stage)
to identify active high-probability short-to-medium term swing trade setups.
"""

import logging
from typing import List, Optional
from datetime import datetime, timezone

from app.models.schemas import (
    SwingTradeAlertItem,
    SwingTradeAlertsResponse,
)
from app.services.strategies.technical_engines import (
    run_vpa_b4,
    run_rs_rating_b6,
    run_pocket_pivot_b7,
    run_mean_reversion_d17,
)
from app.services.market_data import normalize_symbol, get_quote, create_meta_header, get_history
from app.services.research.market_regime import classify_market_regime

logger = logging.getLogger(__name__)

# Default active universe for swing scanning if no list provided
_DEFAULT_SWING_UNIVERSE = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "BHARTIARTL", "LT", "HINDUNILVR", "ITC", "SBIN",
    "NETWEB", "E2E", "MACPOWER", "HBLPOWER", "APOLLO"
]


def get_swing_trade_alerts(symbols: Optional[List[str]] = None) -> SwingTradeAlertsResponse:
    """Scan universe for high-probability swing trade setups with macro regime gating (§99)."""
    target_symbols = symbols if symbols else _DEFAULT_SWING_UNIVERSE
    alerts: List[SwingTradeAlertItem] = []
    now_iso = datetime.now(timezone.utc).isoformat()

    # 0. Evaluate Macro Market Regime (§Phase 99 CRO Fiduciary Gating)
    macro_regime = "DATA_UNAVAILABLE"
    is_macro_regime_favorable = True
    try:
        regime_res = classify_market_regime("^NSEI")
        if regime_res:
            macro_regime = regime_res.regime_code
            if regime_res.regime_code in ("R4_BEAR_TREND", "R5_PANIC_STRESS"):
                is_macro_regime_favorable = False
            elif regime_res.regime_code in ("R1_BULL_TREND", "R2_BULL_VOLATILE", "R6_RECOVERY_TRANSITION"):
                is_macro_regime_favorable = True
    except Exception as reg_err:
        logger.debug("Market regime check bypassed for swing scanner: %s", reg_err)

    for s in target_symbols:
        norm = normalize_symbol(s)
        try:
            # 0. Binary Event Risk Hard Gate (§Phase 107 DEF-017 Day-0 Earnings Binary Gap Risk Gate)
            try:
                from app.services.strategies.short_term_prediction_engine import ShortTermPredictionEngine
                event_risk = ShortTermPredictionEngine.check_event_proximity(norm)
                if event_risk and event_risk.get("imminent_events"):
                    # Hard-block if earnings announcement is today (Day 0)
                    day_zero_events = [
                        ev for ev in event_risk["imminent_events"]
                        if ev.get("days_ahead") == 0 or ev.get("calendar_days_diff") == 0
                    ]
                    if day_zero_events:
                        logger.info("Swing alert suppressed for %s: Day-0 earnings announcement gap risk (EARNINGS_DAY_ZERO_BLOCKED).", norm)
                        continue
            except Exception as ev_err:
                logger.debug("Event proximity check bypassed for swing alert %s: %s", norm, ev_err)

            # 1. Run technical engines
            vpa = run_vpa_b4(norm)
            rs = run_rs_rating_b6(norm)
            pp = run_pocket_pivot_b7(norm)
            d17 = run_mean_reversion_d17(norm)

            rs_rating = int(rs.metrics.get("rs_rating_0_99", 50))
            stage = d17.metrics.get("weinstein_stage", "STAGE_1_BASING")
            pocket_count = int(pp.metrics.get("pocket_pivot_count", 0))
            vpa_score = float(vpa.metrics.get("vpa_score", 50.0))
            acc_sig = str(vpa.results.get("accumulation_signal", "NONE"))

            quote = get_quote(norm)
            price = float(getattr(quote, "price", 100.0) or 100.0)
            if price <= 0:
                price = 100.0

            alert_type: Optional[str] = None
            setup_score = 50.0

            # Condition 1: Stage 2 Pocket Pivot
            if stage == "STAGE_2_ADVANCING" and pocket_count >= 1:
                alert_type = "STAGE_2_POCKET_PIVOT"
                setup_score = 85.0 + min(10.0, pocket_count * 5.0)

            # Condition 2: VPA Accumulation Breakout
            elif vpa_score >= 65.0 and acc_sig in ("STRONG", "MODERATE") and rs_rating >= 70:
                alert_type = "VPA_ACCUMULATION_BREAKOUT"
                setup_score = min(95.0, vpa_score + 10.0)

            # Condition 3: RS Leader Pullback
            elif rs_rating >= 75 and stage in ("STAGE_1_BASING", "STAGE_2_ADVANCING"):
                alert_type = "RS_LEADER_PULLBACK"
                setup_score = 75.0 + (rs_rating - 75) * 0.8

            if alert_type:
                # Calculate key price levels dynamically based on 14-day ATR volatility
                atr_14: Optional[float] = None
                try:
                    df_hist = get_history(norm, period="3mo", interval="1d")
                    if df_hist is not None and not df_hist.empty and len(df_hist) >= 5:
                        from app.services.strategies.swing_predictive_engine import SwingPredictiveEngine
                        calc_atr = float(SwingPredictiveEngine.calculate_atr(df_hist, period=14))
                        if calc_atr > 0 and not (calc_atr != calc_atr):
                            atr_14 = round(calc_atr, 2)
                except Exception as atr_err:
                    logger.debug("Failed calculating ATR for swing alert %s: %s", norm, atr_err)

                if atr_14 is not None and atr_14 > 0:
                    stop_loss = round(max(0.05, price - 2.0 * atr_14), 2)
                    target = round(price + 4.0 * atr_14, 2)
                    stop_loss_distance_pct = round(((price - stop_loss) / price) * 100.0, 2)
                else:
                    # Conservative fallback when historical bars are unavailable
                    stop_loss = round(price * 0.94, 2)     # -6% risk control
                    target = round(price * 1.18, 2)        # +18% reward target
                    stop_loss_distance_pct = 6.0

                risk_amount = max(0.01, price - stop_loss)
                reward_amount = max(0.01, target - price)
                risk_reward_ratio = round(reward_amount / risk_amount, 2)
                if risk_reward_ratio < 1.50:
                    continue  # Fiduciary floor: discard setups with sub-optimal reward-to-risk (< 1.5:1)
                entry_range = f"₹{round(price * 0.99, 2)} - ₹{round(price * 1.01, 2)}"

                # Empirical calibration & Conformal prediction interval
                try:
                    from app.services.research.technical_probability import calculate_calibrated_probability_ladder
                    from app.services.ml.conformal_prediction import ConformalPredictor
                    ladder = calculate_calibrated_probability_ladder(
                        symbol=norm,
                        tss_score=setup_score,
                        setup_class="SETUP_A_BREAKOUT" if alert_type == "STAGE_2_POCKET_PIVOT" else "SETUP_D_BASE_BREAKOUT"
                    )
                    cp = ConformalPredictor()
                    conf_int = cp.predict_interval(point_estimate=ladder.event_t2_prob_10pct_20d, strata="TECHNICAL_SWING")
                    edge_str = f"P(+10% 20D)={int(ladder.event_t2_prob_10pct_20d * 100)}% [90% CI: {int(conf_int.lower_bound_90 * 100)}%-{int(conf_int.upper_bound_90 * 100)}%]"
                except Exception:
                    edge_str = "P(+10% 20D)=UNAVAILABLE [90% CI: N/A]"

                adjusted_score = max(50.0, round(setup_score * 0.85, 1)) if not is_macro_regime_favorable else round(setup_score, 1)

                alerts.append(SwingTradeAlertItem(
                    symbol=norm,
                    company_name=norm,
                    swing_setup_score=adjusted_score,
                    weinstein_stage=stage,
                    rs_rating=rs_rating,
                    volume_signal=f"VPA: {acc_sig} | Pivots: {pocket_count} | {edge_str}",
                    entry_zone=entry_range,
                    stop_loss_level=stop_loss,
                    target_price=target,
                    alert_type=alert_type,
                    triggered_at=now_iso,
                    atr_14=atr_14,
                    risk_reward_ratio=risk_reward_ratio,
                    stop_loss_distance_pct=stop_loss_distance_pct,
                    market_regime=macro_regime,
                    market_regime_favorable=is_macro_regime_favorable,
                ))

        except Exception as e:
            logger.warning("Swing alert scan failed for %s: %s", norm, e)

    # Sort alerts by setup score descending
    alerts.sort(key=lambda a: a.swing_setup_score, reverse=True)

    return SwingTradeAlertsResponse(
        alerts=alerts,
        count=len(alerts),
        scanned_universe=f"NSE Top Universe ({len(target_symbols)} symbols)",
        market_regime=macro_regime,
        market_regime_favorable=is_macro_regime_favorable,
        meta=create_meta_header(source="IERL Swing Trade Alert Scanner"),
    )
