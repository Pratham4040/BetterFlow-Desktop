#!/usr/bin/env bash
# BetterFlow Desktop — macOS / Linux launcher
# Run with: bash run.sh

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "BetterFlow is not installed. Running installer first..."
    bash install.sh
    exit $?
fi

source .venv/bin/activate
python betterflow_desktop.py
