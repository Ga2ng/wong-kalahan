"""Shared base classes for layouts, themes, and frame context.

Kept free of any package-internal side effects so it can be imported
anywhere without triggering circular imports.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from rich.console import RenderableType


@dataclass
class FrameContext:
    """Everything a layout needs to draw one frame."""

    time: float
    song_title: str
    song_artist: str
    active_line_text: Optional[str]
    active_line_index: int
    total_lines: int
    active_word_index: int
    progress: float  # 0..1
    ascii_art: list[str]  # colored lines of the cover
    full_ascii: list[str]  # larger/uncropped cover variant
    all_lines: list[str]  # every lyric line (for stacked/poster views)
    width: int
    height: int
    theme: "object"  # BaseTheme
    beat: float = 0.0  # 0..1 audio-reactive pulse
    cover_path: str = ""   # path to the source cover image (for re-render)
    song_id: str = ""     # song id (to load config for asset paths)


class BaseLayout:
    name = "base"

    def render(self, ctx: FrameContext) -> RenderableType:
        raise NotImplementedError


class BaseTheme:
    """Theme = plain class (NOT dataclass) so subclasses can override palette
    fields by simple class-attribute assignment. (A dataclass would ignore
    subclass field re-assignment and keep the base default.)"""

    name: str = "base"
    # Colorcode palette (DESIGN.md #3) as rich truecolor styles
    portal_red: str = "#E63946"
    fire_orange: str = "#F4A261"
    teal: str = "#2A9D8F"
    pastel_yellow: str = "#E9C46A"
    purple: str = "#8187B5"
    dark_blue: str = "#1D3557"
    # rich text styling
    active_style: str = "bold white"
    glow_style: str = "bold #E63946"
    accent_style: str = "bold #2EC4FF"
    dim_style: str = "dim #6B7A99"
    border_style: str = "bold #2A9D8F"
    ascii_columns: int = 64
    # terminal background tint (set via OSC 11 when this theme is active)
    bg: str = "#0B0E14"

    def color(self, name: str) -> str:
        return getattr(self, name, self.accent_style)
