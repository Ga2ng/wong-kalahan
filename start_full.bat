@echo off
:: Fullscreen launcher — opens a NEW maximized terminal window.
:: Usage:  start_full.bat [song] [start mm:ss] [layout] [audio]
::   start_full.bat                -> merra, full layout, with audio
::   start_full.bat merra          -> merra, full layout, with audio
::   start_full.bat turnover       -> turnover (sad cover animation, no audio)
::   start_full.bat merra 1:30 full audio
setlocal
cd /d "%~dp0"
set "PATH=%~dp0tools\chafa;%PATH%"
set "SONG=merra"
if not "%~1"=="" set "SONG=%~1"
set "STARTARG="
if not "%~2"=="" set "STARTARG=--start %~2"

:: layout: explicit arg > merra defaults to "full" > otherwise use song config
set "LAYOUT="
if "%~3"=="" (
    if /i "%SONG%"=="merra" set "LAYOUT=--layout full"
) else (
    set "LAYOUT=--layout %~3"
)

:: audio: explicit "audio" arg > merra on by default > turnover off
set "AUDIO="
if /i "%~4"=="audio" (
    set "AUDIO=--audio"
) else if /i "%SONG%"=="merra" (
    set "AUDIO=--audio"
)

start "Pixel Lyrics - %SONG%" /max cmd /k "%~dp0.venv\Scripts\python.exe main.py run %SONG% %LAYOUT% %AUDIO% --no-countdown %STARTARG%"
endlocal
