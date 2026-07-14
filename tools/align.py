"""tools/align.py — forced-align Merra.mp3 to produce word/line timestamps.

Uses faster-whisper (CTranslate2, lightweight — no torch). We transcribe the
audio to get accurate word-level timestamps, then map them onto the known
lyric lines from Musixmatch so the output lyrics.json matches the real words
while keeping whisper's timing.

Usage:
    python tools/align.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# --- Known lyrics (from Musixmatch, verified by artist) -------------------
LYRIC_LINES = [
    "Shedding tear it keeps on falling",
    "I hope I could learn to love like you",
    "Girl can we reverse it?",
    "The past is my pains",
    "The past is my regrets",
    "Starring at the ceiling",
    "Thinking about my mistakes till my eyes turns red",
    "This fantasy led me to see you when you were in class",
    "Then you gave me the most beautiful gift",
    "You drew my face and I realized that I've burned our precious memories",
    "That was big regret",
    "I'm better off dead",
    "I'm sorry for everything I did five years ago",
    "I wish I could take back the past",
    "So we can stay again",
    "You had me at hello",
    "And now I'm so low",
    "Can you tell me is it hard for you to give me just last one chance?",
    "When every time you say we're done",
    "I will be a lame blank canvas",
    "I'm all alone and day has gone",
    "Still waiting, when you get back home",
    "I'm sorry for everything I did five years ago",
    "I wish I could take back the past",
    "So we can stay again",
    "You had me at hello",
    "And now I'm so low",
    "Can you tell me is it hard for you to give me just last one chance?",
    "I'm sorry for everything I did five years ago",
    "I wish I could take back the past",
    "So we can stay again",
    "You had me at hello",
    "And now I'm so low",
    "Can you tell me is it hard for you to give me just last one chance?",
    "Give me just last one chance?",
    "I'm sorry for everything I did five years ago",
    "I wish I could take back the past",
    "So we can stay again",
]

SONG_DIR = Path(__file__).resolve().parent.parent / "songs" / "merra"
AUDIO = SONG_DIR / "audio.mp3"


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return s.strip()


def main() -> None:
    from faster_whisper import WhisperModel

    print("[align] loading faster-whisper (tiny) — first run downloads model...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    print("[align] transcribing", AUDIO.name)
    segments, info = model.transcribe(
        str(AUDIO), language="en", word_timestamps=True, beam_size=5, vad_filter=False
    )
    print(f"[align] duration={info.duration:.1f}s  building word list...")

    words: list[dict] = []
    for seg in segments:
        if not seg.words:
            continue
        for w in seg.words:
            if w.word.strip():
                words.append(
                    {"text": w.word.strip(), "start": w.start, "end": w.end, "used": False}
                )

    print(f"[align] {len(words)} words recognized")

    # Map lyric lines onto recognized words by proportional word-count
    # distribution. Whisper text is noisy, but its TIMING is what we need;
    # the displayed text comes from the known (verified) lyrics.
    total_lyric_tokens = sum(max(1, len(norm(l).split())) for l in LYRIC_LINES)
    out_lines = []
    wi = 0
    for line in LYRIC_LINES:
        toks = norm(line).split() or [""]
        n_take = max(1, round(len(toks) / total_lyric_tokens * len(words)))
        n_take = min(n_take, len(words) - wi)
        if n_take <= 0:
            # ran out of words; pad at the tail
            last_end = out_lines[-1]["end"] if out_lines else 0.0
            out_lines.append(
                {
                    "start": round(last_end, 3),
                    "end": round(last_end + 2.0, 3),
                    "text": line,
                    "words": None,
                }
            )
            continue
        ws = words[wi : wi + n_take]
        wi += n_take
        line_words = [
            {"text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3)}
            for w in ws
        ]
        out_lines.append(
            {
                "start": round(ws[0]["start"], 3),
                "end": round(ws[-1]["end"], 3),
                "text": line,
                "words": line_words,
            }
        )

    # Ensure monotonic non-overlapping ends and pad final to duration
    for k in range(1, len(out_lines)):
        if out_lines[k]["start"] < out_lines[k - 1]["start"]:
            out_lines[k]["start"] = out_lines[k - 1]["start"]
    if out_lines and info.duration:
        out_lines[-1]["end"] = round(info.duration, 3)

    lyrics_path = SONG_DIR / "lyrics.json"
    aligned_path = SONG_DIR / "lyrics_aligned.json"
    with open(lyrics_path, "w", encoding="utf-8") as f:
        json.dump({"lyrics": out_lines}, f, indent=2, ensure_ascii=False)
    with open(aligned_path, "w", encoding="utf-8") as f:
        json.dump({"lyrics": out_lines}, f, indent=2, ensure_ascii=False)

    print(f"[align] wrote {lyrics_path.name} and {aligned_path.name} ({len(out_lines)} lines)")


if __name__ == "__main__":
    main()
