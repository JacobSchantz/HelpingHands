#!/bin/sh
# "Jarvis, record" / "replay": teach the hand by moving it (teach.py record | replay [take|last]).
exec "$HOME/HelpingHands-tools/aero/venv/bin/python" "$(dirname "$0")/teach.py" "$@"
