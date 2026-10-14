// =============================================================================
//  crow_beak.scad — the crow-beak end effector for the SO-101.  Open this one.
// =============================================================================
//
//      openscad -D 'part="assembly"' -o crow_assembly.stl crow_beak.scad
//      openscad -D 'crow_opening=25'                       crow_beak.scad
//
//  part = "assembly" | "open" | "tool" | "interference"
//       | "upper" | "lower" | "pivot_plug" | "camera_mount" | "puck"
//                       (the printable pieces, each in its assembled position)
//       | "handheld" | "armed" | "exploded"       (the two uses, and pulled apart)
//       | "parts"       (echoes the piece list build.sh turns into parts.json)
//       | "plugclash" | "fitclash"       (overlap tests, must come out EMPTY)
//
//  The same beak (upper + lower + camera) is held by hand -- thumb dimple and
//  strap loops, pivot plug in the servo pocket -- or carries the gripper servo
//  and slides onto the wrist puck.  plans/crow_gripper.md section 14.
//
//  "interference" renders the overlap between the two mandibles at the current
//  crow_opening.  It must come out EMPTY at every opening — that is the test
//  ../NOTES.md section 5 says this model was missing.  build.sh runs it.
// =============================================================================

include <crow_common.scad>
use <crow_upper.scad>
use <crow_lower.scad>
use <crow_dock.scad>
use <crow_camera.scad>
use <crow_hand.scad>

part = "assembly";

// Same transform as the stock gripper's jaw_place(): the crow jaws hang off the
// unmodified pivot, so the servo, horn and calibration are unchanged.
module crow_place(angle = crow_angle) {
    translate([jaw_pivot_x, 0, jaw_pivot_z])
        rotate([0, angle, 0])
            rotate([-90, 0, 0])
                children();
}

module crow_beak(angle = crow_angle) {
    color("#8d9aa6") crow_upper();
    color("#2f3336") crow_place(angle) crow_lower();
}

// Only the beak.  Below crow_root_z the moving jaw's fork plates already
// overlap the body's outer walls in the stock rebuild too -- an artifact of
// fj_fork_clearance() being a square step rather than the swept arc the real
// part has (../NOTES.md section 6, item 5).  Inherited, not introduced here,
// and out of scope for a jaw swap; clipping it away is what makes this test
// mean "the mandibles never touch".
module crow_interference(angle = crow_angle) {
    intersection() {
        translate([-60, -40, crow_root_z]) cube([120, 80, 120]);
        crow_upper();
        crow_place(angle) crow_lower();
    }
}

// A rod chucked in the tool notch, at the gape crow_opening_for_rod() says it
// takes.  This is the crow's actual trick and the reason the notch is there.
module crow_with_tool(d = crow_rod_d) {
    crow_beak(crow_angle_for(crow_opening_for_rod(d)));
    color("#b8823c")
        translate([crow_tomium_x(crow_notch_z), 0, crow_notch_z])
            rotate([0, crow_tomium_lean(crow_notch_z), 0])
                translate([crow_opening_for_rod(d) * crow_notch_r / crow_tip_arm / 2, 0, 0])
                    rotate([90, 0, 0]) cylinder(d = d, h = 90, center = true);
}

// Every printed piece, each in its assembled position: [part, label, colour,
// explode offset].  build.sh exports one STL per row and turns the echo into
// export/parts.json, which the app's 3D view reads for its explode toggle.
PIECES = [
    ["upper",        "Upper mandible + body (thumb dimple, strap loops)", "#8d9aa6", [-45,   0,   0]],
    ["lower",        "Lower mandible (finger strap loops) - moves",      "#2f3336", [ 55,   0,  20]],
    ["pivot_plug",   "Pivot plug (handheld - stands in for the servo)",  "#e0a458", [ 10, -75, -10]],
    ["camera_mount", "Camera mount",                                     "#5b6770", [-20,  80,  10]],
    ["puck",         "SO-101 wrist puck (arm only)",                     "#c8813a", [  0,   0, -50]],
];

