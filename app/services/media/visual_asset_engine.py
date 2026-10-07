"""Visual Asset & Institutional Scene Card Engine (Phase 162).

Generates high-resolution (1080p landscape & vertical) institutional
presentation cards, procedural candlestick charts, and metric dashboards
using Pillow with zero external GPU requirements.
"""

import os
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont


class VisualAssetEngine:
    """Institutional Visual Asset & Graphic Renderer."""

    # Color Palette: Deep Institutional Dark Mode
    COLOR_BG_DARK = (11, 17, 32)       # #0b1120 Deep space navy
    COLOR_BG_CARD = (30, 41, 59)       # #1e293b Slate 800
    COLOR_BORDER = (51, 65, 85)        # #334155 Slate 700
    COLOR_CYAN = (56, 189, 248)        # #38bdf8 Sky 400 (Accents)
    COLOR_EMERALD = (52, 211, 153)     # #34d399 Emerald 400 (Bullish)
    COLOR_ROSE = (251, 113, 133)       # #fb7185 Rose 400 (Bearish/Alert)
    COLOR_TEXT_WHITE = (248, 250, 252) # #f8fafc Pure slate white
    COLOR_TEXT_MUTED = (148, 163, 184) # #94a3b8 Slate 400

    @classmethod
    def get_dimensions(cls, aspect_ratio: str = "16:9") -> Tuple[int, int]:
        """Returns (width, height) for specified aspect ratio."""
        if aspect_ratio == "9:16":
            return (1080, 1920)
        return (1920, 1080)

    @classmethod
    def render_scene_frame(
        cls,
        title: str,
        headline: str,
        bullet_points: List[str],
        metric_highlights: Dict[str, Any],
        visual_type: str = "METRIC_CARD",
        symbol: Optional[str] = None,
        aspect_ratio: str = "16:9",
        output_path: Optional[str] = None,
    ) -> Image.Image:
        """Renders a complete 1080p scene card image."""
        w, h = cls.get_dimensions(aspect_ratio)
        img = Image.new("RGB", (w, h), color=cls.COLOR_BG_DARK)
        draw = ImageDraw.Draw(img)

        # Draw subtle grid pattern background
        grid_step = 80
        for x in range(0, w, grid_step):
            draw.line([(x, 0), (x, h)], fill=(20, 29, 47), width=1)
        for y in range(0, h, grid_step):
            draw.line([(0, y), (w, y)], fill=(20, 29, 47), width=1)

        # Header Badge
        badge_text = f"EQUITY LAB AI  |  {symbol.upper() if symbol else 'INSTITUTIONAL RESEARCH'}"
        draw.rectangle([60, 40, 460, 85], fill=(30, 58, 102), outline=cls.COLOR_CYAN, width=2)
        draw.text((80, 52), badge_text, fill=cls.COLOR_CYAN)

        # Category Title
        draw.text((60, 110), title.upper(), fill=cls.COLOR_TEXT_MUTED)

        # Main Headline
        draw.text((60, 150), headline, fill=cls.COLOR_TEXT_WHITE)
        draw.line([(60, 210), (w - 60, 210)], fill=cls.COLOR_CYAN, width=3)

        if visual_type == "STOCK_CHART":
            cls._draw_candlestick_chart(draw, w, h, metric_highlights)
        elif visual_type == "VERDICT_BANNER":
            cls._draw_verdict_banner(draw, w, h, headline, metric_highlights)
        else:
            cls._draw_metric_cards(draw, w, h, bullet_points, metric_highlights)

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            img.save(output_path, "PNG")

        return img

    @classmethod
    def _draw_metric_cards(
        cls,
        draw: ImageDraw.ImageDraw,
        w: int,
        h: int,
        bullets: List[str],
        metrics: Dict[str, Any],
    ) -> None:
        """Draws structured bullet cards and metric pills."""
        # Left Panel: Key Highlights & Evidence
        left_w = int(w * 0.55)
        top_y = 250
        draw.rectangle([60, top_y, left_w, h - 80], fill=cls.COLOR_BG_CARD, outline=cls.COLOR_BORDER, width=2)
        draw.text((90, top_y + 25), "EVIDENCE & FACTUAL SIGNALS", fill=cls.COLOR_CYAN)

        y_offset = top_y + 80
        for i, b in enumerate(bullets[:4]):
            # Checkmark bullet indicator
            draw.rectangle([90, y_offset + 4, 106, y_offset + 20], fill=cls.COLOR_EMERALD)
            draw.text((125, y_offset), b, fill=cls.COLOR_TEXT_WHITE)
            y_offset += 65

        # Right Panel: Metric Grid
        right_x = left_w + 30
        right_w = w - 60
        draw.rectangle([right_x, top_y, right_w, h - 80], fill=cls.COLOR_BG_CARD, outline=cls.COLOR_BORDER, width=2)
        draw.text((right_x + 30, top_y + 25), "QUANTITATIVE METRICS", fill=cls.COLOR_CYAN)

        m_y = top_y + 80
        for k, v in list(metrics.items())[:4]:
            draw.rectangle([right_x + 30, m_y, right_w - 30, m_y + 80], fill=(20, 29, 47), outline=cls.COLOR_BORDER, width=1)
            draw.text((right_x + 50, m_y + 15), str(k).upper(), fill=cls.COLOR_TEXT_MUTED)
            draw.text((right_x + 50, m_y + 45), str(v), fill=cls.COLOR_EMERALD)
            m_y += 100

    @classmethod
    def _draw_candlestick_chart(
        cls,
        draw: ImageDraw.ImageDraw,
        w: int,
        h: int,
        metrics: Dict[str, Any],
    ) -> None:
        """Draws synthetic institutional candlestick chart with moving averages and invalidation line."""
        chart_x1, chart_y1 = 60, 250
        chart_x2, chart_y2 = w - 60, h - 80

        draw.rectangle([chart_x1, chart_y1, chart_x2, chart_y2], fill=cls.COLOR_BG_CARD, outline=cls.COLOR_BORDER, width=2)
        draw.text((chart_x1 + 30, chart_y1 + 20), "STRUCTURE & INVALIDATION PRICE GEOMETRY", fill=cls.COLOR_CYAN)

        # Draw 15 synthetic candles
        num_candles = 14
        step = (chart_x2 - chart_x1 - 100) // num_candles
        candle_w = step // 2
        base_p = 500

        # Synthetic upward price trend
        candle_data = [
            (480, 500, 470, 495), (492, 510, 485, 505), (500, 520, 495, 515),
            (512, 525, 505, 510), (508, 530, 502, 528), (525, 550, 520, 545),
            (540, 565, 535, 560), (555, 570, 550, 565), (560, 585, 555, 580),
            (575, 595, 570, 590), (588, 620, 580, 615), (610, 630, 605, 620),
            (618, 645, 612, 640), (635, 660, 630, 655),
        ]

        mid_y = chart_y1 + (chart_y2 - chart_y1) // 2

        for i, (op, hi, lo, cl) in enumerate(candle_data):
            cx = chart_x1 + 60 + i * step
            # Scale prices relative to chart height
            o_y = mid_y - (op - base_p)
            c_y = mid_y - (cl - base_p)
            h_y = mid_y - (hi - base_p)
            l_y = mid_y - (lo - base_p)

            is_bull = cl >= op
            color = cls.COLOR_EMERALD if is_bull else cls.COLOR_ROSE

            # Wick
            draw.line([(cx, h_y), (cx, l_y)], fill=color, width=2)
            # Body
            top = min(o_y, c_y)
            bot = max(o_y, c_y)
            draw.rectangle([cx - candle_w // 2, top, cx + candle_w // 2, bot], fill=color)

        # Structural Invalidation Line
        inval_str = str(metrics.get("Invalidation", "Support"))
        draw.line([(chart_x1 + 40, mid_y + 60), (chart_x2 - 40, mid_y + 60)], fill=cls.COLOR_ROSE, width=3)
        draw.rectangle([chart_x2 - 280, mid_y + 40, chart_x2 - 40, mid_y + 80], fill=cls.COLOR_ROSE)
        draw.text((chart_x2 - 270, mid_y + 50), f"INVALIDATION: {inval_str}", fill=cls.COLOR_TEXT_WHITE)

    @classmethod
    def _draw_verdict_banner(
        cls,
        draw: ImageDraw.ImageDraw,
        w: int,
        h: int,
        verdict: str,
        metrics: Dict[str, Any],
    ) -> None:
        """Renders final institutional verdict banner and return multiple gauge."""
        banner_x1, banner_y1 = 60, 250
        banner_x2, banner_y2 = w - 60, h - 80

        is_buy = "BUY" in verdict.upper() or "ACCUMULATE" in verdict.upper()
        v_color = cls.COLOR_EMERALD if is_buy else cls.COLOR_ROSE

        draw.rectangle([banner_x1, banner_y1, banner_x2, banner_y2], fill=cls.COLOR_BG_CARD, outline=v_color, width=4)

        # Huge Verdict Stamp
        draw.rectangle([banner_x1 + 40, banner_y1 + 40, banner_x2 - 40, banner_y1 + 180], fill=(20, 29, 47), outline=v_color, width=2)
        draw.text((banner_x1 + 80, banner_y1 + 90), verdict.upper(), fill=v_color)

        # Sub-stats
        mult = metrics.get("Multiple Ceiling", "2.5x")
        draw.text((banner_x1 + 80, banner_y1 + 240), f"REVERSE-DCF CEILING MULTIPLE: {mult}", fill=cls.COLOR_CYAN)
        draw.text((banner_x1 + 80, banner_y1 + 300), "DISCIPLINED RISK BUDGETING ENFORCED", fill=cls.COLOR_TEXT_MUTED)
        draw.text((banner_x1 + 80, banner_y1 + 350), "EQUITY LAB COGNITIVE DECISION COPILOT", fill=cls.COLOR_TEXT_MUTED)
