"""SongRegistry: auto-discovers every folder under songs/ (PRD #3, #10)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import orjson

from engine.config_schema import SongConfig, load_config, load_lyrics

SONGS_DIR = Path(__file__).resolve().parent.parent / "songs"


@dataclass
class Song:
    config: SongConfig
    folder: Path

    def config_path(self) -> Path:
        return self.folder / "config.json"

    def lyrics_path(self) -> Path:
        # Prefer aligned lyrics if present, else the declared lyrics file
        if self.config.lyrics_aligned:
            p = self.folder / self.config.lyrics_aligned
            if p.exists():
                return p
        return self.folder / self.config.lyrics

    def cover_path(self) -> Path | None:
        if self.config.cover:
            return self.folder / self.config.cover
        return None

    def audio_path(self) -> Path | None:
        for name in ("audio.mp3", "audio.wav", "audio.ogg", self.config.id + ".mp3"):
            p = self.folder / name
            if p.exists():
                return p
        return None


class SongRegistry:
    def __init__(self, songs_dir: Path = SONGS_DIR):
        self.songs_dir = songs_dir
        self._songs: dict[str, Song] = {}
        self.discover()

    def discover(self) -> None:
        if not self.songs_dir.exists():
            return
        for folder in sorted(self.songs_dir.iterdir()):
            if not folder.is_dir():
                continue
            cfg = folder / "config.json"
            if not cfg.exists():
                continue
            try:
                config = load_config(str(cfg))
            except Exception as e:  # noqa: BLE001
                print(f"[warn] skipping {folder.name}: {e}")
                continue
            self._songs[config.id] = Song(config=config, folder=folder)

    def list(self) -> list[Song]:
        return list(self._songs.values())

    def load(self, song_id: str) -> Song:
        if song_id not in self._songs:
            valid = ", ".join(self._songs.keys()) or "(none)"
            raise KeyError(f"Unknown song '{song_id}'. Available: {valid}")
        return self._songs[song_id]
