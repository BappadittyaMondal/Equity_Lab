"""Governance & Forensic Red-Flag Veto Engine.

Performs forensic accounting audits to detect governance anomalies, earnings manipulation,
auditor resignations, related-party transaction red flags, and share dilution velocity
before capital commitment.

Phase 135 Enhancement: Compound Annual Dilution Rate (CADR) Gate
- Warrant/Preferential allotments CADR >= 5%/yr → Tier 2 Objective Block for EARLY_MICROCAP
- Rights/QIP for genuine capacity expansion CADR >= 12%/yr → Tier 3 Contextual Caution
- Differentiates dilution TYPE: extraction (warrants) vs structural expansion (rights/QIP)
- Non-circular: additive to F13 (historical drag computation). F13 measures EPS drag;
  CADR gate measures forward velocity with archetype-conditional severity.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


# ---------------------------------------------------------------------------
# CADR Sovereign Sector Keywords — used to classify dilution instrument type
# ---------------------------------------------------------------------------
_EXPANSION_DILUTION_KEYWORDS = frozenset([
    "rights issue", "rights entitlement", "rights shares",
    "qip", "qualified institutional placement",
    "fpo", "follow-on public offer",
    "preferential allotment for capex", "preferential allotment for expansion",
])

_EXTRACTION_DILUTION_KEYWORDS = frozenset([
    "warrants", "convertible warrants", "preferential warrants",
    "esop", "employee stock option", "stock option plan",
    "preferential allotment", "preferential issue",
])

# CADR threshold constants (% per year)
_CADR_WARRANT_BLOCK_THRESHOLD = 0.05   # 5% p.a. → Tier 2 Objective Block (EARLY_MICROCAP)
_CADR_EXPANSION_CAUTION_THRESHOLD = 0.12  # 12% p.a. → Tier 3 Contextual Caution (all archetypes)


@dataclass
class CADRResult:
    """Compound Annual Dilution Rate (CADR) forensic result."""
    cadr: Optional[float]              # annualised dilution rate (0.0–1.0+), or None if data absent
    dilution_type: str                 # "WARRANT_EXTRACTION" | "EXPANSION_CAPITAL" | "MIXED" | "UNKNOWN"
    shares_t0: Optional[float]         # share count 3 years ago
    shares_t1: Optional[float]         # share count latest
    years: float                       # lookback window used (typically 3.0)
    severity: str                      # "TIER2_OBJECTIVE_BLOCK" | "TIER3_CONTEXTUAL_CAUTION" | "CLEAN" | "DATA_ABSENT"
    flag_message: Optional[str]        # human-readable flag or None


def compute_cadr(
    shares_latest: Optional[float],
    shares_3y_ago: Optional[float],
    dilution_instrument_hint: Optional[str] = None,
    archetype: str = "GENERAL",
    years: float = 3.0,
) -> CADRResult:
    """Compute CADR and classify severity with dilution-type branching.

    Args:
        shares_latest: Current total shares outstanding (any unit).
        shares_3y_ago: Shares outstanding 3 years prior (same unit).
        dilution_instrument_hint: Free-text hint from annual report / BSE filing
            (e.g. "preferential warrants to promoters", "QIP for capex").
        archetype: Strategy archetype string (e.g. "EARLY_MICROCAP", "MULTIBAGGER").
        years: Lookback window used (default 3.0).

    Returns:
        CADRResult with severity classification.
    """
    if shares_latest is None or shares_3y_ago is None or shares_3y_ago <= 0:
        return CADRResult(
            cadr=None, dilution_type="UNKNOWN",
            shares_t0=shares_3y_ago, shares_t1=shares_latest, years=years,
            severity="DATA_ABSENT",
            flag_message="CADR: Share count data absent; dilution velocity unverifiable.",
        )

    cadr = (shares_latest / shares_3y_ago) ** (1.0 / years) - 1.0

    if cadr <= 0.0:
        # Net share reduction (buyback) — positive signal, no flag
        return CADRResult(
            cadr=round(cadr, 4), dilution_type="UNKNOWN",
            shares_t0=shares_3y_ago, shares_t1=shares_latest, years=years,
            severity="CLEAN",
            flag_message=None,
        )

    # --- Classify dilution instrument type ---
    hint_lower = (dilution_instrument_hint or "").lower()
    is_extraction = any(k in hint_lower for k in _EXTRACTION_DILUTION_KEYWORDS)
    is_expansion = any(k in hint_lower for k in _EXPANSION_DILUTION_KEYWORDS)

    if is_expansion and not is_extraction:
        dilution_type = "EXPANSION_CAPITAL"
        effective_threshold = _CADR_EXPANSION_CAUTION_THRESHOLD
        block_severity = "TIER3_CONTEXTUAL_CAUTION"
    elif hint_lower and not is_expansion:
        dilution_type = "WARRANT_EXTRACTION"
        effective_threshold = _CADR_WARRANT_BLOCK_THRESHOLD
        block_severity = "TIER2_OBJECTIVE_BLOCK"
    elif is_extraction and is_expansion:
        # Mixed — apply stricter warrant threshold
        dilution_type = "MIXED"
        effective_threshold = _CADR_WARRANT_BLOCK_THRESHOLD
        block_severity = "TIER2_OBJECTIVE_BLOCK"
    else:
        # Hint absent — default conservative: treat as WARRANT_EXTRACTION if archetype is EARLY_MICROCAP
        dilution_type = "UNKNOWN"
        if archetype.upper() in ("EARLY_MICROCAP", "MULTIBAGGER"):
            effective_threshold = _CADR_WARRANT_BLOCK_THRESHOLD
            block_severity = "TIER2_OBJECTIVE_BLOCK"
        else:
            effective_threshold = _CADR_EXPANSION_CAUTION_THRESHOLD
            block_severity = "TIER3_CONTEXTUAL_CAUTION"

    cadr_pct = round(cadr * 100.0, 2)

    if cadr < effective_threshold:
        return CADRResult(
            cadr=round(cadr, 4), dilution_type=dilution_type,
            shares_t0=shares_3y_ago, shares_t1=shares_latest, years=years,
            severity="CLEAN",
            flag_message=None,
        )

    # Threshold breached — compute flag message
    threshold_pct = round(effective_threshold * 100.0, 1)
    if block_severity == "TIER2_OBJECTIVE_BLOCK":
        msg = (
            f"CADR DILUTION VELOCITY BLOCK ({dilution_type}): "
            f"3Y CADR={cadr_pct:.2f}% >= {threshold_pct}% p.a. threshold. "
            f"Shares grew from {shares_3y_ago:,.0f} to {shares_latest:,.0f} "
            f"over {years:.0f}Y via {dilution_type.lower().replace('_', ' ')}. "
            f"EPS compounding structurally impaired; Tier 2 Objective Block for EARLY_MICROCAP archetype."
        )
    else:
        msg = (
            f"CADR DILUTION CAUTION ({dilution_type}): "
            f"3Y CADR={cadr_pct:.2f}% >= {threshold_pct}% p.a. threshold. "
            f"Shares grew from {shares_3y_ago:,.0f} to {shares_latest:,.0f} "
            f"over {years:.0f}Y. Verify that capex-linked equity expansion "
            f"translates to proportional ROIC and EPS accretion."
        )

    return CADRResult(
        cadr=round(cadr, 4), dilution_type=dilution_type,
        shares_t0=shares_3y_ago, shares_t1=shares_latest, years=years,
        severity=block_severity,
        flag_message=msg,
    )


@dataclass
class ForensicAuditResult:
    symbol: str
    forensic_score: float  # 0 to 100
    governance_veto: bool
    auditor_qualification_flag: bool
    related_party_revenue_pct: float
    cash_accrual_divergence_flag: bool
    m_score: Optional[float] = None
    z_score: Optional[float] = None
    red_flags: List[str] = field(default_factory=list)
    data_mode: str = "OBSERVED"  # "OBSERVED" | "PARTIAL_DATA" | "INSUFFICIENT_DATA" | "MOCK"
    confidence_score: float = 1.0
    missing_metrics: List[str] = field(default_factory=list)
    cadr_result: Optional[CADRResult] = None   # Phase 135: CADR gate result


class ForensicAuditor:
    """Forensic accounting and governance auditor."""

    def audit_equity(
        self,
        symbol: str,
        related_party_pct: Optional[float] = None,
        auditor_resigned_recently: Optional[bool] = None,
        net_income_3y_cagr: Optional[float] = None,
        ocf_3y_cagr: Optional[float] = None,
        is_mock: bool = False,
        # Phase 135: CADR parameters
        shares_latest: Optional[float] = None,
        shares_3y_ago: Optional[float] = None,
        dilution_instrument_hint: Optional[str] = None,
        archetype: str = "GENERAL",
    ) -> ForensicAuditResult:
        """Perform comprehensive forensic audit on an equity without silent default assumptions.

        Phase 135 Additions:
            shares_latest: Current total shares outstanding (any unit).
            shares_3y_ago: Shares outstanding 3 years prior (same unit).
            dilution_instrument_hint: Free-text describing dilution instrument (warrants, QIP, rights).
            archetype: Investment archetype to calibrate CADR severity.
        """
        # Attempt to populate missing parameters from canonical ResearchDataStore timeline
        if related_party_pct is None or auditor_resigned_recently is None or net_income_3y_cagr is None or ocf_3y_cagr is None:
            try:
                from app.services.research_data import ResearchDataStore
                timeline = ResearchDataStore().get_timeline(symbol)
                for obs in timeline.financial_observations:
                    if related_party_pct is None and obs.metric == "related_party_pct":
                        related_party_pct = float(obs.value)
                    elif net_income_3y_cagr is None and obs.metric == "net_income_3y_cagr":
                        net_income_3y_cagr = float(obs.value)
                    elif ocf_3y_cagr is None and obs.metric == "ocf_3y_cagr":
                        ocf_3y_cagr = float(obs.value)
                    # Phase 135: pull share count data from timeline if not provided
                    elif shares_latest is None and obs.metric in ("shares_outstanding", "total_shares"):
                        shares_latest = float(obs.value)
                    elif shares_3y_ago is None and obs.metric in ("shares_outstanding_3y", "shares_3y_ago"):
                        shares_3y_ago = float(obs.value)
                for ev in timeline.events:
                    if auditor_resigned_recently is None and getattr(ev, "event_type", None) == "auditor_resignation":
                        auditor_resigned_recently = True
            except Exception:
                pass

        # Compute Beneish M-Score & Altman Z-Score from forensic_engine if available
        m_score = None
        z_score = None
        try:
            from app.services.strategies.forensic_engine import run_forensic_engine
            forensic_res = run_forensic_engine(symbol)
            m_score = forensic_res.metrics.get("m_score")
            z_score = forensic_res.metrics.get("z_score")
        except Exception:
            pass

        missing_metrics = []
        if related_party_pct is None:
            missing_metrics.append("related_party_pct")
        if auditor_resigned_recently is None:
            missing_metrics.append("auditor_resigned_recently")
        if net_income_3y_cagr is None:
            missing_metrics.append("net_income_3y_cagr")
        if ocf_3y_cagr is None:
            missing_metrics.append("ocf_3y_cagr")

        if is_mock:
            data_mode = "MOCK"
        elif len(missing_metrics) == 4 and m_score is None and z_score is None:
            data_mode = "INSUFFICIENT_DATA"
        elif len(missing_metrics) > 0:
            data_mode = "PARTIAL_DATA"
        else:
            data_mode = "OBSERVED"

        provided_count = 4 - len(missing_metrics)
        confidence_score = round(provided_count / 4.0, 2)

        red_flags = []
        score = 100.0

        if data_mode == "INSUFFICIENT_DATA":
            score = 50.0
            red_flags.append("INSUFFICIENT_DATA: Missing forensic accounting metrics (related_party_pct, auditor_resigned_recently, net_income_3y_cagr, ocf_3y_cagr).")
            governance_veto = False
        else:
            # 1. Auditor Resignation Veto
            if auditor_resigned_recently is True:
                score -= 40.0
                red_flags.append("Statutory auditor resigned prematurely prior to annual audit completion.")

            # 2. Related Party Transactions (>15% Revenue Veto)
            if related_party_pct is not None and related_party_pct > 15.0:
                score -= 30.0
                red_flags.append(f"Related-party transactions ({related_party_pct:.1f}%) exceed 15% revenue threshold.")

            # 3. Cash vs Accrual Divergence (Earnings manipulation check)
            if net_income_3y_cagr is not None and ocf_3y_cagr is not None:
                if net_income_3y_cagr > 10.0 and ocf_3y_cagr < 0.0:
                    score -= 35.0
                    red_flags.append("Severe Cash-Accrual Divergence: Net profit expanding while OCF is negative.")

            # 4. Beneish M-Score Manipulation Veto (> -1.78)
            if m_score is not None and m_score > -1.78:
                score -= 30.0
                red_flags.append(f"Beneish M-Score ({m_score:.2f}) > -1.78 threshold: Earnings manipulation risk detected.")

            # 5. Altman Z-Score Distress Warning (< 1.81)
            if z_score is not None and z_score < 1.81:
                score -= 30.0
                red_flags.append(f"Altman Z-Score ({z_score:.2f}) < 1.81 threshold: Corporate financial distress risk detected.")

            score = max(0.0, score)
            governance_veto = score < 60.0 or bool(auditor_resigned_recently) or (m_score is not None and m_score > -1.78) or (z_score is not None and z_score < 1.81)

        # 6. Phase 135: CADR Dilution Velocity Gate (additive to F13 drag; non-circular)
        cadr_result = compute_cadr(
            shares_latest=shares_latest,
            shares_3y_ago=shares_3y_ago,
            dilution_instrument_hint=dilution_instrument_hint,
            archetype=archetype,
            years=3.0,
        )
        if cadr_result.severity == "TIER2_OBJECTIVE_BLOCK" and cadr_result.flag_message:
            # Only penalise score for extraction-type dilution; expansion capital gets caution only
            score = max(0.0, score - 20.0)
            red_flags.append(cadr_result.flag_message)
        elif cadr_result.severity == "TIER3_CONTEXTUAL_CAUTION" and cadr_result.flag_message:
            # No score penalty — contextual advisory only
            red_flags.append(f"[CAUTION] {cadr_result.flag_message}")

        divergence = bool(
            net_income_3y_cagr is not None and ocf_3y_cagr is not None and
            net_income_3y_cagr > 10.0 and ocf_3y_cagr < 0.0
        )

        return ForensicAuditResult(
            symbol=symbol.upper(),
            forensic_score=round(score, 1),
            governance_veto=governance_veto,
            auditor_qualification_flag=bool(auditor_resigned_recently),
            related_party_revenue_pct=float(related_party_pct or 0.0),
            cash_accrual_divergence_flag=divergence,
            m_score=m_score,
            z_score=z_score,
            red_flags=red_flags,
            data_mode=data_mode,
            confidence_score=confidence_score,
            missing_metrics=missing_metrics,
            cadr_result=cadr_result,
        )
