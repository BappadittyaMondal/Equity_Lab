"""Debate Engine — Phase 3, Layer 9.

Implements structured Bull vs Bear debate for every conviction call.

Key features:
  - BullCase: Top 3 supporting engines + cited evidence
  - BearCase: Top 3 contradicting engines + cited evidence  
  - Thesis attack: For each bull point, generate the strongest counter-argument
  - Contradiction severity: LOW/MEDIUM/HIGH/CRITICAL based on engine category conflicts
  - Falsification conditions: 2–3 specific measurable conditions that invalidate the thesis

Severity escalation rules (from master prompt):
  - Fundamental vs Technical disagreement → LOW
  - Fundamental vs Fundamental (growth vs quality) → MEDIUM
  - Fundamental vs Forensic → HIGH (governance concern overrides growth)
  - Any FORENSIC engine flags CRITICAL (Beneish > -1.78, Altman < 1.81) → CRITICAL
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from app.models.schemas import ContradictionReport

logger = logging.getLogger(__name__)

# Engine category mapping for severity calculation
ENGINE_CATEGORIES: Dict[str, str] = {
    "E1": "FUNDAMENTAL", "E2": "FUNDAMENTAL", "E3": "FUNDAMENTAL",
    "E4": "FUNDAMENTAL", "E5": "FUNDAMENTAL", "E6": "FUNDAMENTAL",
    "E7": "VALUATION",
    "B4": "TECHNICAL", "B5": "TECHNICAL", "B6": "TECHNICAL",
    "B7": "TECHNICAL", "B8": "TECHNICAL",
    "C9": "VALUATION", "DCF_FWD": "VALUATION",
    "C11": "FORENSIC", "C12": "FORENSIC", "C13": "FORENSIC",
    "FORENSIC": "FORENSIC",
    "D15": "TECHNICAL", "D17": "TECHNICAL", "D18": "GOVERNANCE",
    "A1": "OPTIONS", "A2": "OPTIONS", "A3": "OPTIONS",
}

# Severity matrix: which category pairs cause what severity
SEVERITY_MATRIX: Dict[Tuple[str, str], str] = {
    ("FUNDAMENTAL", "TECHNICAL"): "LOW",
    ("TECHNICAL", "FUNDAMENTAL"): "LOW",
    ("VALUATION", "TECHNICAL"): "LOW",
    ("TECHNICAL", "VALUATION"): "LOW",
    ("FUNDAMENTAL", "VALUATION"): "MEDIUM",
    ("VALUATION", "FUNDAMENTAL"): "MEDIUM",
    ("FUNDAMENTAL", "FORENSIC"): "HIGH",
    ("FORENSIC", "FUNDAMENTAL"): "HIGH",
    ("FORENSIC", "TECHNICAL"): "HIGH",
    ("TECHNICAL", "FORENSIC"): "HIGH",
    ("FORENSIC", "GOVERNANCE"): "CRITICAL",
    ("GOVERNANCE", "FORENSIC"): "CRITICAL",
}


def _get_engine_category(engine_id: str) -> str:
    return ENGINE_CATEGORIES.get(engine_id, "OTHER")


def _compute_contradiction_severity(
    bull_engines: List[str],
    bear_engines: List[str],
    engine_outputs: List[Dict[str, Any]],
) -> str:
    """Compute worst-case severity across all bull vs bear category pairs."""
    severity_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    worst = "LOW"

    for bull_id in bull_engines:
        bull_cat = _get_engine_category(bull_id)
        for bear_id in bear_engines:
            bear_cat = _get_engine_category(bear_id)

            # Check if any forensic engine reports a CRITICAL flag
            for out in engine_outputs:
                if out.get("engine_id") == bear_id:
                    raw = out.get("raw")
                    if raw:
                        results = getattr(raw, "results", {}) or {}
                        forensic_risk = results.get("forensic_risk", "")
                        if forensic_risk == "CRITICAL":
                            worst = "CRITICAL"

            pair_severity = SEVERITY_MATRIX.get((bull_cat, bear_cat), "LOW")
            if severity_order.index(pair_severity) > severity_order.index(worst):
                worst = pair_severity

    return worst


def _extract_engine_evidence(output: Dict[str, Any]) -> List[str]:
    """Extract evidence strings from a strategy engine output."""
    raw = output.get("raw")
    if not raw:
        return []
    results = getattr(raw, "results", {}) or {}
    evidence = results.get("evidence", [])
    if isinstance(evidence, list):
        return evidence[:3]  # Top 3 evidence items
    return []


def _generate_thesis_attack(bull_evidence: str, bear_evidence: List[str]) -> str:
    """Generate the strongest counter-argument to a bull evidence point."""
    bull_lower = bull_evidence.lower()

    # Pattern matching for common bull claims → counter-arguments
    if "revenue" in bull_lower and ("grow" in bull_lower or "acceler" in bull_lower):
        if bear_evidence:
            return f"Counter: Revenue may be growing, but check margin trajectory — {bear_evidence[0] if bear_evidence else 'profitability may not be keeping pace'}."
        return "Counter: Revenue growth without margin expansion may indicate unprofitable growth."

    if "fcf" in bull_lower or "free cash flow" in bull_lower:
        return "Counter: FCF may be inflated by working capital release or deferred capex — check maintenance vs growth capex split."

    if "roce" in bull_lower or "roe" in bull_lower:
        return "Counter: High ROCE can be a lagging indicator — verify if it is sustainable at current asset base or will compress as the company scales."

    if "beneish" in bull_lower or "piotroski" in bull_lower:
        return "Counter: Quantitative forensic scores use approximated variables — complement with annual report review for related-party transactions."

    if "rs rating" in bull_lower or "relative strength" in bull_lower:
        return "Counter: High RS may indicate the stock is already extended — check distance from last base breakout and volume confirmation."

    if "vcp" in bull_lower or "breakout" in bull_lower:
        return "Counter: Breakout requires volume ≥ 150% of 50-day average on the breakout day — confirm before entry."

    # Generic attack
    return f"Counter: Verify that this signal ({bull_evidence[:60]}...) holds on a 4-quarter sequential basis, not just the most recent period."


def _generate_falsification_conditions(
    symbol: str,
    engine_outputs: List[Dict[str, Any]],
    macro_regime: str = "CALM",
) -> List[str]:
    """Generate 2–3 specific measurable invalidation conditions from engine results."""
    conditions = []

    # Scan engine results for specific thresholds to cite
    for out in engine_outputs:
        raw = out.get("raw")
        if not raw:
            continue
        results = getattr(raw, "results", {}) or {}
        metrics = getattr(raw, "metrics", {}) or {}

        # Governance threshold
        pledge_risk = results.get("promoter_pledge_risk")
        pledge_pct = metrics.get("promoter_pledge_pct")
        if pledge_pct and isinstance(pledge_pct, (int, float)):
            conditions.append(
                f"Thesis invalidated if promoter pledge exceeds {min(pledge_pct + 10, 40):.0f}% "
                f"(currently {pledge_pct:.1f}%)"
            )

        # Revenue growth threshold
        rev_yoy = results.get("revenue_yoy_pct") or results.get("revenue_growth_pct")
        if rev_yoy and isinstance(rev_yoy, (int, float)):
            threshold = max(rev_yoy * 0.5, 5.0)
            conditions.append(
                f"Thesis invalidated if next-quarter revenue growth falls below {threshold:.0f}% YoY "
                f"(current trend: {rev_yoy:.1f}%)"
            )

        # D/E ratio threshold
        de = metrics.get("de_ratio") or results.get("de_ratio")
        if de and isinstance(de, (int, float)):
            conditions.append(
                f"Thesis invalidated if D/E ratio exceeds {min(de * 1.5, 1.5):.1f}x "
                f"(currently {de:.1f}x)"
            )

        if len(conditions) >= 3:
            break

    # Ensure we always have at least 3 conditions
    defaults = [
        f"Thesis invalidated if {symbol} reports revenue decline for 2 consecutive quarters",
        "Thesis invalidated if Altman Z-Score falls below 1.81 (distress zone)",
        f"Thesis invalidated if regime transitions to CRISIS and position lacks stop-loss protection",
    ]
    while len(conditions) < 3:
        conditions.append(defaults[len(conditions)])

    return conditions[:3]


def generate_debate(
    symbol: str,
    engine_outputs: List[Dict[str, Any]],
    macro_regime: str = "CALM",
) -> ContradictionReport:
    """Generate a structured Bull vs Bear debate from engine outputs.

    Args:
        symbol: Stock symbol.
        engine_outputs: List of dicts from Arbiter._collect_engine_outputs().
        macro_regime: Current market regime (CALM/ELEVATED/VOLATILE/CRISIS).

    Returns:
        ContradictionReport with full debate structure.
    """
    if not engine_outputs:
        return ContradictionReport(
            symbol=symbol,
            decision_impact="No engine outputs available for debate.",
            contradiction_severity="LOW",
            net_evidence_balance="NEUTRAL",
        )

    # Split into bull and bear
    bull_outputs = [o for o in engine_outputs if o.get("verdict") == "Buy"]
    bear_outputs = [o for o in engine_outputs if o.get("verdict") == "Avoid"]

    bull_ids = [o["engine_id"] for o in bull_outputs]
    bear_ids = [o["engine_id"] for o in bear_outputs]

    # ── Build Bull Case (top 3 by confidence) ─────────────────────────────
    bull_sorted = sorted(bull_outputs, key=lambda x: x.get("confidence", 0), reverse=True)
    bull_case = []
    for out in bull_sorted[:3]:
        evidence = _extract_engine_evidence(out)
        raw = out.get("raw")
        bull_case.append({
            "engine_id": out["engine_id"],
            "engine_name": getattr(raw, "strategy_name", out["engine_id"]) if raw else out["engine_id"],
            "confidence": out.get("confidence", 0),
            "evidence": evidence,
            "category": _get_engine_category(out["engine_id"]),
        })

    # ── Build Bear Case (top 3 by confidence) ─────────────────────────────
    bear_sorted = sorted(bear_outputs, key=lambda x: x.get("confidence", 0), reverse=True)
    bear_case = []
    for out in bear_sorted[:3]:
        evidence = _extract_engine_evidence(out)
        raw = out.get("raw")
        bear_case.append({
            "engine_id": out["engine_id"],
            "engine_name": getattr(raw, "strategy_name", out["engine_id"]) if raw else out["engine_id"],
            "confidence": out.get("confidence", 0),
            "evidence": evidence,
            "category": _get_engine_category(out["engine_id"]),
        })

    # ── Thesis attack: add counter-argument for each bull point ───────────
    bear_evidence_pool = [e for bc in bear_case for e in bc.get("evidence", [])]
    for bull in bull_case:
        attacks = []
        for evidence_str in bull.get("evidence", []):
            attack = _generate_thesis_attack(evidence_str, bear_evidence_pool)
            attacks.append(attack)
        bull["counter_arguments"] = attacks

    # ── Contradiction severity ─────────────────────────────────────────────
    severity = _compute_contradiction_severity(bull_ids, bear_ids, engine_outputs)

    # ── Net evidence balance ───────────────────────────────────────────────
    bull_weight = len(bull_outputs) * 1.0
    bear_weight = len(bear_outputs) * 1.0

    # Forensic bears count double
    for bid in bear_ids:
        if _get_engine_category(bid) in ("FORENSIC", "GOVERNANCE"):
            bear_weight += 1.0

    if bear_weight == 0:
        balance = "BULLISH_DOMINANT"
    elif bull_weight == 0:
        balance = "BEARISH_DOMINANT"
    elif bull_weight >= bear_weight * 2:
        balance = "BULLISH_DOMINANT"
    elif bear_weight >= bull_weight * 2:
        balance = "BEARISH_DOMINANT"
    else:
        balance = "CONTESTED"

    # ── Key contradiction summary ──────────────────────────────────────────
    if bull_case and bear_case:
        bull_cats = list({_get_engine_category(b["engine_id"]) for b in bull_case})
        bear_cats = list({_get_engine_category(b["engine_id"]) for b in bear_case})
        key_contradiction = (
            f"Conflict: {', '.join(bull_cats)} engines BULLISH vs "
            f"{', '.join(bear_cats)} engines BEARISH. "
            f"Severity: {severity}."
        )
        decision_impact = (
            "Conviction score penalized for contradiction. "
            f"Forensic/governance flags take precedence over fundamental signals."
            if severity in ("HIGH", "CRITICAL")
            else "Mixed signals — wait for convergence before increasing position size."
        )
    elif bear_case:
        key_contradiction = f"All active engines flagged risks: {', '.join(bear_ids)}."
        decision_impact = "Avoid or reduce position."
    else:
        key_contradiction = None
        decision_impact = "Consensus positive signals across all engines."

    # ── Falsification conditions ───────────────────────────────────────────
    falsification_conditions = _generate_falsification_conditions(
        symbol, engine_outputs, macro_regime
    )

    return ContradictionReport(
        symbol=symbol,
        primary_positives=bull_ids,
        primary_negatives=bear_ids,
        key_contradiction=key_contradiction,
        decision_impact=decision_impact,
        bull_case=bull_case,
        bear_case=bear_case,
        falsification_conditions=falsification_conditions,
        contradiction_severity=severity,
        net_evidence_balance=balance,
    )
