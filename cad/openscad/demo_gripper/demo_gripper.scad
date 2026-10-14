// Four interchangeable jaws, ONE common hub/camera/arm interface.
// Reuse the existing mechanism, rather than maintaining a second gear/mount.
use <../hand_gripper/hand_gripper.scad>
part = "assembly";
variant = "A";
angle = 18;
skew = 0;
print_pose = false;
$fn = 48;
// Interface contract inherited from hand_gripper: 24 mm pivot spacing,
// 10 mm jaw root, M3 pin, 9.9 mm horn square, 30 degree opening stop.
pivot = 12;

PARTS = [
 ["a_left", "A · left / thumb", "#efb739", [-38,0,22]],
 ["a_right", "A · right / fingers", "#efb739", [38,0,22]],
 ["b_left", "B · left / thumb (swap pair)", "#36b2b0", [-24,0,22]],
 ["b_right", "B · right / fingers (swap pair)", "#36b2b0", [24,0,22]],
 ["hub", "Shared pivot hub", "#454e60", [0,0,-35]],
 ["camera", "Shared camera bracket", "#79869b", [0,45,-20]],
 ["pivot_insert", "Handheld pivot insert · remove for servo", "#bdc6d4", [0,-25,0]],
 ["so101_mount", "Shared SO-101 cradle · arm only", "#454e60", [0,-50,-45]]
];

// Flat bed side is Y=-5 for every jaw. Extra finger width grows only toward
// +Y, avoiding the unsupported underside of a centred wide pad.
module pad2d(v) {
 polygon(v == "A"
   ? [[0.4,32],[18,28],[18,62],[9,72],[0.4,72]]
   : [[0.4,32],[18,28],[18,56],[11,70],[3,84],[0.4,84]]);
}
module pad(v, thumb) {
 width = thumb ? 24 : 32;
 intersection() {
  translate([0,width-5,0]) rotate([90,0,0]) linear_extrude(width) pad2d(v);
  // Taper in Y toward the beak tip. The flat printing face stays at -5.
  hull() {
   translate([-1,-5,28]) cube([22,width,30]);
   translate([-1,-5,v=="A" ? 72 : 84]) cube([22,10,0.1]);
  }
 }
}
// Existing straight-flank teeth started at the faceted root-circle tangent;
// the half-tooth phase could leave teeth detached. Extend the root 0.225 mm
// into their bases (still below the opposing 13.5 mm tooth tip clearance).
module connected_sector(thumb) {
 gear_sector2d(thumb ? 11.25 : 0);
 translate([12,0]) intersection() {
  circle(10.35);
  polygon([[0,0],for(a=[125:5:235]) 40*[cos(a),sin(a)]]);
 }
}
module jaw(v, thumb, teeth=true) {
 difference() {
  union() {
   xz() jaw_link2d(!thumb);
   if(teeth) xz() connected_sector(thumb);
   pad(v,thumb);
  }
  along_y(12,0,1.65,-6,40);
  if(!thumb) for(dx=[-1,1],dz=[-1,1]) {
   along_y(12+dx*4.95,dz*4.95,1.6,-6,6);
   along_y(12+dx*4.95,dz*4.95,2.9,2,6);
  }
  // A single through-slot forms a strong integral belt loop; 20 mm strap
  // threads through the 22 x 3 mm slot and around the digit on the outside.
  translate([9,-6,36]) cube([3,40,22]);
  // Broad shallow thumb/finger saddle on the OUTER face, behind contact.
  translate([23.5,thumb ? 7 : 11,47]) scale([8,thumb ? 12 : 18,16]) sphere(1);
  if(v=="A") for(z=[34:4:66]) translate([-0.6,-6,z]) cube([1.6,40,1]);
  if(v=="B") {
   // Opposing V seats for a rod, plus a gated recess in the thumb jaw only.
   translate([0,35,66]) rotate([90,0,0]) linear_extrude(42)
     polygon([[-1,-4],[4,0],[-1,4]]);
   if(thumb) along_y(0,40,4.5,-6,35);
  }
 }
}
module placed_jaw(v,thumb,a=0,teeth=true) {
 if(thumb) swing_thumb(a) mirror([1,0,0]) jaw(v,true,teeth);
 else swing_finger(a) jaw(v,false,teeth);
}
// Small keyed flange supports the driven pivot in the hub's large horn port.
// Its extra bridge screw prevents rotation. Remove insert + pivot bolt for arm.
module pivot_insert() {
 difference() {
  union() {
   along_y(12,0,12.05,-10.4,-5.5);
   translate([0,-10.4,0]) rotate([90,0,0]) linear_extrude(2.4)
     hull() { translate([12,0]) circle(14); translate([15,-22]) circle(5); }
  }
  along_y(12,0,1.65,-14,-5);
  along_y(15,-22,1.65,-14,-5);
 }
}
// Raise the optical centre above the pivot: the old rearward camera could
// see closed tips but the widening jaw faces hid them during opening.
cam_center = [0,65,20];
cam_target = [0,0,60];
module shared_camera() {
 direction=(cam_target-cam_center)/norm(cam_target-cam_center);
 difference() {
  union() {
   translate([-21,10.4,-26]) cube([42,4,12]);
   for(s=[-1,1]) hull() {
    translate([s*7,14.4,-22]) sphere(4);
    translate(cam_center+[s*12,0,0]-direction*4) sphere(3.5);
   }
   translate(cam_center) orient(direction) translate([-18,-18,-6]) cube([36,36,3]);
  }
  for(s=[-1,1]) along_y(s*15,-22,1.65,0,30);
  translate(cam_center) orient(direction) {
   translate([0,0,-12]) cylinder(d=14,h=12);
   for(x=[-14,14],y=[-14,14]) translate([x,y,-12]) cylinder(d=2.2,h=12);
  }
 }
}
module core(insert=true,arm=false) {
 color("#454e60") hub();
 color("#79869b") shared_camera();
 if(insert) color("#bdc6d4") pivot_insert();
 if(arm) color("#454e60") so101_mount();
}
module pair(v,a=angle) {
 color(v=="A" ? "#efb739" : "#36b2b0")
 for(t=[false,true]) placed_jaw(v,t,a);
}
module physical(v=variant,arm=false) { core(!arm,arm); pair(v); if(arm) servo_ghost(); }
module raw_piece(q) {
 if(q=="a_left") placed_jaw("A",true);
 else if(q=="a_right") placed_jaw("A",false);
 else if(q=="b_left") placed_jaw("B",true);
 else if(q=="b_right") placed_jaw("B",false);
 else if(q=="hub") hub();
 else if(q=="camera") shared_camera();
 else if(q=="pivot_insert") pivot_insert();
 else if(q=="so101_mount") so101_mount();
}
// In the app A occupies the shared hub; the alternate B pair sits to its right.
// The arm-only cradle is parked behind, not intersecting the handheld insert.
function parked(q) = q=="b_left" || q=="b_right" ? [140,0,0]
                    : q=="so101_mount" ? [0,-85,0] : [0,0,0];
