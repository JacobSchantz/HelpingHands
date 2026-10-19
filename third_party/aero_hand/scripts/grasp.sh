#!/bin/sh
# Timed, filmed grasp from a recorded posture, with monitored load and heat.
exec "$HOME/HelpingHands-tools/aero/venv/bin/python" "$(dirname "$0")/grasp_trial.py" "$@"
