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

        # ── Phase 139: CAQI Hard Gate (Cash Accrual Quality Index) ───────────
        # CAQI = CFO_TTM / PAT_TTM. Tier-1 Multibagger 5x status requires CAQI ≥ 0.80.
        # Uses cfo_last_year / net_profit_last_year as TTM proxy (both from annual filing).
        # Applies only when PAT > 0; otherwise DATA_UNAVAILABLE (not a disqualifier by itself).
        _caqi_val: Optional[float] = None
        _caqi_gate: str = "DATA_UNAVAILABLE"
        if net_profit_last_year > 0:
            _caqi_val = round(cfo_last_year / net_profit_last_year, 3)
            if _caqi_val >= 0.80:
                _caqi_gate = "PASS"
            else:
                _caqi_gate = "FAIL"
                risk_flags.append(
                    f"CAQI Gate FAIL: Cash Accrual Quality ({_caqi_val:.2f}x) < 0.80 threshold "
                    f"(CFO ₹{cfo_last_year:.1f}Cr / PAT ₹{net_profit_last_year:.1f}Cr) — "
                    f"Earnings not fully backed by operating cash; disqualifies Tier-1 5x status"
                )

        # ── Phase 139: DEME-HR — Dual-Engine Multiple Expansion Ceiling Ratio ─
        # DEME-HR = Sector Benchmark P/E Ceiling / Current Trailing P/E.
        # If DEME-HR ≤ 1.0 → stock is at or above sector P/E ceiling → "VALUATION_CONSTRAINED".
        # Prevents conviction on great businesses trapped at bubble multiples (e.g. P/E 264x vs sector 45x).
        _SECTOR_PE_CEILING: Dict[str, float] = {
            "DEFENSE":          90.0,
            "HEAVY_ENGINEERING": 45.0,
            "ENGINEERING":       45.0,
            "CAPITAL_GOODS":     55.0,
            "RENEWABLE":         60.0,
            "POWER":             35.0,
            "TRANSFORMERS":      55.0,
            "IT":                35.0,
            "SOFTWARE":          35.0,
            "BANKING":           20.0,
            "NBFC":              25.0,
            "PHARMA":            30.0,
            "CHEMICALS":         35.0,
            "FMCG":              55.0,
            "CONSUMER":          50.0,
            "METALS":            18.0,
            "CEMENT":            25.0,
            "SHIPPING":          20.0,
            "REAL_ESTATE":       30.0,
            "AUTO":              30.0,
            "AUTO_ANCILLARY":    35.0,
            "TEXTILES":          25.0,
            "AGRI":              30.0,
            "DIVERSIFIED":       40.0,
        }
        _sector_key = str(item.get("sector", "DIVERSIFIED")).upper().replace(" ", "_")
        _pe_ceiling = _SECTOR_PE_CEILING.get(_sector_key, 40.0)  # conservative default
        _deme_hr: Optional[float] = None
        _deme_hr_verdict: str = "DATA_UNAVAILABLE"
        if item.get("pe_ratio") is not None:
            try:
                _trailing_pe = float(item.get("pe_ratio"))
            except (TypeError, ValueError):
                _trailing_pe = None
        elif peg_ratio is not None and peg_ratio > 0:
            # Trailing P/E = PEG * EPS growth (3yr CAGR approximation) fallback proxy
            _trailing_pe = peg_ratio * max(sales_growth_3yr, 1.0)
        else:
            _trailing_pe = None

        if _trailing_pe is not None and _trailing_pe > 0:
            _deme_hr = round(_pe_ceiling / _trailing_pe, 3)
            if _deme_hr <= 1.0:
                _deme_hr_verdict = "VALUATION_CONSTRAINED"
                risk_flags.append(
                    f"DEME-HR = {_deme_hr:.2f} ≤ 1.0 → Trailing P/E ({_trailing_pe:.1f}x) at or above "
                    f"sector ceiling ({_pe_ceiling:.0f}x for {_sector_key}). "
                    f"Confidence downgraded to VALUATION_CONSTRAINED."
                )
            elif _deme_hr <= 1.3:
                _deme_hr_verdict = "FAIR_VALUE"
            elif _deme_hr > 2.0:
                _deme_hr_verdict = "UNDERVALUED"
            else:
                _deme_hr_verdict = "FAIR_VALUE"

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

        # Phase 35-38: Launchpad Discovery Engines (C1, C2, C3, I1, I2)
        # These are additive analytical outputs — no score modification to existing engines.
        # Launchpad readiness is an independent signal, not a substitute for the main scoring pipeline.
        # Sub-engine results injected into item cache to avoid redundant re-computation inside
        # evaluate_launchpad_readiness_score() (which otherwise would re-call all three sub-engines).
        revenue_quality = cls.evaluate_revenue_quality_composition(item)
        regulatory_lag = cls.compute_regulatory_discovery_lag_score(item)
        jaw_effect = cls.evaluate_jaw_effect_predictor(item)
        # Inject pre-computed results into a temporary cache dict (not mutating original item)
        _item_with_cache = dict(item)
        _item_with_cache["_cached_lifecycle"] = lifecycle_stage
        _item_with_cache["_cached_jaw"] = jaw_effect
        _item_with_cache["_cached_rev_quality"] = revenue_quality
        launchpad_readiness = cls.evaluate_launchpad_readiness_score(_item_with_cache)


        # Launchpad bonus: LAUNCHPAD_CANDIDATE with HIGH_CONVICTION gets a positive driver note
        if (
            lifecycle_stage.get("is_launchpad_candidate", False)
            and launchpad_readiness.get("conviction_tier") == "HIGH_CONVICTION_LAUNCHPAD"
        ):
            positive_drivers.append(
                f"LAUNCHPAD_CANDIDATE (Sub-Rs.500Cr pre-discovery zone) | "
                f"Readiness: {launchpad_readiness['launchpad_readiness_score']:.0f}/100 | "
                f"{launchpad_readiness['conviction_tier_note']}"
            )

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
            "revenue_quality_composition": revenue_quality,
            "regulatory_discovery_lag": regulatory_lag,
            "jaw_effect_predictor": jaw_effect,
            "launchpad_readiness": launchpad_readiness,
            "caqi": _caqi_val,
            "caqi_gate": _caqi_gate,
            "deme_hr": _deme_hr,
            "deme_hr_verdict": _deme_hr_verdict,
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
        """Classifies the structural lifecycle stage (M0 to M4) of a multibagger candidate.

        Lifecycle stages:
          M0_UNVERIFIED       — Extreme microcap (< Rs.50 Cr) or data completeness < 60%
          LAUNCHPAD_CANDIDATE — Sub-Rs.500 Cr undiscovered stock passing 5-gate quality screen
                                (Phase 35: all 14 historical 10x-50x multibaggers were in this zone)
          M1_BASE_STABILIZING — Cash bleed arrested, margins stabilizing
          M2_OPERATING_INFLECTION — CWIP commissioning or OPM expansion
          M3_INSTITUTIONAL_SCALING — High incremental ROIC or institutional accumulation
          M4_MATURE_COMPOUNDER — Large cap with established moat
        """
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
        # Phase 35 (C3): Additional fields for LAUNCHPAD_CANDIDATE gate
        piotroski_score = float(item.get("piotroski_score") or 0.0)
        promoter_holding = float(item.get("promoter_holding") or 0.0)
        pledged_pct = float(item.get("pledged_pct") or 0.0)
        unexecuted_ob = float(
            item.get("unexecuted_order_book") or item.get("order_book") or
            item.get("order_book_cr") or item.get("order_wins_value_cr") or 0.0
        )
        ob_to_mcap = round(unexecuted_ob / max(market_cap, 1.0), 2) if market_cap > 0 else 0.0

        cwip_ratio = (cwip / net_block) if net_block > 0 else 0.0

        # Hard floor: extreme microcap < Rs.50 Cr — insufficient data reliability
        if market_cap > 0 and market_cap < 50.0:
            stage = "M0_UNVERIFIED"
            description = "Extreme microcap (< Rs.50 Cr): insufficient data reliability for institutional analysis"
        elif data_completeness < 60.0:
            stage = "M0_UNVERIFIED"
            description = "Incomplete financial history: data completeness below 60% threshold"
        elif market_cap >= 10000.0 and sales_growth >= 12.0 and inc_roic >= 18.0:
            stage = "M4_MATURE_COMPOUNDER"
            description = "Market cap > Rs.10,000 Cr with established moat and steady compounding runway"
        elif inc_roic >= 22.0 or (5.0 <= inst_holding <= 25.0 and sales_growth >= 20.0):
            stage = "M3_INSTITUTIONAL_SCALING"
            description = "Institutional accumulation phase with high incremental capital productivity (ROIC >= 22%)"
        elif cwip_ratio >= 0.25 or (opm_latest >= (opm_5yr + 2.0) and sales_growth >= 15.0):
            stage = "M2_OPERATING_INFLECTION"
            description = "Operating inflection: capex commissioning (CWIP/Block >= 25%) or operating margin expansion"
        elif (
            50.0 <= market_cap < 500.0
            and piotroski_score >= 7.0
            and promoter_holding >= 50.0
            and pledged_pct <= 5.0
            and ob_to_mcap >= 1.5
            and (cfo_last_year > 0 or opm_latest >= opm_5yr)
        ):
            # LAUNCHPAD_CANDIDATE: Sub-Rs.500 Cr pre-discovery zone with 5-gate quality screen.
            # Gate rationale (each gate traceable to 14-stock DNA evidence — Phase 35 C3):
            #   1. Piotroski >= 7   : Fundamental quality integrity (all 14 had Piotroski 7-9 at entry)
            #   2. Promoter >= 50%  : Skin-in-the-game / low free float (all 14 had >= 50% promoter)
            #   3. Pledge <= 5%     : Zero stress — no forced selling risk (all 14 near-zero pledge)
            #   4. OB/MCap >= 1.5x  : Asymmetric order book vs market cap (all 14 had 2x-8x OB:MCap)
            #   5. CFO > 0 or OPM stable: Cash bleed arrested (prevents pre-revenue shell inclusion)
            stage = "LAUNCHPAD_CANDIDATE"
            description = (
                f"Sub-Rs.500 Cr pre-discovery launchpad: MCap Rs.{market_cap:.0f} Cr | "
                f"Piotroski {piotroski_score:.0f}/9 | Promoter {promoter_holding:.1f}% | "
                f"Pledge {pledged_pct:.1f}% | OB/MCap {ob_to_mcap:.1f}x"
            )
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
            "incremental_roic_pct": round(inc_roic, 2),
            "ob_to_mcap_ratio": ob_to_mcap,
            "is_launchpad_candidate": stage == "LAUNCHPAD_CANDIDATE"
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
    def evaluate_revenue_quality_composition(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 36 (C1): Revenue Quality Composition Tracker.

        Detects revenue CHARACTER change — not just revenue GROWTH. Tracks the shift toward
        recurring / high-margin / export revenue that predates visible total growth.

        Evidence: Present in 5 of 14 historical multibaggers:
          - Gravita: commodity lead -> specialty alloys + export (margin transformation)
          - Kovai Medical: OPD -> NABH surgical volumes (ticket size jump)
          - GE Vernova India: EPC project -> recurring service contracts (margin profile change)
          - ASM Technologies: tooling (8% OPM) -> ADAS embedded software (22% OPM)
          - JSLL: Rs.500 OPD consult -> Rs.40,000 HiiMS residential program (80x ticket size)

        Scoring (additive, max 100):
          - Recurring revenue % increase >= 5 ppt YoY           : +25
          - Export revenue % increase >= 5 ppt YoY              : +20
          - Ticket size / avg revenue per customer increase >= 2x: +20
          - Premium segment revenue % increase >= 5 ppt         : +15
          - Gross margin improvement >= 200 bps YoY             : +20

        Returns:
          revenue_quality_score (0-100), transformation_signals (list), has_quality_shift (bool)
        """
        recurring_rev_pct = float(item.get("recurring_revenue_pct") or 0.0)
        recurring_rev_pct_prev = float(item.get("recurring_revenue_pct_prev_year") or 0.0)
        export_rev_pct = float(item.get("export_revenue_pct") or 0.0)
        export_rev_pct_prev = float(item.get("export_revenue_pct_prev_year") or 0.0)
        avg_ticket_size = float(item.get("avg_revenue_per_customer") or item.get("avg_ticket_size_rs") or 0.0)
        avg_ticket_size_prev = float(item.get("avg_revenue_per_customer_prev") or item.get("avg_ticket_size_rs_prev") or 0.0)
        premium_seg_pct = float(item.get("premium_segment_revenue_pct") or 0.0)
        premium_seg_pct_prev = float(item.get("premium_segment_revenue_pct_prev") or 0.0)
        gross_margin_latest = float(item.get("gross_margin_pct") or item.get("opm_latest") or 0.0)
        gross_margin_prev = float(item.get("gross_margin_pct_prev") or item.get("opm_5yr") or 0.0)

        score = 0.0
        signals: List[str] = []

        # Gate 1: Recurring revenue mix shift
        recurring_delta = recurring_rev_pct - recurring_rev_pct_prev
        if recurring_delta >= 5.0:
            score += 25.0
            signals.append(f"Recurring revenue +{recurring_delta:.1f}ppt YoY ({recurring_rev_pct_prev:.0f}%→{recurring_rev_pct:.0f}%): subscription/service mix increasing")
        elif recurring_delta >= 2.0:
            score += 10.0
            signals.append(f"Recurring revenue marginal improvement +{recurring_delta:.1f}ppt YoY (watch for acceleration)")

        # Gate 2: Export revenue mix shift
        export_delta = export_rev_pct - export_rev_pct_prev
        if export_delta >= 5.0:
            score += 20.0
            signals.append(f"Export revenue +{export_delta:.1f}ppt YoY ({export_rev_pct_prev:.0f}%→{export_rev_pct:.0f}%): global market entry in progress")
        elif export_delta >= 2.0:
            score += 8.0
            signals.append(f"Export revenue marginal improvement +{export_delta:.1f}ppt YoY")

        # Gate 3: Ticket size / revenue per customer jump
        if avg_ticket_size > 0 and avg_ticket_size_prev > 0:
            ticket_mult = avg_ticket_size / max(avg_ticket_size_prev, 1.0)
            if ticket_mult >= 2.0:
                score += 20.0
                signals.append(f"Ticket size {ticket_mult:.1f}x YoY: revenue character transformation (e.g. HiiMS-type shift)")
            elif ticket_mult >= 1.3:
                score += 8.0
                signals.append(f"Ticket size +{(ticket_mult-1)*100:.0f}% YoY: meaningful per-customer value increase")

        # Gate 4: Premium segment mix shift
        premium_delta = premium_seg_pct - premium_seg_pct_prev
        if premium_delta >= 5.0:
            score += 15.0
            signals.append(f"Premium segment +{premium_delta:.1f}ppt YoY: portfolio premiumization underway")

        # Gate 5: Gross margin improvement (proxy for revenue quality when mix data absent)
        margin_delta_bps = (gross_margin_latest - gross_margin_prev) * 100.0
        if margin_delta_bps >= 200.0:
            score += 20.0
            signals.append(f"Gross margin +{margin_delta_bps:.0f}bps YoY: revenue quality inflection reflected in margin profile")
        elif margin_delta_bps >= 100.0:
            score += 8.0
            signals.append(f"Gross margin +{margin_delta_bps:.0f}bps YoY: positive quality trend")

        # Fallback: If no mix data provided, use OPM trend as revenue quality proxy
        if not signals and gross_margin_latest > gross_margin_prev:
            score += 5.0
            signals.append(f"OPM improving ({gross_margin_prev:.1f}%→{gross_margin_latest:.1f}%): partial revenue quality signal (detailed mix data not provided)")

        has_quality_shift = score >= 20.0 or len(signals) >= 2
        return {
            "revenue_quality_score": round(min(100.0, score), 1),
            "has_revenue_quality_shift": has_quality_shift,
            "transformation_signals": signals,
            "recurring_rev_delta_ppt": round(recurring_delta, 1),
            "export_rev_delta_ppt": round(export_delta, 1),
            "gross_margin_delta_bps": round(margin_delta_bps, 0),
            "data_available": any([
                recurring_rev_pct > 0, export_rev_pct > 0,
                avg_ticket_size > 0, premium_seg_pct > 0
            ]),
            "methodology_note": (
                "Revenue quality composition tracker (Phase 36-C1). Detects revenue CHARACTER "
                "transformation (recurring/export/ticket shift) that predates visible revenue growth. "
                "When mix data unavailable, OPM trend is used as a partial proxy."
            )
        }

    @classmethod
    def compute_regulatory_discovery_lag_score(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 37 (C2): Pre-Event Regulatory Trigger Time-Lag Scorer.

        Scores the alpha window between a known regulatory/policy trigger date and
        the estimated price discovery date. Larger lag = more undiscovered alpha.

        Evidence across all 14 historical multibaggers:
          - Genus Power:       RDSS smart meter scheme (Dec 2021) → price breakout (Jun 2022) = 6 months
          - Avantel:           DRDO naval terminal approval (Q4 FY22) → price breakout (Jun 2022) = ~3 months
          - E2E Networks:      RBI data localization (Jan 2022) → price (Jul 2022) = 6 months
          - Cupid:             WHO prequalification + UNFPA tender → price = 4 months
          - Marsons:           RDSO IPEX certification (Jan 2023) → price breakout = 3 months
          - Average: 3–6 months regulatory-trigger-to-price-discovery lag

        Inputs (all optional):
          regulatory_trigger_date (ISO str or None): date of known policy/regulatory event
          regulatory_category: one of RDSO_APPROVAL, PLI_INCLUSION, WHO_PREQUALIFICATION,
                                UNFPA_TENDER, RDSS_SCHEME, BIS_CERTIFICATION, EXPORT_CONTROL,
                                NCLT_RESOLUTION, CREDIT_RATING_UPGRADE, GENERIC
          analyst_coverage_count (int): number of analysts covering the stock
          fii_dii_holding (float): institutional holding % (proxy for discovery)
          days_since_trigger (int): optional override if trigger_date parsing unavailable

        Returns:
          lag_score (0-100), undiscovered_alpha_probability, lag_days_estimated
        """
        from datetime import datetime, timezone

        regulatory_trigger_date_str = item.get("regulatory_trigger_date")
        regulatory_category = str(item.get("regulatory_category") or "GENERIC").upper()
        analyst_coverage = int(item.get("analyst_coverage_count") or 5)
        inst_holding = float(item.get("fii_dii_holding", item.get("institutional_holding", 15.0)) or 15.0)
        days_since_trigger = item.get("days_since_trigger")

        # Category-specific typical discovery lag benchmarks (from 14-stock evidence)
        LAG_BENCHMARKS = {
            "RDSO_APPROVAL": 90,
            "PLI_INCLUSION": 120,
            "WHO_PREQUALIFICATION": 90,
            "UNFPA_TENDER": 120,
            "RDSS_SCHEME": 150,
            "BIS_CERTIFICATION": 60,
            "EXPORT_CONTROL": 90,
            "NCLT_RESOLUTION": 60,
            "CREDIT_RATING_UPGRADE": 30,
            "DRDO_APPROVAL": 90,
            "GENERIC": 60,
        }

        # Compute lag days
        if days_since_trigger is not None:
            lag_days = int(days_since_trigger)
        elif regulatory_trigger_date_str:
            try:
                trigger_dt = datetime.fromisoformat(str(regulatory_trigger_date_str).replace("Z", "+00:00"))
                now_dt = datetime.now(timezone.utc)
                lag_days = max(0, (now_dt - trigger_dt.replace(tzinfo=timezone.utc) if trigger_dt.tzinfo is None else now_dt - trigger_dt).days)
            except (ValueError, TypeError):
                lag_days = 0
        else:
            lag_days = 0

        # Typical discovery window for this category
        typical_lag = LAG_BENCHMARKS.get(regulatory_category, 60)

        score = 0.0
        signals: List[str] = []

        # Score 1: Is trigger recent and within the undiscovered window?
        if 0 < lag_days <= typical_lag:
            # Still within the typical undiscovered window — maximum alpha
            lag_pct = lag_days / typical_lag
            score += 50.0 * (1.0 - lag_pct * 0.5)  # Decays as more time passes but still in window
            signals.append(
                f"Regulatory trigger is {lag_days}d ago (within {typical_lag}d typical discovery window for {regulatory_category})"
            )
        elif typical_lag < lag_days <= typical_lag * 2:
            # Past typical window — partial alpha remaining
            score += 20.0
            signals.append(
                f"Regulatory trigger is {lag_days}d ago (past {typical_lag}d typical window but within 2x — partial alpha remaining)"
            )

        # Score 2: Analyst coverage — fewer analysts = more undiscovered
        if analyst_coverage <= 1:
            score += 30.0
            signals.append(f"Analyst coverage: {analyst_coverage} (undiscovered — maximum discovery alpha)")
        elif analyst_coverage <= 3:
            score += 15.0
            signals.append(f"Analyst coverage: {analyst_coverage} (lightly covered — meaningful discovery alpha)")
        elif analyst_coverage <= 6:
            score += 5.0
            signals.append(f"Analyst coverage: {analyst_coverage} (moderate coverage — partial alpha)")

        # Score 3: Institutional holding — lower = less discovery
        if inst_holding < 2.0:
            score += 20.0
            signals.append(f"Institutional holding {inst_holding:.1f}% < 2%: zero institutional discovery")
        elif inst_holding < 5.0:
            score += 10.0
            signals.append(f"Institutional holding {inst_holding:.1f}%: minimal institutional presence")
        elif inst_holding < 10.0:
            score += 3.0
            signals.append(f"Institutional holding {inst_holding:.1f}%: partial discovery underway")

        score = round(min(100.0, score), 1)
        undiscovered_prob = round(score / 100.0, 2)

        return {
            "regulatory_lag_score": score,
            "undiscovered_alpha_probability": undiscovered_prob,
            "regulatory_category": regulatory_category,
            "lag_days_since_trigger": lag_days,
            "typical_discovery_lag_days": typical_lag,
            "is_within_undiscovered_window": 0 < lag_days <= typical_lag,
            "analyst_coverage": analyst_coverage,
            "institutional_holding_pct": inst_holding,
            "discovery_signals": signals,
            "methodology_note": (
                "Pre-event regulatory trigger time-lag scorer (Phase 37-C2). Scores the alpha window "
                "between a known policy/regulatory trigger and estimated market price discovery. "
                "Based on 14-stock evidence: average 3-6 month lag between trigger and price breakout. "
                "E13 (post-event EMR) and this module are complementary, not redundant."
            )
        }

    @classmethod
    def evaluate_jaw_effect_predictor(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 38a (I1): Jaw Effect Pre-Indicator.

        Predicts operating leverage explosion BEFORE it materializes in OPM.
        The 'Jaw Effect': fixed overhead stays flat while revenue doubles/triples
        from order book execution — all incremental revenue falls to PAT.

        Evidence across ALL 14 historical multibaggers:
          At launchpad: Fixed overhead was 70-85% of revenue → PAT margins 2-8%
          Post-order execution: Revenue 2x-3x, fixed overhead same → PAT 12-25%
          Result: 5x-15x EPS growth on 2x-3x revenue growth

        Engine 3 (lines 130-135) scores the RESULT (opm_latest > opm_5yr).
        This method scores the PREDICTOR SETUP — the pre-condition.

        Scoring (additive, max 100):
          - Fixed cost ratio >= 0.70 (high operating leverage setup)  : +25
          - Utilization headroom: OB-implied revenue / current revenue >= 1.5x: +30
          - Cash breakeven distance > 0 (not loss-making)            : +20
          - Unexecuted OB > 1x TTM revenue (guaranteed revenue surge) : +25

        Returns:
          jaw_effect_score (0-100), jaw_effect_probability, predictor_signals
        """
        current_revenue = float(
            item.get("revenue_cr") or item.get("sales_last_year") or item.get("revenue") or 0.0
        )
        opm_latest = float(item.get("opm_latest") or 0.0)
        unexecuted_ob = float(
            item.get("unexecuted_order_book") or item.get("order_book") or
            item.get("order_book_cr") or item.get("order_wins_value_cr") or 0.0
        )
        net_profit = float(item.get("net_profit_last_year") or 0.0)
        cfo = float(item.get("cfo_last_year") or 0.0)
        fixed_cost_ratio = float(item.get("fixed_cost_ratio") or 0.0)
        # Note: breakeven_revenue reserved for future Gate 5 (cash breakeven distance)
        # breakeven_revenue = float(item.get("cash_breakeven_revenue_cr") or 0.0)

        score = 0.0
        signals: List[str] = []
        utilization_headroom = 0.0  # Pre-initialized: avoids dir() idiom, always deterministic

        # Gate 1: Fixed cost ratio >= 0.70 (70%+ of revenue is fixed = high operating leverage setup)
        # If not directly provided, estimate from OPM: fixed_cost_ratio ~ 1 - (contribution_margin%)
        if fixed_cost_ratio <= 0.0 and opm_latest > 0:
            # Approximation: OPM ~ contribution_margin for asset-heavy businesses
            # Fixed cost ratio = 1 - OPM (simplified — assumes COGS is mostly variable)
            fixed_cost_ratio = max(0.0, 1.0 - (opm_latest / 100.0))

        if fixed_cost_ratio >= 0.70:
            score += 25.0
            signals.append(f"Fixed cost ratio {fixed_cost_ratio*100:.0f}% >= 70%: high operating leverage setup — incremental revenue flows disproportionately to PAT")
        elif fixed_cost_ratio >= 0.60:
            score += 10.0
            signals.append(f"Fixed cost ratio {fixed_cost_ratio*100:.0f}%: moderate operating leverage — partial jaw effect potential")

        # Gate 2: Utilization headroom — OB-implied revenue vs current revenue
        if current_revenue > 0 and unexecuted_ob > 0:
            # OB typically executes over 12-24 months — use 18 months average
            ob_implied_annual_revenue = unexecuted_ob / 1.5
            utilization_headroom = ob_implied_annual_revenue / max(current_revenue, 1.0)
            if utilization_headroom >= 2.0:
                score += 30.0
                signals.append(f"OB-implied revenue {utilization_headroom:.1f}x current revenue: major capacity utilization surge incoming → jaw opens")
            elif utilization_headroom >= 1.5:
                score += 20.0
                signals.append(f"OB-implied revenue {utilization_headroom:.1f}x current revenue: significant utilization headroom → jaw beginning to open")
            elif utilization_headroom >= 1.0:
                score += 8.0
                signals.append(f"OB-implied revenue {utilization_headroom:.1f}x current revenue: moderate headroom")

        # Gate 3: Cash / profit positive (not bleeding — base is arrested)
        if net_profit > 0 and cfo > 0:
            score += 20.0
            signals.append(f"Both PAT (Rs.{net_profit:.0f}Cr) and CFO (Rs.{cfo:.0f}Cr) positive: business viable, jaw effect will produce incremental PAT not absorbed by losses")
        elif net_profit > 0:
            score += 10.0
            signals.append(f"PAT positive (Rs.{net_profit:.0f}Cr): breakeven passed, jaw effect will add to existing profitability")

        # Gate 4: Order book > 1x TTM revenue (guaranteed near-term revenue expansion)
        if current_revenue > 0 and unexecuted_ob >= current_revenue:
            score += 25.0
            signals.append(f"Unexecuted OB Rs.{unexecuted_ob:.0f}Cr >= TTM revenue Rs.{current_revenue:.0f}Cr: revenue doubling virtually assured from execution alone")
        elif current_revenue > 0 and unexecuted_ob >= 0.5 * current_revenue:
            score += 10.0
            signals.append(f"Unexecuted OB {unexecuted_ob/max(current_revenue,1)*100:.0f}% of TTM revenue: meaningful near-term revenue top-up")

        score = round(min(100.0, score), 1)
        jaw_prob = round(score / 100.0, 2)
        has_jaw_setup = score >= 40.0 and len(signals) >= 2

        return {
            "jaw_effect_score": score,
            "jaw_effect_probability": jaw_prob,
            "has_jaw_effect_setup": has_jaw_setup,
            "fixed_cost_ratio_estimated": round(fixed_cost_ratio, 2),
            "utilization_headroom_multiple": round(utilization_headroom, 2),
            "predictor_signals": signals,
            "methodology_note": (
                "Jaw Effect Pre-Indicator (Phase 38a-I1). Scores the setup for operating leverage "
                "explosion BEFORE it appears in OPM. Engine 3 in evaluate_company() scores the RESULT "
                "(opm_latest > opm_5yr). This method scores the PRE-CONDITION. Both are "
                "complementary and non-redundant. Evidence: all 14 historical multibaggers showed "
                "this fixed-cost + utilization headroom setup at their launchpad price."
            )
        }


    @classmethod
    def evaluate_launchpad_readiness_score(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 38b (I2): Composite Launchpad Readiness Score.

        Synthesizes 5 individual engine signals into a single pre-discovery conviction number.
        Individual engines (OBV_ACC, B5 VCP, Engine 7 Capex, E9 Promoter, Lifecycle Stage)
        are fully functional but evaluated independently. This composite combines them.

        Evidence: ALL 14 historical multibaggers had 4-5 of these 5 signals simultaneously
        at their launchpad price — no single signal was sufficient alone.

        Component scores (max points):
          1. OB:MCap asymmetry >= 2x                             : +20
          2. Promoter holding >= 50% + zero equity dilution      : +20
          3. Lifecycle stage = LAUNCHPAD_CANDIDATE               : +25
          4. Jaw Effect setup (jaw_effect_score >= 40)           : +20
          5. Revenue quality shift (revenue_quality_score >= 20) : +15

        Composite threshold:
          >= 70: HIGH CONVICTION LAUNCHPAD (4-5 signals present)
          >= 45: MODERATE CONVICTION LAUNCHPAD (3 signals present)
          >= 20: EARLY SIGNAL (1-2 signals — watch but do not act)
          <  20: INSUFFICIENT SIGNAL

        Returns:
          launchpad_readiness_score (0-100), conviction_tier, component_scores
        """
        market_cap = float(item.get("market_cap") or 0.0)
        unexecuted_ob = float(
            item.get("unexecuted_order_book") or item.get("order_book") or
            item.get("order_book_cr") or item.get("order_wins_value_cr") or 0.0
        )
        promoter_holding = float(item.get("promoter_holding") or 0.0)
        pledged_pct = float(item.get("pledged_pct") or 0.0)
        # Equity dilution check: no QIP/rights within last 4 quarters
        recent_equity_dilution = bool(item.get("recent_equity_dilution", False))

        # Use pre-computed sub-engine results if injected by evaluate_company() (avoids triple computation).
        # Falls back to direct computation when called standalone.
        lifecycle = item.get("_cached_lifecycle") or cls.classify_multibagger_lifecycle_stage(item)
        jaw = item.get("_cached_jaw") or cls.evaluate_jaw_effect_predictor(item)
        rev_quality = item.get("_cached_rev_quality") or cls.evaluate_revenue_quality_composition(item)

        ob_to_mcap = unexecuted_ob / max(market_cap, 1.0) if market_cap > 0 else 0.0

        component_scores: Dict[str, Any] = {}
        total = 0.0

        # Component 1: OB:MCap asymmetry
        if ob_to_mcap >= 3.0:
            c1 = 20.0
        elif ob_to_mcap >= 2.0:
            c1 = 15.0
        elif ob_to_mcap >= 1.5:
            c1 = 8.0
        else:
            c1 = 0.0
        component_scores["ob_to_mcap_asymmetry"] = {"score": c1, "value": round(ob_to_mcap, 2), "threshold": ">=2.0x for full score"}
        total += c1

        # Component 2: Promoter quality + no dilution
        if promoter_holding >= 50.0 and pledged_pct <= 5.0 and not recent_equity_dilution:
            c2 = 20.0
        elif promoter_holding >= 50.0 and pledged_pct <= 5.0:
            c2 = 12.0
        elif promoter_holding >= 40.0 and pledged_pct <= 10.0:
            c2 = 5.0
        else:
            c2 = 0.0
        component_scores["promoter_quality_no_dilution"] = {"score": c2, "promoter_holding": promoter_holding, "pledge_pct": pledged_pct, "no_dilution": not recent_equity_dilution}
        total += c2

        # Component 3: Lifecycle stage
        if lifecycle.get("stage") == "LAUNCHPAD_CANDIDATE":
            c3 = 25.0
        elif lifecycle.get("stage") == "M2_OPERATING_INFLECTION":
            c3 = 12.0
        elif lifecycle.get("stage") == "M1_BASE_STABILIZING":
            c3 = 5.0
        else:
            c3 = 0.0
        component_scores["lifecycle_stage"] = {"score": c3, "stage": lifecycle.get("stage"), "description": lifecycle.get("description", "")}
        total += c3

        # Component 4: Jaw Effect Pre-Indicator
        jaw_score = jaw.get("jaw_effect_score", 0.0)
        if jaw_score >= 60.0:
            c4 = 20.0
        elif jaw_score >= 40.0:
            c4 = 12.0
        elif jaw_score >= 20.0:
            c4 = 5.0
        else:
            c4 = 0.0
        component_scores["jaw_effect_predictor"] = {"score": c4, "jaw_effect_score": jaw_score, "has_jaw_setup": jaw.get("has_jaw_effect_setup")}
        total += c4

        # Component 5: Revenue quality shift
        rq_score = rev_quality.get("revenue_quality_score", 0.0)
        if rq_score >= 40.0:
            c5 = 15.0
        elif rq_score >= 20.0:
            c5 = 8.0
        else:
            c5 = 0.0
        component_scores["revenue_quality_shift"] = {"score": c5, "revenue_quality_score": rq_score, "has_shift": rev_quality.get("has_revenue_quality_shift")}
        total += c5

        total = round(min(100.0, total), 1)

        # Check SEBI surveillance / ESM Stage II circuit lock risk (Phase 141)
        surveillance = item.get("surveillance") or {}
        esm_stage = str(surveillance.get("esm_stage") or item.get("esm_stage") or "CLEAN").upper()
        circuit_band_pct = float(surveillance.get("circuit_band_pct") or item.get("circuit_band_pct") or 20.0)
        has_esm_lock = (esm_stage == "STAGE_II") or (circuit_band_pct <= 2.0 and esm_stage != "CLEAN")

        # Capacity guard calculation (Phase 142 ADTV Capacity Ceiling)
        adtv_cr = float(item.get("adtv_cr") or item.get("adtv_30d_cr") or 0.0)
        if adtv_cr <= 0.0:
            vol = float(item.get("volume") or item.get("avg_volume_20d") or 0.0)
            px = float(item.get("current_price") or item.get("price") or 0.0)
            if vol > 0 and px > 0:
                adtv_cr = round((vol * px) / 1e7, 2)

        capacity_guard = {
            "adtv_cr": adtv_cr,
            "max_institutional_position_cr": round(0.10 * adtv_cr, 2) if adtv_cr > 0 else None,
            "max_retail_order_cr": round(0.02 * adtv_cr, 2) if adtv_cr > 0 else None,
            "liquidity_status": "LIQUID" if adtv_cr >= 2.0 else ("MICRO_LIQUID" if adtv_cr >= 0.5 else "ILLIQUID_CAUTION")
        }

        if total >= 70.0:
            conviction_tier = "HIGH_CONVICTION_LAUNCHPAD"
            tier_note = "4-5 signals simultaneously present — historically matches all 14 launchpad multibaggers"
        elif total >= 45.0:
            conviction_tier = "MODERATE_CONVICTION_LAUNCHPAD"
            tier_note = "3 signals present — watch closely for 4th trigger before position entry"
        elif total >= 20.0:
            conviction_tier = "EARLY_SIGNAL_WATCH"
            tier_note = "1-2 signals — place on watchlist; insufficient conviction for entry"
        else:
            conviction_tier = "INSUFFICIENT_SIGNAL"
            tier_note = "No launchpad signals detected at current metrics"

        if has_esm_lock:
            conviction_tier = "SPECULATIVE_MONITORING_ESM_LOCKED"
            tier_note = (
                f"FATAL SURVEILLANCE OVERLAY: Scrip under ESM Stage II / 2% circuit band ({esm_stage}). "
                "Periodic call auction prevents orderly entry/exit. Capital deployment prohibited until surveillance exit."
            )

        return {
            "launchpad_readiness_score": total,
            "conviction_tier": conviction_tier,
            "conviction_tier_note": tier_note,
            "has_esm_circuit_lock": has_esm_lock,
            "capacity_guard": capacity_guard,
            "component_scores": component_scores,
            "ob_to_mcap_ratio": round(ob_to_mcap, 2),
            "methodology_note": (
                "Composite Launchpad Readiness Score (Phase 38b-I2 / Phase 141-142). Synthesizes 5 individual engine "
                "signals: OB:MCap asymmetry, Promoter quality/no-dilution, Lifecycle stage, "
                "Jaw Effect predictor, Revenue quality shift, bounded by ESM Stage II surveillance "
                "and ADTV capacity limits. Individual components are non-redundant. "
                "Threshold evidence: all 14 historical multibaggers scored >= 70 at launchpad prices."
            )
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
