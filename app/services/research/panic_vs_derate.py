"""Phase 179: Panic vs. Structural De-Rating Classifier.

Distinguishes two superficially similar price-drop scenarios that require
opposite investment decisions:

  PANIC_DISLOCATION_OPPORTUNITY:
    Fundamentals intact + RSI oversold + sharp recent price drop.
    Smart money exits temporarily; business quality unchanged.
    → Potential entry opportunity for patient capital.

  STRUCTURAL_DE_RATING_AVOID:
    Fundamentals deteriorating (ROCE declining QoQ, margin compression) +
    P/E contraction signaling earnings downgrade cycle.
    → Not a dip — a re-pricing of lower quality. Avoid or exit.

  AMBIGUOUS_AWAIT_NEXT_QUARTER:
    Mixed signals or insufficient data. No actionable conviction.
    → Wait for next quarterly result to confirm direction.

This is a 3-signal heuristic composite — NOT a probabilistic model.
All outputs include methodology_note disclosing the rule-based nature.
"""

from typing import Dict, Any, Optional


# ── Thresholds (all tunable at Phase level, not magic numbers) ────────────
_RSI_OVERSOLD = 40.0          # RSI ≤ 40 = technically oversold
_PRICE_DROP_3M_PCT = 15.0     # ≥ 15% 3-month drop = meaningful dislocation
_ROCE_DECLINE_THRESHOLD = 3.0  # ≥ 3 pp QoQ ROCE decline = deteriorating
_PE_CONTRACTION_THRESHOLD = 0.85  # P/E now ≤ 85% of 1Y avg = P/E contracted


