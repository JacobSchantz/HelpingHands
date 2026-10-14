#!/usr/bin/env bash
# Regenerate every committed artifact from the .scad sources.
# STLs, PNGs and parts.json are build outputs -- never hand-edit them, just re-run this.
set -euo pipefail
cd "$(dirname "$0")"

OPENSCAD="${OPENSCAD:-/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD}"
# --viewall/--autocenter so a shape change can never silently crop the tip.
FIT="--viewall --autocenter"
SIDE="--camera=0,0,0,90,0,0,0  $FIT --projection=o --imgsize=700,1100"
ISO="--camera=0,0,0,62,0,28,0  $FIT --imgsize=950,1100"
COLOR="--colorscheme=Tomorrow"

rm -f export/*.stl render/*.png
mkdir -p export render

echo "--- STL: one per printed piece, each in its assembled position (lay it flat in the slicer) ---"
for p in upper lower pivot_plug camera_mount puck; do
    "$OPENSCAD" --render --export-format binstl -D "part=\"$p\"" -o "export/$p.stl" crow_beak.scad
done

echo "--- parts.json: the app's explode toggle reads labels, colours and offsets from here ---"
echo_file=$(mktemp -t parts).echo
"$OPENSCAD" -D 'part="parts"' -o "$echo_file" crow_beak.scad 2>/dev/null
python3 - "$echo_file" > export/parts.json <<'PY'
import json, sys
parts = []
for line in open(sys.argv[1]):
    if "PART|" not in line:
        continue
    _, key, label, colour, offset = line.strip().strip('ECHO: ').strip('"').split("|")
    parts.append({"file": key + ".stl", "name": label, "color": colour,
                  "explode": [float(v) for v in offset.split(",")]})
print(json.dumps({"parts": parts}, indent=1))
PY

echo "--- PNG ---"
"$OPENSCAD" --render -D 'part="assembly"' $SIDE $COLOR -o render/beak_closed_side.png crow_beak.scad
"$OPENSCAD" --render -D 'part="open"'     $SIDE $COLOR -o render/beak_open_side.png   crow_beak.scad
"$OPENSCAD" --render -D 'part="assembly"' $ISO  $COLOR -o render/beak_iso.png         crow_beak.scad
"$OPENSCAD" --render -D 'part="assembly"' -D 'crow_opening=14' \
    --camera=-11,0,84,90,0,0,170 --imgsize=900,780 $COLOR -o render/tip_and_notch.png  crow_beak.scad
"$OPENSCAD" --render -D 'part="tool"' --camera=-9,0,80,90,0,0,210 --imgsize=900,820 $COLOR \
    -o render/tool_in_notch.png crow_beak.scad
"$OPENSCAD" --render -D 'part="upper"' $ISO $COLOR -o render/upper.png crow_beak.scad
"$OPENSCAD" --render -D 'part="assembly"' -D 'crow_opening=18' \
    --camera=-11,0,72,90,0,0,150 --imgsize=900,780 $COLOR -o render/throat_open.png crow_beak.scad
"$OPENSCAD" --render -D 'part="armed"'    --camera=0,0,0,65,0,35,0 $FIT --imgsize=900,1000 $COLOR \
    -o render/armed_iso.png crow_beak.scad
"$OPENSCAD" --render -D 'part="handheld"' --camera=0,0,0,70,0,50,0 $FIT --imgsize=1000,1000 $COLOR \
    -o render/handheld_iso.png crow_beak.scad
"$OPENSCAD" --render -D 'part="handheld"' --camera=0,0,0,75,0,235,0 $FIT --imgsize=1000,1000 $COLOR \
    -o render/thumb_side.png crow_beak.scad
"$OPENSCAD" --render -D 'part="exploded"' --camera=0,0,0,60,0,20,0 $FIT --imgsize=1100,1000 $COLOR \
    -o render/exploded.png crow_beak.scad
"$OPENSCAD" --render -D 'part="handheld"' --camera=0,0,0,90,0,0,0  $FIT --projection=o --imgsize=900,1000 $COLOR \
    -o render/handheld_side.png crow_beak.scad
"$OPENSCAD" --render -D 'part="lower"' --camera=0,0,0,68,0,22,0 $FIT --imgsize=900,900 $COLOR \
    -o render/lower.png crow_beak.scad

echo "--- interference ---"
./check_interference.sh

echo "--- wrist budget ---"
python3 check_budget.py

ls -la export render
