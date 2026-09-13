"""Phase 3: Generative AI Multi-Agent & Qualitative Red-Team Service.

Implements qualitative LLM analysis features:
1. Automated Earnings Call Analyst (concall transcript risk keyword audit & management tone extraction).
2. Automated Geopolitical Stress Tester (simulates tariff shocks, US IT budget cuts, shipping bottlenecks).
3. Automated Counter-Thesis Bot (generates adversarial pre-mortem bear cases for stock picks).
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings
from app.services.market_data import normalize_symbol, create_meta_header, get_ist_now_str
from app.services.research.geopolitical_engine import evaluate_geopolitical_risk
from app.services.decision_brain.red_team_engine import evaluate_red_team_review
from app.services.security.prompt_sanitizer import sanitize_prompt

logger = logging.getLogger(__name__)


class GenAIRedTeamService:
    """Phase 3 Generative AI Qualitative Intelligence & Red-Team Service."""

    CONCALL_RISK_KEYWORDS = {
        "slowing demand": ("DEMAND_SLOWDOWN", "HIGH"),
        "us enterprise demand": ("US_TECH_HEADWIND", "HIGH"),
        "pricing pressure": ("MARGIN_DEFLATION", "MODERATE"),
        "raw material tariff": ("INPUT_TARIFF_RISK", "HIGH"),
        "billing rate deflation": ("PRICING_POWER_LOSS", "HIGH"),
        "supply chain bottleneck": ("LOGISTICS_DISRUPTION", "MODERATE"),
        "h1-b visa": ("IMMIGRATION_POLICY_RISK", "MODERATE"),
        "order cancellation": ("REVENUE_CONTRACT_RISK", "CRITICAL")
    }

    @classmethod
    def audit_earnings_call_transcript(
        cls,
        symbol: str,
        transcript_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Scans earnings call transcripts to extract qualitative risk factors & management sentiment."""
        norm_sym = normalize_symbol(symbol)
        clean_sym = norm_sym.replace(".NS", "").replace(".BO", "").upper()
        
        sanitization_res = sanitize_prompt(transcript_text or "")
        clean_transcript = sanitization_res["sanitized_text"]
        text = clean_transcript.lower()
        
        if not text:
            return {
                "symbol": clean_sym,
                "data_mode": "INSUFFICIENT_DATA",
                "sentiment_score": None,
                "sentiment_label": "NEUTRAL",
                "flagged_concall_risks": [],
                "concall_summary": f"No earnings call transcript supplied for {clean_sym}. Qualitative audit skipped.",
                "executed_at": get_ist_now_str(),
                "meta": create_meta_header(source=f"Automated Earnings Call Analyst ({clean_sym})")
            }

        flagged_risks = []
        sentiment_score = 75.0  # Baseline neutral-positive

        for kw, (risk_type, severity) in cls.CONCALL_RISK_KEYWORDS.items():
            if kw in text:
                flagged_risks.append({
                    "keyword": kw,
                    "risk_type": risk_type,
                    "severity": severity
                })
                if severity == "CRITICAL":
                    sentiment_score -= 20.0
                elif severity == "HIGH":
                    sentiment_score -= 10.0
                else:
                    sentiment_score -= 5.0

        # Try Gemini LLM semantic transcript evaluation when API key is available
        llm_analysis_note = ""
        gemini_key = getattr(settings, "GEMINI_API_KEY", "")
        if gemini_key and "your_" not in gemini_key.lower() and len(clean_transcript) > 50:
            from app.services.llm import check_and_log_llm_budget
            if check_and_log_llm_budget("concall_audit", clean_sym):
                try:
                    prompt = (
                        f"Analyze the following earnings call transcript for equity {clean_sym}.\n"
                        f"1. Extract overall management sentiment (BULLISH/NEUTRAL/BEARISH)\n"
                        f"2. Identify qualitative risk flags (e.g. pricing pressure, demand slowdown, guidance cuts)\n"
                        f"3. Summarize key takeaways in 2 concise sentences.\n\n"
                        f"TRANSCRIPT:\n{clean_transcript[:2000]}"
                    )
                    candidate_models = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-2.5-flash", "gemini-1.5-flash"]
                    gen_text = None
                    try:
                        from google import genai
                        client = genai.Client(api_key=gemini_key)
                        for m in candidate_models:
                            try:
                                resp = client.models.generate_content(model=m, contents=prompt)
                                if resp.text:
                                    gen_text = resp.text
                                    break
                            except Exception:
                                continue
                    except Exception:
                        pass

                    if not gen_text:
                        import google.generativeai as genai
                        genai.configure(api_key=gemini_key)
                        for m in candidate_models:
                            try:
                                model = genai.GenerativeModel(m)
                                resp = model.generate_content(prompt)
                                if resp.text:
                                    gen_text = resp.text
                                    break
                            except Exception:
                                continue

                    if gen_text:
                        llm_analysis_note = f" [Gemini AI Analysis: {gen_text.strip()[:200]}...]"
                except Exception as e:
                    logger.warning("Gemini concall analysis failed: %s", e)

        sentiment_label = "BULLISH" if sentiment_score >= 70.0 else ("NEUTRAL" if sentiment_score >= 50.0 else "BEARISH")

        return {
            "symbol": clean_sym,
            "data_mode": "OBSERVED",
            "sentiment_score": round(max(0.0, min(100.0, sentiment_score)), 1),
            "sentiment_label": sentiment_label,
            "flagged_concall_risks": flagged_risks,
            "concall_summary": f"Concall transcript analysis completed for {clean_sym}. Management tone: {sentiment_label}. {len(flagged_risks)} risk flags identified.{llm_analysis_note}",
            "executed_at": get_ist_now_str(),
            "meta": create_meta_header(source=f"Automated Earnings Call Analyst ({clean_sym})")
        }

    @classmethod
    def run_geopolitical_stress_test(
        cls,
        symbol: str,
        scenario: str = "US_TARIFF_10PCT_INCREASE"
    ) -> Dict[str, Any]:
        """Simulates geopolitical stress scenarios on stock performance & cash flows."""
        norm_sym = normalize_symbol(symbol)
        clean_sym = norm_sym.replace(".NS", "").replace(".BO", "").upper()
        geo_res = evaluate_geopolitical_risk(clean_sym)
        sector = geo_res.get("sector", "UNKNOWN")

        scenarios = {
            "US_TARIFF_10PCT_INCREASE": {
                "description": "Simulates a 10% tariff increase on US exports",
                "impact_map": {"IT": -12.0, "METALS": -15.0, "DEFENSE": 0.0, "TRANSFORMERS": -3.0}
            },
            "US_IT_BUDGET_CUT_15PCT": {
                "description": "Simulates a 15% freeze in US corporate IT spending",
                "impact_map": {"IT": -22.0, "SOFTWARE": -20.0, "DEFENSE": 0.0, "TRANSFORMERS": 0.0}
            },
            "MIDDLE_EAST_SHIPPING_BOTTLENECK": {
                "description": "Simulates a 30-day shipping rerouting bottleneck around Red Sea",
                "impact_map": {"SHIPPING": -18.0, "LOGISTICS": -15.0, "PAINTS": -10.0, "TRANSFORMERS": -5.0}
            }
        }

        scen_info = scenarios.get(scenario, scenarios["US_TARIFF_10PCT_INCREASE"])
        est_revenue_impact_pct = scen_info["impact_map"].get(sector, -5.0)

        pass_stress_test = est_revenue_impact_pct >= -10.0
        recommendation = "MAINTAIN_POSITION" if pass_stress_test else "APPLY_MACRO_HEDGE"

        return {
            "symbol": clean_sym,
            "scenario": scenario,
            "scenario_description": scen_info["description"],
            "sector": sector,
            "estimated_revenue_impact_pct": est_revenue_impact_pct,
            "pass_stress_test": pass_stress_test,
            "stress_test_recommendation": recommendation,
            "executed_at": get_ist_now_str(),
            "meta": create_meta_header(source=f"Automated Geopolitical Stress Tester ({clean_sym})")
        }

    @classmethod
    def generate_counter_thesis_redteam(
        cls,
        symbol: str,
        primary_bull_thesis: str = "High-growth compounder with expanding market share"
    ) -> Dict[str, Any]:
        """Generates an adversarial GenAI Red-Team pre-mortem bear case challenging top stock picks."""
        norm_sym = normalize_symbol(symbol)
        clean_sym = norm_sym.replace(".NS", "").replace(".BO", "").upper()
        
        sanitization_res = sanitize_prompt(primary_bull_thesis)
        clean_thesis = sanitization_res["sanitized_text"]
        
        red_team_res = evaluate_red_team_review(clean_sym, thesis_statement=clean_thesis)
        concall_res = cls.audit_earnings_call_transcript(clean_sym)

        bear_case_summary = (
            f"RED-TEAM BEAR CASE FOR {clean_sym}: Primary bull thesis '{clean_thesis}' is challenged. "
            f"Concall Sentiment: {concall_res['sentiment_label']} ({concall_res['sentiment_score']}/100). "
            f"Failure vectors: {', '.join(red_team_res['red_team_record']['pre_mortem_failure_causes'])}."
        )

        return {
            "symbol": clean_sym,
            "primary_bull_thesis": clean_thesis,
            "red_team_passed": red_team_res["gate_7_passed"],
            "bear_case_summary": bear_case_summary,
            "failure_causes": red_team_res["red_team_record"]["pre_mortem_failure_causes"],
            "adversarial_review_notes": red_team_res["red_team_record"]["adversarial_review_notes"],
            "executed_at": get_ist_now_str(),
            "meta": create_meta_header(source=f"Generative AI Red-Team Bear Bot ({clean_sym})")
        }

    @classmethod
    def synthesize_four_lens_evidence(
        cls,
        symbol: str,
        item: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Synthesizes qualitative primary-source evidence under Skill 42 contract."""
        norm_sym = normalize_symbol(symbol)
        clean_sym = norm_sym.replace(".NS", "").replace(".BO", "").upper()
        data = dict(item) if item else {}

        if not data:
            try:
                from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
                fetched = ScreenerCloudConnector.get_company_fundamentals(clean_sym)
                if fetched:
                    data = fetched
            except Exception:
                pass

        def _get_val(keys: List[str], default: float) -> float:
            for k in keys:
                if k in data and data[k] is not None:
                    try:
                        return float(data[k])
                    except (ValueError, TypeError):
                        pass
            return default

        # 1. Kacholia Metrics (Capital Efficiency & Scalability)
        roce = _get_val(["roce_latest", "roce", "roce_3yr"], 15.0)
        inc_roic = _get_val(["incremental_roic", "inc_roic"], roce)
        asset_turn = _get_val(["asset_turnover", "fixed_asset_turnover"], 1.2)
        sales_3y = _get_val(["sales_growth_3yr", "sales_cagr_3y"], 15.0)

        if inc_roic >= 20.0 or (roce >= 18.0 and asset_turn >= 1.4):
            kacholia_quality = "HIGH"
        elif inc_roic < 12.0 and roce < 12.0:
            kacholia_quality = "LOW"
        else:
            kacholia_quality = "MEDIUM"

        # 2. Kedia Metrics (Management Execution, Promoter Alignment & Solvency)
        prom_hold = _get_val(["promoter_holding", "promoter_holding_pct"], 50.0)
        pledge = _get_val(["pledged_pct", "promoter_pledge_pct"], 0.0)
        debt_eq = _get_val(["debt_to_equity"], 0.1)

        if prom_hold >= 50.0 and pledge <= 5.0 and debt_eq <= 0.35 and roce >= 15.0:
            kedia_quality = "HIGH"
        elif pledge > 20.0 or debt_eq > 1.0 or prom_hold < 35.0:
            kedia_quality = "LOW"
        else:
            kedia_quality = "MEDIUM"

        # 3. Agrawal Metrics (Operating Inflection & Volume Confirmation)
        pat_growth_latest = _get_val(["pat_growth_latest", "pat_growth_yoy"], 20.0)
        pat_growth_3y = _get_val(["pat_growth_3yr"], 15.0)
        vol_z = _get_val(["volume_z_score", "vol_z", "z_vol"], 1.5)
        dtr = _get_val(["delivery_turnover_5d", "dtr_5d"], 2.0)

        if pat_growth_latest >= 20.0 and (vol_z >= 1.5 or dtr >= 1.8):
            agrawal_quality = "HIGH"
        elif pat_growth_latest < 5.0 and pat_growth_3y < 5.0:
            agrawal_quality = "LOW"
        else:
            agrawal_quality = "MEDIUM"

        # 4. Parikh Metrics (Cash Flow Durability & Conversion)
        cfo = _get_val(["cfo_last_year", "cfo"], 120.0)
        pat = _get_val(["net_profit_last_year", "net_profit"], 100.0)
        capex = _get_val(["capex_last_year", "capex"], 30.0)
        fcf = _get_val(["fcf_last_year"], cfo - capex)

        if cfo > pat and fcf > 0.0 and (cfo / max(1.0, pat) >= 0.80):
            parikh_quality = "HIGH"
        elif cfo <= 0.0 or (pat > 0.0 and cfo < 0.0):
            parikh_quality = "LOW"
        else:
            parikh_quality = "MEDIUM"

        # Falsifiable Contradictions & Red Flags
        contradictions: List[str] = []
        red_flags: List[str] = []

        if pledge > 20.0:
            red_flags.append(f"CRITICAL: High promoter pledge ({pledge:.1f}%) creates margin liquidation risk.")
        if pat > 0.0 and cfo < 0.0:
            red_flags.append("CRITICAL: Distributive financing trap — accounting PAT is positive while operating CFO is negative.")
        if pat_growth_latest >= 30.0 and vol_z < -1.0:
            contradictions.append("Reported earnings acceleration not confirmed by institutional delivery volumes.")
        if debt_eq > 1.2:
            red_flags.append(f"HIGH: Elevated balance sheet leverage (Debt/Equity: {debt_eq:.2f}x).")
        if [kacholia_quality, kedia_quality, agrawal_quality, parikh_quality].count("LOW") >= 2:
            red_flags.append("Evidence Quality LOW on 2 or more modules (High-scoring hypothesis, weak evidence).")

        return {
            "skill_name": "Skill 42 — Four-Lens Evidence Weighting",
            "symbol": clean_sym,
            "kacholia_evidence": {
                "finding": f"Incremental Capital: ROIC {inc_roic:.1f}% vs ROCE {roce:.1f}%, Fixed Asset Turn: {asset_turn:.2f}x, 3Y Sales: {sales_3y:.1f}%",
                "evidence_quality": kacholia_quality
            },
            "kedia_evidence": {
                "finding": f"Management & Balance Sheet: Promoter Holding {prom_hold:.1f}%, Pledge {pledge:.1f}%, Debt/Equity {debt_eq:.2f}x",
                "evidence_quality": kedia_quality
            },
            "agrawal_evidence": {
                "finding": f"Inflection & Volume: Latest PAT Growth {pat_growth_latest:.1f}% vs 3Y ({pat_growth_3y:.1f}%), Volume Z-Score: {vol_z:+.1f}s, DTR: {dtr:.1f}%",
                "evidence_quality": agrawal_quality
            },
            "parikh_evidence": {
                "finding": f"Cash Durability: CFO ₹{cfo:.1f}Cr vs PAT ₹{pat:.1f}Cr (FCF: ₹{fcf:.1f}Cr)",
                "evidence_quality": parikh_quality
            },
            "contradictions": contradictions,
            "red_flags": red_flags
        }
