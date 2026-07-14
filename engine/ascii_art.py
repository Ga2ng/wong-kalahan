"""Convert the album cover into colored ASCII art for the terminal TUI.

Primary backend: `chafa` (https://github.com/hpjansson/chafa) — the C image-to-
terminal renderer. It emits truecolor ANSI/Unicode art that looks great in
PowerShell / Windows Terminal. If chafa is not on PATH, we fall back to a
self-contained Pillow truecolor converter so the engine always runs.

Output is cached to a .txt keyed by backend so we don't re-decode the JPG
every frame.
"""
from __future__ import annotations

import os
import shutil
import subprocess

from PIL import Image

RAMP = " .:-=+*#%@"


def _ansi(r: int, g: int, b: int) -> str:
    return f"\x1b[38;2;{r};{g};{b}m"


def _pillow_ascii(path: str, width: int) -> list[str]:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    aspect = h / w
    out_h = max(1, int(width * aspect * 0.5))
    img = img.resize((width, out_h), Image.LANCZOS)
    px = img.load()
    lines: list[str] = []
    for y in range(out_h):
        row = ""
        for x in range(width):
            r, g, b = px[x, y]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            ch = RAMP[int((lum / 255) * (len(RAMP) - 1))]
            row += _ansi(r, g, b) + ch
        row += "\x1b[0m"
        lines.append(row)
    return lines


def _chafa_ascii(path: str, width: int) -> list[str] | None:
    # Search PATH first, then a bundled copy in tools/chafa (Windows standalone).
    exe = shutil.which("chafa") or shutil.which("chafa.exe")
    if not exe:
        candidate = os.path.join(os.path.dirname(__file__), "..", "tools", "chafa", "chafa.exe")
        candidate = os.path.abspath(candidate)
        if os.path.exists(candidate):
            exe = candidate
    if not exe:
        return None
    # chafa auto-detects truecolor in PowerShell/Windows Terminal.
    # --colors full = 24-bit truecolor (38;2;), best for modern terminals.
    # --symbols block = dense pixel look, --format symbols = ANSI text.
    cmd = [
        exe, path,
        "--colors", "full",
        "--symbols", "block",
        "--format", "symbols",
        "--size", f"{width}x",
        "--work", "6",
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             encoding="utf-8", errors="replace",
                             timeout=30, check=False)
    except Exception:  # noqa: BLE001
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    return out.stdout.replace("\r\n", "\n").splitlines()


def image_to_ascii(path: str, width: int = 70) -> tuple[list[str], str]:
    """Return (lines, backend_name). Backend is 'chafa' if available else 'pillow'."""
    lines = _chafa_ascii(path, width)
    if lines is not None:
        return lines, "chafa"
    return _pillow_ascii(path, width), "pillow"


def cached_ascii(path: str, width: int, cache_path: str) -> tuple[list[str], str]:
    # Cache key includes the backend so chafa vs pillow outputs don't collide.
    exe = shutil.which("chafa") or shutil.which("chafa.exe")
    backend_tag = "chafa" if exe else "pillow"
    real_cache = f"{cache_path}.{backend_tag}"
    if (
        os.path.exists(real_cache)
        and os.path.getmtime(real_cache) >= os.path.getmtime(path)
    ):
        with open(real_cache, "r", encoding="utf-8") as f:
            return f.read().splitlines(), backend_tag
    lines, backend = image_to_ascii(path, width=width)
    with open(real_cache, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return lines, backend
