"""Phase 3: Generative AI Multi-Agent & Qualitative Red-Team Service.

Implements qualitative LLM analysis features:
1. Automated Earnings Call Analyst (concall transcript risk keyword audit & management tone extraction).
2. Automated Geopolitical Stress Tester (simulates tariff shocks, US IT budget cuts, shipping bottlenecks).
3. Automated Counter-Thesis Bot (generates adversarial pre-mortem bear cases for stock picks).
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
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

        sentiment_label = "BULLISH" if sentiment_score >= 70.0 else ("NEUTRAL" if sentiment_score >= 50.0 else "BEARISH")

        return {
            "symbol": clean_sym,
            "data_mode": "OBSERVED",
            "sentiment_score": round(max(0.0, min(100.0, sentiment_score)), 1),
            "sentiment_label": sentiment_label,
            "flagged_concall_risks": flagged_risks,
            "concall_summary": f"Concall transcript analysis completed for {clean_sym}. Management tone: {sentiment_label}. {len(flagged_risks)} risk flags identified.",
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
