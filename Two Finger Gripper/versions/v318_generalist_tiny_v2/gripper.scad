// Tiny V2 / Base 17 / Gripper 24. Original recognizable fingers, resized 30:30:24 gears and direct full-size servo mounting.
// large_source.scad is Base 15 with only its output dispatcher renamed.
include <large_source.scad>
part="assembly";
module mechanism(a=angle) {
 for(s=[-1,1]) placed(s,a) color("#efb83b") finger();
 for(q=["left","right"]) color("#35383e") gear_piece(q,a);
 color("#35383e") {pinion(a);base();top_plate();}
}
module tiny_piece(k,a=angle) {
 if(k=="left"||k=="right") placed(k=="left"?-1:1,a) finger();
 if(k=="left_gear"||k=="right_gear") gear_piece(k=="left_gear"?"left":"right",a);
 if(k=="pinion") pinion(a);
 if(k=="base") base();
 if(k=="top_plate") top_plate();
}
if(part=="assembly") scale(scale_factor) {mechanism();color("#a3a8ad") motor();}
for(k=["left","right","left_gear","right_gear","pinion","base","top_plate"]) {
 if(part==str("viewer_",k)) scale(scale_factor) tiny_piece(k);
 if(part==str("print_",k)) scale(scale_factor) print_part(k);
}
if(part=="viewer_right") echo(pivot=pivot*scale_factor);
if(part=="measure") echo(axes=[pivot,pin_c[0],pin_c[1],pin_ratio]);
// Genuine unscaled hardware for interference review, never published as a fitted part.
if(part=="hardware_reference") scale(scale_factor) motor();
if(part=="viewer_motor") scale(scale_factor) motor();
if(part=="viewer_cable") scale(scale_factor) sts_cable();
if(part=="comparison") {translate([-100,0,0]) mechanism(30);translate([100,0,0]) scale(scale_factor) mechanism(30);}

// Clearance probes contain only the portions inside/above printed parts;
// threaded portions inside the horn/case and self-tapped pillars are intentional.
module horn_screw_probes(a=angle) {
 translate([pin_c[0],0,pin_c[1]]) rotate([0,-a*pin_ratio,0]) ring3(m_out_screws,m_out_pcd,gear_bolt_phase_deg) {
  slab(flange_y,gear_y1-gear_bolt_head_h-flange_y) circle(d=actual_m3_shank_d/scale_factor,$fn=32);
  translate([0,gear_y1-gear_bolt_head_h,0]) rotate([90,0,0]) cylinder(d1=actual_m3_head_d/scale_factor,d2=actual_m3_shank_d/scale_factor,h=actual_m3_head_h/scale_factor,$fn=32);
 }
}
module case_screw_probes() {
 slab(base_y0,base_t-sts_screw_head_h) sts_holes2d() circle(d=actual_m2_shank_d/scale_factor,$fn=32);
 slab(base_y1-sts_screw_head_h,actual_m2_head_h/scale_factor) sts_holes2d() circle(d=actual_m2_head_d/scale_factor,$fn=32);
}
module cap_screw_probes() {
 for(c=pillar_c) translate([c[0],0,c[1]]) {
  slab(top_y0,top_t) circle(d=actual_m3_shank_d/scale_factor,$fn=32);
  translate([0,top_y1,0]) rotate([90,0,0]) cylinder(d1=actual_m3_head_d/scale_factor,d2=actual_m3_shank_d/scale_factor,h=actual_m3_head_h/scale_factor,$fn=32);
 }
}
if(part=="viewer_horn_screws") scale(scale_factor) horn_screw_probes();
if(part=="viewer_case_screws") scale(scale_factor) case_screw_probes();
if(part=="viewer_cap_screws") scale(scale_factor) cap_screw_probes();
