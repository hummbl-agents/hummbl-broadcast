"""Brand overlay compositor.

Real impl will shell out to ffmpeg. Stub uses PIL to verify the overlay logic
in tests without needing ffmpeg installed.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .models import BrandOverlay, Clip


class Composer:
    def __init__(self, overlay: BrandOverlay) -> None:
        self.overlay = overlay

    def compose_to_file(self, clip: Clip, output_path: Path) -> Path:
        """Stub: produce a single-frame placeholder PNG that visually represents
        the overlay placement. Real impl will run ffmpeg on the video file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if shutil.which("ffmpeg") is None and clip.local_path:
            # No ffmpeg available and we have a real clip — fail loud, don't fake it
            raise RuntimeError(
                "ffmpeg not found in PATH; required for real video composition. "
                "Install ffmpeg or run with --dry-run."
            )

        # Placeholder frame — proves the overlay coordinates are correct
        frame = Image.new("RGB", (1920, 1080), color=(20, 20, 24))
        draw = ImageDraw.Draw(frame)
        self._draw_overlay(draw, frame.size)
        frame.save(output_path)
        return output_path

    def _draw_overlay(self, draw: ImageDraw.ImageDraw, size: tuple[int, int]) -> None:
        margin = 32
        text = self.overlay.ai_disclosure
        watermark = self.overlay.watermark_text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except OSError:
            font = ImageFont.load_default()
            small = font

        if self.overlay.corner == "bottom-right":
            xy_text = (size[0] - 480, size[1] - 100)
            xy_wm = (size[0] - 480, size[1] - 60)
        elif self.overlay.corner == "bottom-left":
            xy_text = (margin, size[1] - 100)
            xy_wm = (margin, size[1] - 60)
        elif self.overlay.corner == "top-right":
            xy_text = (size[0] - 480, margin)
            xy_wm = (size[0] - 480, margin + 40)
        else:
            xy_text = (margin, margin)
            xy_wm = (margin, margin + 40)

        draw.rectangle(
            [xy_text, (xy_text[0] + 440, xy_text[1] + 64)],
            fill=(0, 0, 0),
        )
        draw.text((xy_text[0] + 12, xy_text[1] + 16), text, fill=(255, 255, 255), font=font)
        draw.text(xy_wm, watermark, fill=(200, 200, 200), font=small)
