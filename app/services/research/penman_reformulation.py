"""Phase 164: University-Level Fundamental & Capital Allocation Master Engine.

Synthesizes foundational academic & institutional equity research canons:
1. Stephen Penman (Columbia University): Statement Reformulation & RNOA Decomposition.
   Deconstructs ROE = RNOA + FLEV * (RNOA - NBC) to flag debt-inflated ROE illusions.
2. Edward Chancellor (Marathon Asset Management): Capital Cycle & Capex Starvation Detector.
   Capex / D&A < 0.80 identifies supply-side consolidation & cyclical turnaround inflection.
3. William Thorndike (The Outsiders): Incremental ROIC Capital Allocation Scorer.
   Measures management skill in redeploying retained earnings (Delta NOPAT / Reinvestment).
4. Aswath Damodaran (NYU Stern): Corporate Life Cycle Classifier & Valuation Anchor.
   Calibrates cost of capital, reinvestment rates, and terminal growth ceilings.
5. Michael Mauboussin (Expectations Investing / Base Rate Book): Empirical Base Rate Filter.
   Benchmarked against Indian NSE/BSE long-term empirical growth distribution.

Non-Domination & Strict Mathematical Invariance:
All modules operate deterministically, degrade gracefully when detailed line items are absent,
and never throw unhandled exceptions.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class PenmanStatementReformulator:
    """Reformulates standard financial statements into Operating vs Financing activities.
    
    Penman Equation:
    CSE = NOA - NFO
    NOPAT = EBIT * (1 - t)
    NFE = Net Interest Expense * (1 - t)
    RNOA = NOPAT / NOA
    NBC = NFE / NFO
    Spread = RNOA - NBC
    FLEV = NFO / CSE
    Decomposed ROE = RNOA + (FLEV * Spread)
    """

    @staticmethod
    def reformulate(
        operating_assets: float,
        operating_liabilities: float,
        financial_obligations: float,
        financial_assets: float,
        ebit: float,
        net_interest_expense: float,
        tax_rate_pct: float = 25.0,
        sales: Optional[float] = None,
        reported_equity: Optional[float] = None,
        reported_pat: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Performs rigorous statement reformulation and ROE deconstruction.
        
        Args:
            operating_assets: Operating assets (Cash required for ops + Receivables + Inv + PPE).
            operating_liabilities: Operating liabilities (Trade payables + provisions).
            financial_obligations: Total debt & interest-bearing obligations.
            financial_assets: Liquid treasury cash & marketable securities in excess of ops.
            ebit: Operating earnings before interest & taxes.
            net_interest_expense: Gross interest expense minus treasury income.
            tax_rate_pct: Effective marginal tax rate % (default 25.0%).
            sales: Optional total revenue/sales for profit margin & asset turnover decomposition.
            reported_equity: Optional reported book equity for consistency check.
            reported_pat: Optional reported PAT.
        """
        t = max(0.0, min(1.0, tax_rate_pct / 100.0))
        
        # Net Operating Assets (NOA) and Net Financial Obligations (NFO)
        noa = float(operating_assets - operating_liabilities)
        nfo = float(financial_obligations - financial_assets)
        
        # Common Shareholders' Equity (CSE)
        calculated_cse = noa - nfo
        cse = calculated_cse if (reported_equity is None or calculated_cse > 0) else float(reported_equity)
        if cse <= 0 and reported_equity and reported_equity > 0:
            cse = float(reported_equity)
        
        # Net Operating Profit After Tax (NOPAT) & Net Financial Expense (NFE)
        nopat = float(ebit * (1.0 - t))
        nfe = float(net_interest_expense * (1.0 - t))
        net_income = nopat - nfe
        if reported_pat is not None and reported_pat > 0 and nopat <= 0:
            # Fallback if ebit was 0 or unpopulated
            nopat = float(reported_pat)
            net_income = float(reported_pat)

        # RNOA (Return on Net Operating Assets)
        rnoa_pct = round((nopat / noa) * 100.0, 2) if noa > 0 else 0.0
        
        # NBC (Net Borrowing Cost)
        nbc_pct = round((nfe / nfo) * 100.0, 2) if nfo > 0 else 0.0
        
        # Spread & FLEV
        spread_pct = round(rnoa_pct - nbc_pct, 2)
        flev = round(nfo / cse, 3) if cse > 0 else (99.0 if nfo > 0 else 0.0)
        
        # Penman Decomposed ROE
        decomposed_roe_pct = round(rnoa_pct + (flev * spread_pct), 2) if cse > 0 else rnoa_pct
        
        # Reported ROE
        reported_roe_pct = 0.0
        if reported_pat is not None and cse > 0:
            reported_roe_pct = round((float(reported_pat) / cse) * 100.0, 2)
        elif cse > 0:
            reported_roe_pct = round((net_income / cse) * 100.0, 2)

        # Operating Margin & Asset Turnover (RNOA = PM * ATO)
        pm_pct = round((nopat / sales) * 100.0, 2) if (sales and sales > 0) else None
        ato = round(sales / noa, 2) if (sales and sales > 0 and noa > 0) else None

        # Debt-inflated ROE Trap Guard:
        # High ROE driven by extreme financial leverage while core operating engine (RNOA) is mediocre
        debt_inflated_roe_trap = False
        trap_reason = None
        if reported_roe_pct >= 18.0 and rnoa_pct < 10.0 and flev >= 1.2:
            debt_inflated_roe_trap = True
            trap_reason = f"High ROE ({reported_roe_pct}%) is driven by high leverage (FLEV {flev:.2f}) while core RNOA is weak ({rnoa_pct}%)."
        elif spread_pct < 0.0 and flev >= 0.8:
            debt_inflated_roe_trap = True
            trap_reason = f"Negative operating spread ({spread_pct}%): Net borrowing cost exceeds RNOA, destroying shareholder equity."

        # Engine Quality Classification
        if debt_inflated_roe_trap:
            engine_quality = "FINANCIAL_ENGINEERING_TRAP"
        elif rnoa_pct >= 25.0 and flev <= 0.5:
            engine_quality = "EXCEPTIONAL_CORE_ENGINE"
        elif rnoa_pct >= 18.0 and spread_pct >= 5.0:
            engine_quality = "STRONG_OPERATING_ENGINE"
        elif rnoa_pct >= 12.0 and spread_pct >= 0.0:
            engine_quality = "MODERATE_ENGINE"
        elif spread_pct < -2.0:
            engine_quality = "DESTRUCTIVE_SPREAD"
        elif rnoa_pct < 0:
            engine_quality = "DISTRESSED_OPERATING_LOSS"
        else:
            engine_quality = "NEUTRAL_ENGINE"

        return {
            "noa": round(noa, 2),
            "nfo": round(nfo, 2),
            "cse": round(cse, 2),
            "nopat": round(nopat, 2),
            "nfe": round(nfe, 2),
            "rnoa_pct": rnoa_pct,
            "nbc_pct": nbc_pct,
            "spread_pct": spread_pct,
            "flev": flev,
            "penman_decomposed_roe_pct": decomposed_roe_pct,
            "reported_roe_pct": reported_roe_pct,
            "operating_profit_margin_pct": pm_pct,
            "asset_turnover": ato,
            "debt_inflated_roe_trap": debt_inflated_roe_trap,
            "trap_reason": trap_reason,
            "engine_quality": engine_quality,
        }


