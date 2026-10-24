// Base 26 from Base 25; Gripper 30 from Gripper 29; split support-free prints. +Y above hand.
include <compact_source.scad>
part="assembly";
// Work in inherited underside frame; reflect drive as a rigid assembly at output.
// Entire gear tooth slab is below finger band before inversion.
drive_drop=gear_y1+plate/2+drive_gap;
module down() {translate([0,-drive_drop,0]) children();}
// Original lattice blade and rounded tip, without distal additions or trimming.
module finger2d() {
 offset(r=-fillet_r) offset(delta=fillet_r) union() {
  difference(){profile();circle(r=loop_r,$fn=96);rail2d() translate([contact_edge_w,contact_trim_u0]) square([2*tip[1],contact_trim_u1-contact_trim_u0]);}
  circle(r=loop_r,$fn=96);
 }
}

// Split the inherited 7.7 mm tooth slab, without adding overall height.
// Lower teeth mesh the jaws; only the right jaw has upper teeth at the pinion.
module sector(phase,right,upper=false) {
 pitch=upper?drive_pitch:gear_pitch;
 span=upper?[180+pin_theta-gear_extra*pitch,180+pin_theta+max_angle+gear_extra*pitch]:[180-gear_extra*pitch,180+max_angle+gear_extra*pitch];
 slab(upper?gear_y0-drive_drop:-mesh_split,upper?-mesh_split-mesh_layer_gap-(gear_y0-drive_drop):mesh_split-plate/2-drive_gap)
 rotate(-toe) gear2d(upper?drive_teeth:gear_teeth,180+phase,span[0],span[1],m=upper?drive_m:gear_m);
}
// Original outer outline/tips retained; delete fragile through-lattice; retain original surface grooves.
// Flat blade prints first, hex torque shaft grows directly from its root.
module direct_finger(){difference(){mirror([0,1,0])tapered()xz(plate)finger2d();xz(plate+2)ridges2d();}}
key_end=gear_y0-drive_drop+key_end_gap;
module hexkey(clear=0){circle(r=fdm_key_r+clear,$fn=6);}
module blade(){difference(){
 union(){direct_finger();slab(key_end,plate/2-key_end) hexkey();}
 slab(key_end-1,plate+drive_drop+20) circle(d=post_d+2*base_clear,$fn=64);
}}
module gear_layer(phase=0,right=true,upper=false){difference(){
 union(){sector(phase,right,upper);slab(upper?gear_y0-drive_drop:-mesh_split,upper?-mesh_split-mesh_layer_gap-(gear_y0-drive_drop):mesh_split-plate/2-drive_gap) circle(r=gear_join_r,$fn=64);}
 slab(gear_y0-drive_drop-1,plate+drive_drop+20) hexkey(fdm_key_fit);
}}
module integral_jaw(phase=0,right=true){blade();gear_layer(phase,right);if(right)gear_layer(phase,right,true);}
// Pinion teeth only occupy upper level; spline plate, screws and rotor remain real size.
module stepped_pinion(a=angle){difference(){down() pinion(a);slab(-mesh_split-mesh_layer_gap,gear_y1-drive_drop+mesh_split+mesh_layer_gap+1) translate(pin_c) circle(r=g_ra(pinion_teeth,drive_m)+base_clear,$fn=96);}}
// Two through-bored sleeves are clamped between overhead base and local washers.
sleeve_end=plate/2+retainer_gap;
washer_end=sleeve_end+washer_t;
module top_holes2d(){translate(pin_c)rotate(-hls_body_deg)for(u=[hls_mount_cad_u0,hls_mount_cad_u1],s=[-1,1])let(q=[u,s*hls_mount_span_w/2])translate(q+fdm_spacer_offset*q/norm(q))children();}
module base(){union(){
 difference(){
 slab(base_y0-drive_drop,base_t)hull(){base2d();top_holes2d()circle(d=fdm_top_boss_d,$fn=48);}
 slab(base_y0-drive_drop-1,base_t+2)translate(pin_c)circle(d=hls_plate_d+2*base_clear,$fn=96);
 }
 for(s=[-1,1])translate([s*pivot,0,0])slab(base_y1-drive_drop,sleeve_end-base_y1+drive_drop)circle(d=post_d,$fn=64);
}}
module bored_base(){difference(){base();
 for(s=[-1,1])translate([s*pivot,0,0])slab(base_y0-drive_drop-1,sleeve_end-base_y0+drive_drop+2)circle(d=pivot_bore,$fn=48);
 slab(base_y0-drive_drop-1,base_t+2)top_holes2d()circle(d=pivot_bore,$fn=48);
 slab(base_y1-drive_drop-fdm_spacer_head_h,fdm_spacer_head_h+1)top_holes2d()circle(d=fdm_spacer_head_d,$fn=48);
}}
module ear_spacers(){translate([pin_c[0],0,pin_c[1]])rotate([0,hls_body_deg,0])for(u=[hls_mount_cad_u0,hls_mount_cad_u1],s=[-1,1])let(q=[u,s*hls_mount_span_w/2],r=q+fdm_spacer_offset*q/norm(q))difference(){
 slab(hls_ear_y-drive_drop,base_y0-hls_ear_y)hull(){translate(q)circle(d=hls_mount_boss_d,$fn=48);translate(r)circle(d=fdm_top_boss_d,$fn=48);}
 // Through pilots avoid blind-hole roofs. Off-axis screw tips remain separated in Y.
 translate([q[0],0,q[1]])slab(hls_ear_y-drive_drop-1,base_y0-hls_ear_y+2)hls_slots2d(hls_mount_clear_d);
 translate([r[0],0,r[1]])slab(hls_ear_y-drive_drop-1,base_y0-hls_ear_y+2)circle(d=hls_mount_clear_d,$fn=32);
}}
module spacer_screws(){
 slab(base_y1-drive_drop-fdm_spacer_head_h,fdm_spacer_head_h)top_holes2d()circle(d=fdm_spacer_head_d-2*base_clear,$fn=48);
 slab(base_y0-drive_drop,base_t-fdm_spacer_head_h+.01)top_holes2d()circle(d=hls_m2_shank_d,$fn=32);
}
module pivot_washers() {for(s=[-1,1]) translate([s*pivot,0,0]) slab(sleeve_end,washer_t) difference(){circle(d=washer_d,$fn=64);circle(d=washer_bore,$fn=48);}}
module pivot_screws() {for(s=[-1,1]) translate([s*pivot,0,0]) difference() {
 union(){slab(washer_end-pivot_screw_len,pivot_screw_len+.01) circle(d=pivot_screw_d,$fn=48);slab(washer_end,pivot_head_h) circle(d=pivot_head_d,$fn=48);}
 slab(washer_end+pivot_head_h/2,pivot_head_h) circle(r=pivot_socket_af/sqrt(3),$fn=6);
}}
module pivot_nuts() {for(s=[-1,1]) translate([s*pivot,0,0]) slab(base_y0-drive_drop-pivot_nut_h,pivot_nut_h) difference(){circle(r=pivot_nut_af/sqrt(3),$fn=6);circle(d=pivot_nut_bore,$fn=48);}}

