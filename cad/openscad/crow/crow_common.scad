// =============================================================================
//  crow_common.scad — the station lists both mandibles are lofted from, and
//  the one feature they share: the tool notch.
// =============================================================================

include <../common.scad>
include <crow_params.scad>

// follower frame -> moving-jaw frame (the inverse of jaw_place at angle 0)
function f2j_y(z) = jaw_pivot_z - z;
function f2j_x(x) = x - jaw_pivot_x;


// --- upper mandible (the fixed jaw's blade) ---------------------------------
// loft_z wants [z, x_back, x_front, half_y].  Back is the culmen, front is the
// tomium.
crow_upper_zs = [38.0, 45.0, 50.0, 55.0, 62.0, 70.0, 74.0, 78.0,
                 84.0, 92.0, 98.0, 102.5, 105.375];
crow_upper_stations =
    [for (z = crow_upper_zs) [z, crow_culmen_x(z), crow_tomium_x(z), crow_half_y(z)]];


// --- lower mandible (the moving jaw's blade) --------------------------------
// Three neck stations lifted straight from the stock jaw, so the fork-to-blade
// transition is the part that is already known to work, then the beak.
function crow_neck_back_x(y) = mj_back_x_at_pivot + y * tan(mj_back_taper_deg);
function crow_neck_station(y) =
    [y, mj_neck_x_min, crow_neck_back_x(y),
        mj_neck_half_h + (mj_fork_outer_w / 2 - mj_neck_half_h)
                       * (y - mj_neck_y_start) / (-10.0 - mj_neck_y_start)];

crow_lower_zs = [crow_lower_root_z, 52.0, 58.0, 62.0, 70.0, 78.0,
                 84.0, 92.0, 98.0, 102.5, 105.375];
crow_lower_stations = concat(
    [for (y = [-10.0, mj_neck_y_end, -18.0]) crow_neck_station(y)],
    [for (z = crow_lower_zs)
        [f2j_y(z), f2j_x(crow_lo_tomium_x(z)), f2j_x(crow_gonys_x(z)), crow_half_y(z)]]);


// --- the tool notch ----------------------------------------------------------
// A 90-degree V straddling the tomial line, square to it.  Subtracted from both
// parts, so closed the two halves form a diamond aperture the beak can chuck a
// rod in.  Defined in the follower frame; crow_lower.scad maps it back.
module crow_tool_notch() {
    translate([crow_tomium_x(crow_notch_z), 0, crow_notch_z])
        rotate([0, crow_tomium_lean(crow_notch_z), 0])
            rotate([-90, 0, 0])
                linear_extrude(crow_notch_len, center = true)
                    rotate(45) square(crow_notch_depth * sqrt(2), center = true);
}

// The same notch expressed in the moving jaw's own frame.
module crow_tool_notch_jaw_frame() {
    rotate([90, 0, 0])
        translate([-jaw_pivot_x, 0, -jaw_pivot_z])
            crow_tool_notch();
}
