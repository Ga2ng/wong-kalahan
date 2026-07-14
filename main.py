"""Pixel Lyrics Engine — TUI CLI (rich + ascii-magic, PRD + DESIGN).

Usage:
    python main.py merra                  # windowed (manual/phone audio)
    python main.py merra --audio          # internal audio playback
    python main.py merra --layout kinetic # force a TUI layout
    python main.py merra --theme neon
    python main.py list                   # list discovered songs
    python main.py validate merra         # validate without rendering
    python main.py merra --duration 20    # render first N seconds (testing)
"""
from __future__ import annotations

import sys

import typer
from rich.console import Console

from engine.config_schema import load_lyrics
from engine.layout_registry import LayoutRegistry
from engine.theme_registry import ThemeRegistry
from engine.tui_renderer import render
from engine.song_registry import SongRegistry

app = typer.Typer(help="Pixel Lyrics Engine — realtime lyric + ASCII-art TUI")
console = Console()


def _discover() -> SongRegistry:
    return SongRegistry()


@app.command()
def run(
    song_id: str = typer.Argument(..., help="Song id (folder name under songs/)"),
    audio: bool = typer.Option(False, "--audio", help="Play audio internally"),
    layout: str = typer.Option(None, "--layout", help="Override layout name"),
    theme: str = typer.Option(None, "--theme", help="Override theme name"),
    fullscreen: bool = typer.Option(False, "--fullscreen", help="Showcase fullscreen"),
    nocountdown: bool = typer.Option(False, "--no-countdown", help="Skip 3-2-1-GO"),
    duration: float = typer.Option(None, "--duration", help="(unused) testing"),
    fps: int = typer.Option(None, "--fps", help="Override fps"),
    debug: bool = typer.Option(False, "--debug", help="Verbose logging"),
):
    reg = _discover()
    try:
        song = reg.load(song_id)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    if layout:
        song.config.layout = layout
    if theme:
        song.config.theme = theme

    for kind, reg_, name in (("layout", LayoutRegistry, song.config.layout),
                             ("theme", ThemeRegistry, song.config.theme)):
        try:
            reg_.get(name)
        except KeyError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1)

    console.print(f"[bold]▶ {song.config.title} — {song.config.artist}[/bold]  "
                  f"[dim](layout={song.config.layout}, theme={song.config.theme})[/dim]")
    backend = render(
        song,
        console,
        audio=audio,
        fps=fps,
        countdown=not nocountdown,
        duration=duration,
    )
    console.print(f"[dim]cover backend: {backend}[/dim]")


@app.command("list")
def list_songs():
    reg = _discover()
    songs = reg.list()
    if not songs:
        console.print("[yellow]No songs found in songs/[/yellow]")
        return
    console.print("[bold]Discovered songs:[/bold]")
    for s in songs:
        console.print(f"  • [cyan]{s.config.id}[/cyan]  {s.config.title} — {s.config.artist}  "
                      f"[dim](layout={s.config.layout})[/dim]")


@app.command("validate")
def validate(song_id: str = typer.Argument(...)):
    reg = _discover()
    try:
        song = reg.load(song_id)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    errs = []
    try:
        lyrics = load_lyrics(str(song.lyrics_path()))
    except Exception as e:  # noqa: BLE001
        errs.append(f"lyrics: {e}")
        lyrics = None
    if lyrics:
        if not lyrics.lyrics:
            errs.append("lyrics file has no lines")
        for i, ln in enumerate(lyrics.lyrics):
            if ln.end < ln.start:
                errs.append(f"line {i}: end < start")
    if errs:
        console.print(f"[red]✗ {song_id} invalid:[/red]")
        for e in errs:
            console.print(f"  - {e}")
        raise typer.Exit(1)
    console.print(f"[green]✓ {song_id} valid[/green]  ({len(lyrics.lyrics)} lines)")
    console.print(f"  layouts: {', '.join(LayoutRegistry.names())}")
    console.print(f"  themes:  {', '.join(ThemeRegistry.names())}")


if __name__ == "__main__":
    app()
