// =============================================================================
//  hand_gripper.scad — two Generalist-style jaws and a camera, worn on the
//  fingertips or bolted to an SO-101.  (voice-6d8b9fd8, third pass)
// =============================================================================
//  What it is:
//    * two yellow JAWS on a small HUB.  Each jaw curves in to a point, like
//      Generalist's lattice fingers, and gear teeth at the pivots keep the two
//      jaws mirror images of each other;
//    * a fingertip SLEEVE on the outer face of each jaw, right behind the
//      gripping face: index + middle in one, thumb in the other.  Your finger
//      pads press on the back of the gripping faces, so closing the jaws is
//      the same motion as pinching a sheet of paper;
//    * a CAMERA bracket on the hub, looking down the jaws at the tips;
//    * for the arm only, an SO-101 MOUNT: the wrist_roll horn pattern on the
//      bottom and a cradle for the gripper servo (STS3215), whose horn bolts
//      to the finger jaw.  The gears drive the thumb jaw.
//  The hub, jaws and camera are the same parts in both uses, so the camera
//  sees the jaws from the same place in your hand and on the robot.
//
//  Frame: +Z along the jaws toward the tips, X is the direction they open
//  (finger jaw at +X, thumb jaw at -X), Y is the pivot axis (+Y is the camera
//  side).  Origin midway between the two pivots.
//
//      openscad hand_gripper.scad                       # assembly, 40 mm gape
//      openscad -D 'part="exploded"' hand_gripper.scad  # pieces pulled apart
//      openscad -D 'part="in_hand"' hand_gripper.scad   # with a ghost hand
//      openscad -D 'part="on_arm"' hand_gripper.scad    # with the SO-101 mount
//      openscad -D 'hand="L"' hand_gripper.scad         # S / M / L sleeves
// =============================================================================

part    = "assembly";  // assembly | exploded | in_hand | on_arm | hub | jaw_finger | jaw_thumb |
                       // camera | so101_mount | clash | gearclash | parts
hand    = "M";         // S | M | L — sizes the sleeves only
opening = 40;          // mm between the gripping faces at their middle
swing   = -1;          // degrees per jaw; >= 0 overrides opening and the stop (tests)
skew    = 0;           // degrees the thumb gear is turned past the finger gear (mesh test)

$fn = 48;

// ---------------------------------------------------------------- the hand ---
s         = hand == "S" ? 0.9 : hand == "L" ? 1.1 : 1.0;
finger_d  = 19.5 * s;     // index / middle, across the last joint
thumb_d   = 23 * s;
clear     = 1.6;          // added to every sleeve diameter
sleeve_wall = 2.2;
sleeve_z  = [38, 66];     // fingertip pocket, along the jaw; the cap is above it

// ------------------------------------------------------------ the mechanism ---
p         = 12;     // gear pitch radius; the pivots sit at x = ±p
gear_m    = 1.5;    // module: 16 teeth on a full circle
link_t    = 10;     // jaw thickness along Y at the pivot
cheek_t   = 5;
side_gap  = 0.4;
pin_d     = 3.3;    // M3 pivot bolts
open_max  = 30;     // degrees each jaw swings before the stop tabs meet
tab_R     = 14;     // stop tab: distance from the pivot ...
tab_r     = 2.5;    // ... and radius

// jaw profile in the XZ plane, finger jaw, closed (the thumb jaw mirrors it)
face_x    = 0.4;    // gripping face; closed jaws sit 2 * face_x apart
pad_back  = 9;      // outer face of the jaw, behind the gripping face
pad_z     = [32, 64];
tip_z     = 72;     // the point
arm_path  = [[p, 0, 7], [15, 18, 5.5], [pad_back - 4, pad_z[0] + 2, 4]];   // [x, z, r]
pad_half  = [22.5, 14.5];   // finger jaw, thumb jaw: half-width along Y
z_contact = 52;     // middle of the gripping face

