#!/usr/bin/env bash
# Regenerate every committed artifact from hand_gripper.scad.
# STLs, PNGs and parts.json are build outputs -- never hand-edit them, just re-run this.
set -euo pipefail
cd "$(dirname "$0")"

OPENSCAD="${OPENSCAD:-/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD}"
FIT="--viewall --autocenter"
COLOR="--colorscheme=Tomorrow"

rm -rf export/*.stl render/*.png
mkdir -p export render

echo "--- STL: one per piece, each in its assembled position (lay it flat in the slicer) ---"
PIECES="hub jaw_finger jaw_thumb camera so101_mount"
for p in $PIECES; do
    "$OPENSCAD" --render --export-format binstl -D "part=\"$p\"" -o "export/$p.stl" hand_gripper.scad 2>/dev/null
done

echo "--- parts.json: the app's explode toggle reads labels, colours and offsets from here ---"
echo_file=$(mktemp -t parts).echo
"$OPENSCAD" -D 'part="parts"' -o "$echo_file" hand_gripper.scad 2>/dev/null
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
"$OPENSCAD" --render -D 'part="in_hand"' --camera=0,0,0,62,0,215,0 $FIT --imgsize=1100,900 $COLOR \
    -o render/in_hand.png hand_gripper.scad 2>/dev/null
"$OPENSCAD" --render -D 'part="on_arm"' --camera=0,0,0,65,0,35,0 $FIT --imgsize=1100,900 $COLOR \
    -o render/on_arm.png hand_gripper.scad 2>/dev/null
"$OPENSCAD" --render -D 'part="exploded"' --camera=0,0,0,65,0,35,0 $FIT --imgsize=1100,900 $COLOR \
    -o render/exploded.png hand_gripper.scad 2>/dev/null
"$OPENSCAD" --render -D 'part="in_hand"' --camera=0,0,0,90,0,0,0 $FIT --projection=o --imgsize=1100,900 $COLOR \
    -o render/pinch_front.png hand_gripper.scad 2>/dev/null
"$OPENSCAD" --render -D 'part="in_hand"' -D 'opening=0' --camera=0,0,0,90,0,0,0 $FIT --projection=o --imgsize=1100,900 $COLOR \
    -o render/pinch_closed.png hand_gripper.scad 2>/dev/null

echo "--- interference: jaws never touch each other, the hub, the camera, the mount or the servo ---"
fail=0
clash_stl=$(mktemp -t clash).stl
clear_at() {   # hand, degrees, [part, skew]
    out=$("$OPENSCAD" --render --export-format binstl -D "hand=\"$1\"" -D "part=\"${3:-clash}\"" -D "swing=$2" \
          -D "skew=${4:-0}" -o "$clash_stl" hand_gripper.scad 2>&1 || true)
    grep -q "top level object is empty" <<<"$out"
}
for h in S M L; do for deg in 0 7 14 21 29.5; do
    if clear_at "$h" "$deg"; then echo "  $h @ $deg deg: clear"; else echo "  $h @ $deg deg: CLASH"; fail=1; fi
done; done
if clear_at M 0 fitclash; then echo "  hub, camera, mount and servo: no overlap"
else echo "  hub, camera, mount and servo OVERLAP"; fail=1; fi
if clear_at M 31.5 gearclash; then echo "  open stop: MISSING"; fail=1
else echo "  open stop: the tabs meet at 30 deg"; fi
# the gear teeth roll through without binding, and are engaged: turning one
# jaw 3 degrees without the other has to jam them
for deg in 0 7 14 21 29.5; do
    if clear_at M "$deg" gearclash; then :; else echo "  gears bind at $deg deg"; fail=1; fi
    if clear_at M "$deg" gearclash 3; then echo "  gears slip at $deg deg"; fail=1; fi
done
[ $fail -eq 0 ] && echo "  gears: mesh 0-29.5 deg, backlash under 3 deg"
[ $fail -eq 0 ] || { echo "interference check failed"; exit 1; }

ls -la export render