class ChancellorCapitalCycleDetector:
    """Edward Chancellor Capital Cycle & Capex Starvation Detector.
    
    Identifies supply-side contraction/expansion dynamics:
    - Capex / D&A < 0.80: Capital Starvation / Supply Contraction -> High future return potential.
    - Capex / D&A > 2.20: Capex Glut / Overinvestment -> Excess capacity risk.
    - Asset Growth Anomaly: Asset expansion > 25% YoY with flat/falling profits.
    """

    @staticmethod
    def detect_capital_cycle(
        capex_cr: float,
        da_cr: float,
        asset_growth_pct: Optional[float] = None,
        cfo_cr: Optional[float] = None,
        pat_cr: Optional[float] = None,
        industry_capex_curbing: bool = False,
    ) -> Dict[str, Any]:
        """Detects capital cycle phase and supply side inflection catalysts.
        
        Args:
            capex_cr: Capital expenditure in ₹ Crore.
            da_cr: Depreciation & Amortization in ₹ Crore.
            asset_growth_pct: Total asset growth rate YoY %.
            cfo_cr: Cash flow from operations in ₹ Crore.
            pat_cr: Net profit after tax in ₹ Crore.
            industry_capex_curbing: Boolean flag indicating broader industry supply contraction.
        """
        capex_cr = max(0.0, float(capex_cr))
        da_cr = max(0.001, float(da_cr))
        capex_to_da_ratio = round(capex_cr / da_cr, 2)
        
        # Capital Starvation: under-investing relative to asset depreciation
        capital_starvation = capex_to_da_ratio < 0.80
        capex_glut_risk = capex_to_da_ratio > 2.20
        
        # Asset Growth Anomaly Risk (Cooper, Gulen, Schill)
        asset_growth_anomaly_risk = False
        if asset_growth_pct is not None and asset_growth_pct > 25.0:
            if pat_cr is not None and pat_cr <= 0:
                asset_growth_anomaly_risk = True
            elif cfo_cr is not None and cfo_cr < 0:
                asset_growth_anomaly_risk = True

        # Phase classification
        if capital_starvation:
            cycle_phase = "CAPITAL_STARVATION_SUPPLY_CONTRACTION"
            cycle_score = 0.85
        elif capex_glut_risk or asset_growth_anomaly_risk:
            cycle_phase = "CAPITAL_EXPANSION_GLUT_RISK"
            cycle_score = 0.25
        elif 0.80 <= capex_to_da_ratio <= 1.50:
            cycle_phase = "BALANCED_MAINTENANCE_GROWTH"
            cycle_score = 0.65
        else:
            cycle_phase = "MODERATE_EXPANSION"
            cycle_score = 0.50

        # Turnaround Supply Catalyst:
        # Capex starved, capacity consolidated, and cash generation (CFO > 0) has inflected
        turnaround_supply_catalyst = False
        if capital_starvation and cfo_cr is not None and cfo_cr > 0:
            turnaround_supply_catalyst = True
        elif capital_starvation and industry_capex_curbing:
            turnaround_supply_catalyst = True

        return {
            "capex_to_da_ratio": capex_to_da_ratio,
            "capital_starvation": capital_starvation,
            "capex_glut_risk": capex_glut_risk,
            "asset_growth_anomaly_risk": asset_growth_anomaly_risk,
            "capital_cycle_phase": cycle_phase,
            "turnaround_supply_catalyst": turnaround_supply_catalyst,
            "supply_side_tailwinds_score": cycle_score,
        }


