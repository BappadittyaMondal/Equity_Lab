"""Governance & Forensic Red-Flag Veto Engine.

Performs forensic accounting audits to detect governance anomalies, earnings manipulation,
auditor resignations, and related-party transaction red flags before capital commitment.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ForensicAuditResult:
    symbol: str
    forensic_score: float  # 0 to 100
    governance_veto: bool
    auditor_qualification_flag: bool
    related_party_revenue_pct: float
    cash_accrual_divergence_flag: bool
    red_flags: List[str] = field(default_factory=list)
    data_mode: str = "OBSERVED"  # "OBSERVED" | "PARTIAL_DATA" | "INSUFFICIENT_DATA" | "MOCK"
    confidence_score: float = 1.0
    missing_metrics: List[str] = field(default_factory=list)


class ForensicAuditor:
    """Forensic accounting and governance auditor."""

    def audit_equity(
        self,
        symbol: str,
        related_party_pct: Optional[float] = None,
        auditor_resigned_recently: Optional[bool] = None,
        net_income_3y_cagr: Optional[float] = None,
        ocf_3y_cagr: Optional[float] = None,
        is_mock: bool = False
    ) -> ForensicAuditResult:
        """Perform comprehensive forensic audit on an equity without silent default assumptions."""
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
                for ev in timeline.events:
                    if auditor_resigned_recently is None and getattr(ev, "event_type", None) == "auditor_resignation":
                        auditor_resigned_recently = True
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
        elif len(missing_metrics) == 4:
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

            score = max(0.0, score)
            governance_veto = score < 60.0 or bool(auditor_resigned_recently)

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
            red_flags=red_flags,
            data_mode=data_mode,
            confidence_score=confidence_score,
            missing_metrics=missing_metrics,
        )

