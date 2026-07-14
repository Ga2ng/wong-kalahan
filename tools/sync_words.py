"""Normalize lyrics_aligned.json: replace each line's `words` with the tokens
of that line's `text` (so words == text), leaving `start`/`end`/`text` intact
so the user can tune the timings by hand. Backup written alongside.
"""
import json, shutil, re
from pathlib import Path

p = Path("songs/merra/lyrics_aligned.json")
bak = p.with_suffix(".json.bak")
shutil.copy(p, bak)
print("[sync_words] backup ->", bak.name)

data = json.load(open(p, encoding="utf-8"))
for ln in data["lyrics"]:
    txt = ln.get("text", "")
    s = ln.get("start", 0.0)
    e = ln.get("end", s + 1.0)
    # split on whitespace, keep words only
    toks = [w for w in re.split(r"\s+", txt.strip()) if w]
    ln["words"] = [{"text": w, "start": s, "end": e} for w in toks]

json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"[sync_words] done: {len(data['lyrics'])} lines, words now match text.")
# show one sample
sample = data["lyrics"][0]
print("sample:", json.dumps(sample, ensure_ascii=False)[:200])
