// label: fit-test surround
// gen_01 · fit-test surround (voice-0c526dc0). Never edit a generation once a
// newer one exists: copy the newest gen_NN_*.scad to the next number and
// change the copy, as in ../demo_gripper.
//
// The first try-on glove: a thin closed shell around Jake's whole hand, open
// at the wrist, so he can slide his hand in and feel where it pinches or
// floats. It is built from two independent things:
//   - the hand: jake_hand.scad (measurements only; correct the hand there),
//   - the fit: the parameters below (clearance per region, wall, pose).
// The comfort volume is the hand swollen by the clearance; it is the cutout.
// Too tight somewhere: raise that region's clearance. Wrong everywhere in the
// same way: the hand model is off, fix jake_hand.scad. Neither file changes
// the other.
//
// Prints in two pieces, each in the orientation shown, no supports inside:
//   palm  - the 0.8 mm TPU palm / finger-pad layer (the only material under
//           the hand) with straight walls up to the split;
//   back  - the dome over the back of the hand and fingers, rim down.
// Both have a flange at the split: tape or clip them together for a try-on.
use <jake_hand.scad>

part = "assembly";   // assembly | palm | back | comfort | hand | parts

/* [Fit] */
clearance_palm = 2.0;      // mm of room around the palm and back of the hand
clearance_fingers = 1.5;   // around each finger
clearance_thumb = 2.0;     // around the thumb
tip_room = 3;              // extra length past each fingertip
wall = 1.2;                // three 0.4 mm perimeters
pad = 0.8;                 // palm layer: the only TPU between the hand and an object
split = 11;                // where the two pieces meet, mm above the palm surface
flange = 4;                // lip on each piece at the split, for tape or clips
flange_t = 1.2;
wrist_cut = 5;             // the glove ends this far past the wrist crease, toward the arm

/* [Pose, degrees: the try-on pose, not the hand's measurements] */
splay = [6, 0, -6, -13];   // fingers fanned a little so each gets its own sleeve
thumb_yaw = 30;            // thumb out from the index enough for its own sleeve

$fn = 28;

grow = [clearance_palm, clearance_fingers, clearance_thumb];
function plus(g, d) = [for (v = g) v + d];

module hand(g = 0) jake_hand(grow = g, tip_room = tip_room, splay = splay, thumb_yaw = thumb_yaw);
module comfort() hand(grow);
module skin() hand(plus(grow, wall));

module glove_end() translate([-200, -wrist_cut - 400, -50]) cube([400, 400, 200]);
module below(z) translate([-200, -200, -50]) cube([400, 400, z + 50]);
module above(z) translate([-200, -200, z]) cube([400, 400, 200]);

// The comfort volume seen from above, from the palm surface up to the split.
module footprint() projection() intersection() { comfort(); below(split); }
// Its cross-section at the split, where the back piece's dome starts.
module split_section() projection(cut = true) translate([0, 0, -split]) comfort();

module palm_piece()
    difference() {
        union() {
            translate([0, 0, -pad]) linear_extrude(split + pad) offset(r = wall) footprint();
            translate([0, 0, split - flange_t]) linear_extrude(flange_t) offset(r = wall + flange) footprint();
        }
        linear_extrude(split + 1) footprint();
        glove_end();
    }

module back_piece()
    difference() {
        union() {
            intersection() { skin(); above(split); }
            translate([0, 0, split]) linear_extrude(flange_t) offset(r = wall + flange) footprint();
        }
        comfort();
        translate([0, 0, split - 1]) linear_extrude(flange_t + 1.01) split_section();
        glove_end();
    }

if (part == "parts") { echo(["palm"]); echo(["back"]); }
if (part == "assembly") { color("#2b2f36") palm_piece(); color("#9aa6b8", 0.8) back_piece(); }
if (part == "palm") palm_piece();
if (part == "back") back_piece();
if (part == "comfort") comfort();
if (part == "hand") hand();
