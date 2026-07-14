"""Layout registry (TUI rich variant). Maps name -> Layout class (PRD #3)."""
from __future__ import annotations

from engine.base import BaseLayout  # noqa: F401  (type compat)


def _ensure_layouts_imported() -> None:
    from engine import layouts as _layouts  # noqa: F401  (runs register())


class LayoutRegistry:
    _registry: dict = {}

    @classmethod
    def register(cls, name: str, layout_cls) -> None:
        cls._registry[name] = layout_cls

    @classmethod
    def get(cls, name: str):
        _ensure_layouts_imported()
        if name not in cls._registry:
            valid = ", ".join(sorted(cls._registry.keys()))
            raise KeyError(f"Unknown layout '{name}'. Available: {valid}")
        return cls._registry[name]

    @classmethod
    def names(cls) -> list:
        _ensure_layouts_imported()
        return sorted(cls._registry.keys())
