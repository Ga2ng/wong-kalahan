"""Shared helpers for TUI layouts."""
from __future__ import annotations

from rich.text import Text


def progress_bar(progress: float, width: int = 30, fill: str = "█", empty: str = "·") -> str:
    n = int(progress * width)
    return fill * n + empty * (width - n)


def center(text: str, width: int) -> str:
    if len(text) >= width:
        return text
    return " " * ((width - len(text)) // 2) + text


def num_lines(s: str) -> int:
    return len(s.splitlines() or [""])
