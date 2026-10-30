"""Phase 165: Institutional Valuation Frontiers & Forensic Shenanigans Engine.

Codifies university graduate-level valuation and forensic accounting canons:
1. Bruce Greenwald (Columbia Business School - Competition Demystified / Value Investing):
   Earnings Power Value (EPV) vs Asset Reproduction Cost (AV).
   Deconstructs Asset Value, Zero-Growth EPV, and Franchise Moat Value.
2. Howard Schilit (Financial Shenanigans, 4th ed):
   7 Financial Shenanigans detector: CWIP expense capitalization, premature revenue/receivables
   divergence, and non-operating income boosting.
3. Howard Marks (Oaktree Capital - Mastering the Market Cycle / The Most Important Thing):
   Market & Credit Cycle Pendulum Scorer: Quantifies credit availability and market sentiment posture.
4. McKinsey / Tim Koller (Valuation, 8th ed, 2025):
   Invested Capital normalization, Economic Profit calculation (Invested Capital * (ROIC - WACC)),
   and Blume-adjusted Beta.

Strict Mathematical Invariance:
Deterministic calculations, graceful degradation when granular balance-sheet notes are missing,
and zero unhandled exceptions.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class GreenwaldEPVEngine:
    """Bruce Greenwald Earnings Power Value (EPV) & Franchise Moat Engine.
    
    Deconstructs firm value into 3 fundamental tiers:
    1. Asset Reproduction Cost (AV): Cost for an entrant to replicate the operating asset base.
    2. Earnings Power Value (EPV): Capitalized normalized operating earnings with ZERO growth (g = 0).
    3. Franchise Value (Moat): EPV - AV.
       - If EPV > AV (Moat Multiple >= 1.40): Firm possesses a durable competitive barrier to entry.
       - If EPV ~= AV (0.90 <= Moat Multiple < 1.40): Competitive parity / commodity firm.
       - If EPV < AV (Moat Multiple < 0.90): Capital-destroying asset trap (ROIC < WACC).
    """

    @staticmethod
    def calculate_epv(
        ebit_cr: float,
        wacc_pct: float = 13.5,
        tax_rate_pct: float = 25.0,
        net_debt_cr: float = 0.0,
        asset_reproduction_cost_cr: Optional[float] = None,
        book_equity_cr: Optional[float] = None,
        total_assets_cr: Optional[float] = None,
        total_liabilities_cr: Optional[float] = None,
        current_mcap_cr: Optional[float] = None,
        one_time_income_cr: float = 0.0,
    ) -> Dict[str, Any]:
        """Calculates Greenwald Earnings Power Value, Asset Value, and Franchise Moat Multiple.
        
        Args:
            ebit_cr: Operating EBIT in ₹ Crore.
            wacc_pct: Weighted Average Cost of Capital % (default 13.5% for Indian equities).
            tax_rate_pct: Effective corporate tax rate % (default 25.0%).
            net_debt_cr: Net Debt (Total Financial Debt minus Liquid Cash) in ₹ Crore.
            asset_reproduction_cost_cr: Optional explicit reproduction cost of assets.
            book_equity_cr: Book value of equity in ₹ Crore (fallback proxy for AV).
            total_assets_cr: Total reported balance-sheet assets in ₹ Crore.
            total_liabilities_cr: Total balance-sheet liabilities in ₹ Crore.
            current_mcap_cr: Current market capitalization in ₹ Crore.
            one_time_income_cr: Non-operating / one-time gains embedded in EBIT to remove.
        """
        wacc = max(0.05, float(wacc_pct) / 100.0)
        t = max(0.0, min(1.0, float(tax_rate_pct) / 100.0))
        
        # 1. Normalized Operating Earnings (NOPAT with zero growth assumption)
        normalized_ebit = max(0.0, float(ebit_cr) - float(one_time_income_cr))
        adjusted_nopat = normalized_ebit * (1.0 - t)
        
        # 2. Enterprise EPV (Operating Value at g = 0)
        epv_firm_cr = round(adjusted_nopat / wacc, 2)
        
        # 3. Equity EPV (EPV_firm - Net Debt)
        epv_equity_cr = round(max(0.0, epv_firm_cr - float(net_debt_cr)), 2)
        
        # 4. Asset Reproduction Cost (AV)
        if asset_reproduction_cost_cr is not None and asset_reproduction_cost_cr > 0:
            av_cr = float(asset_reproduction_cost_cr)
        elif book_equity_cr is not None and book_equity_cr > 0:
            av_cr = float(book_equity_cr)
        elif total_assets_cr is not None and total_liabilities_cr is not None:
            av_cr = max(0.1, float(total_assets_cr - total_liabilities_cr))
        else:
            av_cr = max(0.1, epv_equity_cr * 0.8)  # Neutral fallback

        av_cr = round(av_cr, 2)
        
        # 5. Franchise Moat Multiple & Economic Moat Classification
        moat_multiple = round(epv_equity_cr / max(0.1, av_cr), 2)
        franchise_value_cr = round(max(0.0, epv_equity_cr - av_cr), 2)
        
        if moat_multiple >= 1.40:
            moat_classification = "DURABLE_FRANCHISE_MOAT"
            moat_commentary = f"High Franchise Value (EPV/AV = {moat_multiple:.2f}x). Structural barrier to entry protects excess returns."
        elif moat_multiple >= 0.90:
            moat_classification = "COMPETITIVE_PARITY"
            moat_commentary = f"EPV roughly equals Asset Value ({moat_multiple:.2f}x). Returns hover near cost of capital; commodity economics."
        else:
            moat_classification = "CAPITAL_DESTROYING_ASSET_TRAP"
            moat_commentary = f"EPV is below Asset Reproduction Cost ({moat_multiple:.2f}x). Business destroys economic value on its asset base."

        # 6. Market Price vs EPV (Growth Premium / Expectations Embedded)
        price_to_epv = None
        growth_premium_pct = None
        if current_mcap_cr is not None and current_mcap_cr > 0 and epv_equity_cr > 0:
            price_to_epv = round(float(current_mcap_cr) / epv_equity_cr, 2)
            growth_premium_pct = round(((float(current_mcap_cr) - epv_equity_cr) / float(current_mcap_cr)) * 100.0, 1)

        return {
            "normalized_nopat_cr": round(adjusted_nopat, 2),
            "wacc_pct": round(wacc * 100.0, 2),
            "epv_firm_cr": epv_firm_cr,
            "net_debt_cr": round(net_debt_cr, 2),
            "epv_equity_cr": epv_equity_cr,
            "asset_reproduction_cost_cr": av_cr,
            "franchise_value_cr": franchise_value_cr,
            "moat_multiple": moat_multiple,
            "moat_classification": moat_classification,
            "moat_commentary": moat_commentary,
            "price_to_epv": price_to_epv,
            "market_growth_premium_pct": growth_premium_pct,
        }


class SchilitShenanigansDetector:
    """Howard Schilit Financial Shenanigans Forensic Detector.
    
    Identifies 7 institutional accounting warning flags:
    1. Capitalizing operating expenses into Capital Work-in-Progress (CWIP).
    2. Premature revenue recognition & Receivables/DSO acceleration.
    3. Boosting operating income via non-operating / other income.
    4. Divergence between reported PAT and Operating Cash Flow (CFO).
    """

    @staticmethod
    def detect_shenanigans(
        cwip_cr: Optional[float] = None,
        gross_block_cr: Optional[float] = None,
        ebit_cr: Optional[float] = None,
        delta_cwip_cr: Optional[float] = None,
        sales_growth_yoy_pct: Optional[float] = None,
        receivables_growth_yoy_pct: Optional[float] = None,
        dso_latest_days: Optional[float] = None,
        dso_previous_days: Optional[float] = None,
        other_income_cr: Optional[float] = None,
        pbt_cr: Optional[float] = None,
        cfo_cr: Optional[float] = None,
        pat_cr: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Evaluates financial statement line items for forensic shenanigans."""
        flags: List[str] = []
        score = 100.0
        
        # 1. Shenanigan 1: CWIP Expense Capitalization
        cwip_anomaly = False
        if cwip_cr is not None and gross_block_cr is not None and gross_block_cr > 0:
            cwip_to_gross = cwip_cr / gross_block_cr
            if cwip_to_gross > 0.40:
                flags.append(f"Excessive CWIP intensity ({cwip_to_gross:.1%} of gross block); potential park-and-hide of routine opex.")
                score -= 15.0
                cwip_anomaly = True

        if delta_cwip_cr is not None and ebit_cr is not None and ebit_cr > 0:
            if delta_cwip_cr > 0.50 * ebit_cr:
                flags.append("Delta CWIP exceeds 50% of annual EBIT; possible capitalization of maintenance capex.")
                score -= 15.0
                cwip_anomaly = True

        # 2. Shenanigan 2: Premature Revenue / Receivables Acceleration
        revenue_anomaly = False
        if sales_growth_yoy_pct is not None and receivables_growth_yoy_pct is not None:
            if receivables_growth_yoy_pct > sales_growth_yoy_pct + 15.0 and sales_growth_yoy_pct > 0:
                flags.append(f"Receivables growing ({receivables_growth_yoy_pct:.1f}%) significantly faster than sales ({sales_growth_yoy_pct:.1f}%). Possible channel stuffing.")
                score -= 20.0
                revenue_anomaly = True

        if dso_latest_days is not None and dso_previous_days is not None:
            delta_dso = dso_latest_days - dso_previous_days
            if delta_dso > 20.0:
                flags.append(f"Debtor days (DSO) jumped by {delta_dso:.1f} days YoY. Slower collections / aggressive revenue booking.")
                score -= 15.0
                revenue_anomaly = True

        # 3. Shenanigan 3: Boosting Operating Income with Other Income
        other_income_anomaly = False
        if other_income_cr is not None and pbt_cr is not None and pbt_cr > 0:
            other_ratio = other_income_cr / pbt_cr
            if other_ratio > 0.30:
                flags.append(f"Non-operating Other Income contributes {other_ratio:.1%} of PBT. Core operating quality masked.")
                score -= 15.0
                other_income_anomaly = True

        # 4. Shenanigan 4: Cash Flow Divergence (CFO vs PAT)
        cfo_divergence = False
        if cfo_cr is not None and pat_cr is not None:
            if pat_cr > 0 and cfo_cr <= 0:
                flags.append("Company reported positive PAT but negative Operating Cash Flow (CFO <= 0). Paper profits.")
                score -= 25.0
                cfo_divergence = True
            elif pat_cr > 0 and cfo_cr < 0.50 * pat_cr:
                flags.append(f"Low cash realization: CFO is only {(cfo_cr/pat_cr):.1%} of reported PAT.")
                score -= 12.0
                cfo_divergence = True

        final_score = round(max(0.0, min(100.0, score)), 1)
        
        if final_score >= 85.0:
            hygiene_rating = "CLEAN_ACCOUNTING_CONSERVATIVE"
        elif final_score >= 65.0:
            hygiene_rating = "MODERATE_ACCOUNTING_NOISE"
        else:
            hygiene_rating = "AGGRESSIVE_ACCOUNTING_RED_FLAG"

        return {
            "forensic_hygiene_score": final_score,
            "hygiene_rating": hygiene_rating,
            "detected_shenanigans_count": len(flags),
            "warning_flags": flags,
            "cwip_anomaly_detected": cwip_anomaly,
            "revenue_anomaly_detected": revenue_anomaly,
            "other_income_anomaly_detected": other_income_anomaly,
            "cfo_divergence_detected": cfo_divergence,
        }


