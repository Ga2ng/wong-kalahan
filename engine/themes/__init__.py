"""Theme registry + concrete themes (TUI rich variant).

Themes self-register on import (PRD #3).
"""
from __future__ import annotations

from engine.base import BaseTheme
from engine.theme_registry import ThemeRegistry


class DarkTheme(BaseTheme):
    name = "dark"
    active_style = "bold white"
    glow_style = "bold #E63946"
    accent_style = "bold #2EC4FF"
    dim_style = "dim #6B7A99"
    border_style = "bold #2A9D8F"


class RetroGreenTheme(BaseTheme):
    name = "retro_green"
    active_style = "bold #00FF66"
    glow_style = "bold #00FF66"
    accent_style = "bold #7CFFB0"
    dim_style = "dim #2E6B47"
    border_style = "bold #00FF66"


class NeonTheme(BaseTheme):
    name = "neon"
    active_style = "bold #FF2EC4"
    glow_style = "bold #FF2EC4"
    accent_style = "bold #2EC4FF"
    dim_style = "dim #7A4D8A"
    border_style = "bold #FF2EC4"


ThemeRegistry.register("default", DarkTheme)
ThemeRegistry.register("dark", DarkTheme)
ThemeRegistry.register("retro_green", RetroGreenTheme)
ThemeRegistry.register("neon", NeonTheme)
