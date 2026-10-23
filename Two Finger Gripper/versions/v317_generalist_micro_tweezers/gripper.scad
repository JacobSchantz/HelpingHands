// Base 16 / Gripper 23: miniature derivative of Base 15 / Gripper 22.
// Involute tooth construction retained; axes captured between base and cap.
// CAD study, not load-qualified. Dimensions come only from params.json.
include <params.scad>
$fn=64;
part="assembly";
angle=0;
pitch=gear_m*gear_teeth/2;
spacing=2*pitch;
pivot=spacing;
gear_z=plate_z+plate_t+axial_gap;
cap_z=gear_z+gear_t+axial_gap;
shaft_top=cap_z+cap_socket-post_fit;
function inv_deg(a)=(tan(a)-a*PI/180)*180/PI;
function flank(r)=90/gear_teeth-gear_backlash/2/pitch*180/PI+inv_deg(gear_pressure_deg)-inv_deg(acos(min(1,pitch*cos(gear_pressure_deg)/r)));
module gear2d(phase=0) {
 rb=pitch*cos(gear_pressure_deg); rf=pitch-1.25*gear_m; ra=pitch+gear_m;
 r0=max(rb,rf); rr=[for(i=[0:10]) r0+(ra-r0)*i/10]; rin=rf-gear_m;
 union() {
  circle(r=rf);
  for(i=[0:gear_teeth-1]) rotate(phase+i*360/gear_teeth)
   polygon(concat([[rin*cos(-flank(r0)),rin*sin(-flank(r0))]],
    [for(r=rr) [r*cos(-flank(r)),r*sin(-flank(r))]],
    [for(i=[10:-1:0]) let(r=rr[i]) [r*cos(flank(r)),r*sin(flank(r))]],
    [[rin*cos(flank(r0)),rin*sin(flank(r0))]]));
 }
}
module dshaft(fit=0) {
 intersection() {circle(d=drive_d+2*fit);translate([-drive_d,-drive_d])square([drive_d+drive_flat+fit,2*drive_d]);}
}
module finger2d() {
 hull() {
  translate([0,pitch-gear_m]) circle(r=jaw_root_r);
  translate([spacing/2-tip_r,jaw_len]) circle(r=tip_r);
 }
}
module jaw(left=true) {
 translate([left?0:spacing,0,gear_z]) rotate([0,0,left?angle:-angle])
 linear_extrude(gear_t) difference() {
  union() {gear2d(left?0:180/gear_teeth);if(left) finger2d();else mirror([1,0])finger2d();}
  if(left) dshaft(drive_fit); else circle(d=post_d+2*post_fit);
 }
}
module case_holes() {for(x=[-case_holes_x/2,case_holes_x/2],y=[-case_hole_near,-case_hole_far])translate([x,y,0])children();}
module cap_holes() {for(p=[[-cap_post_x,cap_left_y],[cap_post_x,cap_right_y]])translate([p[0],p[1],0])children();}
module base() {
 difference() {
  union() {
   translate([-plate_w/2,-plate_back,plate_z])cube([plate_w,plate_back+plate_front,plate_t]);
   case_holes()cylinder(h=plate_z,r=rail_r);
   translate([spacing,0,plate_z+plate_t])cylinder(h=shaft_top-plate_z-plate_t,d=post_d);
   cap_holes()translate([0,0,plate_z+plate_t])cylinder(h=cap_z-plate_z-plate_t,r=cap_post_r);
  }
  translate([0,0,plate_z-1])linear_extrude(plate_t+2)circle(d=drive_d+2*post_fit);
  case_holes()translate([0,0,-1])cylinder(h=cap_z+cap_t+2,d=case_hole_d);
  cap_holes()translate([0,0,plate_z])cylinder(h=cap_z+cap_t+1,d=cap_pilot_d);
 }
}
module cap() {
 difference() {
  translate([-plate_w/2,-cap_back,cap_z])cube([plate_w,cap_back+plate_front,cap_t]);
  for(x=[0,spacing])translate([x,0,cap_z-.01])cylinder(h=cap_socket+.01,d=post_d+2*post_fit);
  cap_holes()translate([0,0,cap_z-1])cylinder(h=cap_t+2,d=cap_screw_d);
 }
}
module coupler() {
 rotate([0,0,angle])difference() {
  union() {
   translate([0,0,horn_top])cylinder(h=coupler_t,d=coupler_d);
   translate([0,0,horn_top+coupler_t-.01])linear_extrude(gear_z+gear_t-horn_top-coupler_t+.01)dshaft();
   translate([0,0,gear_z+gear_t-.01])cylinder(h=shaft_top-gear_z-gear_t+.01,d=post_d);
  }
  for(a=[0:90:270])rotate([0,0,horn_bolt_phase+a])translate([horn_pcd/2,0,horn_top-1])cylinder(h=coupler_t+2,d=horn_screw_d);
  for(a=[0:90:270])rotate([0,0,horn_bolt_phase+a])translate([horn_pcd/2,0,horn_top+coupler_t-(horn_csk_d-horn_screw_d)/2])cylinder(h=(horn_csk_d-horn_screw_d)/2+.01,d1=horn_screw_d,d2=horn_csk_d);
  translate([0,0,horn_top-.01])cylinder(h=horn_head_depth+.01,d=horn_head_d);
 }
}
module motor() {
 translate([-servo_w/2,-(servo_len-servo_near),-servo_depth])cube([servo_w,servo_len,servo_depth]);
 cylinder(h=horn_top,d=horn_d);
}
module horn_heads() {rotate([0,0,angle])for(a=[0:90:270])rotate([0,0,horn_bolt_phase+a])translate([horn_pcd/2,0,horn_top+coupler_t-(horn_csk_d-horn_screw_d)/2])cylinder(h=(horn_csk_d-horn_screw_d)/2,d1=horn_screw_d,d2=horn_csk_d);}
module case_heads() {case_holes()translate([0,0,plate_z+plate_t])cylinder(d=case_head_d,h=case_head_h);}
module cap_heads() {cap_holes()translate([0,0,cap_z+cap_t])cylinder(d=cap_head_d,h=cap_head_h);}
module cable() {translate([-plug_w/2,plug_y,-servo_depth-plug_back])cube([plug_w,plug_len,plug_back]);}
module selected() {
 if(part=="left")jaw(true);
 else if(part=="right")jaw(false);
 else if(part=="base")base();
 else if(part=="cap")cap();
 else if(part=="coupler")coupler();
 else if(part=="motor")motor();
 else if(part=="horn_heads")horn_heads();
 else if(part=="case_heads")case_heads();
 else if(part=="cap_heads")cap_heads();
 else if(part=="cable")cable();
 else if(part=="collision_hardware")union(){intersection(){horn_heads();union(){base();cap();case_heads();cap_heads();jaw(false);}}intersection(){union(){jaw(true);jaw(false);coupler();}union(){case_heads();cap_heads();}}}
 else if(part=="collision_jaws")intersection(){jaw(true);jaw(false);}
 else if(part=="collision_frame")intersection(){union(){jaw(true);jaw(false);coupler();}union(){base();cap();}}
 else if(part=="assembly") {
  color("#e7b842")jaw(true);color("#e7b842")jaw(false);
  color("#353e48")base();color("#697581")cap();color("#cc8e32")coupler();
  color("#3a3b40")motor();
  color("#999999") {horn_heads();case_heads();cap_heads();}
  color("#586b64",.25)cable();
 }
}
// Same gallery axes as the existing family: X width, Z jaw length, -Y stack.
if(part=="print_left")translate([0,0,-gear_z])jaw(true);
else if(part=="print_right")translate([0,0,-gear_z])jaw(false);
else if(part=="print_base")base();
else if(part=="print_cap")translate([0,0,cap_z+cap_t])rotate([180,0,0])cap();
else if(part=="print_coupler")translate([0,0,-horn_top])coupler();
else rotate([90,0,0])selected();

echo(pivot=pivot);
