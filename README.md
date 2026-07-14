# Pixel Lyrics Engine (Terminal TUI + chafa)

Engine Python: cover album di-render jadi **pixel-art berwarna di terminal** pakai
`chafa` (tools/chafa/chafa.exe, sudah ada — TIDAK perlu install apa pun), lalu
di-layout bersama **lirik realtime + audio** ala Spotify tapi bergrafis pixel-art.
Semua tampil BARENGAN di terminal (PowerShell / cmd / Windows Terminal).

## Cara jalanin (SATU tombol)
Double-click **`start.bat`**  → langsung: audio muter + cover chafa + lirik sync.
Pilih lagu: `start.bat merra`  (atau lagu lain nanti).

Manual di PowerShell:
```
cd C:\DEV\wong_kalahan
.venv\Scripts\Activate.ps1
python main.py run merra --audio --no-countdown
```

## Kenapa tadi gambar nggak muncul? (sudah dibenahi)
- `chafa songs/merra/cover.jpeg` gagal karena `chafa` belum di PATH.
  Sekarang `start.bat` menaruh `tools/chafa` ke PATH, dan engine otomatis pakai
  `tools/chafa/chafa.exe`. Bisa juga panggil manual:
  `tools/chafa/chafa.exe songs/merra/cover.jpeg`
- Cover kepotong di terminal sempit → sekarang lebar cover adaptif ke terminal.
- Escape ANSI di-strip → engine enable Virtual Terminal Processing + utf-8 otomatis.

## chafa
https://github.com/hpjansson/chafa — engine panggil:
`chafa <img> --colors full --symbols block --format symbols --size Wx`
(truecolor 24-bit, block-character pixel art).

## Struktur
```
engine/   clock_source, sync_engine, song_registry, layout_registry,
          theme_registry, tui_renderer (Live loop + _enable_vt), ascii_art (chafa),
          countdown_engine
engine/layouts/   10 layout TUI (split, watermark, grid, portal, focus, matrix,
                  cli, cinematic, syntax, kinetic)
engine/themes/    dark / retro_green / neon
songs/merra/      config.json, lyrics.json, lyrics_aligned.json, cover.jpeg, audio.mp3
tools/chafa/      chafa.exe (bundled Windows binary)
tools/align.py     forced lyric alignment (faster-whisper)
start.bat         SATU tombol: audio + cover + lirik barengan
```
