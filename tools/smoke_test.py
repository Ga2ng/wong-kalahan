"""Smoke test: every TUI layout x theme renders to a buffer without crashing."""
from __future__ import annotations

from io import StringIO

from rich.console import Console

from engine.ascii_art import cached_ascii
from engine.config_schema import load_lyrics
from engine.layout_registry import LayoutRegistry
from engine.theme_registry import ThemeRegistry
from engine.layouts.base_layout import FrameContext
from engine.song_registry import SongRegistry
from engine.sync_engine import SyncEngine


def main() -> None:
    reg = SongRegistry()
    song = reg.load("merra")
    lyrics = load_lyrics(str(song.lyrics_path()))
    sync = SyncEngine(lyrics)
    cover = song.cover_path()
    small, _ = cached_ascii(str(cover), 64, str(song.folder / ".art_small.txt"))
    full, _ = cached_ascii(str(cover), 128, str(song.folder / ".art_full.txt"))
    assert small and full, "ascii art empty"

    test_t = sync.lines[2].start + 0.5
    idx = sync.active_line_index(test_t)
    line = sync.active_line(test_t)
    print(f"[smoke] t={test_t:.2f} active={line.text!r}")

    fails = []
    for lname in LayoutRegistry.names():
        for tname in ThemeRegistry.names():
            ThemeCls = ThemeRegistry.get(tname)
            theme = ThemeCls()
            ctx = FrameContext(time=test_t, song_title=song.config.title, song_artist=song.config.artist,
                active_line_text=line.text, active_line_index=idx, total_lines=len(sync.lines),
                active_word_index=-1, progress=sync.progress(test_t),
                ascii_art=small, full_ascii=full, width=100, height=40, theme=theme, beat=0.5)
            try:
                buf = StringIO()
                c = Console(file=buf, width=160, height=44, color_system="truecolor")
                c.print(LayoutRegistry.get(lname)().render(ctx))
                if not buf.getvalue().strip():
                    fails.append((lname, tname))
            except Exception as e:  # noqa: BLE001
                fails.append((lname, tname, repr(e)))
                print("FAIL", lname, tname, e)
    if fails:
        print(f"{len(fails)} FAILURES")
        raise SystemExit(1)
    print(f"[smoke] OK — {len(LayoutRegistry.names())} layouts x {len(ThemeRegistry.names())} themes")


if __name__ == "__main__":
    main()
