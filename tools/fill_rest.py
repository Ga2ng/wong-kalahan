"""Fill timing for lines AFTER the user's manual edit using a proportional
model: total remaining time (anchor -> song end) is split across the
remaining lines in proportion to their word counts (longer lines get more
time). Lines before the anchor are LEFT UNTOUCHED. The last line ends exactly
at the audio duration.

Usage:
  tools/fill_rest.py            # fill from default anchor (79.00)
  tools/fill_rest.py --from 162.09   # fill from line 33's end (user edited up to there)
"""
import json, re, argparse
from pathlib import Path

p = Path("songs/merra/lyrics_aligned.json")
bak = p.with_suffix(".json.bak3")
bak.write_bytes(p.read_bytes())
print("[fill] backup ->", bak.name)

ap = argparse.ArgumentParser()
ap.add_argument("--from", dest="anchor", type=float, default=79.00,
                help="anchor seconds: lines at/after this start get filled")
args = ap.parse_args()
ANCHOR_START = args.anchor

data = json.load(open(p, encoding="utf-8"))
lyrics = data["lyrics"]

song_end = max(ln["end"] for ln in lyrics)
print(f"[fill] song_end={song_end:.2f}, fill from {ANCHOR_START:.2f}")

start_idx = next(i for i, ln in enumerate(lyrics) if ln["start"] >= ANCHOR_START)
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
rest[-1]["end"] = round(song_end, 3)
for ln in rest:
    for wk in ln.get("words", []):
        wk["start"] = ln["start"]
        wk["end"] = ln["end"]

json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"[fill] filled lines {start_idx}..{len(lyrics)-1} ({len(rest)} lines)")
for i in range(start_idx - 2, len(lyrics)):
    print(f"  {i:2d} {lyrics[i]['start']:7.2f}-{lyrics[i]['end']:7.2f}  {lyrics[i]['text'][:40]}")