// ---------------------------------------------------------------- the hub ---
y_cheek0  = link_t / 2 + side_gap;     // 5.4
y_cheek1  = y_cheek0 + cheek_t;        // 10.4
bridge_z  = [-26, -18];
hub_x     = 21;
driven_r  = 15.5;                      // cheek disc round the finger pivot (room for the horn hole)
bolt_x    = 15;                        // the two M3 bolts through the bridge, at (±bolt_x, bolt_z)
bolt_z    = -22;

// ------------------------------------------------------------------ camera ---
cam_at    = [0, 44, -34];   // board centre
cam_look  = [0, 0, 52];     // aim at the middle of the gripping faces
cam_board = 32;             // common 32 x 32 UVC board ...
cam_holes = 28;             // ... M2 holes on a 28 mm square
cam_lens  = 14;
plate_t   = 4;

// ------------------------------------------------------ SO-101 interface ---
// The stock horn pattern, copied from ../params.scad (all [STEP]):
horn_bolt_square = 9.9;   horn_centre_bore_d = 5.4;
horn_recess_d    = 24.0;  horn_recess_depth  = 6.0;
m3_clear_d = 3.2;         m3_cap_d = 6.0;
// STS3215 gripper servo envelope [GUESS — measure yours]: 45.2 x 24.7 x 35,
// output shaft 11 mm from one end.  It sits on the -Y side of the hub with
// its shaft on the finger pivot; its horn sits in the -Y cheek's horn hole.
servo_L = 45.2;  servo_W = 24.7;  servo_H = 35;  servo_shaft = 11;
horn_face_y = -link_t / 2;                        // horn top face against the jaw
servo_y0  = horn_face_y - 5.6;                    // [GUESS] case top, below the horn
servo_box = [[p - servo_W / 2, servo_y0 - servo_H, -(servo_L - servo_shaft)],
             [p + servo_W / 2, servo_y0,            servo_shaft]];
cradle_wall = 3;
cradle_gap  = 0.2;
puck_d    = 34;
puck_h    = 10;
puck_c    = [0, -8];          // wrist_roll axis in XY: the pinch line is 8 mm off it
horn_hole_d = 24.5;

// ---------------------------------------------------------------- exploded ---
// One table drives the exploded render AND the app's explode toggle (build.sh
// writes it to export/parts.json): [part, label, colour, offset mm].
PARTS = [
    ["hub",         "Hub (pivots + gears)",              "#2b2f36", [  0,   0, -25]],
    ["jaw_finger",  "Finger jaw (index + middle sleeve)", "#f2b705", [ 45,   0,  20]],
    ["jaw_thumb",   "Thumb jaw (thumb sleeve)",           "#f2b705", [-45,   0,  20]],
    ["camera",      "Camera bracket",                     "#5d6670", [  0,  45, -20]],
    ["so101_mount", "SO-101 mount + servo cradle (arm only)", "#3a4048", [  0, -50, -45]],
];

// ------------------------------------------------------- jaw angle <-> gape ---
function gape_at(a) = 2 * (p + (face_x - p) * cos(a) + z_contact * sin(a));
function angle_for(g, lo = 0, hi = 60, n = 0) =
    n > 30 ? (lo + hi) / 2
    : gape_at((lo + hi) / 2) < g ? angle_for(g, (lo + hi) / 2, hi, n + 1)
                                 : angle_for(g, lo, (lo + hi) / 2, n + 1);
theta = swing >= 0 ? swing : min(open_max, angle_for(opening));

echo(str("jaw angle ", round(theta * 10) / 10, " deg; gape at the stop ",
         round(gape_at(open_max)), " mm"));

// -------------------------------------------------------------- utilities ---
module xz(h = link_t) { rotate([90, 0, 0]) linear_extrude(h, center = true) children(); }
module along_y(x, z, r, y0, y1) { translate([x, y0, z]) rotate([-90, 0, 0]) cylinder(r = r, h = y1 - y0); }
module chain2d(pts) { for (i = [0 : len(pts) - 2]) hull() for (q = [pts[i], pts[i + 1]]) translate([q[0], q[1]]) circle(q[2]); }
module box(b) { translate(b[0]) cube(b[1] - b[0]); }
// finger jaw swings +a about the +X pivot (tip moves +X); thumb jaw mirrors
module swing_finger(a) { translate([p, 0, 0]) rotate([0, a, 0]) translate([-p, 0, 0]) children(); }
module swing_thumb(a)  { translate([-p, 0, 0]) rotate([0, -a, 0]) translate([p, 0, 0]) children(); }
// point local +Z along v
module orient(v) { rotate([0, acos(v[2] / norm(v)), atan2(v[1], v[0])]) children(); }

