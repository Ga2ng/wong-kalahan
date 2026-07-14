@echo off
cd /d %~dp0
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=0
:: put bundled chafa on PATH so `chafa` works and engine finds it
set PATH=%~dp0tools\chafa;%PATH%
:: use the project venv python directly (avoids resolving to another venv)
set PY=%~dp0.venv\Scripts\python.exe
if "%~1"=="" (
    set SONG=merra
) else (
    set SONG=%~1
)
:: %2 = start time, e.g. "1:30" or "90" (start at that minute/second)
if "%~2"=="" (
    set STARTARG=
) else (
    set STARTARG=--start %~2
)
:: one button: audio + chafa cover + synced lyrics, all together
::   usage: start.bat [song] [start_time]
::   example: start.bat merra 1:30
%PY% main.py run %SONG% --audio --no-countdown %STARTARG%
pause
