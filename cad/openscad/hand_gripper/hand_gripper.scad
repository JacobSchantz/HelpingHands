// =============================================================================
//  hand_gripper.scad — a wearable pincer modelled on Generalist AI's human
//  data-collection gripper.  (voice-6d8b9fd8)
// =============================================================================
//  What Generalist's device looks like (photo of a data collector wearing two,
//  x.com/DominiqueCAPaul/status/2040765175779778585, and their robot-side
//  twins in generalistai.com/blog/gen-1 "box folding handheld"):
//    * a black SPINE bar strapped along the back of the hand,
//    * a HUB under its front end that the two fingers pivot from,
//    * two rigid finger LINKS hanging down: index+middle ride in a loop on the
//      front one, the thumb in a loop on the rear one, so the hand drives the
//      jaws both ways (pinch closes, spread opens, no spring),
//    * swappable yellow lattice TIPS on the links,
//    * a camera that sees both tips (the gape is read from the image).
//
//  Every piece is its own print and its own STL, and every joint is a
//  standard one, so the pieces work on their own and snap back together:
//    spine   — dovetail slot for the hub, strap pad, camera clip rail
//    hub     — dovetail tongue on top, two M3 pivots, fiducial pocket
//    link_*  — gear sector (keeps the jaws symmetric), digit loop, tip socket
//    tip_*   — tongue + M3 cross-pin, swap for other tip shapes
//    camera  — C-clip that snaps onto the spine bar anywhere along it
//  Pull the hub off the spine and hub+links+tips is a plain hand pincer; the
//  spine alone is a camera handle.
//
//  Frame (right hand, palm down):  +X forward along the forearm toward the
//  hub, +Z up, +Y toward the thumb side.  The origin is midway between the two
//  pivots; the pivot axes run along Y; the jaws open and close along X.
//
//      openscad hand_gripper.scad                       # assembly, 40 mm gape
//      openscad -D 'part="exploded"' hand_gripper.scad  # the pieces pulled apart
//      openscad -D 'part="hub"' hand_gripper.scad       # one printable piece
//      openscad -D 'hand="L"' hand_gripper.scad         # S / M / L hands
// =============================================================================

part    = "assembly";  // assembly | exploded | in_hand | spine | hub | link_front |
                       // link_thumb | tip_front | tip_thumb | camera | clash | gearclash | parts
hand    = "M";         // S | M | L — or edit the measured numbers below
handed  = "right";     // "left" mirrors everything
opening = 40;          // mm between the tip pads
swing   = -1;          // degrees per jaw; >= 0 overrides opening and the stop (tests)
skew    = 0;           // degrees the thumb gear is turned past the front one (mesh test)

$fn = 48;

// ---------------------------------------------------------------- the hand ---
s         = hand == "S" ? 0.9 : hand == "L" ? 1.1 : 1.0;
finger_d  = [19.0, 19.5, 18.5, 16.5] * s;   // index .. pinky, across the PIP joint
finger_len = [70,  78,   73,   58  ] * s;   // knuckle -> fingertip
thumb_d   = 23 * s;
clear     = 1.6;                            // added to every loop diameter

// ------------------------------------------------------------ the mechanism ---
pitch_r   = 10;     // gear pitch radius; the pivots sit 2 * pitch_r apart
gear_m    = 1.25;   // module: 16 teeth on a full circle
link_t    = 10;     // every link, gear and tab is this thick along Y
cheek_t   = 5;      // hub cheeks either side of the links
side_gap  = 0.4;
pin_d     = 3.3;    // M3 pivot bolts, M3 tip cross-pins
open_max  = 22;     // degrees each jaw swings before the stop tabs meet
tab_R     = 14;     // stop tab: distance from the pivot ...
tab_r     = 2.5;    // ... and radius
loop_wall = 2.4;
loop_h    = 12;     // loops are this tall along the digit

// where the digits ride, closed pose (the loops are built around these)
x_digit   = 22;                                   // ± along X
fr        = (max(finger_d[0], finger_d[1]) + clear) / 2;
tr        = (thumb_d + clear) / 2;
y_index   = -(link_t / 2 + 1.5 + loop_wall + fr);
y_middle  = y_index - (finger_d[0] + finger_d[1]) / 2 - 0.5;
y_thumb   = -(link_t / 2 + 1.5 + loop_wall + tr);
z_loop_f  = -55;
z_loop_t  = -66;

