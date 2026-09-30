// =============================================================================
//  crow_beak.scad — the crow-beak end effector for the SO-101.  Open this one.
// =============================================================================
//
//      openscad -D 'part="assembly"' -o crow_assembly.stl crow_beak.scad
//      openscad -D 'crow_opening=25'                       crow_beak.scad
//
//  part = "assembly" | "open" | "tool" | "upper" | "lower" | "interference"
//       | "puck" | "camera_mount" | "handle" | "trigger"      (printable parts)
//       | "armed" | "handheld"                                (the two hosts)
//
//  The same cartridge (upper + lower + camera) docks on the wrist puck or on
//  the handle -- plans/crow_gripper.md sections 9-11.
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
use <crow_handle.scad>

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

// The cartridge: the thing that moves between hosts.
module crow_cartridge(angle = crow_angle) {
    crow_beak(angle);
    color("#5b6770") crow_camera_mount();
    color("#1d2226") crow_camera_ghost();
}

// On the arm: cartridge on the puck, puck on a stand-in for the wrist_roll horn.
module crow_armed(angle = crow_angle) {
    crow_cartridge(angle);
    color("#c8813a") crow_wrist_puck();
    color("#444a50") translate([0, dock_y, dock_z - dock_puck_h - 12])
        cylinder(d = 24, h = 12);
}

// In the hand: the same cartridge on the handle, trigger and phone.
module crow_handheld(angle = crow_angle) {
    crow_cartridge(angle);
    color("#c8813a") crow_handle();
    color("#e0a458") crow_trigger();
    color("#26303a", 0.55) crow_phone_ghost();
}

if      (part == "assembly")     crow_beak();
else if (part == "tool")         crow_with_tool();
else if (part == "open")         crow_beak(crow_angle_for(crow_opening_max));
else if (part == "upper")        crow_upper();
else if (part == "lower")        crow_lower();
else if (part == "interference") crow_interference();
else if (part == "puck")         crow_wrist_puck();
else if (part == "camera_mount") crow_camera_mount();
else if (part == "handle")       crow_handle();
else if (part == "trigger")      crow_trigger();
else if (part == "armed")        crow_armed();
else if (part == "handheld")     crow_handheld();
