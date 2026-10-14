// =============================================================================
//  crow_hand.scad — what lets a hand hold the beak: the thumb dimple, the strap
//  loops, and the pivot plug that stands in for the gripper servo.
// =============================================================================
//  The dimple and the upper loops are cut into / added onto crow_upper(); the
//  lower loops onto crow_lower().  The plug is its own printed piece.
//  Numbers: crow_params.scad, "IN THE HAND".  Frame: the follower frame.
// =============================================================================

include <crow_params.scad>

// A dimple in the culmen for the thumb pad: an ellipsoid, square to the face.
module crow_thumb_dimple() {
    lean = atan((crow_culmen_x(thumb_z + 1) - crow_culmen_x(thumb_z - 1)) / 2);
    a = thumb_a;                               // ellipsoid semi-axis, normal to the face
    k = thumb_k;                               // its section at the face, as a fraction
    translate([crow_culmen_x(thumb_z), 0, thumb_z])
        rotate([0, lean, 0])
            translate([-(a - thumb_depth), 0, 0])
                scale([a, thumb_w / 2 / k, thumb_len / 2 / k]) sphere(r = 1, $fn = 48);
}

// One belt loop on the +Y (s = 1) or -Y (s = -1) flank, centred on z.  The strap
// threads through it along X, so it can wrap the digit lying on the outer face.
// face(z) is the x of the outer face's inside edge -- the loop runs in from it.
module strap_loop(s, z, x_at) {
    zs = [z - strap_w / 2 - strap_post, z + strap_w / 2];      // the two posts
    module chunk(zz, y0, y1)
        translate([x_at(zz + strap_post / 2), 0, zz])
            translate([0, s > 0 ? y0 : -y1, 0]) cube([strap_bar_x, y1 - y0, strap_post]);
    // the bar, standing strap_gap off the flank
    hull() for (zz = zs)
        chunk(zz, crow_half_y(zz) + strap_gap, crow_half_y(zz) + strap_gap + strap_bar_t);
    // the posts, rooted 1 mm into the flank
    for (zz = zs)
        chunk(zz, crow_half_y(zz + strap_post) - 1.0, crow_half_y(zz) + strap_gap + strap_bar_t);
}

// The upper mandible's pair: the thumb strap, on the culmen side.
module crow_upper_strap_loops() {
    for (s = [-1, 1])
        strap_loop(s, strap_upper_z, function(z) crow_culmen_x(z) + strap_inset);
}

// The lower mandible's pair: the finger strap, on the gonys side.  Follower frame.
module crow_lower_strap_loops() {
    for (s = [-1, 1])
        strap_loop(s, strap_lower_z, function(z) crow_gonys_x(z) - strap_inset - strap_bar_x);
}

// The pivot bolt's hole through the pocket walls (and the plug).
module crow_pivot_bore() {
    translate([jaw_pivot_x, 0, jaw_pivot_z])
        rotate([90, 0, 0]) cylinder(d = pivot_bolt_d, h = mj_fork_outer_w + 4, center = true);
}

// The pivot plug: fills the servo pocket so the walls carry the pivot bolt
// without folding in.  Slides in from +X, held by the servo's own two M2 screws.
module crow_pivot_plug() {
    difference() {
        translate([fj_pocket_x_min + plug_clear, -fj_pocket_half_y + plug_clear, fj_pocket_z0 + plug_clear])
            cube([plug_x1 - fj_pocket_x_min - plug_clear,
                  2 * (fj_pocket_half_y - plug_clear),
                  fj_pocket_z1 - fj_pocket_z0 - 2 * plug_clear]);
        crow_pivot_bore();
        // the lower mandible's neck swings down over the top +X corner as the
        // beak opens: chamfer it off (check_interference.sh sweeps this)
        translate([plug_x1, 0, fj_pocket_z1]) rotate([0, 45, 0])
            cube([plug_chamfer * sqrt(2), 40, plug_chamfer * sqrt(2)], center = true);
        // M2 pilot holes, where the servo's retaining screws come through the walls
        for (z = fj_servo_screw_z) {
            translate([fj_servo_screw_x_neg, -fj_pocket_half_y - 1, z])
                rotate([-90, 0, 0]) cylinder(d = 1.7, h = 10);
            translate([fj_servo_screw_x_pos, fj_pocket_half_y + 1, z])
                rotate([90, 0, 0]) cylinder(d = 1.7, h = 10);
        }
    }
}

// A stand-in for the gripper servo, for renders only.  Envelope is [GUESS].
module crow_servo_ghost() {
    translate([fj_pocket_x_min + plug_clear, -fj_pocket_half_y + plug_clear, fj_pocket_z0 + plug_clear])
        cube([45.2, 2 * (fj_pocket_half_y - plug_clear), fj_pocket_z1 - fj_pocket_z0 - 2 * plug_clear]);
}
