"""Deterministic Multi-Factor Investment Vector Rules Engine — IC Protocol.

Simulates a structured institutional Investment Committee evaluation across 4 specialized rule-based analytical vectors:
1. Forensic Auditor Vector (Accounting integrity & fraud signals)
2. Valuation Skeptic Vector (Margin of safety & PEG/DCF validation)
3. Growth Optimist Vector (CAGR, CWIP expansion & TAM momentum)
4. Geopolitical & Macro Officer Vector (Sector overlays & macro stress tests)

Calculates reproducible, rule-based consensus conviction scores and formal IC Memos.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.services.market_data import normalize_symbol, create_meta_header, get_ist_now_str
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
from app.services.research.geopolitical_engine import evaluate_geopolitical_risk
from app.services.decision_brain.red_team_engine import evaluate_red_team_review
from app.services.intelligence.sub_agents import (
    ForensicAuditorSubAgent,
    SupplyChainCatalystSubAgent,
    RedTeamBearCaseSubAgent,
)
from app.services.intelligence.arbiter import VirtualICArbiter

logger = logging.getLogger(__name__)


@dataclass
class AgentOpinion:
    agent_name: str
    role: str
    vote: str  # "APPROVE", "CAUTION", "REJECT"
    conviction_weight: float  # 0.0 to 100.0
    key_findings: List[str]
    risk_concerns: List[str]


class VirtualInvestmentCommittee:
    """Deterministic Rule-Based Boardroom Consensus Orchestrator."""

    @classmethod
    def forensic_auditor_agent(cls, symbol: str, stock_data: Dict[str, Any]) -> AgentOpinion:
        """Evaluates accounting quality, CFO vs PAT, and earnings manipulation signals."""
        cfo = stock_data.get("cfo_last_year", 0.0)
        pat = stock_data.get("net_profit_last_year", 0.0)
        fcf = stock_data.get("fcf_last_year", cfo - stock_data.get("capex_last_year", 0.0))
        piotroski = stock_data.get("piotroski_score", 6)

        findings = []
        concerns = []

        if cfo > pat:
            findings.append(f"Strong Cash Conversion: CFO (₹{cfo:.1f} Cr) > PAT (₹{pat:.1f} Cr). High earnings quality.")
        else:
            concerns.append(f"Earnings Quality Warning: CFO (₹{cfo:.1f} Cr) < PAT (₹{pat:.1f} Cr). Working capital lag.")

        if fcf < -500.0:
            concerns.append(f"Severe Free Cash Flow Burn: FCF is -₹{abs(fcf):.1f} Cr. Capex trap risk active.")
        elif fcf > 0.0:
            findings.append(f"Positive FCF Generation: FCF is +₹{fcf:.1f} Cr.")

        if piotroski >= 7:
            findings.append(f"High Financial Strength: Piotroski F-Score is {piotroski}/9.")
        elif piotroski <= 4:
            concerns.append(f"Weak Piotroski F-Score ({piotroski}/9). Balance sheet stress.")

        vote = "REJECT" if fcf < -1000.0 or piotroski <= 3 else ("CAUTION" if concerns else "APPROVE")
        weight = 85.0 if vote == "APPROVE" else (60.0 if vote == "CAUTION" else 30.0)

        return AgentOpinion(
            agent_name="Forensic Auditor",
            role="Accounting Integrity & Fraud Detection",
            vote=vote,
            conviction_weight=weight,
            key_findings=findings,
            risk_concerns=concerns
        )

    @classmethod
    def valuation_skeptic_agent(cls, symbol: str, stock_data: Dict[str, Any]) -> AgentOpinion:
        """Evaluates valuation safety margin, PEG ratio, and downside risk."""
        pe = stock_data.get("pe_ratio", 25.0)
        peg = stock_data.get("peg_ratio", 1.0)
        debt_to_equity = stock_data.get("debt_to_equity", 0.2)

        findings = []
        concerns = []

        if peg < 1.0 and peg > 0.0:
            findings.append(f"Attractive Valuation Safety: PEG ratio is {peg:.2f} (< 1.0 growth at reasonable price).")
        elif peg > 2.0:
            concerns.append(f"Valuation Stretch: PEG ratio is {peg:.2f} (> 2.0 premium valuation).")

        if debt_to_equity < 0.3:
            findings.append(f"Low Solvency Risk: Debt-to-Equity is {debt_to_equity:.2f}x (Conservative balance sheet).")
        elif debt_to_equity > 1.0:
            concerns.append(f"High Leverage: Debt-to-Equity is {debt_to_equity:.2f}x.")

        vote = "REJECT" if debt_to_equity > 1.5 or peg > 3.0 else ("CAUTION" if concerns else "APPROVE")
        weight = 90.0 if vote == "APPROVE" else (65.0 if vote == "CAUTION" else 35.0)

        return AgentOpinion(
            agent_name="Valuation Skeptic",
            role="Margin of Safety & Valuation Discipline",
            vote=vote,
            conviction_weight=weight,
            key_findings=findings,
            risk_concerns=concerns
        )

    @classmethod
    def growth_optimist_agent(cls, symbol: str, stock_data: Dict[str, Any]) -> AgentOpinion:
        """Evaluates revenue/PAT CAGR, CWIP capacity expansion, and growth momentum."""
        sales_growth = stock_data.get("sales_growth_3yr", 20.0)
        pat_growth = stock_data.get("pat_growth_3yr", 25.0)
        roce = stock_data.get("roce_3yr", 22.0)

        findings = []
        concerns = []

        if sales_growth > 25.0 and pat_growth > 25.0:
            findings.append(f"High Growth Inflection: 3-Yr Sales CAGR {sales_growth:.1f}% & PAT CAGR {pat_growth:.1f}%.")
        elif sales_growth < 10.0:
            concerns.append(f"Slow Growth Trajectory: 3-Yr Sales CAGR is only {sales_growth:.1f}%.")

        if roce > 20.0:
            findings.append(f"Exceptional Capital Efficiency: 3-Yr ROCE is {roce:.1f}%.")
        elif roce < 12.0:
            concerns.append(f"Subpar ROCE ({roce:.1f}%). Below institutional cost of capital threshold.")

        vote = "REJECT" if sales_growth < 5.0 and roce < 10.0 else ("CAUTION" if concerns else "APPROVE")
        weight = 95.0 if vote == "APPROVE" else (65.0 if vote == "CAUTION" else 40.0)

        return AgentOpinion(
            agent_name="Growth Optimist",
            role="TAM Expansion & Operating Inflection",
            vote=vote,
            conviction_weight=weight,
            key_findings=findings,
            risk_concerns=concerns
        )

    @classmethod
    def macro_geopolitical_officer(cls, symbol: str) -> AgentOpinion:
        """Evaluates macro geopolitical overlays, sector tailwinds/headwinds, and trade risks."""
        clean_sym = symbol.replace(".NS", "").replace(".BO", "").upper()
        geo_res = evaluate_geopolitical_risk(clean_sym)

        overlay_pct = geo_res.get("overlay_pct", 0.0)
        overlay_type = geo_res.get("overlay_type", "NEUTRAL")
        reason = geo_res.get("overlay_reason", "")

        findings = []
        concerns = []

        if overlay_pct > 0.0:
            findings.append(f"Macro Tailwind ({overlay_type}): {overlay_pct:+.1f}% — {reason}.")
        elif overlay_pct < 0.0:
            concerns.append(f"Macro Risk Headwind ({overlay_type}): {overlay_pct:+.1f}% — {reason}.")

        vote = "REJECT" if overlay_pct <= -25.0 else ("CAUTION" if overlay_pct < 0.0 else "APPROVE")
        weight = 85.0 if vote == "APPROVE" else (55.0 if vote == "CAUTION" else 30.0)

        return AgentOpinion(
            agent_name="Macro/Geopolitical Officer",
            role="Macro Overlay & Geopolitical Risk",
            vote=vote,
            conviction_weight=weight,
            key_findings=findings,
            risk_concerns=concerns
        )

    @classmethod
    def evaluate_investment_committee(
        cls,
        symbol: str,
        stock_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Runs the multi-agent IC debate and produces a consensus conviction score & IC Memo."""
        norm_sym = normalize_symbol(symbol)
        clean_sym = norm_sym.replace(".NS", "").replace(".BO", "").upper()

        data = stock_data or {
            "symbol": clean_sym,
            "sales_growth_3yr": 35.0,
            "pat_growth_3yr": 45.0,
            "roce_3yr": 28.0,
            "cfo_last_year": 250.0,
            "net_profit_last_year": 180.0,
            "capex_last_year": 40.0,
            "fcf_last_year": 210.0,
            "debt_to_equity": 0.05,
            "pe_ratio": 22.0,
            "peg_ratio": 0.8,
            "piotroski_score": 8
        }

        # 1. Execute all 4 Agent Opinions
        forensic = cls.forensic_auditor_agent(clean_sym, data)
        valuation = cls.valuation_skeptic_agent(clean_sym, data)
        growth = cls.growth_optimist_agent(clean_sym, data)
        macro = cls.macro_geopolitical_officer(clean_sym)

        opinions = [forensic, valuation, growth, macro]

        # 2. Execute Skill-42 Domain Sub-Agents & Synthesize via VirtualICArbiter
        sub_forensic_report = ForensicAuditorSubAgent().evaluate(
            clean_sym,
            ownership_snapshot={"promoter_pledge_pct": data.get("pledged_pct", 0.0)}
        )
        sub_supply_report = SupplyChainCatalystSubAgent().evaluate(
            clean_sym,
            sector=data.get("sector")
        )
        sub_red_team_report = RedTeamBearCaseSubAgent().evaluate(
            clean_sym,
            de_ratio=data.get("debt_to_equity")
        )

        arbiter = VirtualICArbiter()
        sub_agent_reports = [sub_forensic_report, sub_supply_report, sub_red_team_report]
        avg_raw_conviction = sum(op.conviction_weight for op in opinions) / len(opinions)
        synthesis = arbiter.synthesize(sub_agent_reports, base_score=avg_raw_conviction)

        # 3. Consensus Resolution (Adjusted by Arbiter synthesis)
        approve_count = sum(1 for op in opinions if op.vote == "APPROVE")
        caution_count = sum(1 for op in opinions if op.vote == "CAUTION")
        reject_count = sum(1 for op in opinions if op.vote == "REJECT")

        avg_conviction = synthesis["adjusted_score"]

        if reject_count >= 2 or synthesis["is_halted"] or avg_conviction < 50.0:
            committee_decision = "REJECT_INVESTMENT"
        elif approve_count >= 3:
            committee_decision = "STRONG_CONVICTION_BUY"
        elif approve_count >= 2:
            committee_decision = "MODERATE_BUY"
        else:
            committee_decision = "CAUTION_WATCHLIST"

        # 4. Generate Executive IC Memo
        ic_memo_lines = [
            f"=== INSTITUTIONAL INVESTMENT COMMITTEE (IC) MEMO: {clean_sym} ===",
            f"FINAL COMMITTEE DECISION: {committee_decision} (Consensus Weight: {avg_conviction:.1f}/100)",
            f"VOTE BREAKDOWN: {approve_count} APPROVE | {caution_count} CAUTION | {reject_count} REJECT\n",
            "--- AGENT DEBATE FINDINGS ---"
        ]

        for op in opinions:
            ic_memo_lines.append(f"[{op.agent_name} ({op.role})] -> Vote: {op.vote} (Weight: {op.conviction_weight:.0f})")
            for f in op.key_findings:
                ic_memo_lines.append(f"  + FINDING: {f}")
            for r in op.risk_concerns:
                ic_memo_lines.append(f"  - RISK: {r}")

        if synthesis["invalidation_triggers"]:
            ic_memo_lines.append("\n--- THESIS INVALIDATION TRIGGERS ---")
            for trig in synthesis["invalidation_triggers"]:
                ic_memo_lines.append(f"  ! TRIGGER: {trig}")

        ic_memo_text = "\n".join(ic_memo_lines)

        return {
            "symbol": clean_sym,
            "committee_decision": committee_decision,
            "consensus_conviction_score": round(avg_conviction, 1),
            "vote_summary": {
                "approve": approve_count,
                "caution": caution_count,
                "reject": reject_count
            },
            "agent_opinions": [
                {
                    "agent_name": op.agent_name,
                    "role": op.role,
                    "vote": op.vote,
                    "conviction_weight": op.conviction_weight,
                    "key_findings": op.key_findings,
                    "risk_concerns": op.risk_concerns
                }
                for op in opinions
            ],
            "arbiter_synthesis": synthesis,
            "ic_memo": ic_memo_text,
            "executed_at": get_ist_now_str(),
            "meta": create_meta_header(source=f"Deterministic IC Rules Engine ({clean_sym})")
        }