// arm and tip paths in the XZ plane (front link; the thumb link is mirrored)
arm_path  = [[pitch_r, 0, 7], [20, -35, 6], [24, -78, 6]];   // [x, z, r]
z_socket  = -84;                                            // arm ends, tip starts
tip_path  = [[24, -91, 6], [18, -106, 5], [8, -117, 4.5], [4, -122, 4], [3.6, -132, 3.4]];
pad_x     = 0.3;    // tip contact face; closed tips sit 2 * pad_x apart
z_contact = -126;   // middle of the contact pad

// ------------------------------------------------------------------- spine ---
bar_r     = 11;     // the black bar, Ø22
bar_y     = -14;    // over the index metacarpal
bar_z     = 40;
bar_x     = [-120, 40];
hub_x     = 22;     // hub is ±hub_x along X
cheek_bot = -9;
bridge_z  = [18, 24];
dove      = [12, 16, 6];   // tongue: bottom width, top width, height
hand_top  = -14;    // back of the hand under the strap pad
pad_x0    = -112;
pad_x1    = -56;

// ------------------------------------------------------------------ camera ---
cam_at    = [12, 62, -22];     // board centre
cam_look  = [0, 0, -110];      // aim between the tips
cam_board = 32;                // common 32 x 32 UVC board ...
cam_holes = 28;                // ... M2 holes on a 28 mm square
cam_lens  = 14;
clip_x    = [27, 39];

// ---------------------------------------------------------------- exploded ---
// One table drives the exploded render AND the app's explode toggle (build.sh
// writes it to export/parts.json): [part, label, colour, offset mm].
PARTS = [
    ["spine",      "Spine + strap pad",       "#2b2f36", [  0,   0,  55]],
    ["camera",     "Camera clip",             "#5d6670", [ 25,  45,  55]],
    ["hub",        "Hub (pivots + fiducial)", "#1d2024", [  0,   0,  20]],
    ["link_front", "Finger link",             "#3a4048", [ 40,   0,  -5]],
    ["link_thumb", "Thumb link",              "#3a4048", [-40,   0,  -5]],
    ["tip_front",  "Finger tip (TPU)",        "#f2b705", [ 60,   0, -35]],
    ["tip_thumb",  "Thumb tip (TPU)",         "#f2b705", [-60,   0, -35]],
];

// ------------------------------------------------------- jaw angle <-> gape ---
// The contact point swings about its pivot; gape = 2 * its x.
function gape_at(a) = 2 * (pitch_r + (pad_x - pitch_r) * cos(a) - z_contact * sin(a));
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
module along_x(y, z, r, x0, x1) { translate([x0, y, z]) rotate([0, 90, 0]) cylinder(r = r, h = x1 - x0); }
module chain2d(pts) { for (i = [0 : len(pts) - 2]) hull() for (p = [pts[i], pts[i + 1]]) translate([p[0], p[1]]) circle(p[2]); }
module mirror_hand() { if (handed == "left") mirror([0, 1, 0]) children(); else children(); }
module mirror_x() { mirror([1, 0, 0]) children(); }
// front pieces swing -theta about the +X pivot, thumb pieces +theta about -X
module swing_front(a) { translate([pitch_r, 0, 0]) rotate([0, -a, 0]) translate([-pitch_r, 0, 0]) children(); }
module swing_thumb(a) { translate([-pitch_r, 0, 0]) rotate([0, a, 0]) translate([pitch_r, 0, 0]) children(); }

// --------------------------------------------------------------- the gears ---
// Straight-flanked teeth on a sector facing the other pivot.  Good enough to
// keep a hand tool symmetric; not a power transmission.
module gear_sector2d(centre_deg, offset_deg) {   // about the pivot at (+pitch_r, 0)
    circ   = PI * gear_m;
    add    = gear_m;
    ded    = 1.25 * gear_m;
    step   = 360 / (2 * pitch_r / gear_m);
    w_root = circ * 0.55;
    w_tip  = circ * 0.25;
    translate([pitch_r, 0]) {
        intersection() {
            circle(pitch_r - ded + 0.01);
            polygon([[0, 0], for (a = [-50 : 10 : 50]) 30 * [cos(centre_deg + a), sin(centre_deg + a)]]);
        }
        for (k = [-2 : 2]) let(a = centre_deg + offset_deg + k * step)
            if (abs(a - centre_deg) <= 46)
                rotate(a) translate([pitch_r - ded, 0])
                    polygon([[0, -w_root / 2], [ded + add, -w_tip / 2], [ded + add, w_tip / 2], [0, w_root / 2]]);
    }
}

