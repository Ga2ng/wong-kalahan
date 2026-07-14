"""10 TUI layouts (DEIGN.md) rendered as ANSI text in the terminal.

The cover is pre-converted to colored ASCII (ascii-magic) and passed in
ctx.ascii_art / ctx.full_ascii as lists of ANSI strings. Each layout composes
that ASCII art with the live lyric using rich Panels / Columns / Text.
"""
from __future__ import annotations

from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from engine.layout_registry import LayoutRegistry
from engine.layouts.base_layout import BaseLayout, FrameContext
from engine.layouts.helpers import center, progress_bar, volume_bars, waveform, rain, stacked_lyrics


def _cover(ctx: FrameContext, which: str = "ascii_art") -> Text:
    lines = getattr(ctx, which, []) or [""]
    # chafa output is raw ANSI (truecolor escapes) -> parse it, don't treat as
    # plain text, or rich collapses it to one mangled line.
    t = Text.from_ansi("\n".join(lines))
    t.no_wrap = True
    return t


def _ansi(lines, dim: bool = False) -> Text:
    """Parse chafa's raw-ANSI lines into a rich Text (colors preserved)."""
    s = "\n".join(lines)
    if dim:
        s = "\x1b[2m" + s + "\x1b[0m"
    t = Text.from_ansi(s)
    t.no_wrap = True
    return t


def _fit(lines: list, h: int, fill: str = " ") -> list:
    """Truncate or pad a list of render-lines to exactly `h` rows so columns
    share a uniform height (no ragged edges)."""
    lines = list(lines)
    if len(lines) >= h:
        return lines[:h]
    return lines + [fill] * (h - len(lines))


def _lyric(ctx: FrameContext, text: str | None = None) -> Text:
    t = text if text is not None else (ctx.active_line_text or "")
    r = Text()
    r.append(t, style=ctx.theme.active_style)
    return r


# 1. Split Screen — cover kiri, lyric kanan
class LayoutSplit(BaseLayout):
    name = "split"

    def render(self, ctx: FrameContext):
        left = Panel(_cover(ctx), border_style=ctx.theme.border_style, title="COLORCODE")
        right = Group(
            Text(ctx.song_title, style=f"bold {ctx.theme.portal_red}"),
            Text(ctx.song_artist, style=ctx.theme.dim_style),
            Text(""),
            _lyric(ctx),
            Text(""),
            Text(progress_bar(ctx.progress, 30), style=ctx.theme.accent_style),
        )
        return Columns([left, right], padding=(2, 4))


# 2. Watermark — cover redup full bg, lyric besar tengah
class LayoutWatermark(BaseLayout):
    name = "watermark"

    def render(self, ctx: FrameContext):
        # chafa lines are raw ANSI -> parse with from_ansi (dim whole block)
        dim = Text.from_ansi("\n".join("\x1b[2m" + l + "\x1b[0m" for l in ctx.full_ascii))
        dim.no_wrap = True
        big = Text(center(ctx.active_line_text or "", ctx.width), style=f"bold {ctx.theme.fire_orange}")
        return Group(dim, Text(""), big)


