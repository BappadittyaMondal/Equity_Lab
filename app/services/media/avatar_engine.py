"""Presenter & Talking Avatar Composition Engine (Phase 162).

Manages avatar presenter overlays for 'with face' video production.
Composites institutional presenter cards or floating speaker badges
with zero external GPU dependencies.
"""

from typing import Tuple
from PIL import Image, ImageDraw


class AvatarEngine:
    """Presenter Overlay & Avatar Engine."""

    COLOR_ACCENT = (56, 189, 248)       # Cyan glowing border
    COLOR_AVATAR_BG = (15, 23, 42)      # Deep slate

    @classmethod
    def apply_avatar_overlay(
        cls,
        base_img: Image.Image,
        speaker_label: str = "Senior Equity Analyst",
        avatar_size: Tuple[int, int] = (240, 240),
        position: str = "bottom_right",
    ) -> Image.Image:
        """Composites an institutional talking-head analyst avatar badge onto the scene."""
        w, h = base_img.size
        aw, ah = avatar_size

        if position == "bottom_right":
            x = w - aw - 80
            y = h - ah - 80
        else:
            x = 80
            y = h - ah - 80

        draw = ImageDraw.Draw(base_img)

        # Circular or rounded rectangle presenter badge
        badge_box = [x, y, x + aw, y + ah]
        draw.ellipse(badge_box, fill=cls.COLOR_AVATAR_BG, outline=cls.COLOR_ACCENT, width=4)

        # Draw presenter silhouette / icon
        cx = x + aw // 2
        cy = y + ah // 2

        # Head circle
        head_radius = aw // 6
        draw.ellipse([cx - head_radius, cy - head_radius - 20, cx + head_radius, cy + head_radius - 20], fill=(71, 85, 105))
        # Body curve
        draw.chord([cx - aw // 3, cy + 5, cx + aw // 3, cy + ah // 2 + 10], start=0, end=180, fill=(51, 65, 85))

        # Speaking indicator waveform
        wave_y = y + ah - 35
        for i, h_bar in enumerate([8, 16, 24, 18, 12, 22, 10]):
            wx = cx - 25 + i * 8
            draw.line([(wx, wave_y - h_bar // 2), (wx, wave_y + h_bar // 2)], fill=cls.COLOR_ACCENT, width=2)

        # Lower-third Speaker Label
        draw.rectangle([x - 20, y + ah + 10, x + aw + 20, y + ah + 45], fill=(30, 41, 59), outline=cls.COLOR_ACCENT, width=1)
        draw.text((x - 10, y + ah + 18), speaker_label.upper(), fill=(248, 250, 252))

        return base_img
