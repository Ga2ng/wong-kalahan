"""Clock source abstraction.

Two implementations:
  - ManualClock: time advances from a wall clock (use when audio plays on a
    phone/speaker externally — PRD #4A). The `--offset` shifts the whole sync.
  - AudioClock: time is driven by pygame.mixer playback position, so lyrics
    stay locked to the actual audio (PRD #4B, `--audio`).

Renderers never know which source is active (PRD #9).
"""
from __future__ import annotations

import time


class ClockSource:
    def __init__(self, offset: float = 0.0):
        self.offset = offset
        self._running = False
        self._paused_at = 0.0
        self._accum = 0.0

    def start(self) -> None:
        self._running = True
        self._start = time.perf_counter()
        self._accum = 0.0

    def pause(self) -> None:
        if self._running:
            self._paused_at = self.raw_time()
            self._running = False

    def resume(self) -> None:
        if not self._running:
            self._start = time.perf_counter() - self._paused_at
            self._running = True

    def raw_time(self) -> float:
        if self._running:
            return time.perf_counter() - self._start
        return self._paused_at

    def time(self) -> float:
        """Effective time with offset applied (clock read-time, PRD #8)."""
        return self.raw_time() + self.offset

    @property
    def running(self) -> bool:
        return self._running


class AudioClock(ClockSource):
    """Clock driven by a wall clock started at the exact moment playback
    begins, NOT pygame's get_pos() (which drifts/lags). This keeps lyrics
    locked to the audio without accumulating error."""

    def __init__(self, offset: float = 0.0):
        super().__init__(offset=offset)
        import pygame

        self._pg = pygame
        self._audio_start = 0.0

    def start(self) -> None:
        # called right after pygame.mixer.music.play()
        super().start()
        self._audio_start = time.perf_counter()

    def raw_time(self) -> float:
        # wall-clock since playback started == real audio position
        return time.perf_counter() - self._audio_start