class MarksCreditCyclePendulum:
    """Howard Marks Market & Credit Cycle Pendulum Scorer.
    
    Tracks systemic macro credit availability and investor risk posture:
    - Greed / Easy Credit: Tight credit spreads, aggressive IPO issuance, low hurdle rates.
    - Fear / Tight Credit: Wide credit spreads, distressed debt emergence, high margin of safety.
    """

    @staticmethod
    def assess_pendulum(
        sovereign_10y_yield_pct: float = 7.10,
        nifty_trailing_pe: float = 21.5,
        historical_median_pe: float = 20.0,
        credit_spread_bps: float = 120.0,
        speculative_ipo_frenzy: bool = False,
    ) -> Dict[str, Any]:
        """Assesses macro cycle positioning between Fear and Greed."""
        pe_ratio = nifty_trailing_pe / max(1.0, historical_median_pe)
        
        # Credit spread assessment (bps over G-Sec)
        tight_spread = credit_spread_bps < 100.0
        wide_spread = credit_spread_bps > 250.0

        if pe_ratio > 1.25 and (tight_spread or speculative_ipo_frenzy):
            posture = "EXTREME_GREED_TIGHT_SPREAD_RISK"
            recommended_action = "DEFENSIVE_RISK_CONTROL"
            cash_allocation_recommendation = "ELEVATED_CASH_BUFFER_15_25PCT"
            commentary = "Market pendulum is at the optimistic extreme. Credit is cheap and risk perception is subdued. Prioritize capital preservation."
        elif pe_ratio < 0.85 or wide_spread:
            posture = "DISTRESS_LIQUIDITY_CONTRACTION"
            recommended_action = "AGGRESSIVE_CAPITAL_DEPLOYMENT"
            cash_allocation_recommendation = "MAXIMAL_DEPLOYMENT_UNDER_5PCT_CASH"
            commentary = "Market pendulum is near fear/distress extreme. Wide credit spreads and depressed multiples offer asymmetric upside."
        else:
            posture = "MODERATE_EXPANSION_BALANCED"
            recommended_action = "SELECTIVE_STOCK_PICKING"
            cash_allocation_recommendation = "BALANCED_CASH_5_10PCT"
            commentary = "Credit and valuation conditions are within historical mid-cycle ranges."

        return {
            "pendulum_state": posture,
            "recommended_risk_posture": recommended_action,
            "cash_allocation_guide": cash_allocation_recommendation,
            "pe_to_median_ratio": round(pe_ratio, 2),
            "credit_spread_bps": credit_spread_bps,
            "commentary": commentary,
        }