// --------------------------------------------------------------- the gears ---
// Straight-flanked teeth on a sector facing the other pivot.  Good enough to
// keep a hand tool symmetric; not a power transmission.
step = 360 / (2 * p / gear_m);
module gear_sector2d(offset_deg) {   // about the pivot at (+p, 0), facing -X
    circ = PI * gear_m;  add = gear_m;  ded = 1.25 * gear_m;
    translate([p, 0]) {
        intersection() {
            circle(p - ded + 0.01);
            polygon([[0, 0], for (a = [-55 : 10 : 55]) 40 * [cos(180 + a), sin(180 + a)]]);
        }
        for (k = [-3 : 3]) let(a = 180 + offset_deg + k * step)
            if (abs(a - 180) <= 50)
                rotate(a) translate([p - ded, 0])
                    polygon([[0, -circ * 0.275], [ded + add, -circ * 0.125], [ded + add, circ * 0.125], [0, circ * 0.275]]);
    }
}

// -------------------------------------------------------------------- jaws ---
// Built as the FINGER jaw, closed; the thumb jaw is its mirror in X with its
// own sleeve and its gear teeth half a tooth round.
tab_phi = open_max + acos((p - tab_r) / tab_R);   // tabs meet at open_max

module jaw_link2d(horn = false) {
    chain2d(arm_path);
    if (horn) translate([p, 0]) circle(10.2);   // room for the SO-101 horn screws
    hull() {   // stop tab: down and inward, meets its twin at open_max
        translate([p, 0]) circle(5);
        translate([p - tab_R * cos(tab_phi), -tab_R * sin(tab_phi)]) circle(tab_r);
    }
}
module jaw_pad2d() {   // the gripping face and the inward-curving point
    polygon([[face_x, pad_z[0]], [pad_back, pad_z[0] - 4], [pad_back, pad_z[1]],
             [face_x + 4, tip_z - 1], [face_x, tip_z]]);
}

// sleeve cavity centres in the (x, y) plane; the cavity just touches the pad's
// outer face, so the finger pad rests on the back of the gripping face
function sleeve_r(thumb) = ((thumb ? thumb_d : finger_d) + clear) / 2;
function sleeve_ys(thumb) = thumb ? [0] : [-1, 1] * (finger_d / 2 + 0.25);

module sleeve(thumb) {
    r  = sleeve_r(thumb);
    xc = pad_back + r;
    difference() {
        union() {
            hull() for (y = sleeve_ys(thumb)) translate([xc, y, sleeve_z[0]])
                cylinder(r = r + sleeve_wall, h = sleeve_z[1] - sleeve_z[0] + sleeve_wall);
            // web to the pad
            translate([pad_back - 1, -pad_half[thumb ? 1 : 0], sleeve_z[0]])
                cube([r, 2 * pad_half[thumb ? 1 : 0], sleeve_z[1] - sleeve_z[0] + sleeve_wall]);
        }
        hull() for (y = sleeve_ys(thumb)) translate([xc, y, sleeve_z[0] - 1])
            cylinder(r = r, h = sleeve_z[1] - sleeve_z[0] + 1);
        translate([pad_back - 0.01, -50, sleeve_z[0] - 1]) mirror([1, 0, 0]) cube([30, 100, 60]);   // keep the pad
    }
}

