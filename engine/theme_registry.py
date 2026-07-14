"""Theme registry (PRD #3). Maps name -> Theme class."""
from __future__ import annotations

from engine.base import BaseTheme


def _ensure_themes_imported() -> None:
    from engine import themes as _themes  # noqa: F401  (runs register())


class ThemeRegistry:
    _registry: dict = {}

    @classmethod
    def register(cls, name: str, theme_cls) -> None:
        cls._registry[name] = theme_cls

    @classmethod
    def get(cls, name: str):
        _ensure_themes_imported()
        if name == "default" and name not in cls._registry:
            name = "dark"
        if name not in cls._registry:
            valid = ", ".join(sorted(cls._registry.keys()))
            raise KeyError(f"Unknown theme '{name}'. Available: {valid}")
        return cls._registry[name]

    @classmethod
    def names(cls) -> list:
        _ensure_themes_imported()
        return sorted(cls._registry.keys())
