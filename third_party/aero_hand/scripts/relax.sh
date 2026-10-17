#!/bin/sh
# "Jarvis, relax the hand": zero torque on every servo
exec "$HOME/HelpingHands-tools/aero/venv/bin/python" "$(dirname "$0")/relax.py" "$@"