module jaw_body(thumb, gear = true, horn = false) {
    hw = pad_half[thumb ? 1 : 0];
    difference() {
        union() {
            xz() jaw_link2d(horn);
            if (gear) xz() gear_sector2d(thumb ? step / 2 : 0);
            // the pad, full width; a hull eases it down onto the thin link
            intersection() {   // narrows to the point above the sleeve cap
                xz(2 * hw) jaw_pad2d();
                hull() {
                    translate([-50, -hw, 0]) cube([100, 2 * hw, sleeve_z[1] + sleeve_wall]);
                    translate([-50, -5, 0]) cube([100, 10, tip_z + 1]);
                }
            }
            hull() {
                xz(2 * hw) intersection() { jaw_pad2d(); translate([0, pad_z[0] - 4]) square([20, 6]); }
                xz() intersection() { chain2d(arm_path); translate([0, 16]) square([30, 2]); }
            }
            sleeve(thumb);
        }
        along_y(p, 0, pin_d / 2, -30, 30);
        // grip ribs across the face, 0.8 deep
        for (z = [pad_z[0] + 3 : 3.5 : tip_z - 6]) translate([face_x - 1, -hw - 1, z]) cube([1.8, 2 * hw + 2, 1.4]);
        // lattice windows through the arm, Generalist-style
        for (q = [[13.6, 8], [13.2, 15.5], [10.5, 23]]) along_y(q[0], q[1], 2.1, -10, 10);
        if (horn) for (dx = [-1, 1], dz = [-1, 1])   // SO-101 horn: 4 x M3, heads on the +Y face
            translate([p + dx * horn_bolt_square / 2, 0, dz * horn_bolt_square / 2]) {
                along_y(0, 0, m3_clear_d / 2, -30, 30);
                along_y(0, 0, 2.9, link_t / 2 - 3, 30);
            }
    }
}
module jaw_finger(gear = true) { jaw_body(false, gear, horn = true); }
module jaw_thumb(gear = true)  { mirror([1, 0, 0]) jaw_body(true, gear); }

// --------------------------------------------------------------------- hub ---
// Two cheeks either side of the jaws, joined by a bridge behind the gears.
module cheek2d() {
    hull() {
        translate([-p, 0]) circle(9);
        translate([p, 0]) circle(driven_r);
        translate([-hub_x, bridge_z[0]]) square([2 * hub_x, bridge_z[1] - bridge_z[0]]);
    }
}
module hub() {
    difference() {
        union() {
            for (y = [[y_cheek0, y_cheek1], [-y_cheek1, -y_cheek0]])
                translate([0, y[1], 0]) rotate([90, 0, 0]) linear_extrude(y[1] - y[0]) cheek2d();
            translate([-hub_x, -y_cheek1, bridge_z[0]]) cube([2 * hub_x, 2 * y_cheek1, bridge_z[1] - bridge_z[0]]);
        }
        for (x = [-p, p]) along_y(x, 0, pin_d / 2, -30, 30);
        // -Y cheek: the servo horn passes through to the finger jaw (arm use)
        along_y(p, 0, horn_hole_d / 2, -y_cheek1 - 1, -y_cheek0 + 0.01);
        // +Y cheek: screwdriver access to the four horn screws
        for (dx = [-1, 1], dz = [-1, 1]) along_y(p + dx * horn_bolt_square / 2, dz * horn_bolt_square / 2, 3.2, y_cheek0 - 0.01, 30);
        // camera / mount bolts: -X goes right through, +X stops in a nut trap
        along_y(-bolt_x, bolt_z, pin_d / 2, -30, 30);
        along_y(bolt_x, bolt_z, pin_d / 2, -7, 30);
        translate([bolt_x - 3, -8.6, bridge_z[0] - 0.01]) cube([6, 2.8, bolt_z - bridge_z[0] + 3]);
    }
}

