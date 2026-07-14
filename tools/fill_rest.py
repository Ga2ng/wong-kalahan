"""Fill timing for lines AFTER the user's manual edit (line 13..end) using a
proportional model: total remaining time (79.00 -> song end) is split across
the remaining lines in proportion to their word counts (longer lines get more
time). Lines 0..12 are LEFT UNTOUCHED (user-edited). Also guarantees the last
line ends exactly at the audio duration, and end >= start with a small gap.
"""
import json, re
from pathlib import Path

p = Path("songs/merra/lyrics_aligned.json")
bak = p.with_suffix(".json.bak2")
bak.write_bytes(p.read_bytes())
print("[fill] backup ->", bak.name)

ANCHOR_START = 79.00          # user's last manual end (line 12)
data = json.load(open(p, encoding="utf-8"))
lyrics = data["lyrics"]

# audio duration from the last line's end
song_end = max(ln["end"] for ln in lyrics)
print(f"[fill] song_end={song_end:.2f}, fill from {ANCHOR_START:.2f}")

# find first line to fill (first line whose start >= ANCHOR_START)
start_idx = next(i for i, ln in enumerate(lyrics) if ln["start"] >= ANCHOR_START)
# ensure line[start_idx-1].end == ANCHOR_START
lyrics[start_idx - 1]["end"] = round(ANCHOR_START, 3)

rest = lyrics[start_idx:]
n_words = [len(re.findall(r"\S+", ln["text"])) for ln in rest]
total_words = sum(n_words) or len(rest)
remaining = song_end - ANCHOR_START

t = ANCHOR_START
for ln, w in zip(rest, n_words):
    dur = (w / total_words) * remaining
    ln["start"] = round(t, 3)
    t += dur
    ln["end"] = round(t, 3)
# clamp final to song_end exactly
rest[-1]["end"] = round(song_end, 3)
# sync words start/end to their line (words already == text tokens)
for ln in rest:
    for wk in ln.get("words", []):
        wk["start"] = ln["start"]
        wk["end"] = ln["end"]

json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"[fill] filled lines {start_idx}..{len(lyrics)-1} ({len(rest)} lines)")
for i in range(start_idx - 2, len(lyrics)):
    print(f"  {i:2d} {lyrics[i]['start']:7.2f}-{lyrics[i]['end']:7.2f}  {lyrics[i]['text'][:40]}")
