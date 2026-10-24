// Base 27 from Base 26; Gripper 31 from Gripper 30. Five independent printed solids.
include <compact_source.scad>
part="assembly";
// Work in inherited underside frame; reflect drive as a rigid assembly at output.
// Entire gear tooth slab is below finger band before inversion.
drive_drop=gear_y1+plate/2+drive_gap+fdm_upper_lift;
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
 slab(upper?gear_y0-drive_drop:-mesh_split,upper?-mesh_split-mesh_layer_gap-fdm_upper_lift-(gear_y0-drive_drop):mesh_split-plate/2-drive_gap)
 rotate(-toe) gear2d(upper?drive_teeth:gear_teeth,180+phase,span[0],span[1],m=upper?drive_m:gear_m);
}
// Original outer outline/tips retained; delete fragile through-lattice; retain original surface grooves.
// Flat blade prints first, hex torque shaft grows directly from its root.
module direct_finger(){difference(){mirror([0,1,0])tapered()xz(plate)finger2d();xz(plate+2)ridges2d();}}
key_end=gear_y0-drive_drop+key_end_gap;
module hexkey(clear=0){circle(r=fdm_key_r+clear,$fn=6);}
module core2d(phase,right,upper=false){union(){
 pitch=upper?drive_pitch:gear_pitch;
 span=upper?[180+pin_theta-gear_extra*pitch,180+pin_theta+max_angle+gear_extra*pitch]:[180-gear_extra*pitch,180+max_angle+gear_extra*pitch];
 rotate(-toe)gear2d(upper?drive_teeth:gear_teeth,180+phase,span[0],span[1],m=upper?drive_m:gear_m);
 circle(r=gear_join_r,$fn=64);
}}
// Z extrusion rotates toward negative Y; every new layer grows from the previous.
module taper(y0,y1,start,phase,right,upper=false){
 translate([0,y0,0])rotate([90,0,0])linear_extrude(height=y0-y1,scale=1/start,convexity=10)scale(start)core2d(phase,right,upper);
}
module integral_jaw(phase=0,right=true){difference(){union(){
 direct_finger();
 let(end=right?gear_y0-drive_drop:-mesh_split)slab(end,plate/2-end)circle(r=fdm_key_r,$fn=64);
 // Small starting gear silhouette is wholly inside the original solid root.
 taper(-plate/2,-plate/2-drive_gap-fdm_boolean_overlap,fdm_taper_start,phase,right);
 sector(phase,right);slab(-mesh_split,mesh_split-plate/2-drive_gap)circle(r=gear_join_r,$fn=64);
 if(right){
  taper(-mesh_split+fdm_boolean_overlap,-mesh_split-mesh_layer_gap-fdm_upper_lift-fdm_boolean_overlap,fdm_upper_start,phase,right,true);
  sector(phase,right,true);slab(gear_y0-drive_drop,-mesh_split-mesh_layer_gap-fdm_upper_lift-(gear_y0-drive_drop))circle(r=gear_join_r,$fn=64);
 }
 }slab(gear_y0-drive_drop-1,plate+drive_drop+20)circle(d=post_d+2*base_clear,$fn=64);}}
