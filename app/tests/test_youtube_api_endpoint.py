"""Unit tests for YouTube Video Intelligence FastAPI Endpoints."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app


def test_youtube_analyze_api_endpoint(monkeypatch):
    """Verify /api/v1/youtube-analyze endpoint with mocked transcript service."""
    from app.core.config import settings
    monkeypatch.setattr(settings, "API_KEY_SECRET", "test_dev_key")

    client = TestClient(app)
    headers = {"X-API-Key": "test_dev_key"}

    mock_transcript_res = {
        "status": "SUCCESS",
        "video_id": "test_video_123",
        "language": "hi",
        "total_duration_sec": 450.0,
        "full_text": "Yeh official earnings concall mein management ne bataya ki unbilled revenue aur contract assets monitor ho rahe hain. Debt free status maintain kiya gaya hai.",
        "segments": [
            {"start": 10.0, "duration": 5.0, "timestamp": "00:10", "text": "Debt free status maintain kiya gaya hai."},
            {"start": 80.0, "duration": 10.0, "timestamp": "01:20", "text": "Ind AS 115 contract assets growth par vigilance hai."}
        ]
    }

    with patch("app.services.ingestion.youtube_transcript_service.YouTubeTranscriptService.fetch_transcript", return_value=mock_transcript_res):
        payload = {
            "url": "https://www.youtube.com/watch?v=test_video_123",
            "query": "What is the debt position and contract asset status?",
            "symbol": "MOCK_TECH",
            "language_pref": "en",
            "title": "Q1 FY25 Earnings Concall"
        }

        # 1. Primary endpoint: /api/v1/youtube-analyze
        res = client.post("/api/v1/youtube-analyze", json=payload, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert data["video_id"] == "test_video_123"
        assert data["source_classification"]["tier"] == "TIER_1_OFFICIAL_CONCALL"
        assert "qa_synthesis" in data
        assert "platform_innovation_radar" in data
        assert data["platform_innovation_radar"]["has_platform_improvement_idea"] is True

        # 2. Research alias endpoint: /api/v1/research/youtube-analyze
        res_alias = client.post("/api/v1/research/youtube-analyze", json=payload, headers=headers)
        assert res_alias.status_code == 200
        assert res_alias.json()["status"] == "SUCCESS"


def test_youtube_analyze_unauthorized(monkeypatch):
    """Verify endpoint rejects unauthenticated requests when API_KEY_SECRET is configured."""
    from app.core.config import settings
    monkeypatch.setattr(settings, "API_KEY_SECRET", "test_secure_key")

    client = TestClient(app)
    res = client.post("/api/v1/youtube-analyze", json={"url": "https://youtu.be/dQw4w9WgXcQ"})
    assert res.status_code == 401

