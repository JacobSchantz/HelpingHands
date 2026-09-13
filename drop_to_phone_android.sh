#!/bin/bash
# Android drop — identity is pebbles-build.conf; the engine lives in Pebbles.
set -euo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
export PB_REPO="$PWD"
for r in "$HOME/pebbles-github/scripts/project_run.sh" \
         "$HOME/pebbles/scripts/project_run.sh" \
         "$HOME/testables/scripts/project_run.sh"; do
    [ -f "$r" ] && exec bash "$r" android "$@"
done
echo "❌ Pebbles engines not found (clone https://github.com/JacobSchantz/Pebbles)" >&2
exit 1