module project(explode=0) {
 for(r=PARTS) color(r[2]) translate(parked(r[0])+explode*r[3]) raw_piece(r[0]);
}
module hand_ghost() {
 // Schematic only; digit endpoints sit on the new outside saddles.
 color([0.86,0.65,0.49,0.55]) {
  for(y=[3,20]) hull() {
   swing_finger(angle) translate([26,y,47]) sphere(9);
   translate([38,y,-12]) sphere(10);
  }
  hull() {
   swing_thumb(angle) translate([-27,7,47]) sphere(11);
   translate([-35,-8,-20]) sphere(13);
  }
  hull() {
   translate([-35,-8,-20]) sphere(13);
   translate([38,12,-12]) sphere(14);
   translate([5,-10,-68]) sphere(21);
  }
 }
 // Strap schematic, actual fabric hardware is NOT a printable part.
 color([0.22,0.25,0.32,0.8]) for(t=[false,true]) {
  if(t) swing_thumb(angle) mirror([1,0,0]) strap(true);
  else swing_finger(angle) strap(false);
 }
}
module strap(t) {
 difference() {
  translate([20,t?7:11,47]) scale([16,t?16:22,1]) cylinder(h=20,r=1,center=true);
  translate([20,t?7:11,47]) scale([14,t?14:20,1]) cylinder(h=22,r=1,center=true);
 }
}
if(part=="assembly") project();
else if(part=="exploded") project(1);
else if(part=="in_hand") { physical(); hand_ghost(); }
else if(part=="on_arm") physical(arm=true);
else if(part=="pair") physical();
else if(part=="clash") {
 intersection() { placed_jaw(variant,true,angle,false); placed_jaw(variant,false,angle,false); }
 intersection() {
  union() { placed_jaw(variant,true,angle,false); placed_jaw(variant,false,angle,false); }
  union() { hub(); shared_camera(); so101_mount(); servo_ghost(); pivot_insert(); }
 }
}
else if(part=="gearclash") intersection() {
 placed_jaw(variant,false,angle); placed_jaw(variant,true,angle+skew);
}
else if(part=="fitclash") {
 intersection() { hub(); shared_camera(); }
 intersection() { so101_mount(); shared_camera(); }
 intersection() { servo_ghost(); shared_camera(); }
 intersection() { hub(); so101_mount(); }
 intersection() { so101_mount(); servo_ghost(); }
}
else if(part=="insertclash") intersection() { pivot_insert(); union() { hub(); shared_camera(); } }
else if(part=="parts") for(r=PARTS) echo(r);
else if(print_pose) rotate([90,0,0]) translate([0,5,0]) raw_piece(part);
else translate(parked(part)) raw_piece(part);
