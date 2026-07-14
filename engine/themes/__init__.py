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


class MerraTheme(BaseTheme):
    """Maroon / cream aesthetic — terminal bg tinted maroon, ala 'merra'."""
    name = "merra"
    bg: str = "#000000"            # pure black terminal background (OSC 11)
    portal_red = "#E63946"
    fire_orange = "#F4A261"
    teal = "#E9C46A"          # gold/cream accent on maroon
    pastel_yellow = "#F1E3C3"
    purple = "#C98B9B"        # dusty rose
    dark_blue = "#5C1A1A"
    active_style = "bold #F1E3C3"      # cream highlight
    glow_style = "bold #E63946"
    accent_style = "bold #E9C46A"      # gold
    dim_style = "dim #B98A8A"          # muted rose-dim
    border_style = "bold #E9C46A"      # gold borders


ThemeRegistry.register("default", DarkTheme)
ThemeRegistry.register("dark", DarkTheme)
ThemeRegistry.register("retro_green", RetroGreenTheme)
ThemeRegistry.register("neon", NeonTheme)
ThemeRegistry.register("merra", MerraTheme)
