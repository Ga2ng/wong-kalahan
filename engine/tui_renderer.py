"""TUI render loop: drives frames at target FPS inside the real terminal.

Reads the clock each frame -> sync engine -> resolved layout.render(ctx) ->
rich Live updates the terminal (no separate window). PRD #9 / #11.
"""
from __future__ import annotations

import shutil
import sys
import time

from rich.console import Console
from rich.live import Live
from rich.text import Text

from engine.ascii_art import cached_ascii
from engine.clock_source import AudioClock, ClockSource
from engine.config_schema import load_lyrics
from engine.layout_registry import LayoutRegistry
from engine.theme_registry import ThemeRegistry
from engine.layouts.base_layout import FrameContext
from engine.song_registry import Song
from engine.sync_engine import SyncEngine


def _enable_vt() -> None:
    """Enable Windows Virtual Terminal Processing so ANSI/truecolor escapes
    are honored in conhost/PowerShell (not just Windows Terminal)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        ENABLE_VT = 0x0004
        for handle in (kernel32.GetStdHandle(-11), kernel32.GetStdHandle(-12)):
            mode = ctypes.c_uint32(0)
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | ENABLE_VT)
    except Exception:  # noqa: BLE001
        pass


def render(
    song: Song,
    console: Console,
    *,
    audio: bool = False,
    fps: int | None = None,
    countdown: bool = True,
    duration: float | None = None,
    beat_provider=None,
) -> None:
    _enable_vt()
    cfg = song.config
    fps = fps or cfg.fps

    lyrics = load_lyrics(str(song.lyrics_path()))
    sync = SyncEngine(lyrics)
    LayoutCls = LayoutRegistry.get(cfg.layout)
    ThemeCls = ThemeRegistry.get(cfg.theme)
    theme = ThemeCls()

    cover = song.cover_path()
    art_small: list[str] = []
    art_full: list[str] = []
    backend = "pillow"
    if cover:
        try:
            # adapt cover width to the actual terminal so it never gets
            # truncated/clipped by rich Columns in a narrow conhost/PowerShell
            term_w_, _ = shutil.get_terminal_size((100, 40))
            cols = min(theme.ascii_columns, max(24, term_w_ - 42))
            art_small, backend = cached_ascii(str(cover), cols, str(song.folder / ".art_small.txt"))
            art_full, _ = cached_ascii(str(cover), cols * 2, str(song.folder / ".art_full.txt"))
        except Exception as e:  # noqa: BLE001
            console.print(f"[dim]cover fallback: {e}[/dim]")

    term_w, term_h = shutil.get_terminal_size((100, 40))

    clock = AudioClock(offset=cfg.offset) if audio else ClockSource(offset=cfg.offset)

    if audio:
        import pygame
        ap = song.audio_path()
        if ap:
            pygame.mixer.init()
            pygame.mixer.music.load(str(ap))
        else:
            console.print("[red]no audio file for --audio mode[/red]")

    if countdown:
        from engine.countdown_engine import run_countdown
        run_countdown(console, seconds=3, fps=fps)

    # audio + clock start together so visuals and sound are synced from t=0
    if audio:
        import pygame
        if song.audio_path() and pygame.mixer.get_init():
            pygame.mixer.music.play()
    clock.start()
    last = time.perf_counter()
    try:
        # No alternate screen (screen=False) -> safest for conhost/PowerShell
        # where the VT alternate buffer is unreliable. transient=False keeps
        # the final frame visible instead of wiping it on exit.
        with Live(console=console, screen=False, auto_refresh=False, transient=False) as live:
            while True:
                t = clock.time()
                if duration and t >= duration:
                    break
                if audio and not pygame.mixer.music.get_busy() and t > 1.0:
                    break

                idx = sync.active_line_index(t)
                line = sync.active_line(t)
                word_idx = sync.active_word_index(line, t) if line else -1
                beat = beat_provider(t) if beat_provider else 0.0

                ctx = FrameContext(
                    time=t, song_title=cfg.title, song_artist=cfg.artist,
                    active_line_text=line.text if line else None,
                    active_line_index=idx, total_lines=len(sync.lines),
                    active_word_index=word_idx, progress=sync.progress(t),
                    ascii_art=art_small, full_ascii=art_full,
                    width=term_w, height=term_h, theme=theme, beat=beat,
                )
                try:
                    renderable = LayoutCls().render(ctx)
                except Exception as e:  # noqa: BLE001
                    renderable = Text(f"[layout error] {e}", style="red")
                live.update(renderable, refresh=True)

                frame = 1
                now = time.perf_counter()
                sleep_for = (1.0 / fps) - (now - last)
                if sleep_for > 0:
                    time.sleep(sleep_for)
                last = time.perf_counter()
    except KeyboardInterrupt:
        pass
    finally:
        if audio:
            try:
                pygame.mixer.music.stop()
            except Exception:  # noqa: BLE001
                pass
    return backend
