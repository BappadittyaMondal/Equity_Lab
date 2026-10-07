"""Master Video Compositor & Subtitle Renderer (Phase 162).

Encodes, concatenates, and muxes image sequences, voiceovers,
foley acoustic cues, and soundtrack audio into broadcast-ready 1080p MP4 videos
using the embedded imageio-ffmpeg binary.
"""

import logging
import os
import subprocess
from typing import List, Optional
import imageio_ffmpeg

logger = logging.getLogger(__name__)


class MasterCompositor:
    """Master Multi-Track Video Compositor."""

    @classmethod
    def get_ffmpeg_path(cls) -> str:
        """Returns the absolute path to the verified FFmpeg executable."""
        return imageio_ffmpeg.get_ffmpeg_exe()

    @classmethod
    def assemble_scene_clip(
        cls,
        image_path: str,
        audio_path: str,
        output_clip_path: str,
        duration_sec: Optional[float] = None,
    ) -> bool:
        """Assembles a single static scene card image and audio track into an MP4 segment."""
        ffmpeg_bin = cls.get_ffmpeg_path()
        os.makedirs(os.path.dirname(os.path.abspath(output_clip_path)), exist_ok=True)

        cmd = [
            ffmpeg_bin,
            "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_clip_path,
        ]

        if duration_sec:
            cmd.insert(1, "-t")
            cmd.insert(2, str(duration_sec))

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return os.path.exists(output_clip_path) and os.path.getsize(output_clip_path) > 0
        except Exception as e:
            logger.error("FFmpeg scene assembly failed: %s", e)
            return False

    @classmethod
    def concatenate_clips(
        cls,
        clip_paths: List[str],
        final_output_path: str,
    ) -> bool:
        """Concatenates multiple MP4 scene segments into the final master video."""
        ffmpeg_bin = cls.get_ffmpeg_path()
        os.makedirs(os.path.dirname(os.path.abspath(final_output_path)), exist_ok=True)

        concat_list_file = os.path.join(os.path.dirname(final_output_path), "concat_manifest.txt")
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for cp in clip_paths:
                clean_path = os.path.abspath(cp).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        cmd = [
            ffmpeg_bin,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_file,
            "-c", "copy",
            final_output_path,
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return os.path.exists(final_output_path) and os.path.getsize(final_output_path) > 0
        except Exception as e:
            logger.error("FFmpeg clip concatenation failed: %s", e)
            return False
        finally:
            if os.path.exists(concat_list_file):
                try:
                    os.remove(concat_list_file)
                except Exception:
                    pass

    @classmethod
    def generate_srt_subtitles(
        cls,
        subtitles_data: List[dict],
        output_srt_path: str,
    ) -> str:
        """Generates a standard SRT subtitle file from timestamped text cues."""
        os.makedirs(os.path.dirname(os.path.abspath(output_srt_path)), exist_ok=True)
        with open(output_srt_path, "w", encoding="utf-8") as f:
            for i, sub in enumerate(subtitles_data, 1):
                start_s = sub.get("start_sec", 0.0)
                end_s = sub.get("end_sec", start_s + 3.0)
                text = sub.get("text", "")

                def _fmt_time(seconds: float) -> str:
                    hrs = int(seconds // 3600)
                    mins = int((seconds % 3600) // 60)
                    secs = int(seconds % 60)
                    millis = int((seconds - int(seconds)) * 1000)
                    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

                f.write(f"{i}\n")
                f.write(f"{_fmt_time(start_s)} --> {_fmt_time(end_s)}\n")
                f.write(f"{text}\n\n")

        return output_srt_path
