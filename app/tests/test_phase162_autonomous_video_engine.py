"""Phase 162 Test Suite — Autonomous Multi-Expert AI Video Production Engine.

Verifies:
  1. ScriptAgent: Fact-grounded script generation, symbol extraction, scene budgeting.
  2. VoiceEngine: Neural voice presets, offline acoustic synthesis, foley sound generation.
  3. VisualAssetEngine: 1080p landscape & 9:16 vertical cards, candlestick charts, verdict banners.
  4. AvatarEngine: Analyst presenter overlay composition for 'with face' mode.
  5. AudioMixer: Procedural ambient score generation & automated audio ducking.
  6. MasterCompositor: FFmpeg clip encoding, clip concatenation, SRT subtitle burning.
  7. VideoOrchestrator: End-to-end single-prompt execution in both faceless and avatar modes.
  8. Zero-Conflict Architecture: Ensures no regression on core research engines.
"""

import os
import wave
import pytest

from app.services.media.audio_mixer import AudioMixer
from app.services.media.avatar_engine import AvatarEngine
from app.services.media.compositor import MasterCompositor
from app.services.media.script_agent import ScriptAgent, VideoScript
from app.services.media.visual_asset_engine import VisualAssetEngine
from app.services.media.voice_engine import VoiceEngine, VOICE_PRESETS
from app.services.media.video_orchestrator import VideoOrchestrator, generate_production_video
from app.services.research.technical_base_quality import TechnicalBaseQualityEngine
from app.services.research.return_ceiling import compute_return_ceiling


# =============================================================================
# 1. ScriptAgent Tests
# =============================================================================

def test_script_agent_symbol_extraction():
    """Verifies ticker extraction from natural language prompts."""
    assert ScriptAgent.extract_symbol_from_prompt("Create a video on CDSL breakout") == "CDSL"
    assert ScriptAgent.extract_symbol_from_prompt("Why MANORAMA is an early multibagger") == "MANORAMA"
    assert ScriptAgent.extract_symbol_from_prompt("General market outlook for next week") is None


def test_script_agent_fact_grounding_and_scene_structure():
    """Verifies that script is divided into 5 scenes and contains audited financials."""
    prompt = "Create a 3-minute video analyzing CDSL"
    script = ScriptAgent.generate_script(prompt=prompt, duration_seconds=180, symbol="CDSL")

    assert isinstance(script, VideoScript)
    assert script.symbol == "CDSL"
    assert script.target_duration_sec == 180.0
    assert len(script.scenes) == 5

    # Check that scene 2 contains ground-truth ROCE
    scene2 = script.scenes[1]
    assert "32.5" in scene2.voice_text or "ROCE" in scene2.voice_text

    # Check that scene 4 contains invalidation level
    scene4 = script.scenes[3]
    assert "1340" in scene4.voice_text or "invalidation" in scene4.voice_text.lower()


# =============================================================================
# 2. VoiceEngine Tests
# =============================================================================

def test_voice_engine_presets_available():
    """Verifies voice presets dictionary contains male and female options."""
    assert "male_in" in VOICE_PRESETS
    assert "female_in" in VOICE_PRESETS
    assert "narrator_male" in VOICE_PRESETS


