// label: flat-hand fit tray
// gen_00 · flat-hand fit tray (voice-0c526dc0, step 1). Never edit a
// generation once a newer one exists: copy the newest gen_NN_*.scad to the
// next number and change the copy, as in ../demo_gripper.
//
// The first thing to print for the Robot Glove Hand: the hand's own outline,
// fully spread, as one thin TPU pad (the future palm / finger-pad layer) with
// a low wall around it. Lay the spread hand in it: if every finger and the
// thumb drop in with a little room and nothing rides up the wall, the photo
// outline is right and the glove shell (gen_01) can be built on it. It tests
// width and finger angles only; thickness needs a side photo or measurements.
//
// The outline comes from hand_outline.scad, written by outline_from_photo.py.
// Until Jake's photo arrives it is a PLACEHOLDER large hand, not his.
include <hand_outline.scad>

part = "tray";
clearance = 1.5;   // per side between skin and wall; tighten once a print fits
wall = 1.2;        // three 0.4 mm perimeters
pad = 0.8;         // palm / finger-pad layer: the only TPU under the hand
wall_h = 8;        // enough to see whether a finger sits inside or rides up
$fn = 48;

if (len(search("PLACEHOLDER", hand_source)) > 0)
    echo("NOTE: hand_outline.scad is a PLACEHOLDER, not Jake's hand. Run outline_from_photo.py on his photo.");

module hand() polygon(hand_outline);
// Everything below the wrist line (y=0) is cut away, so the wrist end is open.
module above_wrist() intersection() { children(); translate([-500, 0]) square(1000); }

module tray() {
    linear_extrude(pad) above_wrist() offset(r = clearance + wall) hand();
    linear_extrude(pad + wall_h) above_wrist() difference() {
        offset(r = clearance + wall) hand();
        offset(r = clearance) union() { hand(); translate([-60, -20]) square([120, 21]); }
    }
}

if (part == "tray") tray();
if (part == "outline") linear_extrude(1) hand();