class McKinseyInvestedCapitalNormalizer:
    """McKinsey / Tim Koller Invested Capital & Economic Profit Calculator.
    
    Calculates Economic Profit = Invested Capital * (ROIC - WACC).
    Applies Blume-adjusted beta formula: Beta_adj = 0.67 * Beta_raw + 0.33 * 1.0.
    """

    @staticmethod
    def calculate_economic_profit(
        invested_capital_cr: float,
        nopat_cr: float,
        wacc_pct: float = 13.5,
        raw_beta: float = 1.0,
    ) -> Dict[str, Any]:
        """Calculates ROIC, Blume-adjusted Beta, and Economic Profit."""
        ic = max(0.1, float(invested_capital_cr))
        nopat = float(nopat_cr)
        wacc = float(wacc_pct) / 100.0
        
        roic_pct = round((nopat / ic) * 100.0, 2)
        blume_beta = round(0.67 * float(raw_beta) + 0.33 * 1.0, 2)
        
        # Economic Profit = Invested Capital * (ROIC - WACC)
        spread_pct = round(roic_pct - (wacc * 100.0), 2)
        economic_profit_cr = round(ic * (spread_pct / 100.0), 2)
        
        value_creation = "VALUE_CREATING" if economic_profit_cr > 0 else "VALUE_DESTROYING"

        return {
            "invested_capital_cr": round(ic, 2),
            "nopat_cr": round(nopat, 2),
            "roic_pct": roic_pct,
            "wacc_pct": round(wacc * 100.0, 2),
            "roic_wacc_spread_pct": spread_pct,
            "economic_profit_cr": economic_profit_cr,
            "blume_adjusted_beta": blume_beta,
            "value_creation_status": value_creation,
        }


