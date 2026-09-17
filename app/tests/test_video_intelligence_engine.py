"""Unit tests for VideoIntelligenceEngine & Platform Innovation Radar."""

import pytest
from unittest.mock import MagicMock, patch
from app.services.research.video_intelligence_engine import VideoIntelligenceEngine


def test_source_classification():
    """Verify epistemic classification: Tier-1 Official Concall vs Tier-2 Retail Commentary."""
    # 1. Official concall
    res_concall = VideoIntelligenceEngine.classify_source_epistemic_tier(
        title="Tata Motors Q1 FY25 Earnings Conference Call",
        channel="Tata Motors Official"
    )
    assert res_concall["tier"] == "TIER_1_OFFICIAL_CONCALL"
    assert res_concall["credibility_grade"] == "A+"
    assert res_concall["epistemic_authority"] == "PRIMARY_CATALYST_FEED"

    # 2. Retail influencer commentary
    res_influencer = VideoIntelligenceEngine.classify_source_epistemic_tier(
        title="Top 5 Multibagger Stocks to Buy Now for 100x Return",
        channel="SuperStockTrader"
    )
    assert res_influencer["tier"] == "TIER_2_INFLUENCER_COMMENTARY"
    assert res_influencer["credibility_grade"] == "B"
    assert res_influencer["epistemic_authority"] == "QUALITATIVE_SENTIMENT_ONLY"


def test_fact_checking_discrepancies():
    """Verify cross-referencing transcript claims against audited company financials."""
    # Case 1: Speaker claims debt free, audited shows heavy debt
    audited_indebted = {
        "debt": 850.0,
        "debt_to_equity": 1.45,
        "net_block": 400.0
    }
    transcript_text = "Yeh company completely debt free hai aur iska balance sheet bohot clean hai."
    findings = VideoIntelligenceEngine.fact_check_claims(transcript_text, company_data=audited_indebted)
    assert len(findings) > 0
    assert findings[0]["topic"] == "DEBT_SOLVENCY"
    assert findings[0]["status"] == "DISCREPANCY_FLAGGED"
    assert findings[0]["severity"] == "HIGH_ALERT"
    assert "₹850.0Cr" in findings[0]["audited_fact"]

    # Case 2: Speaker claims order book that exceeds fixed asset capacity by 10x
    audited_capacity = {
        "debt": 0.0,
        "debt_to_equity": 0.05,
        "net_block": 100.0
    }
    transcript_orders = "Management announced an order book of ₹2,500 Cr in EPC construction."
    findings_order = VideoIntelligenceEngine.fact_check_claims(transcript_orders, company_data=audited_capacity)
    assert len(findings_order) > 0
    assert any(f["topic"] == "CAPACITY_FEASIBILITY" for f in findings_order)
    cfr_finding = next(f for f in findings_order if f["topic"] == "CAPACITY_FEASIBILITY")
    assert cfr_finding["status"] == "CAPACITY_STRESS_WARNING"


def test_qa_synthesis_with_timestamps():
    """Verify evidence-grounded Q&A extraction citing precise timestamps."""
    segments = [
        {"start": 12.0, "duration": 4.0, "timestamp": "00:12", "text": "Our domestic EV EBITDA margins reached 4.2% in Q1."},
        {"start": 45.0, "duration": 5.0, "timestamp": "00:45", "text": "Annual commercial vehicle capex is capped at 2500 Cr."},
        {"start": 120.0, "duration": 6.0, "timestamp": "02:00", "text": "Raw material commodity inflation is largely passed through."}
    ]

    # English query
    qa_en = VideoIntelligenceEngine.synthesize_qa(segments, user_query="What is EV margin and capex?", language_pref="en")
    assert "00:12" in qa_en["cited_timestamps"]
    assert "EV EBITDA margins reached 4.2%" in qa_en["answer"]

    # Hindi query
    qa_hi = VideoIntelligenceEngine.synthesize_qa(segments, user_query="Capex kitna hoga?", language_pref="hi")
    assert "00:45" in qa_hi["cited_timestamps"]
    assert "2500 Cr" in qa_hi["answer"]
    assert "हिंदी" in qa_hi["answer"]

    # Bengali query
    qa_bn = VideoIntelligenceEngine.synthesize_qa(segments, user_query="EV margin koto?", language_pref="bn")
    assert "বাংলা" in qa_bn["answer"]


def test_platform_innovation_radar():
    """Verify autonomous identification of novel institutional models vs retail folklore veto."""
    # 1. Retail folklore veto
    folklore_text = "Use this secret indicator with 99% win rate to double your money tomorrow in options jackpot."
    radar_folk = VideoIntelligenceEngine.evaluate_platform_innovation_radar(folklore_text)
    assert radar_folk["has_platform_improvement_idea"] is False
    assert radar_folk["status"] == "RETAIL_FOLKLORE_VETOED"

    # 2. Genuine institutional innovation (Ind AS 115 Unbilled Revenue Drift)
    institutional_text = (
        "In EPC contracting, when unbilled revenue under Ind AS 115 and contract assets grow faster "
        "than billable receivables, operating cash flow collapses two quarters later."
    )
    radar_inst = VideoIntelligenceEngine.evaluate_platform_innovation_radar(institutional_text)
    assert radar_inst["has_platform_improvement_idea"] is True
    assert radar_inst["status"] == "INNOVATION_ADVISORY_DETECTED"
    assert len(radar_inst["advisories"]) > 0
    adv = radar_inst["advisories"][0]
    assert "Ind AS 115" in adv["innovation_topic"]
    assert "Engine F12" in adv["target_engine"]
    assert "HIGH_ALPHA" in adv["fiduciary_impact"]


def test_master_video_analysis_orchestrator():
    """Verify end-to-end analyze_youtube_video orchestration."""
    mock_transcript_res = {
        "status": "SUCCESS",
        "video_id": "dQw4w9WgXcQ",
        "language": "hi",
        "total_duration_sec": 300.0,
        "full_text": "Yeh management interview mein unbilled revenue aur contract assets par charcha hui. Company completely debt free hai.",
        "segments": [
            {"start": 10.0, "duration": 5.0, "timestamp": "00:10", "text": "Company completely debt free hai."},
            {"start": 60.0, "duration": 8.0, "timestamp": "01:00", "text": "Hum contract assets aur unbilled revenue monitor karte hain."}
        ]
    }

    with patch("app.services.ingestion.youtube_transcript_service.YouTubeTranscriptService.fetch_transcript", return_value=mock_transcript_res):
        res = VideoIntelligenceEngine.analyze_youtube_video(
            url_or_video_id="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            user_query="Debt aur contract assets ka kya status hai?",
            title="CEO Management Interview Q1",
            company_data={"debt": 500.0, "debt_to_equity": 1.2}  # Discrepancy trigger
        )

        assert res["status"] == "SUCCESS"
        assert res["video_id"] == "dQw4w9WgXcQ"
        assert res["source_classification"]["tier"] == "TIER_1_OFFICIAL_CONCALL"
        assert res["discrepancies_count"] == 1  # Flagged debt discrepancy
        assert res["platform_innovation_radar"]["has_platform_improvement_idea"] is True
        assert len(res["qa_synthesis"]["cited_timestamps"]) > 0
