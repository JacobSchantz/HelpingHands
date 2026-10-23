module so_hub() {
    difference() {
        union() {
            cylinder(d=hub_d,h=hub_t,$fn=96);
            translate([0,0,so_horn_z-so_socket_h]) cylinder(d=so_neck_d,h=so_neck_h+so_socket_h+0.01,$fn=96);
        }
        translate([0,0,so_horn_z-so_socket_h-1]) cylinder(d=so_socket_d,h=so_socket_h+1,$fn=96);   // round the horn
        if(so_center_d>0) translate([0,0,so_horn_z-so_socket_h-1]) cylinder(d=so_center_d,h=hub_t+so_neck_h+so_socket_h+2,$fn=48);
        for(i=[0:sts_horn_holes-1]) rotate(45+i*360/sts_horn_holes) translate([sts_horn_pcd/2,0,0]) {   // the horn's 4 M3, countersunk from the tool face
            translate([0,0,so_horn_z-1]) cylinder(d=screw_clear_d,h=hub_t-so_horn_z+2,$fn=24);
            translate([0,0,so_head_z]) cylinder(d=so_head_d,h=hub_t-so_head_z+1,$fn=24);
            translate([0,0,so_head_z-(so_head_d-screw_clear_d)/2]) cylinder(d1=screw_clear_d,d2=so_head_d+0.02,h=(so_head_d-screw_clear_d)/2+0.01,$fn=24);   // 45 deg on into the head's hole
        }
        for(i=[0:radial_n-1]) let(t=radial_phase_deg+i*360/radial_n) radial_hole(t,hub_t-radial_h,hub_d/2-radial_pilot_len,hub_d/2+1,radial_pilot_d,-1);   // point down: up as it prints
        for(i=[0:3]) rotate(tool_screw_phase_deg+i*90) translate([tool_screw_pcd/2,0,-1]) cylinder(d=hub_scallop_d,h=hub_t+2,$fn=32);
    }
}
// the tool plate, in its own frame: the floor's tool face at z 0, the socket below it (open at -tool_t), and spacer (Aero) above