// ------------------------------------------------------------------- links ---
// Built as the FRONT link in the closed pose; the thumb link mirrors it in X.
tab_phi = open_max + acos((pitch_r - tab_r) / tab_R);   // tabs meet at open_max

module link_body2d() {
    chain2d(arm_path);
    // stop tab: up and inward, meets its twin when both jaws are at open_max
    hull() {
        translate([pitch_r, 0]) circle(5);
        translate([pitch_r - tab_R * cos(tab_phi), tab_R * sin(tab_phi)]) circle(tab_r);
    }
}

module link_arm(gear = true) {
    difference() {
        union() {
            xz() link_body2d();
            if (gear) xz() gear_sector2d(180, 0);
        }
        along_y(pitch_r, 0, pin_d / 2, -20, 20);
        // tip socket: tongue pocket + cross-pin
        translate([24 - 4.2, -3.2, z_socket - 1]) cube([8.4, 6.4, 15]);
        along_y(24, z_socket + 7, pin_d / 2, -20, 20);
    }
}

module digit_loop(x, z, centres, r) {
    difference() {
        union() {
            hull() for (y = centres) translate([x, y, z - loop_h / 2]) cylinder(r = r + loop_wall, h = loop_h);
            // web back to the arm
            translate([x - 6, max(centres) + r - 1, z - loop_h / 2]) cube([12, -max(centres) - r + 1, loop_h]);
        }
        hull() for (y = centres) translate([x, y, z - loop_h]) cylinder(r = r, h = 2 * loop_h);
    }
}

module link_front(gear = true) {
    link_arm(gear);
    digit_loop(x_digit, z_loop_f, [y_index, y_middle], fr);
}

module link_thumb(gear = true) {
    // the thumb gear's teeth sit half a tooth round from the front gear's
    mirror_x() difference() {
        union() {
            xz() link_body2d();
            if (gear) xz() gear_sector2d(180, 360 / (2 * pitch_r / gear_m) / 2);
        }
        along_y(pitch_r, 0, pin_d / 2, -20, 20);
        translate([24 - 4.2, -3.2, z_socket - 1]) cube([8.4, 6.4, 15]);
        along_y(24, z_socket + 7, pin_d / 2, -20, 20);
    }
    digit_loop(-x_digit, z_loop_t, [y_thumb], tr);
}

// -------------------------------------------------------------------- tips ---
// Generalist's tips are yellow, curved and perforated.  This one is TPU with
// a hex lattice cut through it so it gives a little on contact.
module tip_profile2d() {
    intersection() {
        union() {
            chain2d(tip_path);
            translate([24 - 6, z_socket - 8]) square([12, 8]);
        }
        translate([pad_x, -200]) square([100, 200 + z_socket]);   // flat contact face, flat top
    }
}

module hex_grid2d(r, pitch) {
    for (i = [-6 : 6], j = [-12 : 2]) translate([i * pitch + (j % 2) * pitch / 2, -80 + j * pitch * 0.866])
        circle(r, $fn = 6);
}

module tip_front() {
    difference() {
        union() {
            xz(link_t) difference() {
                tip_profile2d();
                intersection() { offset(-1.8) tip_profile2d(); hex_grid2d(1.9, 5.4); }
            }
            translate([24 - 4, -3, z_socket - 0.5]) cube([8, 6, 14.5]);   // tongue
        }
        along_y(24, z_socket + 7, pin_d / 2, -20, 20);
    }
}
module tip_thumb() { mirror_x() tip_front(); }

// --------------------------------------------------------------------- hub ---
module dovetail2d(grow = 0) {
    polygon([[-dove[0] / 2 - grow, -0.01], [dove[0] / 2 + grow, -0.01],
             [dove[1] / 2 + grow, dove[2] + grow], [-dove[1] / 2 - grow, dove[2] + grow]]);
}

y_cheek0 = link_t / 2 + side_gap;
y_cheek1 = y_cheek0 + cheek_t;

