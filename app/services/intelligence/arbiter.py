"""Virtual IC Arbiter — Rule-Based Score Synthesis Engine.

Converts structured sub-agent findings into deterministic quantitative penalties/bonuses.
Strictly adheres to Pipeline Law: No raw LLM % score shifts; penalties are computed by deterministic rules.
"""

from typing import Any, Dict, List
from app.services.intelligence.event_extractor import FindingSeverity, SubAgentAuditReport


class VirtualICArbiter:
    """Synthesizes sub-agent audit reports into deterministic quantitative adjustments."""

    SEVERITY_WEIGHTS: Dict[FindingSeverity, float] = {
        FindingSeverity.CRITICAL_RED_FLAG: -30.0,
        FindingSeverity.HIGH_PENALTY: -15.0,
        FindingSeverity.MODERATE_RISK: -5.0,
        FindingSeverity.NEUTRAL_OBSERVATION: 0.0,
        FindingSeverity.POSITIVE_CATALYST: 5.0,
    }

    def synthesize(self, reports: List[SubAgentAuditReport], base_score: float) -> Dict[str, Any]:
        """Synthesize sub-agent reports into deterministic score adjustments.

        Returns:
            Dict containing base_score, net_adjustment, adjusted_score, is_halted, and findings.
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

        adjusted_score = max(0.0, min(100.0, base_score + net_adjustment))

        return {
            "base_score": base_score,
            "net_adjustment": round(net_adjustment, 2),
            "adjusted_score": round(adjusted_score, 2),
            "is_halted": has_critical_red_flag,
            "findings_summary": findings_summary,
            "invalidation_triggers": invalidation_triggers,
        }