// ------------------------------------------------------------------ camera ---
cam_dir = (cam_look - cam_at) / norm(cam_look - cam_at);
module camera() {
    y0 = y_cheek1;
    difference() {
        union() {
            // plate on the +Y cheek, over the bridge bolts
            translate([-hub_x, y0, bridge_z[0]]) cube([2 * hub_x, plate_t, bridge_z[1] - bridge_z[0] + 4]);
            // two struts out to the board, between the bolt heads
            for (sx = [-1, 1]) hull() {
                translate([sx * 7, y0 + 4, bolt_z]) sphere(4);
                translate(cam_at + [sx * 12, 0, 0] - cam_dir * 4) sphere(3.5);
            }
            translate(cam_at) orient(cam_dir) translate([-cam_board / 2 - 2, -cam_board / 2 - 2, -6])
                cube([cam_board + 4, cam_board + 4, 3]);
        }
        for (sx = [-1, 1]) along_y(sx * bolt_x, bolt_z, pin_d / 2, 0, 30);
        translate(cam_at) orient(cam_dir) {
            translate([0, 0, -12]) cylinder(d = cam_lens, h = 12);
            for (dx = [-1, 1], dy = [-1, 1]) translate([dx * cam_holes / 2, dy * cam_holes / 2, -12]) cylinder(d = 2.2, h = 12);
        }
    }
}

// --------------------------------------------------------- SO-101 mount ---
// A cradle round the gripper servo on the -Y side, a flange that bolts to the
// hub (the -X bridge bolt and the thumb pivot bolt both run through it), and
// the stock wrist_roll horn pattern on the bottom.
module so101_mount() {
    b0 = servo_box[0] - [cradle_gap, cradle_gap, cradle_gap];
    b1 = servo_box[1] + [cradle_gap, 0, cradle_gap];
    w  = cradle_wall;
    floor_z = b0[2] - w;
    z_puck = floor_z - puck_h;
    hs = horn_bolt_square / 2;
    difference() {
        union() {
            // the U round the servo: back, both sides, floor
            translate([b0[0] - w, b0[1] - w, floor_z]) cube([b1[0] - b0[0] + 2 * w, w, b1[2] - floor_z]);
            for (x = [b0[0] - w, b1[0]]) translate([x, b0[1] - w, floor_z]) cube([w, b1[1] - b0[1] + w, b1[2] - floor_z]);
            // floor: under the servo and forward under the hub to carry the puck
            translate([-hub_x, b0[1] - w, floor_z]) cube([b1[0] + w + hub_x, b1[1] - b0[1] + w + 18, w]);
            // flange against the -Y cheek, -X of the servo, down to the floor
            translate([0, -y_cheek1, 0]) rotate([90, 0, 0]) linear_extrude(3.5)
                hull() {
                    translate([-p, 0]) circle(9);
                    translate([-hub_x, bridge_z[0]]) square([hub_x + b0[0], bridge_z[1] - bridge_z[0]]);
                    translate([-hub_x, floor_z]) square([hub_x + b0[0], 1]);
                }
            translate([puck_c[0], puck_c[1], z_puck]) cylinder(d = puck_d, h = puck_h + 0.01);
        }
        // horn recess, centre bore, four horn screws with heads from above
        translate([puck_c[0], puck_c[1], z_puck - 0.01]) {
            cylinder(d = horn_recess_d, h = horn_recess_depth + 0.01);
            cylinder(d = horn_centre_bore_d, h = 30);
            for (dx = [-hs, hs], dy = [-hs, hs]) translate([dx, dy, 0]) {
                cylinder(d = m3_clear_d, h = 30);
                translate([0, 0, horn_recess_depth + 2]) cylinder(d = m3_cap_d, h = 30);
            }
        }
        // bolts to the hub
        along_y(-bolt_x, bolt_z, pin_d / 2, -40, 0);
        along_y(-p, 0, pin_d / 2, -40, 0);
        // servo retaining screws through the side walls (stock: Ø2)
        for (x = [b0[0] - w - 1, b1[0] - 1], z = [b0[2] + 8, b1[2] - 8])
            translate([x, (b0[1] + b1[1]) / 2, z]) rotate([0, 90, 0]) cylinder(d = 2, h = w + 2);
        // cable out of the top end of the cradle is left open
    }
}
module servo_ghost() { color([0.1, 0.1, 0.12, 0.5]) box(servo_box); }

