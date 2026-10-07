"""Autonomous Multi-Expert AI Video Production Package (Phase 162).

Exposes:
  - VideoOrchestrator: Master multi-expert pipeline
  - generate_production_video: High-level single-prompt entry point
  - ScriptAgent: Topic to fact-grounded storyboard
  - VoiceEngine: Neural voiceover & foley acoustic generator
  - VisualAssetEngine: 1080p institutional scene card & chart renderer
  - AvatarEngine: Analyst presenter overlay engine
  - AudioMixer: Procedural soundtrack generator with audio ducking
  - MasterCompositor: FFmpeg multi-track encoder & subtitle renderer
"""

from app.services.media.audio_mixer import AudioMixer
from app.services.media.avatar_engine import AvatarEngine
from app.services.media.compositor import MasterCompositor
from app.services.media.script_agent import Scene, ScriptAgent, VideoScript
from app.services.media.visual_asset_engine import VisualAssetEngine
from app.services.media.voice_engine import VOICE_PRESETS, VoiceEngine
from app.services.media.video_orchestrator import VideoOrchestrator, generate_production_video

__all__ = [
    "VideoOrchestrator",
    "generate_production_video",
    "ScriptAgent",
    "Scene",
    "VideoScript",
    "VoiceEngine",
    "VOICE_PRESETS",
    "VisualAssetEngine",
    "AvatarEngine",
    "AudioMixer",
    "MasterCompositor",
]