// Straight holes, external bought washers: no counterbore roof or floating perimeter.
pinion_face=-mesh_split-mesh_layer_gap;
module plate_screws(a=angle){hls_rotor(a)hls_plate_holes(){
 slab(hls_plate_y,pinion_face+drive_drop+fdm_plate_washer_t-hls_plate_y+.01)circle(d=hls_m2_shank_d,$fn=32);
 slab(pinion_face+drive_drop+fdm_plate_washer_t,hls_plate_head_h)circle(d=hls_plate_head_d-2*base_clear,$fn=32);
}}
module plate_washers(){hls_rotor()hls_plate_holes()slab(pinion_face,fdm_plate_washer_t)difference(){circle(d=fdm_plate_washer_d,$fn=64);circle(d=fdm_plate_washer_bore,$fn=48);}}
module capture_ring(){down()hls_rotor()slab(hls_plate_y,center_capture_t)difference(){circle(d=fdm_capture_d,$fn=64);circle(d=center_clear_d,$fn=48);}}

module item(k) {
 if(k=="left"||k=="right") placed(k=="left"?-1:1,angle) integral_jaw(k=="left"?half_tooth:0,k=="right");

 if(k=="base") bored_base();
 if(k=="capture_ring")capture_ring();
 if(k=="plate_washers")plate_washers();
 if(k=="ear_spacers")ear_spacers();
 if(k=="spacer_screws")spacer_screws();
 if(k=="left_blade"||k=="right_blade")placed(k=="left_blade"?-1:1,angle)blade();
 if(k=="left_gear"||k=="right_gear"||k=="right_upper")placed(k=="left_gear"?-1:1,angle)gear_layer(k=="left_gear"?half_tooth:0,k!="left_gear",k=="right_upper");
 if(k=="pivot_washers") pivot_washers();
 if(k=="pivot_screws") pivot_screws();
 if(k=="pivot_nuts") pivot_nuts();
 if(k=="pinion") stepped_pinion();
 if(k=="motor") down() motor();
 if(k=="stock_plate") down() stock_plate();
 if(k=="plate_screws") down() plate_screws();
 if(k=="case_screws") down() case_screws();
 if(k=="center_screw") down() center_screw();
 if(k=="cable") down() cable();
}
keys=["left_blade","right_blade","left_gear","right_gear","right_upper","ear_spacers","spacer_screws","capture_ring","plate_washers","pinion","base","motor","stock_plate","plate_screws","case_screws","pivot_screws","pivot_washers","pivot_nuts","center_screw","cable"];
for(k=["left","right"])if(part==str("viewer_",k))scale(scale_factor)mirror([0,1,0])item(k);
for(k=keys) {
 if(part==str("viewer_",k)) scale(scale_factor) mirror([0,1,0]) item(k);
 if(part=="assembly" && k!="cable") scale(scale_factor) mirror([0,1,0]) item(k);
 if(part==str("print_",k)) scale(scale_factor) {
  if(k=="left_blade"||k=="right_blade")bed_down(plate/2)blade();
  if(k=="left_gear"||k=="right_gear")bed_up(-mesh_split)gear_layer(k=="left_gear"?half_tooth:0,k!="left_gear");
  if(k=="right_upper")bed_up(gear_y0-drive_drop)gear_layer(0,true,true);
  if(k=="base")bed_up(base_y0-drive_drop)bored_base();
  if(k=="ear_spacers")bed_up(hls_ear_y-drive_drop)ear_spacers();
  if(k=="capture_ring")bed_up(hls_plate_y-drive_drop)capture_ring();
  if(k=="pinion")bed_down(-mesh_split-mesh_layer_gap)stepped_pinion(0);
 
 }
}
if(part=="viewer_right") {echo(pivot=pivot*scale_factor);echo(drive_drop=drive_drop*scale_factor);echo(toe=toe,pin_c=pin_c*scale_factor);}

