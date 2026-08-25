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


class ForensicAuditor:
    """Forensic accounting and governance auditor."""

    def audit_equity(
        self,
        symbol: str,
        related_party_pct: float = 5.0,
        auditor_resigned_recently: bool = False,
        net_income_3y_cagr: float = 15.0,
        ocf_3y_cagr: float = 18.0
    ) -> ForensicAuditResult:
        """Perform comprehensive forensic audit on an equity."""
        red_flags = []
        score = 100.0

        # 1. Auditor Resignation Veto
        if auditor_resigned_recently:
            score -= 40.0
            red_flags.append("Statutory auditor resigned prematurely prior to annual audit completion.")

        # 2. Related Party Transactions (>15% Revenue Veto)
        if related_party_pct > 15.0:
            score -= 30.0
            red_flags.append(f"Related-party transactions ({related_party_pct:.1f}%) exceed 15% revenue threshold.")

        # 3. Cash vs Accrual Divergence (Earnings manipulation check)
        divergence = False
        if net_income_3y_cagr > 10.0 and ocf_3y_cagr < 0.0:
            divergence = True
            score -= 35.0
            red_flags.append("Severe Cash-Accrual Divergence: Net profit expanding while OCF is negative.")

        score = max(0.0, score)
        governance_veto = score < 60.0 or auditor_resigned_recently

        return ForensicAuditResult(
            symbol=symbol.upper(),
            forensic_score=round(score, 1),
            governance_veto=governance_veto,
            auditor_qualification_flag=auditor_resigned_recently,
            related_party_revenue_pct=related_party_pct,
            cash_accrual_divergence_flag=divergence,
            red_flags=red_flags
        )
