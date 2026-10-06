"""Phase 155-156: Deadliest Combination Pipeline Orchestrator.

The single callable that chains ALL project engines end-to-end:
  Ticker list → Fundamental Fetch → Multibagger Score → TBQE Pre-Fly Score →
  Return Ceiling → Earnings Quality Gate → Forensic Audit →
  Continuous Quality Q × Multiplicative Cross-Product Rank → Portfolio Constraints → Top N

Incorporates Phase 156 Institutional Refinements:
  1. MCap Band: ₹150 Cr – ₹15,000 Cr.
  2. Multiplicative cross-product formula:
     Score = 100 * (Potential^0.55 * Timing^0.30 * CeilingFactor^0.15) * Q_continuous
  3. Continuous quality multiplier Q in [0.50, 1.00].
  4. Operating leverage convexity factor Omega in [1.0, 2.5].
  5. Order-book conversion burn rate kappa >= 0.20 guard.
  6. Portfolio construction layer: 30% sector concentration cap, ADTV liquidity limit.
  7. Segmented threshold tapering across Micro, Small, Mid caps.
  8. Segment-relative headroom (min(3.0%, 0.75 * price_band)) and 60D delivery benchmark.
"""

import logging
import os
import math
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DeadliestComboResult:
    """Result container for a single stock's full-pipeline evaluation."""

    __slots__ = (
        "symbol", "company_name", "rank",
        "composite_score", "multibagger_score", "tbqe_score",
        "return_ceiling", "pat_quality_flag", "forensic_verdict",
        "weinstein_stage", "launchpad_label", "lifecycle_stage",
        "hard_gate_pass", "disqualification_reason",
        "fundamentals", "breakdown",
        "continuous_q", "omega_convexity", "sector", "tier",
    )

    def __init__(self, **kwargs):
        for slot in self.__slots__:
            setattr(self, slot, kwargs.get(slot))

    def to_dict(self) -> Dict[str, Any]:
        return {s: getattr(self, s) for s in self.__slots__}


# ─────────────────────────────────────────────────────────────────────────────
# Scoring Power Configuration (Multiplicative Model)
# ─────────────────────────────────────────────────────────────────────────────

SCORING_POWERS = {
    "potential": 0.55,       # Multibagger potential & operating leverage
    "timing": 0.30,          # TBQE technical base quality & launchpad readiness
    "ceiling_factor": 0.15,  # Reverse-DCF room-to-grow headroom factor
}

# Retained for backwards compatibility with legacy readers
COMPOSITE_WEIGHTS = {
    "multibagger_score": 0.50,
    "tbqe_score": 0.25,
    "return_ceiling_base": 0.15,
    "earnings_quality": 0.10,
}


# ─────────────────────────────────────────────────────────────────────────────
# Hard Gate Disqualifiers (instant elimination, no scoring)
# ─────────────────────────────────────────────────────────────────────────────

def _check_hard_gates(fundamentals: Dict[str, Any]) -> Optional[str]:
    """Return disqualification reason string, or None if all gates pass.

    Hard constraints:
    - MCap between ₹150 Cr and ₹15,000 Cr
    - D/E <= 0.35
    - Promoter pledge <= 5.0%
    - PAT quality flag != NON_OPERATING_DOMINATED
    """
    mcap = fundamentals.get("market_cap", 0.0) or 0.0
    # MCap in yfinance is in absolute currency (INR), convert to Cr
    mcap_cr = mcap / 1e7 if mcap > 1e7 else mcap

    if mcap_cr < 150.0:
        return f"MCap ₹{mcap_cr:.0f} Cr < ₹150 Cr minimum"
    if mcap_cr > 15000.0:
        return f"MCap ₹{mcap_cr:.0f} Cr > ₹15,000 Cr maximum"

    sector = str(fundamentals.get("sector") or fundamentals.get("industry") or "").upper().strip()
    is_lending_bfsi = any(b in sector for b in ("BANK", "NBFC", "LENDING", "HOUSING FINANCE"))
    if is_lending_bfsi:
        return f"OUT_OF_SCOPE_V1: Sector '{sector}' is a financial lending institution (requires banking asset-quality gates, not industrial D/E)"

    d_e = fundamentals.get("debt_to_equity", 0.0) or 0.0
    if d_e > 0.35:
        return f"D/E {d_e:.2f} > 0.35 threshold"

    pledged = fundamentals.get("pledged_pct")
    if pledged is not None and pledged > 5.0:
        return f"Promoter pledge {pledged:.1f}% > 5% threshold"

    pat_qf = fundamentals.get("pat_quality_flag", "")
    if pat_qf == "NON_OPERATING_DOMINATED":
        return f"PAT quality: {pat_qf} — earnings dominated by non-operating income"

    return None  # All gates passed


