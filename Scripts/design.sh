#!/usr/bin/env bash
# design.sh <name> — bring the Helping Hands Mac app forward, full screen, on
# that design: web concept on one side, OpenSCAD STL on the other, live.
# The voice session runs this for "work on <design>". Names are fuzzy:
# "gripper" is the newest gripper generation, "glove hand", "gripper gen 0".
#
#   design.sh gripper
#   design.sh --list
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
registry="$repo/cad/compare/designs.py"

if [[ $# -eq 0 || "$1" == "--list" ]]; then
    python3 "$registry"
    exit 0
fi

id="$(python3 "$registry" --match "$*" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')"
open "helpinghands://designs/$id"
echo "Opened $id"
