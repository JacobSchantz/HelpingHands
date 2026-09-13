#!/usr/bin/env bash
# Regenerate every committed artifact from the .scad sources.
# STLs and PNGs are build outputs -- never hand-edit them, just re-run this.
set -euo pipefail
cd "$(dirname "$0")"

OPENSCAD="${OPENSCAD:-/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD}"
ISO="--camera=-4,0,52,62,0,28,330 --imgsize=1000,1100"
SIDE="--camera=-4,0,52,90,0,0,300 --imgsize=800,1100"
COLOR="--colorscheme=Tomorrow"

mkdir -p export render

echo "--- STL ---"
for p in assembly fixed_jaw moving_jaw; do
    "$OPENSCAD" --render --export-format binstl -D "part=\"$p\"" -o "export/$p.stl" gripper.scad
done

echo "--- PNG ---"
"$OPENSCAD" --render -D 'part="assembly"'   $ISO  $COLOR -o render/gripper_closed.png gripper.scad
"$OPENSCAD" --render -D 'part="open"'       $ISO  $COLOR -o render/gripper_open.png   gripper.scad
"$OPENSCAD" --render -D 'part="assembly"'   $SIDE $COLOR -o render/gripper_side.png   gripper.scad
"$OPENSCAD" --render -D 'part="fixed_jaw"'  --camera=0,0,50,62,0,25,320 --imgsize=1000,1000 $COLOR -o render/fixed_jaw.png  gripper.scad
"$OPENSCAD" --render -D 'part="moving_jaw"' --camera=0,-36,0,62,0,25,260 --imgsize=1000,900 $COLOR -o render/moving_jaw.png gripper.scad

ls -la export render
