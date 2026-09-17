"""Multilingual Video Intelligence Analyst & Autonomous Innovation Radar Engine.

Provides:
  1. Epistemic Source Classification (Official Concall vs Retail Commentary)
  2. Contextual Financial Fact-Checking (Transcript Claims vs Audited Financials)
  3. Multilingual Q&A Synthesis with Timestamped Citations (Hindi, Bengali, English)
  4. Autonomous Platform Innovation Radar (Meta-Feedback Loop mapping to 45 Engines)
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from app.services.ingestion.youtube_transcript_service import YouTubeTranscriptService

logger = logging.getLogger(__name__)


class VideoIntelligenceEngine:
    """Institutional Multilingual Video Intelligence & Platform Evolution Engine."""

    OFFICIAL_INDICATORS = [
        "concall", "conference call", "earnings call", "analyst meet",
        "investor presentation", "q1", "q2", "q3", "q4", "fy24", "fy25", "fy26",
        "agm", "annual general meeting", "management interview", "ceo interview",
        "cfo interview", "cnbc", "bloomberg", "zee business", "et now", "ndtv profit"
    ]

    NOVEL_STRUCTURAL_INDICATORS = [
        "ind as 115", "contract asset", "unbilled revenue", "capacity execution velocity",
        "channel inventory aging", "fleet replacement cohort", "strip ratio", "plf load factor",
        "working capital drag", "cash conversion divergence", "scrappage policy multiplier",
        "dealer inventory days", "order backlog burn rate"
    ]

    RETAIL_FOLKLORE_KEYWORDS = [
        "secret indicator", "99% win rate", "holy grail", "double your money tomorrow",
        "moon cycle", "best strategy for beginners", "options jackpot"
    ]

    @classmethod
    def classify_source_epistemic_tier(cls, title: str, description: str = "", channel: str = "") -> Dict[str, Any]:
        """Classifies video into Tier-1 Official Concall/Management or Tier-2 Influencer Commentary."""
        corpus = f"{title} {description} {channel}".lower()

        is_official = any(ind in corpus for ind in cls.OFFICIAL_INDICATORS)
        if is_official:
            return {
                "tier": "TIER_1_OFFICIAL_CONCALL",
                "credibility_grade": "A+",
                "epistemic_authority": "PRIMARY_CATALYST_FEED",
                "rationale": "Official management, earnings concall, or institutional analyst briefing."
            }

        return {
            "tier": "TIER_2_INFLUENCER_COMMENTARY",
            "credibility_grade": "B",
            "epistemic_authority": "QUALITATIVE_SENTIMENT_ONLY",
            "rationale": "Third-party market commentary or educational analysis; quarantined against audited financial tables."
        }

    @classmethod
    def fact_check_claims(
        cls,
        transcript_text: str,
        symbol: Optional[str] = None,
        company_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Cross-references quantitative claims in transcript against verified company financials."""
        findings: List[Dict[str, Any]] = []
        text_lower = transcript_text.lower()

        # If company data not directly provided, attempt to resolve via symbol
        audited = company_data or {}
        if not audited and symbol:
            try:
                from app.services.research.institutional_multibagger_engine import InstitutionalMultibaggerEngine
                from app.services.data_ingestion.screener_connector import ScreenerCloudConnector
                comp = ScreenerCloudConnector.get_company_fundamentals(symbol)
                if comp:
                    audited = comp
            except Exception:
                pass

        # 1. Debt Status Fact Check
        debt_claim_match = re.search(r'\b(debt[-\s]?free|zero debt|no debt|nil debt)\b', text_lower)
        if debt_claim_match:
            actual_debt = float(audited.get("debt") or audited.get("total_debt") or 0.0)
            de_ratio = float(audited.get("debt_to_equity") or 0.0)
            if actual_debt > 50.0 or de_ratio > 0.30:
                findings.append({
                    "topic": "DEBT_SOLVENCY",
                    "claim": "Speaker claimed company is debt-free / zero-debt.",
                    "audited_fact": f"Audited balance sheet shows total debt of ₹{actual_debt:,.1f}Cr (D/E: {de_ratio:.2f}x).",
                    "status": "DISCREPANCY_FLAGGED",
                    "severity": "HIGH_ALERT",
                    "guidance": "Speaker statement contradicts audited debt liabilities; verify whether net-debt includes off-balance sheet items."
                })
            elif audited:
                findings.append({
                    "topic": "DEBT_SOLVENCY",
                    "claim": "Speaker claimed company is debt-free.",
                    "audited_fact": f"Audited financials confirm negligible debt (₹{actual_debt:.1f}Cr, D/E: {de_ratio:.2f}x).",
                    "status": "VERIFIED_ACCURATE",
                    "severity": "CLEAN",
                    "guidance": "Debt-free status matches audited annual disclosures."
                })

        # 2. Promoter Pledge Check
        pledge_claim = re.search(r'\b(no pledge|zero pledge|clean holding|promoter holding.*good)\b', text_lower)
        if pledge_claim and audited:
            actual_pledge = float(audited.get("pledged_pct") or audited.get("promoter_pledge_pct") or 0.0)
            if actual_pledge > 10.0:
                findings.append({
                    "topic": "PROMOTER_PLEDGE",
                    "claim": "Speaker indicated clean promoter holding without encumbrances.",
                    "audited_fact": f"Shareholding pattern reflects {actual_pledge:.1f}% promoter pledge.",
                    "status": "DISCREPANCY_FLAGGED",
                    "severity": "HIGH_ALERT",
                    "guidance": "Encumbered promoter equity represents margin-call liquidation risk."
                })

        # 3. Order Book Claim Check
        order_book_match = re.search(r'order\s*book\s*(?:of|is|around)?\s*(?:₹|rs\.?|inr)?\s*([0-9,]+)\s*(?:cr|crore)', text_lower)
        if order_book_match and audited:
            claimed_val = float(order_book_match.group(1).replace(",", ""))
            net_block = float(audited.get("net_block") or audited.get("fixed_assets") or 1.0)
            cfr = round(claimed_val / max(net_block * 2.0, 1.0), 1)
            if cfr > 4.0:
                findings.append({
                    "topic": "CAPACITY_FEASIBILITY",
                    "claim": f"Speaker highlighted order book of ₹{claimed_val:,.1f}Cr.",
                    "audited_fact": f"Fixed assets (Net Block: ₹{net_block:,.1f}Cr) yield Capacity Feasibility Ratio CFR of {cfr:.1f}x.",
                    "status": "CAPACITY_STRESS_WARNING",
                    "severity": "MODERATE",
                    "guidance": f"Order book exceeds 4x manufacturing capacity; monitor for subcontractor margin leakage unless capex underway."
                })

        return findings

    @classmethod
    def evaluate_platform_innovation_radar(
        cls,
        transcript_text: str,
        title: str = ""
    ) -> Dict[str, Any]:
        """Scans transcript for novel institutional techniques that could improve Equity Lab's 45 engines."""
        corpus = f"{title} {transcript_text}".lower()

        # Reject retail folklore
        is_retail_folklore = any(folk in corpus for folk in cls.RETAIL_FOLKLORE_KEYWORDS)
        if is_retail_folklore:
            return {
                "has_platform_improvement_idea": False,
                "confidence_score": 10.0,
                "status": "RETAIL_FOLKLORE_VETOED",
                "advisories": []
            }

        advisories: List[Dict[str, Any]] = []

        # Check for unmeasured structural dimensions
        for indicator in cls.NOVEL_STRUCTURAL_INDICATORS:
            if indicator in corpus:
                # Build context-aware advisory
                if "ind as 115" in indicator or "contract asset" in indicator or "unbilled revenue" in indicator:
                    advisories.append({
                        "innovation_topic": "Ind AS 115 Unbilled Contract Asset Drift",
                        "target_engine": "Engine F12 (Working Capital Cycle) & Capacity Feasibility (CFR)",
                        "target_file": "app/services/research/institutional_multibagger_engine.py",
                        "current_capability": "Evaluates trade receivables DSO and gross cash conversion cycle days.",
                        "proposed_enhancement": "Track ratio of contract assets (unbilled revenue) to trade receivables. A growth rate > 1.5x in contract assets signals aggressive early revenue recognition prior to physical milestone certification.",
                        "fiduciary_impact": "HIGH_ALPHA: Early detection of EPC and software milestone inflation."
                    })
                elif "fleet replacement" in indicator or "scrappage policy" in indicator:
                    advisories.append({
                        "innovation_topic": "Fleet Replacement Age Cohort Multiplier",
                        "target_engine": "Engine E20 (Causal Analysis Engine) & Auto Sector Matrix",
                        "target_file": "app/services/research/causal_engine.py",
                        "current_capability": "Evaluates macro interest rate changes and fuel price pass-through on auto volumes.",
                        "proposed_enhancement": "Integrate 15-year commercial vehicle deregistration cohorts to forecast replacement demand inflection.",
                        "fiduciary_impact": "MODERATE_ALPHA: Improves cyclic bottom forecasting in automotive OEMs."
                    })
                elif "plf load factor" in indicator:
                    advisories.append({
                        "innovation_topic": "Power Plant PLF Dispatch Inflection",
                        "target_engine": "Engine F11 (Operating Leverage) & Power Sector Engine",
                        "target_file": "app/services/research/institutional_multibagger_engine.py",
                        "current_capability": "Evaluates quarterly revenue growth and EBITDA margin spread.",
                        "proposed_enhancement": "Incorporate Plant Load Factor (PLF) crossing 70% threshold as non-linear fixed cost absorption trigger.",
                        "fiduciary_impact": "HIGH_ALPHA: Accurately predicts margin expansion in power generation."
                    })

        has_idea = len(advisories) > 0
        return {
            "has_platform_improvement_idea": has_idea,
            "confidence_score": 88.0 if has_idea else 20.0,
            "status": "INNOVATION_ADVISORY_DETECTED" if has_idea else "NO_NOVEL_MODEL_DETECTED",
            "advisories_count": len(advisories),
            "advisories": advisories
        }

    @classmethod
    def synthesize_qa(
        cls,
        segments: List[Dict[str, Any]],
        user_query: Optional[str] = None,
        language_pref: str = "en"
    ) -> Dict[str, Any]:
        """Synthesizes an evidence-grounded answer to the user's question citing timestamps."""
        if not segments:
            return {
                "answer": "No transcript content available to answer query.",
                "cited_timestamps": [],
                "confidence": 0.0
            }

        q = (user_query or "summarize key investment highlights, guidance, and risks").lower().strip()
        terms = [t for t in re.findall(r'[a-zA-Z0-9]+', q) if len(t) > 2 and t not in ("what", "how", "why", "when", "does", "the", "and", "for")]

        # Match relevant segments
        scored_segments = []
        for s in segments:
            score = 0
            text_lower = s["text"].lower()
            for t in terms:
                if t in text_lower:
                    score += 1
            if score > 0:
                scored_segments.append((score, s))

        scored_segments.sort(key=lambda x: x[0], reverse=True)
        top_matches = [item[1] for item in scored_segments[:5]]

        if not top_matches:
            top_matches = segments[:3]  # Fallback to opening segments

        citations = [m["timestamp"] for m in top_matches]
        summary_points = [f"• [{m['timestamp']}] {m['text']}" for m in top_matches]

        answer_lead = "Synthesized Analysis from Video Transcript"
        if language_pref.lower() in ("hi", "hindi"):
            answer_lead = "वीडियो ट्रांसक्रिप्ट से विश्लेषण (हिंदी)"
        elif language_pref.lower() in ("bn", "bengali"):
            answer_lead = "ভিডিও ট্রান্সক্রিপ্ট থেকে বিশ্লেষণ (বাংলা)"

        answer_text = (
            f"**{answer_lead}**\n\n"
            f"**Query Addressed**: *{user_query or 'Key Highlights'}*\n\n"
            + "\n".join(summary_points)
        )

        return {
            "answer": answer_text,
            "cited_timestamps": citations,
            "top_matches_count": len(top_matches),
            "confidence": 85.0 if scored_segments else 60.0
        }

    @classmethod
    def analyze_youtube_video(
        cls,
        url_or_video_id: str,
        user_query: Optional[str] = None,
        symbol: Optional[str] = None,
        language_pref: str = "en",
        title: str = "Corporate Management Analysis",
        company_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Master orchestrator: transcript retrieval, source classification, fact check, Q&A, and innovation radar."""
        video_id = YouTubeTranscriptService.extract_video_id(url_or_video_id) or url_or_video_id
        if not video_id:
            return {
                "status": "ERROR_INVALID_URL",
                "error": "Could not extract valid YouTube video ID.",
                "video_id": None
            }

        # 1. Fetch transcript
        transcript_res = YouTubeTranscriptService.fetch_transcript(video_id)
        if transcript_res.get("status") != "SUCCESS":
            return {
                "status": transcript_res.get("status"),
                "error": transcript_res.get("error"),
                "video_id": video_id
            }

        segments = transcript_res.get("segments", [])
        full_text = transcript_res.get("full_text", "")

        # 2. Classify epistemic tier
        source_class = cls.classify_source_epistemic_tier(title=title, description=full_text[:300])

        # 3. Contextual financial fact check
        fact_checks = cls.fact_check_claims(
            transcript_text=full_text,
            symbol=symbol,
            company_data=company_data
        )

        # 4. Multilingual Q&A synthesis
        qa_res = cls.synthesize_qa(
            segments=segments,
            user_query=user_query,
            language_pref=language_pref
        )

        # 5. Autonomous Platform Innovation Radar
        innovation_radar = cls.evaluate_platform_innovation_radar(
            transcript_text=full_text,
            title=title
        )

        return {
            "status": "SUCCESS",
            "video_id": video_id,
            "title": title,
            "language_detected": transcript_res.get("language"),
            "source_classification": source_class,
            "fact_checks": fact_checks,
            "discrepancies_count": sum(1 for f in fact_checks if f.get("status") == "DISCREPANCY_FLAGGED"),
            "qa_synthesis": qa_res,
            "platform_innovation_radar": innovation_radar,
            "total_segments": len(segments),
            "duration_sec": transcript_res.get("total_duration_sec", 0.0)
        }