module hub() {
    difference() {
        union() {
            for (sy = [-1, 1]) hull() {
                for (x = [-pitch_r, pitch_r]) along_y(x, 0, -cheek_bot, sy > 0 ? y_cheek0 : -y_cheek1, sy > 0 ? y_cheek1 : -y_cheek0);
                translate([-hub_x, sy > 0 ? y_cheek0 : -y_cheek1, 8]) cube([2 * hub_x, cheek_t, bridge_z[1] - 8]);
            }
            translate([-hub_x, -y_cheek1, bridge_z[0]]) cube([2 * hub_x, 2 * y_cheek1, bridge_z[1] - bridge_z[0]]);
            // tongue, along X
            translate([-hub_x, 0, bridge_z[1]]) rotate([90, 0, 90]) linear_extrude(2 * hub_x) dovetail2d();
        }
        for (x = [-pitch_r, pitch_r]) along_y(x, 0, pin_d / 2, -30, 30);
        along_y(0, bridge_z[1] + 3, pin_d / 2, -30, 30);              // lock pin
        // fiducial pocket on the camera side: a printed AprilTag sticker
        translate([-8, y_cheek1 - 0.6, 0]) cube([16, 1, 16]);
    }
}

// ------------------------------------------------------------------- spine ---
module spine() {
    difference() {
        union() {
            along_x(bar_y, bar_z, bar_r, bar_x[0], bar_x[1]);
            // front boss the hub hangs from
            hull() {
                along_x(bar_y, bar_z, bar_r, -hub_x - 2, hub_x + 2);
                translate([-hub_x - 2, -y_cheek1, bridge_z[1]]) cube([2 * hub_x + 4, 2 * y_cheek1, 4]);
            }
            // strap pad on the back of the hand, and the web up to the bar
            translate([pad_x0, -64 * s, hand_top]) cube([pad_x1 - pad_x0, 64 * s, 4]);
            hull() {
                translate([pad_x0 + 8, bar_y - 6, hand_top]) cube([pad_x1 - pad_x0 - 16, 12, 4]);
                along_x(bar_y, bar_z, bar_r * 0.8, pad_x0 + 14, pad_x1 - 14);
            }
        }
        // dovetail slot, open at the front, stops 0.3 short of the rear
        translate([-hub_x - 0.3, 0, bridge_z[1] - 0.01]) rotate([90, 0, 90])
            linear_extrude(2 * hub_x + 30) dovetail2d(0.25);
        along_y(0, bridge_z[1] + 3, pin_d / 2, -40, 40);              // lock pin
        // lightening window through the web
        translate([pad_x0 + 22, -50, hand_top + 10]) cube([pad_x1 - pad_x0 - 44, 100, 16]);
        // strap slots, 25 mm strap
        for (y = [-60 * s, -4]) translate([(pad_x0 + pad_x1) / 2 - 13.5, y - 2, hand_top - 1]) cube([27, 4, 10]);
    }
}

// ------------------------------------------------------------------ camera ---
// A C-clip that snaps over the bar, an arm out to the thumb side, and a plate
// for a 32 mm UVC board looking at the tips from the side, so the image shows
// the gape directly (and the hub's fiducial gives the pose).
cam_dir = (cam_look - cam_at) / norm(cam_look - cam_at);
module camera() {
    clip_r = bar_r + 0.15;
    difference() {
        union() {
            along_x(bar_y, bar_z, clip_r + 3, clip_x[0], clip_x[1]);
            hull() {
                translate([(clip_x[0] + clip_x[1]) / 2, bar_y + clip_r, bar_z]) sphere(4);
                translate([(clip_x[0] + clip_x[1]) / 2, cam_at[1] - 8, bar_z]) sphere(4);
            }
            hull() {
                translate([(clip_x[0] + clip_x[1]) / 2, cam_at[1] - 8, bar_z]) sphere(4);
                translate(cam_at - cam_dir * 6) sphere(4);
            }
            translate(cam_at) orient(cam_dir) translate([-cam_board / 2 - 2, -cam_board / 2 - 2, -6])
                cube([cam_board + 4, cam_board + 4, 3]);
        }
        along_x(bar_y, bar_z, clip_r, clip_x[0] - 1, clip_x[1] + 1);
        // snap opening on the underside, 75 % of the bar diameter
        translate([clip_x[0] - 1, bar_y - bar_r * 0.75, bar_z - 2 * bar_r]) cube([clip_x[1] - clip_x[0] + 2, 1.5 * bar_r, 2 * bar_r]);
        translate(cam_at) orient(cam_dir) {
            translate([0, 0, -10]) cylinder(d = cam_lens, h = 10);
            for (dx = [-1, 1], dy = [-1, 1]) translate([dx * cam_holes / 2, dy * cam_holes / 2, -10]) cylinder(d = 2.2, h = 10);
        }
    }
}
// point local +Z along v
module orient(v) {
    b = acos(v[2]);
    c = atan2(v[1], v[0]);
    rotate([0, b, c]) children();
}

