// =============================================================================
//  moving_jaw.scad — the SO-101 gripper's moving jaw, rebuilt parametrically.
// =============================================================================
//  Frame matches Moving_Jaw_SO101.step: pivot axis = Z, blade runs toward -Y,
//  gripping face looks toward -X.  Every dimension comes from params.scad.
//  Preview this file on its own, or open gripper.scad for the assembly.
// =============================================================================

include <params.scad>
include <common.scad>

// --- the two faces of the blade, as functions of position down the blade -----

// Back (outer) face: two straight tapers meeting at mj_back_kink_y.
function mj_back_x(y) =
    (y >= mj_back_kink_y)
        ? mj_back_x_at_pivot + y * tan(mj_back_taper_deg)
        : mj_back_x_at_pivot + mj_back_kink_y * tan(mj_back_taper_deg)
          + (y - mj_back_kink_y) * tan(mj_back_taper2_deg);

// Gripping face: the staircase.  Each step brings the face 2 mm closer to the
// fixed jaw, so the pads meet at the fingertip and open into a throat behind.
function mj_front_x(y) =
    (y <= mj_face_steps[2][0]) ? mj_face_steps[2][1] :
    (y <= mj_face_steps[1][0]) ? mj_face_steps[1][1] :
                                 mj_face_steps[0][1];

// Blade half-height, interpolated between the measured stations.
function mj_half_h(y) = lookup(-y, [for (p = mj_blade_profile) [-p[0], p[1]]]);

// Station list for the loft.  Duplicated y's straddle each step in the face.
mj_step_gap = 0.05;
mj_loft_ys = concat(
    [-10.0, mj_neck_y_end, -18.0, mj_neck_y_start],            // fork spine
    [for (p = mj_blade_profile)
        each (p[0] == mj_face_steps[1][0] || p[0] == mj_face_steps[2][0])
            ? [p[0] + mj_step_gap, p[0] - mj_step_gap]         // straddle a step
            : [p[0]]]);

function mj_station(y) =
    (y > mj_neck_y_start)
        ? [y, mj_neck_x_min, mj_back_x(y),
              mj_neck_half_h + (mj_fork_outer_w / 2 - mj_neck_half_h)
                             * (y - mj_neck_y_start) / (-10.0 - mj_neck_y_start)]
        : [y, mj_front_x(y), mj_back_x(y), mj_half_h(y)];

mj_stations = [for (y = mj_loft_ys) mj_station(y)];


// --- the fork plates that bolt to the gripper servo's horn -------------------

module mj_plate_2d() {
    hull() {
        circle(r = mj_hub_r);
        translate([mj_plate_x_min, mj_plate_y_min])
            square([mj_plate_x_max - mj_plate_x_min, 2]);
    }
}

// One M3 through-hole plus its counterbore, driven from the outer face inward.
module mj_bolt(x, y, outer_z, dir, cb_depth) {
    translate([x, y, outer_z]) {
        cylinder(d = m3_clear_d, h = 40, center = true);
        translate([0, 0, dir * -cb_depth])
            cylinder(d = m3_socket_d, h = cb_depth + eps);
    }
}

module mj_horn_bolts() {
    s = horn_bolt_square / 2;
    for (dx = [-s, s], dy = [-s, s]) {
        mj_bolt(dx, dy,  mj_fork_outer_w / 2,                     1, m3_socket_depth);
        mj_bolt(dx, dy, -mj_fork_outer_w / 2 + mj_cb_depth_bottom, 1, mj_cb_depth_bottom);
    }
    // centre screw into the servo's output shaft
    cylinder(d = m3_clear_d, h = mj_fork_outer_w + 2, center = true);
    // the horn's boss is recessed into the inner face of each plate
    translate([0, 0,  mj_fork_gap / 2 - eps])       cylinder(d = horn_spigot_d, h = 1.5);
    translate([0, 0, -mj_fork_gap / 2 - 1.5 + eps]) cylinder(d = horn_spigot_d, h = 1.5);
}


// --- the part ----------------------------------------------------------------

// The two plates that straddle the gripper servo.  Split out from
// moving_jaw() so a different blade can hang off the same horn -- see crow/.
module mj_fork() {
    translate([0, 0,  mj_fork_gap / 2])
        linear_extrude(mj_plate_t_top) mj_plate_2d();
    translate([0, 0, -mj_fork_outer_w / 2])
        linear_extrude(mj_plate_t_bottom) mj_plate_2d();
}

module mj_fork_cuts() {
    // the slot between the plates, open toward +Y and both X faces
    translate([-40, mj_neck_y_end, -mj_fork_outer_w / 2 + mj_plate_t_bottom])
        cube([80, 60, mj_fork_gap]);
    mj_horn_bolts();
}

// The stock blade, on its own.
module mj_blade() { loft_y(mj_stations); }

// Spelled out on purpose -- see the note on fixed_jaw().  Same solid either
// way; grouping it just re-tessellates export/*.stl.
module moving_jaw() {
    difference() {
        union() {
            translate([0, 0,  mj_fork_gap / 2])
                linear_extrude(mj_plate_t_top) mj_plate_2d();
            translate([0, 0, -mj_fork_outer_w / 2])
                linear_extrude(mj_plate_t_bottom) mj_plate_2d();
            loft_y(mj_stations);
        }
        // the slot between the plates, open toward +Y and both X faces
        translate([-40, mj_neck_y_end, -mj_fork_outer_w / 2 + mj_plate_t_bottom])
            cube([80, 60, mj_fork_gap]);
        mj_horn_bolts();
    }
}

moving_jaw();
