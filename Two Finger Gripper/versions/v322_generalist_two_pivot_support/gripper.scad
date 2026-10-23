// Base 21 from Base 20; Gripper 25, direct contact without handles. +Y is above hand.
include <compact_source.scad>
part="assembly";
// Work in inherited underside frame; reflect drive as a rigid assembly at output.
// Entire gear tooth slab is below finger band before inversion.
drive_drop=gear_y1+plate/2+drive_gap;
module down() {translate([0,-drive_drop,0]) children();}
module hex2d(clear=0) {offset(r=clear) circle(r=key_r,$fn=6);}
module finger2d() {
 offset(r=-fillet_r) offset(delta=fillet_r) union() {
  difference() {profile();circle(r=loop_r,$fn=96);rail2d() translate([contact_edge_w,contact_trim_u0]) square([2*tip[1],contact_trim_u1-contact_trim_u0]);}
  circle(r=loop_r,$fn=96);
 }
}
module direct_finger() {
 difference() {
  union() {
   mirror([0,1,0]) finger();
   slab(-plate/2-drive_gap-key_depth,drive_gap+key_depth+.02) hex2d();
  }
  slab(-plate/2-drive_gap-key_depth-1,plate+drive_gap+key_depth+2) circle(d=post_d+2*base_clear,$fn=64);
 }
}
module gear(phase=0,right=true) {
 difference() {
  down() gear_solid(phase,right);
  slab(gear_y0-drive_drop-1,gear_y1-gear_y0+2) circle(d=post_d+2*base_clear,$fn=64);
  slab(-plate/2-drive_gap-key_depth-key_end_gap,key_depth+key_end_gap+1) hex2d(key_fit);
 }
}
// Two through-bored sleeves are clamped between overhead base and local washers.
sleeve_end=plate/2+retainer_gap;
washer_end=sleeve_end+washer_t;
module base() {
 union() {
  down() hls_base();
  for(s=[-1,1]) translate([s*pivot,0,0]) slab(base_y1-drive_drop,sleeve_end-base_y1+drive_drop) circle(d=post_d,$fn=64);
 }
}
module bored_base() {difference() {base();for(s=[-1,1]) translate([s*pivot,0,0]) slab(base_y0-drive_drop-1,sleeve_end-base_y0+drive_drop+2) circle(d=pivot_bore,$fn=48);}}
module pivot_washers() {for(s=[-1,1]) translate([s*pivot,0,0]) slab(sleeve_end,washer_t) difference(){circle(d=washer_d,$fn=64);circle(d=washer_bore,$fn=48);}}
module pivot_screws() {for(s=[-1,1]) translate([s*pivot,0,0]) difference() {
 union(){slab(washer_end-pivot_screw_len,pivot_screw_len) circle(d=pivot_screw_d,$fn=48);slab(washer_end,pivot_head_h) circle(d=pivot_head_d,$fn=48);}
 slab(washer_end+pivot_head_h/2,pivot_head_h) circle(r=pivot_socket_af/sqrt(3),$fn=6);
}}
module pivot_nuts() {for(s=[-1,1]) translate([s*pivot,0,0]) slab(base_y0-drive_drop-pivot_nut_h,pivot_nut_h) difference(){circle(r=pivot_nut_af/sqrt(3),$fn=6);circle(d=pivot_nut_bore,$fn=48);}}
module item(k) {
 if(k=="left"||k=="right") placed(k=="left"?-1:1,angle) direct_finger();
 if(k=="left_gear"||k=="right_gear") gear_piece(k=="left_gear"?"left":"right",angle);
 if(k=="base") bored_base();
 if(k=="pivot_washers") pivot_washers();
 if(k=="pivot_screws") pivot_screws();
 if(k=="pivot_nuts") pivot_nuts();
 if(k=="pinion") down() pinion();
 if(k=="motor") down() motor();
 if(k=="stock_plate") down() stock_plate();
 if(k=="plate_screws") down() plate_screws();
 if(k=="case_screws") down() case_screws();
 if(k=="center_screw") down() center_screw();
 if(k=="cable") down() cable();
}
keys=["left","right","left_gear","right_gear","pinion","base","motor","stock_plate","plate_screws","case_screws","pivot_screws","pivot_washers","pivot_nuts","center_screw","cable"];
for(k=keys) {
 if(part==str("viewer_",k)) scale(scale_factor) mirror([0,1,0]) item(k);
 if(part=="assembly" && k!="cable" && k!="plate_screws" && k!="case_screws" && k!="center_screw") scale(scale_factor) mirror([0,1,0]) item(k);
 if(part==str("print_",k)) scale(scale_factor) {
  // Inversion changes assembly orientation only. Print original-coordinate solids.
  if(k=="left"||k=="right") bed_up(-plate/2-drive_gap-key_depth) {if(k=="left") mirror([1,0,0]) direct_finger();else direct_finger();}
  if(k=="left_gear"||k=="right_gear") bed_up(gear_y0-drive_drop) {if(k=="left_gear") mirror([1,0,0]) gear(half_tooth,false);else gear();}
  if(k=="base") bed_up(hls_ear_y-drive_drop) bored_base();
  if(k=="pinion") bed_down(gear_y1-drive_drop) down() pinion(0);
 
 }
}
if(part=="viewer_right") {echo(pivot=pivot*scale_factor);echo(drive_drop=drive_drop*scale_factor);}

module plate_tools() {down() hls_rotor() hls_plate_holes() slab(gear_y1-hls_plate_head_recess,tool_len) circle(d=tool_d,$fn=32);}
module case_straight_tools() {down() slab(hls_ear_y-hls_ear_thickness-hls_case_head_h-tool_len,tool_len) case_probe_holes() circle(d=tool_d,$fn=32);}
module case_tools() {
 down() hls_frame() rotate([0,hls_body_deg,0]) for(u=[hls_mount_cad_u0,hls_mount_cad_u1],side=[-1,1])
 translate([u,hls_ear_y-hls_ear_thickness-hls_case_head_h,side*hls_mount_span_w/2])
 rotate([0,0,u<0?-case_tool_tilt:0]) rotate([90,0,0]) cylinder(d=tool_d,h=tool_len,$fn=32);
}
module center_tools() {down() hls_rotor() slab(hls_plate_y+hls_center_head_h,tool_len) circle(d=tool_d,$fn=32);}
for(k=["plate_tools","case_tools","center_tools"]) if(part==str("viewer_",k)) scale(scale_factor) mirror([0,1,0]) {
 if(k=="plate_tools") plate_tools(); if(k=="case_tools") case_tools();if(k=="center_tools") center_tools();
}

if(part=="viewer_case_straight_tools") scale(scale_factor) mirror([0,1,0]) case_straight_tools();

module pivot_tools(){for(s=[-1,1]) translate([s*pivot,0,0]) slab(washer_end+pivot_head_h,tool_len) circle(d=tool_d,$fn=32);}
// Hollow nut driver leaves room for exposed screw; its bore is not a forbidden solid.
module nut_tools(){for(s=[-1,1]) translate([s*pivot,0,0]) slab(base_y0-drive_drop-pivot_nut_h-tool_len,tool_len) difference(){circle(d=nut_tool_d,$fn=48);circle(d=pivot_bore,$fn=48);}}
for(k=["pivot_tools","nut_tools"]) if(part==str("viewer_",k)) scale(scale_factor) mirror([0,1,0]) {if(k=="pivot_tools") pivot_tools();if(k=="nut_tools") nut_tools();}
