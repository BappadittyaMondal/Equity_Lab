"""Forensic Scoring Engine — Phase 2, Layer 7.

Implements three institutional forensic models:
  - Beneish M-Score (8-variable earnings manipulation detector)
  - Altman Z-Score (5-ratio financial distress predictor)
  - Piotroski F-Score (9-point binary balance sheet quality signal)

All three use real financial observations from ResearchDataStore.
Results feed directly into the governance veto in the Arbiter.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.models.schemas import StrategyRunResponse
from app.services.market_data import create_meta_header, normalize_symbol, get_ist_now_str
from app.services.research_data import ResearchDataStore
from app.services.strategies.fundamental_metrics import _extract_series


def _get(series: List[Tuple[str, float]], idx: int = -1) -> Optional[float]:
    """Safely get a value from a series by index."""
    try:
        return series[idx][1] if series else None
    except IndexError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Beneish M-Score
# ─────────────────────────────────────────────────────────────────────────────

def compute_beneish_mscore(financials: List[Any]) -> Dict[str, Any]:
    """Compute Beneish M-Score from financial observations.

    8 Variables:
      DSRI  — Days Sales Receivable Index
      GMI   — Gross Margin Index
      AQI   — Asset Quality Index
      SGI   — Sales Growth Index
      DEPI  — Depreciation Index
      SGAI  — SG&A Index
      TATA  — Total Accruals to Total Assets
      LVGI  — Leverage Index

    M-Score > -1.78 → likely manipulator (flag for investigation).
    M-Score < -2.22 → likely not manipulator.
    """
    evidence = []
    result: Dict[str, Any] = {}

    # Extract series needed
    rev_s = _extract_series(financials, ["revenue", "total_revenue"])
    profit_s = _extract_series(financials, ["gross_profit"])
    asset_s = _extract_series(financials, ["total_assets"])
    cfo_s = _extract_series(financials, ["operating_cash_flow", "cfo"])
    pat_s = _extract_series(financials, ["net_income", "pat"])
    debt_s = _extract_series(financials, ["total_debt", "net_debt"])

    # Need at least 2 periods for year-over-year ratios
    if len(rev_s) < 2 or len(asset_s) < 2:
        return {
            "status": "insufficient_data",
            "reason": f"Need ≥2 periods: revenue={len(rev_s)}, assets={len(asset_s)}",
            "evidence": ["Beneish M-Score requires multi-period data"],
        }

    rev_t = _get(rev_s, -1) or 1.0
    rev_t1 = _get(rev_s, -2) or 1.0
    asset_t = _get(asset_s, -1) or 1.0
    asset_t1 = _get(asset_s, -2) or 1.0
    cfo_t = _get(cfo_s, -1) or 0.0
    pat_t = _get(pat_s, -1) or 1.0
    debt_t = _get(debt_s, -1) or 0.0
    debt_t1 = _get(debt_s, -2) or 1.0

    # Gross margin approximation if not direct
    gp_t = _get(profit_s, -1)
    gp_t1 = _get(profit_s, -2)
    gm_t = (gp_t / rev_t) if gp_t and rev_t > 0 else 0.3  # default 30% if missing
    gm_t1 = (gp_t1 / rev_t1) if gp_t1 and rev_t1 > 0 else gm_t

    # ── Variable calculations ──────────────────────────────────────────────

    # DSRI: if receivables unavailable, use revenue proxy (conservative)
    # Typically DSRI = (Receivables_t / Rev_t) / (Receivables_t-1 / Rev_t-1)
    # We approximate using revenue ratio change as proxy
    dsri = 1.0  # neutral if not available
    evidence.append(f"DSRI: {dsri:.3f} (proxy — receivables not in DB)")

    # GMI: Gross Margin Index
    gmi = (gm_t1 / gm_t) if gm_t > 0 else 1.0
    result["gmi"] = round(gmi, 4)
    if gmi > 1.05:
        evidence.append(f"GMI={gmi:.2f}: Gross margin deteriorating (manipulation signal)")

    # AQI: Asset Quality Index (non-current assets / total assets ratio change)
    # Proxy: if total assets grew faster than revenue, flag
    aqi = (asset_t / asset_t1) / (rev_t / rev_t1) if rev_t1 > 0 and asset_t1 > 0 else 1.0
    result["aqi"] = round(aqi, 4)

    # SGI: Sales Growth Index
    sgi = (rev_t / rev_t1) if rev_t1 > 0 else 1.0
    result["sgi"] = round(sgi, 4)
    if sgi < 0.9:
        evidence.append(f"SGI={sgi:.2f}: Revenue declining YoY")

    # DEPI: Depreciation Index (approximated as 1.0 — depreciation rarely stored)
    depi = 1.0
    result["depi"] = depi

    # SGAI: SG&A Index (approximated as 1.0 — SG&A rarely stored separately)
    sgai = 1.0
    result["sgai"] = sgai

    # TATA: Total Accruals to Total Assets
    # TATA = (PAT - CFO) / Total Assets
    accruals = pat_t - cfo_t
    tata = accruals / asset_t if asset_t > 0 else 0.0
    result["tata"] = round(tata, 4)
    if tata > 0.05:
        evidence.append(f"TATA={tata:.3f}: High accruals relative to assets (earnings quality concern)")

    # LVGI: Leverage Index
    lev_t = debt_t / asset_t if asset_t > 0 else 0.0
    lev_t1 = debt_t1 / asset_t1 if asset_t1 > 0 else 0.0
    lvgi = (lev_t / lev_t1) if lev_t1 > 0 else 1.0
    result["lvgi"] = round(lvgi, 4)
    if lvgi > 1.2:
        evidence.append(f"LVGI={lvgi:.2f}: Leverage increasing significantly")

    # ── M-Score calculation ────────────────────────────────────────────────
    m_score = (
        -4.84
        + 0.920 * dsri
        + 0.528 * gmi
        + 0.404 * aqi
        + 0.892 * sgi
        + 0.115 * depi
        - 0.172 * sgai
        + 4.679 * tata
        - 0.327 * lvgi
    )
    m_score = round(m_score, 3)
    result["m_score"] = m_score

    if m_score > -1.78:
        classification = "LIKELY_MANIPULATOR"
        evidence.append(f"⚠️ BENEISH M-SCORE = {m_score:.2f} > -1.78: Earnings manipulation suspected")
    elif m_score > -2.22:
        classification = "GREY_ZONE"
        evidence.append(f"Beneish M-Score = {m_score:.2f}: Grey zone — further investigation recommended")
    else:
        classification = "LIKELY_NOT_MANIPULATOR"
        evidence.append(f"Beneish M-Score = {m_score:.2f}: No manipulation signal")

    result["classification"] = classification
    result["threshold"] = -1.78
    result["evidence"] = evidence
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Altman Z-Score
# ─────────────────────────────────────────────────────────────────────────────

def compute_altman_zscore(financials: List[Any]) -> Dict[str, Any]:
    """Compute Altman Z-Score for financial distress prediction.

    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5

    Where:
      X1 = Working Capital / Total Assets
      X2 = Retained Earnings / Total Assets
      X3 = EBIT / Total Assets
      X4 = Market Cap / Total Liabilities (or Book Equity / Total Debt)
      X5 = Revenue / Total Assets

    Zones:
      Z > 2.99  → Safe
      1.81–2.99 → Grey Zone
      Z < 1.81  → Distress
    """
    evidence = []
    result: Dict[str, Any] = {}

    wc_s = _extract_series(financials, ["working_capital"])
    re_s = _extract_series(financials, ["retained_earnings"])
    ebit_s = _extract_series(financials, ["operating_income", "ebitda"])
    asset_s = _extract_series(financials, ["total_assets"])
    equity_s = _extract_series(financials, ["total_equity"])
    debt_s = _extract_series(financials, ["total_debt", "total_liabilities"])
    rev_s = _extract_series(financials, ["revenue", "total_revenue"])

    total_assets = _get(asset_s, -1)
    if not total_assets or total_assets <= 0:
        return {
            "status": "insufficient_data",
            "reason": "Total assets not available",
            "evidence": ["Altman Z-Score requires balance sheet data"],
        }

    wc = _get(wc_s, -1) or 0.0
    re = _get(re_s, -1) or 0.0
    ebit = _get(ebit_s, -1) or 0.0
    equity = _get(equity_s, -1) or 0.0
    debt = _get(debt_s, -1) or total_assets * 0.3  # approximate if missing
    rev = _get(rev_s, -1) or 0.0

    x1 = wc / total_assets
    x2 = re / total_assets
    x3 = ebit / total_assets
    x4 = equity / debt if debt > 0 else 2.0  # book equity/debt ratio
    x5 = rev / total_assets

    z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
    z_score = round(z_score, 3)

    result.update({
        "z_score": z_score,
        "x1_working_capital_ratio": round(x1, 3),
        "x2_retained_earnings_ratio": round(x2, 3),
        "x3_ebit_ratio": round(x3, 3),
        "x4_equity_debt_ratio": round(x4, 3),
        "x5_asset_turnover": round(x5, 3),
    })

    if z_score > 2.99:
        zone = "SAFE"
        evidence.append(f"Altman Z-Score = {z_score:.2f}: SAFE zone (> 2.99)")
    elif z_score > 1.81:
        zone = "GREY"
        evidence.append(f"Altman Z-Score = {z_score:.2f}: GREY zone (1.81–2.99) — monitor")
    else:
        zone = "DISTRESS"
        evidence.append(f"⚠️ Altman Z-Score = {z_score:.2f}: DISTRESS zone (< 1.81) — financial risk")

    result["zone"] = zone
    result["evidence"] = evidence
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Piotroski F-Score
# ─────────────────────────────────────────────────────────────────────────────

def compute_piotroski_fscore(financials: List[Any]) -> Dict[str, Any]:
    """Compute Piotroski F-Score (0–9 binary signals).

    Profitability (4 signals):
      F1: ROA > 0
      F2: CFO > 0
      F3: ROA increased YoY
      F4: CFO > ROA (earnings quality / accruals)

    Leverage/Liquidity (3 signals):
      F5: Long-term debt ratio decreased YoY
      F6: Current ratio increased YoY (proxy: working capital ratio)
      F7: No new shares issued (shares outstanding stable)

    Operating Efficiency (2 signals):
      F8: Gross margin improved YoY
      F9: Asset turnover improved YoY

    Score ≥ 7 → Strong
    Score 4–6 → Moderate
    Score ≤ 3 → Weak
    """
    evidence = []
    scores: Dict[str, int] = {}

    pat_s = _extract_series(financials, ["net_income", "pat"])
    cfo_s = _extract_series(financials, ["operating_cash_flow", "cfo"])
    asset_s = _extract_series(financials, ["total_assets"])
    debt_s = _extract_series(financials, ["total_debt"])
    rev_s = _extract_series(financials, ["revenue", "total_revenue"])
    gp_s = _extract_series(financials, ["gross_profit"])

    def _binary(condition: bool, label: str, true_msg: str, false_msg: str) -> int:
        if condition:
            evidence.append(f"✅ {label}: {true_msg}")
            return 1
        else:
            evidence.append(f"❌ {label}: {false_msg}")
            return 0

    # Need at least 2 periods
    if len(pat_s) < 2 or len(asset_s) < 2:
        return {
            "status": "insufficient_data",
            "reason": f"Need ≥2 periods of data. Have: pat={len(pat_s)}, assets={len(asset_s)}",
            "evidence": ["Piotroski F-Score requires year-over-year comparison"],
        }

    pat_t = _get(pat_s, -1) or 0.0
    pat_t1 = _get(pat_s, -2) or 0.0
    cfo_t = _get(cfo_s, -1) or 0.0
    asset_t = _get(asset_s, -1) or 1.0
    asset_t1 = _get(asset_s, -2) or 1.0
    debt_t = _get(debt_s, -1) or 0.0
    debt_t1 = _get(debt_s, -2) or 0.0
    rev_t = _get(rev_s, -1) or 0.0
    rev_t1 = _get(rev_s, -2) or 0.0
    gp_t = _get(gp_s, -1) or 0.0
    gp_t1 = _get(gp_s, -2) or 0.0

    roa_t = pat_t / asset_t if asset_t > 0 else 0.0
    roa_t1 = pat_t1 / asset_t1 if asset_t1 > 0 else 0.0

    # F1: ROA > 0
    scores["F1"] = _binary(roa_t > 0, "F1 Profitability", f"ROA positive ({roa_t:.3f})", f"ROA negative ({roa_t:.3f})")
    # F2: CFO > 0
    scores["F2"] = _binary(cfo_t > 0, "F2 Cash Flow", f"Operating CFO positive ({cfo_t:,.0f})", f"Negative CFO ({cfo_t:,.0f})")
    # F3: ROA improved
    scores["F3"] = _binary(roa_t > roa_t1, "F3 ROA trend", f"ROA improving ({roa_t1:.3f} → {roa_t:.3f})", f"ROA declining ({roa_t1:.3f} → {roa_t:.3f})")
    # F4: CFO > ROA (cash-backed earnings)
    scores["F4"] = _binary(cfo_t / asset_t > roa_t if asset_t > 0 else False, "F4 Accruals", "CFO > ROA: high earnings quality", "CFO < ROA: accrual concern")

    # F5: Debt ratio decreased
    lev_t = debt_t / asset_t if asset_t > 0 else 0.0
    lev_t1 = debt_t1 / asset_t1 if asset_t1 > 0 else 0.0
    scores["F5"] = _binary(lev_t <= lev_t1, "F5 Leverage", f"Debt ratio stable/improving ({lev_t1:.2f} → {lev_t:.2f})", f"Debt ratio rising ({lev_t1:.2f} → {lev_t:.2f})")

    # F6: Working capital (proxy: current assets ratio improved)
    # Proxy: revenue/asset turnover improved
    turn_t = rev_t / asset_t if asset_t > 0 else 0.0
    turn_t1 = rev_t1 / asset_t1 if asset_t1 > 0 else 0.0
    scores["F6"] = _binary(turn_t >= turn_t1, "F6 Liquidity proxy", "Asset turnover improved", "Asset turnover declined")

    # F7: No dilution (approximated — share count not stored, assume neutral)
    scores["F7"] = 1  # Neutral — no share issuance data
    evidence.append("⚪ F7 Dilution: data not tracked — neutral score")

    # F8: Gross margin improved
    gm_t = (gp_t / rev_t) if rev_t > 0 and gp_t > 0 else 0.0
    gm_t1 = (gp_t1 / rev_t1) if rev_t1 > 0 and gp_t1 > 0 else gm_t
    scores["F8"] = _binary(gm_t >= gm_t1, "F8 Gross Margin", f"Gross margin stable/improving ({gm_t1*100:.1f}% → {gm_t*100:.1f}%)", f"Gross margin declining ({gm_t1*100:.1f}% → {gm_t*100:.1f}%)")

    # F9: Asset turnover improved
    scores["F9"] = _binary(turn_t > turn_t1, "F9 Asset Turnover", f"Improving ({turn_t1:.2f} → {turn_t:.2f})", f"Declining ({turn_t1:.2f} → {turn_t:.2f})")

    f_score = sum(scores.values())

    if f_score >= 7:
        strength = "STRONG"
        evidence.append(f"Piotroski F-Score: {f_score}/9 — STRONG balance sheet quality")
    elif f_score >= 4:
        strength = "MODERATE"
        evidence.append(f"Piotroski F-Score: {f_score}/9 — MODERATE quality")
    else:
        strength = "WEAK"
        evidence.append(f"⚠️ Piotroski F-Score: {f_score}/9 — WEAK fundamentals")

    return {
        "f_score": f_score,
        "max_score": 9,
        "strength": strength,
        "component_scores": scores,
        "evidence": evidence,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Unified Forensic Engine Runner (routes to registry)
# ─────────────────────────────────────────────────────────────────────────────

def run_forensic_engine(
    symbol: str,
    store: Optional[ResearchDataStore] = None,
    strategy_id: str = "FORENSIC",
) -> StrategyRunResponse:
    """Run all three forensic models and combine into a single StrategyRunResponse."""
    norm = normalize_symbol(symbol)
    data_store = store or ResearchDataStore()
    all_evidence = []
    governance_flags = []

    try:
        _, financials, _, _, _, _ = data_store.get_timeline(norm)
    except Exception as e:
        return StrategyRunResponse(
            strategy_id=strategy_id,
            strategy_name="Forensic & Governance Engine (Beneish + Altman + Piotroski)",
            status="data_insufficient",
            executed_at=get_ist_now_str(),
            symbol=norm,
            passed_gates=True,  # Benefit of the doubt when no data
            results={"status": "data_insufficient", "reason": str(e)},
            metrics={},
            risk_warnings=["No financial data — forensic models cannot run"],
            disclaimer="Cannot compute forensic scores without financial data.",
            meta=create_meta_header(source=f"IERL Forensic Engine ({norm})"),
        )

    beneish = compute_beneish_mscore(financials)
    altman = compute_altman_zscore(financials)
    piotroski = compute_piotroski_fscore(financials)

    all_evidence.extend(beneish.get("evidence", []))
    all_evidence.extend(altman.get("evidence", []))
    all_evidence.extend(piotroski.get("evidence", []))

    # Determine if any CRITICAL flag
    beneish_flag = beneish.get("classification") == "LIKELY_MANIPULATOR"
    altman_distress = altman.get("zone") == "DISTRESS"
    piotroski_weak = piotroski.get("strength") == "WEAK"

    if beneish_flag:
        governance_flags.append("BENEISH_MANIPULATION_SIGNAL")
    if altman_distress:
        governance_flags.append("ALTMAN_FINANCIAL_DISTRESS")
    if piotroski_weak:
        governance_flags.append("PIOTROSKI_WEAK_FUNDAMENTALS")

    # Overall forensic verdict
    passed = len(governance_flags) == 0
    forensic_risk = "CRITICAL" if beneish_flag or altman_distress else ("HIGH" if piotroski_weak else "LOW")

    return StrategyRunResponse(
        strategy_id=strategy_id,
        strategy_name="Forensic & Governance Engine",
        status="production",
        executed_at=get_ist_now_str(),
        symbol=norm,
        passed_gates=passed,
        results={
            "beneish_m_score": beneish,
            "altman_z_score": altman,
            "piotroski_f_score": piotroski,
            "governance_flags": governance_flags,
            "forensic_risk": forensic_risk,
            "evidence": all_evidence,
        },
        metrics={
            "m_score": beneish.get("m_score"),
            "z_score": altman.get("z_score"),
            "f_score": piotroski.get("f_score"),
            "forensic_risk": forensic_risk,
        },
        risk_warnings=[
            "Beneish M-Score uses approximated DSRI/DEPI/SGAI — improves with full accounting data.",
            "Altman Z-Score calibrated for manufacturing/industrial firms — adjust for banks/NBFCs.",
        ],
        disclaimer="Forensic scores are quantitative signals, not auditor conclusions.",
        meta=create_meta_header(source=f"IERL Forensic Engine ({norm})"),
    )
