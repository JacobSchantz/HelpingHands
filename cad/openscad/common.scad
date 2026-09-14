// common.scad — the two shape helpers both parts are built from.
include <params.scad>

// A rounded rectangle in 2D, given by its bounds rather than size+centre,
// because every number in params.scad is a measured face position.
module rrect(a0, a1, b0, b1, r) {
    rr = min(r, (a1 - a0) / 2 - 0.001, (b1 - b0) / 2 - 0.001);
    translate([a0 + rr, b0 + rr])
        offset(r = rr)
            square([a1 - a0 - 2 * rr, b1 - b0 - 2 * rr]);
}

// One cross-section of a blade that runs along Y: a wafer in the XZ plane.
// x0..x1 is front-to-back, +-half_h is the blade's height.
module station_y(y, x0, x1, half_h, r = mj_corner_r, t = 0.02) {
    translate([0, y, 0])
        rotate([90, 0, 0])
            linear_extrude(t, center = true)
                rrect(x0, x1, -half_h, half_h, r);
}

// One cross-section of a blade that runs along Z: a wafer in the XY plane.
module station_z(z, x0, x1, half_w, r = 2.0, t = 0.02) {
    translate([0, 0, z])
        linear_extrude(t, center = true)
            rrect(x0, x1, -half_w, half_w, r);
}

// Loft a list of [y, x_front, x_back, half_h] stations by hulling neighbours.
// A repeated y with different x/half_h therefore reads as a step, not a blend —
// which is exactly how both jaws' gripping faces are shaped.
module loft_y(stations, r = mj_corner_r) {
    for (i = [0 : len(stations) - 2])
        hull() {
            station_y(stations[i][0],     stations[i][1],     stations[i][2],     stations[i][3],     r);
            station_y(stations[i + 1][0], stations[i + 1][1], stations[i + 1][2], stations[i + 1][3], r);
        }
}

module loft_z(stations, r = 2.0) {
    for (i = [0 : len(stations) - 2])
        hull() {
            station_z(stations[i][0],     stations[i][1],     stations[i][2],     stations[i][3],     r);
            station_z(stations[i + 1][0], stations[i + 1][1], stations[i + 1][2], stations[i + 1][3], r);
        }
}
