"""tools/sync_manual.py — manual, 100% accurate lyric timing.

Whisper is unreliable for SUNG vocals (distortion/reverb make word
timestamps drift). This tool lets YOU mark each line as you HEAR it:
the audio plays, and you tap SPACE the instant a line STARTS being sung.
The recorded times come straight from the audio clock, so the result is
perfectly in sync with YOUR mp3.

Controls
  SPACE  mark the current line as starting NOW (accurate)
  ENTER  skip this line (estimate from average gap so far)
  R      restart the song from 0:00
  Q      quit without saving

Usage:
  .venv\Scripts\python.exe tools\sync_manual.py merra
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pygame


def main() -> None:
    song = sys.argv[1] if len(sys.argv) > 1 else "merra"
    base = Path("songs") / song
    aligned_path = base / "lyrics_aligned.json"
    audio_path = base / "audio.mp3"

    if not aligned_path.exists():
        print(f"[sync_manual] missing {aligned_path}")
        sys.exit(1)
    if not audio_path.exists():
        print(f"[sync_manual] missing {audio_path}")
        sys.exit(1)

    data = json.load(open(aligned_path, encoding="utf-8"))
    lines = [l["text"] for l in data["lyrics"]]

    # song duration (for the final line)
    try:
        from pydub import AudioSegment
        dur = len(AudioSegment.from_file(audio_path)) / 1000.0
    except Exception:
        dur = 0.0

    pygame.mixer.init()
    pygame.mixer.music.load(str(audio_path))

    import msvcrt

    print("=" * 60)
    print(" MANUAL LYRIC SYNC  —  %s" % song)
    print(" SPACE = mark line start NOW | ENTER = estimate | R = restart | Q = quit")
    print("=" * 60)
    time.sleep(1.5)

    starts: list[float] = []

    def play_from_start():
        pygame.mixer.music.play()
        time.sleep(0.05)

    play_from_start()
    for i, txt in enumerate(lines):
        print(f"\n[{i + 1}/{len(lines)}]  {txt}")
        while True:
            if msvcrt.kbhit():
                k = msvcrt.getch()
                if k == b" ":
                    starts.append(pygame.mixer.music.get_pos() / 1000.0)
                    print(f"        -> marked {starts[-1]:.2f}s")
                    break
                elif k in (b"\r", b"\n"):
                    if starts:
                        avg = (starts[-1] - starts[0]) / max(1, len(starts) - 1)
                        starts.append(starts[-1] + max(1.0, avg))
                    else:
                        starts.append(0.0)
                    print("        -> estimated")
                    break
                elif k in (b"r", b"R"):
                    starts.clear()
                    play_from_start()
                    print("        -> restarted")
                    # re-show from line 0
                    return main() if False else restart(lines, starts, play_from_start)
                elif k in (b"q", b"Q"):
                    pygame.mixer.music.stop()
                    print("quit, not saved")
                    sys.exit(0)
            time.sleep(0.01)

    out = []
    for i, txt in enumerate(lines):
        s = starts[i]
        e = starts[i + 1] if i + 1 < len(starts) else (dur or s + 3.0)
        out.append({"text": txt, "start": round(s, 3), "end": round(e, 3), "words": []})
    json.dump({"lyrics": out}, open(aligned_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    pygame.mixer.music.stop()
    print("\n[sync_manual] saved accurate timings to", aligned_path)


def restart(lines, starts, play_from_start):
    """Re-run the marking loop from the top (used by R)."""
    import msvcrt
    print("\n--- restart ---")
    for i, txt in enumerate(lines):
        print(f"\n[{i + 1}/{len(lines)}]  {txt}")
        while True:
            if msvcrt.kbhit():
                k = msvcrt.getch()
                if k == b" ":
                    starts.append(pygame.mixer.music.get_pos() / 1000.0)
                    print(f"        -> marked {starts[-1]:.2f}s")
                    break
                elif k in (b"\r", b"\n"):
                    if starts:
                        avg = (starts[-1] - starts[0]) / max(1, len(starts) - 1)
                        starts.append(starts[-1] + max(1.0, avg))
                    else:
                        starts.append(0.0)
                    print("        -> estimated")
                    break
                elif k in (b"q", b"Q"):
                    pygame.mixer.music.stop()
                    sys.exit(0)
            time.sleep(0.01)
    out = []
    for i, txt in enumerate(lines):
        s = starts[i]
        e = starts[i + 1] if i + 1 < len(starts) else s + 3.0
        out.append({"text": txt, "start": round(s, 3), "end": round(e, 3), "words": []})
    json.dump({"lyrics": out}, open(Path("songs") / sys.argv[1] / "lyrics_aligned.json",
              "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    pygame.mixer.music.stop()
    print("\n[sync_manual] saved accurate timings")


if __name__ == "__main__":
    main()