module plate_tools(){hls_rotor()hls_plate_holes()slab(pinion_face+fdm_plate_washer_t+hls_plate_head_h,tool_len)circle(d=tool_d,$fn=32);}
module case_straight_tools() {down() slab(hls_ear_y-hls_ear_thickness-hls_case_head_h-tool_len,tool_len) case_probe_holes() circle(d=tool_d,$fn=32);}
module case_tools() {
 down() hls_frame() rotate([0,hls_body_deg,0]) for(u=[hls_mount_cad_u0,hls_mount_cad_u1],side=[-1,1])
 translate([u,hls_ear_y-hls_ear_thickness-hls_case_head_h,side*hls_mount_span_w/2])
 rotate([0,0,u<0?-case_tool_tilt:0]) rotate([90,0,0]) cylinder(d=tool_d,h=tool_len,$fn=32);
}
module center_tools() {down() hls_rotor() slab(hls_plate_y+center_capture_t+hls_center_head_h,tool_len) circle(d=tool_d,$fn=32);}
for(k=["plate_tools","case_tools","center_tools"]) if(part==str("viewer_",k)) scale(scale_factor) mirror([0,1,0]) {
 if(k=="plate_tools") plate_tools(); if(k=="case_tools") case_tools();if(k=="center_tools") center_tools();
}

if(part=="viewer_case_straight_tools") scale(scale_factor) mirror([0,1,0]) case_straight_tools();

module pivot_tools(){for(s=[-1,1]) translate([s*pivot,0,0]) slab(washer_end+pivot_head_h,tool_len) circle(d=tool_d,$fn=32);}
// Hollow nut driver leaves room for exposed screw; its bore is not a forbidden solid.
module nut_tools(){for(s=[-1,1]) translate([s*pivot,0,0]) slab(base_y0-drive_drop-pivot_nut_h-tool_len,tool_len) difference(){circle(d=nut_tool_d,$fn=48);circle(d=pivot_bore,$fn=48);}}
for(k=["pivot_tools","nut_tools"]) if(part==str("viewer_",k)) scale(scale_factor) mirror([0,1,0]) {if(k=="pivot_tools") pivot_tools();if(k=="nut_tools") nut_tools();}

if(part=="viewer_spacer_tools")scale(scale_factor)mirror([0,1,0])slab(base_y1-drive_drop,tool_len)top_holes2d()circle(d=tool_d,$fn=32);
