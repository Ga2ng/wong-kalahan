@echo off
:: Fullscreen showcase launcher — opens a NEW maximized terminal window,
:: renders the "full" layout (big chafa lyric left, big cover right, JSON
:: data panel bottom). Usage:  start_full.bat [song] [start mm:ss]
::   start_full.bat merra
::   start_full.bat merra 1:30
setlocal
cd /d "%~dp0"
set "PATH=%~dp0tools\chafa;%PATH%"
set "SONG=merra"
if not "%~1"=="" set "SONG=%~1"
set "STARTARG="
if not "%~2"=="" set "STARTARG=--start %~2"
:: open a fresh MAXIMIZED console running the full layout
start "Pixel Lyrics - FULL" /max cmd /k "%~dp0.venv\Scripts\python.exe main.py run %SONG% --layout full --audio --no-countdown %STARTARG%"
endlocal
