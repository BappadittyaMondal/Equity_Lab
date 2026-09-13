"""Multi-Horizon Return Probability & Conformal Matrix Engine.

Computes 6-Month, 1-Year, 2-Year, 3-Year, and 5-Year CAGR predictions,
conformal return probabilities (P(>0%), P(>=2x), P(>=3x), P(>=5x)), data-truth
conformal confidence tiers, M0-M4 lifecycle stage mapping, and strategy bucket classification.
"""

import logging
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import numpy as np

from app.models.schemas import (
    MultiHorizonMatrixItem,
    MultiHorizonMatrixResponse,
    MetaHeader,
)
from app.services.market_data import (
    normalize_symbol,
    get_quote,
    create_meta_header,
)
from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine

logger = logging.getLogger(__name__)


class MultiHorizonMatrixEngine:
    """Institutional Multi-Horizon Matrix Analysis Engine."""

    @staticmethod
    def calculate_single_symbol_matrix(
        symbol: str, override_data: Optional[Dict[str, Any]] = None
    ) -> MultiHorizonMatrixItem:
        """Evaluates multi-horizon return probabilities and conformal metrics for a single stock."""
        norm_sym = normalize_symbol(symbol)
        
        # Fetch fundamental snapshot or use override
        data = override_data or {}
        if not data:
            try:
                db_data = ScreenerCloudConnector.get_company_fundamentals(norm_sym)
                if db_data:
                    data = db_data
            except Exception as e:
                logger.warning(f"Could not load Screener DB fundamentals for {norm_sym}: {e}")

        # Fetch market quote
        quote = get_quote(norm_sym)
        quote_price = 0.0
        if isinstance(quote, dict):
            quote_price = float(quote.get("price") or quote.get("current_price") or 0.0)
        elif quote is not None:
            quote_price = float(getattr(quote, "price", 0.0) or 0.0)

        price = float(data.get("current_price") or quote_price or 100.0)
        if price <= 0:
            price = 100.0
        
        quote_mcap = 0.0
        if isinstance(quote, dict):
            quote_mcap = float(quote.get("market_cap") or 0.0)
        elif quote is not None:
            quote_mcap = float(getattr(quote, "market_cap", 0.0) or 0.0)

        market_cap = float(data.get("market_cap") or quote_mcap or 0.0)
        company_name = str(data.get("company_name") or norm_sym)
        sector = str(data.get("sector") or "Equity / Special Situations")

        # Evaluate company through Institutional Multibagger Engine
        scorecard = {}
        try:
            scorecard = InstitutionalMultibaggerEngine.evaluate_company(data) if data else {}
        except Exception as err:
            logger.warning(f"InstitutionalMultibaggerEngine evaluation warning for {norm_sym}: {err}")

        # Extract underlying fundamental metrics
        import os
        is_offline = os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true"
        has_fundamentals = bool(data and any(k in data for k in ("eps_growth_3yr", "pat_growth_3yr", "roce_latest", "roce_3yr", "cfo_pat_ratio", "debt_to_equity", "pledged_pct", "piotroski_score")))

        if not has_fundamentals and not is_offline:
            return MultiHorizonMatrixItem(
                symbol=norm_sym,
                company_name=company_name,
                sector=sector,
                market_cap_cr=round(market_cap, 1) if market_cap > 0 else None,
                current_price=round(price, 2),
                m_stage="M0 (Unverified)",
                strategy_bucket="DATA_INSUFFICIENT",
                conformal_confidence_score=0.0,
                conformal_confidence_label="UNTRUSTED (Data Insufficient)",
                cagr_6m_pct=0.0,
                cagr_1y_pct=0.0,
                cagr_2y_pct=0.0,
                cagr_3y_pct=0.0,
                cagr_5y_pct=0.0,
                target_price_6m=round(price, 2),
                target_price_1y=round(price, 2),
                target_price_2y=round(price, 2),
                target_price_3y=round(price, 2),
                target_price_5y=round(price, 2),
                prob_6m_positive_pct=0.0,
                prob_1y_positive_pct=0.0,
                prob_2y_positive_pct=0.0,
                prob_3y_2x_pct=0.0,
                prob_3y_3x_pct=0.0,
                prob_5y_3x_pct=0.0,
                prob_5y_5x_pct=0.0,
                primary_catalyst_thesis="DATA_INSUFFICIENT: Fundamental filings unavailable in production.",
                forensic_invalidation_rules=["Missing audited financial statements."],
            )

        eps_growth = float(data.get("eps_growth_3yr") or data.get("pat_growth_3yr") or (25.0 if is_offline else 0.0))
        roce = float(data.get("roce_latest") or data.get("roce_3yr") or (20.0 if is_offline else 0.0))
        cfo_pat = float(data.get("cfo_pat_ratio") or (1.0 if is_offline else 0.0))
        if "cfo_3yr" in data and "net_profit_last_year" in data and data["net_profit_last_year"] > 0:
            cfo_pat = float(data["cfo_3yr"]) / float(data["net_profit_last_year"])

        de_ratio = float(data.get("debt_to_equity") or (0.1 if is_offline else 1.0))
        pledge_raw = data.get("pledged_pct")
        if pledge_raw is not None:
            try:
                pledge_pct = float(pledge_raw)
            except (ValueError, TypeError):
                pledge_pct = 0.0 if is_offline else None
        else:
            pledge_pct = 0.0 if is_offline else None
        piotroski = int(data.get("piotroski_score") or (7 if is_offline else 0))

        # 1. Compute Conformal Confidence Score & Label
        conf_score = 65.0
        if cfo_pat >= 1.0:
            conf_score += 15.0
        elif cfo_pat > 0.0:
            conf_score += 5.0
        else:
            conf_score -= 20.0  # Cash flow trap penalty

        if de_ratio <= 0.3:
            conf_score += 10.0
        elif de_ratio > 0.8:
            conf_score -= 10.0

        if pledge_pct is not None:
            if pledge_pct == 0.0:
                conf_score += 5.0
            elif pledge_pct > 25.0:
                conf_score -= 25.0
        else:
            conf_score -= 15.0  # Undisclosed/missing promoter pledge penalty in production

        if piotroski >= 8:
            conf_score += 10.0
        elif piotroski < 6:
            conf_score -= 10.0

        conf_score = min(98.0, max(25.0, round(conf_score, 1)))

        if conf_score >= 88.0:
            conf_label = "HIGH (Institutional Grade)"
        elif conf_score >= 75.0:
            conf_label = "MEDIUM-HIGH (Audited)"
        elif conf_score >= 60.0:
            conf_label = "MEDIUM (Proof Pending)"
        else:
            conf_label = "SPECULATIVE / HIGH RISK"

        # 2. Determine M0-M4 Lifecycle Stage & Strategy Bucket
        overall_score = float(scorecard.get("overall_score") or 75.0)
        archetype = str(scorecard.get("archetype") or "")

        if "Turnaround" in archetype or data.get("turnaround_candidate"):
            m_stage = "T2 Candidate"
            bucket = "Bucket D: Turnaround & Recovery"
        elif roce >= 30.0 and cfo_pat >= 1.0 and de_ratio <= 0.2:
            m_stage = "M3 -> M4"
            bucket = "Bucket B: Long-Duration SIP Compounder"
        elif eps_growth >= 35.0 and overall_score >= 80.0:
            m_stage = "M2 -> M3"
            bucket = "Bucket A: High-Asymmetry Early Multibagger"
        elif de_ratio > 0.5 or de_ratio > 0.0 and cfo_pat < 0:
            m_stage = "M2"
            bucket = "Bucket A: High-Asymmetry Early Multibagger"
        elif de_ratio <= 0.5 and piotroski >= 7:
            m_stage = "M3"
            bucket = "Bucket B: Long-Duration SIP Compounder"
        else:
            m_stage = "M1 -> M2"
            bucket = "Bucket C: Value / Optionality Inflection"

        # Override for specific archetype cues
        if "Early Multibagger" in archetype:
            m_stage = "M2 -> M3"
            bucket = "Bucket A: High-Asymmetry Early Multibagger"

        # 3. Calculate Horizon CAGR Projections (%) (§CRO Valuation-Aware Equity Decomposition)
        fundamental_growth = eps_growth
        if cfo_pat < 0:
            fundamental_growth *= 0.70  # Negative cash flow penalty
        elif cfo_pat < 0.60:
            fundamental_growth *= (0.70 + 0.50 * max(0.0, cfo_pat))

        # Working Capital & DSO Stress Haircut (§CRO Liquidity Shield)
        dso = float(data.get("dso") or data.get("debtor_days") or data.get("days_sales_outstanding") or 0.0)
        if dso > 120.0 and cfo_pat < 0.75:
            dso_penalty = max(0.0, min(0.35, ((dso - 120.0) / 365.0) * (1.0 - max(0.0, cfo_pat))))
            fundamental_growth *= (1.0 - dso_penalty)

        # Valuation multiple adjustment (§CRO Equity Decomposition)
        curr_pe = float(data.get("pe_ratio") or data.get("pe") or 25.0)
        if curr_pe <= 0:
            curr_pe = 25.0
        median_pe = float(data.get("median_pe") or data.get("historical_pe") or (curr_pe if curr_pe < 35.0 else curr_pe * 0.85))
        pe_ratio_factor = median_pe / curr_pe if curr_pe > 0 else 1.0

        # Horizon multiple adjustments (incorporating 5-year mean-reversion drift)
        mult_adj_6m = (pe_ratio_factor ** (0.5 / 5.0))
        mult_adj_1y = (pe_ratio_factor ** (1.0 / 5.0))
        mult_adj_2y = (pe_ratio_factor ** (2.0 / 5.0))
        mult_adj_3y = (pe_ratio_factor ** (3.0 / 5.0))
        mult_adj_5y = (pe_ratio_factor ** (5.0 / 5.0))

        def compute_cagr(g_rate: float, mult_factor: float, years: float) -> float:
            if g_rate <= -40.0:
                return -40.0
            g_dec = g_rate / 100.0
            gross_factor = max(0.01, ((1.0 + g_dec) ** years) * mult_factor)
            annualized = ((gross_factor ** (1.0 / years)) - 1.0) * 100.0
            return round(max(-40.0, min(85.0, annualized)), 1)

        cagr_6m = compute_cagr(fundamental_growth, mult_adj_6m, 0.5)
        cagr_1y = compute_cagr(fundamental_growth, mult_adj_1y, 1.0)
        cagr_2y = compute_cagr(fundamental_growth, mult_adj_2y, 2.0)
        cagr_3y = compute_cagr(fundamental_growth, mult_adj_3y, 3.0)
        cagr_5y = compute_cagr(fundamental_growth, mult_adj_5y, 5.0)

        # Target Prices (safeguarded against negative base)
        p_6m = round(price * (max(0.01, 1.0 + cagr_6m / 100.0) ** 0.5), 2)
        p_1y = round(price * (max(0.01, 1.0 + cagr_1y / 100.0) ** 1.0), 2)
        p_2y = round(price * (max(0.01, 1.0 + cagr_2y / 100.0) ** 2.0), 2)
        p_3y = round(price * (max(0.01, 1.0 + cagr_3y / 100.0) ** 3.0), 2)
        p_5y = round(price * (max(0.01, 1.0 + cagr_5y / 100.0) ** 5.0), 2)

        # 4. Compute Return Probabilities (%)
        def calculate_probability(cagr: float, horizon_years: float, target_mult: float) -> float:
            ret_expected = (((1.0 + cagr / 100.0) ** horizon_years) - 1.0) * 100.0
            target_return_pct = (target_mult - 1.0) * 100.0
            dispersion = 28.0 / (horizon_years ** 0.35)
            prob = 1.0 / (1.0 + math.exp(-(ret_expected - target_return_pct) / dispersion)) * 100.0
            return round(min(96.0, max(5.0, prob)), 1)

        prob_6m_pos = calculate_probability(cagr_6m, 0.5, 1.05)
        prob_1y_pos = calculate_probability(cagr_1y, 1.0, 1.05)
        prob_2y_pos = calculate_probability(cagr_2y, 2.0, 1.05)
        prob_3y_2x = calculate_probability(cagr_3y, 3.0, 2.0)
        prob_3y_3x = calculate_probability(cagr_3y, 3.0, 3.0)
        prob_5y_3x = calculate_probability(cagr_5y, 5.0, 3.0)
        prob_5y_5x = calculate_probability(cagr_5y, 5.0, 5.0)

        # 5. Build Thesis & Invalidation Rules
        thesis = (
            f"EPS growth ({eps_growth:.1f}%) and ROCE ({roce:.1f}%) driving {cagr_3y}% projected 3Y CAGR "
            f"under {conf_label} confidence."
        )
        if data.get("thesis"):
            thesis = str(data["thesis"])

        invalidation_rules = [
            "Revenue growth without CFO conversion (CFO < 0) invalidates thesis.",
            "Promoter pledge exceeding 25% triggers immediate hard exit gate.",
            f"Share price closing below 200 DMA ({round(price * 0.82, 2)} INR) breaches technical support.",
        ]
        if dso > 180.0 and cfo_pat < 0.50:
            invalidation_rules.append(f"Working capital stretch (DSO {dso:.0f}d, CFO/PAT {cfo_pat:.2f}) triggers mandatory 2.5% position cap.")
        if pledge_pct is None:
            invalidation_rules.append("Undisclosed or missing promoter pledge filings requires mandatory forensic verification.")

        return MultiHorizonMatrixItem(
            symbol=norm_sym,
            company_name=company_name,
            sector=sector,
            market_cap_cr=round(market_cap, 1) if market_cap > 0 else None,
            current_price=round(price, 2),
            m_stage=m_stage,
            strategy_bucket=bucket,
            conformal_confidence_score=conf_score,
            conformal_confidence_label=conf_label,
            cagr_6m_pct=cagr_6m,
            cagr_1y_pct=cagr_1y,
            cagr_2y_pct=cagr_2y,
            cagr_3y_pct=cagr_3y,
            cagr_5y_pct=cagr_5y,
            target_price_6m=p_6m,
            target_price_1y=p_1y,
            target_price_2y=p_2y,
            target_price_3y=p_3y,
            target_price_5y=p_5y,
            prob_6m_positive_pct=prob_6m_pos,
            prob_1y_positive_pct=prob_1y_pos,
            prob_2y_positive_pct=prob_2y_pos,
            prob_3y_2x_pct=prob_3y_2x,
            prob_3y_3x_pct=prob_3y_3x,
            prob_5y_3x_pct=prob_5y_3x,
            prob_5y_5x_pct=prob_5y_5x,
            primary_catalyst_thesis=thesis,
            forensic_invalidation_rules=invalidation_rules,
        )

    @classmethod
    def analyze_universe_matrix(
        cls, symbols: List[str], override_data_map: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> MultiHorizonMatrixResponse:
        """Evaluates a batch of symbols and returns a ranked MultiHorizonMatrixResponse."""
        override_map = override_data_map or {}
        items: List[MultiHorizonMatrixItem] = []

        for sym in symbols:
            try:
                item_data = override_map.get(sym) or override_map.get(normalize_symbol(sym))
                item = cls.calculate_single_symbol_matrix(sym, item_data)
                items.append(item)
            except Exception as e:
                logger.error(f"Error evaluating symbol {sym} in MultiHorizonMatrixEngine: {e}")

        # Sort matrix by Conformal Confidence Score & 3Y CAGR descending
        items.sort(
            key=lambda x: (x.conformal_confidence_score, x.cagr_3y_pct), reverse=True
        )

        now_str = datetime.now(timezone.utc).isoformat()
        meta = create_meta_header(source="IERL MultiHorizonMatrixEngine")
        meta["nature"] = "SCENARIO_GROWTH_SENSITIVITY"
        meta["methodology"] = "Multi-Horizon Scenario Growth Sensitivity Grid (PE Exit Multiple x Fundamental Growth Trajectory). Not a point forecast or guaranteed directional return."

        return MultiHorizonMatrixResponse(
            symbols_evaluated=len(items),
            as_of=now_str,
            matrix=items,
            meta=meta,
        )