def classify_panic_vs_derate(item: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 179: Classify a price drop as panic dislocation or structural de-rating.

    Args:
        item: Company profile dict. Relevant keys:
            rsi_14 (float): Current 14-day RSI
            price_drop_3m_pct (float): 3-month price decline % (positive = drop)
            roce_latest (float): Current trailing ROCE %
            roce_3yr (float): 3-year average ROCE % (proxy for prior period)
            roce_qoq_change (float): QoQ ROCE change in pp (negative = declining)
            pe_ratio (float): Current trailing P/E
            pe_1yr_avg (float): 1-year average trailing P/E
            opm_latest (float): Current OPM %
            opm_5yr (float): 5-year median OPM %
            pat_growth_latest (float): Latest PAT growth YoY %

    Returns:
        Dict with keys:
            verdict: PANIC_DISLOCATION_OPPORTUNITY | STRUCTURAL_DE_RATING_AVOID | AMBIGUOUS_AWAIT_NEXT_QUARTER
            panic_signals: list of observed panic indicators
            derate_signals: list of observed de-rating indicators
            panic_signal_count: int
            derate_signal_count: int
            confidence: LOW | MEDIUM | HIGH
            methodology_note: str (always present — heuristic disclosure)
            actionable_note: str
    """
    panic_signals = []
    derate_signals = []

    # ── Signal 1: Technical oversold ─────────────────────────────────────
    rsi = item.get("rsi_14")
    if rsi is not None:
        try:
            rsi_f = float(rsi)
            if rsi_f <= _RSI_OVERSOLD:
                panic_signals.append(
                    f"RSI={rsi_f:.1f} ≤ {_RSI_OVERSOLD} (technically oversold — selling exhaustion zone)"
                )
            elif rsi_f >= 60.0:
                derate_signals.append(
                    f"RSI={rsi_f:.1f} ≥ 60 (no oversold condition — price drop may be measured selling, not panic)"
                )
        except (ValueError, TypeError):
            pass

    # ── Signal 2: Sharp recent price drop ────────────────────────────────
    drop_3m = item.get("price_drop_3m_pct")
    if drop_3m is not None:
        try:
            drop_f = float(drop_3m)
            if drop_f >= _PRICE_DROP_3M_PCT:
                panic_signals.append(
                    f"Price drop {drop_f:.1f}% in 3M ≥ {_PRICE_DROP_3M_PCT}% threshold (sharp dislocation)"
                )
            elif 5.0 <= drop_f < _PRICE_DROP_3M_PCT:
                pass  # Mild drop — not a panic signal
            elif drop_f < 0:
                derate_signals.append(
                    f"Price actually UP {abs(drop_f):.1f}% in 3M — no dislocation to buy"
                )
        except (ValueError, TypeError):
            pass

    # ── Signal 3: Fundamentals intact (ROCE, OPM) ────────────────────────
    roce_latest = item.get("roce_latest")
    roce_qoq = item.get("roce_qoq_change")
    opm_latest = item.get("opm_latest")
    opm_5yr = item.get("opm_5yr")

    if roce_latest is not None:
        try:
            roce_f = float(roce_latest)
            if roce_f >= 15.0:
                panic_signals.append(
                    f"ROCE={roce_f:.1f}% ≥ 15% (capital efficiency intact — no fundamental deterioration)"
                )
            elif roce_f < 10.0:
                derate_signals.append(
                    f"ROCE={roce_f:.1f}% < 10% (below cost of capital — structural quality issue)"
                )
        except (ValueError, TypeError):
            pass

    if roce_qoq is not None:
        try:
            rqoq_f = float(roce_qoq)
            if rqoq_f <= -_ROCE_DECLINE_THRESHOLD:
                derate_signals.append(
                    f"ROCE declined {abs(rqoq_f):.1f} pp QoQ ≥ {_ROCE_DECLINE_THRESHOLD} pp threshold "
                    f"(operating deterioration — earnings downgrade risk)"
                )
            elif rqoq_f >= 2.0:
                panic_signals.append(
                    f"ROCE improved +{rqoq_f:.1f} pp QoQ (fundamentals strengthening despite price drop)"
                )
        except (ValueError, TypeError):
            pass

    if opm_latest is not None and opm_5yr is not None:
        try:
            opm_l = float(opm_latest)
            opm_5 = float(opm_5yr)
            if opm_l < opm_5 - 3.0:
                derate_signals.append(
                    f"OPM={opm_l:.1f}% vs 5Y median {opm_5:.1f}% — margin compression (structural, not transient)"
                )
            elif opm_l >= opm_5:
                panic_signals.append(
                    f"OPM={opm_l:.1f}% ≥ 5Y median {opm_5:.1f}% — operating leverage intact"
                )
        except (ValueError, TypeError):
            pass

    # ── Signal 4: P/E contraction (de-rating indicator) ──────────────────
    pe_now = item.get("pe_ratio") or item.get("current_pe")
    pe_1yr = item.get("pe_1yr_avg")
    if pe_now is not None and pe_1yr is not None:
        try:
            pe_n = float(pe_now)
            pe_y = float(pe_1yr)
            if pe_y > 0:
                pe_ratio_to_avg = pe_n / pe_y
                if pe_ratio_to_avg <= _PE_CONTRACTION_THRESHOLD:
                    derate_signals.append(
                        f"P/E={pe_n:.1f}x vs 1Y avg {pe_y:.1f}x "
                        f"(contracted to {pe_ratio_to_avg:.0%} of average — market pricing in lower earnings)"
                    )
                elif pe_ratio_to_avg >= 1.10 and float(item.get("price_drop_3m_pct", 0)) >= _PRICE_DROP_3M_PCT:
                    panic_signals.append(
                        f"P/E={pe_n:.1f}x still at/above 1Y avg despite {item.get('price_drop_3m_pct', 0):.1f}% drop "
                        f"(market hasn't de-rated — price drop is panic, not earnings revision)"
                    )
        except (ValueError, TypeError):
            pass

    # ── Signal 5: PAT growth trajectory ──────────────────────────────────
    pat_growth = item.get("pat_growth_latest")
    if pat_growth is not None:
        try:
            pat_f = float(pat_growth)
            if pat_f >= 15.0:
                panic_signals.append(
                    f"PAT growth={pat_f:.1f}% YoY — earnings growing despite price drop (classic panic setup)"
                )
            elif pat_f <= -10.0:
                derate_signals.append(
                    f"PAT growth={pat_f:.1f}% YoY (earnings declining — de-rating is earnings-justified)"
                )
        except (ValueError, TypeError):
            pass

    # ── Verdict logic ─────────────────────────────────────────────────────
    p = len(panic_signals)
    d = len(derate_signals)
    total = p + d

    if total == 0:
        verdict = "AMBIGUOUS_AWAIT_NEXT_QUARTER"
        confidence = "LOW"
    elif p >= 3 and d == 0:
        verdict = "PANIC_DISLOCATION_OPPORTUNITY"
        confidence = "HIGH"
    elif p >= 2 and d <= 1:
        verdict = "PANIC_DISLOCATION_OPPORTUNITY"
        confidence = "MEDIUM"
    elif d >= 3 and p == 0:
        verdict = "STRUCTURAL_DE_RATING_AVOID"
        confidence = "HIGH"
    elif d >= 2 and p <= 1:
        verdict = "STRUCTURAL_DE_RATING_AVOID"
        confidence = "MEDIUM"
    else:
        verdict = "AMBIGUOUS_AWAIT_NEXT_QUARTER"
        confidence = "LOW" if total <= 2 else "MEDIUM"

    # ── Actionable note ───────────────────────────────────────────────────
    if verdict == "PANIC_DISLOCATION_OPPORTUNITY":
        actionable = (
            "Fundamentals are intact and price drop appears sentiment-driven. "
            "Consider staged entry if thesis is confirmed by next quarter result. "
            "Set a hard stop at 20% below current price."
        )
    elif verdict == "STRUCTURAL_DE_RATING_AVOID":
        actionable = (
            "Price drop is being driven by deteriorating fundamentals — this is not a dip, "
            "it is a re-pricing of lower quality. Avoid new positions. "
            "Existing holders: exit on bounces, do not average down."
        )
    else:
        actionable = (
            "Signals are mixed. Await next quarterly result for clarification. "
            "Do not commit capital until one direction is confirmed."
        )

    return {
        "verdict": verdict,
        "panic_signal_count": p,
        "derate_signal_count": d,
        "panic_signals": panic_signals,
        "derate_signals": derate_signals,
        "confidence": confidence,
        "actionable_note": actionable,
        "methodology_note": (
            "Phase 179 Panic-vs-Derate Classifier. Rule-based 5-signal heuristic composite. "
            "Signals: RSI oversold, 3M price drop ≥15%, ROCE/OPM stability, P/E contraction, "
            "PAT growth trajectory. NOT a probabilistic model. Verdict is a directional guide "
            "requiring confirmation from next quarterly filing. "
            "Thresholds: RSI≤40, drop≥15%, ROCE_QoQ≤-3pp, P/E≤85% of 1Y avg."
        ),
    }
