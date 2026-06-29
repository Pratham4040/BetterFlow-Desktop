"""
BetterFlow Desktop — entry point.

Run this file to start the app:
    python betterflow_desktop.py
"""

import sys
from betterflow.app import BetterFlowApp


def main():
    app = BetterFlowApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye! ☕")
        sys.exit(0)


if __name__ == "__main__":
    main()
