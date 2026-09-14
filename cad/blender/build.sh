#!/bin/sh
# Regenerate every artifact in cad/blender/out/ from so101_gripper.py.
# Run from the repo root.  Nothing in out/ should ever be hand-edited.
set -e
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
"$BLENDER" --background --python cad/blender/so101_gripper.py -- \
    --out cad/blender/out "$@"
