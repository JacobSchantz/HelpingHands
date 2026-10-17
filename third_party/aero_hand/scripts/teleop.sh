#!/bin/sh
# "Jarvis, copy my hand": webcam teleop (Esc quits; --dry-run only shows tracking).
exec "$HOME/HelpingHands-tools/aero/venv/bin/python" "$(dirname "$0")/teleop.py" "$@"
