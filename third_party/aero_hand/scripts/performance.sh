#!/bin/sh
# "Run our hand performance" — song first, then the routine.
exec "$HOME/HelpingHands-tools/aero/venv/bin/python" "$(dirname "$0")/performance.py" "$@"
