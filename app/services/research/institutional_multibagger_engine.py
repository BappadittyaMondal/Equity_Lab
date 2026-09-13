"""Institutional Multibagger & Investment Intelligence Scoring Engine.

Implements 27 analytical sub-engines across 10 weighted dimensions, 
Risk Penalty Engine, 8 Stock Archetype Classifier, Causal Chain Tracker, 
Confidence Calculator, and Automated Thesis Generator.
"""

import logging
import os
import re
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

        operating_profit = float(item.get("operating_profit") or 0.0)
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
        promoter_holding = float(item.get("promoter_holding") or 0.0)
        is_prof_managed = bool(
            item.get("is_professionally_managed")
            or (
                item.get("promoter_holding") is not None
                and float(item.get("promoter_holding", 100.0)) < 5.0
                and (market_cap >= 10000.0 or item.get("institutional_holding", 0.0) >= 25.0)
            )
        )
        is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"
        pledged_raw = item.get("pledged_pct")
        if pledged_raw is not None:
            try:
                pledged_pct = float(pledged_raw)
            except (ValueError, TypeError):
                pledged_pct = 0.0 if is_offline else None
        else:
            pledged_pct = 0.0 if is_offline else None

        debt_raw = item.get("debt_to_equity")
        if debt_raw is not None:
            try:
                debt_to_equity = float(debt_raw)
            except (ValueError, TypeError):
                debt_to_equity = 0.0 if is_offline else None
        else:
            debt_to_equity = 0.0 if is_offline else None

        int_cov_raw = item.get("interest_coverage")
        if int_cov_raw is not None:
            try:
                interest_coverage = float(int_cov_raw)
            except (ValueError, TypeError):
                interest_coverage = 0.0 if is_offline else None
        else:
            interest_coverage = 0.0 if is_offline else None

        peg_raw = item.get("peg_ratio")
        if peg_raw is not None:
            try:
                peg_ratio = float(peg_raw)
            except (ValueError, TypeError):
                peg_ratio = 0.0 if is_offline else None
        else:
            peg_ratio = 0.0 if is_offline else None

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
        if debt_to_equity is not None:
            if debt_to_equity <= 0.75:
                balance_score += 5.0
            if debt_to_equity <= 0.3:
                balance_score += 2.5
        if interest_coverage is not None and interest_coverage >= 4.0:
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
        if pledged_pct is not None and pledged_pct <= 2.0:
            ownership_score += 1.0

        # 9. Engine: Valuation Safety (Max: 4)
        valuation_score = 0.0
        if peg_ratio is not None:
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
        if is_prof_managed:
            pass  # Professionally managed: no promoter pledge penalty
        elif pledged_pct is not None:
            if pledged_pct > 10.0:
                risk_penalties -= 15.0
                risk_flags.append(f"High Promoter Pledge ({pledged_pct:.1f}%)")
        else:
            risk_penalties -= 15.0
            risk_flags.append("Promoter Pledge Data Missing/Unverified")
        if debt_to_equity is not None:
            if debt_to_equity > 1.5:
                risk_penalties -= 10.0
                risk_flags.append(f"High Financial Leverage (D/E {debt_to_equity:.2f})")
        else:
            risk_penalties -= 10.0
            risk_flags.append("Debt-to-Equity Data Missing/Unverified")
        if net_profit_last_year > 0 and cfo_last_year < 0.7 * net_profit_last_year:
            risk_penalties -= 10.0
            risk_flags.append("Poor CFO to PAT Cash Conversion (< 0.7x)")
        if interest_coverage is not None:
            if 0 <= interest_coverage < 2.0:
                risk_penalties -= 10.0
                risk_flags.append(f"Weak Interest Coverage ({interest_coverage:.2f}x < 2x)")
        else:
            risk_penalties -= 10.0
            risk_flags.append("Interest Coverage Data Missing/Unverified")
        
        # Gap B: Heavy FCF Burn / Capex Trap Penalty
        de_for_burn = debt_to_equity if debt_to_equity is not None else 0.0
        if fcf_last_year < -500.0 or (fcf_last_year < 0.0 and sales_growth_3yr > 25.0 and de_for_burn > 0.8):
            risk_penalties -= 15.0
            risk_flags.append(f"Severe Free Cash Flow Burn / Capex Trap (FCF: ₹{fcf_last_year:.1f}Cr)")

        overall_score = max(0.0, min(100.0, raw_score + risk_penalties))

        # Data Completeness Tracking (§Institutional Epistemic Separation)
        observed_fields = [
            item.get("market_cap") is not None,
            item.get("current_price") is not None,
            item.get("sales_growth_3yr") is not None,
            item.get("pat_growth_3yr") is not None,
            item.get("roce_latest") is not None,
            item.get("roe_latest") is not None,
            item.get("cfo_last_year") is not None,
            item.get("net_block") is not None,
            item.get("promoter_holding") is not None
        ]
        data_completeness_pct = round(sum(100.0 / len(observed_fields) for obs in observed_fields if obs), 1)

        # Confidence Score (0-100)
        data_points = [
            market_cap > 0, current_price > 0, sales_growth_3yr > 0,
            pat_growth_3yr > 0, roce_latest > 0, roe_latest > 0,
            cfo_last_year != 0, net_block > 0, promoter_holding > 0
        ]
        confidence_score = round(sum(100.0 / len(data_points) for dp in data_points if dp), 1)

        # 8 Stock Archetype Classifier
        archetype = "Watchlist Candidate"
        if risk_penalties <= -15.0 or (roce_latest < 10 and sales_growth_3yr < 5 and debt_to_equity is not None and debt_to_equity > 1.2):
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
        elif valuation_score >= 3.0 and peg_ratio is not None and peg_ratio <= 1.2:
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
            d_str = f"{debt_to_equity:.2f}" if debt_to_equity is not None else "N/A"
            ic_str = f"{interest_coverage:.1f}x" if interest_coverage is not None else "N/A"
            positive_drivers.append(f"Prudent Balance Sheet (Debt/Equity: {d_str}, Interest Coverage: {ic_str})")
        if not positive_drivers:
            positive_drivers.append("Stable basic baseline metrics")

        invalidation_criteria = [
            "Sales Growth 3Y falls below 10%",
            "OPM falls below 5-Year Median",
            "CFO drops below PAT for 2 consecutive periods",
            "Debt-to-Equity accelerates above 1.2x",
            "Price drops > 25% from 52-Week High on high volume",
            "Weekly close finishes below 30-WMA for 2 consecutive weeks (Mandatory 50% de-risking exit)",
            "Quarterly revenue growth falls below 20% YoY or EBITDA margins contract for 2 consecutive quarters"
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
            "valuation": "HIGH" if (peg_ratio is not None and peg_ratio > 0) else "MEDIUM",
            "market": "MEDIUM"
        })

        thesis_maturity = item.get("thesis_maturity", {
            "status": "Hypothesis",
            "confirmed_quarters": item.get("confirmed_quarters", 0),
            "thesis_age_days": item.get("thesis_age_days", 0)
        })

        # Wire MultibaggerStateMachine (Lifecycle & Kill-Trigger Governance)
        from app.services.research.finder_state_machines import MultibaggerStateMachine

        is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"

        # Context-Aware 3-Tier Pledge Matrix (DEF-001 & Pillar 1 Alignment)
        if is_prof_managed:
            pledge_val = 0.0  # Professionally managed: pledge check evaluates cleanly
        elif pledged_pct is not None:
            pledge_val = float(pledged_pct)
        elif is_offline:
            pledge_val = 0.0
        else:
            pledge_val = 50.0  # Promoter unobserved in prod: fail-closed to protect capital
            risk_flags.append("Promoter Pledge Data Missing/Unverified in Production")

        # Multi-period ROCE persistence tracking
        if roce_latest >= 20.0 and roce_3yr >= 20.0:
            consec_roce_q = 6
        elif roce_latest >= 20.0:
            consec_roce_q = 2
        elif roce_latest >= 15.0:
            consec_roce_q = 1
        else:
            consec_roce_q = 0

        # Valuation Z-score relative to fair value PEG benchmark (1.0)
        val_z = round((peg_ratio - 1.0) / 0.5, 2) if (peg_ratio is not None and peg_ratio > 0) else 0.0

        # Real EBITDA derivation (DEF-005 & DEF-C): Track proxy flags honestly
        cfo_is_proxy = False
        if operating_profit > 0.0:
            cfo_ebitda_val = round(cfo_last_year / operating_profit, 2)
        elif not is_offline:
            fund_data = ScreenerCloudConnector.get_company_fundamentals(symbol)
            op_prof_db = float(fund_data.get("operating_profit") or 0.0) if fund_data else 0.0
            if op_prof_db > 0.0:
                cfo_ebitda_val = round(cfo_last_year / op_prof_db, 2)
            elif net_profit_last_year > 0:
                cfo_ebitda_val = round(cfo_last_year / (net_profit_last_year * 1.2), 2)
                cfo_is_proxy = True
            else:
                cfo_ebitda_val = 0.0
        else:
            cfo_ebitda_val = round(cfo_last_year / max(net_profit_last_year * 1.2, 1e-4), 2)
            cfo_is_proxy = True

        inc_roic_input = item.get("incremental_roic")
        if inc_roic_input is not None:
            inc_roic_val = float(inc_roic_input)
            inc_roic_estimated = False
        else:
            delta_nopat = item.get("delta_nopat")
            delta_ic = item.get("delta_invested_capital") or item.get("delta_ic")
            if delta_nopat is not None and delta_ic is not None and float(delta_ic) > 0:
                inc_roic_val = round((float(delta_nopat) / float(delta_ic)) * 100.0, 1)
                inc_roic_estimated = False
            else:
                inc_roic_val = float(roce_latest) if (is_offline or roce_latest is not None) else 0.0
                inc_roic_estimated = True

        evidence_quality["cfo_ebitda_is_proxy"] = cfo_is_proxy
        evidence_quality["incremental_roic_estimated"] = inc_roic_estimated

        mb_sm = MultibaggerStateMachine.evaluate(
            symbol=symbol,
            pat_growth_ttm=pat_growth_latest,
            pat_growth_prev=pat_growth_3yr,
            incremental_roic=inc_roic_val,
            wacc=12.0,
            cfo_to_ebitda=cfo_ebitda_val,
            promoter_pledge_pct=pledge_val,
            is_breakout_cleared=technical_score >= 3.0,
            consecutive_high_roce_quarters=consec_roce_q,
            valuation_z_score=val_z,
        )

        if mb_sm["state"] == "INVALIDATED":
            risk_flags.extend(mb_sm["kill_triggers_fired"])

        # Phase 45: Multibagger State-Transition Classification & 5x/10x Economic Feasibility
        lifecycle_stage = cls.classify_multibagger_lifecycle_stage(item)
        economic_feasibility = cls.evaluate_multibagger_economic_feasibility(item)
        if economic_feasibility.get("is_haircut_applied", False):
            overall_score = max(0.0, overall_score - economic_feasibility.get("haircut_points", 0.0))
            risk_flags.extend(economic_feasibility.get("risk_flags", []))

        # Phase 76: Quarterly Invalidation Milestone Tracker
        invalidation_milestones = cls.evaluate_quarterly_invalidation_milestones(item)
        if invalidation_milestones.get("thesis_health") == "THESIS_DEGRADATION_ALERT":
            risk_flags.extend(invalidation_milestones.get("breached_milestones", []))

        # Phase 80: 5x Operational Inflection Catalysts ("Anatomy of a True 5x Move")
        operational_5x_catalysts = cls.evaluate_5x_operational_catalysts(item)
        if operational_5x_catalysts.get("has_5x_catalyst"):
            positive_drivers.extend(operational_5x_catalysts.get("active_catalyst_notes", []))

        # Phase 114: Capacity Feasibility Ratio (CFR) Check
        capacity_feasibility = cls.evaluate_capacity_feasibility_ratio(item)
        if capacity_feasibility.get("is_capacity_stressed", False):
            overall_score = max(0.0, overall_score - capacity_feasibility.get("haircut_points", 0.0))
            if capacity_feasibility.get("stress_flag"):
                risk_flags.append(capacity_feasibility["stress_flag"])

        return {
            "symbol": symbol,
            "company_name": name,
            "overall_score": round(overall_score, 1),
            "confidence_score": confidence_score,
            "data_completeness_pct": data_completeness_pct,
            "archetype": archetype,
            "lifecycle_state_machine": mb_sm,
            "lifecycle_stage": lifecycle_stage,
            "economic_feasibility": economic_feasibility,
            "capacity_feasibility": capacity_feasibility,
            "invalidation_milestones": invalidation_milestones,
            "operational_5x_catalysts": operational_5x_catalysts,
            "is_investable": mb_sm["is_investable"] and economic_feasibility["is_feasible"] and not capacity_feasibility["is_capacity_stressed"],
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
        is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"
        pledged_raw = item.get("pledged_pct")
        if pledged_raw is not None:
            try:
                pledged_pct = float(pledged_raw)
            except (ValueError, TypeError):
                pledged_pct = 0.0 if is_offline else None
        else:
            pledged_pct = 0.0 if is_offline else None

        auditor_resigned = item.get("auditor_resignation", False)
        related_party_red_flag = item.get("related_party_flag", False)
        debt_raw = item.get("debt_to_equity")
        if debt_raw is not None:
            try:
                debt_to_equity = float(debt_raw)
            except (ValueError, TypeError):
                debt_to_equity = 0.0 if is_offline else None
        else:
            debt_to_equity = 0.0 if is_offline else None

        is_prof_managed = bool(item.get("promoter_holding") is not None and float(item.get("promoter_holding", 100.0)) < 5.0)
        disqualifications = []
        if is_prof_managed:
            pass  # Professionally managed: zero promoter pledge is standard
        elif pledged_pct is None:
            disqualifications.append("Promoter Pledge Data Missing/Unverified (Fail-Closed Risk Gate)")
        elif pledged_pct > 25.0:
            disqualifications.append(f"Excessive Promoter Pledge ({pledged_pct:.1f}% > 25%)")
        if auditor_resigned:
            disqualifications.append("Auditor Resignation Flagged")
        if related_party_red_flag:
            disqualifications.append("Severe Related-Party Transaction Red Flag")
        if debt_to_equity is not None and debt_to_equity > 3.0:
            disqualifications.append(f"Extreme Debt-to-Equity ({debt_to_equity:.2f} > 3.0x)")

        return {
            "passed": len(disqualifications) == 0,
            "disqualifications": disqualifications
        }

    @classmethod
    def classify_multibagger_lifecycle_stage(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Classifies the structural lifecycle stage (M0 to M4) of a multibagger candidate."""
        market_cap = float(item.get("market_cap") or 0.0)
        net_block = float(item.get("net_block") or 0.0)
        cwip = float(item.get("cwip") or 0.0)
        opm_latest = float(item.get("opm_latest") or 0.0)
        opm_5yr = float(item.get("opm_5yr") or 0.0)
        cfo_last_year = float(item.get("cfo_last_year") or 0.0)
        net_profit_last_year = float(item.get("net_profit_last_year") or 0.0)
        inst_holding = float(item.get("fii_dii_holding", item.get("institutional_holding", 0.0)) or 0.0)
        inc_roic = float(item.get("incremental_roic", item.get("roce_latest", 0.0)) or 0.0)
        sales_growth = float(item.get("sales_growth_latest", item.get("sales_growth_3yr", 0.0)) or 0.0)
        data_completeness = float(item.get("data_completeness_pct", 100.0) or 100.0)

        cwip_ratio = (cwip / net_block) if net_block > 0 else 0.0

        if data_completeness < 60.0 or (market_cap > 0 and market_cap < 50.0):
            stage = "M0_UNVERIFIED"
            description = "Incomplete financial history or unverified microcap ceiling"
        elif market_cap >= 10000.0 and sales_growth >= 12.0 and inc_roic >= 18.0:
            stage = "M4_MATURE_COMPOUNDER"
            description = "Market cap > ₹10,000 Cr with established moat and steady compounding runway"
        elif inc_roic >= 22.0 or (5.0 <= inst_holding <= 25.0 and sales_growth >= 20.0):
            stage = "M3_INSTITUTIONAL_SCALING"
            description = "Institutional accumulation phase with high incremental capital productivity (ROIC >= 22%)"
        elif cwip_ratio >= 0.25 or (opm_latest >= (opm_5yr + 2.0) and sales_growth >= 15.0):
            stage = "M2_OPERATING_INFLECTION"
            description = "Operating inflection: capex commissioning (CWIP/Block >= 25%) or operating margin expansion"
        elif cfo_last_year > 0 or (opm_latest >= opm_5yr and net_profit_last_year > 0):
            stage = "M1_BASE_STABILIZING"
            description = "Base stabilizing: cash bleed arrested and margins stabilizing"
        else:
            stage = "M0_UNVERIFIED"
            description = "Unverified baseline or early pre-turnaround phase"

        return {
            "stage": stage,
            "stage_code": stage.split("_")[0],
            "description": description,
            "cwip_to_block_ratio": round(cwip_ratio, 3),
            "institutional_holding_pct": round(inst_holding, 2),
            "incremental_roic_pct": round(inc_roic, 2)
        }

    @classmethod
    def evaluate_multibagger_economic_feasibility(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates 7-year 5x/10x return CAGR hurdles and required earnings growth feasibility."""
        current_price = float(item.get("current_price") or 0.0)
        eps_latest = float(item.get("eps_latest") or 0.0)
        peg_ratio = item.get("peg_ratio")
        eps_growth = float(item.get("eps_growth_3yr", item.get("pat_growth_3yr", 0.0)) or 0.0)

        # Starting P/E derivation
        pe_0 = None
        for key in ("pe_ratio", "pe", "trailing_pe", "price_to_earnings"):
            val = item.get(key)
            if val is not None:
                try:
                    p = float(val)
                    if p > 0:
                        pe_0 = p
                        break
                except (ValueError, TypeError):
                    pass

        if pe_0 is None and current_price > 0 and eps_latest > 0:
            pe_0 = round(current_price / eps_latest, 2)
        elif pe_0 is None and peg_ratio is not None and eps_growth > 0:
            try:
                pe_0 = round(float(peg_ratio) * eps_growth, 2)
            except (ValueError, TypeError):
                pe_0 = None

        if pe_0 is None or pe_0 <= 0:
            pe_0 = 22.0  # Conservative institutional default benchmark

        pe_terminal = 20.0  # Conservative terminal exit multiple

        # Mathematical 7-Year Price CAGRs
        # 5x in 7 years: (5)^(1/7) - 1 = 25.85%
        # 10x in 7 years: (10)^(1/7) - 1 = 38.92%
        cagr_5x_price = round(((5.0 ** (1.0 / 7.0)) - 1.0) * 100.0, 2)
        cagr_10x_price = round(((10.0 ** (1.0 / 7.0)) - 1.0) * 100.0, 2)

        # Implied Earnings Multiple: Target_Multiple * (PE_0 / PE_terminal)
        earnings_mult_5x = round(5.0 * (pe_0 / pe_terminal), 2)
        earnings_cagr_5x = round(((max(0.01, earnings_mult_5x) ** (1.0 / 7.0)) - 1.0) * 100.0, 2)

        earnings_mult_10x = round(10.0 * (pe_0 / pe_terminal), 2)
        earnings_cagr_10x = round(((max(0.01, earnings_mult_10x) ** (1.0 / 7.0)) - 1.0) * 100.0, 2)

        is_haircut_applied = False
        haircut_points = 0.0
        risk_flags = []

        if earnings_cagr_5x > 45.0 or pe_0 > 75.0:
            hurdle_status = "EXTREME_HURDLE"
            is_feasible = False
            is_haircut_applied = True
            haircut_points = 10.0
            risk_flags.append(
                f"Economic Feasibility Breach: Required 5x Earnings CAGR of {earnings_cagr_5x:.1f}% "
                f"exceeds institutional ceiling (45.0%) due to inflated entry P/E ({pe_0:.1f}x)"
            )
        elif earnings_cagr_5x > 32.0:
            hurdle_status = "AMBITIOUS_HURDLE"
            is_feasible = True
        else:
            hurdle_status = "REALISTIC_HURDLE"
            is_feasible = True

        # Sector TAM Ceiling Check
        current_rev = float(item.get("revenue_cr", item.get("sales_last_year", item.get("revenue", 0.0))) or 0.0)
        sector_tam = float(item.get("sector_tam_cr", item.get("sector_tam", 25000.0)) or 25000.0)
        export_transition = bool(item.get("export_transition", False))

        implied_7y_revenue = current_rev * ((1.0 + (earnings_cagr_5x / 100.0)) ** 7.0) if current_rev > 0 else 0.0
        implied_market_share_pct = round((implied_7y_revenue / sector_tam) * 100.0, 2) if sector_tam > 0 else 0.0

        tam_ceiling_breach = False
        if current_rev > 0 and implied_market_share_pct > 35.0 and not export_transition:
            tam_ceiling_breach = True
            is_feasible = False
            is_haircut_applied = True
            haircut_points += 10.0
            hurdle_status = "SECTOR_TAM_CEILING_BREACH"
            risk_flags.append(
                f"Sector TAM Ceiling Breach: Implied 7Y Revenue (₹{implied_7y_revenue:,.1f}Cr) requires "
                f"{implied_market_share_pct:.1f}% of domestic TAM (₹{sector_tam:,.1f}Cr) without export transition"
            )

        return {
            "entry_pe": round(pe_0, 2),
            "assumed_terminal_pe": pe_terminal,
            "target_horizon_years": 7,
            "cagr_5x_price_pct": cagr_5x_price,
            "cagr_10x_price_pct": cagr_10x_price,
            "earnings_growth_required_5x_mult": earnings_mult_5x,
            "earnings_cagr_required_5x_pct": earnings_cagr_5x,
            "earnings_growth_required_10x_mult": earnings_mult_10x,
            "earnings_cagr_required_10x_pct": earnings_cagr_10x,
            "implied_7y_revenue_cr": round(implied_7y_revenue, 2),
            "sector_tam_cr": round(sector_tam, 2),
            "implied_market_share_pct": round(implied_market_share_pct, 2),
            "tam_ceiling_breach": tam_ceiling_breach,
            "hurdle_status": hurdle_status,
            "is_feasible": is_feasible,
            "is_haircut_applied": is_haircut_applied,
            "haircut_points": haircut_points,
            "risk_flags": risk_flags
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
    def evaluate_quarterly_invalidation_milestones(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Quarterly Invalidation Milestone Tracker (§CRO Operational Compounding Auditing).
        
        Tracks 4 core empirical operating invariants required for institutional multibagger compounding:
          1. Revenue Growth >= 20.0% YoY (TTM or 3Y CAGR)
          2. Incremental ROIC >= 22.0% (Reinvestment Capital Efficiency)
          3. Operating Margin Stability (OPM latest >= OPM 5Y - 2.0%, within +/- 150-200 bps)
          4. Governance & Balance Sheet Hygiene (Clean Audit & Promoter Pledge < 5.0%)
        """
        milestones = {}
        breaches = []

        # 1. Topline Revenue Expansion Milestone (>= 20% YoY)
        sales_growth_latest = item.get("sales_growth_latest")
        sales_growth_3yr = item.get("sales_growth_3yr", 0.0)
        topline_growth = float(sales_growth_latest if sales_growth_latest is not None else sales_growth_3yr)
        rev_pass = topline_growth >= 20.0
        milestones["revenue_growth_20pct"] = {
            "title": "Revenue Expansion Invariant (>= 20.0% YoY)",
            "observed_value": round(topline_growth, 2),
            "threshold": 20.0,
            "status": "PASS" if rev_pass else "BREACH",
            "notes": f"Observed Topline Growth: {topline_growth:.1f}% vs 20.0% milestone."
        }
        if not rev_pass:
            breaches.append(f"Topline growth ({topline_growth:.1f}%) decelerated below 20.0% compounding benchmark.")

        # 2. Incremental Capital Efficiency Milestone (ROIC >= 22%)
        inc_roic = item.get("incremental_roic") or item.get("inc_roic")
        if inc_roic is None:
            inc_roic = item.get("roce_latest", 0.0)
        inc_roic_val = float(inc_roic)
        roic_pass = inc_roic_val >= 22.0
        milestones["incremental_roic_22pct"] = {
            "title": "Incremental Capital Productivity Invariant (ROIC >= 22.0%)",
            "observed_value": round(inc_roic_val, 2),
            "threshold": 22.0,
            "status": "PASS" if roic_pass else "BREACH",
            "notes": f"Observed Incremental ROIC/ROCE: {inc_roic_val:.1f}% vs 22.0% hurdle."
        }
        if not roic_pass:
            breaches.append(f"Capital productivity ({inc_roic_val:.1f}%) failed 22.0% incremental ROIC hurdle.")

        # 3. Operating Margin Stability (+/- 150-200 bps tolerance)
        opm_latest = float(item.get("opm_latest") or 0.0)
        opm_5yr = float(item.get("opm_5yr") or 0.0)
        # Margin degradation exceeding 200 bps indicates pricing power loss
        margin_pass = (opm_latest >= (opm_5yr - 2.0)) or (opm_latest >= 20.0)
        milestones["margin_stability"] = {
            "title": "Operating Margin Stability Invariant (OPM >= 5Y Avg - 2.0%)",
            "observed_value": round(opm_latest, 2),
            "benchmark_5yr": round(opm_5yr, 2),
            "status": "PASS" if margin_pass else "BREACH",
            "notes": f"Latest OPM: {opm_latest:.1f}% vs 5Y Benchmark: {opm_5yr:.1f}%."
        }
        if not margin_pass:
            breaches.append(f"Operating margin ({opm_latest:.1f}%) contracted > 200 bps below 5Y avg ({opm_5yr:.1f}%).")

        # 4. Forensic & Governance Hygiene (Clean Audit & Pledge < 5%)
        audit_qualification = bool(item.get("audit_qualification", False))
        is_prof_managed = bool(item.get("is_professionally_managed", False))
        pledged_pct = float(item.get("pledged_pct") or 0.0) if not is_prof_managed else 0.0
        gov_pass = (not audit_qualification) and (pledged_pct < 5.0)
        milestones["forensic_governance"] = {
            "title": "Governance & Forensic Invariant (Clean Audit & Pledge < 5.0%)",
            "audit_qualified": audit_qualification,
            "promoter_pledge_pct": round(pledged_pct, 2),
            "status": "PASS" if gov_pass else "BREACH",
            "notes": f"Audit Clean: {not audit_qualification}, Pledge: {pledged_pct:.1f}%."
        }
        if not gov_pass:
            if audit_qualification:
                breaches.append("Auditor qualification detected on financial statements.")
            if pledged_pct >= 5.0:
                breaches.append(f"Promoter pledge ({pledged_pct:.1f}%) exceeds 5.0% institutional tolerance.")

        passed_count = sum(1 for m in milestones.values() if m["status"] == "PASS")
        total_milestones = len(milestones)

        # Fatal governance breach or >= 2 operational breaches triggers THESIS_DEGRADATION_ALERT
        is_thesis_healthy = (passed_count >= 3) and gov_pass
        thesis_health = "HEALTHY_COMPOUNDING" if is_thesis_healthy else "THESIS_DEGRADATION_ALERT"

        guidance = (
            "All operational compounding invariants satisfied. Maintain institutional allocation."
            if is_thesis_healthy else
            f"ALERT: {len(breaches)} compounding milestones breached ({', '.join(breaches)}). Trigger institutional thesis re-underwriting."
        )

        return {
            "thesis_health": thesis_health,
            "milestones_passed_count": passed_count,
            "total_milestones": total_milestones,
            "is_thesis_healthy": is_thesis_healthy,
            "milestones": milestones,
            "breached_milestones": breaches,
            "actionable_guidance": guidance
        }

    SECTOR_ASSET_TURNOVER_BENCHMARKS: Dict[str, float] = {
        "DEFENSE_ELECTRONICS": 3.5,
        "DEFENSE": 3.0,
        "ESDM_ELECTRONICS": 3.0,
        "ELECTRONICS": 2.8,
        "CAPITAL_GOODS": 2.2,
        "HEAVY_ENGINEERING": 1.8,
        "INDUSTRIAL_MACHINERY": 2.0,
        "EPC_INFRASTRUCTURE": 1.3,
        "CIVIL_CONSTRUCTION": 1.2,
        "INFRASTRUCTURE": 1.3,
        "METALS_AND_MINING": 1.4,
        "POWER_EQUIPMENT": 1.8,
        "POWER": 1.5,
        "RENEWABLE_ENERGY": 1.6,
        "CHEMICALS": 1.8,
        "AUTO_COMPONENTS": 2.4,
        "IT_SERVICES": 8.0,
        "SOFTWARE": 8.0,
        "TECHNOLOGY": 6.0,
        "SERVICES": 6.0,
        "DEFAULT": 2.0
    }

    @classmethod
    def resolve_sector_asset_turnover(cls, sector_str: str) -> float:
        """Resolves empirical asset turnover benchmark for a sector or industry string using exact & token boundary resolution."""
        if not sector_str:
            return cls.SECTOR_ASSET_TURNOVER_BENCHMARKS["DEFAULT"]
        clean = str(sector_str).upper().replace(" ", "_").strip()
        # 1. Exact match
        if clean in cls.SECTOR_ASSET_TURNOVER_BENCHMARKS:
            return cls.SECTOR_ASSET_TURNOVER_BENCHMARKS[clean]

        # 2. Match with boundary protection (longest keys checked first)
        sorted_keys = sorted([k for k in cls.SECTOR_ASSET_TURNOVER_BENCHMARKS.keys() if k != "DEFAULT"], key=len, reverse=True)
        for k in sorted_keys:
            pattern = r"(?:^|_|\b)" + re.escape(k) + r"(?:$|_|\b)"
            if re.search(pattern, clean):
                return cls.SECTOR_ASSET_TURNOVER_BENCHMARKS[k]

        # 3. Token subset matching (clean tokens match a key)
        clean_tokens = set(re.findall(r"[A-Z0-9]+", clean))
        for k in sorted_keys:
            k_tokens = set(re.findall(r"[A-Z0-9]+", k))
            if clean_tokens and clean_tokens.issubset(k_tokens):
                return cls.SECTOR_ASSET_TURNOVER_BENCHMARKS[k]

        return cls.SECTOR_ASSET_TURNOVER_BENCHMARKS["DEFAULT"]

    @classmethod
    def evaluate_capacity_feasibility_ratio(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Capacity Feasibility Ratio (CFR) (§Institutional Pre-Inflection Microstructure).
        
        In manufacturing and EPC/industrial sectors, prevent phantom order-book narratives
        by computing:
            CFR = Unexecuted Order Book / (max(Net Block, 1.0) * Sector Asset Turnover Benchmark)
            
        Flags EXECUTION_CAPACITY_STRESS if CFR > 3.5x and CWIP / Net Block < 0.20 (i.e. company
        claims massive unexecutable order book without sufficient internal fixed assets or
        underway capex, leading to severe subcontracting margin leakage or delivery default).
        """
        unexecuted_order_book = float(
            item.get("unexecuted_order_book")
            or item.get("order_book")
            or item.get("order_book_cr")
            or item.get("order_wins_value_cr")
            or item.get("accumulated_order_wins")
            or 0.0
        )
        # Automated headless accumulation fallback from Corporate Announcements Radar
        if unexecuted_order_book <= 0.0:
            symbol = item.get("symbol")
            if symbol:
                try:
                    from app.services.ingestion.announcements_radar import CorporateAnnouncementsRadar
                    clean_sym = str(symbol).replace(".NS", "").replace(".BO", "").upper()
                    radar_res = CorporateAnnouncementsRadar.get_company_instant_announcements(clean_sym)
                    if radar_res and radar_res.get("recent_announcements"):
                        order_wins = [
                            float(a.get("order_value_cr") or 0.0)
                            for a in radar_res["recent_announcements"]
                            if a.get("category") == "MEGA_ORDER_WIN" and a.get("order_value_cr")
                        ]
                        if order_wins:
                            unexecuted_order_book = sum(order_wins)
                except Exception:
                    pass

        net_block = float(item.get("net_block") or item.get("fixed_assets") or 0.0)
        cwip = float(item.get("cwip") or 0.0)
        
        # Sector asset turnover benchmark resolution (explicit -> sector lookup -> default 2.0)
        raw_turnover = item.get("sector_asset_turnover_benchmark") or item.get("asset_turnover_benchmark")
        if raw_turnover is not None:
            try:
                sector_turnover = float(raw_turnover)
            except (ValueError, TypeError):
                sector_turnover = 2.0
        else:
            sector_str = str(item.get("sector") or item.get("industry") or "").upper().replace(" ", "_").strip()
            sector_turnover = cls.resolve_sector_asset_turnover(sector_str)
        if sector_turnover <= 0.0:
            sector_turnover = 2.0

        denom = max(net_block, 1.0) * sector_turnover
        cfr = round(unexecuted_order_book / denom, 2) if unexecuted_order_book > 0 else 0.0
        cwip_to_nb = round(cwip / max(net_block, 1.0), 2) if net_block > 0 else 0.0

        is_stressed = False
        stress_flag = None
        haircut_points = 0.0

        if unexecuted_order_book > 0 and cfr > 3.5 and cwip_to_nb < 0.20:
            is_stressed = True
            stress_flag = (
                f"EXECUTION_CAPACITY_STRESS: CFR {cfr:.2f}x > 3.5x with CWIP/Net Block {cwip_to_nb:.2f} < 0.20 "
                f"(Order Book: ₹{unexecuted_order_book:,.1f}Cr exceeds operational capacity)"
            )
            haircut_points = 10.0

        return {
            "unexecuted_order_book_cr": round(unexecuted_order_book, 2),
            "net_block_cr": round(net_block, 2),
            "cwip_cr": round(cwip, 2),
            "sector_asset_turnover_benchmark": round(sector_turnover, 2),
            "capacity_feasibility_ratio": cfr,
            "cwip_to_net_block_ratio": cwip_to_nb,
            "is_capacity_stressed": is_stressed,
            "status": "EXECUTION_CAPACITY_STRESS" if is_stressed else "CAPACITY_FEASIBLE",
            "stress_flag": stress_flag,
            "haircut_points": haircut_points
        }

    @classmethod
    def evaluate_5x_operational_catalysts(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Quantifies the 4 core non-linear triggers from 'The Anatomy of a True 5x Move'.
        
        1. Capacity Inflection: CWIP / Net Block >= 30.0% transitioning into commercial production.
        2. Float Squeeze & Institutional Discovery: Low Free Float (<= 20%) + first institutional entry (>= 1.0%).
        3. Radical Deleveraging: Significant debt reduction (>= 50% or Net Debt <= 0) eliminating interest burn.
        4. Baseline Forensic Gate: Tier-1 auditor verification, clean RPTs, aligned compensation.
        """
        catalysts: Dict[str, Any] = {}
        active_notes: List[str] = []
        score = 0.0

        # 1. Capacity Inflection (CWIP / Net Block)
        cwip = float(item.get("cwip") or 0.0)
        net_block = float(item.get("net_block") or item.get("fixed_assets") or 0.0)
        cwip_ratio_pct = round((cwip / max(net_block, 1.0)) * 100.0, 1) if net_block > 0 else 0.0
        has_capex_inflection = (cwip_ratio_pct >= 30.0) or bool(item.get("cwip_inflection", False))
        catalysts["capacity_inflection"] = {
            "title": "Capacity Inflection (CWIP / Net Block >= 30%)",
            "cwip_to_net_block_pct": cwip_ratio_pct,
            "is_active": has_capex_inflection,
            "note": f"CWIP/Net Block is {cwip_ratio_pct:.1f}% (>= 30% threshold)" if has_capex_inflection else f"CWIP/Net Block at {cwip_ratio_pct:.1f}%"
        }
        if has_capex_inflection:
            score += 30.0
            active_notes.append(f"Major Capacity Inflection (CWIP {cwip_ratio_pct:.1f}% of Net Block)")

        # 2. Float Squeeze & Institutional Discovery
        promoter_h = float(item.get("promoter_holding") or 0.0)
        dii_h = float(item.get("dii_holding") or 0.0)
        fii_h = float(item.get("fii_holding") or 0.0)
        inst_h = round(dii_h + fii_h, 2)
        free_float_pct = round(max(0.0, 100.0 - promoter_h - inst_h), 1) if promoter_h > 0 else float(item.get("free_float_pct") or 50.0)
        
        has_float_squeeze = (free_float_pct <= 25.0 and inst_h >= 1.0) or bool(item.get("float_squeeze_active", False))
        catalysts["float_and_institutional"] = {
            "title": "Low Free Float (<= 25%) & First Institutional Entry (>= 1.0%)",
            "free_float_pct": free_float_pct,
            "institutional_holding_pct": inst_h,
            "is_active": has_float_squeeze,
            "note": f"Free float is {free_float_pct:.1f}%, Institutional entry is {inst_h:.1f}%"
        }
        if has_float_squeeze:
            score += 25.0
            active_notes.append(f"Institutional Discovery on Low Float (Float: {free_float_pct:.1f}%, Inst: {inst_h:.1f}%)")

        # 3. Radical Balance Sheet Deleveraging
        debt = float(item.get("debt") or item.get("total_debt") or 0.0)
        cash = float(item.get("cash") or item.get("cash_and_equivalents") or 0.0)
        prev_debt = float(item.get("prev_debt") or debt)
        debt_reduction_pct = round(((prev_debt - debt) / max(prev_debt, 1.0)) * 100.0, 1) if prev_debt > debt else 0.0
        net_debt = round(debt - cash, 1)
        has_radical_deleveraging = (debt_reduction_pct >= 50.0) or (net_debt <= 0.0 and prev_debt > 0.0) or bool(item.get("deleveraging_active", False))
        catalysts["radical_deleveraging"] = {
            "title": "Radical Deleveraging (>= 50% Debt Reduction / Net Cash Turn)",
            "debt_reduction_pct": debt_reduction_pct,
            "net_debt_cr": net_debt,
            "is_active": has_radical_deleveraging,
            "note": f"Debt reduction: {debt_reduction_pct:.1f}%, Net Debt: ₹{net_debt:.1f}Cr"
        }
        if has_radical_deleveraging:
            score += 25.0
            active_notes.append(f"Radical Deleveraging (Debt Reduced by {debt_reduction_pct:.1f}%)")

        # 4. Forensic Hygiene Baseline
        tier1_auditor = bool(item.get("tier1_auditor", True))
        rpt_clean = not bool(item.get("related_party_flag", False))
        promoter_comp_clean = float(item.get("promoter_comp_pct_of_profit") or 2.0) <= 5.0
        forensic_clean = tier1_auditor and rpt_clean and promoter_comp_clean
        catalysts["forensic_baseline"] = {
            "title": "Baseline Forensic Hygiene (Tier-1 Auditor, Clean RPT, Aligned Compensation)",
            "tier1_auditor": tier1_auditor,
            "rpt_clean": rpt_clean,
            "compensation_aligned": promoter_comp_clean,
            "is_active": forensic_clean,
            "note": f"Auditor: {'Tier-1' if tier1_auditor else 'Unverified/Small'}, RPT Clean: {rpt_clean}"
        }
        if forensic_clean:
            score += 20.0

        has_5x_catalyst = (score >= 50.0) and forensic_clean
        return {
            "catalyst_score": round(score, 1),
            "has_5x_catalyst": has_5x_catalyst,
            "active_catalysts_count": sum(1 for c in [has_capex_inflection, has_float_squeeze, has_radical_deleveraging] if c),
            "catalysts": catalysts,
            "active_catalyst_notes": active_notes,
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
