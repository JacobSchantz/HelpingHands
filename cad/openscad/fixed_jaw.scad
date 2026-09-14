// =============================================================================
//  fixed_jaw.scad — the SO-101 "wrist roll follower": the gripper body that
//  cradles the gripper servo, bolts to wrist_roll (ID 5), and carries the
//  fixed jaw as one piece with itself.
// =============================================================================
//  Frame matches Wrist_Roll_Follower_SO101.step.  See params.scad for the
//  frame definition and for where every number came from.
// =============================================================================

include <params.scad>
include <common.scad>

// Back of the blade: one plane leaning fj_back_lean_deg off vertical, above
// fj_back_z_start; below that the back is the flat rear wall.
function fj_back_x(z) =
    max(fj_x_min, fj_back_x_at_z0 + z * tan(fj_back_lean_deg));

// Gripping face + blade width: step down the measured staircase.
function fj_step_index(z) =
    (z >= fj_face_steps[4][0]) ? 4 :
    (z >= fj_face_steps[3][0]) ? 3 :
    (z >= fj_face_steps[2][0]) ? 2 :
    (z >= fj_face_steps[1][0]) ? 1 : 0;

function fj_front_x(z) = fj_face_steps[fj_step_index(z)][1];
function fj_half_y(z)  = lookup(z, [for (s = fj_face_steps) [s[0], s[2]]]);

fj_step_gap = 0.07;
function fj_station(z) = [z, fj_back_x(z), fj_front_x(z), fj_half_y(z)];

// stations must climb monotonically, so build the list in order by hand
fj_stations = [
    fj_station(fj_body_top_z),
    fj_station(fj_back_z_start),
    fj_station(fj_face_steps[1][0] - fj_step_gap), fj_station(fj_face_steps[1][0] + fj_step_gap),
    fj_station(55),
    fj_station(fj_face_steps[2][0] - fj_step_gap), fj_station(fj_face_steps[2][0] + fj_step_gap),
    fj_station(75),
    fj_station(fj_face_steps[3][0] - fj_step_gap), fj_station(fj_face_steps[3][0] + fj_step_gap),
    fj_station(fj_face_steps[4][0] - fj_step_gap), fj_station(fj_face_steps[4][0] + fj_step_gap),
    fj_station(fj_face_steps[5][0]),
    [fj_top_z, fj_back_x(fj_face_steps[5][0]) + fj_tip_r,
               fj_front_x(fj_top_z) - fj_tip_r / 2, fj_tip_r]
];


// --- the body ----------------------------------------------------------------

// The body's footprint tapers: full width in the middle, narrow at the rear
// where it is only as wide as the fixed jaw's own back.  Hulling the two
// measured rectangles gets that taper for free.
module fj_footprint_2d(x_max, y_min, y_max) {
    hull() {
        rrect(fj_x_min, fj_x_min + 2, -fj_rear_half_y, fj_rear_half_y, 2.0);
        rrect(fj_x_min + 11, x_max, y_min, y_max, fj_flange_r);
    }
}

module fj_flange() {
    linear_extrude(fj_flange_z1 - fj_flange_z0)
        fj_footprint_2d(fj_flange_x_max, fj_flange_y_min, fj_flange_y_max);
}

module fj_cradle() {
    linear_extrude(fj_body_top_z - fj_floor_z)
        fj_footprint_2d(fj_cradle_x_max, fj_y_min, fj_y_max - 4.0);
}

// The servo pocket: open toward +X, floored at the second flange face.
module fj_servo_pocket() {
    translate([fj_pocket_x_min, -fj_pocket_half_y, fj_pocket_z0])
        cube([60, 2 * fj_pocket_half_y, fj_pocket_z1 - fj_pocket_z0]);
}

// The moving jaw's fork sweeps over the top of both side walls, so they are
// stepped in to the boss faces the fork straddles.
module fj_fork_clearance() {
    translate([fj_pocket_x_min, fj_boss_y_pos, fj_fork_clear_z]) cube([60, 20, 60]);
    translate([fj_pocket_x_min, fj_boss_y_neg - 20, fj_fork_clear_z]) cube([60, 20, 60]);
}

// The tab that reaches out to x=30 and carries the servo lead clear of the jaw.
module fj_cable_tab() {
    translate([0, 0, fj_floor_z])
        linear_extrude(fj_flange_z1 - fj_floor_z)
            rrect(fj_tab_x0, fj_x_max, -fj_tab_half_y, fj_tab_half_y, 3.0);
}

// --- the wrist_roll horn interface at the base -------------------------------

module fj_horn_mount() {
    s = horn_bolt_square / 2;
    // horn pocket, open at the bottom face
    translate([0, -0.22, -0.05 - eps])
        cylinder(d = horn_recess_d, h = horn_recess_depth + eps);
    // centre clearance for the output-shaft screw
    translate([0, -0.22, fj_flange_z0])
        cylinder(d = horn_centre_bore_d, h = m3_cap_depth + 3.0 + eps);
    for (dx = [-s, s], dy = [-s, s])
        translate([dx, -0.22 + dy, fj_flange_z0 - eps]) {
            cylinder(d = m3_clear_d, h = 3.0 + 2 * eps);
            translate([0, 0, 3.0]) cylinder(d = m3_cap_d, h = m3_cap_depth + eps);
        }
}

module fj_horn_rim() {
    translate([0, -0.22, -0.05])
        cylinder(d = horn_recess_d + 2, h = fj_flange_z0 + 0.05);
}

// --- the servo's own retaining screws, through the side walls -----------------

module fj_servo_screws() {
    for (z = fj_servo_screw_z) {
        translate([fj_servo_screw_x_neg, fj_y_min - 1, z]) rotate([-90, 0, 0]) {
            cylinder(d = fj_servo_screw_d, h = 12);
            cylinder(d = fj_servo_screw_cb_d, h = 6.0);
        }
        translate([fj_servo_screw_x_pos, fj_boss_y_pos + 1, z]) rotate([90, 0, 0]) {
            cylinder(d = fj_servo_screw_d, h = 12);
            cylinder(d = fj_servo_screw_cb_d, h = 6.0);
        }
    }
}

// --- the part ----------------------------------------------------------------

module fixed_jaw() {
    difference() {
        union() {
            translate([0, 0, fj_flange_z0]) fj_flange();
            translate([0, 0, fj_floor_z])   fj_cradle();
            fj_cable_tab();
            fj_horn_rim();
            loft_z(fj_stations);
        }
        fj_servo_pocket();
        fj_fork_clearance();
        fj_horn_mount();
        fj_servo_screws();
        // Ø10 cable bore through the back tower
        translate([fj_x_min - 1, fj_cable_bore_y, fj_cable_bore_z])
            rotate([0, 90, 0]) cylinder(d = fj_cable_bore_d, h = fj_x_min * -1 + fj_pocket_x_min + 1);
    }
}

fixed_jaw();
