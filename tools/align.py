"""tools/align.py — forced-align a song's audio to produce word/line timestamps.

Uses faster-whisper (CTranslate2, lightweight — no torch) for accurate
WORD-LEVEL timing, then FORCED-ALIGNS the known lyric lines onto the
recognized words via a sliding-window token match. The displayed text stays
the verified lyrics; the TIMING comes straight from whisper's word clocks
(not a proportional guess), so lines track the audio instead of drifting.

PER-SONG and GENERIC: lyrics come from  songs/<SONG_ID>/lyrics.txt
(one line per row). Song id via  --song <id>  (defaults to "merra").

Usage:
    python tools/align.py --song <id>
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SONGS = ROOT / "songs"


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return s.strip()


def load_lyrics_plain(song_dir: Path) -> list[str]:
    p = song_dir / "lyrics.txt"
    if not p.exists():
        raise SystemExit(
            f"[align] ERROR: {p} not found.\n"
            f"         Create it with one lyric line per row, then re-run."
        )
    lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()]
    lines = [ln for ln in lines if ln]
    if not lines:
        raise SystemExit(f"[align] ERROR: {p} is empty.")
    return lines


def forced_align(lyric_lines: list[str], words: list[dict]) -> list[dict]:
    """Map each lyric line onto a contiguous run of whisper words using a
    sliding-window token match. Returns lyric lines with whisper's start/end.

    Falls back to a proportional slice when a line can't be matched (whisper
    heard something different), so output is always monotonic.
    """
    wt = [norm(w["text"]) for w in words]
    out: list[dict] = []
    wi = 0
    last_end = 0.0
    for line in lyric_lines:
        lt = [t for t in norm(line).split() if t]
        placed = None
        if lt:
            best_score = -1
            best = None
            # search a window ahead of the current word index
            for s in range(wi, min(len(wt), wi + 24)):
                for e in range(s + max(1, len(lt) - 3),
                               min(len(wt), s + len(lt) + 4) + 1):
                    seg = wt[s:e]
                    score = sum(1 for a, b in zip(lt, seg) if a == b)
                    # reward coverage of the line
                    score += 0.5 * min(len(lt), len(seg)) / max(1, len(lt))
                    if score > best_score:
                        best_score = score
                        best = (s, e)
            need = max(1, len(lt) // 2)
            if best and best_score >= need:
                s, e = best
                ws = words[s:e]
                placed = {
                    "start": round(ws[0]["start"], 3),
                    "end": round(ws[-1]["end"], 3),
                    "text": line,
                    "words": [
                        {"text": w["text"], "start": round(w["start"], 3),
                         "end": round(w["end"], 3)}
                        for w in ws
                    ],
                }
                wi = e
        if placed is None:
            # fallback: take the next few words proportionally / pad
            n_take = max(1, round(len(lt) / max(1, sum(len(norm(x).split()) for x in lyric_lines))
                                   * len(words))) if lt else 1
            n_take = min(n_take, len(words) - wi)
            if n_take > 0:
                ws = words[wi:wi + n_take]
                wi += n_take
                placed = {
                    "start": round(ws[0]["start"], 3),
                    "end": round(ws[-1]["end"], 3),
                    "text": line,
                    "words": [
                        {"text": w["text"], "start": round(w["start"], 3),
                         "end": round(w["end"], 3)}
                        for w in ws
                    ],
                }
            else:
                placed = {
                    "start": round(last_end, 3),
                    "end": round(last_end + 2.0, 3),
                    "text": line,
                    "words": None,
                }
        # keep monotonic non-overlapping
        if placed["start"] < last_end:
            placed["start"] = round(last_end, 3)
        last_end = placed["end"]
        out.append(placed)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Align a song's audio to its lyrics.")
    ap.add_argument("--song", default="merra", help="song id (folder under songs/)")
    ap.add_argument("--audio", default=None, help="audio filename (default audio.mp3)")
    args = ap.parse_args()

    song_dir = SONGS / args.song
    if not song_dir.is_dir():
        raise SystemExit(f"[align] ERROR: song folder not found: {song_dir}")

    audio_name = args.audio or "audio.mp3"
    audio = song_dir / audio_name
    if not audio.exists():
        raise SystemExit(f"[align] ERROR: audio not found: {audio}")

    lyric_lines = load_lyrics_plain(song_dir)
    print(f"[align] song={args.song}  lines={len(lyric_lines)}  audio={audio.name}")

    from faster_whisper import WhisperModel

    model_name = os.environ.get("ALIGN_MODEL", "tiny")
    print(f"[align] loading faster-whisper ({model_name}) — first run downloads model...")
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    print("[align] transcribing", audio.name)
    segments, info = model.transcribe(
        str(audio), language="en", word_timestamps=True, beam_size=5, vad_filter=False
    )
    print(f"[align] duration={info.duration:.1f}s  building word list...")

    words: list[dict] = []
    for seg in segments:
        if not seg.words:
            continue
        for w in seg.words:
            if w.word.strip():
                words.append(
                    {"text": w.word.strip(), "start": w.start, "end": w.end}
                )
    print(f"[align] {len(words)} words recognized")

    out_lines = forced_align(lyric_lines, words)

    # clamp to [0, duration] and keep end >= start (whisper tiny/base can overshoot)
    dur = info.duration or 0.0
    for ln in out_lines:
        ln["start"] = round(min(max(0.0, ln["start"]), dur), 3)
        ln["end"] = round(min(max(ln["start"], ln["end"]), dur), 3)
        if ln["end"] <= ln["start"]:
            ln["end"] = min(ln["start"] + 1.0, dur)
        if ln["words"]:
            for w in ln["words"]:
                w["start"] = min(max(0.0, w["start"]), dur)
                w["end"] = min(max(w["start"], w["end"]), dur)

    # pad final line to song duration
    if out_lines and dur:
        out_lines[-1]["end"] = round(dur, 3)

    lyrics_path = song_dir / "lyrics.json"
    aligned_path = song_dir / "lyrics_aligned.json"
    with open(lyrics_path, "w", encoding="utf-8") as f:
        json.dump({"lyrics": out_lines}, f, indent=2, ensure_ascii=False)
    with open(aligned_path, "w", encoding="utf-8") as f:
        json.dump({"lyrics": out_lines}, f, indent=2, ensure_ascii=False)

    print(f"[align] wrote {lyrics_path.name} and {aligned_path.name} ({len(out_lines)} lines)")


if __name__ == "__main__":
    main()
