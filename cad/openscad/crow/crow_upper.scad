// =============================================================================
//  crow_upper.scad — the upper mandible, on the stock wrist-roll follower body.
// =============================================================================
//  Everything below z = 38 is the SO-101's own part, untouched: the wrist_roll
//  horn pocket, the gripper-servo cradle, the cable bore and tab.  Above z = 38
//  the stock stepped blade is gone and a crow's maxilla is in its place.
//  Frame and interface numbers: ../params.scad.
// =============================================================================

include <crow_common.scad>
include <crow_dock.scad>
use <../fixed_jaw.scad>

// crow_mount = "dock" (default): the base is a dovetail groove that slides onto
// the wrist puck or the handle -- crow_dock.scad.  "horn": the stock body's
// base, bolted straight to wrist_roll, as the beak was first drawn.
module crow_upper() {
    difference() {
        union() {
            if (crow_mount == "horn") fj_body_solid(); // the arm interface, as-is
            else {                                     // same, minus the horn rim
                translate([0, 0, fj_flange_z0]) fj_flange();
                translate([0, 0, fj_floor_z])   fj_cradle();
                fj_cable_tab();
            }
            loft_z(crow_upper_stations, crow_corner_r);
        }
        if (crow_mount == "horn") fj_body_cuts();  // pockets, bores, horn, screws
        else {
            fj_servo_pocket();
            fj_fork_clearance();
            fj_servo_screws();
            translate([fj_x_min - 1, fj_cable_bore_y, fj_cable_bore_z])
                rotate([0, 90, 0]) cylinder(d = fj_cable_bore_d, h = -fj_x_min + fj_pocket_x_min + 1);
            crow_dock_groove();
            crow_dock_pin();
            crow_cam_mount_inserts();
        }
        crow_tool_notch();
        crow_throat();
    }
}

// Two heat-set insert holes in the flange's +Y face for the camera mount.
module crow_cam_mount_inserts() {
    for (x = cam_mount_screw_x)
        translate([x, fj_flange_y_max + eps, cam_mount_screw_z])
            rotate([90, 0, 0]) cylinder(d = 4.0, h = 6.0);   // M3 heat-set, 4 mm
}

crow_upper();
