// =============================================================================
//  crow_camera.scad — the wrist camera's mount: where a crow's eye would be.
// =============================================================================
//  Bolts to the cartridge's +Y flange face (two M3 into heat-set inserts), so it
//  comes off the arm WITH the cartridge and the view is identical in both
//  modes.  Stays outside |y| = 24, the lower mandible fork's envelope.
//  Placement and the framing check: crow_params.scad (cam_*, check 7).
// =============================================================================

include <crow_params.scad>

cam_plate_t = 3.0;
cam_standoff = 6.0;                     // plate face -> lens centre, along the axis

// Rotate +Z onto the optical axis (toed in about X, toward the beak).
module cam_frame() {
    translate(cam_pos) rotate([cam_toe, 0, 0]) children();
}

module crow_camera_plate() {
    cam_frame() translate([0, 0, -cam_standoff - cam_plate_t])
        difference() {
            translate([-cam_board / 2 - 2, -cam_board / 2 - 2, 0])
                cube([cam_board + 4, cam_board + 4, cam_plate_t]);
            translate([0, 0, -1]) cylinder(d = cam_lens_d, h = 10);
            for (dx = [-1, 1], dy = [-1, 1])
                translate([dx * cam_hole_sq / 2, dy * cam_hole_sq / 2, -1])
                    cylinder(d = 2.2, h = 10);
        }
}

// The corner of the plate nearest the flange, for the strut to reach.
module cam_plate_root() {
    cam_frame() translate([-8, cam_board / 2 - 4, -cam_standoff - cam_plate_t])
        cube([16, 6, cam_plate_t]);
}

module crow_camera_mount() {
    foot_y0 = fj_flange_y_max;
    difference() {
        union() {
            // foot on the flange face
            translate([cam_mount_x0, foot_y0, 1.5]) cube([cam_mount_x1 - cam_mount_x0, 4, 10.4]);
            // strut: foot -> plate, kept outside the fork's |y| = 24
            hull() {
                translate([-18, foot_y0, 8]) cube([12, 5, 4]);
                cam_plate_root();
            }
            crow_camera_plate();
        }
        for (x = cam_mount_screw_x)
            translate([x, foot_y0 - 1, cam_mount_screw_z]) rotate([-90, 0, 0]) {
                cylinder(d = m3_clear_d, h = 20);
                translate([0, 0, 5]) cylinder(d = m3_cap_d, h = 20);
            }
        // keep the lens path clear of the strut
        cam_frame() translate([0, 0, -cam_standoff]) cylinder(d = cam_lens_d, h = 40);
    }
}

cam_mount_x0 = -24.0;
cam_mount_x1 = 2.0;

// A stand-in for the board and lens, for renders only.
module crow_camera_ghost() {
    cam_frame() {
        translate([-cam_board / 2, -cam_board / 2, -cam_standoff]) cube([cam_board, cam_board, 2]);
        translate([0, 0, -cam_standoff]) cylinder(d = 14, h = cam_standoff + 4);
    }
}