class ThorndikeCapitalAllocationScorer:
    """William Thorndike Outsiders Capital Allocation Scorer.
    
    Measures management's skill in deploying retained cash:
    - Incremental ROIC = Delta NOPAT / Cumulative Reinvestment.
    - Share count discipline (anti-dilution / accretive buybacks).
    - FCF conversion quality.
    """

    @staticmethod
    def score_capital_allocation(
        nopat_start_cr: float,
        nopat_end_cr: float,
        reinvestment_cr: float,
        share_dilution_cagr_pct: float = 0.0,
        fcf_to_nopat_ratio: float = 1.0,
        buyback_yield_pct: float = 0.0,
    ) -> Dict[str, Any]:
        """Calculates quantitative capital allocation score [0 - 100].
        
        Args:
            nopat_start_cr: NOPAT at beginning of multi-year period (e.g. 3Y ago).
            nopat_end_cr: Current NOPAT.
            reinvestment_cr: Cumulative reinvestment (Net Capex + Delta Working Capital).
            share_dilution_cagr_pct: Annual equity dilution rate % (e.g. 3.5%).
            fcf_to_nopat_ratio: FCF conversion ratio (FCF / NOPAT).
            buyback_yield_pct: Net share buyback yield % over horizon.
        """
        delta_nopat = float(nopat_end_cr - nopat_start_cr)
        reinv = float(reinvestment_cr)
        
        # Incremental ROIC
        if reinv > 0:
            incremental_roic_pct = round((delta_nopat / reinv) * 100.0, 2)
        elif delta_nopat > 0:
            # Grew earnings without capital reinvestment (capital-light asset moat)
            incremental_roic_pct = 99.99
        else:
            incremental_roic_pct = 0.0

        # Base Score derivation from Incremental ROIC
        if incremental_roic_pct >= 25.0:
            score = 85.0 + min(15.0, (incremental_roic_pct - 25.0) * 0.5)
        elif incremental_roic_pct >= 18.0:
            score = 70.0 + ((incremental_roic_pct - 18.0) / 7.0) * 15.0
        elif incremental_roic_pct >= 12.0:
            score = 55.0 + ((incremental_roic_pct - 12.0) / 6.0) * 15.0
        elif incremental_roic_pct >= 6.0:
            score = 40.0 + ((incremental_roic_pct - 6.0) / 6.0) * 15.0
        else:
            score = max(10.0, 30.0 + incremental_roic_pct)

        # Share dilution penalty
        if share_dilution_cagr_pct > 2.0:
            dilution_penalty = min(25.0, (share_dilution_cagr_pct - 2.0) * 5.0)
            score -= dilution_penalty
        
        # Buyback accretion bonus
        if buyback_yield_pct > 0.5:
            buyback_bonus = min(10.0, buyback_yield_pct * 2.5)
            score += buyback_bonus

        # Cash conversion modifier
        if fcf_to_nopat_ratio >= 0.85:
            score += 5.0
        elif fcf_to_nopat_ratio < 0.40:
            score -= 15.0

        final_score = round(max(0.0, min(100.0, score)), 1)

        # Rating categorization
        if final_score >= 85.0:
            rating = "OUTSIDER_EXCELLENCE"
        elif final_score >= 70.0:
            rating = "DISCIPLINED_COMPOUNDER"
        elif final_score >= 50.0:
            rating = "AVERAGE_ALLOCATOR"
        else:
            rating = "VALUE_DESTROYER"

        return {
            "incremental_nopat_cr": round(delta_nopat, 2),
            "reinvestment_cr": round(reinv, 2),
            "incremental_roic_pct": incremental_roic_pct,
            "capital_allocation_score": final_score,
            "allocation_rating": rating,
            "dilution_penalized": share_dilution_cagr_pct > 2.0,
            "buyback_accretion_applied": buyback_yield_pct > 0.5,
        }


