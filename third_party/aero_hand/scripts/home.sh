#!/bin/sh
# "Jarvis, home the hand" — runs the firmware homing on all seven servos.
exec "$HOME/HelpingHands-tools/aero/venv/bin/python" "$(dirname "$0")/home.py" "$@"
