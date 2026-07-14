"""Countdown 3-2-1-GO for the TUI (rich). No GUI dependencies."""
from __future__ import annotations

import time

from rich.console import Console
from rich.text import Text


def run_countdown(console: Console, seconds: int = 3, fps: int = 20) -> None:
    """Print a 3-2-1-GO countdown in the terminal, then clear."""
    delay = 1.0 / fps
    for n in range(seconds, 0, -1):
        console.clear()
        t = Text()
        t.append("\n\n")
        t.append(f"  {n}", style="bold white on red")
        t.append("\n\n  press PLAY on your speaker now...\n")
        console.print(t)
        time.sleep(1.0)
    console.clear()
    t = Text()
    t.append("\n\n  ")
    t.append("GO!", style="bold white on green")
    t.append("\n\n")
    console.print(t)
    time.sleep(0.7)
    console.clear()
