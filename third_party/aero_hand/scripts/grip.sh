#!/bin/sh
# "Jarvis, grip it" / "let go": slow gentle grip (grip.sh close|release)
exec "$HOME/HelpingHands-tools/aero/venv/bin/python" "$(dirname "$0")/grip.py" "$@"
