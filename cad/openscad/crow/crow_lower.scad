// =============================================================================
//  crow_lower.scad — the lower mandible, on the stock gripper-servo fork.
// =============================================================================
//  The fork, its horn bolt pattern and its counterbores are the SO-101's own,
//  untouched.  The blade is a crow's mandible: steep through the rami, a long
//  flat gonys, a gonydeal angle at z = 86 and an upturned tip.
//  Frame: the moving jaw's own frame, so gripper-style jaw_place() still works.
// =============================================================================

include <crow_common.scad>
include <crow_hand.scad>
use <../moving_jaw.scad>

module crow_lower() {
    difference() {
        union() {
            mj_fork();                             // the servo interface, as-is
            loft_y(crow_lower_stations, crow_corner_r);
            rotate([90, 0, 0]) translate([-jaw_pivot_x, 0, -jaw_pivot_z])
                crow_lower_strap_loops();          // follower frame -> jaw frame
        }
        mj_fork_cuts();                            // slot + horn bolts
        crow_tool_notch_jaw_frame();
    }
}

crow_lower();
