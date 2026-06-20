@echo off
REM BetterFlow Desktop — Windows installer
REM Run by double-clicking this file.

setlocal
cd /d "%~dp0"

echo.
echo  ==========================================
echo   BetterFlow Desktop - Windows Installer
echo  ==========================================
echo.

REM Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
python --version

REM Create virtual environment
echo.
echo [2/4] Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
)
call .venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo [3/4] Installing dependencies (first run downloads ~150MB Whisper model)...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies.
    echo.
    pause
    exit /b 1
)

REM Copy default config
echo.
echo [4/4] Setting up config...
if not exist "%USERPROFILE%\.betterflow\config.json" (
    if not exist "%USERPROFILE%\.betterflow" mkdir "%USERPROFILE%\.betterflow"
    copy config.example.json "%USERPROFILE%\.betterflow\config.json" >nul
    echo Config created at: %USERPROFILE%\.betterflow\config.json
) else (
    echo Config already exists at: %USERPROFILE%\.betterflow\config.json
)

echo.
echo  ==========================================
echo   Installation complete!
echo  ==========================================
echo.
echo  To start BetterFlow:
echo    1. Double-click run.bat
echo    2. Look for the coffee cup icon in your system tray
echo    3. Click into any text field (WhatsApp, Word, etc.)
echo    4. Press Ctrl+Shift+Space to start dictating
echo    5. Press it again (or stop talking) to transcribe
echo.
pause
