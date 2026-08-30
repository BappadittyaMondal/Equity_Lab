"""Virtual IC Arbiter — Rule-Based Score Synthesis Engine.

Converts structured sub-agent findings into deterministic quantitative penalties/bonuses.
Strictly adheres to Pipeline Law: No raw LLM % score shifts; penalties are computed by deterministic rules.
"""

from typing import Any, Dict, List, Optional
import numpy as np

from app.services.intelligence.event_extractor import FindingSeverity, SubAgentAuditReport
from app.services.intelligence.financial_forensics import FinancialForensicsEngine
from app.services.ml.evt_gpd_engine import EVTGPDEngine


class VirtualICArbiter:
    """Synthesizes sub-agent audit reports, financial forensics, and EVT tail metrics into deterministic quantitative adjustments."""

    SEVERITY_WEIGHTS: Dict[FindingSeverity, float] = {
        FindingSeverity.CRITICAL_RED_FLAG: -30.0,
        FindingSeverity.HIGH_PENALTY: -15.0,
        FindingSeverity.MODERATE_RISK: -5.0,
        FindingSeverity.NEUTRAL_OBSERVATION: 0.0,
        FindingSeverity.POSITIVE_CATALYST: 5.0,
    }

    def synthesize(
        self,
        reports: List[SubAgentAuditReport],
        base_score: float,
        financials_data: Optional[Dict[str, Any]] = None,
        return_series: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """Synthesize sub-agent reports, balance sheet forensics, and EVT tail metrics into deterministic score adjustments.

        Returns:
            Dict containing base_score, net_adjustment, adjusted_score, is_halted, findings, and forensic/evt metrics.
        """
        has_critical_red_flag = False
        net_adjustment = 0.0
        findings_summary = []
        invalidation_triggers = []

        for report in reports:
            for finding in report.findings:
                adj = self.SEVERITY_WEIGHTS.get(finding.severity, 0.0)
                net_adjustment += adj * finding.confidence
                if finding.severity == FindingSeverity.CRITICAL_RED_FLAG:
                    has_critical_red_flag = True

                findings_summary.append({
                    "agent": report.agent_name,
                    "finding": finding.finding,
                    "severity": finding.severity.value,
                    "adjustment_applied": round(adj * finding.confidence, 2),
                })
                if finding.thesis_invalidation_trigger:
                    invalidation_triggers.append(finding.thesis_invalidation_trigger)

        # 1. Integrate Financial Forensics Engine
        forensic_res = FinancialForensicsEngine.analyze_company_forensics(financials_data) if financials_data else None
        if forensic_res:
            if forensic_res.get("forensic_risk_level") == "HIGH_FRAUD_RISK":
                has_critical_red_flag = True
                net_adjustment -= 25.0
            elif forensic_res.get("forensic_risk_level") == "ELEVATED_MONITOR":
                net_adjustment -= 10.0

        # 2. Integrate EVT GPD Engine
        evt_res = EVTGPDEngine.fit_gpd_tail_exceedances(return_series) if return_series is not None else None

        adjusted_score = max(0.0, min(100.0, base_score + net_adjustment))

        return {
            "base_score": base_score,
            "net_adjustment": round(net_adjustment, 2),
            "adjusted_score": round(adjusted_score, 2),
            "is_halted": has_critical_red_flag,
            "findings_summary": findings_summary,
            "invalidation_triggers": invalidation_triggers,
            "forensic_audit": forensic_res,
            "evt_tail_metrics": evt_res,
        }