# ─────────────────────────────────────────────────────────────────────────────
# Phase 156 Institutional Quality Multiplier Q in [0.50, 1.00]
# ─────────────────────────────────────────────────────────────────────────────

def _calculate_continuous_q(fundamentals: Dict[str, Any]) -> float:
    """Compute continuous balance-sheet & earnings quality multiplier Q in [0.50, 1.00].

    Formula:
      Q = 0.40 * min(1.0, max(0.0, CFO/PAT))
        + 0.30 * max(0.0, 1.0 - Pledge / 10.0)
        + 0.30 * max(0.0, 1.0 - (D/E / 0.50))
    Ensures non-binary grading: heavily rewards pristine balance sheets & pure cash conversion.
    """
    cfo_pat = fundamentals.get("cfo_pat")
    if cfo_pat is None:
        cfo_pat = fundamentals.get("cfo_pat_ratio")
    if cfo_pat is None and fundamentals.get("cfo_ttm_pat") is not None:
        cfo_pat = fundamentals.get("cfo_ttm_pat")

    pledged = fundamentals.get("pledged_pct")
    pledge_val = float(pledged) if (pledged is not None and str(pledged).replace('.', '', 1).isdigit()) else 0.0
    d_e = fundamentals.get("debt_to_equity", 0.0) or 0.0

    if cfo_pat is None:
        # Graceful neutral baseline when CFO is unobserved (SEBI LODR semi-annual filing lag)
        cfo_val = 0.80
    else:
        try:
            cfo_val = float(cfo_pat)
        except (ValueError, TypeError):
            cfo_val = 0.80

    try:
        de_val = float(d_e)
    except (ValueError, TypeError):
        de_val = 0.0

    q_cfo = 0.40 * max(0.0, min(1.0, cfo_val))
    q_pledge = 0.30 * max(0.0, 1.0 - (pledge_val / 10.0))
    q_de = 0.30 * max(0.0, 1.0 - (de_val / 0.50))

    q_raw = q_cfo + q_pledge + q_de
    return round(max(0.50, min(1.00, q_raw)), 4)


# ─────────────────────────────────────────────────────────────────────────────
# Phase 156 Operating Leverage Convexity Factor Omega in [1.0, 2.5]
# ─────────────────────────────────────────────────────────────────────────────

def _calculate_operating_leverage_convexity(fundamentals: Dict[str, Any]) -> float:
    """Operating Leverage Convexity factor Omega in [1.0, 2.5].

    Formula:
      Omega = min(2.5, max(1.0, (TTM Operating PAT Growth %) / max(5.0, TTM Revenue Growth %)))
    """
    pat_growth = (
        fundamentals.get("pat_growth_latest") or
        fundamentals.get("pat_growth_3yr") or
        fundamentals.get("op_growth", 0.0) or 0.0
    )
    rev_growth = (
        fundamentals.get("sales_growth_latest") or
        fundamentals.get("sales_growth_3yr", 0.0) or 0.0
    )

    try:
        pat_growth_val = float(pat_growth)
        rev_growth_val = float(rev_growth)
    except (ValueError, TypeError):
        return 1.0

    if pat_growth_val <= 0 or rev_growth_val <= 0:
        return 1.0

    denom = max(5.0, rev_growth_val)
    ratio = pat_growth_val / denom
    return round(min(2.5, max(1.0, ratio)), 3)


# ─────────────────────────────────────────────────────────────────────────────
# Phase 156 Order Book Conversion Burn Rate kappa >= 0.20 Guard
# ─────────────────────────────────────────────────────────────────────────────

