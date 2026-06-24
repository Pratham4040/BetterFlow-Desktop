"""
BetterFlow Desktop — entry point.

Run this file to start the app:
    python betterflow_desktop.py
"""

import sys
from betterflow import APP_NAME, APP_VERSION, APP_TAGLINE
from betterflow.app import BetterFlowApp


def main():
    print(f"\n  ☕  {APP_NAME} {APP_VERSION}  —  {APP_TAGLINE}\n")
    app = BetterFlowApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
