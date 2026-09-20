#!/usr/bin/env bash
# Regenerate every committed artifact from the .scad sources.
# STLs and PNGs are build outputs -- never hand-edit them, just re-run this.
set -euo pipefail
cd "$(dirname "$0")"

OPENSCAD="${OPENSCAD:-/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD}"
# --viewall/--autocenter so a shape change can never silently crop the tip.
FIT="--viewall --autocenter"
SIDE="--camera=0,0,0,90,0,0,0  $FIT --projection=o --imgsize=700,1100"
ISO="--camera=0,0,0,62,0,28,0  $FIT --imgsize=950,1100"
COLOR="--colorscheme=Tomorrow"

mkdir -p export render

echo "--- STL ---"
for p in assembly upper lower; do
    "$OPENSCAD" --render --export-format binstl -D "part=\"$p\"" -o "export/$p.stl" crow_beak.scad
done
"$OPENSCAD" --render --export-format binstl -D 'part="assembly"' -D 'crow_opening=25' \
    -o export/assembly_open.stl crow_beak.scad

echo "--- PNG ---"
"$OPENSCAD" --render -D 'part="assembly"' $SIDE $COLOR -o render/beak_closed_side.png crow_beak.scad
"$OPENSCAD" --render -D 'part="open"'     $SIDE $COLOR -o render/beak_open_side.png   crow_beak.scad
"$OPENSCAD" --render -D 'part="assembly"' $ISO  $COLOR -o render/beak_iso.png         crow_beak.scad
"$OPENSCAD" --render -D 'part="assembly"' -D 'crow_opening=14' \
    --camera=-11,0,84,90,0,0,170 --imgsize=900,780 $COLOR -o render/tip_and_notch.png  crow_beak.scad
"$OPENSCAD" --render -D 'part="tool"' --camera=-9,0,80,90,0,0,210 --imgsize=900,820 $COLOR \
    -o render/tool_in_notch.png crow_beak.scad
"$OPENSCAD" --render -D 'part="upper"' $ISO $COLOR -o render/upper.png crow_beak.scad
"$OPENSCAD" --render -D 'part="lower"' --camera=0,0,0,68,0,22,0 $FIT --imgsize=900,900 $COLOR \
    -o render/lower.png crow_beak.scad

echo "--- interference ---"
./check_interference.sh

ls -la export render
