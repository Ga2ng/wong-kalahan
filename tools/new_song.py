"""tools/new_song.py — scaffold a new song folder (generic, no hardcoding).

Usage:
    python tools/new_song.py <song_id> "Song Title" "Artist Name"

Creates  songs/<song_id>/  with config.json + empty lyrics.txt.
Drop your cover image as  cover.<ext>  and audio as  audio.<ext>  in that
folder, fill lyrics.txt (one line per row), then:
    python tools/align.py --song <song_id>     # optional, needs faster-whisper
or write lyrics.json manually. Then run:  start.bat <song_id>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SONGS = ROOT / "songs"


def main() -> None:
    ap = argparse.ArgumentParser(description="Scaffold a new song folder.")
    ap.add_argument("song_id", help="folder name, e.g. merra")
    ap.add_argument("title", help="display title")
    ap.add_argument("artist", help="artist name")
    ap.add_argument("--layout", default="poster")
    ap.add_argument("--theme", default="dark")
    args = ap.parse_args()

    folder = SONGS / args.song_id
    folder.mkdir(parents=True, exist_ok=True)

    cfg = {
        "id": args.song_id,
        "title": args.title,
        "artist": args.artist,
        "layout": args.layout,
        "theme": args.theme,
        "offset": 0.0,
        "fps": 30,
        "cover": "cover.jpeg",
        "background": None,
        "font": None,
        "lyrics": "lyrics.json",
        "lyrics_aligned": "lyrics_aligned.json",
        "background_mode": "static",
        "effects": ["glow"],
    }
    (folder / "config.json").write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lt = folder / "lyrics.txt"
    if not lt.exists():
        lt.write_text(
            "# one lyric line per row\n", encoding="utf-8"
        )
    print(f"[new_song] created {folder}")
    print(f"[new_song] next: put cover.jpeg + audio.mp3 here, fill lyrics.txt")
    print(f"[new_song] then:  python tools/align.py --song {args.song_id}")


if __name__ == "__main__":
    main()
