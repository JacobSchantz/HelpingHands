// ORCA Hand hardware: Copyright (c) 2026 ORCA Dexterity, Inc. — CC BY 4.0.
// Source: orcahand/orcahand_hardware, 37b71dc03d3f11e48b920cbf54562b33c025bc8c.
// See ../upstream/LICENSE and README.md for attribution and placement evidence.
// Original manufacturing STLs. Only rigid placement; no shape changes.
// Three printed components, assembled at their CAD bearing-seat axes.
// Bearings, pins, tendons, skin and palm are not included in this subassembly.

// Pose controls are geometric inspection, not a force/tendon simulation.
mcp_angle = 0; // [-20:1:90]
pip_angle = 0; // [-15:1:100]
show_axes = false;
explode = 0; // [0:1:30]

module orca_index_ap() {
    // Source AP MCP seat: [0,0,0], Y axis. Rotate so its carpal end faces -Z.
    rotate([0,90,0]) import("../upstream/orca_v2/base/01_Fingers/I-AP-R.stl");
}

module orca_index_pp() {
    import("../upstream/orca_v2/base/01_Fingers/I-PP.stl");
}

module orca_index_ip() {
    import("../upstream/orca_v2/base/01_Fingers/I-IP.stl");
}

module orca_index_assembly(mcp=0, pip=0, separation=0) {
    color([0.28,0.43,0.58]) translate([0,0,-separation]) orca_index_ap();
    rotate([0,-mcp,0]) {
        color([0.76,0.82,0.87]) orca_index_pp();
        // Source I-PP PIP bearing seats share this exact analytic STEP axis.
        translate([1.5,0,37+separation]) rotate([0,-pip,0])
            color([0.94,0.66,0.30]) orca_index_ip();
    }
}

module joint_axes(mcp=0) {
    color([0.1,0.8,0.7,0.8]) rotate([90,0,0]) cylinder(d=0.7,h=30,center=true,$fn=24);
    rotate([0,-mcp,0]) translate([1.5,0,37])
        color([0.8,0.2,0.6,0.8]) rotate([90,0,0]) cylinder(d=0.7,h=30,center=true,$fn=24);
}

orca_index_assembly(mcp_angle,pip_angle,explode);
if (show_axes) joint_axes(mcp_angle);
