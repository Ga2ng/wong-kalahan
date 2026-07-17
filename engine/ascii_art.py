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

# Per-session caches to avoid regenerating chafa every frame (prevents flicker).
_LYRIC_CACHE: dict = {}
_RAIN_CACHE: dict = {}


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


def pil_to_ascii(img: "Image.Image", width: int, work: int = 6) -> tuple[list[str], str]:
    """Render an in-memory PIL image to ANSI via chafa (no disk cache, so it
    is safe to call every frame for animations). Falls back to a Pillow
    truecolor converter if chafa is unavailable."""
    import tempfile, uuid
    exe = shutil.which("chafa") or shutil.which("chafa.exe")
    if not exe:
        candidate = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "chafa", "chafa.exe"))
        if os.path.exists(candidate):
            exe = candidate
    if exe:
        fd, tmp = tempfile.mkstemp(suffix=".png", prefix=f"chafa_{uuid.uuid4().hex[:8]}_")
        os.close(fd)
        try:
            img.save(tmp, format="PNG")
            cmd = [exe, tmp, "--colors", "full", "--symbols", "block",
                   "--format", "symbols", "--size", f"{width}x", "--work", str(work)]
            out = subprocess.run(cmd, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=30, check=False)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.replace("\r\n", "\n").splitlines(), "chafa"
        finally:
            try:
                os.remove(tmp)
            except OSError:  # noqa: BLE001
                pass
    # fallback: pillow truecolor
    w, h = img.size
    aspect = h / w
    out_h = max(1, int(width * aspect * 0.5))
    img = img.resize((width, out_h), Image.LANCZOS)
    px = img.load()
    lines = []
    for y in range(out_h):
        row = "".join(_ansi(*px[x, y]) + RAMP[int((sum(px[x, y]) / 3 / 255) * (len(RAMP) - 1))] for x in range(width))
        lines.append(row + "\x1b[0m")
    return lines, "pillow"


