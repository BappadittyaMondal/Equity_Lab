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
from app.services.intelligence.committee_arbiter import VirtualICArbiter

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
        piotroski = stock_data.get("piotroski_score")

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

        if piotroski is not None:
            if piotroski >= 7:
                findings.append(f"High Financial Strength: Piotroski F-Score is {piotroski}/9.")
            elif piotroski <= 4:
                concerns.append(f"Weak Piotroski F-Score ({piotroski}/9). Balance sheet stress.")
        else:
            concerns.append("Piotroski F-Score unverified in corporate filings.")

        vote = "REJECT" if (fcf < -1000.0 or (piotroski is not None and piotroski <= 3)) else ("CAUTION" if concerns else "APPROVE")
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
        from app.services.utils.safe_extractor import SafeDataExtractor
        pe = SafeDataExtractor.get_numeric(stock_data, "pe_ratio")
        peg = SafeDataExtractor.get_numeric(stock_data, "peg_ratio")
        debt_to_equity = SafeDataExtractor.get_numeric(stock_data, "debt_to_equity")

        findings = []
        concerns = []

        if peg is None:
            concerns.append("Valuation Safety Unverified: PEG ratio missing.")
        elif peg < 1.0 and peg > 0.0:
            findings.append(f"Attractive Valuation Safety: PEG ratio is {peg:.2f} (< 1.0 growth at reasonable price).")
        elif peg > 2.0:
            concerns.append(f"Valuation Stretch: PEG ratio is {peg:.2f} (> 2.0 premium valuation).")

        if debt_to_equity is None:
            concerns.append("Solvency Unverified: Debt-to-Equity ratio missing.")
        elif debt_to_equity < 0.3:
            findings.append(f"Low Solvency Risk: Debt-to-Equity is {debt_to_equity:.2f}x (Conservative balance sheet).")
        elif debt_to_equity > 1.0:
            concerns.append(f"High Leverage: Debt-to-Equity is {debt_to_equity:.2f}x.")

        if (debt_to_equity is not None and debt_to_equity > 1.5) or (peg is not None and peg > 3.0):
            vote = "REJECT"
        elif concerns:
            vote = "CAUTION"
        else:
            vote = "APPROVE"
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
        raw_sales = stock_data.get("sales_growth_3yr")
        raw_pat = stock_data.get("pat_growth_3yr")
        raw_roce = stock_data.get("roce_3yr")

        sales_growth = float(raw_sales) if raw_sales is not None else None
        pat_growth = float(raw_pat) if raw_pat is not None else None
        roce = float(raw_roce) if raw_roce is not None else None

        findings = []
        concerns = []

        if sales_growth is None:
            concerns.append("Unverified Revenue Growth: 3-Yr Sales CAGR is unobserved/missing.")
        elif pat_growth is not None and sales_growth > 25.0 and pat_growth > 25.0:
            findings.append(f"High Growth Inflection: 3-Yr Sales CAGR {sales_growth:.1f}% & PAT CAGR {pat_growth:.1f}%.")
        elif sales_growth < 10.0:
            concerns.append(f"Slow Growth Trajectory: 3-Yr Sales CAGR is only {sales_growth:.1f}%.")

        if roce is None:
            concerns.append("Capital Efficiency Unverified: 3-Yr ROCE is unobserved/missing.")
        elif roce > 20.0:
            findings.append(f"Exceptional Capital Efficiency: 3-Yr ROCE is {roce:.1f}%.")
        elif roce < 12.0:
            concerns.append(f"Subpar ROCE ({roce:.1f}%). Below institutional cost of capital threshold.")

        if (sales_growth is not None and sales_growth < 5.0) and (roce is not None and roce < 10.0):
            vote = "REJECT"
        elif concerns:
            vote = "CAUTION"
        else:
            vote = "APPROVE"
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
        import os
        is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"
        norm_sym = normalize_symbol(symbol)
        clean_sym = norm_sym.replace(".NS", "").replace(".BO", "").upper()

        data = stock_data
        if not data:
            try:
                from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
                data = ScreenerCloudConnector.get_company_fundamentals(clean_sym)
            except Exception:
                data = None

        if not data:
            if is_offline:
                data = {
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
            else:
                return {
                    "symbol": clean_sym,
                    "committee_decision": "ABSTAIN_DATA_INSUFFICIENT",
                    "consensus_conviction_score": 0.0,
                    "agent_opinions": [],
                    "ic_memo": f"=== INSTITUTIONAL INVESTMENT COMMITTEE (IC) MEMO: {clean_sym} ===\nFINAL COMMITTEE DECISION: ABSTAIN_DATA_INSUFFICIENT (Consensus Weight: 0.0/100)\n\nEXECUTIVE REASONING:\nAbstaining due to unverified fundamental observations in production.",
                    "meta": create_meta_header(source="Virtual Investment Committee")
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

    @classmethod
    def kedia_smile_vector(cls, symbol: str, stock_data: Dict[str, Any]) -> AgentOpinion:
        """Evaluates Kedia's SMILE framework: Promoter skin-in-the-game, debt-free fortress, and multi-year runway."""
        prom_hold = float(stock_data.get("promoter_holding") or stock_data.get("promoter_holding_pct") or 50.0)
        pledge = float(stock_data.get("pledged_pct") or stock_data.get("promoter_pledge_pct") or 0.0)
        debt_eq = float(stock_data.get("debt_to_equity") or 0.0)
        roce = float(stock_data.get("roce_latest") or stock_data.get("roce_3yr") or 15.0)
        mcap = float(stock_data.get("market_cap") or 2500.0)
        cfo = float(stock_data.get("cfo_last_year") or 0.0)
        pat = float(stock_data.get("net_profit_last_year") or 0.0)

        findings = []
        concerns = []

        # S - Small in size / under-tracked market share
        if mcap <= 10000.0:
            findings.append(f"Small Base Runway (S): Market cap Rs {mcap:.0f} Cr provides compounding headroom.")
        else:
            concerns.append(f"Base Scale Limit (S): Large market cap (Rs {mcap:.0f} Cr) dampens multi-fold SMILE multiplier.")

        # M - Management track record & integrity
        if prom_hold >= 50.0 and pledge <= 2.0:
            findings.append(f"Pristine Insider Alignment (M): Promoter holding {prom_hold:.1f}%, near-zero pledge ({pledge:.1f}%).")
        elif prom_hold < 40.0:
            concerns.append(f"Low Skin in the Game (M): Promoter holding is only {prom_hold:.1f}%.")

        if pledge > 10.0:
            concerns.append(f"Promoter Pledge Vulnerability: {pledge:.1f}% shares encumbered.")

        # I & L - Conservative Solvency & Long Runway
        if debt_eq <= 0.25:
            findings.append(f"Fortress Balance Sheet (I/L): Debt-to-Equity is {debt_eq:.2f}x (virtually debt-free).")
        elif debt_eq > 0.60:
            concerns.append(f"Leverage Stress: Debt-to-Equity is {debt_eq:.2f}x (exceeds Kedia 0.30 threshold).")

        # E - Execution through cycles
        if roce >= 18.0:
            findings.append(f"Cycle-Tested Capital Efficiency (E): ROCE is {roce:.1f}% through business cycles.")
        elif roce < 12.0:
            concerns.append(f"Subpar Capital Allocation: ROCE is only {roce:.1f}%.")

        if pat > 0 and cfo > pat:
            findings.append(f"High Earnings Quality: CFO (Rs {cfo:.1f} Cr) converts fully into reported PAT (Rs {pat:.1f} Cr).")
        elif pat > 0 and cfo < 0:
            concerns.append("Distributive Earnings Red Flag: Negative operating cash flow despite positive accounting profit.")

        vote = "REJECT" if (pledge > 20.0 or debt_eq > 1.0 or prom_hold < 35.0) else ("CAUTION" if concerns else "APPROVE")
        weight = 90.0 if vote == "APPROVE" else (60.0 if vote == "CAUTION" else 30.0)

        return AgentOpinion(
            agent_name="Vijay Kedia Lens",
            role="SMILE Governance, Low Leverage & Long Runway",
            vote=vote,
            conviction_weight=weight,
            key_findings=findings,
            risk_concerns=concerns
        )

    @classmethod
    def kacholia_scalability_vector(cls, symbol: str, stock_data: Dict[str, Any]) -> AgentOpinion:
        """Evaluates Kacholia's capital scalability: Incremental ROIC, Fixed Asset Turnover, and CWIP monetization."""
        roce = float(stock_data.get("roce_latest") or stock_data.get("roce_3yr") or 15.0)
        inc_roic = float(stock_data.get("incremental_roic") or stock_data.get("inc_roic") or roce)
        asset_turn = float(stock_data.get("asset_turnover") or stock_data.get("fixed_asset_turnover") or 1.2)
        sales_3y = float(stock_data.get("sales_growth_3yr") or stock_data.get("sales_cagr_3y") or 15.0)
        pat_3y = float(stock_data.get("pat_growth_3yr") or 18.0)
        cfo = float(stock_data.get("cfo_last_year") or 0.0)
        pat = float(stock_data.get("net_profit_last_year") or 0.0)
        debt_eq = float(stock_data.get("debt_to_equity") or 0.1)

        findings = []
        concerns = []

        # Incremental Capital Productivity
        if inc_roic >= 22.0:
            findings.append(f"Superior Incremental ROIC: {inc_roic:.1f}% (falling incremental capital required per Rs 100 Cr revenue).")
        elif inc_roic >= 16.0:
            findings.append(f"Healthy Incremental Return: ROIC {inc_roic:.1f}%.")
        else:
            concerns.append(f"Capital-Intensive Growth: Incremental ROIC is only {inc_roic:.1f}%.")

        # Operating leverage & asset turnover
        if asset_turn >= 1.5:
            findings.append(f"High Fixed Asset Productivity: Asset turnover is {asset_turn:.2f}x.")
        elif asset_turn < 1.0:
            concerns.append(f"Sluggish Asset Utilization: Fixed asset turn is {asset_turn:.2f}x.")

        if sales_3y >= 18.0 and pat_3y >= 22.0:
            findings.append(f"Convex Operating Leverage: 3Y Sales CAGR {sales_3y:.1f}% translating into PAT CAGR {pat_3y:.1f}%.")
        elif sales_3y < 10.0:
            concerns.append(f"Subdued Growth Runway: 3Y Sales CAGR is {sales_3y:.1f}%.")

        if pat > 0 and cfo >= (0.75 * pat):
            findings.append(f"Disciplined Working Capital: CFO/PAT ratio is {cfo / max(1.0, pat):.2f}x.")
        elif pat > 0 and cfo < (0.50 * pat):
            concerns.append("Working Capital Drain: Operating cash conversion is under 50% of net profit.")

        if debt_eq > 0.80:
            concerns.append(f"Capex Leverage Burden: Debt/Equity is {debt_eq:.2f}x.")

        vote = "REJECT" if (inc_roic < 10.0 and roce < 10.0) or debt_eq > 1.3 else ("CAUTION" if concerns else "APPROVE")
        weight = 90.0 if vote == "APPROVE" else (65.0 if vote == "CAUTION" else 35.0)

        return AgentOpinion(
            agent_name="Ashish Kacholia Lens",
            role="Capital Scalability, Incremental ROIC & Operating Leverage",
            vote=vote,
            conviction_weight=weight,
            key_findings=findings,
            risk_concerns=concerns
        )

    @classmethod
    def agrawal_inflection_vector(cls, symbol: str, stock_data: Dict[str, Any]) -> AgentOpinion:
        """Evaluates Agrawal's techno-funda framework: Earnings acceleration, delivery volume surge, and base breakouts."""
        pat_growth_latest = float(stock_data.get("pat_growth_latest") or stock_data.get("pat_growth_yoy") or 20.0)
        pat_growth_3y = float(stock_data.get("pat_growth_3yr") or 15.0)
        vol_z = float(stock_data.get("volume_z_score") or stock_data.get("vol_z") or 1.5)
        dtr = float(stock_data.get("delivery_turnover_5d") or stock_data.get("dtr_5d") or 2.0)
        current_price = float(stock_data.get("current_price") or stock_data.get("price") or 100.0)
        high_52w = float(stock_data.get("high_52w") or current_price * 1.1)

        findings = []
        concerns = []

        # Fundamental Acceleration
        if pat_growth_latest >= 25.0:
            findings.append(f"Explosive Earnings Inflection: Latest quarter PAT growth +{pat_growth_latest:.1f}% (accelerating above 3Y {pat_growth_3y:.1f}%).")
        elif pat_growth_latest >= 15.0:
            findings.append(f"Solid PAT Inflection: Latest growth +{pat_growth_latest:.1f}%.")
        else:
            concerns.append(f"Lacking Operating Inflection: Latest PAT growth is only {pat_growth_latest:.1f}%.")

        # Technical Delivery Footprint Confirmation
        if vol_z >= 2.0 and dtr >= 2.0:
            findings.append(f"Heavy Institutional Accumulation: Volume Z-Score +{vol_z:.1f}s, Float Delivery Turnover {dtr:.1f}%.")
        elif vol_z >= 1.0:
            findings.append(f"Positive Accumulation Footprint: Volume Z-Score +{vol_z:.1f}s.")
        else:
            concerns.append("Muted Volume Participation: Price movement unconfirmed by institutional delivery expansion.")

        # Price Proximity to 52W High
        proximity_pct = ((high_52w - current_price) / max(1.0, high_52w)) * 100.0
        if proximity_pct <= 10.0:
            findings.append(f"Stage 2 Breakout Proximity: Trading within {proximity_pct:.1f}% of 52-week high.")
        elif proximity_pct > 25.0:
            concerns.append(f"Technical Lag: Trading {proximity_pct:.1f}% below 52-week high (overhead supply resistance).")

        vote = "REJECT" if (pat_growth_latest < 0.0 and pat_growth_3y < 5.0) else ("CAUTION" if concerns else "APPROVE")
        weight = 95.0 if vote == "APPROVE" else (65.0 if vote == "CAUTION" else 35.0)

        return AgentOpinion(
            agent_name="Mukul Agrawal Lens",
            role="Techno-Funda Operating Inflection & Volume Breakout",
            vote=vote,
            conviction_weight=weight,
            key_findings=findings,
            risk_concerns=concerns
        )

    @classmethod
    def evaluate_ace_investor_committee(
        cls,
        symbol: str,
        stock_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Runs the simulated Indian Ace Investor (Kedia, Kacholia, Agrawal) committee debate."""
        import os
        is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"
        norm_sym = normalize_symbol(symbol)
        clean_sym = norm_sym.replace(".NS", "").replace(".BO", "").upper()

        data = stock_data
        if not data:
            try:
                from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
                data = ScreenerCloudConnector.get_company_fundamentals(clean_sym)
            except Exception:
                data = None

        if not data:
            if is_offline:
                data = {
                    "symbol": clean_sym,
                    "market_cap": 2500.0,
                    "promoter_holding": 58.0,
                    "pledged_pct": 0.0,
                    "debt_to_equity": 0.15,
                    "roce_latest": 24.0,
                    "roce_3yr": 22.0,
                    "incremental_roic": 26.0,
                    "asset_turnover": 1.8,
                    "sales_growth_3yr": 28.0,
                    "pat_growth_3yr": 35.0,
                    "pat_growth_latest": 42.0,
                    "cfo_last_year": 180.0,
                    "net_profit_last_year": 140.0,
                    "capex_last_year": 40.0,
                    "fcf_last_year": 140.0,
                    "volume_z_score": 2.2,
                    "delivery_turnover_5d": 3.1,
                    "current_price": 450.0,
                    "high_52w": 475.0,
                }
            else:
                return {
                    "symbol": clean_sym,
                    "committee_decision": "ABSTAIN_DATA_INSUFFICIENT",
                    "consensus_conviction_score": 0.0,
                    "agent_opinions": [],
                    "ic_memo": f"=== ACE INVESTOR BOARDROOM MEMO: {clean_sym} ===\nFINAL COMMITTEE DECISION: ABSTAIN_DATA_INSUFFICIENT\n\nAbstaining due to unobserved fundamental data.",
                    "meta": create_meta_header(source="Ace Investor Virtual Committee")
                }

        # 1. Execute all 3 Ace Investor Vectors
        kedia = cls.kedia_smile_vector(clean_sym, data)
        kacholia = cls.kacholia_scalability_vector(clean_sym, data)
        agrawal = cls.agrawal_inflection_vector(clean_sym, data)

        opinions = [kedia, kacholia, agrawal]

        # 2. Execute Skill 42 Four-Lens Synthesis
        from app.services.research.genai_redteam_service import GenAIRedTeamService
        skill42_synthesis = GenAIRedTeamService.synthesize_four_lens_evidence(clean_sym, data)

        # 3. Consensus & Sweet-Spot Resolution
        approve_count = sum(1 for op in opinions if op.vote == "APPROVE")
        caution_count = sum(1 for op in opinions if op.vote == "CAUTION")
        reject_count = sum(1 for op in opinions if op.vote == "REJECT")
        avg_conviction = sum(op.conviction_weight for op in opinions) / len(opinions)

        has_fatal_red_flag = any("CRITICAL" in rf for rf in skill42_synthesis.get("red_flags", []))

        if reject_count >= 2 or has_fatal_red_flag or avg_conviction < 50.0:
            committee_decision = "REJECT_INVESTMENT"
        elif approve_count == 3:
            committee_decision = "TRIPLE_CONVICTION_MULTIBAGGER"
        elif kedia.vote == "APPROVE" and kacholia.vote == "APPROVE":
            committee_decision = "KEDIA_KACHOLIA_STRUCTURAL_COMPOUNDER"
        elif agrawal.vote == "APPROVE" and kacholia.vote == "APPROVE":
            committee_decision = "AGRAWAL_KACHOLIA_GROWTH_MOMENTUM"
        elif kedia.vote == "APPROVE":
            committee_decision = "KEDIA_COMPOUNDER"
        elif kacholia.vote == "APPROVE":
            committee_decision = "KACHOLIA_SCALABILITY_PLAY"
        elif agrawal.vote == "APPROVE":
            committee_decision = "AGRAWAL_MOMENTUM_INFLECTION"
        else:
            committee_decision = "CAUTION_WATCHLIST"

        # 4. Generate Structured IC Memo
        ic_memo_lines = [
            f"=== ACE INVESTOR BOARDROOM (IC) MEMO: {clean_sym} ===",
            f"FINAL COMMITTEE DECISION: {committee_decision} (Consensus Weight: {avg_conviction:.1f}/100)",
            f"VOTE BREAKDOWN: {approve_count} APPROVE | {caution_count} CAUTION | {reject_count} REJECT\n",
            "--- INVESTOR DEBATE FINDINGS ---"
        ]

        for op in opinions:
            ic_memo_lines.append(f"[{op.agent_name} ({op.role})] -> Vote: {op.vote} (Weight: {op.conviction_weight:.0f})")
            for f in op.key_findings:
                ic_memo_lines.append(f"  + FINDING: {f}")
            for r in op.risk_concerns:
                ic_memo_lines.append(f"  - RISK: {r}")

        if skill42_synthesis.get("red_flags"):
            ic_memo_lines.append("\n--- SKILL 42 RED FLAGS ---")
            for rf in skill42_synthesis["red_flags"]:
                ic_memo_lines.append(f"  ! FLAG: {rf}")

        if skill42_synthesis.get("contradictions"):
            ic_memo_lines.append("\n--- CONTRADICTIONS ---")
            for c in skill42_synthesis["contradictions"]:
                ic_memo_lines.append(f"  ~ CONTRADICTION: {c}")

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
            "skill42_four_lens_synthesis": skill42_synthesis,
            "ic_memo": ic_memo_text,
            "executed_at": get_ist_now_str(),
            "meta": create_meta_header(source=f"Ace Investor Virtual Committee ({clean_sym})")
        }

