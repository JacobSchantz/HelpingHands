#!/bin/sh
# "Jarvis peace" etc. — move the hand to a named pose (pose.sh --list for names).
exec "$HOME/HelpingHands-tools/aero/venv/bin/python" "$(dirname "$0")/pose.py" "$@"
