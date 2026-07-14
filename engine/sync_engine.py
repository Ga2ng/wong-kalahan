"""Sync engine: binary-search the active lyric line (and word) for a frame.

Keeps lines sorted by start; O(log n) lookup regardless of song length (PRD #7).
"""
from __future__ import annotations

import bisect
from typing import List, Optional

from engine.config_schema import Line, LyricsFile


class SyncEngine:
    def __init__(self, lyrics: LyricsFile):
        self.lines: List[Line] = lyrics.sorted_lines()
        self._starts = [l.start for l in self.lines]
        self._ends = [l.end for l in self.lines]

    def active_line_index(self, t: float) -> int:
        """Return index of the line active at time t, or -1 if none."""
        if not self.lines:
            return -1
        # largest index with start <= t
        i = bisect.bisect_right(self._starts, t) - 1
        if i < 0:
            return -1
        # include a small tail so the line lingers slightly past its end
        if t > self._ends[i] + 0.6:
            return -1
        return i

    def active_line(self, t: float) -> Optional[Line]:
        i = self.active_line_index(t)
        return self.lines[i] if i >= 0 else None

    def active_word_index(self, line: Line, t: float) -> int:
        if not line.words:
            return -1
        for idx, w in enumerate(line.words):
            if w.start <= t <= w.end:
                return idx
        return -1

    def progress(self, t: float) -> float:
        """0..1 progress across the whole song."""
        if not self.lines:
            return 0.0
        last = self._ends[-1]
        if last <= 0:
            return 0.0
        return max(0.0, min(1.0, t / last))