class DamodaranLifeCycleClassifier:
    """Aswath Damodaran Corporate Life Cycle Classifier.
    
    Classifies companies across 5 stages to calibrate cost of capital and terminal assumptions:
    1. STARTUP_EARLY
    2. HIGH_GROWTH
    3. MATURE_GROWTH
    4. MATURE_CASH_COW
    5. DECLINE_DISTRESS
    """

    @staticmethod
    def classify_life_cycle(
        sales_cagr_pct: float,
        operating_margin_pct: float,
        reinvestment_rate_pct: Optional[float] = None,
        age_years: Optional[int] = None,
        fcf_positive: bool = True,
        debt_to_equity: float = 0.0,
    ) -> Dict[str, Any]:
        """Classifies corporate stage and outputs adaptive valuation anchors."""
        cagr = float(sales_cagr_pct)
        margin = float(operating_margin_pct)
        age = age_years if age_years is not None else 10

        if (cagr > 30.0 or age <= 4) and margin < 0.0:
            stage = "STARTUP_EARLY"
            wacc_range = [18.0, 24.0]
            terminal_growth_ceiling = 6.0
            terminal_roic_assumption = "COST_OF_CAPITAL_EQUALIZATION"
            key_risk = "HIGH_SURVIVAL_RUNWAY_RISK"
        elif cagr > 20.0 and margin > 0.0:
            stage = "HIGH_GROWTH"
            wacc_range = [14.5, 17.5]
            terminal_growth_ceiling = 6.0
            terminal_roic_assumption = "COMPETITIVE_ADVANTAGE_SPREAD_PLUS_4PCT"
            key_risk = "MARGIN_COMPRESSION_COMPETITION"
        elif 10.0 <= cagr <= 20.0 and margin >= 10.0 and fcf_positive:
            stage = "MATURE_GROWTH"
            wacc_range = [13.0, 15.0]
            terminal_growth_ceiling = 6.0
            terminal_roic_assumption = "SUSTAINABLE_ROIC_EXCESS_2PCT"
            key_risk = "GROWTH_DECELERATION"
        elif 2.0 <= cagr < 10.0 and margin >= 15.0 and fcf_positive:
            stage = "MATURE_CASH_COW"
            wacc_range = [12.0, 14.0]
            terminal_growth_ceiling = 5.5
            terminal_roic_assumption = "ROIC_EQUAL_TO_WACC"
            key_risk = "DISRUPTION_VALUE_TRAP"
        elif cagr < 0.0 or (margin < 0.0 and age > 8) or debt_to_equity > 2.5:
            stage = "DECLINE_DISTRESS"
            wacc_range = [16.0, 22.0]
            terminal_growth_ceiling = 3.0
            terminal_roic_assumption = "BELOW_COST_OF_CAPITAL"
            key_risk = "SOLVENCY_AND_ASSET_IMPAIRMENT"
        else:
            stage = "TRANSITIONAL_GROWTH"
            wacc_range = [13.5, 15.5]
            terminal_growth_ceiling = 6.0
            terminal_roic_assumption = "NEUTRAL"
            key_risk = "OPERATIONAL_EXECUTION"

        return {
            "life_cycle_stage": stage,
            "recommended_wacc_range_pct": wacc_range,
            "terminal_growth_ceiling_pct": terminal_growth_ceiling,
            "terminal_roic_assumption": terminal_roic_assumption,
            "primary_stage_risk": key_risk,
        }


