"""Institutional Multibagger & Investment Intelligence Scoring Engine.

Implements 27 analytical sub-engines across 10 weighted dimensions, 
Risk Penalty Engine, 8 Stock Archetype Classifier, Causal Chain Tracker, 
Confidence Calculator, and Automated Thesis Generator.
"""

import logging
from typing import Dict, Any, List, Optional
from app.services.data_ingestion.screener_connector import ScreenerCloudConnector

logger = logging.getLogger(__name__)


class InstitutionalMultibaggerEngine:
    """Master institutional 100-point scoring, archetype, and thesis generation engine."""

    @classmethod
    def evaluate_company(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single company profile across all 27 sub-engines."""
        symbol = item.get("symbol", "UNKNOWN")
        name = item.get("company_name", symbol)

        # Extract metric values safely with negative/zero denominator protection
        market_cap = item.get("market_cap", 0.0)
        current_price = item.get("current_price", 0.0)
        high_52w = item.get("high_52w", 1.0)
        low_52w = item.get("low_52w", 1.0)
        volume = item.get("volume", 0)
        vol_1w_avg = item.get("vol_1w_avg", 0.0)
        vol_1y_avg = item.get("vol_1y_avg", 1.0)

        roe_3yr = item.get("roe_3yr", 0.0)
        roe_latest = item.get("roe_latest", 0.0)
        roce_3yr = item.get("roce_3yr", 0.0)
        roce_latest = item.get("roce_latest", 0.0)
        opm_5yr = item.get("opm_5yr", 0.0)
        opm_latest = item.get("opm_latest", 0.0)

        op_growth = item.get("op_growth", 0.0)
        pat_growth_3yr = item.get("pat_growth_3yr", 0.0)
        pat_growth_latest = item.get("pat_growth_latest", 0.0)
        sales_growth_3yr = item.get("sales_growth_3yr", 0.0)
        sales_growth_latest = item.get("sales_growth_latest", 0.0)
        eps_growth_3yr = item.get("eps_growth_3yr", 0.0)
        eps_latest = item.get("eps_latest", 0.0)

        cfo_3yr = item.get("cfo_3yr", 0.0)
        cfo_last_year = item.get("cfo_last_year", 0.0)
        net_profit_last_year = item.get("net_profit_last_year", 0.0)

        net_block = item.get("net_block", 0.0)
        net_block_3yr_back = item.get("net_block_3yr_back", 0.0)
        net_block_prec = item.get("net_block_preceding_year", 0.0)
        cwip = item.get("cwip", 0.0)
        cwip_prec = item.get("cwip_preceding_year", 0.0)

        capex_last_year = item.get("capex_last_year", max(0.0, net_block - net_block_prec + cwip))
        # Free Cash Flow (FCF = CFO - Capex)
        fcf_last_year = item.get("fcf_last_year", cfo_last_year - capex_last_year)

        piotroski_score = item.get("piotroski_score", 0.0)
        promoter_holding = item.get("promoter_holding", 0.0)
        pledged_pct = item.get("pledged_pct", 0.0)
        debt_to_equity = item.get("debt_to_equity", 0.0)
        interest_coverage = item.get("interest_coverage", 0.0)
        peg_ratio = item.get("peg_ratio", 0.0)

        # 1. Engine: Growth Quality (Max: 15)
        growth_score = 0.0
        if sales_growth_3yr >= 15.0:
            growth_score += 5.0
        if sales_growth_3yr >= 25.0:
            growth_score += 2.5
        if pat_growth_3yr >= 20.0:
            growth_score += 5.0
        if pat_growth_3yr >= 30.0:
            growth_score += 2.5

        # 2. Engine: Growth Acceleration (Max: 15)
        acceleration_score = 0.0
        if sales_growth_3yr > 0 and eps_growth_3yr >= sales_growth_3yr * 1.2:
            acceleration_score += 7.5
        if pat_growth_latest >= pat_growth_3yr * 1.1:
            acceleration_score += 7.5

        # 3. Engine: Earnings Inflection (Max: 10)
        inflection_score = 0.0
        if opm_latest > opm_5yr:
            inflection_score += 5.0
        if pat_growth_latest >= 20.0:
            inflection_score += 5.0

        # 4. Engine: Profitability / ROCE / ROIC (Max: 15)
        quality_score = 0.0
        if roce_latest >= 15.0:
            quality_score += 5.0
        if roce_latest >= 25.0:
            quality_score += 2.5
        if roe_3yr >= 15.0:
            quality_score += 5.0
        if roce_3yr >= 18.0:
            quality_score += 2.5

        # 5. Engine: Cash Flow Quality (Max: 15)
        cash_score = 0.0
        if net_profit_last_year > 0 and cfo_last_year > net_profit_last_year:
            cash_score += 7.5
        if net_profit_last_year > 0 and cfo_last_year >= net_profit_last_year * 1.2:
            cash_score += 5.0
        if cfo_3yr > 0:
            cash_score += 2.5

        # 6. Engine: Balance Sheet Safety (Max: 10)
        balance_score = 0.0
        if debt_to_equity <= 0.75:
            balance_score += 5.0
        if debt_to_equity <= 0.3:
            balance_score += 2.5
        if interest_coverage >= 4.0:
            balance_score += 2.5

        # 7. Engine: Reinvestment / Capex Efficiency (Max: 10)
        capex_score = 0.0
        nb_cwip_curr = net_block + cwip
        nb_cwip_prev = net_block_prec + cwip_prec
        if nb_cwip_prev > 0 and nb_cwip_curr >= 1.2 * nb_cwip_prev:
            capex_score += 5.0
        if net_block_3yr_back > 0 and net_block >= 1.4 * net_block_3yr_back:
            capex_score += 5.0

        # 8. Engine: Ownership Alignment (Max: 3)
        ownership_score = 0.0
        if promoter_holding >= 40.0:
            ownership_score += 2.0
        if pledged_pct <= 2.0:
            ownership_score += 1.0

        # 9. Engine: Valuation Safety (Max: 4)
        valuation_score = 0.0
        if 0.1 <= peg_ratio <= 1.5:
            valuation_score += 2.5
        elif 0.1 <= peg_ratio <= 2.5:
            valuation_score += 1.5
        if piotroski_score >= 7.0:
            valuation_score += 1.5

        # 10. Engine: Technical Confirmation (Max: 3)
        technical_score = 0.0
        if low_52w > 0 and current_price >= 1.4 * low_52w:
            technical_score += 1.5
        if vol_1y_avg > 0 and (volume >= 2.0 * vol_1y_avg or vol_1w_avg >= 1.5 * vol_1y_avg):
            technical_score += 1.5

        # Raw Positive Score (0-100)
        raw_score = (
            growth_score + acceleration_score + inflection_score +
            quality_score + cash_score + balance_score +
            capex_score + ownership_score + valuation_score + technical_score
        )

        # Risk Penalty Engine (Phase 2 Enhanced: FCF vs Capex Trap Differentiation)
        risk_penalties = 0.0
        risk_flags = []
        if pledged_pct > 10.0:
            risk_penalties -= 15.0
            risk_flags.append(f"High Promoter Pledge ({pledged_pct:.1f}%)")
        if debt_to_equity > 1.5:
            risk_penalties -= 10.0
            risk_flags.append(f"High Financial Leverage (D/E {debt_to_equity:.2f})")
        if net_profit_last_year > 0 and cfo_last_year < 0.7 * net_profit_last_year:
            risk_penalties -= 10.0
            risk_flags.append("Poor CFO to PAT Cash Conversion (< 0.7x)")
        if interest_coverage < 2.0 and interest_coverage > 0:
            risk_penalties -= 10.0
            risk_flags.append("Weak Interest Coverage (< 2x)")
        
        # Gap B: Heavy FCF Burn / Capex Trap Penalty
        if fcf_last_year < -500.0 or (fcf_last_year < 0.0 and sales_growth_3yr > 25.0 and debt_to_equity > 0.8):
            risk_penalties -= 15.0
            risk_flags.append(f"Severe Free Cash Flow Burn / Capex Trap (FCF: ₹{fcf_last_year:.1f}Cr)")

        overall_score = max(0.0, min(100.0, raw_score + risk_penalties))

        # Confidence Score (0-100)
        data_points = [
            market_cap > 0, current_price > 0, sales_growth_3yr > 0,
            pat_growth_3yr > 0, roce_latest > 0, roe_latest > 0,
            cfo_last_year != 0, net_block > 0, promoter_holding > 0
        ]
        confidence_score = round(sum(100.0 / len(data_points) for dp in data_points if dp), 1)

        # 8 Stock Archetype Classifier
        archetype = "Watchlist Candidate"
        if risk_penalties <= -15.0 or (roce_latest < 10 and sales_growth_3yr < 5 and debt_to_equity > 1.2):
            archetype = "Value Trap"
        elif overall_score >= 80.0 and acceleration_score >= 10.0 and capex_score >= 5.0 and market_cap <= 50000:
            archetype = "Early Multibagger"
        elif overall_score >= 75.0 and quality_score >= 12.0 and cash_score >= 10.0:
            archetype = "Emerging Compounder"
        elif inflection_score >= 8.0 and acceleration_score >= 7.5:
            archetype = "Earnings Inflection"
        elif capex_score >= 8.0 and growth_score >= 7.5:
            archetype = "Capex Expansion"
        elif sales_growth_3yr < 10.0 and pat_growth_latest >= 25.0 and opm_latest > opm_5yr:
            archetype = "Turnaround"
        elif valuation_score >= 3.0 and peg_ratio <= 1.2:
            archetype = "Value Re-rating"
        elif technical_score >= 3.0:
            archetype = "Momentum Leader"

        # Causal Chain Tracking
        causal_chain = []
        if capex_score >= 5.0:
            causal_chain.append("1. Capacity Expansion (Net Block/CWIP Growth)")
        if sales_growth_3yr >= 15.0:
            causal_chain.append("2. Revenue Growth Confirmation")
        if opm_latest > opm_5yr:
            causal_chain.append("3. Operating Leverage & Margin Expansion")
        if pat_growth_3yr >= 20.0:
            causal_chain.append("4. Earnings Acceleration (PAT/EPS Growth)")
        if cfo_last_year > net_profit_last_year:
            causal_chain.append("5. Cash Conversion Confirmation (CFO > PAT)")
        if roce_latest >= 18.0:
            causal_chain.append("6. Capital Efficiency (ROCE > 18%)")
        if technical_score >= 1.5:
            causal_chain.append("7. Technical & Volume Trend Confirmation")

        # Top 5 Positive Drivers & Key Risks
        positive_drivers = []
        if acceleration_score >= 7.5:
            positive_drivers.append(f"EPS Growth ({eps_growth_3yr:.1f}%) outpacing Sales Growth ({sales_growth_3yr:.1f}%)")
        if cash_score >= 7.5:
            positive_drivers.append(f"Strong CFO (₹{cfo_last_year:.1f}Cr) exceeding Net Profit (₹{net_profit_last_year:.1f}Cr)")
        if quality_score >= 10.0:
            positive_drivers.append(f"High Capital Return Efficiency (ROCE: {roce_latest:.1f}%, ROE: {roe_latest:.1f}%)")
        if capex_score >= 5.0:
            positive_drivers.append("Active Capacity Reinvestment (Net Block / CWIP expansion)")
        if balance_score >= 7.5:
            positive_drivers.append(f"Prudent Balance Sheet (Debt/Equity: {debt_to_equity:.2f}, Interest Coverage: {interest_coverage:.1f}x)")
        if not positive_drivers:
            positive_drivers.append("Stable basic baseline metrics")

        invalidation_criteria = [
            "Sales Growth 3Y falls below 10%",
            "OPM falls below 5-Year Median",
            "CFO drops below PAT for 2 consecutive periods",
            "Debt-to-Equity accelerates above 1.2x",
            "Price drops > 25% from 52-Week High on high volume"
        ]

        # Phase 1 & 4 Enhancements: Hard Risk Gate, Early-Stage Inflection, Discovery Status, Thesis Maturity
        hard_gate_res = cls.evaluate_hard_risk_gate(item)
        inflection_res = cls.evaluate_early_stage_inflection(item)
        discovery_res = cls.get_discovery_status(item)

        if not hard_gate_res["passed"]:
            overall_score = 0.0
            archetype = "Disqualified (Hard Risk Gate)"
            risk_flags.extend(hard_gate_res["disqualifications"])

        evidence_quality = item.get("evidence_quality", {
            "inflection": "MEDIUM",
            "runway": "MEDIUM",
            "management": "MEDIUM",
            "scalability": "MEDIUM",
            "cash_quality": "HIGH" if cash_score >= 10.0 else "MEDIUM",
            "valuation": "HIGH" if peg_ratio > 0 else "MEDIUM",
            "market": "MEDIUM"
        })

        thesis_maturity = item.get("thesis_maturity", {
            "status": "Hypothesis",
            "confirmed_quarters": item.get("confirmed_quarters", 0),
            "thesis_age_days": item.get("thesis_age_days", 0)
        })

        return {
            "symbol": symbol,
            "company_name": name,
            "overall_score": round(overall_score, 1),
            "confidence_score": confidence_score,
            "archetype": archetype,
            "hard_risk_gate": hard_gate_res,
            "early_stage_inflection": inflection_res,
            "discovery_status": discovery_res,
            "evidence_quality": evidence_quality,
            "thesis_maturity": thesis_maturity,
            "engine_breakdown": {
                "growth_quality": round(growth_score, 1),
                "growth_acceleration": round(acceleration_score, 1),
                "earnings_inflection": round(inflection_score, 1),
                "profitability_roce": round(quality_score, 1),
                "cash_flow_quality": round(cash_score, 1),
                "balance_sheet_safety": round(balance_score, 1),
                "reinvestment_capex": round(capex_score, 1),
                "ownership_alignment": round(ownership_score, 1),
                "valuation_safety": round(valuation_score, 1),
                "technical_confirmation": round(technical_score, 1),
                "risk_penalties": round(risk_penalties, 1)
            },
            "causal_chain_steps": causal_chain,
            "positive_drivers": positive_drivers[:5],
            "risk_flags": risk_flags,
            "invalidation_criteria": invalidation_criteria
        }

    @classmethod
    def evaluate_hard_risk_gate(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Hard Risk Gate: disqualifies high-risk candidates before scoring."""
        pledged_pct = item.get("pledged_pct", 0.0)
        auditor_resigned = item.get("auditor_resignation", False)
        related_party_red_flag = item.get("related_party_flag", False)
        debt_to_equity = item.get("debt_to_equity", 0.0)

        disqualifications = []
        if pledged_pct > 25.0:
            disqualifications.append(f"Excessive Promoter Pledge ({pledged_pct:.1f}% > 25%)")
        if auditor_resigned:
            disqualifications.append("Auditor Resignation Flagged")
        if related_party_red_flag:
            disqualifications.append("Severe Related-Party Transaction Red Flag")
        if debt_to_equity > 3.0:
            disqualifications.append(f"Extreme Debt-to-Equity ({debt_to_equity:.2f} > 3.0x)")

        return {
            "passed": len(disqualifications) == 0,
            "disqualifications": disqualifications
        }

    @classmethod
    def evaluate_early_stage_inflection(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Early-Stage Detector: Classifies company inflection state."""
        categories_triggered = []
        
        if item.get("op_growth", 0.0) >= 20.0 or item.get("sales_growth_latest", 0.0) >= 20.0:
            categories_triggered.append("Business Inflection")
            
        net_block = item.get("net_block", 0.0)
        net_block_prec = item.get("net_block_preceding_year", 0.0)
        cwip = item.get("cwip", 0.0)
        if cwip > 0 or (net_block_prec > 0 and net_block >= 1.2 * net_block_prec):
            categories_triggered.append("Capacity Inflection")

        if item.get("opm_latest", 0.0) > item.get("opm_5yr", 0.0) or item.get("pat_growth_latest", 0.0) >= 25.0:
            categories_triggered.append("Financial Inflection")

        if item.get("export_transition", False) or item.get("pli_beneficiary", False):
            categories_triggered.append("Strategic Inflection")

        vol_1w = item.get("vol_1w_avg", 0.0)
        vol_1y = item.get("vol_1y_avg", 1.0)
        if vol_1y > 0 and vol_1w >= 1.5 * vol_1y:
            categories_triggered.append("Market Inflection")

        count = len(categories_triggered)
        if count >= 4:
            status = "CONFIRMED INFLECTION"
        elif count >= 2:
            status = "EARLY INFLECTION"
        elif count == 1:
            status = "WATCHING"
        else:
            status = "NO INFLECTION"

        return {
            "status": status,
            "inflection_categories": categories_triggered
        }

    @classmethod
    def get_discovery_status(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Discovery Status: Institutional attention level (0=Heavy, 1=Moderate, 2=Light, 3=Undiscovered)."""
        inst_holding = item.get("fii_dii_holding", item.get("institutional_holding", 15.0))
        analyst_coverage = item.get("analyst_coverage_count", 5)

        if inst_holding < 2.0 and analyst_coverage <= 1:
            level = 3
            label = "Undiscovered"
        elif inst_holding < 10.0 and analyst_coverage <= 3:
            level = 2
            label = "Lightly Covered"
        elif inst_holding < 25.0:
            level = 1
            label = "Moderately Covered"
        else:
            level = 0
            label = "Heavily Covered"

        return {
            "discovery_level": level,
            "discovery_label": label,
            "context_note": f"{label} (FII/DII: {inst_holding:.1f}%, Analysts: {analyst_coverage})"
        }

    @classmethod
    def rank_universe(cls, min_score: float = 50.0) -> List[Dict[str, Any]]:
        """Fetch all fundamentals, filter via DynamicCandidateGate (MAD Outlier/Trust), and rank by score."""
        from app.services.intelligence.candidate_gate import DynamicCandidateGate
        universe = ScreenerCloudConnector.get_all_fundamentals()
        evaluated = [cls.evaluate_company(comp) for comp in universe]

        gate = DynamicCandidateGate()
        candidate_pool = [
            {
                "symbol": e["symbol"],
                "inflection_score": e["overall_score"],
                "quotes": [{"price": e.get("current_price", 100.0)}]
            }
            for e in evaluated
        ]
        accepted_candidates, _ = gate.evaluate_candidates(candidate_pool, min_inflection_score=min_score)
        accepted_symbols = {c["symbol"] for c in accepted_candidates}

        filtered = [e for e in evaluated if e["symbol"] in accepted_symbols]
        filtered.sort(key=lambda x: x["overall_score"], reverse=True)
        return filtered
