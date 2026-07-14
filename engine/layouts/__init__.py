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
from engine.layouts.helpers import center, progress_bar


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


# Register all
for _c in (LayoutSplit, LayoutWatermark, LayoutGrid, LayoutPortal, LayoutFocus,
          LayoutMatrix, LayoutCLI, LayoutCinematic, LayoutSyntax, LayoutKinetic):
    LayoutRegistry.register(_c.name, _c)
