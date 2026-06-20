@echo off
REM BetterFlow Desktop — Windows launcher
REM Double-click to start.

cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
    echo BetterFlow is not installed. Running installer first...
    call install.bat
    if errorlevel 1 exit /b 1
)
call .venv\Scripts\activate.bat
python betterflow_desktop.py
pause