// Pinion teeth only occupy upper level; spline plate, screws and rotor remain real size.
module stepped_pinion(a=angle){difference(){down() pinion(a);slab(-mesh_split-mesh_layer_gap-fdm_upper_lift,gear_y1-drive_drop+mesh_split+mesh_layer_gap+fdm_upper_lift+1) translate(pin_c) circle(r=g_ra(pinion_teeth,drive_m)+base_clear,$fn=96);}}
// Frame prints broad back down, with all journals/motor pillars growing upward.
frame_top=-(fdm_frame_back+drive_gap-fdm_original_gap+fdm_upper_lift+fdm_frame_t);
frame_face=frame_top+fdm_frame_t;
sleeve_end=plate/2+fdm_retainer_gap;
washer_end=sleeve_end+fdm_frame_t;
module routed_holes2d(){translate(pin_c)rotate(-hls_body_deg)for(u=[hls_mount_cad_u0,hls_mount_cad_u1],side=[-1,1])translate([u,side*(hls_mount_span_w/2+fdm_pillar_offset)])children();}
module frame_outline(){hull(){for(s=[-1,1])translate([s*pivot,0])circle(d=post_d+4*base_clear+2*retainer_gap,$fn=64);routed_holes2d()circle(d=hls_mount_boss_d,$fn=48);}}
module base(){difference(){union(){
 slab(frame_top,fdm_frame_t)frame_outline();
 for(s=[-1,1])translate([s*pivot,0,0]){
 slab(frame_face,sleeve_end-frame_face)circle(d=post_d,$fn=64);
 let(stop=s<0?-mesh_split-retainer_gap:gear_y0-drive_drop-retainer_gap)slab(frame_face,stop-frame_face)circle(d=post_d+4*base_clear+2*retainer_gap,$fn=64);
 }
 translate([pin_c[0],0,pin_c[1]])rotate([0,hls_body_deg,0])for(u=[hls_mount_cad_u0,hls_mount_cad_u1],side=[-1,1])let(ear=hls_ear_y-drive_drop-hls_ear_thickness,q=[u,side*hls_mount_span_w/2],r=q+[0,side*fdm_pillar_offset]){
 slab(frame_face,ear-fdm_pillar_ramp-fdm_motor_pilot_depth-frame_face)translate(r)circle(d=hls_mount_boss_d,$fn=48);
 slab(ear-fdm_motor_pilot_depth,fdm_motor_pilot_depth)translate(q)circle(d=hls_mount_boss_d,$fn=48);
 hull(){slab(ear-fdm_pillar_ramp-fdm_motor_pilot_depth,fdm_boolean_overlap)translate(r)circle(d=hls_mount_boss_d,$fn=48);slab(ear-fdm_motor_pilot_depth-fdm_boolean_overlap,fdm_boolean_overlap)translate(q)circle(d=hls_mount_boss_d,$fn=48);}
 }
 }
 for(s=[-1,1])translate([s*pivot,0,0])slab(frame_top-1,washer_end-frame_top+2)circle(d=pivot_bore,$fn=48);
 // Blind pilots open at printed pillar tips; no roofs, no tiny emerging lip around an oblique through slot.
 // Real motor-ear slots retained; 5mm blind pilot leaves0.5mm beyond6mm screw through1.5mm ear.
 slab(hls_ear_y-drive_drop-hls_ear_thickness-fdm_motor_pilot_depth,fdm_motor_pilot_depth+1)hls_holes2d()hls_slots2d(hls_mount_clear_d);

}}
module retaining_plate(){difference(){slab(sleeve_end,fdm_frame_t)hull(){for(s=[-1,1])translate([s*pivot,0])circle(d=washer_d,$fn=64);}
 for(s=[-1,1])translate([s*pivot,0,0])slab(sleeve_end-1,fdm_frame_t+2)circle(d=pivot_bore,$fn=48);
}}
module pivot_washers() {for(s=[-1,1]) translate([s*pivot,0,0]) slab(sleeve_end,washer_t) difference(){circle(d=washer_d,$fn=64);circle(d=washer_bore,$fn=48);}}
module pivot_screws(){for(s=[-1,1])translate([s*pivot,0,0])slab(washer_end+pivot_nut_h+fdm_rod_tip-pivot_screw_len,pivot_screw_len)circle(d=pivot_screw_d,$fn=48);}
module pivot_nuts(){for(s=[-1,1])translate([s*pivot,0,0])for(y=[frame_top-pivot_nut_h,washer_end])slab(y,pivot_nut_h)difference(){circle(r=pivot_nut_af/sqrt(3),$fn=6);circle(d=pivot_nut_bore,$fn=48);}}

// Straight holes, external bought washers: no counterbore roof or floating perimeter.
pinion_face=-mesh_split-mesh_layer_gap-fdm_upper_lift;
module plate_screws(a=angle){hls_rotor(a)hls_plate_holes(){
 slab(hls_plate_y,pinion_face+drive_drop+fdm_plate_washer_t-hls_plate_y+.01)circle(d=hls_m2_shank_d,$fn=32);
 slab(pinion_face+drive_drop+fdm_plate_washer_t,hls_plate_head_h)circle(d=hls_plate_head_d-2*base_clear,$fn=32);
}}
module plate_washers(){hls_rotor()hls_plate_holes()slab(pinion_face,fdm_plate_washer_t)difference(){circle(d=fdm_plate_washer_d,$fn=64);circle(d=fdm_plate_washer_bore,$fn=48);}}
module capture_ring(){down()hls_rotor()slab(hls_plate_y,center_capture_t)difference(){circle(d=fdm_capture_metal_d,$fn=64);circle(d=fdm_capture_metal_bore,$fn=48);}}

