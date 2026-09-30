// =============================================================================
//  crow_dock.scad — the one interface both hosts share.
// =============================================================================
//  A 60-degree dovetail along X, open toward +X, locked by one M3 cross-pin
//  along Y.  The WRIST PUCK and the HANDLE both carry crow_dock_rail(); the
//  cartridge carries crow_dock_groove().  Because it is literally the same
//  module on both hosts, the cartridge -- and so the tip, the throat and the
//  camera -- sits in the same place relative to the dock in both modes.  That
//  frame is what the capture pipeline agrees on (plans/crow_gripper.md 10).
//
//  Frame: the cartridge's (the follower frame).  The dock plane is z = dock_z.
// =============================================================================

include <crow_params.scad>

// The dovetail cross-section in the YZ plane, base on z = 0.
module dock_dovetail_2d(grow = 0) {
    wb = dock_rail_w_base + 2 * grow;
    wt = dock_rail_w_top + 2 * grow;
    polygon([[-wb / 2, -grow], [wb / 2, -grow],
             [wt / 2, dock_rail_h + grow], [-wt / 2, dock_rail_h + grow]]);
}

// The rail, standing on the dock plane.  Both hosts use this.
module crow_dock_rail() {
    difference() {
        translate([-dock_rail_len / 2, dock_y, dock_z])
            rotate([90, 0, 90])
                linear_extrude(dock_rail_len) dock_dovetail_2d();
        crow_dock_pin();
    }
}

// The groove in the cartridge's base: blind at -X (that end is the stop), open
// toward +X so the cartridge slides on from the front.
module crow_dock_groove() {
    translate([-dock_rail_len / 2 - dock_clear, dock_y, dock_z])
        rotate([90, 0, 90])
            linear_extrude(60) dock_dovetail_2d(dock_clear);
    // a lead-in chamfer on the open end would go here; the flange ends at x=27
}

// The cross-pin that locks it: an M3 bolt through the flange and the rail.
module crow_dock_pin() {
    translate([dock_pin_x, 0, dock_pin_z])
        rotate([90, 0, 0]) cylinder(d = dock_pin_d, h = 80, center = true);
}

// The wrist puck: bolts to the wrist_roll horn with the SO-101's own pattern
// (4 x M3 on a 9.9 mm square, the Ø24 x 6 horn recess, the centre bore) and
// presents the rail.  It stays on the arm.
module crow_wrist_puck() {
    z0 = dock_z - dock_puck_h;          // the horn face, in the cartridge frame
    s  = horn_bolt_square / 2;
    difference() {
        union() {
            translate([0, dock_y, z0]) cylinder(d = dock_puck_d, h = dock_puck_h);
            crow_dock_rail();
        }
        // horn recess, open at the bottom
        translate([0, dock_y, z0 - eps]) cylinder(d = horn_recess_d, h = horn_recess_depth + eps);
        // centre bore, and a driver hole down through the rail
        translate([0, dock_y, z0]) cylinder(d = horn_centre_bore_d, h = 40);
        translate([0, dock_y, z0 + horn_recess_depth + dock_horn_floor - dock_head_h])
            cylinder(d = m3_cap_d, h = 40);
        // the four horn screws: clearance through the floor, heads counterbored
        // from the rail top so they go in before the cartridge does
        for (dx = [-s, s], dy = [-s, s])
            translate([dx, dock_y + dy, z0]) {
                cylinder(d = m3_clear_d, h = 40);
                translate([0, 0, horn_recess_depth + dock_horn_floor - dock_head_h])
                    cylinder(d = m3_cap_d, h = 40);
            }
        crow_dock_pin();
    }
}
