// Four interchangeable jaws, ONE common hub/arm interface. No camera on the
// gripper: vision is two stereo cameras at eye height (plans/hand_1_0.md §3).
// Reuse the existing mechanism, rather than maintaining a second gear/mount.
use <../hand_gripper/hand_gripper.scad>
part = "assembly";
variant = "A";
angle = 18;
skew = 0;
print_pose = false;
sensor_pockets = false;  // reserve: four fingertip sensor seats, two per jaw (not designed yet)
$fn = 48;
// Interface contract inherited from hand_gripper: 24 mm pivot spacing,
// 10 mm jaw root, M3 pin, 9.9 mm horn square, 30 degree opening stop.
pivot = 12;
// Slim jaw: 10 mm deep behind the gripping face (was 18), 16 / 22 mm wide
// (was 24 / 32). The finger pad presses straight on the back of the jaw.
pad_depth = 10;
pad_w = [16, 22];  // thumb, fingers

PARTS = [
 ["a_left", "A · left / thumb", "#efb739", [-38,0,22]],
 ["a_right", "A · right / fingers", "#efb739", [38,0,22]],
 ["b_left", "B · left / thumb (swap pair)", "#36b2b0", [-24,0,22]],
 ["b_right", "B · right / fingers (swap pair)", "#36b2b0", [24,0,22]],
 ["hub", "Shared pivot hub", "#454e60", [0,0,-35]],
 ["pivot_insert", "Handheld pivot insert · remove for servo", "#bdc6d4", [0,-25,0]],
 ["so101_mount", "Shared SO-101 cradle · arm only", "#454e60", [0,-50,-45]]
];

// Flat bed side is Y=-5 for every jaw. Extra finger width grows only toward
// +Y, avoiding the unsupported underside of a centred wide pad.
function tip(v) = v == "A" ? 72 : 84;
module pad2d(v) {
 d = pad_depth;
 polygon(v == "A"
   ? [[0.4,32],[d,28],[d,64],[5,72],[0.4,72]]
   : [[0.4,32],[d,28],[d,58],[6,72],[2,84],[0.4,84]]);
}
module pad(v, thumb) {
 width = pad_w[thumb ? 0 : 1];
 intersection() {
  translate([0,width-5,0]) rotate([90,0,0]) linear_extrude(width) pad2d(v);
  // Taper in Y toward the beak tip. The flat printing face stays at -5.
  hull() {
   translate([-1,-5,28]) cube([pad_depth+2,width,30]);
   translate([-1,-5,tip(v)]) cube([pad_depth+2,8,0.1]);
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
// Two 12 x 8 mm seats per jaw on the gripping face, 1.2 mm deep, with a
// 2 mm lead channel down the face. Off by default: room is kept, nothing cut.
module sensor_seats(v, thumb) {
 w = pad_w[thumb ? 0 : 1];
 for(z=[tip(v)-24, tip(v)-38]) translate([-0.6,(w-5)/2-6-1,z]) cube([1.8,12,8]);
 translate([-0.6,(w-5)/2-6-1+5,30]) cube([1.8,2,tip(v)-22-30]);
}
module jaw(v, thumb, teeth=true) {
 w = pad_w[thumb ? 0 : 1];
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
  // One through-slot is the strap loop: a 20 mm strap threads the
  // 22 x 3 mm slot and wraps the digit on the outer face.
  translate([pad_depth-5,-6,38]) cube([3,40,22]);
  if(v=="A") for(z=[34:4:66]) translate([-0.6,-6,z]) cube([1.6,40,1]);
  if(v=="B") {
   // Opposing V seats for a rod, plus a gated recess in the thumb jaw only.
   translate([0,35,66]) rotate([90,0,0]) linear_extrude(42)
     polygon([[-1,-4],[4,0],[-1,4]]);
   if(thumb) along_y(0,44,3.5,-6,35);
  }
  if(sensor_pockets) sensor_seats(v,thumb);
 }
}
module placed_jaw(v,thumb,a=0,teeth=true) {
 if(thumb) swing_thumb(a) mirror([1,0,0]) jaw(v,true,teeth);
 else swing_finger(a) jaw(v,false,teeth);
}
// Hub: the inherited cheek planes, pivots, horn port, bolts and nut trap, but
// a rounded profile hugging the pivots and the two bridge bolts instead of
// the old 42 mm square-cornered block. The SO-101 cradle still bolts on as-is.
module slim_hub() {
 intersection() {
  hub();
  rotate([90,0,0]) linear_extrude(30, center=true) hull() {
   translate([-pivot,0]) circle(9);
   translate([pivot,0]) circle(15.5);
   for(x=[-15,15]) translate([x,-22]) circle(5);
  }
 }
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
module core(insert=true,arm=false) {
 color("#454e60") slim_hub();
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
 else if(q=="hub") slim_hub();
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
 // Schematic only; digit pads rest on the back of each jaw, over the strap.
 color([0.86,0.65,0.49,0.55]) {
  for(y=[3,15]) hull() {
   swing_finger(angle) translate([pad_depth+7,y,49]) sphere(8);
   translate([30,y,-12]) sphere(9);
  }
  hull() {
   swing_thumb(angle) translate([-pad_depth-9,3,49]) sphere(10);
   translate([-30,-8,-20]) sphere(12);
  }
  hull() {
   translate([-30,-8,-20]) sphere(12);
   translate([30,9,-12]) sphere(13);
   translate([5,-10,-62]) sphere(19);
  }
 }
 // Strap schematic, actual fabric hardware is NOT a printable part.
 color([0.22,0.25,0.32,0.8]) for(t=[false,true]) {
  if(t) swing_thumb(angle) mirror([1,0,0]) strap(true);
  else swing_finger(angle) strap(false);
 }
}
module strap(t) {
 c = [pad_depth+3, t ? 3 : 8, 49];
 difference() {
  translate(c) scale([10,t?11:16,1]) cylinder(h=20,r=1,center=true);
  translate(c) scale([8.5,t?9.5:14.5,1]) cylinder(h=22,r=1,center=true);
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
  union() { slim_hub(); so101_mount(); servo_ghost(); pivot_insert(); }
 }
}
else if(part=="gearclash") intersection() {
 placed_jaw(variant,false,angle); placed_jaw(variant,true,angle+skew);
}
else if(part=="fitclash") {
 intersection() { slim_hub(); so101_mount(); }
 intersection() { so101_mount(); servo_ghost(); }
}
else if(part=="insertclash") intersection() { pivot_insert(); slim_hub(); }
else if(part=="parts") for(r=PARTS) echo(r);
else if(print_pose) rotate([90,0,0]) translate([0,5,0]) raw_piece(part);
else translate(parked(part)) raw_piece(part);