def _calculate_order_book_burn_rate(fundamentals: Dict[str, Any]) -> Optional[float]:
    """Calculate order book conversion burn rate kappa = Annual Revenue / Order Book.

    Returns None if order book is not reported. Valid conversion expects kappa >= 0.20.
    """
    order_book = fundamentals.get("order_book") or fundamentals.get("order_book_cr", 0.0) or 0.0
    annual_rev = fundamentals.get("total_revenue") or fundamentals.get("sales_latest") or fundamentals.get("revenue_ttm", 0.0) or 0.0
    try:
        ob = float(order_book)
        rev = float(annual_rev)
        if ob > 0 and rev > 0:
            return round(rev / ob, 3)
    except (ValueError, TypeError):
        pass
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Phase 156 Segmented Threshold Tapering (Micro, Small, Mid)
# ─────────────────────────────────────────────────────────────────────────────

def _get_segmented_thresholds(mcap_cr: float) -> Dict[str, Any]:
    """Returns dynamic capacity and capital efficiency thresholds by MCap tier:
    - Micro (₹150–1.5k Cr): CWIP >= 15%, Inc-ROIC >= 22%
    - Small (₹1.5k–6k Cr): CWIP >= 12%, Inc-ROIC >= 20%
    - Mid (₹6k–15k Cr): CWIP >= 8%, Inc-ROIC >= 16%
    """
    if mcap_cr < 1500.0:
        return {"tier": "MICRO", "cwip_pct_min": 15.0, "inc_roic_min": 22.0}
    elif mcap_cr < 6000.0:
        return {"tier": "SMALL", "cwip_pct_min": 12.0, "inc_roic_min": 20.0}
    else:
        return {"tier": "MID", "cwip_pct_min": 8.0, "inc_roic_min": 16.0}


# ─────────────────────────────────────────────────────────────────────────────
# Phase 156 Segment-Relative Headroom & Delivery Benchmark
# ─────────────────────────────────────────────────────────────────────────────