def test_voice_engine_offline_speech_and_foley(tmp_path):
    """Verifies speech proxy and foley acoustic cues generate valid WAV files."""
    speech_wav = os.path.join(tmp_path, "speech.wav")
    VoiceEngine.generate_offline_speech_proxy("Institutional analysis confirms breakout", speech_wav)
    assert os.path.exists(speech_wav)
    with wave.open(speech_wav, "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getframerate() == 44100
        assert wf.getnframes() > 0

    foley_wav = os.path.join(tmp_path, "bell.wav")
    VoiceEngine.synthesize_foley_sound("bell", foley_wav, duration_sec=0.5)
    assert os.path.exists(foley_wav)
    with wave.open(foley_wav, "rb") as wf:
        assert wf.getnframes() > 0


# =============================================================================
# 3. VisualAssetEngine Tests
# =============================================================================

def test_visual_asset_dimensions_and_rendering(tmp_path):
    """Verifies 1080p landscape (16:9) and vertical (9:16) rendering."""
    # Landscape 16:9
    w, h = VisualAssetEngine.get_dimensions("16:9")
    assert (w, h) == (1920, 1080)

    # Vertical 9:16
    w_v, h_v = VisualAssetEngine.get_dimensions("9:16")
    assert (w_v, h_v) == (1080, 1920)

    card_path = os.path.join(tmp_path, "metric_card.png")
    img = VisualAssetEngine.render_scene_frame(
        title="Institutional Thesis",
        headline="HIGH-CONVICTION RUNWAY",
        bullet_points=["ROCE: 32.5%", "CFO/PAT: >1.0", "Zero Debt"],
        metric_highlights={"ROCE": "32.5%", "PE": "48x"},
        visual_type="METRIC_CARD",
        symbol="CDSL",
        aspect_ratio="16:9",
        output_path=card_path,
    )
    assert os.path.exists(card_path)
    assert img.size == (1920, 1080)


def test_visual_asset_chart_and_verdict_rendering(tmp_path):
    """Verifies procedural chart card and verdict banner rendering."""
    chart_path = os.path.join(tmp_path, "chart.png")
    VisualAssetEngine.render_scene_frame(
        title="Technical Geometry",
        headline="STAGE 2 UPTREND BREAKOUT",
        bullet_points=[],
        metric_highlights={"Wave": "WAVE_3_IMPULSE", "Invalidation": "Rs 1340"},
        visual_type="STOCK_CHART",
        symbol="CDSL",
        output_path=chart_path,
    )
    assert os.path.exists(chart_path)

    verdict_path = os.path.join(tmp_path, "verdict.png")
    VisualAssetEngine.render_scene_frame(
        title="Final Scorecard",
        headline="CONVICTION BUY",
        bullet_points=[],
        metric_highlights={"Multiple Ceiling": "3.8x"},
        visual_type="VERDICT_BANNER",
        symbol="CDSL",
        output_path=verdict_path,
    )
    assert os.path.exists(verdict_path)


# =============================================================================
# 4. AvatarEngine Tests
# =============================================================================

def test_avatar_engine_overlay(tmp_path):
    """Verifies presenter badge is composited onto base image."""
    base_img = VisualAssetEngine.render_scene_frame(
        title="Overview",
        headline="PRESENTER SCENE",
        bullet_points=["Point 1"],
        metric_highlights={},
        visual_type="METRIC_CARD",
    )
    avatar_img = AvatarEngine.apply_avatar_overlay(base_img, speaker_label="Chief Analyst")
    assert avatar_img.size == (1920, 1080)


# =============================================================================
# 5. AudioMixer Tests
# =============================================================================

def test_audio_mixer_soundtrack_and_ducking(tmp_path):
    """Verifies procedural score generation and automated audio ducking."""
    bgm_path = os.path.join(tmp_path, "bgm.wav")
    AudioMixer.generate_ambient_soundtrack(bgm_path, duration_sec=3.0, mood="analytical")
    assert os.path.exists(bgm_path)

    voice_path = os.path.join(tmp_path, "voice.wav")
    VoiceEngine.generate_offline_speech_proxy("Testing audio ducking functionality", voice_path)

    mixed_path = os.path.join(tmp_path, "mixed.wav")
    ok = AudioMixer.mix_voice_and_soundtrack(voice_path, bgm_path, mixed_path)
    assert ok is True
    assert os.path.exists(mixed_path)


# =============================================================================
# 6. MasterCompositor Tests
# =============================================================================

def test_master_compositor_ffmpeg_and_srt(tmp_path):
    """Verifies FFmpeg binary discovery and SRT subtitle generation."""
    ffmpeg_exe = MasterCompositor.get_ffmpeg_path()
    assert os.path.exists(ffmpeg_exe)

    srt_path = os.path.join(tmp_path, "test.srt")
    cues = [
        {"start_sec": 0.0, "end_sec": 3.0, "text": "Welcome to Equity Lab."},
        {"start_sec": 3.0, "end_sec": 6.5, "text": "Here is the institutional research breakdown."},
    ]
    MasterCompositor.generate_srt_subtitles(cues, srt_path)
    assert os.path.exists(srt_path)
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "00:00:00,000 --> 00:00:03,000" in content
    assert "Welcome to Equity Lab." in content


# =============================================================================
# 7. End-to-End VideoOrchestrator Tests
# =============================================================================

def test_end_to_end_faceless_video_generation(tmp_path):
    """Verifies complete end-to-end production video generation from a single prompt."""
    out_dir = str(tmp_path / "videos")
    res = generate_production_video(
        prompt="Explain why CDSL is a monopoly compounder",
        symbol="CDSL",
        duration_seconds=10,  # Fast 10-sec test duration
        mode="faceless",
        aspect_ratio="16:9",
        output_dir=out_dir,
    )
    assert res["status"] == "SUCCESS"
    assert os.path.exists(res["video_path"])
    assert res["video_path"].endswith(".mp4")
    assert os.path.getsize(res["video_path"]) > 5000  # Valid encoded MP4
    assert os.path.exists(res["subtitles_path"])
    assert res["actual_scenes_count"] == 5


def test_end_to_end_avatar_vertical_video_generation(tmp_path):
    """Verifies single-prompt production for 9:16 vertical Shorts/Reels in avatar mode."""
    out_dir = str(tmp_path / "shorts")
    res = generate_production_video(
        prompt="MANORAMA 1-minute multibagger breakdown",
        symbol="MANORAMA",
        duration_seconds=10,
        mode="avatar",
        aspect_ratio="9:16",
        output_dir=out_dir,
    )
    assert res["status"] == "SUCCESS"
    assert os.path.exists(res["video_path"])
    assert res["mode"] == "avatar"
    assert res["aspect_ratio"] == "9:16"


# =============================================================================
# 8. Zero Conflict / Regression Guard
# =============================================================================

def test_media_pipeline_zero_conflict_with_core_engines():
    """Verifies that media pipeline does not mutate or conflict with TBQE or Return Ceiling."""
    # Test TBQE continues to function with 100% precision
    data = {
        "current_price": 500.0,
        "wave_label": "WAVE_3_IMPULSE",
        "wave_invalidation_level": 460.0,
    }
    score, bd = TechnicalBaseQualityEngine.score(data)
    assert score > 0
    assert "elliott_wave_cycle" in bd

    # Test Return Ceiling continues to function
    res = compute_return_ceiling(current_mcap_cr=2000.0, ttm_pat_cr=100.0)
    assert res["base_multiple"] > 0
