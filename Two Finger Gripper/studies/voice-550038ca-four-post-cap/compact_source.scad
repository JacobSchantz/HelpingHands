// Base 18 from Base 17, Gripper 24 unchanged. All new dimensions live in params.json.
include <large_source.scad>
part="assembly";
hls_ear_y=base_y0+hls_plate_face-hls_plate_above_ear;
hls_plate_y=base_y0+hls_plate_face;
module hls_frame() {translate([pin_c[0],0,pin_c[1]]) children();}
module hls_holes2d() {translate(pin_c) rotate(-hls_body_deg) for(u=[hls_mount_cad_u0,hls_mount_cad_u1],s=[-1,1]) translate([u,s*hls_mount_span_w/2]) children();}
module hls_slots2d(d) {hull() for(dx=[-hls_mount_slot_travel/2,hls_mount_slot_travel/2]) translate([dx,0]) circle(d=d,$fn=32);}
module hls_base() {
 difference() {
  union() {
   slab(base_y0,base_t) hull() {base2d();pillars2d();hls_holes2d() circle(d=hls_mount_boss_d,$fn=48);}
   slab(hls_ear_y,base_y0-hls_ear_y) hls_holes2d() circle(d=hls_mount_boss_d,$fn=48);
  }
  slab(base_y0-1,base_t+2) translate(pin_c) circle(d=hls_plate_d+2*base_clear,$fn=96);
  slab(hls_ear_y-1,hls_case_pilot_depth+1) hls_holes2d() hls_slots2d(hls_mount_clear_d);

  for(c=pillar_c) slab(base_y1+pillar_floor,top_y+top_gap-base_y1-pillar_floor+1) translate(c) circle(d=pillar_pilot_d,$fn=16);
 }
}
module hls_rotor(a=angle) {hls_frame() rotate([0,-a*pin_ratio,0]) children();}
module hls_plate_holes() {for(t=hls_plate_angles) rotate([0,-(-90-t-hls_body_deg),0]) translate([hls_plate_pcd/2,0,0]) children();}
module pinion(a=angle,extra=0) {
 hls_rotor(a) difference() {
  union() {
   slab(gear_y0,gear_y1-gear_y0) gear2d(pinion_teeth,pin_phase);
   slab(hls_plate_y,gear_y0-hls_plate_y+0.01) circle(d=hls_plate_d-2*base_clear,$fn=96);
  }
  slab(hls_plate_y-1,gear_y1-hls_plate_y+2) circle(d=hls_center_access_d,$fn=64);
  hls_plate_holes() {
   slab(hls_plate_y-1,gear_y1-hls_plate_y+2) circle(d=hls_plate_clear_d,$fn=32);
   slab(gear_y1-hls_plate_head_recess-hls_plate_head_h, hls_plate_head_h+hls_plate_head_recess+1) circle(d=hls_plate_head_d,$fn=32);
  }
 }
}
module native_hls(file) {hls_frame() rotate([0,hls_body_deg,0]) translate([0,hls_ear_y,0]) scale(1/scale_factor) import(file,convexity=10);}
module motor(a=angle) {native_hls("reference/servo.stl");}
module stock_plate(a=angle) {hls_frame() rotate([0,hls_body_deg-a*pin_ratio,0]) translate([0,hls_ear_y,0]) scale(1/scale_factor) import("reference/stock_plate.stl",convexity=10);}
module plate_screws(a=angle) {
 hls_rotor(a) hls_plate_holes() {
  // Omit intended thread engagement in purchased plate.
  slab(hls_plate_y,gear_y1-hls_plate_head_recess-hls_plate_head_h-hls_plate_y) circle(d=hls_m2_shank_d,$fn=32);
  slab(gear_y1-hls_plate_head_recess-hls_plate_head_h,hls_plate_head_h) circle(d=hls_plate_head_d-2*base_clear,$fn=32);
 }
}
module case_probe_holes() {translate(pin_c) rotate(-hls_body_deg) for(u=[hls_mount_cad_u0,hls_mount_cad_u1],s=[-1,1]) translate([u,s*hls_mount_span_w/2]) children();}
module case_screws() {
 // Only unthreaded screw portions in the ear and heads; intended self-tapped engagement omitted.
 slab(hls_ear_y-hls_ear_thickness,hls_ear_thickness) case_probe_holes() circle(d=hls_m2_shank_d,$fn=32);
 slab(hls_ear_y-hls_ear_thickness-hls_case_head_h,hls_case_head_h) case_probe_holes() circle(d=hls_case_head_d,$fn=32);
}
module center_screw() {hls_rotor() slab(hls_plate_y,hls_center_head_h) circle(d=hls_center_head_d,$fn=48);}
module cable() {hls_frame() slab(hls_ear_y-hls_cable_h,hls_cable_h) rotate(-hls_body_deg) translate([hls_body_length-hls_near+ hls_cable_len/4,-hls_cable_w/2]) square([hls_cable_len,hls_cable_w]);}
module cap_screws() {for(c=pillar_c) translate([c[0],0,c[1]]) {
 slab(top_y0,top_t) circle(d=actual_m3_shank_d/scale_factor,$fn=32);
 translate([0,top_y1,0]) rotate([90,0,0]) cylinder(d1=actual_m3_head_d/scale_factor,d2=actual_m3_shank_d/scale_factor,h=actual_m3_head_h/scale_factor,$fn=32);
}}