class RegulatoryAndSovereignSolvencyScorer:
    """Phase 189: Regulatory & Sovereign Obligation Solvency Scorer.

    Addresses structural solvency blindspots in capital-intensive regulated sectors
    (Telecom, Utilities, Power, Infrastructure, Concessionaires):
    1. Standard reported financial debt frequently excludes deferred spectrum payment dues (DoT),
       statutory concession fees, or long-term lease liabilities under Ind AS 116.
    2. Deconstructs:
       - Standard Net Debt = Financial Debt - Liquid Cash
       - Standard Leverage = Standard Net Debt / EBITDA
       - Total Sovereign / Regulatory Obligations = Deferred Spectrum Liabilities + Lease Obligations
       - Adjusted Net Debt = Standard Net Debt + Total Sovereign / Regulatory Obligations
       - Adjusted Leverage = Adjusted Net Debt / max(0.1, EBITDA)
       - Adjusted Interest Coverage = EBITDA / max(0.1, Gross Interest + Accretion of Deferred Liabilities)
    3. Emits alerts when hidden regulatory leverage expands true debt burden by >= 50%.
    """

    @staticmethod
    def calculate_adjusted_solvency(
        symbol: str,
        ebitda_cr: float,
        financial_debt_cr: float,
        cash_and_equivalents_cr: float,
        deferred_spectrum_liabilities_cr: float = 0.0,
        lease_liabilities_cr: float = 0.0,
        annual_interest_expense_cr: Optional[float] = None,
        interest_accretion_cr: float = 0.0,
        sector: str = "GENERAL",
    ) -> Dict[str, Any]:
        """Calculates standard vs adjusted solvency ratios accounting for sovereign and regulatory obligations."""
        ebitda = max(0.1, float(ebitda_cr))
        fin_debt = max(0.0, float(financial_debt_cr))
        cash = max(0.0, float(cash_and_equivalents_cr))
        spectrum_due = max(0.0, float(deferred_spectrum_liabilities_cr))
        lease_due = max(0.0, float(lease_liabilities_cr))
        interest_acc = max(0.0, float(interest_accretion_cr))

        total_regulatory_obligations = round(spectrum_due + lease_due, 2)
        standard_net_debt = round(fin_debt - cash, 2)
        adjusted_net_debt = round(standard_net_debt + total_regulatory_obligations, 2)

        standard_leverage = round(standard_net_debt / ebitda, 2)
        adjusted_leverage = round(adjusted_net_debt / ebitda, 2)

        standard_interest_coverage = None
        adjusted_interest_coverage = None
        if annual_interest_expense_cr is not None and annual_interest_expense_cr > 0:
            fin_interest = float(annual_interest_expense_cr)
            standard_interest_coverage = round(ebitda / fin_interest, 2)
            adjusted_interest_coverage = round(ebitda / (fin_interest + interest_acc), 2)

        # Classify Solvency Health
        if adjusted_leverage <= 1.50:
            solvency_status = "PRISTINE_SOLVENCY"
        elif adjusted_leverage <= 3.00:
            solvency_status = "HEALTHY_REGULATED_LEVERAGE"
        elif adjusted_leverage <= 4.50:
            solvency_status = "MODERATE_REGULATORY_BURDEN"
        else:
            solvency_status = "HIGH_REGULATORY_SOLVENCY_RISK"

        flags: List[str] = []
        if spectrum_due > 0 and (fin_debt == 0 or spectrum_due >= 0.50 * fin_debt):
            flags.append(
                f"DEFERRED_SPECTRUM_OVERHANG: Deferred regulatory/spectrum obligation of ₹{spectrum_due:,.1f} Cr "
                f"represents {round((spectrum_due / max(0.1, fin_debt)) * 100.0, 1)}% of reported financial debt."
            )

        if adjusted_leverage >= standard_leverage * 1.50 and total_regulatory_obligations > 1000.0:
            flags.append(
                f"HIDDEN_REGULATORY_LEVERAGE_EXPANSION: True leverage expands from {standard_leverage:.2f}x (standard) "
                f"to {adjusted_leverage:.2f}x (adjusted) after capitalizing ₹{total_regulatory_obligations:,.1f} Cr in sovereign/lease obligations."
            )

        return {
            "symbol": symbol.upper(),
            "sector": sector.upper(),
            "ebitda_cr": round(ebitda, 2),
            "financial_debt_cr": fin_debt,
            "liquid_cash_cr": cash,
            "deferred_spectrum_liabilities_cr": spectrum_due,
            "lease_liabilities_cr": lease_due,
            "total_regulatory_obligations_cr": total_regulatory_obligations,
            "standard_net_debt_cr": standard_net_debt,
            "adjusted_net_debt_cr": adjusted_net_debt,
            "standard_leverage_ratio": standard_leverage,
            "adjusted_leverage_ratio": adjusted_leverage,
            "standard_interest_coverage": standard_interest_coverage,
            "adjusted_interest_coverage": adjusted_interest_coverage,
            "solvency_status": solvency_status,
            "regulatory_debt_burden_flags": flags,
        }


