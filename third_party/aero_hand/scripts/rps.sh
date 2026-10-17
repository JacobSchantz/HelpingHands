#!/bin/sh
# "Jarvis, rock paper scissors": play the hand on camera (Esc quits; --dry-run leaves the hand still).
exec "$HOME/HelpingHands-tools/aero/venv/bin/python" "$(dirname "$0")/rps.py" "$@"
