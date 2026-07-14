# start.ps1 — jalan di terminal SAAT INI (PowerShell / VS Code), tidak spawn window baru.
# Pakai:  .\start.ps1          (atau  .\start.ps1 merra)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONLEGACYWINDOWSSTDIO = "0"
$env:PATH = "$root\tools\chafa;$env:PATH"
$venv = "$root\.venv\Scripts\python.exe"
if (-not (Test-Path $venv)) { Write-Error "venv tidak ditemukan: $venv" ; exit 1 }
$song = if ($args.Count -ge 1) { $args[0] } else { "merra" }
& $venv "$root\main.py" run $song --audio --no-countdown
