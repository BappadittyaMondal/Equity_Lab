"""Autonomous Multi-Expert Video Orchestrator (Phase 162).

Coordinates the multi-expert pipeline from a single prompt to a finished,
broadcast-ready 1080p MP4 video for YouTube / Facebook / Reels.
"""

import logging
import os
import shutil
import tempfile
import time
from typing import Any, Dict, Optional

from app.services.media.audio_mixer import AudioMixer
from app.services.media.avatar_engine import AvatarEngine
from app.services.media.compositor import MasterCompositor
from app.services.media.script_agent import ScriptAgent, VideoScript
from app.services.media.visual_asset_engine import VisualAssetEngine
from app.services.media.voice_engine import VoiceEngine

logger = logging.getLogger(__name__)


class VideoOrchestrator:
    """Master Orchestration Engine for AI Video Production."""

    @classmethod
    def generate_video(
        cls,
        prompt: str,
        symbol: Optional[str] = None,
        duration_seconds: int = 60,
        mode: str = "faceless",  # faceless or avatar
        aspect_ratio: str = "16:9",  # 16:9 or 9:16
        voice_preset: str = "narrator_male",
        dossier: Optional[Dict[str, Any]] = None,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """End-to-end multi-expert production video generation pipeline."""
        start_time = time.time()
        final_dir = output_dir or os.path.join("data", "generated_videos")
        os.makedirs(final_dir, exist_ok=True)

        # 1. Expert 1: Script & Narrative Converter
        script: VideoScript = ScriptAgent.generate_script(
            prompt=prompt,
            duration_seconds=duration_seconds,
            symbol=symbol,
            dossier=dossier,
            mode=mode,
            aspect_ratio=aspect_ratio,
            voice_preset=voice_preset,
        )

        sym_tag = script.symbol or "RESEARCH"
        timestamp_str = int(time.time())
        video_filename = f"{sym_tag}_{mode}_{aspect_ratio.replace(':', 'x')}_{timestamp_str}.mp4"
        final_video_path = os.path.join(final_dir, video_filename)
        final_srt_path = os.path.join(final_dir, f"{sym_tag}_{timestamp_str}.srt")

        # Working temporary directory for scene rendering
        with tempfile.TemporaryDirectory() as temp_work_dir:
            scene_clips = []
            subtitles_list = []
            cumulative_time = 0.0

            # 2. Expert 5: Generate Ambient Soundtrack for the video duration
            soundtrack_path = os.path.join(temp_work_dir, "master_bgm.wav")
            AudioMixer.generate_ambient_soundtrack(
                output_path=soundtrack_path,
                duration_sec=script.target_duration_sec + 5.0,
                mood=script.scenes[0].background_mood if script.scenes else "analytical",
            )

            # Process each scene through specialized expert engines
            for idx, scene in enumerate(script.scenes, 1):
                scene_prefix = os.path.join(temp_work_dir, f"scene_{idx:02d}")

                # 3. Expert 2: Storyboard & Visual Asset Engine
                img_path = f"{scene_prefix}_card.png"
                scene_img = VisualAssetEngine.render_scene_frame(
                    title=scene.title,
                    headline=scene.overlay_headline,
                    bullet_points=scene.overlay_bullet_points,
                    metric_highlights=scene.metric_highlights,
                    visual_type=scene.visual_type,
                    symbol=script.symbol,
                    aspect_ratio=aspect_ratio,
                    output_path=None,  # keep in memory for avatar compositing
                )

                # 4. Expert 3: Presenter & Avatar Engine
                if mode == "avatar" or scene.visual_type == "AVATAR_PRESENTER":
                    scene_img = AvatarEngine.apply_avatar_overlay(
                        base_img=scene_img,
                        speaker_label="Senior Equity Analyst",
                        avatar_size=(240, 240) if aspect_ratio == "16:9" else (180, 180),
                    )
                scene_img.save(img_path, "PNG")

                # 5. Expert 4: Voice & Foley Audio Engine
                raw_voice_path = f"{scene_prefix}_voice.wav"
                VoiceEngine.synthesize_speech(
                    text=scene.voice_text,
                    output_path=raw_voice_path,
                    voice_preset=scene.speaker,
                )

                # 6. Foley Sound Effect Injection
                if scene.foley_cue:
                    foley_path = f"{scene_prefix}_foley.wav"
                    VoiceEngine.synthesize_foley_sound(
                        foley_type=scene.foley_cue,
                        output_path=foley_path,
                        duration_sec=0.8,
                    )

                # 7. Ducking Mix: Voice + Background Music segment
                mixed_audio_path = f"{scene_prefix}_mixed.wav"
                # Use voice track as primary mixed audio
                if not AudioMixer.mix_voice_and_soundtrack(
                    voice_path=raw_voice_path,
                    soundtrack_path=soundtrack_path,
                    output_path=mixed_audio_path,
                ):
                    mixed_audio_path = raw_voice_path

                # 8. Expert 6: Scene Assembler
                clip_path = f"{scene_prefix}_clip.mp4"
                if MasterCompositor.assemble_scene_clip(
                    image_path=img_path,
                    audio_path=mixed_audio_path,
                    output_clip_path=clip_path,
                    duration_sec=scene.duration_sec,
                ):
                    scene_clips.append(clip_path)

                # Accumulate Subtitles
                subtitles_list.append({
                    "start_sec": cumulative_time,
                    "end_sec": cumulative_time + scene.duration_sec,
                    "text": scene.voice_text,
                })
                cumulative_time += scene.duration_sec

            # Concatenate all clips into the master video
            success = MasterCompositor.concatenate_clips(scene_clips, final_video_path)
            MasterCompositor.generate_srt_subtitles(subtitles_list, final_srt_path)

        render_sec = round(time.time() - start_time, 2)

        return {
            "status": "SUCCESS" if (success and os.path.exists(final_video_path)) else "FAILED",
            "video_path": os.path.abspath(final_video_path),
            "subtitles_path": os.path.abspath(final_srt_path),
            "topic": prompt,
            "symbol": script.symbol,
            "target_duration_sec": script.target_duration_sec,
            "actual_scenes_count": len(script.scenes),
            "estimated_word_count": script.estimated_word_count,
            "mode": mode,
            "aspect_ratio": aspect_ratio,
            "render_time_sec": render_sec,
            "format": "H.264 / AAC 1080p MP4",
        }


def generate_production_video(
    prompt: str,
    symbol: Optional[str] = None,
    duration_seconds: int = 60,
    mode: str = "faceless",
    aspect_ratio: str = "16:9",
    voice_preset: str = "narrator_male",
    dossier: Optional[Dict[str, Any]] = None,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Top-level single-prompt entry point for production video generation."""
    return VideoOrchestrator.generate_video(
        prompt=prompt,
        symbol=symbol,
        duration_seconds=duration_seconds,
        mode=mode,
        aspect_ratio=aspect_ratio,
        voice_preset=voice_preset,
        dossier=dossier,
        output_dir=output_dir,
    )