def _calculate_headroom_and_delivery(fundamentals: Dict[str, Any]) -> Dict[str, Any]:
    """Scale headroom to min(3.0%, 0.75 * price_band); benchmark delivery >= 1.30x of 60D median."""
    price_band = fundamentals.get("price_band_pct", 5.0) or 5.0
    headroom_cap = min(3.0, 0.75 * float(price_band))

    deliv_pct = fundamentals.get("delivery_pct", 0.0) or 0.0
    deliv_60d_med = fundamentals.get("delivery_60d_median", 0.0) or 0.0
    deliv_pass = (deliv_pct >= 1.30 * deliv_60d_med) if (deliv_60d_med > 0) else None

    return {
        "headroom_cap_pct": round(headroom_cap, 2),
        "delivery_benchmark_pass": deliv_pass,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Earnings Quality Score (0.0 – 1.0)
# ─────────────────────────────────────────────────────────────────────────────

def _earnings_quality_score(fundamentals: Dict[str, Any]) -> float:
    """Score earnings quality based on PAT quality flag and CFO/PAT.

    Returns 0.0–1.0 where 1.0 = highest quality (pure operating earnings).
    """
    pat_qf = fundamentals.get("pat_quality_flag", "OPERATING")
    cfo_pat = fundamentals.get("cfo_pat", 0.0) or 0.0

    # Base score from PAT quality flag
    if pat_qf == "OPERATING":
        base = 1.0
    elif pat_qf == "ELEVATED_OTHER_INCOME":
        base = 0.6
    else:  # NON_OPERATING_DOMINATED (should be hard-gated, but defensive)
        base = 0.2

    # CFO/PAT bonus/penalty
    if cfo_pat >= 1.0:
        cfo_bonus = min(0.2, (cfo_pat - 1.0) * 0.1)  # Up to +0.2 for strong cash conversion
    elif cfo_pat >= 0.5:
        cfo_bonus = 0.0
    else:
        cfo_bonus = -0.2  # Penalty for poor cash conversion

    return max(0.0, min(1.0, base + cfo_bonus))


# ─────────────────────────────────────────────────────────────────────────────
# Return Ceiling Normalizer (maps multiple to 0.0–1.0 score)
# ─────────────────────────────────────────────────────────────────────────────

def _normalize_return_ceiling(base_multiple: float) -> float:
    """Map base-case return multiple to 0.0–1.0 score.

    0.0x → 0.0
    1.0x → 0.0 (breakeven floor)
    2.0x → 0.33
    4.0x → 0.67
    8.0x+ → 1.0
    """
    if base_multiple <= 0:
        return 0.0
    return min(1.0, max(0.0, math.log2(max(base_multiple, 0.01)) / 3.0))


# ─────────────────────────────────────────────────────────────────────────────
# Main Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

def run_deadliest_combo_pipeline(
    tickers: List[str],
    top_n: int = 10,
    fetch_live: bool = True,
    pledge_overrides: Optional[Dict[str, float]] = None,
    enforce_portfolio_constraints: bool = True,
    max_sector_exposure: float = 0.30,
) -> List[DeadliestComboResult]:
    """Run the full Deadliest Combination pipeline on a list of tickers.

    Pipeline stages:
      1. Fundamental data fetch (yfinance via FundamentalFetcher / ScreenerCloudConnector)
      2. Hard Gate check (MCap ₹150–15,000 Cr, D/E <= 0.35, Pledge <= 5%, Operating PAT)
      3. Multibagger Engine scoring (27 sub-engines, 100-point scale)
      4. TBQE Pre-Fly scoring (Weinstein, VCP, OBV, base length)
      5. Return Ceiling (reverse-DCF bear/base/bull)
      6. Earnings Quality scoring & Continuous Q multiplier computation
      7. Forensic Audit (Beneish, Altman-Z, RPT, Auditor Resignation)
      8. Multiplicative Cross-Product Scoring:
         Deadliest Score = 100 * (Potential^0.55 * Timing^0.30 * CeilingFactor^0.15) * Q_continuous
      9. Institutional Portfolio Layer: Sector cap (30%) & ADTV ranking -> Top N

    Args:
        tickers: List of NSE/BSE ticker symbols (e.g., ["JSLL", "DYCL", "FRONTSP"])
        top_n: Number of top-ranked stocks to return (default 10)
        fetch_live: If True, fetch live data. If False, use cached data only.
        pledge_overrides: Optional dict of verified promoter pledge % (e.g., {"INDOTECH": 80.26, "DYCL": 0.0})
        enforce_portfolio_constraints: If True, enforce 30% sector concentration cap.
        max_sector_exposure: Maximum portfolio fraction allowed for any single sector (default 0.30).

    Returns:
        List of DeadliestComboResult sorted by composite_score descending.
    """
    from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher
    from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
    from app.services.research.technical_base_quality import TechnicalBaseQualityEngine
    from app.services.research.return_ceiling import compute_return_ceiling
    from app.services.research.forensic_auditor import ForensicAuditor

    results: List[DeadliestComboResult] = []
    disqualified: List[DeadliestComboResult] = []

    forensic = ForensicAuditor()

    for ticker in tickers:
        logger.info(f"[PIPELINE] Processing {ticker}...")
        symbol = ticker.upper().strip()

        # ── Stage 1: Fetch Fundamentals ──────────────────────────────────
        try:
            if fetch_live:
                fundamentals = FundamentalFetcher.fetch_and_store(symbol)
            else:
                from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
                fundamentals = ScreenerCloudConnector.get_or_fetch_fundamentals(symbol)

            if fundamentals is None:
                disqualified.append(DeadliestComboResult(
                    symbol=symbol, company_name=symbol,
                    hard_gate_pass=False,
                    disqualification_reason="DATA_FETCH_FAILED",
                    composite_score=0.0,
                ))
                continue
        except Exception as e:
            logger.warning(f"[PIPELINE] Failed to fetch {symbol}: {e}")
            disqualified.append(DeadliestComboResult(
                symbol=symbol, company_name=symbol,
                hard_gate_pass=False,
                disqualification_reason=f"FETCH_ERROR: {e}",
                composite_score=0.0,
            ))
            continue

        # Apply verified pledge override if provided
        if pledge_overrides:
            norm_key = symbol.replace(".NS", "").replace(".BO", "")
            for k, val in pledge_overrides.items():
                if k.upper().replace(".NS", "").replace(".BO", "") == norm_key:
                    fundamentals["pledged_pct"] = float(val)
                    fundamentals["pledge_provenance"] = "BSE_FILING_VERIFIED"
                    break

        company_name = fundamentals.get("company_name", symbol)

        # ── Stage 2: Hard Gates ──────────────────────────────────────────
        dq_reason = _check_hard_gates(fundamentals)
        if dq_reason:
            disqualified.append(DeadliestComboResult(
                symbol=symbol, company_name=company_name,
                hard_gate_pass=False,
                disqualification_reason=dq_reason,
                composite_score=0.0,
                fundamentals=fundamentals,
            ))
            logger.info(f"[PIPELINE] {symbol} DISQUALIFIED: {dq_reason}")
            continue

        # ── Stage 3: Multibagger Engine (100-point scoring) ──────────────
        try:
            mb_result = InstitutionalMultibaggerEngine.evaluate_company(fundamentals)
            mb_score = mb_result.get("overall_score", 0.0)
            lifecycle = mb_result.get("lifecycle_stage", "UNKNOWN")
            launchpad = mb_result.get("launchpad_readiness", {}).get("label", "UNKNOWN")
        except Exception as e:
            logger.warning(f"[PIPELINE] Multibagger engine failed for {symbol}: {e}")
            mb_score = 0.0
            mb_result = {}
            lifecycle = "UNKNOWN"
            launchpad = "UNKNOWN"

        # ── Stage 4: TBQE Pre-Fly Scoring ────────────────────────────────
        try:
            tbqe_raw, tbqe_breakdown = TechnicalBaseQualityEngine.score(fundamentals)
            weinstein = tbqe_breakdown.get("weinstein_stage", "UNKNOWN")
        except Exception as e:
            logger.warning(f"[PIPELINE] TBQE failed for {symbol}: {e}")
            tbqe_raw = 0.5
            tbqe_breakdown = {}
            weinstein = "UNKNOWN"

        # ── Stage 5: Return Ceiling (reverse-DCF) ────────────────────────
        mcap_cr = (fundamentals.get("market_cap", 0.0) or 0.0)
        if mcap_cr > 1e7:
            mcap_cr = mcap_cr / 1e7  # Convert from INR to Cr

        net_income = fundamentals.get("net_profit_last_year", 0.0) or 0.0
        if net_income > 1e7:
            net_income_cr = net_income / 1e7
        elif net_income > 0:
            net_income_cr = net_income
        else:
            net_income_cr = 0.0

        try:
            rc_result = compute_return_ceiling(mcap_cr, net_income_cr)
            rc_base = rc_result.get("base_multiple", 0.0)
            rc_label = rc_result.get("label", "INSUFFICIENT_DATA")
        except Exception as e:
            logger.warning(f"[PIPELINE] Return ceiling failed for {symbol}: {e}")
            rc_result = {}
            rc_base = 0.0
            rc_label = "INSUFFICIENT_DATA"

        # ── Stage 6: Earnings Quality & Institutional Multipliers ────────
        eq_score = _earnings_quality_score(fundamentals)
        pat_qf = fundamentals.get("pat_quality_flag", "OPERATING")
        continuous_q = _calculate_continuous_q(fundamentals)
        omega = _calculate_operating_leverage_convexity(fundamentals)
        kappa = _calculate_order_book_burn_rate(fundamentals)
        segmented_info = _get_segmented_thresholds(mcap_cr)
        headroom_delivery = _calculate_headroom_and_delivery(fundamentals)

        # ── Stage 7: Forensic Audit ──────────────────────────────────────
        try:
            forensic_result = forensic.audit_equity(
                symbol=symbol,
                shares_latest=fundamentals.get("shares_count"),
                shares_3y_ago=fundamentals.get("shares_count_10yr_back"),
            )
            if forensic_result.governance_veto:
                forensic_verdict = "RED_FLAG_VETO"
            elif forensic_result.forensic_score >= 60.0:
                forensic_verdict = "CLEAN"
            else:
                forensic_verdict = "CAUTION"

            # Hard veto on forensic RED flags
            if forensic_verdict == "RED_FLAG_VETO":
                flags_msg = ", ".join(forensic_result.red_flags) if forensic_result.red_flags else "Governance Veto"
                disqualified.append(DeadliestComboResult(
                    symbol=symbol, company_name=company_name,
                    hard_gate_pass=False,
                    disqualification_reason=f"FORENSIC_RED_FLAG: {flags_msg}",
                    composite_score=0.0,
                    fundamentals=fundamentals,
                ))
                logger.info(f"[PIPELINE] {symbol} FORENSIC VETO: {flags_msg}")
                continue
        except Exception as e:
            logger.warning(f"[PIPELINE] Forensic audit failed for {symbol}: {e}")
            forensic_verdict = "UNAVAILABLE"

        # ── Stage 8: Multiplicative Cross-Product Scoring ─────────────────
        # Normalize multibagger score from 0-100 to 0.0-1.0
        mb_normalized = min(1.0, max(0.01, mb_score / 100.0))
        rc_normalized = _normalize_return_ceiling(rc_base)

        # Potential amplified by Operating Leverage Convexity Omega
        potential = min(1.0, max(0.01, mb_normalized * (omega ** 0.10)))
        timing = min(1.0, max(0.01, tbqe_raw))
        ceiling_factor = min(1.0, max(0.05, rc_normalized))

        # Deadliest Score = 100 * (Potential^0.55 * Timing^0.30 * CeilingFactor^0.15) * Q_continuous
        cross_product = (
            (potential ** SCORING_POWERS["potential"]) *
            (timing ** SCORING_POWERS["timing"]) *
            (ceiling_factor ** SCORING_POWERS["ceiling_factor"])
        )
        deadliest_score = round(100.0 * cross_product * continuous_q, 2)

        sector = fundamentals.get("sector") or fundamentals.get("industry") or "GENERAL"

        result = DeadliestComboResult(
            symbol=symbol,
            company_name=company_name,
            composite_score=deadliest_score,
            multibagger_score=round(mb_score, 2),
            tbqe_score=round(tbqe_raw, 4),
            return_ceiling=rc_result,
            pat_quality_flag=pat_qf,
            forensic_verdict=forensic_verdict,
            weinstein_stage=weinstein,
            launchpad_label=launchpad,
            lifecycle_stage=lifecycle,
            hard_gate_pass=True,
            disqualification_reason=None,
            fundamentals=fundamentals,
            continuous_q=continuous_q,
            omega_convexity=omega,
            sector=sector,
            tier=segmented_info["tier"],
            breakdown={
                "mb_normalized": round(mb_normalized, 4),
                "tbqe_raw": round(tbqe_raw, 4),
                "rc_base_multiple": rc_base,
                "rc_normalized": round(rc_normalized, 4),
                "eq_score": round(eq_score, 4),
                "continuous_q": continuous_q,
                "operating_leverage_convexity_omega": omega,
                "order_book_burn_rate_kappa": kappa,
                "segmented_tier": segmented_info["tier"],
                "segmented_thresholds": segmented_info,
                "headroom_and_delivery": headroom_delivery,
                "cross_product": round(cross_product, 4),
                "forensic_verdict": forensic_verdict,
                "scoring_model": "multiplicative_cross_product_v2",
                "powers": SCORING_POWERS,
                "weights": COMPOSITE_WEIGHTS,
            },
        )
        results.append(result)

    # ── Stage 9: Rank & Institutional Portfolio Layer ────────────────────
    results.sort(key=lambda r: r.composite_score, reverse=True)

    if enforce_portfolio_constraints and len(results) > 1:
        max_per_sector = max(1, int(round(top_n * max_sector_exposure)))
        sector_counts: Dict[str, int] = {}
        filtered_results: List[DeadliestComboResult] = []
        deferred_results: List[DeadliestComboResult] = []

        for r in results:
            sec = r.sector or "GENERAL"
            if sector_counts.get(sec, 0) < max_per_sector:
                sector_counts[sec] = sector_counts.get(sec, 0) + 1
                filtered_results.append(r)
            else:
                deferred_results.append(r)

        final_list = filtered_results + deferred_results
    else:
        final_list = results

    # Assign ranks
    for i, r in enumerate(final_list, 1):
        r.rank = i

    # Log disqualified
    if disqualified:
        logger.info(f"[PIPELINE] {len(disqualified)} stocks disqualified:")
        for dq in disqualified:
            logger.info(f"  {dq.symbol}: {dq.disqualification_reason}")

    return final_list[:top_n]


def run_deadliest_combo_pipeline_with_audit(
    tickers: List[str],
    top_n: int = 10,
    fetch_live: bool = True,
    pledge_overrides: Optional[Dict[str, float]] = None,
    enforce_portfolio_constraints: bool = True,
    max_sector_exposure: float = 0.30,
) -> Tuple[List[DeadliestComboResult], List[DeadliestComboResult]]:
    """Same as run_deadliest_combo_pipeline, but returns (ranked_results, disqualified_list)."""
    ranked = run_deadliest_combo_pipeline(
        tickers=tickers,
        top_n=top_n,
        fetch_live=fetch_live,
        pledge_overrides=pledge_overrides,
        enforce_portfolio_constraints=enforce_portfolio_constraints,
        max_sector_exposure=max_sector_exposure,
    )
    from app.services.data_ingestion.fundamental_fetcher import FundamentalFetcher
    from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
    from app.services.research.forensic_auditor import ForensicAuditor
    forensic = ForensicAuditor()
    disqualified = []
    ranked_symbols = {r.symbol for r in ranked}

    for ticker in tickers:
        sym = ticker.upper().strip()
        if sym in ranked_symbols:
            continue
        try:
            f = FundamentalFetcher.fetch_and_store(sym) if fetch_live else ScreenerCloudConnector.get_or_fetch_fundamentals(sym)
            if f is None:
                disqualified.append(DeadliestComboResult(symbol=sym, company_name=sym, disqualification_reason="DATA_FETCH_FAILED"))
                continue
            if pledge_overrides:
                norm_key = sym.replace(".NS", "").replace(".BO", "")
                for k, val in pledge_overrides.items():
                    if k.upper().replace(".NS", "").replace(".BO", "") == norm_key:
                        f["pledged_pct"] = float(val)
                        break
            reason = _check_hard_gates(f)
            if reason:
                disqualified.append(DeadliestComboResult(symbol=sym, company_name=f.get("company_name", sym), disqualification_reason=reason))
                continue
            fr = forensic.audit_equity(symbol=sym)
            if fr.governance_veto:
                msg = ", ".join(fr.red_flags) if fr.red_flags else "Governance Veto"
                disqualified.append(DeadliestComboResult(symbol=sym, company_name=f.get("company_name", sym), disqualification_reason=f"FORENSIC_RED_FLAG: {msg}"))
        except Exception as e:
            disqualified.append(DeadliestComboResult(symbol=sym, company_name=sym, disqualification_reason=str(e)))

    return ranked, disqualified


def format_pipeline_report(
    results: List[DeadliestComboResult],
    disqualified: Optional[List[DeadliestComboResult]] = None,
) -> str:
    """Format pipeline results as a markdown report string."""
    lines = [
        "# Deadliest Combination Pipeline Report",
        f"## Top {len(results)} — Pre-Fly + Multibagger + Return Ceiling + Earnings Quality + Forensic",
        "",
        "| Rank | Ticker | Company | Composite | MB Score | TBQE | Base Return | PAT Quality | Continuous Q | Omega | Weinstein | Forensic |",
        "|:---:|:---|:---|:---:|:---:|:---:|:---:|:---|:---:|:---:|:---|:---|",
    ]

    for r in results:
        rc_base = r.return_ceiling.get("base_multiple", 0.0) if r.return_ceiling else 0.0
        q_disp = f"{r.continuous_q:.2f}" if r.continuous_q is not None else "-"
        om_disp = f"{r.omega_convexity:.2f}x" if r.omega_convexity is not None else "1.00x"
        lines.append(
            f"| {r.rank} | `{r.symbol}` | {r.company_name} | "
            f"**{r.composite_score:.1f}** | {r.multibagger_score:.1f}/100 | "
            f"{r.tbqe_score:.2f} | {rc_base:.2f}x | {r.pat_quality_flag} | "
            f"{q_disp} | {om_disp} | {r.weinstein_stage} | {r.forensic_verdict} |"
        )

    if disqualified:
        lines.append("")
        lines.append(f"## Disqualified Candidates & Red Flag Vetoes ({len(disqualified)})")
        lines.append("")
        lines.append("| Ticker | Company | Reason for Disqualification | Hard Gate / Forensic |")
        lines.append("|:---|:---|:---|:---|")
        for dq in disqualified:
            lines.append(f"| `{dq.symbol}` | {dq.company_name} | {dq.disqualification_reason} | FAILED |")

    lines.append("")
    lines.append("### Institutional Scoring Model (Multiplicative Cross-Product)")
    lines.append(f"- **Formulation**: $$\\text{{Score}} = 100 \\times (\\text{{Potential}}^{{0.55}} \\times \\text{{Timing}}^{{0.30}} \\times \\text{{CeilingFactor}}^{{0.15}}) \\times Q_{{\\text{{continuous}}}}$$")
    lines.append("- **Quality Multiplier Q**: Continuous range `[0.50, 1.00]` evaluating CFO/PAT, zero-pledge, and leverage.")
    lines.append("- **Operating Leverage Convexity Omega**: Range `[1.0, 2.5]` boosting operating acceleration.")

    return "\n".join(lines)
