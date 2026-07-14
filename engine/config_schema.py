"""Pydantic schemas for song config.json + lyrics.json.

Fail-fast validation with readable errors (PRD #14).
"""
from __future__ import annotations

from typing import List, Optional

import orjson
import pydantic


class Word(pydantic.BaseModel):
    text: str
    start: float
    end: float


class Line(pydantic.BaseModel):
    start: float
    end: float
    text: str
    words: Optional[List[Word]] = None


class LyricsFile(pydantic.BaseModel):
    lyrics: List[Line]

    def sorted_lines(self) -> List[Line]:
        return sorted(self.lyrics, key=lambda l: l.start)


class SongConfig(pydantic.BaseModel):
    # Required
    id: str
    title: str
    layout: str
    lyrics: str

    # Optional with sensible fallbacks
    artist: str = "Unknown Artist"
    artist_label: Optional[str] = None
    album: Optional[str] = None
    about: Optional[str] = None
    monthly_listeners: Optional[str] = None
    theme: str = "default"
    offset: float = 0.0
    fps: int = 30
    cover: Optional[str] = None
    left_section: Optional[str] = None   # image for the left/rain column
    about_image: Optional[str] = None     # image for the about panel
    background: Optional[str] = None
    font: Optional[str] = None
    background_mode: str = "static"
    effects: List[str] = pydantic.Field(default_factory=list)

    # Secondary lyrics file (for aligned timestamps produced by tools/align.py)
    lyrics_aligned: Optional[str] = None

    @pydantic.validator("fps")
    def fps_range(cls, v):
        if v < 1 or v > 120:
            raise ValueError("fps must be between 1 and 120")
        return v


def load_config(path: str) -> SongConfig:
    with open(path, "rb") as f:
        data = orjson.loads(f.read())
    return SongConfig(**data)


def load_lyrics(path: str) -> LyricsFile:
    with open(path, "rb") as f:
        data = orjson.loads(f.read())
    return LyricsFile(**data)


def save_lyrics(path: str, lyrics: LyricsFile) -> None:
    with open(path, "wb") as f:
        f.write(orjson.dumps(lyrics.model_dump(), option=orjson.OPT_INDENT_2))