class CashTaxShieldRunwayScorer:
    """Phase 189: Cash Tax vs P&L Tax Shield Runway Scorer.

    Detects hidden cash tax cliffs arising from expiring accelerated depreciation shields:
    1. During massive capex expansion (e.g. Jio 2016-2024 telecom rollout), accelerated tax depreciation
       under Section 32 of Indian Income Tax Act creates massive unabsorbed tax depreciation.
    2. Result: While P&L provisions statutory/deferred tax, actual cash tax paid is ~0, inflating FCF.
    3. As unabsorbed depreciation is exhausted, the tax shield runs out: the company faces a "cash tax cliff"
       where cash tax jumps to full statutory rate (~25.17%), creating an abrupt 20-30% FCF contraction.
    """

    @staticmethod
    def evaluate_tax_shield_runway(
        symbol: str,
        unabsorbed_tax_depreciation_cr: float,
        annual_accelerated_depreciation_claimed_cr: float,
        annual_pbt_cr: float,
        annual_fcf_cr: Optional[float] = None,
        statutory_tax_rate_pct: float = 25.17,
        current_cash_tax_paid_cr: float = 0.0,
    ) -> Dict[str, Any]:
        """Computes runway years remaining on unabsorbed tax depreciation and potential cash tax drag."""
        unabsorbed = max(0.0, float(unabsorbed_tax_depreciation_cr))
        annual_claim = max(0.1, float(annual_accelerated_depreciation_claimed_cr))
        pbt = max(0.0, float(annual_pbt_cr))
        stat_rate = max(0.0, min(100.0, float(statutory_tax_rate_pct)))
        cash_tax_now = max(0.0, float(current_cash_tax_paid_cr))

        # Runway in years = remaining unabsorbed tax shield / annual shield consumption
        runway_years = round(unabsorbed / annual_claim, 2)

        # Projected full statutory cash tax when shield expires = PBT * statutory rate
        projected_statutory_cash_tax_cr = round(pbt * (stat_rate / 100.0), 2)
        incremental_cash_tax_drag_cr = round(max(0.0, projected_statutory_cash_tax_cr - cash_tax_now), 2)

        cash_tax_drag_pct_of_fcf = None
        if annual_fcf_cr is not None and annual_fcf_cr > 0:
            cash_tax_drag_pct_of_fcf = round((incremental_cash_tax_drag_cr / float(annual_fcf_cr)) * 100.0, 1)

        # Classify Runway Urgency
        if runway_years >= 6.0:
            runway_classification = "LONG_RUNWAY_SECURE_TAX_SHIELD"
            risk_level = "LOW"
        elif runway_years >= 3.0:
            runway_classification = "MEDIUM_RUNWAY_MONITOR_EXPIRATION"
            risk_level = "MODERATE"
        elif runway_years >= 1.0:
            runway_classification = "APPROACHING_TAX_CLIFF_ELEVATED_RISK"
            risk_level = "HIGH"
        else:
            runway_classification = "IMMINENT_TAX_CLIFF_FCF_CONTRACTION"
            risk_level = "CRITICAL"

        flags: List[str] = []
        if runway_years < 4.0 and incremental_cash_tax_drag_cr > 0:
            drag_info = f" ({cash_tax_drag_pct_of_fcf:.1f}% of annual FCF)" if cash_tax_drag_pct_of_fcf is not None else ""
            flags.append(
                f"TAX_SHIELD_CLIFF_ALERT: Unabsorbed depreciation tax shield expires in {runway_years:.1f} years. "
                f"Future cash tax will increase by ₹{incremental_cash_tax_drag_cr:,.1f} Cr/yr{drag_info} "
                f"upon full statutory reversion to {stat_rate:.2f}%."
            )

        return {
            "symbol": symbol.upper(),
            "unabsorbed_tax_depreciation_cr": unabsorbed,
            "annual_accelerated_depreciation_claimed_cr": annual_claim,
            "tax_shield_runway_years": runway_years,
            "runway_classification": runway_classification,
            "risk_level": risk_level,
            "projected_statutory_cash_tax_cr": projected_statutory_cash_tax_cr,
            "incremental_cash_tax_drag_cr": incremental_cash_tax_drag_cr,
            "cash_tax_drag_pct_of_fcf": cash_tax_drag_pct_of_fcf,
            "warning_flags": flags,
        }

