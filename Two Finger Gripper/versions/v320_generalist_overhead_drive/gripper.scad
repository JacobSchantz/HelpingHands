// Base 19, from Base 15; unchanged Gripper 22 and Mount 2.
include <source.scad>
include <so_hub.scad>
part="assembly";
// +Y is dorsal: orient this side above the operator's hand in use.
cable_low=base_y0-sts_depth-sts_conn_h-sts_plug_len;
lift=plate/2+overhead_gap-cable_low;
shoulder_y=plate/2+fit;
so_horn_z=-so_neck_h;
so_head_z=hub_t-(hub_t+so_neck_h-(so_screw_len-so_screw_bite));
module up() {translate([0,lift,0]) children();}
module hex2d(clear=0) {circle(r=post_d/2+clear,$fn=6);}
module low_driver() {
 difference() {
  union() {
   slab(web_y0,slide_h) hub2d();
   handle_body();
  }
  finger_pocket();
  slab(web_y0-1,slide_h+2) hex2d(key_fit);
  slab(web_y1,slide_h) circle(d=post_d+2*base_clear,$fn=96);
  // Screw enters from below, head flush to the original web underside.
  // Retaining screw bears on separate washer spanning this hex socket.
 }
}
module shaft_gear(phase=0,right=true) {
 difference() {
  union() {
   up() gear_solid(phase,right);
   // Journal/shoulder is above finger loop. Shaft steps down through loop.
   slab(shoulder_y,lift+gear_y0-shoulder_y+0.01) circle(d=shaft_d,$fn=96);
   slab(web_y1,shoulder_y-web_y1+0.01) circle(d=post_d,$fn=96);
   slab(web_y0+fit,web_t-fit+0.01) hex2d();
   up() slab(gear_y1-0.01,post_y1-gear_y1+0.01) circle(d=post_d,$fn=96);
  }
  slab(web_y0+fit-0.01,shaft_pilot_depth) circle(d=shaft_pilot_d,$fn=32);
 }
}
module new_base() {
 up() difference() {
  // Keep plate/servo seat, wrist tab and corner pillars; delete fixed pivot posts.
  difference() {
   base();
   for(s=[-1,1]) translate([s*pivot,0,0]) slab(base_y1-0.01,post_y1-base_y1+1) circle(d=post_d+0.02,$fn=64);
  }
  for(s=[-1,1]) translate([s*pivot,0,0]) slab(base_y0-1,base_t+2) circle(d=shaft_d+2*shaft_fit,$fn=96);
 }
}
module washer() {
 difference() {
  slab(web_y0-washer_t,washer_t) circle(d=washer_d,$fn=96);
  csk(web_y0-washer_t,driver_head_d+2*key_fit,0,down=false,len=washer_t+1);
 }
}
module new_bracket() {
 difference() {
  union() {
   up() bracket();
   translate([0,0,tool_z]) linear_extrude(foot_t) hull() {
    translate(axis_c) circle(d=tool_d,$fn=96);
    translate(axis_c+[0,lift]) circle(d=tool_d,$fn=96);
   }
  }
  translate([axis_c[0],axis_c[1],tool_z-1]) for(i=[0:3]) rotate(tool_screw_phase_deg+i*90) translate([tool_screw_pcd/2,0,0]) cylinder(d=foot_pilot_d,h=foot_t+2,$fn=32);
 }
}
module moving(q,k,a=angle) {
 if(q=="right") placed(1,a) {if(k=="gear") shaft_gear();else if(k=="driver") low_driver();else washer();}
 if(q=="left") placed(-1,a) {if(k=="gear") shaft_gear(half_tooth,false);else if(k=="driver") low_driver();else washer();}
}
module item(k,a=angle) {
 if(k=="left"||k=="right") piece(k,a);
 if(k=="left_gear"||k=="right_gear") moving(k=="left_gear"?"left":"right","gear",a);
 if(k=="left_driver"||k=="right_driver") moving(k=="left_driver"?"left":"right","driver",a);
 if(k=="left_washer"||k=="right_washer") moving(k=="left_washer"?"left":"right","washer",a);
 if(k=="base") new_base();
 if(k=="pinion") up() pinion(a);
 if(k=="top_plate") up() top_plate();
 if(k=="motor") up() motor(a);
 if(k=="cable") up() sts_cable();
 if(k=="bracket") new_bracket();
 if(k=="tool_plate") mount_tool_plate();
 if(k=="hub") translate([axis_c[0],axis_c[1],hub_z0]) so_hub();
}
keys=["left","right","left_driver","right_driver","left_washer","right_washer","left_gear","right_gear","pinion","base","top_plate","bracket","tool_plate","hub","motor"];
for(k=keys) {
 if(part==str("viewer_",k)) item(k);
 if(part=="assembly") color(k=="left"||k=="right"?"#efb83b":k=="motor"?"#a3a8ad":"#35383e") item(k);
}
if(part=="viewer_cable") item("cable");
if(part=="viewer_right") {echo(pivot=pivot); echo(lift=lift);echo(so101_horn=[axis_c[0],axis_c[1],hub_z0+so_horn_z]);}
if(part=="finger_holes") echo(loop_holes=len([for(h=holes_px) if(in_loop(h)) 1]));
assert(shaft_d>post_d+2,"Shoulder must retain finger loop");
assert(shaft_d+2*shaft_fit<2*bush_r,"Bearing wall too thin");
module retention_probes(a=angle) {
 for(s=[-1,1]) placed(s,a) {
  translate([0,web_y0-washer_t,0]) rotate([-90,0,0]) cylinder(d1=driver_head_d,d2=3,h=(driver_head_d-3)/2,$fn=32);
  slab(web_y0-washer_t,washer_t+fit) circle(d=3,$fn=32);
 }
}
module horn_tools(a=angle) {up() bolt_access(a);}
if(part=="viewer_retention_screws") retention_probes();
if(part=="viewer_horn_tools") horn_tools();
