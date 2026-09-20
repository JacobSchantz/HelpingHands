// =============================================================================
//  crow_lower.scad — the lower mandible, on the stock gripper-servo fork.
// =============================================================================
//  The fork, its horn bolt pattern and its counterbores are the SO-101's own,
//  untouched.  The blade is a crow's mandible: steep through the rami, a long
//  flat gonys, a gonydeal angle at z = 86 and an upturned tip.
//  Frame: the moving jaw's own frame, so gripper-style jaw_place() still works.
// =============================================================================

include <crow_common.scad>
use <../moving_jaw.scad>

module crow_lower() {
    difference() {
        union() {
            mj_fork();                             // the servo interface, as-is
            loft_y(crow_lower_stations, crow_corner_r);
        }
        mj_fork_cuts();                            // slot + horn bolts
        crow_tool_notch_jaw_frame();
    }
}

crow_lower();