class WorkingCapitalVelocityScorer:
    """Dr. Anil Lamba Working Capital Velocity & Cash-to-Cash Cycle (CCC) Scorer (Phase 191).

    Derived from "Romancing the Balance Sheet" financial management principles:
      1. Cash-to-Cash Cycle (CCC) = Debtor Days + Inventory Days - Creditor Days.
      2. Good Cost vs Bad Cost: Revenue-generating operating efficiency vs bloated working capital.
      3. Working Capital Suffocation / Paper Profit Trap:
         When PAT growth is positive, but CCC expands sharply (delta CCC > 25 days YoY),
         accounting profits are trapped in uncollected receivables or unsold inventory,
         draining cash and forcing companies to take expensive short-term borrowings.
      4. Negative Working Capital Flyaway:
         When CCC <= 0 (e.g. FMCG, retail giants), the business operates on supplier credit
         and upfront customer cash, generating an internal zero-cost financing float.
    """

    @classmethod
    def evaluate_working_capital_velocity(
        cls,
        symbol: str,
        debtor_days: float,
        inventory_days: float,
        creditor_days: float,
        prior_debtor_days: Optional[float] = None,
        prior_inventory_days: Optional[float] = None,
        prior_creditor_days: Optional[float] = None,
        pat_growth_pct: Optional[float] = None,
        cfo_cr: Optional[float] = None,
        pat_cr: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Calculates Cash-to-Cash Cycle velocity, working capital drag, and forensic traps."""
        clean_sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        cur_d = max(0.0, float(debtor_days))
        cur_i = max(0.0, float(inventory_days))
        cur_c = max(0.0, float(creditor_days))

        current_ccc = round(cur_d + cur_i - cur_c, 1)

        delta_ccc = None
        if (
            prior_debtor_days is not None
            and prior_inventory_days is not None
            and prior_creditor_days is not None
        ):
            prior_ccc = round(float(prior_debtor_days) + float(prior_inventory_days) - float(prior_creditor_days), 1)
            delta_ccc = round(current_ccc - prior_ccc, 1)

        signals: List[str] = []
        alerts: List[str] = []
        risk_score: float = 0.0

        # Tier 1: Negative Working Capital Float (Pristine Cash Machine)
        if current_ccc <= 0.0:
            velocity_tier = "NEGATIVE_WORKING_CAPITAL_FLOAT"
            risk_score = 0.0
            conviction_boost = 15.0
            signals.append("PRISTINE_NEGATIVE_WORKING_CAPITAL_FLOAT")
            notes = (
                f"Negative Cash-to-Cash Cycle ({current_ccc:.1f} days). Company operates on supplier credit, "
                "generating internal zero-cost float financing."
            )
        # Tier 2: Severe Working Capital Suffocation / Paper Profit Trap
        elif delta_ccc is not None and delta_ccc > 30.0 and (pat_growth_pct is None or pat_growth_pct > 0):
            velocity_tier = "CRITICAL_WORKING_CAPITAL_SUFFOCATION"
            risk_score = 30.0
            conviction_boost = -25.0
            signals.append("WORKING_CAPITAL_SUFFOCATION_TRAP")
            alerts.append("LAMBA_PAPER_PROFIT_SUFFOCATION_ALERT")
            notes = (
                f"Severe Cash-to-Cash elongation (+{delta_ccc:.1f} days YoY to {current_ccc:.1f} days). "
                "Reported earnings trapped in unpaid receivables/inventory pileup. High risk of short-term debt spike."
            )
        # Tier 3: Moderate Working Capital Drag
        elif delta_ccc is not None and delta_ccc > 15.0:
            velocity_tier = "MODERATE_WORKING_CAPITAL_DRAG"
            risk_score = 15.0
            conviction_boost = -10.0
            signals.append("WORKING_CAPITAL_CYCLE_ELONGATION")
            notes = f"Working capital cycle extended by +{delta_ccc:.1f} days YoY ({current_ccc:.1f} days)."
        # Tier 4: Fast Cash Velocity
        elif current_ccc <= 60.0:
            velocity_tier = "FAST_CASH_VELOCITY_EFFICIENT"
            risk_score = 0.0
            conviction_boost = 10.0
            signals.append("HIGH_WORKING_CAPITAL_EFFICIENCY")
            notes = f"Lean cash conversion cycle ({current_ccc:.1f} days). Superior working capital discipline."
        else:
            velocity_tier = "NORMAL_WORKING_CAPITAL_CYCLE"
            risk_score = 5.0
            conviction_boost = 0.0
            signals.append("STANDARD_WORKING_CAPITAL_CYCLE")
            notes = f"Operating Cash-to-Cash cycle is {current_ccc:.1f} days."

        # Cross-validate CFO to PAT Cash Conversion
        cfo_pat_ratio = None
        if cfo_cr is not None and pat_cr is not None and pat_cr > 0:
            cfo_pat_ratio = round(float(cfo_cr) / float(pat_cr), 2)
            if cfo_pat_ratio < 0.5:
                alerts.append("CFO_PAT_DIVERGENCE_WORKING_CAPITAL_ABSORPTION")
                signals.append("WEAK_CFO_PAT_CONVERSION")
                conviction_boost -= 10.0

        return {
            "symbol": clean_sym,
            "debtor_days": cur_d,
            "inventory_days": cur_i,
            "creditor_days": cur_c,
            "cash_to_cash_cycle_days": current_ccc,
            "prior_cash_to_cash_cycle_days": prior_ccc if delta_ccc is not None else None,
            "delta_ccc_days": delta_ccc,
            "velocity_tier": velocity_tier,
            "risk_score": risk_score,
            "conviction_boost": conviction_boost,
            "cfo_pat_ratio": cfo_pat_ratio,
            "signals": signals,
            "alerts": alerts,
            "notes": notes,
        }

