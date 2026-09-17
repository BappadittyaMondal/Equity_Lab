"""Unit tests for YouTubeTranscriptService."""

import os
import shutil
import pytest
from unittest.mock import MagicMock, patch
from app.services.ingestion.youtube_transcript_service import YouTubeTranscriptService, CACHE_DIR


def test_youtube_url_video_id_extraction():
    """Verify video ID extraction across diverse URL structures."""
    valid_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/live/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s", "dQw4w9WgXcQ"),
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ]
    for url, expected in valid_cases:
        assert YouTubeTranscriptService.extract_video_id(url) == expected

    invalid_cases = [
        "",
        None,
        "https://example.com/not-youtube",
        "https://youtube.com/shortid",
    ]
    for url in invalid_cases:
        assert YouTubeTranscriptService.extract_video_id(url) is None


def test_seconds_to_timestamp():
    """Verify conversion of seconds to MM:SS and HH:MM:SS."""
    assert YouTubeTranscriptService.seconds_to_timestamp(0) == "00:00"
    assert YouTubeTranscriptService.seconds_to_timestamp(45) == "00:45"
    assert YouTubeTranscriptService.seconds_to_timestamp(125) == "02:05"
    assert YouTubeTranscriptService.seconds_to_timestamp(3665) == "01:01:05"


def test_normalize_segments():
    """Verify normalization of heterogeneous segment structures."""
    raw = [
        {"start": 1.5, "duration": 3.2, "text": "Company revenue grew 25%"},
        {"start": 5.0, "duration": 2.0, "text": "Capex commissioning in Q3"},
        {"invalid": "no text"},
    ]
    norm = YouTubeTranscriptService.normalize_segments(raw)
    assert len(norm) == 2
    assert norm[0]["timestamp"] == "00:01"
    assert norm[0]["text"] == "Company revenue grew 25%"
    assert norm[1]["timestamp"] == "00:05"
    assert norm[1]["duration"] == 2.0


def test_timestamped_blocks_grouping():
    """Verify chronological grouping of segments into 2-minute blocks."""
    segments = [
        {"start": 10.0, "duration": 5.0, "timestamp": "00:10", "text": "Opening remarks."},
        {"start": 70.0, "duration": 10.0, "timestamp": "01:10", "text": "Q1 performance review."},
        {"start": 135.0, "duration": 15.0, "timestamp": "02:15", "text": "Margin expansion discussion."},
    ]
    blocks = YouTubeTranscriptService.get_timestamped_blocks(segments, block_duration_sec=120.0)
    assert len(blocks) == 2
    assert blocks[0]["timestamp"] == "00:10"
    assert "Opening remarks. Q1 performance review." in blocks[0]["text"]
    assert blocks[1]["timestamp"] == "02:15"
    assert "Margin expansion discussion." in blocks[1]["text"]


def test_cache_roundtrip(tmp_path):
    """Verify saving to and reading from disk cache."""
    test_video_id = "test_vid_123"
    test_payload = {
        "video_id": test_video_id,
        "status": "SUCCESS",
        "language": "hi",
        "full_text": "Yeh company ka order book bohot strong hai",
        "segments": [{"start": 0.0, "duration": 2.0, "timestamp": "00:00", "text": "Yeh company"}]
    }

    # Use monkeypatch for CACHE_DIR
    custom_cache = str(tmp_path / "test_cache")
    with patch("app.services.ingestion.youtube_transcript_service.CACHE_DIR", custom_cache):
        YouTubeTranscriptService.save_cached_transcript(test_video_id, test_payload)
        cached = YouTubeTranscriptService.get_cached_transcript(test_video_id)
        assert cached is not None
        assert cached["video_id"] == test_video_id
        assert cached["language"] == "hi"

        # Verify fetch uses cache
        res = YouTubeTranscriptService.fetch_transcript(test_video_id, use_cache=True)
        assert res["source"] == "DISK_CACHE"
        assert res["full_text"] == test_payload["full_text"]


def test_fetch_transcript_mocked_network():
    """Verify fetch_transcript workflow with mocked YouTubeTranscriptApi."""
    mock_fetched = MagicMock()
    mock_fetched.language_code = "hi"
    mock_fetched.language = "Hindi"
    mock_fetched.is_generated = False
    mock_fetched.to_raw_data.return_value = [
        {"start": 0.0, "duration": 2.5, "text": "Management concall presentation"},
        {"start": 2.5, "duration": 3.0, "text": "Net block turnover is 3.5x"}
    ]

    with patch("youtube_transcript_api.YouTubeTranscriptApi.fetch", return_value=mock_fetched):
        res = YouTubeTranscriptService.fetch_transcript("mock_video_99", use_cache=False)
        assert res["status"] == "SUCCESS"
        assert res["language"] == "hi"
        assert res["segment_count"] == 2
        assert "Management concall presentation" in res["full_text"]

