"""Multilingual YouTube Transcript Extraction & Caching Service.

Provides robust URL video ID parsing, multilingual subtitle retrieval 
(Hindi, Bengali, English, Hinglish/Benglish), segment normalization, 
and persistent disk caching to eliminate redundant network fetches and token costs.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join("data", "video_transcripts_cache")


class YouTubeTranscriptService:
    """Institutional service for fetching and caching YouTube transcripts."""

    DEFAULT_LANGUAGES = ["hi", "hi-Latn", "bn", "en", "en-IN"]

    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """Extracts standard 11-character YouTube video ID from heterogeneous URL formats.
        
        Supports:
        - https://www.youtube.com/watch?v=dQw4w9WgXcQ
        - https://youtu.be/dQw4w9WgXcQ
        - https://www.youtube.com/embed/dQw4w9WgXcQ
        - https://www.youtube.com/shorts/dQw4w9WgXcQ
        - https://www.youtube.com/live/dQw4w9WgXcQ
        - Bare 11-character video ID
        """
        if not url or not isinstance(url, str):
            return None
        clean_url = url.strip()

        # If already a valid video ID format (alphanumeric, -, _)
        if re.fullmatch(r"[a-zA-Z0-9_-]{8,32}", clean_url):
            return clean_url

        patterns = [
            r"(?:v=|\/v\/|youtu\.be\/|\/embed\/|\/shorts\/|\/live\/)([a-zA-Z0-9_-]{8,32})",
            r"[?&]v=([a-zA-Z0-9_-]{8,32})",
        ]
        for pattern in patterns:
            match = re.search(pattern, clean_url)
            if match:
                return match.group(1)

        return None

    @classmethod
    def seconds_to_timestamp(cls, seconds: float) -> str:
        """Converts floating point seconds into clean MM:SS or HH:MM:SS format."""
        total_sec = int(max(0, seconds))
        hours = total_sec // 3600
        minutes = (total_sec % 3600) // 60
        secs = total_sec % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    @classmethod
    def normalize_segments(cls, raw_segments: List[Any]) -> List[Dict[str, Any]]:
        """Normalizes raw transcript entries into a consistent dictionary format."""
        normalized = []
        for s in raw_segments:
            if isinstance(s, dict):
                start = float(s.get("start", 0.0))
                duration = float(s.get("duration", 0.0))
                text = str(s.get("text", "")).strip()
            elif hasattr(s, "start") and hasattr(s, "duration") and hasattr(s, "text"):
                start = float(getattr(s, "start", 0.0))
                duration = float(getattr(s, "duration", 0.0))
                text = str(getattr(s, "text", "")).strip()
            else:
                continue

            if text:
                normalized.append({
                    "start": round(start, 2),
                    "duration": round(duration, 2),
                    "timestamp": cls.seconds_to_timestamp(start),
                    "text": text
                })
        return normalized

    @classmethod
    def get_cached_transcript(cls, video_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached transcript from local disk if present."""
        if not os.path.exists(CACHE_DIR):
            return None
        cache_file = os.path.join(CACHE_DIR, f"{video_id}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data
            except Exception as e:
                logger.warning("Error reading transcript cache for %s: %s", video_id, e)
        return None

    @classmethod
    def save_cached_transcript(cls, video_id: str, payload: Dict[str, Any]) -> None:
        """Saves transcript payload to local disk cache."""
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            cache_file = os.path.join(CACHE_DIR, f"{video_id}.json")
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning("Error saving transcript cache for %s: %s", video_id, e)

    @classmethod
    def fetch_transcript(
        cls,
        video_id: str,
        languages: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Fetches complete video transcript with multilingual fallbacks and caching."""
        if not video_id:
            return {
                "video_id": video_id,
                "status": "ERROR_INVALID_VIDEO_ID",
                "error": "No valid YouTube video ID provided.",
                "segments": [],
                "full_text": "",
                "language": None
            }

        # Check disk cache
        if use_cache:
            cached = cls.get_cached_transcript(video_id)
            if cached and cached.get("status") == "SUCCESS":
                cached["source"] = "DISK_CACHE"
                return cached

        target_languages = languages or cls.DEFAULT_LANGUAGES

        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            api = YouTubeTranscriptApi()
            
            fetched = None
            try:
                fetched = api.fetch(video_id, languages=target_languages)
            except Exception:
                # Fallback to listing all transcripts and picking first available
                try:
                    transcript_list = api.list(video_id)
                    for t in transcript_list:
                        fetched = t.fetch()
                        break
                except Exception:
                    pass

            if fetched is None:
                return {
                    "video_id": video_id,
                    "status": "ERROR_NO_TRANSCRIPT",
                    "error": "No manual or auto-generated transcript available for this video.",
                    "segments": [],
                    "full_text": "",
                    "language": None
                }

            raw_data = fetched.to_raw_data() if hasattr(fetched, "to_raw_data") else list(fetched)
            normalized = cls.normalize_segments(raw_data)
            full_text = " ".join(s["text"] for s in normalized)

            result = {
                "video_id": video_id,
                "status": "SUCCESS",
                "source": "NETWORK_FETCH",
                "language": getattr(fetched, "language_code", "unknown"),
                "language_name": getattr(fetched, "language", "unknown"),
                "is_generated": getattr(fetched, "is_generated", False),
                "segment_count": len(normalized),
                "total_duration_sec": normalized[-1]["start"] + normalized[-1]["duration"] if normalized else 0.0,
                "segments": normalized,
                "full_text": full_text
            }

            if use_cache:
                cls.save_cached_transcript(video_id, result)

            return result

        except Exception as e:
            err_msg = str(e)
            logger.warning("YouTube transcript fetch failed for %s: %s", video_id, err_msg)
            return {
                "video_id": video_id,
                "status": "ERROR_FETCH_FAILED",
                "error": err_msg,
                "segments": [],
                "full_text": "",
                "language": None
            }

    @classmethod
    def get_timestamped_blocks(
        cls,
        segments: List[Dict[str, Any]],
        block_duration_sec: float = 120.0
    ) -> List[Dict[str, Any]]:
        """Groups transcript segments into coherent chronological blocks (e.g. 2-minute blocks)."""
        if not segments:
            return []

        blocks = []
        current_block_texts = []
        block_start = segments[0]["start"]

        for s in segments:
            if (s["start"] - block_start) >= block_duration_sec and current_block_texts:
                blocks.append({
                    "start_sec": block_start,
                    "timestamp": cls.seconds_to_timestamp(block_start),
                    "text": " ".join(current_block_texts)
                })
                current_block_texts = []
                block_start = s["start"]
            current_block_texts.append(s["text"])

        if current_block_texts:
            blocks.append({
                "start_sec": block_start,
                "timestamp": cls.seconds_to_timestamp(block_start),
                "text": " ".join(current_block_texts)
            })

        return blocks