// -------------------------------------------------------------- ghost hand ---
module ghost_hand(a) {
    color([0.93, 0.76, 0.65, 0.45]) {
        // palm and back of the hand, fingers hang down from the knuckles at x_digit
        hull() {
            translate([-100, y_middle - 40 * s, hand_top - 32]) cube([40, 40 * s + y_index - y_middle + fr, 32]);
            for (y = [y_index, y_middle, y_middle - 19 * s, y_middle - 37 * s])
                translate([x_digit - 4, y, hand_top - 14]) rotate([0, 90, 0]) cylinder(r = 14, h = 6);
        }
        // index + middle follow the front link
        swing_front(a) for (i = [0 : 1]) let(y = [y_index, y_middle][i])
            hull() { translate([x_digit, y, hand_top - 12]) sphere(finger_d[i] / 2); translate([x_digit, y, hand_top - 12 - finger_len[i]]) sphere(finger_d[i] / 2 * 0.9); }
        // ring + pinky curled into the palm
        for (i = [2 : 3]) let(y = y_middle - (i - 1) * 18.5 * s)
            hull() { translate([x_digit - 2, y, hand_top - 12]) sphere(finger_d[i] / 2); translate([x_digit - 30, y, hand_top - 45]) sphere(finger_d[i] / 2); }
        // thumb from under the palm, down through its loop
        hull() { translate([-70, y_thumb - 4, hand_top - 30]) sphere(tr + 2); translate([-x_digit - 4, y_thumb, hand_top - 40]) sphere(tr - 1); }
        swing_thumb(a) hull() { translate([-x_digit, y_thumb, hand_top - 40]) sphere(tr - 1); translate([-x_digit, y_thumb, -92]) sphere(tr - 2); }
    }
}

// --------------------------------------------------------------- assembly ---
function colour_of(p) = [for (q = PARTS) if (q[0] == p) q[2]][0];
function offset_of(p) = [for (q = PARTS) if (q[0] == p) q[3]][0];

module piece(p, a = 0) {
    color(colour_of(p))
    if      (p == "spine")      spine();
    else if (p == "camera")     camera();
    else if (p == "hub")        hub();
    else if (p == "link_front") swing_front(a) link_front();
    else if (p == "link_thumb") swing_thumb(a) link_thumb();
    else if (p == "tip_front")  swing_front(a) tip_front();
    else if (p == "tip_thumb")  swing_thumb(a) tip_thumb();
}

module assembly(a, explode = 0) {
    for (q = PARTS) translate(explode * q[3]) piece(q[0], a);
}

// jaw bodies without their gear teeth, for the interference sweep
module front_body(a) { swing_front(a) { link_front(false); tip_front(); } }
module thumb_body(a) { swing_thumb(a) { link_thumb(false); tip_thumb(); } }

mirror_hand() {
    if      (part == "assembly") assembly(theta);
    else if (part == "exploded") assembly(theta, 1);
    else if (part == "in_hand")  { assembly(theta); ghost_hand(theta); }
    else if (part == "clash") {
        // the two jaws must never touch each other or the hub (gears excluded)
        intersection() { front_body(theta); thumb_body(theta); }
        intersection() { union() { front_body(theta); thumb_body(theta); } hub(); }
    }
    else if (part == "gearclash")   // the teeth themselves, full links
        intersection() { swing_front(theta) link_front(); swing_thumb(theta + skew) link_thumb(); }
    else if (part == "parts") for (q = PARTS) echo(str("PART|", q[0], "|", q[1], "|", q[2], "|", q[3][0], ",", q[3][1], ",", q[3][2]));
    else piece(part, 0);   // printable pieces export closed, in assembly position
}
