"""Procedural Soundtrack Generator & Audio Ducking Mixer (Phase 162).

Generates ambient royalty-free soundtrack audio and mixes voice tracks
with automated audio ducking (lowering music volume while voice is active)
using pure Python standard library wave & math.
"""

import math
import os
import struct
import wave
from typing import Optional


class AudioMixer:
    """Soundtrack Generator & Audio Ducking Mixer."""

    @classmethod
    def generate_ambient_soundtrack(
        cls,
        output_path: str,
        duration_sec: float = 60.0,
        mood: str = "analytical",
        sample_rate: int = 44100,
    ) -> None:
        """Generates procedural harmonic ambient background score."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        total_samples = int(sample_rate * duration_sec)

        # Chords & Frequencies based on mood
        if mood == "dramatic":
            # C minor / suspense pad (130.81, 155.56, 196.00)
            base_freqs = [130.81, 155.56, 196.00]
        elif mood == "triumphant":
            # C major / confident resolution (130.81, 164.81, 196.00)
            base_freqs = [130.81, 164.81, 196.00, 261.63]
        elif mood == "energetic":
            # Pulse drive (146.83, 220.00, 293.66)
            base_freqs = [146.83, 220.00, 293.66]
        else:  # analytical
            # Calm ambient fifth (110.00, 164.81, 220.00)
            base_freqs = [110.00, 164.81, 220.00]

        with wave.open(output_path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)

            data = bytearray()
            for i in range(total_samples):
                t = float(i) / sample_rate
                # Slow LFO breathing filter
                lfo = 0.6 + 0.3 * math.sin(2.0 * math.pi * 0.2 * t)

                harmonic_sum = 0.0
                for f in base_freqs:
                    harmonic_sum += math.sin(2.0 * math.pi * f * t)
                harmonic_sum /= len(base_freqs)

                sample = int(32767.0 * 0.12 * lfo * harmonic_sum)
                data.extend(struct.pack("<h", max(-32767, min(32767, sample))))

            wf.writeframes(data)

    @classmethod
    def mix_voice_and_soundtrack(
        cls,
        voice_path: str,
        soundtrack_path: str,
        output_path: str,
        ducking_ratio: float = 0.18,  # Music volume during voice (18%)
        music_nominal_vol: float = 0.55,  # Music volume during pauses (55%)
    ) -> bool:
        """Mixes voice and background music with automated ducking."""
        if not (os.path.exists(voice_path) and os.path.exists(soundtrack_path)):
            return False

        with wave.open(voice_path, "rb") as vf, wave.open(soundtrack_path, "rb") as sf:
            v_sr = vf.getframerate()
            s_sr = sf.getframerate()
            v_frames = vf.readframes(vf.getnframes())
            s_frames = sf.readframes(sf.getnframes())

        v_samples = [struct.unpack("<h", v_frames[i : i + 2])[0] for i in range(0, len(v_frames), 2)]
        s_samples = [struct.unpack("<h", s_frames[i : i + 2])[0] for i in range(0, len(s_frames), 2)]

        out_len = max(len(v_samples), len(s_samples))
        mixed_data = bytearray()

        for i in range(out_len):
            v_val = v_samples[i] if i < len(v_samples) else 0
            s_val = s_samples[i] if i < len(s_samples) else 0

            # Ducking detector: if voice has significant energy, duck music
            voice_active = abs(v_val) > 800
            current_duck = ducking_ratio if voice_active else music_nominal_vol

            combined = int(v_val * 0.90 + (s_val * current_duck))
            clamped = max(-32767, min(32767, combined))
            mixed_data.extend(struct.pack("<h", clamped))

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with wave.open(output_path, "wb") as out_f:
            out_f.setnchannels(1)
            out_f.setsampwidth(2)
            out_f.setframerate(v_sr)
            out_f.writeframes(mixed_data)

        return True