# 3. Border Grid — 3 panel
class LayoutGrid(BaseLayout):
    name = "grid"

    def render(self, ctx: FrameContext):
        tl = Panel(Text("COLORCODE", style=f"bold {ctx.theme.portal_red}"),
                   border_style=ctx.theme.purple, title="ALBUM")
        bl = Panel(_cover(ctx)[len(ctx.ascii_art) // 2:], border_style=ctx.theme.teal, title="PORTAL")
        lyric = Panel(Group(Text(""), _lyric(ctx), Text(""),
                             Text(progress_bar(ctx.progress, 28), style=ctx.theme.accent_style)),
                      border_style=ctx.theme.fire_orange, title="LYRIC")
        return Columns([Group(tl, bl), lyric], padding=(2, 4))


# 4. Portal — cover tengah, lyric naik-turun (beat)
class LayoutPortal(BaseLayout):
    name = "portal"

    def render(self, ctx: FrameContext):
        mid = len(ctx.full_ascii) // 2
        portal = ctx.full_ascii[mid - 8: mid + 8] if len(ctx.full_ascii) > 16 else ctx.full_ascii
        portal_t = _ansi(portal)
        off = int((ctx.beat - 0.5) * 4)
        lyric = Text("\n" * (2 + max(0, off)) + center(ctx.active_line_text or "", ctx.width),
                     style=f"bold {ctx.theme.portal_red}")
        return Group(portal_t, lyric)


# 5. Focus — zoom cover kiri, lyric typewriter kanan
class LayoutFocus(BaseLayout):
    name = "focus"

    def render(self, ctx: FrameContext):
        import time
        zoom = ctx.ascii_art[len(ctx.ascii_art) * 3 // 4:]
        art = _ansi(["  " + l for l in zoom[:16]])
        raw = ctx.active_line_text or ""
        n = int((time.time() * 18) % (len(raw) + 1))
        typed = raw[:n] + "▌"
        lyric = Group(Text(ctx.song_title, style=f"bold {ctx.theme.portal_red}"), Text(""),
                      Text(typed, style=ctx.theme.active_style))
        return Columns([art, lyric], padding=(2, 4))


# 6. Matrix — cover kiri, lyric jatuh kanan
class LayoutMatrix(BaseLayout):
    name = "matrix"

    def render(self, ctx: FrameContext):
        import random
        left = _ansi(ctx.ascii_art[:14])
        lyric = ctx.active_line_text or ""
        height = max(16, ctx.height - 6)
        pos = int(ctx.progress * height) % (len(lyric) + 4)
        rows = []
        for i in range(height):
            if i == pos:
                rows.append(Text(lyric, style="bold white"))
            elif 0 <= i - pos < len(lyric):
                rows.append(Text(" " * (i - pos) + lyric[i - pos], style=f"bold {ctx.theme.teal}"))
            else:
                rows.append(Text(" " * random.randint(0, 3) + random.choice("01ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜ"),
                                style=ctx.theme.teal))
        return Columns([left, Group(*rows)], padding=(2, 6))


# 7. CLI — prompt terminal minimalis
class LayoutCLI(BaseLayout):
    name = "cli"

    def render(self, ctx: FrameContext):
        prompt = Text()
        prompt.append("user@colorcode", style=f"bold {ctx.theme.teal}")
        prompt.append(":~$ ", style="white")
        prompt.append("current_lyrics --play", style=ctx.theme.dim_style)
        lyric = Text("  " + (ctx.active_line_text or ""), style=f"bold {ctx.theme.fire_orange}")
        return Group(Text(""), Text(" ⌛ ", style=ctx.theme.purple), Text(""),
                     prompt, Text(""), lyric, Text(""),
                     Text(progress_bar(ctx.progress, 50), style=ctx.theme.accent_style))


# 8. Cinematic — cover wide atas, subtitle bawah
class LayoutCinematic(BaseLayout):
    name = "cinematic"

    def render(self, ctx: FrameContext):
        widened = ["".join(ch * 2 for ch in l) for l in ctx.full_ascii]
        top_rows = int(ctx.height * 0.72)
        top = _ansi(widened[:top_rows])
        block = Text("\n" + center((ctx.active_line_text or "").upper(), ctx.width),
                     style=f"bold white on black")
        return Group(top, block)


# 9. Syntax — lyric jadi kode
class LayoutSyntax(BaseLayout):
    name = "syntax"

    def render(self, ctx: FrameContext):
        from rich.syntax import Syntax
        code = f'# "{ctx.song_title}" — {ctx.song_artist}\n'
        code += "def sing():\n    pain = buried_inside()\n"
        code += f'    lyrics = "{ctx.active_line_text or ""}"\n'
        code += "    if pain_inside == True:\n        print(lyrics)\n"
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        comment = _ansi([" * " + l for l in ctx.ascii_art[:14]])
        return Columns([comment, syntax], padding=(2, 4))


# 10. Kinetic — kata besar acak
class LayoutKinetic(BaseLayout):
    name = "kinetic"

    def render(self, ctx: FrameContext):
        import random
        words = (ctx.active_line_text or "").split()
        if not words:
            return Text("")
        random.seed(int(ctx.time * 3))
        feat = random.choice(words).upper()
        out = Text()
        out.append(feat, style=f"bold {ctx.theme.portal_red}")
        return Panel(out, border_style=ctx.theme.fire_orange, title="HOOK")


# 11. Poster — like a band poster / Spotify-now-playing card.
# Cover kiri, lyric STACKED (ditumpuk, tidak hilang) kanan, header NOW
# PLAYING di atas, footer status bar (progress + volume bars) di bawah.
class LayoutPoster(BaseLayout):
    name = "poster"

    def render(self, ctx: FrameContext):
        teal = ctx.theme.teal
        purple = ctx.theme.purple
        red = ctx.theme.portal_red

        # --- Header ---------------------------------------------------
        header = Text()
        header.append("● NOW PLAYING", style=f"bold {red}")
        header.append("   " + ctx.song_title.upper(), style=f"bold {teal}")

        # --- Body: cover (left) + stacked lyrics (right) ---------------
        left = Panel(
            _cover(ctx),
            border_style=teal,
            title="COLORCODE",
            title_align="left",
            padding=(0, 1),
        )
        right = Panel(
            stacked_lyrics(ctx, window=14),
            border_style=purple,
            title=f"{ctx.song_artist} — lyrics",
            title_align="left",
            padding=(0, 2),
        )
        body = Columns([left, right], padding=(2, 4))

        # --- Footer / status bar --------------------------------------
        ts = f"{int(ctx.time // 60)}:{int(ctx.time % 60):02d}"
        bar = progress_bar(ctx.progress, width=24)
        vol = volume_bars((ctx.beat if ctx.beat else 0.5))
        footer = Text()
        footer.append(f"  {ts}  ", style=ctx.theme.dim_style)
        footer.append(bar, style=teal)
        footer.append(f"  [ {vol} ]", style=purple)
        footer.append(f"  {int(ctx.progress * 100)}%", style=ctx.theme.dim_style)

        return Group(
            header,
            Text(""),
            body,
            Text(""),
            footer,
        )


# 12. Editor — single giant Panel + vertical Group (per rich spec):
# top = cover(left) + metadata(right, no border, far padding);
# middle = lyrics directly below with NO horizontal divider, format
# " NN │ text", active line "> NN │" highlighted, 3 before/after;
# bottom = Rule separator, then waveform(left) + progress(right).
class LayoutEditor(BaseLayout):
    name = "editor"

    def render(self, ctx: FrameContext):
        from rich.rule import Rule
        from rich.table import Table

        gold = ctx.theme.teal        # gold accent on maroon
        cream = ctx.theme.pastel_yellow
        red = ctx.theme.portal_red
        dim = ctx.theme.dim_style

        # --- TOP: cover (left) + metadata (right), no border -----------
        # re-render a compact cover so the whole thing fits one screen
        from engine.ascii_art import cached_ascii
        from pathlib import Path
        cover_lines, _ = (cached_ascii(ctx.cover_path, 22,
                            str(Path(ctx.cover_path).parent / ".art_editor.txt"))
                           if ctx.cover_path else ([], "pillow"))
        cover_txt = (Text.from_ansi("\n".join(cover_lines))
                     if cover_lines else _cover(ctx, "ascii_art"))
        cover_txt.no_wrap = True

        ts = f"{int(ctx.time // 60)}:{int(ctx.time % 60):02d}"
        total_s = int(ctx.time / ctx.progress // 60) if ctx.progress > 0 else 0
        total_m = int(ctx.time / ctx.progress % 60) if ctx.progress > 0 else 0
        total = f"{total_s}:{total_m:02d}" if ctx.progress > 0 else "--:--"
        info = Text()
        info.append(ctx.song_title.upper() + "\n", style=f"bold {cream}")
        info.append(ctx.song_artist + "\n", style=dim)
        info.append("COLORCODE\n", style=dim)
        info.append(f"{ts} / {total}", style=f"bold {gold}")

        top = Columns([cover_txt, info], padding=(0, 6), align="left")

        # --- MIDDLE: lyrics, NO divider, 3 before / 1 active / 3 after --
        idx = ctx.active_line_index if ctx.active_line_index >= 0 else 0
        all_lines = ctx.all_lines
        window = 7  # 3 + 1 + 3
        start = max(0, idx - 3)
        end = min(len(all_lines), start + window)
        if end - start < window:
            start = max(0, end - window)
        lyric_rows = []
        for i in range(start, end):
            num = f"{i + 1:>3}"
            text = all_lines[i]
            if i == idx:
                lyric_rows.append(
                    Text(f"> {num} │ ", style=f"bold {red}") +
                    Text(text, style=f"bold {cream}"))
            else:
                lyric_rows.append(
                    Text(f"  {num} │ ", style=dim) +
                    Text(text, style=dim))

        # --- BOTTOM: Rule, then waveform (left) + progress (right) -----
        wave = waveform(ctx.beat if ctx.beat else (ctx.progress * 3 % 1), width=18)
        bar = progress_bar(ctx.progress, width=22)
        bottom = Columns(
            [Text(wave, style=gold), Text(bar + f"  {int(ctx.progress * 100)}%", style=gold)],
            padding=(0, 4), align="left",
        )

        body = Group(top, Text(""), *lyric_rows, Text(""), Rule(style=gold), bottom)

        return Panel(body, border_style=gold, padding=(0, 1))


# 13. Vertical — ONE outer Panel (fixed width & height) holding:
# left photo WITH rain on top | big TTF lyric (center) | cover + about (right).
# All three columns share the SAME height H (left == cover+about), widths are
# modest so everything fits without scrolling. Footer shares the outer width.
class LayoutVertical(BaseLayout):
    name = "vertical"

    def render(self, ctx: FrameContext):
        from pathlib import Path
        from engine.ascii_art import chafa_fit, cover_with_fx, left_with_rain
        from engine.layouts.helpers import spotify_lyric
        from engine.song_registry import SongRegistry

        gold = ctx.theme.teal
        cream = ctx.theme.pastel_yellow
        dim = ctx.theme.dim_style
        red = ctx.theme.portal_red

        cfg = SongRegistry().load(ctx.song_id) if hasattr(ctx, "song_id") else None
        folder = Path(ctx.cover_path).parent if ctx.cover_path else Path(".")

        # Fixed dimensions for symmetry + no reflow/flicker. Heights kept
        # modest so the footer is always visible.
        inner = max(40, ctx.width - 4)
        col_w = max(12, inner // 3 - 2)             # equal-width cards (room for gaps)
        H = max(14, min(ctx.height - 10, 26))     # shared column height

        # ---- LEFT: left-section photo with rain ON TOP, stretched to fill --
        left_img = folder / (cfg.left_section if cfg and getattr(cfg, "left_section", None) else "left-section.png")
        if left_img.exists():
            llines, _ = left_with_rain(str(left_img), col_w, ctx.time, height=H)
        else:
            llines, _ = ([], "pillow")
        left_render = _ansi(llines) if llines else Text(" ")
        left = Panel(left_render, border_style=gold, title="🌧 MERRA",
                     padding=(0, 1), width=col_w, height=H)

        # ---- MIDDLE: current lyric line ONLY (plain, centred) --------
        idx = ctx.active_line_index if ctx.active_line_index >= 0 else 0
        all_lines = ctx.all_lines
        active = all_lines[idx] if 0 <= idx < len(all_lines) else "♪"
        from rich.align import Align
        # no per-word color, no neighbours — just the line being sung, centered
        lyric_block = Align(
            Text(active, style=f"bold {cream}", overflow="fold"),
            align="center", vertical="middle",
        )
        mid_panel = Panel(lyric_block, border_style=gold, title="♪ NOW PLAYING",
                          title_align="left", padding=(0, 1), width=col_w, height=H)

        # ---- RIGHT: single cover image with subtle motion, stretched ----
        if ctx.cover_path:
            cover_lines, _ = cover_with_fx(str(ctx.cover_path), col_w, H, ctx.time)
            cover_render = _ansi(cover_lines) if cover_lines else Text(" ")
        else:
            cover_render = Text(" ")
        cover_render.no_wrap = True
        right_panel = Panel(cover_render, border_style=gold, title=ctx.song_title,
                            padding=(0, 1), width=col_w, height=H)

        # ---- BODY: 3 equal-height, equal-width columns --------------
        body = Columns([left, mid_panel, right_panel], padding=(1, 1), align="center")

        # ---- FOOTER: Spotify-player style (title/artist + NOW PLAYING,
        #          then timestamp | progress bar | percent + waveform) --
        ts = f"{int(ctx.time // 60)}:{int(ctx.time % 60):02d}"
        total_s = int(ctx.time / ctx.progress // 60) if ctx.progress > 0 else 0
        total_m = int(ctx.time / ctx.progress % 60) if ctx.progress > 0 else 0
        total = f"{total_s}:{total_m:02d}" if ctx.progress > 0 else "--:--"
        bar_w = max(10, inner - 40)
        bar = progress_bar(ctx.progress, width=bar_w)
        wave = waveform(ctx.beat if ctx.beat else (ctx.progress * 3 % 1), width=14)
        top = Columns([
            Text(f"{ctx.song_title}", style=f"bold {cream}") +
            Text(f"   {ctx.song_artist}", style=dim),
            Text("● NOW PLAYING", style=f"bold {red}"),
        ], padding=(1, 2), align="left")
        bottom = Text()
        bottom.append(ts, style=dim)
        bottom.append("  ")
        bottom.append(bar, style=gold)
        bottom.append("  ")
        bottom.append(f"{int(ctx.progress*100)}%", style=gold)
        bottom.append("   ")
        bottom.append(wave, style=gold)
        bottom.append(f"   {total}", style=dim)
        foot_panel = Panel(Group(top, bottom), border_style=gold,
                           padding=(0, 1), width=inner)

        outer = Panel(Group(body, Text(""), foot_panel),
                      border_style=gold, padding=(0, 1), width=inner + 2)
        return outer


# Register all
for _c in (LayoutSplit, LayoutWatermark, LayoutGrid, LayoutPortal, LayoutFocus,
          LayoutMatrix, LayoutCLI, LayoutCinematic, LayoutSyntax, LayoutKinetic,
          LayoutPoster, LayoutEditor, LayoutVertical):
    LayoutRegistry.register(_c.name, _c)
