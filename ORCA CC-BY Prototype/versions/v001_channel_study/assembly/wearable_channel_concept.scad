// ORCA-derived geometry study — CC BY 4.0; see README.md and ../upstream/LICENSE.
// Original hardware: Copyright (c) 2026 ORCA Dexterity, Inc.
// Changes: enlargement, assembled placement, and one longitudinal cut.
// CONCEPT ONLY: the cut removes tendon/joint features. It is not an actuated glove.
// Channel dimensions are provisional, not measured fit. Inspect before printing.
use <original_index.scad>

view = "carved"; // [carved,original,comparison,removed_material]
part = "all"; // [all,AP,PP,IP]
enlargement = 2; // [1:0.05:3]
longitudinal_scale = 2; // [0.75:0.05:3]
channel_width = 24; // [12:0.5:36]
channel_depth = 22; // [12:0.5:36]
channel_offset_x = 0; // [-10:0.5:10]
channel_offset_y = 0; // [-10:0.5:10]
show_channel = false;

// Width is along the finger's lateral Y direction; depth is X (palmar/dorsal).
// A straight through-hole in the neutral assembled pose, in FINAL millimeters.
module finger_channel() {
    translate([channel_offset_x,channel_offset_y,-40*longitudinal_scale])
        scale([channel_depth/2,channel_width/2,1])
            cylinder(r=1,h=140*longitudinal_scale,$fn=128);
}

module positioned_part(which) {
    scale([enlargement,enlargement,longitudinal_scale]) {
        if (which=="AP") orca_index_ap();
        if (which=="PP") orca_index_pp();
        if (which=="IP") translate([1.5,0,37]) orca_index_ip();
    }
}

module cut_part(which) {
    difference() { positioned_part(which); finger_channel(); }
}

module carved() {
    if (part=="all" || part=="AP") color([0.28,0.43,0.58]) cut_part("AP");
    if (part=="all" || part=="PP") color([0.76,0.82,0.87]) cut_part("PP");
    if (part=="all" || part=="IP") color([0.94,0.66,0.30]) cut_part("IP");
}

if (view=="original") orca_index_assembly();
if (view=="carved") carved();
if (view=="comparison") {
    translate([-45,0,0]) orca_index_assembly();
    translate([35,0,0]) carved();
}
if (view=="removed_material")
    color([0.9,0.15,0.1]) intersection() {
        scale([enlargement,enlargement,longitudinal_scale]) orca_index_assembly();
        finger_channel();
    }
if (show_channel && view=="carved") %finger_channel();
