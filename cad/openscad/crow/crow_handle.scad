// =============================================================================
//  crow_handle.scad — the handheld host: a pistol grip under the same dock.
// =============================================================================
//  The cartridge slides onto this exactly as it slides onto the wrist puck
//  (crow_dock_rail(), the same module), so the tip, the throat and the wrist
//  camera sit in the same place relative to the dock in both modes.
//
//  What the handle adds, and the arm never carries:
//    - the TRIGGER: a back-driven STS3215 read as a leader.  The cartridge's own
//      ID 6 follows it, so the jaw is driven by the same servo at the same
//      torque limit as on the arm, and gripper.pos is logged from ID 6.
//    - the PHONE: landscape, screen to the user, rear camera forward.  ARKit
//      gives its pose; T_phone->dock is fixed by this file (and checked, see
//      plans/crow_gripper.md 11).
//
//  Posture: culmen up, so -X is up, the grip hangs toward +X and rakes back
//  toward the user (-Z).  Frame: the cartridge's; z = dock_z is the dock plane.
// =============================================================================

include <crow_params.scad>
include <crow_dock.scad>
include <../common.scad>

function hz(z) = dock_z + z;            // relative-to-dock -> cartridge frame

// the grip's top-front corner, and its axis
grip_top    = [handle_head[0][1], 0, hz(grip_front_z - grip_depth / 2)];
grip_axis   = [cos(grip_rake), 0, -sin(grip_rake)];
grip_bottom = grip_top + grip_len * grip_axis;

// trigger servo shaft: near the +Z end of the pocket, on its +Y face
trig_shaft  = [handle_servo_c[0], 0, hz(handle_servo_c[2] + sts_body[2] / 2 - sts_shaft_from_end)];
// the finger pad: trigger_reach ahead of the backstrap, just below the head
trig_pad    = [handle_head[0][1] + 20, 0, hz(grip_front_z - grip_depth + trigger_reach)];
trig_arm    = norm(trig_pad - trig_shaft);
trig_pad_travel = 2 * trig_arm * sin(trigger_travel / 2);

module grip_section(t) {
    translate([0, 0, 0]) rotate([0, 90 - grip_rake, 0])
        linear_extrude(t, center = true)
            resize([grip_depth, grip_width]) circle(d = 10);
}

module handle_body() {
    hx = handle_head[0]; hy = handle_head[1]; hz_ = handle_head[2];
    // head
    translate([hx[0], hy[0], hz(hz_[0])])
        linear_extrude(hz_[1] - hz_[0]) rrect(0, hx[1] - hx[0], 0, hy[1] - hy[0], 5);
    // grip: hull of a section at the top and a slightly fuller one at the base
    hull() {
        translate(grip_top) grip_section(0.1);
        translate(grip_bottom) scale([1, 1.05, 1.05]) grip_section(0.1);
    }
    // phone cradle: a back frame on the camera side, a ledge onto the head,
    // and lips round both ends so the phone slides in from the top (-X)
    px0 = hx[0] - phone_gap - phone[0];
    difference() {
        union() {
            translate([px0 - 3, -phone[1] / 2 - 3, hz(phone_z)])
                cube([phone[0] + phone_gap + 3, phone[1] + 6, 3]);
            for (sy = [-1, 1])                                  // end lips
                translate([px0 - 3, sy > 0 ? phone[1] / 2 : -phone[1] / 2 - 3, hz(phone_z - phone[2] - 2)])
                    cube([phone[0] + 3, 3, phone[2] + 2 + 3]);
            for (sy = [-1, 1])                                  // lip returns
                translate([px0, sy > 0 ? phone[1] / 2 - 5 : -phone[1] / 2 - 3, hz(phone_z - phone[2] - 2)])
                    cube([phone[0], 8, 2]);
            translate([hx[0] - phone_gap - 2, -35, hz(phone_z - phone[2] - 2)])   // ledge
                cube([phone_gap + 2 + 1, 70, phone[2] + 2 + 3]);
            translate([hx[0] - phone_gap - 2, -35, hz(phone_z - 18)])             // gusset
                cube([phone_gap + 3, 70, 18]);
        }
        // window for the rear camera bump
        translate([px0 + phone_cam[0] - phone_window / 2,
                   phone[1] / 2 - phone_cam[1] - phone_window / 2, hz(phone_z) - 1])
            cube([phone_window, phone_window, 6]);
        // lighten the back frame
        translate([px0 + 10, -phone[1] / 2 + 12, hz(phone_z) - 1])
            cube([phone[0] - 20, phone[1] - 24 - phone_window - 6, 6]);
        // the phone itself
        translate([px0, -phone[1] / 2, hz(phone_z - phone[2])]) cube(phone);
    }
}

module handle_servo_pocket() {
    translate([handle_servo_c[0], 0, hz(handle_servo_c[2])]) cube(
        [sts_body[0] + 0.4, sts_body[1] + 0.4, sts_body[2] + 0.4], center = true);
    // service opening out of the -Y side, and the horn out of the +Y side
    translate([handle_servo_c[0] - sts_body[0] / 2 + 2, -40, hz(handle_servo_c[2]) - sts_body[2] / 2 + 2])
        cube([sts_body[0] - 4, 40, sts_body[2] - 4]);
    translate(trig_shaft) rotate([-90, 0, 0]) cylinder(d = 22, h = 40);
    // bus lead down the grip
    hull() {
        translate([handle_servo_c[0] + sts_body[0] / 2, 0, grip_top[2]]) rotate([0, 90, 0]) cylinder(d = 8, h = 1);
        translate(grip_bottom + [-2, 0, 0]) rotate([0, 90 - grip_rake, 0]) cylinder(d = 8, h = 4);
    }
}

module crow_handle() {
    difference() {
        union() {
            handle_body();
            crow_dock_rail();
        }
        handle_servo_pocket();
        crow_dock_pin();
    }
}

// The trigger lever: a horn disc on the servo's +Y side, an arm down to the
// pad, and a crossbar that brings the pad back to the grip's centre line.
lever_y = handle_head[1][1] + 1.5;       // outside the head's +Y wall
module crow_trigger() {
    s = horn_bolt_square / 2;
    difference() {
        union() {
            hull() {
                translate(trig_shaft + [0, lever_y, 0]) rotate([-90, 0, 0]) cylinder(r = 11, h = 4);
                translate([trig_pad[0], lever_y, trig_pad[2]]) rotate([-90, 0, 0]) cylinder(r = 5, h = 4);
            }
            hull() {                                                     // crossbar
                translate([trig_pad[0], -12, trig_pad[2]]) rotate([-90, 0, 0]) cylinder(r = 5, h = 1);
                translate([trig_pad[0], lever_y, trig_pad[2]]) rotate([-90, 0, 0]) cylinder(r = 5, h = 4);
            }
        }
        for (dx = [-s, s], dz = [-s, s])                                 // horn pattern
            translate(trig_shaft + [dx, lever_y - 1, dz]) rotate([-90, 0, 0]) cylinder(d = m3_clear_d, h = 10);
        translate(trig_shaft + [0, lever_y - 1, 0]) rotate([-90, 0, 0]) cylinder(d = horn_centre_bore_d, h = 10);
    }
}

// Stand-in for the phone, for renders only.
module crow_phone_ghost() {
    px0 = handle_head[0][0] - phone_gap - phone[0];
    translate([px0, -phone[1] / 2, hz(phone_z - phone[2])]) cube(phone);
}
