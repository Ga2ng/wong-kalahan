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
:: one button: audio + chafa cover + synced lyrics, all together
%PY% main.py run %SONG% --audio --no-countdown
pause
