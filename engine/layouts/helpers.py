"""Shared helpers for TUI layouts."""
from __future__ import annotations

from rich.console import Group
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


def volume_bars(level: float, width: int = 12, on: str = "█", off: str = "░") -> str:
    """A fake playback/volume visualizer like [██████░░░░]."""
    n = int(level * width)
    return on * n + off * (width - n)


_WAVE = "▁▂▃▄▅▆▇█"


def waveform(level: float, width: int = 24) -> str:
    """A smooth sine-ish waveform bar made of block characters."""
    import math
    out = []
    for i in range(width):
        x = (i / max(1, width)) * math.pi * 2 + level * 6.0
        amp = (math.sin(x) + 1) / 2  # 0..1
        idx = min(len(_WAVE) - 1, int(amp * (len(_WAVE) - 1)))
        out.append(_WAVE[idx])
    return "".join(out)


import random


def rain(width: int, height: int, t: float, seed: int = 7) -> list[str]:
    """Synthetic falling-rain animation (no GIF file needed).

    Returns `height` rows of `width` characters. Each column has a streak
    that falls over time, giving a 'vertical GIF rain' look in the terminal.
    Deterministic per (column, t) so it animates smoothly frame to frame.
    """
    rng = random.Random(seed)
    drops = []
    for c in range(width):
        speed = rng.uniform(0.6, 1.6)
        offset = rng.uniform(0, height)
        head = int((t * speed * 6 + offset)) % (height + 6)
        drops.append((c, head, speed))
    rows = []
    for r in range(height):
        line = []
        for c, head, speed in drops:
            d = head - r
            if 0 <= d <= 4:
                # bright head, fading tail
                chars = "│'·."
                line.append(chars[max(0, 3 - d)] if d < 4 else "│")
            else:
                line.append(" ")
        rows.append("".join(line))
    return rows



def stacked_lyrics(ctx, window: int = 12, show_done: bool = True) -> Group:
    """Render ALL lyric lines up to the active one, stacked (poster style).

    - lines already sung stay visible (dimmed) instead of disappearing
    - the active line is highlighted bright
    - upcoming lines are faintly shown below for context
    Past lines accumulate so the screen reads like a band poster / karaoke
    roll, not a single swapping line.
    """
    idx = ctx.active_line_index
    all_lines = getattr(ctx, "all_lines", None) or [ctx.active_line_text or ""]
    if idx < 0:
        idx = 0
    start = max(0, idx - window + 1)
    end = min(len(all_lines), idx + window)
    rows = []
    for i in range(start, end):
        text = all_lines[i]
        if i < idx:
            style = ctx.theme.dim_style
            prefix = "  "
        elif i == idx:
            style = f"bold {ctx.theme.portal_red}"
            prefix = "▸ "
        else:
            style = ctx.theme.dim_style
            prefix = "  "
        rows.append(Text(prefix + text, style=style))
    return Group(*rows)


def spotify_lyric(all_lines: list[str], idx: int, height: int, width: int,
                  active_style: str, near_style: str, dim_style: str,
                  word_index: int = -1, sung_style: str = "") -> Group:
    """Spotify-style centered lyric stack.

    The ACTIVE line sits in the vertical CENTER of the card; lines above and
    below scroll past it (teleprompter). The active line is bright, its
    immediate neighbours are warm-dim, the rest fade out. Long lines WRAP
    (overflow='fold') so nothing is clipped sideways. Uses the normal
    terminal font.

    Karaoke coloring: on the active line, words already sung use `sung_style`,
    the word currently being sung uses `active_style` (brightest), and the
    not-yet-sung remainder uses `dim_style`. `word_index` is the index of the
    word currently being sung (-1 = none highlighted).
    """
    if idx < 0:
        idx = 0
    half = height // 2
    lo = idx - half
    hi = idx + half + (height % 2)
    rows = []
    for i in range(lo, hi + 1):
        if 0 <= i < len(all_lines):
            text = all_lines[i]
            if i == idx:
                if word_index >= 0 and sung_style:
                    # word-level karaoke highlight on the active line
                    words = text.split()
                    t = Text(overflow="fold")
                    for wi2, w in enumerate(words):
                        if wi2 < word_index:
                            st = sung_style
                        elif wi2 == word_index:
                            st = active_style
                        else:
                            st = dim_style
                        t.append(w, style=st)
                        if wi2 < len(words) - 1:
                            t.append(" ")
                    rows.append(t)
                else:
                    rows.append(Text(text, style=active_style, overflow="fold"))
            elif abs(i - idx) == 1:
                rows.append(Text(text, style=near_style, overflow="fold"))
            else:
                rows.append(Text(text, style=dim_style, overflow="fold"))
        else:
            rows.append(Text(""))
    return Group(*rows)