// -------------------------------------------------------------- ghost hand ---
// Fingertips in the sleeves; the rest of the finger runs back and out.
module ghost_hand(a) {
    xf = pad_back + sleeve_r(false);
    xt = -(pad_back + sleeve_r(true));
    knuckle = [for (y = sleeve_ys(false)) [xf + 22, y, sleeve_z[0] - 52]];
    thumb_base = [xt - 20, -14, sleeve_z[0] - 80];
    color([0.93, 0.76, 0.65, 0.45]) {
        // index + middle: tip in the sleeve, back to the knuckles
        for (i = [0 : 1]) let(y = sleeve_ys(false)[i])
            hull() { swing_finger(a) translate([xf, y, sleeve_z[1] - finger_d / 2]) sphere(finger_d / 2);
                     translate(knuckle[i]) sphere(finger_d / 2 + 0.5); }
        // thumb: tip in its sleeve, back to the base of the thumb
        hull() { swing_thumb(a) translate([xt, 0, sleeve_z[1] - thumb_d / 2 - 3]) sphere(thumb_d / 2);
                 translate([xt - 14, -6, sleeve_z[0] - 35]) sphere(thumb_d / 2 + 1); }
        hull() { translate([xt - 14, -6, sleeve_z[0] - 35]) sphere(thumb_d / 2 + 1); translate(thumb_base) sphere(16); }
        // ring + pinky curled into the palm, on the -Y side
        for (y = [-31, -49]) hull() { translate([xf + 18, y, sleeve_z[0] - 54]) sphere(8.5); translate([xf - 2, y, sleeve_z[0] - 30]) sphere(8); }
        // palm: knuckles to the base of the thumb, on the -Y side of the hub
        hull() {
            for (k = knuckle) translate(k) sphere(finger_d / 2 + 0.5);
            translate([xf + 18, -49, sleeve_z[0] - 54]) sphere(9);
            translate(thumb_base) sphere(16);
            translate([10, -40, sleeve_z[0] - 105]) sphere(22);
        }
    }
}

// --------------------------------------------------------------- assembly ---
function colour_of(q) = [for (r = PARTS) if (r[0] == q) r[2]][0];

module piece(q, a = 0) {
    color(colour_of(q))
    if      (q == "hub")         hub();
    else if (q == "jaw_finger")  swing_finger(a) jaw_finger();
    else if (q == "jaw_thumb")   swing_thumb(a) jaw_thumb();
    else if (q == "camera")      camera();
    else if (q == "so101_mount") so101_mount();
}

module assembly(a, explode = 0, arm = true) {
    for (r = PARTS) if (arm || r[0] != "so101_mount") translate(explode * r[3]) piece(r[0], a);
}

// jaw bodies without their gear teeth, and everything they must never touch
module jaws_nogear(a) { swing_finger(a) jaw_finger(false); swing_thumb(a) jaw_thumb(false); }
module fixed_parts() { hub(); camera(); so101_mount(); box(servo_box); }

if      (part == "assembly") assembly(theta);
else if (part == "exploded") assembly(theta, 1);
else if (part == "in_hand")  { assembly(theta, arm = false); ghost_hand(theta); }
else if (part == "on_arm")   { assembly(theta); servo_ghost(); }
else if (part == "clash") {
    intersection() { swing_finger(theta) jaw_finger(false); swing_thumb(theta) jaw_thumb(false); }
    intersection() { jaws_nogear(theta); fixed_parts(); }
}
else if (part == "fitclash") {   // the fixed parts must not overlap each other
    intersection() { hub(); camera(); }
    intersection() { hub(); so101_mount(); }
    intersection() { hub(); box(servo_box); }
    intersection() { camera(); so101_mount(); }
    intersection() { so101_mount(); box(servo_box); }
}
else if (part == "gearclash")   // the teeth themselves, full jaws
    intersection() { swing_finger(theta) jaw_finger(); swing_thumb(theta + skew) jaw_thumb(); }
else if (part == "parts") for (r = PARTS) echo(str("PART|", r[0], "|", r[1], "|", r[2], "|", r[3][0], ",", r[3][1], ",", r[3][2]));
else piece(part, 0);   // printable pieces export closed, in assembly position