def left_with_rain(photo_path: str, width: int, t: float, seed: int = 7,
                   height: int | None = None) -> tuple[list[str], str]:
    """Load the left-section photo, draw animated rain ON TOP of it, return
    chafa ANSI. Rain is stamped as semi-transparent white streaks so it sits
    over the photo (not as a separate column). When `height` is given the
    photo is CONTAINED (aspect preserved, centred on a black card) so it is
    not stretched/distorted. Result is cached per 0.1s bucket to avoid
    per-frame chafa flicker/cost."""
    # throttle + cache: same photo/width at ~10fps buckets
    import time as _time
    bucket = int(t * 10)
    _rk = (photo_path, width, height, bucket)
    if _rk in _RAIN_CACHE:
        return _RAIN_CACHE[_rk]
    rng = __import__("random").Random(seed)
    img = Image.open(photo_path).convert("RGB")
    if height:
        # CONTAIN: keep aspect ratio, centre on a black card (no distortion)
        cw, ch = width * 8, height * 16
        canvas = Image.new("RGB", (cw, ch), (0, 0, 0))
        scale = min(cw / img.width, ch / img.height)
        nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
        img = img.resize((nw, nh), Image.LANCZOS)
        canvas.paste(img, ((cw - nw) // 2, (ch - nh) // 2))
        img = canvas
    else:
        aspect = img.height / img.width
        h = max(1, int(width * aspect * 0.5))
        img = img.resize((width * 2, h * 2), Image.LANCZOS)  # 2x for crisper rain
    w, hh = img.size
    overlay = Image.new("RGBA", (w, hh), (0, 0, 0, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(overlay)
    drops = []
    for c in range(0, w, 3):
        speed = rng.uniform(0.6, 1.8)
        offset = rng.uniform(0, hh)
        head = int((t * speed * 14 + offset)) % (hh + 20)
        drops.append((c, head, rng.randint(7, 18)))
    for c, head, length in drops:
        x = c
        # bright head + fading tail (white, semi-transparent)
        for k in range(length):
            y = head - k
            if 0 <= y < hh:
                alpha = int(200 * (1 - k / length)) + 30
                d.line([(x, y), (x, y)], fill=(235, 240, 255, alpha), width=1)
    img = img.convert("RGBA")
    img.alpha_composite(overlay)
    img = img.convert("RGB")
    # chafa at `width` from this (width*8 x height*16) canvas yields ~height rows
    res = pil_to_ascii(img, width, work=6)
    if len(_RAIN_CACHE) > 40:
        _RAIN_CACHE.clear()
    _RAIN_CACHE[_rk] = res
    return res


def big_lyric(text: str, width: int, height_chars: int, font_path: str | None = None,
              fg: tuple[int, int, int] = (233, 196, 106), size: int = 24) -> list[str]:
    """Render the active lyric in a BIG TTF font, centered, filling the
    column, and return chafa ANSI. This gives a large 'pixel font' look in
    the terminal center (not just bold rich text). Cached per (text,w,h)."""
    _ck = (text, width, height_chars, fg)
    if _ck in _LYRIC_CACHE:
        return _LYRIC_CACHE[_ck]
    from PIL import ImageDraw, ImageFont
    if not font_path or not os.path.exists(font_path):
        for f in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf",
                  r"C:\Windows\Fonts\impact.ttf"):
            if os.path.exists(f):
                font_path = f
                break
    # render at high res, scale to terminal aspect
    px_w = width * 8
    px_h = height_chars * 16
    img = Image.new("RGB", (px_w, px_h), (0, 0, 0))  # black bg (HP-record friendly)
    d = ImageDraw.Draw(img)
    # pick a font size that fits width with wrapping
    size = size
    font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
    # wrap words
    words = text.split()
    lines = []
    cur = ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if d.textlength(test, font=font) <= px_w - 20:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    # shrink if too many lines
    while len(lines) * (size + 6) > px_h and size > 16:
        size -= 4
        font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
        lines = []
        cur = ""
        for wd in words:
            test = (cur + " " + wd).strip()
            if d.textlength(test, font=font) <= px_w - 20:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
    total_h = len(lines) * (size + 6)
    y = max(4, (px_h - total_h) // 2)
    for ln in lines:
        tw = d.textlength(ln, font=font)
        x = max(6, (px_w - tw) // 2)
        d.text((x, y), ln, font=font, fill=fg)
        y += size + 6
    res = pil_to_ascii(img, width, work=9)[0]
    if len(_LYRIC_CACHE) > 60:
        _LYRIC_CACHE.clear()
    _LYRIC_CACHE[_ck] = res
    return res


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


# Cache for stretched (exact WxH) renders so static art isn't re-chafa'd.
_FIT_CACHE: dict = {}


def chafa_fit(path: str, width: int, height: int) -> tuple[list[str], str]:
    """Resize the image to EXACTLY fill a `width` x `height` block-art cell
    grid (stretch to the card), then render via chafa. This removes empty
    space inside a card. Cached per (path, w, h)."""
    _k = (path, width, height)
    if _k in _FIT_CACHE:
        return _FIT_CACHE[_k]
    img = Image.open(path).convert("RGB")
    # block glyphs are ~1:2 (w:h); scale to that grid so chafa yields height rows.
    img = img.resize((width * 8, height * 16), Image.LANCZOS)
    res = pil_to_ascii(img, width, work=6)
    if len(_FIT_CACHE) > 30:
        _FIT_CACHE.clear()
    _FIT_CACHE[_k] = res
    return res


# Per-session cache so the animated cover isn't re-chafa'd every frame.
_COVERFX_CACHE: dict = {}


def cover_with_fx(path: str, width: int, height: int, t: float,
                  seed: int = 11) -> tuple[list[str], str]:
    """Cover album with a subtle moving effect: a soft 'shine' band sweeps
    down and a gentle vignette 'breathes', so the still image feels alive
    (like a Spotify canvas). The photo is CONTAINED (aspect preserved,
    centred on a black card) so it is not stretched/distorted. Cached per
    0.15s bucket to avoid per-frame chafa cost/flicker."""
    bucket = int(t * 7)  # ~7fps sweep
    _k = (path, width, height, bucket)
    if _k in _COVERFX_CACHE:
        return _COVERFX_CACHE[_k]
    import random
    rng = random.Random(seed)
    img = Image.open(path).convert("RGB")
    # CONTAIN: keep aspect ratio, centre on a black card (no distortion)
    cw, ch = width * 8, height * 16
    canvas = Image.new("RGB", (cw, ch), (0, 0, 0))
    scale = min(cw / img.width, ch / img.height)
    nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
    img = img.resize((nw, nh), Image.LANCZOS)
    canvas.paste(img, ((cw - nw) // 2, (ch - nh) // 2))
    img = canvas
    w, hh = img.size
    overlay = Image.new("RGBA", (w, hh), (0, 0, 0, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(overlay)
    # sweeping shine band
    band_y = int((t * 0.25 * hh) % (hh + 60)) - 30
    for off in range(34):
        y = band_y + off
        if 0 <= y < hh:
            a = int(70 * (1 - off / 34))
            d.line([(0, y), (w, y)], fill=(255, 255, 255, a), width=1)
    # breathing vignette (darken edges slightly, pulsing)
    pulse = 0.5 + 0.5 * __import__("math").sin(t * 1.2)
    v = int(26 + 22 * pulse)
    d.rectangle([0, 0, w - 1, hh - 1], outline=(0, 0, 0, v), width=10)
    img = img.convert("RGBA")
    img.alpha_composite(overlay)
    img = img.convert("RGB")
    res = pil_to_ascii(img, width, work=6)
    if len(_COVERFX_CACHE) > 30:
        _COVERFX_CACHE.clear()
    _COVERFX_CACHE[_k] = res
    return res
