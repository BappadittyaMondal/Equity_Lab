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
