# PRD.md — Pixel Lyrics Engine (Python)

## Project Name
**Pixel Lyrics Engine**

A modular, terminal-launched Python engine that renders real-time synchronized lyrics in a pixel-art UI, built primarily to produce aesthetic lyric-video footage for TikTok / Reels / Shorts. It is **not** a music player — audio is played externally (phone/speaker) by default, with an optional internal audio mode.

> "A game engine, but for lyric visualization."

---

# 1. Vision

One core engine, unlimited songs. Every song is a self-contained "cartridge" (folder) that plugs into the engine and defines its own layout, theme, assets, and lyric timing — without ever touching engine code. Run any song with one command; the engine discovers, validates, and renders it.

---

# 2. Goals

- Real-time, frame-accurate lyric sync (line + word level)
- Per-song custom visual identity (layout, theme, effects)
- Zero engine-code changes to add a new song
- Config-driven, validated with schemas (fail fast, fail clearly)
- 60 FPS rendering suitable for screen recording
- Fast startup (target: under 2s to first frame)
- Cross-platform (Windows / macOS / Linux)
- Scales to dozens/hundreds of songs without perf degradation

---

# 3. Core Design Principle: Plugin Architecture

The engine is a **runtime + registries**. Three registries make the "different layout per song, same project" requirement work:

```
LayoutRegistry   → maps layout name (string) → Layout class
ThemeRegistry    → maps theme name (string)  → Theme class / preset
SongRegistry     → auto-discovers every folder under songs/
```

Flow: `python main.py <song_id>` → SongRegistry loads `songs/<song_id>/config.json` → config declares `layout` + `theme` names → engine resolves them from the registries → engine renders using the resolved layout/theme + that song's own assets.

This means Layout D (RPG dialogue box) and Layout G (CRT monitor) can both exist, be selected per song, and share zero song-specific code inside the engine itself.

---

# 4. Main Use Cases

### A. TikTok Hook Recording (primary use case)
```bash
python main.py title_fight
```
```
3...
2...
1...
GO
```
User presses Play on their phone at "GO". Lyrics render according to timestamps + offset. User screen-records the window.

### B. Internal Audio Mode (optional)
```bash
python main.py title_fight --audio
```
Engine plays the audio itself via `pygame-ce` / `sounddevice`; lyric sync derives from playback clock instead of a manual timer.

### C. Showcase Mode
```bash
python main.py title_fight --fullscreen
```
Fullscreen, animated background, album art, full effect stack — for passive display rather than hook-recording.

---

# 5. Folder Structure

```
pixel-lyrics/
├── main.py                     # CLI entry point (typer)
├── requirements.txt
├── pyproject.toml
├── config/
│   └── app_settings.json       # global defaults (fps, window size, default theme)
│
├── engine/
│   ├── __init__.py
│   ├── song_registry.py        # discovers & validates songs/*
│   ├── layout_registry.py      # registers all Layout classes
│   ├── theme_registry.py       # registers all Theme presets
│   ├── config_schema.py        # pydantic models for config.json / lyrics.json
│   ├── timer_engine.py         # clock, pause/resume/seek/speed
│   ├── sync_engine.py          # active-lyric lookup (binary search by timestamp)
│   ├── countdown_engine.py     # 3-2-1-GO sequence
│   ├── animation_engine.py     # easing / interpolation helpers
│   └── export_engine.py        # future: GIF/MP4 export hooks
│
├── renderer/
│   ├── __init__.py
│   ├── render_loop.py          # QTimer-driven 60 FPS frame loop
│   ├── lyric_renderer.py       # fade/slide/glow/typing/wave/dissolve/rainbow
│   ├── album_renderer.py       # rounded corners, glow, float, rotate, blur-bg
│   └── background_renderer.py # static / gif / procedural (gradient, noise, CRT)
│
├── audio/
│   ├── __init__.py
│   ├── player.py                # pygame-ce / python-vlc playback (--audio mode)
│   └── clock_source.py          # abstracts "time source": manual timer vs audio clock
│
├── layouts/
│   ├── base_layout.py            # abstract Layout interface
│   ├── layout_album_top.py       # Layout A
│   ├── layout_lyrics_top.py      # Layout B
│   ├── layout_large_album.py     # Layout C
│   ├── layout_pixel_dialog.py    # Layout D — RPG dialogue box
│   ├── layout_gameboy.py         # Layout E
│   ├── layout_ps1_memory.py      # Layout F
│   └── layout_crt_monitor.py     # Layout G
│
├── themes/
│   ├── base_theme.py
│   ├── theme_dark.py
│   ├── theme_retro_green.py
│   └── theme_neon.py
│
├── shaders/                     # optional GLSL/QOpenGL effects
│   ├── crt.frag
│   ├── bloom.frag
│   └── scanlines.frag
│
├── fonts/                        # shared/global pixel fonts (fallback)
│   └── pixel_default.ttf
│
├── assets/                       # shared engine assets (icons, placeholders)
│   └── placeholder_cover.png
│
└── songs/
    ├── title_fight/
    │   ├── config.json
    │   ├── lyrics.json
    │   ├── cover.png
    │   ├── background.png
    │   └── font.ttf              # optional, overrides fonts/pixel_default.ttf
    ├── basement/
    │   └── ...
    ├── balance_and_composure/
    │   └── ...
    └── citizen/
        └── ...
```

