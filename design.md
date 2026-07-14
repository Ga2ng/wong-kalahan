# DESIGN.md — Pixel Lyrics Engine (Terminal TUI + chafa)

Engine Python: cover album di-render jadi **pixel-art berwarna di terminal** pakai
`chafa` (`tools/chafa/chafa.exe`, sudah ada — TIDAK perlu install apa pun), lalu
di-layout bersama **lirik realtime + audio** ala Spotify / poster band, semua
tampil BARENGAN di terminal (PowerShell / cmd / Windows Terminal).

## 1. Tujuan & Vibe
- Hook TikTok: cover album jadi grafis terminal yang indah + lirik sync.
- "Layouting terminal styling ala web" → TUI yang terlihat seperti music-player
  card modern (header, panel berborder warna, footer status bar), BUKAN sekadar
  teks lewat.
- Palet diambil dari cover COLORCODE: teal `#2A9D8F`, purple `#8187B5`,
  red `#E63946`, orange `#F4A261` (lihat `engine/base.py` BaseTheme).

## 2. Lyric behaviour (PENTING — keputusan user)
- **Lirik DITUMPUK (stacked), tidak dihilangkan** setelah tampil.
  - Line yang sudah dinyanyikan TETAP terlihat (di-dim) → efek seperti band
    poster / karaoke roll, bukan 1 baris yang saling ganti.
  - Line AKTIF di-highlight terang (red bold, prefix `▸`).
  - Line mendatang tampil redup di bawah untuk konteks.
- Implementasi: `LayoutPoster` + `helpers.stacked_lyrics(ctx, window=14)`.
  Semua line ada di `FrameContext.all_lines` (diisi dari `SyncEngine.lines`).

## 3. Layout "poster" (default, Layout #11)
Struktur (rich Group / Columns / Panel):
```
● NOW PLAYING   MERRA                 <- header (red + teal bold)
+-----------+  +--------------------+
| COLORCODE |  | COLORCODE — lyrics |   <- cover kiri (chafa, border teal),
|  (cover)  |  | ▸ active line      |      lyric stacked kanan (border purple)
|  chafa    |  |   done line (dim) |
+-----------+  |   done line (dim) |
               +--------------------+
  1:05  ████░░░░░░░░░░░  [ ████░░░░░░ ]  56%   <- footer status bar
```
- Border panel pakai warna palet cover (bukan putih).
- Footer: timestamp, progress bar, volume visualizer `[ ███░░░ ]`, persen.

## 4. Integrasi chafa (dari web resmi hpjansson.org/chafa)
Engine panggil:
`chafa <img> --colors full --symbols block --format symbols --size Wx`
- `--colors full` = truecolor 24-bit (`38;2;`) — paling kompatibel terminal modern.
- Output chafa adalah **raw ANSI** → di-layout WAJIB di-parse pakai
  `rich.text.Text.from_ansi(...)`, BUKAN `Text(raw_string)`. Kalau dimasukkan
  ke `Text(...)` biasa, rich tidak parse escape → cover jadi 1 baris rusak.
- Lebar cover adaptif ke terminal: `cols = min(ascii_columns, max(24, term_w-42))`
  supaya tidak kepotong di conhost sempit.

## 5. Prompt penguat (dari user / Gemini) — rujukan styling
> "Create a Python script using `rich` for a TUI music visualizer for a TikTok
> hook. Chafa converts the 'Colorcode' album cover into ANSI-colored text.
> Structure the terminal: Split/Tiling layout, main visual (Chafa) left/center,
> lyrics panel right/bottom. Header 'NOW PLAYING' (cyan/magenta). Lyrics:
> current line highlighted (#E63946 / #F4A261), previous/upcoming dimmed.
> Footer status bar with progress + volume visualizer. Panels with border_style
> from cover palette (teal #2A9D8F, purple #8187B5), rounded/heavy borders."
(Diimplementasikan di `LayoutPoster`.)

## 6. Struktur per-lagu (GENERIC — tidak ada yang hardcode "merra")
```
songs/<SONG_ID>/
  config.json          # id, title, artist, layout, theme, cover, lyrics, ...
  lyrics.txt           # plain, satu baris per lyric  (dipakai align.py)
  lyrics.json          # hasil timestamp (manual atau dari align.py)
  lyrics_aligned.json  # alias lyrics.json
  cover.<ext>          # gambar cover
  audio.<ext>          # file audio
tools/align.py         # --song <id>  (GENERIC, lyrics dari lyrics.txt)
```
- Nambah lagu baru = bikin folder `songs/<id>/` + `config.json` + `lyrics.txt`
  + `cover` + `audio`. Tidak ubah engine.
- `align.py` sudah generic: `python tools/align.py --song <id>` (butuh
  faster-whisper, optional — bisa juga isi `lyrics.json` manual).

## 7. Cara jalanin
Double-click `start.bat` (atau `start.bat <song_id>`). Satu tombol: audio +
cover chafa + lirik sync barengan. Venv python dipakai by absolute path
(`%~dp0.venv\Scripts\python.exe`) supaya tidak bentrok dengan venv lain.

## 8. Layout lain (legacy, masih ada)
split, watermark, grid, portal, focus, matrix, cli, cinematic, syntax, kinetic.
Pilih via `python main.py run <id> --layout <nama>`.
