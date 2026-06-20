#!/usr/bin/env bash
# BetterFlow Desktop — macOS / Linux installer
# Run with: bash install.sh

set -e
cd "$(dirname "$0")"

echo ""
echo "  =========================================="
echo "   BetterFlow Desktop - Installer"
echo "  =========================================="
echo ""

# Check Python
echo "[1/4] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "ERROR: Python 3 is not installed or not in PATH."
    echo ""
    if [[ "$(uname)" == "Darwin" ]]; then
        echo "Install Python 3.10+ with Homebrew:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "  brew install python@3.12"
    else
        echo "On Ubuntu/Debian:"
        echo "  sudo apt update && sudo apt install python3 python3-venv python3-pip python3-tk"
        echo "On Fedora:"
        echo "  sudo dnf install python3 python3-tkinter"
    fi
    echo ""
    exit 1
fi
python3 --version

# Linux: ensure tkinter and portaudio
if [[ "$(uname)" != "Darwin" ]]; then
    echo ""
    echo "[2/4] Checking system libraries..."
    if ! python3 -c "import tkinter" 2>/dev/null; then
        echo "tkinter not found. Installing..."
        sudo apt-get install -y python3-tk 2>/dev/null || sudo dnf install -y python3-tkinter 2>/dev/null || {
            echo "Could not install tkinter automatically. Please run:"
            echo "  sudo apt install python3-tk"
            exit 1
        }
    fi
    # portaudio (for sounddevice)
    if ! ldconfig -p 2>/dev/null | grep -q libportaudio; then
        echo "Installing PortAudio (audio library)..."
        sudo apt-get install -y portaudio19-dev 2>/dev/null || sudo dnf install -y portaudio-devel 2>/dev/null || true
    fi
fi

# Create virtual environment
echo ""
echo "[3/4] Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate and install
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# Copy default config
echo ""
echo "[4/4] Setting up config..."
mkdir -p "$HOME/.betterflow"
if [ ! -f "$HOME/.betterflow/config.json" ]; then
    cp config.example.json "$HOME/.betterflow/config.json"
    echo "Config created at: $HOME/.betterflow/config.json"
else
    echo "Config already exists at: $HOME/.betterflow/config.json"
fi

echo ""
echo "  =========================================="
echo "   Installation complete!"
echo "  =========================================="
echo ""
echo "  To start BetterFlow:"
echo "    bash run.sh"
echo ""
echo "  Then look for the coffee cup icon in your menu bar / system tray."
echo "  Click into any text field and press Ctrl+Shift+Space to dictate."
echo ""

# macOS-specific note
if [[ "$(uname)" == "Darwin" ]]; then
    echo "  NOTE: On macOS, you'll need to grant permissions on first run:"
    echo "    - Microphone access"
    echo "    - Accessibility (for typing into other apps)"
    echo "    System Settings > Privacy & Security > [Microphone / Accessibility]"
    echo ""
fi
