"""Split one lyric line into two at a given cut substring, redistributing the
timing proportionally (by text length) and regenerating the `words` tokens.

Usage:
    .venv\Scripts\python.exe tools\split_line.py --song merra \
        --text "Can you tell me is it hard for you to give me just last one chance?" \
        --cut "to give me just last one"

Backs up the JSON first (lyrics_aligned.json.bakN).
"""
from __future__ import annotations
import argparse, json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--song", default="merra")
    ap.add_argument("--text", required=True, help="exact current line text")
    ap.add_argument("--cut", required=True, help="substring where the 2nd line begins")
    args = ap.parse_args()

    p = ROOT / "songs" / args.song / "lyrics_aligned.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    ly = data["lyrics"]

    for i, l in enumerate(ly):
        if l["text"] == args.text:
            t = l["text"]
            pos = t.find(args.cut)
            if pos < 0:
                print(f"[err] --cut not found in line {i}"); sys.exit(1)
            a = t[:pos].strip()
            b = t[pos:].strip()
            s, e = l["start"], l["end"]
            dur = e - s
            r = len(a) / (len(a) + len(b)) if (a or b) else 0.5
            mid = round(s + dur * r, 3)
            ly[i] = {
                "text": a, "start": s, "end": mid,
                "words": [{"text": w, "start": s, "end": mid} for w in a.split()],
            }
            ly.insert(i + 1, {
                "text": b, "start": mid, "end": e,
                "words": [{"text": w, "start": mid, "end": e} for w in b.split()],
            })
            # backup
            n = 1
            while (p.parent / f"lyrics_aligned.json.bak{n}").exists():
                n += 1
            shutil.copy(p, p.parent / f"lyrics_aligned.json.bak{n}")
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[ok] split line {i}:")
            print(f"     '{a}'   ({s} -> {mid})")
            print(f"     '{b}'   ({mid} -> {e})")
            return
    print(f"[err] line with exact text not found:\n  {args.text!r}")


if __name__ == "__main__":
    main()