module item(k){
 if(k=="left"||k=="right")placed(k=="left"?-1:1,angle)integral_jaw(k=="left"?half_tooth:0,k=="right");
 if(k=="base")base();if(k=="retaining_plate")retaining_plate();
 if(k=="pinion")stepped_pinion();
 if(k=="motor")down()motor();if(k=="stock_plate")down()stock_plate();
 if(k=="plate_screws")down()plate_screws();if(k=="plate_washers")plate_washers();
 if(k=="case_screws")down()reversed_case_screws();if(k=="center_screw")down()center_screw();
 if(k=="capture_washer")capture_ring();
 if(k=="pivot_screws")pivot_screws();if(k=="pivot_nuts")pivot_nuts();
 if(k=="cable")down()cable();
}
keys=["left","right","pinion","base","retaining_plate","motor","stock_plate","plate_screws","plate_washers","case_screws","center_screw","capture_washer","pivot_screws","pivot_nuts","cable"];
for(k=keys){
 if(part==str("viewer_",k))scale(scale_factor)mirror([0,1,0])item(k);
 if(part=="assembly"&&k!="cable")scale(scale_factor)mirror([0,1,0])item(k);
 if(part==str("print_",k))scale(scale_factor){
 if(k=="left"||k=="right")bed_down(plate/2)integral_jaw(k=="left"?half_tooth:0,k=="right");
 if(k=="pinion")bed_down(pinion_face)stepped_pinion(0);
 if(k=="base")bed_up(frame_top)base();
 if(k=="retaining_plate")bed_up(sleeve_end)retaining_plate();
 }
}
if(part=="viewer_right")echo(pivot=pivot*scale_factor);
module plate_tools(){hls_rotor()hls_plate_holes()slab(pinion_face+fdm_plate_washer_t+hls_plate_head_h,tool_len)circle(d=tool_d,$fn=32);}
module case_straight_tools() {down() slab(hls_ear_y-hls_ear_thickness-hls_case_head_h-tool_len,tool_len) case_probe_holes() circle(d=tool_d,$fn=32);}
module case_tools(){down()slab(hls_ear_y,tool_len)case_probe_holes()circle(d=tool_d,$fn=32);}
module center_tools() {down() hls_rotor() slab(hls_plate_y+center_capture_t+hls_center_head_h,tool_len) circle(d=tool_d,$fn=32);}
for(k=["plate_tools","case_tools","center_tools"]) if(part==str("viewer_",k)) scale(scale_factor) mirror([0,1,0]) {
 if(k=="plate_tools") plate_tools(); if(k=="case_tools") case_tools();if(k=="center_tools") center_tools();
}

if(part=="viewer_case_straight_tools") scale(scale_factor) mirror([0,1,0]) case_straight_tools();

module pivot_tools(){for(s=[-1,1]) translate([s*pivot,0,0]) slab(washer_end+pivot_nut_h,tool_len)difference(){circle(d=nut_tool_d,$fn=48);circle(d=pivot_bore,$fn=48);}}
// Hollow nut driver leaves room for exposed screw; its bore is not a forbidden solid.
module nut_tools(){for(s=[-1,1]) translate([s*pivot,0,0]) slab(frame_top-pivot_nut_h-tool_len,tool_len) difference(){circle(d=nut_tool_d,$fn=48);circle(d=pivot_bore,$fn=48);}}
for(k=["pivot_tools","nut_tools"]) if(part==str("viewer_",k)) scale(scale_factor) mirror([0,1,0]) {if(k=="pivot_tools") pivot_tools();if(k=="nut_tools") nut_tools();}


module reversed_case_screws(){
 slab(hls_ear_y-hls_ear_thickness,hls_ear_thickness)case_probe_holes()circle(d=hls_m2_shank_d,$fn=32);
 slab(hls_ear_y,hls_case_head_h)case_probe_holes()circle(d=hls_case_head_d,$fn=32);
}
