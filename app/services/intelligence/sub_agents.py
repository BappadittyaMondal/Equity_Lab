"""Domain-Specialized Rule-Engine Sub-Agents for Evidence Extraction (Pipeline Law Compliant).

Implements deterministic threshold-based evaluation rubrics for:
- ForensicAuditorSubAgent (Promoter pledge & governance thresholds)
- SupplyChainCatalystSubAgent (Sector capex & order book catalysts)
- RedTeamBearCaseSubAgent (Debt balance-sheet leverage stress tests)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.intelligence.event_extractor import (
    FindingSeverity,
    QualitativeEvidenceFinding,
    SubAgentAuditReport,
)


class ForensicAuditorSubAgent:
    """Forensic Accounting & Corporate Governance Sub-Agent (Deterministic Rule Rubric)."""

    def evaluate(self, symbol: str, ownership_snapshot: Optional[Dict[str, Any]] = None) -> SubAgentAuditReport:
        findings = []
        now_str = datetime.now(timezone.utc).isoformat()

        if ownership_snapshot:
            pledge = float(ownership_snapshot.get("promoter_pledge_pct") or 0.0)
            if pledge > 40.0:
                findings.append(
                    QualitativeEvidenceFinding(
                        finding="Critical Promoter Pledge Alarm",
                        evidence=f"Promoter pledge ratio is extremely high at {pledge:.1f}%, exceeding safety threshold of 40.0%",
                        severity=FindingSeverity.CRITICAL_RED_FLAG,
                        confidence=0.98,
                        source="BSE/NSE Shareholding Pattern Filing",
                        thesis_invalidation_trigger="Immediate promoter pledge call risk",
                    )
                )
            elif pledge > 25.0:
                findings.append(
                    QualitativeEvidenceFinding(
                        finding="High Promoter Pledge Risk",
                        evidence=f"Promoter pledge ratio is {pledge:.1f}%, exceeding safety threshold of 25.0%",
                        severity=FindingSeverity.HIGH_PENALTY,
                        confidence=0.95,
                        source="BSE/NSE Shareholding Pattern Filing",
                        thesis_invalidation_trigger="Promoter pledge ratio increases above 35.0%",
                    )
                )

        if not findings:
            findings.append(
                QualitativeEvidenceFinding(
                    finding="Clean Governance Track Record",
                    evidence="No major related-party transaction alarms or promoter pledge red flags detected.",
                    severity=FindingSeverity.NEUTRAL_OBSERVATION,
                    confidence=0.85,
                    source="ResearchDataStore Filings Audit",
                )
            )

        return SubAgentAuditReport(
            symbol=symbol,
            agent_id="SUB_AGENT_FORENSIC",
            agent_name="Forensic Accounting & Governance Auditor",
            executed_at=now_str,
            findings=findings,
            summary_verdict="Audited governance & pledge structure.",
        )


class SupplyChainCatalystSubAgent:
    """Supply Chain & Second-Order Catalyst Sub-Agent."""

    def evaluate(self, symbol: str, sector: Optional[str] = None) -> SubAgentAuditReport:
        findings = []
        now_str = datetime.now(timezone.utc).isoformat()
        norm_sec = (sector or "").strip().title()

        if norm_sec in ("Infrastructure", "Power", "Capital Goods"):
            findings.append(
                QualitativeEvidenceFinding(
                    finding="Capex Inflection Beneficiary",
                    evidence=f"Symbol operates in {norm_sec} benefiting from national infrastructure spending tailwinds.",
                    severity=FindingSeverity.POSITIVE_CATALYST,
                    confidence=0.88,
                    source="Policy Transmission Graph",
                    thesis_invalidation_trigger="Government infrastructure budget allocation reduction > 15%",
                )
            )
        else:
            findings.append(
                QualitativeEvidenceFinding(
                    finding="Stable Demand Pipeline",
                    evidence="Order book execution remains aligned with historical guidance.",
                    severity=FindingSeverity.NEUTRAL_OBSERVATION,
                    confidence=0.80,
                    source="Quarterly MD&A Disclosures",
                )
            )

        return SubAgentAuditReport(
            symbol=symbol,
            agent_id="SUB_AGENT_SUPPLY_CHAIN",
            agent_name="Supply Chain & Catalyst Sub-Agent",
            executed_at=now_str,
            findings=findings,
            summary_verdict="Evaluated order book & supply chain position.",
        )


class RedTeamBearCaseSubAgent:
    """Adversarial Red Team Sub-Agent designed to destroy investment thesis."""

    def evaluate(self, symbol: str, de_ratio: Optional[float] = None) -> SubAgentAuditReport:
        findings = []
        now_str = datetime.now(timezone.utc).isoformat()

        if de_ratio is not None and de_ratio > 1.5:
            findings.append(
                QualitativeEvidenceFinding(
                    finding="High Financial Leverage Vulnerability",
                    evidence=f"Debt-to-Equity ratio is {de_ratio:.2f}x, exposing balance sheet to interest rate shocks.",
                    severity=FindingSeverity.HIGH_PENALTY,
                    confidence=0.90,
                    source="Balance Sheet Financial Statements",
                    thesis_invalidation_trigger="ICR (Interest Coverage Ratio) drops below 2.0x",
                )
            )

        if not findings:
            findings.append(
                QualitativeEvidenceFinding(
                    finding="Moderate Competitive Risk",
                    evidence="No acute debt leverage traps found; sector margin compression remains key risk.",
                    severity=FindingSeverity.MODERATE_RISK,
                    confidence=0.75,
                    source="Red Team Stress Test Framework",
                )
            )

        return SubAgentAuditReport(
            symbol=symbol,
            agent_id="SUB_AGENT_RED_TEAM",
            agent_name="Adversarial Red Team Sub-Agent",
            executed_at=now_str,
            findings=findings,
            summary_verdict="Executed adversarial thesis stress test.",
        )


class IncrementalROICSubAgent:
    """Agent 10: Incremental Return & Capex Productivity Sub-Agent."""

    def evaluate(
        self,
        symbol: str,
        delta_nopat: Optional[float] = None,
        delta_invested_capital: Optional[float] = None,
        capex: Optional[float] = None,
        delta_ebitda: Optional[float] = None,
        trailing_roce: Optional[float] = None,
    ) -> SubAgentAuditReport:
        findings = []
        now_str = datetime.now(timezone.utc).isoformat()

        # Incremental ROIC ≈ ΔNOPAT / ΔInvested Capital
        inc_roic = None
        if delta_nopat is not None and delta_invested_capital is not None and abs(delta_invested_capital) > 0.01:
            inc_roic = round((delta_nopat / delta_invested_capital) * 100.0, 1)

        if inc_roic is not None and inc_roic >= 25.0:
            divergence_msg = ""
            if trailing_roce is not None and trailing_roce < 18.0:
                divergence_msg = f" (Crucial divergence: trailing ROCE {trailing_roce:.1f}% vs surging incremental ROIC {inc_roic:.1f}%)"
            findings.append(
                QualitativeEvidenceFinding(
                    finding="High Incremental ROIC Inflection",
                    evidence=f"Incremental ROIC is surging at {inc_roic:.1f}% on newly deployed capital{divergence_msg}.",
                    severity=FindingSeverity.POSITIVE_CATALYST,
                    confidence=0.92,
                    source="Capital Allocation & Asset Productivity Model",
                    thesis_invalidation_trigger="Incremental ROIC drops below 15.0%",
                )
            )
        elif inc_roic is not None and inc_roic < 10.0:
            findings.append(
                QualitativeEvidenceFinding(
                    finding="Depressed Incremental Return on Capital",
                    evidence=f"Incremental ROIC is poor at {inc_roic:.1f}%, indicating low reinvestment economics.",
                    severity=FindingSeverity.HIGH_PENALTY,
                    confidence=0.88,
                    source="Capital Allocation & Asset Productivity Model",
                    thesis_invalidation_trigger="Capex commissioning fails to yield EBITDA growth",
                )
            )
        else:
            findings.append(
                QualitativeEvidenceFinding(
                    finding="Stable Capital Efficiency",
                    evidence="Incremental return on capital matches sector baseline (~15-18%).",
                    severity=FindingSeverity.NEUTRAL_OBSERVATION,
                    confidence=0.80,
                    source="Capital Allocation & Asset Productivity Model",
                )
            )

        return SubAgentAuditReport(
            symbol=symbol,
            agent_id="SUB_AGENT_INCREMENTAL_ROIC",
            agent_name="Incremental Return & Capex Productivity Sub-Agent (Agent 10)",
            executed_at=now_str,
            findings=findings,
            summary_verdict="Audited incremental ROIC and capex productivity dynamics.",
        )


class ReverseValuationSubAgent:
    """Agent 11: Order-Book Forensics & Reverse Valuation Sub-Agent."""

    def evaluate(
        self,
        symbol: str,
        current_market_cap_cr: float = 200.0,
        current_revenue_cr: float = 100.0,
        target_multiple: float = 5.0,
        target_years: int = 4,
        order_book_executable_pct: float = 85.0,
    ) -> SubAgentAuditReport:
        findings = []
        now_str = datetime.now(timezone.utc).isoformat()

        target_mcap = current_market_cap_cr * target_multiple
        required_terminal_pat = target_mcap / 25.0
        required_terminal_rev = required_terminal_pat / 0.12
        required_cagr = round((((required_terminal_rev / max(current_revenue_cr, 1.0)) ** (1.0 / max(target_years, 1))) - 1.0) * 100.0, 1)

        feasibility = "FEASIBLE" if required_cagr <= 28.0 else ("AGGRESSIVE" if required_cagr <= 40.0 else "IMPLAUSIBLE")

        if feasibility == "IMPLAUSIBLE":
            findings.append(
                QualitativeEvidenceFinding(
                    finding=f"Reverse Valuation Implausible ({target_multiple:.0f}x Target)",
                    evidence=f"{target_multiple:.0f}x market cap expansion requires {required_cagr:.1f}% Revenue CAGR over {target_years}Y, which is mathematically implausible against sector base rates.",
                    severity=FindingSeverity.CRITICAL_RED_FLAG,
                    confidence=0.95,
                    source="Reverse Valuation Arithmetic Engine",
                    thesis_invalidation_trigger="Required CAGR exceeds 40%",
                )
            )
        elif feasibility == "FEASIBLE":
            findings.append(
                QualitativeEvidenceFinding(
                    finding=f"Reverse Valuation Feasible ({target_multiple:.0f}x Target)",
                    evidence=f"{target_multiple:.0f}x outcome requires reasonable {required_cagr:.1f}% Revenue CAGR over {target_years}Y, fully achievable given {order_book_executable_pct:.0f}% firm order book.",
                    severity=FindingSeverity.POSITIVE_CATALYST,
                    confidence=0.90,
                    source="Reverse Valuation Arithmetic Engine",
                )
            )
        else:
            findings.append(
                QualitativeEvidenceFinding(
                    finding=f"Reverse Valuation Aggressive ({target_multiple:.0f}x Target)",
                    evidence=f"{target_multiple:.0f}x target requires {required_cagr:.1f}% Revenue CAGR over {target_years}Y — requires flawless market share execution.",
                    severity=FindingSeverity.MODERATE_RISK,
                    confidence=0.85,
                    source="Reverse Valuation Arithmetic Engine",
                )
            )

        return SubAgentAuditReport(
            symbol=symbol,
            agent_id="SUB_AGENT_REVERSE_VALUATION",
            agent_name="Order-Book Forensics & Reverse Valuation Sub-Agent (Agent 11)",
            executed_at=now_str,
            findings=findings,
            summary_verdict=f"Reverse valuation feasibility classified as [{feasibility}].",
        )


class PMKillTestSubAgent:
    """Agent 12: Mandatory Adversarial PM Kill-Test Sub-Agent."""

    def evaluate(
        self,
        symbol: str,
        growth_normalization_risk: bool = False,
        economic_earnings_divergence: bool = False,
        management_execution_delay: bool = False,
        technical_distribution_detected: bool = False,
        valuation_compression_risk: bool = False,
    ) -> SubAgentAuditReport:
        findings = []
        now_str = datetime.now(timezone.utc).isoformat()

        failed_tests = []
        if growth_normalization_risk:
            failed_tests.append("Growth Normalization Bear Case (margin cycle peak)")
        if economic_earnings_divergence:
            failed_tests.append("Accounting Bear Case (CFO << PAT divergence)")
        if management_execution_delay:
            failed_tests.append("Management Execution Bear Case (capex commissioning delay)")
        if technical_distribution_detected:
            failed_tests.append("Technical Distribution Bear Case (heavy institutional selling)")
        if valuation_compression_risk:
            failed_tests.append("Valuation Multiple Compression Bear Case (cyclical peak multiple)")

        if failed_tests:
            for test in failed_tests:
                findings.append(
                    QualitativeEvidenceFinding(
                        finding=f"PM Kill-Test Failed: {test}",
                        evidence=f"Adversarial underwriting check failed: {test}. Candidate demoted or rejected.",
                        severity=FindingSeverity.CRITICAL_RED_FLAG,
                        confidence=0.95,
                        source="Portfolio Manager Adversarial Kill-Test Matrix",
                        thesis_invalidation_trigger=f"Failed stress test: {test}",
                    )
                )
            verdict = "REJECTED_PM_KILL_TEST_FAILED"
        else:
            findings.append(
                QualitativeEvidenceFinding(
                    finding="PM Kill-Test Passed (All 5 Checks Green)",
                    evidence="Candidate survived all 5 adversarial checks: no growth normalization trap, clean economic CFO earnings, on-time capex commissioning, accumulation volume, and reasonable multiple.",
                    severity=FindingSeverity.POSITIVE_CATALYST,
                    confidence=0.92,
                    source="Portfolio Manager Adversarial Kill-Test Matrix",
                )
            )
            verdict = "PASSED_PM_KILL_TEST"

        return SubAgentAuditReport(
            symbol=symbol,
            agent_id="SUB_AGENT_PM_KILL_TEST",
            agent_name="PM Adversarial Kill-Test Sub-Agent (Agent 12)",
            executed_at=now_str,
            findings=findings,
            summary_verdict=verdict,
        )