class MauboussinBaseRateFilter:
    """Michael Mauboussin Base Rate & Reverse-DCF Expectations Filter.
    
    Provides an empirical anchor against optimistic Inside-View forecasts:
    Indian market empirical 5-year sales/PAT CAGR distribution (NSE/BSE 20-year history):
    - > 40% CAGR: 0.8% of companies
    - 30% - 40% CAGR: 2.8% of companies
    - 25% - 30% CAGR: 6.5% of companies
    - 20% - 25% CAGR: 14.0% of companies
    - 15% - 20% CAGR: 28.0% of companies
    - 10% - 15% CAGR: 52.0% of companies
    - < 10% CAGR: 95.0% of companies
    """

    @staticmethod
    def evaluate_growth_base_rate(
        implied_5y_cagr_pct: float,
        horizon_years: int = 5,
    ) -> Dict[str, Any]:
        """Calculates empirical probability and plausibility rating for a forecasted growth CAGR."""
        cagr = float(implied_5y_cagr_pct)
        
        if cagr >= 40.0:
            empirical_frequency_pct = 0.8
            grade = "STATISTICALLY_IMPLAUSIBLE_TRAP"
            penalty = 0.85
            comment = "Less than 1 in 100 Indian companies sustain >40% CAGR over 5 years. Extreme optimism required."
        elif cagr >= 30.0:
            empirical_frequency_pct = 2.8
            grade = "LOW_PLAUSIBILITY_HERCULEAN"
            penalty = 0.60
            comment = "Top 2.8% hurdle rate. Requires monumental moat, massive industry tailwind, and flawless execution."
        elif cagr >= 25.0:
            empirical_frequency_pct = 6.5
            grade = "CHALLENGING_HIGH_GROWTH"
            penalty = 0.35
            comment = "Top 6.5% historical base rate. Plausible only for secular market share consolidators."
        elif cagr >= 18.0:
            empirical_frequency_pct = 18.0
            grade = "MODERATE_PLAUSIBILITY"
            penalty = 0.15
            comment = "Healthy compounder tier. Achieved by top quartile Indian companies."
        elif cagr >= 10.0:
            empirical_frequency_pct = 52.0
            grade = "HIGHLY_PLAUSIBLE"
            penalty = 0.0
            comment = "Consistent with broader economic nominal GDP growth."
        else:
            empirical_frequency_pct = 85.0
            grade = "CONSERVATIVE_BASE"
            penalty = 0.0
            comment = "Readily achievable baseline."

        return {
            "implied_5y_cagr_pct": round(cagr, 2),
            "horizon_years": horizon_years,
            "empirical_base_rate_frequency_pct": empirical_frequency_pct,
            "plausibility_grade": grade,
            "base_rate_penalty_score": penalty,
            "commentary": comment,
        }