**Rule:** a song folder never contains `.py` logic. If a song truly needs unique behavior beyond config (e.g. a bespoke particle pattern), that behavior is built as a new reusable Layout/Theme class in `layouts/` or `themes/`, registered by name, and referenced from `config.json` — never hardcoded per song inside the engine.

---

# 6. Song Configuration Schema

`songs/<id>/config.json`:

```json
{
  "id": "title_fight",
  "title": "Head In The Ceiling Fan",
  "artist": "Title Fight",

  "layout": "pixel_dialog",
  "theme": "dark",

  "offset": -0.32,
  "fps": 60,

  "cover": "cover.png",
  "background": "background.png",
  "font": "font.ttf",
  "lyrics": "lyrics.json",

  "background_mode": "static",
  "effects": ["glow", "pixel_dissolve"]
}
```

Validated at load time via `pydantic` (`config_schema.py`). Required: `id`, `title`, `layout`, `lyrics`. Everything else falls back to `config/app_settings.json` defaults if omitted — a missing `theme`, for example, resolves to `"default"` rather than crashing.

If `layout` or `theme` names don't exist in the registries, the engine fails fast with a readable error listing valid registered names — not a silent fallback that hides a typo.

---

# 7. Lyrics Format

`songs/<id>/lyrics.json`:

```json
{
  "lyrics": [
    {
      "start": 4.23,
      "end": 7.42,
      "text": "THIS WAS THE FIRST TIME",
      "words": [
        { "text": "THIS", "start": 4.23, "end": 4.80 },
        { "text": "WAS",  "start": 4.81, "end": 5.10 }
      ]
    }
  ]
}
```

- Line-level timestamps are required; `words[]` is optional and only needed for karaoke mode.
- `sync_engine.py` keeps lyric lines sorted by `start` and uses binary search against the current clock time each frame — O(log n) lookup regardless of song length.

---

# 8. Offset System

```json
{ "offset": -0.32 }
```
Applied once, at clock-read time (`clock_source.py`), as `effective_time = raw_time + offset`. This shifts the whole song's sync without touching a single timestamp in `lyrics.json` — essential when recording from an external phone speaker with audio latency.

---

# 9. Rendering Pipeline

```
Load app_settings.json (global defaults)
        ↓
Resolve <song_id> via SongRegistry
        ↓
Validate config.json + lyrics.json (pydantic)
        ↓
Resolve layout + theme from registries
        ↓
Load assets (cover, background, font) with graceful fallback to /assets, /fonts
        ↓
Run Countdown Engine (3-2-1-GO)
        ↓
Start Timer / Clock Source (manual or audio-driven)
        ↓
Render Loop @ target FPS:
    read clock → sync_engine finds active lyric
              → lyric_renderer draws text + effect
              → album_renderer draws cover + effect
              → background_renderer draws background
              → compose frame
        ↓
(optional) Export Engine → GIF/MP4
```

Playback controls (`timer_engine.py`): pause, resume, seek, offset, speed — all operate on the clock source, so renderers never know or care whether time is coming from a manual timer or real audio playback.

---

# 10. Engine Modules — Responsibilities