module crow_piece(name, angle = crow_angle) {
    if      (name == "upper")        crow_upper();
    else if (name == "lower")        crow_place(angle) crow_lower();
    else if (name == "pivot_plug")   crow_pivot_plug();
    else if (name == "camera_mount") crow_camera_mount();
    else if (name == "puck")         crow_wrist_puck();
}

function crow_has(names, n) = len([for (m = names) if (m == n) 1]) > 0;

module crow_pieces(names, explode = 0, angle = crow_angle) {
    for (p = PIECES) if (crow_has(names, p[0]))
        color(p[2]) translate(explode * p[3]) crow_piece(p[0], angle);
}

// In the hand: the beak, the pivot plug in the servo pocket, the camera.  The
// thumb goes in the dimple on the culmen, index and middle along the gonys, a
// strap through each pair of loops.
module crow_handheld(angle = crow_angle) {
    crow_pieces(["upper", "lower", "pivot_plug", "camera_mount"], 0, angle);
    color("#1d2226") crow_camera_ghost();
    color("#3b6ea5", 0.45) crow_strap_ghosts(angle);
}

// On the arm: the same beak with the gripper servo in the pocket, on the puck,
// the puck on a stand-in for the wrist_roll horn.
module crow_armed(angle = crow_angle) {
    crow_pieces(["upper", "lower", "camera_mount", "puck"], 0, angle);
    color("#1d2226") crow_camera_ghost();
    color("#202428", 0.6) crow_servo_ghost();
    color("#444a50") translate([0, dock_y, dock_z - dock_puck_h - 12])
        cylinder(d = 24, h = 12);
}

// The straps, for renders only: a band through each loop pair, around the digit.
module crow_strap_ghosts(angle = crow_angle) {
    module band(z, x_out, x_in, hy) {
        translate([0, 0, z - strap_w / 2]) linear_extrude(strap_w)
            difference() {
                hull() for (x = [x_out, x_in]) for (y = [-1, 1])
                    translate([x, y * (hy + strap_gap / 2)]) circle(r = 1.0, $fn = 12);
                hull() for (x = [x_out, x_in]) for (y = [-1, 1])
                    translate([x, y * (hy + strap_gap / 2)]) circle(r = 0.01, $fn = 4);
            }
    }
    zu = strap_upper_z;
    band(zu, crow_culmen_x(zu) - 18, crow_culmen_x(zu) + strap_inset + strap_bar_x / 2, crow_half_y(zu));
    zl = strap_lower_z;
    crow_place(angle) rotate([90, 0, 0]) translate([-jaw_pivot_x, 0, -jaw_pivot_z])
        band(zl, crow_gonys_x(zl) + 18, crow_gonys_x(zl) - strap_inset - strap_bar_x / 2, crow_half_y(zl));
}

// Overlap tests: the plug against the swinging lower mandible, and the fixed
// pieces against each other.
module crow_plugclash(angle = crow_angle) {
    intersection() { crow_pivot_plug(); crow_place(angle) crow_lower(); }
}
module crow_fitclash() {
    intersection() { crow_upper(); crow_pivot_plug(); }
    intersection() { crow_upper(); crow_camera_mount(); }
    intersection() { crow_upper(); crow_wrist_puck(); }
    intersection() { crow_pivot_plug(); crow_wrist_puck(); }
}

if      (part == "assembly")     crow_beak();
else if (part == "tool")         crow_with_tool();
else if (part == "open")         crow_beak(crow_angle_for(crow_opening_max));
else if (part == "interference") crow_interference();
else if (part == "plugclash")    crow_plugclash();
else if (part == "fitclash")     crow_fitclash();
else if (part == "armed")        crow_armed();
else if (part == "handheld")     crow_handheld();
else if (part == "exploded")     crow_pieces([for (p = PIECES) p[0]], 1);
else if (part == "parts")
    for (p = PIECES) echo(str("PART|", p[0], "|", p[1], "|", p[2], "|",
                              p[3][0], ",", p[3][1], ",", p[3][2]));
else                             crow_piece(part);
