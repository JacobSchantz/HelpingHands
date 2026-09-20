// =============================================================================
//  crow_upper.scad — the upper mandible, on the stock wrist-roll follower body.
// =============================================================================
//  Everything below z = 38 is the SO-101's own part, untouched: the wrist_roll
//  horn pocket, the gripper-servo cradle, the cable bore and tab.  Above z = 38
//  the stock stepped blade is gone and a crow's maxilla is in its place.
//  Frame and interface numbers: ../params.scad.
// =============================================================================

include <crow_common.scad>
use <../fixed_jaw.scad>

module crow_upper() {
    difference() {
        union() {
            fj_body_solid();                       // the arm interface, as-is
            loft_z(crow_upper_stations, crow_corner_r);
        }
        fj_body_cuts();                            // pockets, bores, horn, screws
        crow_tool_notch();
    }
}

crow_upper();