| Module | Responsibility |
|---|---|
| Song Registry | Scans `songs/`, validates each folder, exposes `list()` / `load(id)` |
| Layout Registry | Maps layout name → Layout class; raises on unknown name |
| Theme Registry | Maps theme name → Theme preset; raises on unknown name |
| Config Schema | Pydantic models for `config.json` / `lyrics.json`, with defaults |
| Timer Engine | Clock state machine: play/pause/seek/speed/offset |
| Sync Engine | Binary-search active-lyric lookup per frame |
| Countdown Engine | 3-2-1-GO sequence before render starts |
| Animation Engine | Easing/interpolation shared by all layouts |
| Renderer (render_loop) | Drives the 60 FPS Qt frame loop |
| Audio Engine | Optional internal playback (`--audio` mode) |
| Export Engine | Future: frame capture → GIF/MP4 |

---

# 11. Multiple Layouts (per-song, pluggable)

| Layout | Description |
|---|---|
| A | Album top / Lyrics bottom |
| B | Lyrics top / Album bottom |
| C | Large album / Small lyrics |
| D | Pixel RPG dialogue box |
| E | GameBoy UI |
| F | PS1 memory card style |
| G | CRT monitor |

Every layout implements the same `base_layout.py` interface (`render(frame_ctx)`), so the render loop never branches on "which layout" — it just calls `.render()` on whatever the registry resolved.

---

# 12. Terminal Commands (Typer CLI)

```bash
python main.py title_fight                 # run in windowed mode
python main.py title_fight --fullscreen     # showcase mode
python main.py title_fight --window         # explicit windowed
python main.py title_fight --audio          # internal audio playback
python main.py title_fight --debug          # verbose logging (loguru)
python main.py --list                       # list all discovered songs
python main.py --validate title_fight       # validate config without rendering
```

---

# 13. Tech Stack & Dependencies

**UI / Rendering**
- `PySide6` — GPU-accelerated Qt UI, animations, high-DPI, image rendering
- Qt Graphics View, `QPropertyAnimation`, `QPainter`, OpenGL (optional)

**Audio**
- `pygame-ce`, `sounddevice`, `python-vlc` (optional), `ffmpeg-python`

**Forced Alignment (future auto-sync)**
- `whisperx`, `faster-whisper`, `torch`

**Image Processing**
- `Pillow`, `opencv-python`, `numpy`

**Effects**
- Custom shaders (`.frag`) for CRT/scanlines/bloom, or Qt-native blur/vignette

**Utilities**
- `pydantic` (schema validation), `typer` (CLI), `rich` (terminal output), `loguru` (logging), `orjson` (fast JSON)

**Config**
- JSON (primary), YAML/TOML (optional overrides)

**Packaging**
- `PyInstaller` (now), `Nuitka` (future, for faster startup binaries)

`requirements.txt`:
```
PySide6
pygame-ce
sounddevice
python-vlc
ffmpeg-python
Pillow
opencv-python
numpy
pydantic
typer
rich
loguru
orjson
whisperx
faster-whisper
torch
```

---

# 14. Error Handling & Validation Rules

- Missing/invalid `config.json` → fail fast with the exact validation error (pydantic), never a silent default that masks a typo.
- Unknown `layout` / `theme` name → list valid registered names in the error.
- Missing asset file (cover/background/font) → fall back to `/assets` and `/fonts` shared defaults, with a `--debug` log line noting the fallback (never a hard crash for a missing image).
- Empty or malformed `lyrics.json` → engine still starts, shows title/artist only, logs a warning.
- `--validate <song_id>` runs schema + asset checks only, no rendering — useful before recording.

---

# 15. Future Features

- Spotify "Now Playing" integration
- YouTube Music integration (where legally/technically permitted)
- OBS plugin
- Live lyric editor / visual node editor / theme editor
- Beat detection + audio spectrum visualizer
- Particle engine, camera movement, full shader support
- Multi-monitor support
- GIF / MP4 export
- Plugin marketplace for community themes/layouts
- Auto-alignment pipeline: `song.mp3 + lyrics.txt → WhisperX → forced alignment → lyrics.json`

---

# 16. Non-Goals (Current Version)

- Not a music streaming service
- No DRM bypass
- No automatic downloading of copyrighted lyrics from streaming services
- No audio editing
- Not a full video editor

---

# 17. Success Criteria

- Add a new song by creating a folder + `config.json` + `lyrics.json` only — zero engine code changes.
- Supports dozens/hundreds of songs without touching engine internals.
- Each song can look completely different (layout + theme) while sharing one engine.
- Lyric sync stays accurate and adjustable via a single global `offset` per song.
- App reaches first frame in under ~2 seconds.
- Renders smoothly at 60 FPS, clean enough for TikTok/Reels/Shorts screen recording.