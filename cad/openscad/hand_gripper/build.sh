#!/usr/bin/env bash
# Regenerate every committed artifact from hand_gripper.scad.
# STLs and PNGs are build outputs -- never hand-edit them, just re-run this.
set -euo pipefail
cd "$(dirname "$0")"

OPENSCAD="${OPENSCAD:-/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD}"
FIT="--viewall --autocenter"
COLOR="--colorscheme=Tomorrow"
SIDE="--camera=0,0,0,90,0,180,0 $FIT --projection=o --imgsize=1100,700"

mkdir -p export render

echo "--- STL ---"
for p in upper lower pads; do
    "$OPENSCAD" --render --export-format binstl -D "part=\"$p\"" -o "export/$p.stl" hand_gripper.scad
done
"$OPENSCAD" --render --export-format binstl -o export/assembly.stl hand_gripper.scad

echo "--- PNG ---"
"$OPENSCAD" --render -D 'part="in_hand"' -D opening=45 --camera=0,0,0,65,0,215,0 $FIT --imgsize=1100,900 $COLOR \
    -o render/in_hand_thumb_side.png hand_gripper.scad
"$OPENSCAD" --render -D 'part="in_hand"' -D opening=45 --camera=0,0,0,65,0,35,0 $FIT --imgsize=1100,900 $COLOR \
    -o render/in_hand_pinky_side.png hand_gripper.scad
"$OPENSCAD" --render -D 'part="assembly"' -D opening=60 $SIDE $COLOR -o render/open_side.png   hand_gripper.scad
"$OPENSCAD" --render -D 'part="assembly"'                $SIDE $COLOR -o render/closed_side.png hand_gripper.scad
"$OPENSCAD" --render -D 'part="assembly"' -D opening=30 --camera=0,0,0,120,0,200,0 $FIT --imgsize=1100,900 $COLOR \
    -o render/from_below.png hand_gripper.scad
"$OPENSCAD" --render -D 'part="upper"' --camera=0,0,0,90,0,270,0 $FIT --imgsize=900,700 $COLOR \
    -o render/finger_slot_rear.png hand_gripper.scad

echo "--- interference: the jaws must never touch each other except at the pads ---"
fail=0
clash_stl=$(mktemp -t clash).stl
for h in S M L; do for deg in 0.1 7 14 21 27; do
    out=$("$OPENSCAD" --render --export-format binstl -D "hand=\"$h\"" -D 'part="clash"' -D "swing=$deg" \
          -o "$clash_stl" hand_gripper.scad 2>&1 || true)
    if grep -q "top level object is empty" <<<"$out"; then echo "  $h @ $deg deg: clear"
    else echo "  $h @ $deg deg: CLASH"; fail=1; fi
done; done
# and the open stop must actually stop it: one degree past the stop has to clash
out=$("$OPENSCAD" --render --export-format binstl -D 'part="clash"' -D 'swing=29' \
      -o "$clash_stl" hand_gripper.scad 2>&1 || true)
if grep -q "top level object is empty" <<<"$out"; then echo "  open stop: MISSING"; fail=1
else echo "  open stop: catches the thumb jaw at 28 deg"; fi
[ $fail -eq 0 ] || { echo "interference check failed"; exit 1; }

ls -la export render
