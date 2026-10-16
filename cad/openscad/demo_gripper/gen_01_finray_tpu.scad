// label: fin-ray TPU fingers
// gen_01 · fin-ray TPU fingers. Copied from gen_00_slim_two_pairs.scad, then
// changed (voice-a9595f6b, second turn). Never edit an earlier generation:
// copy the newest gen_NN_*.scad to the next number and change the copy.
//
// What changed from gen_00: long, slim fingers that curve in to a point, the
// UMI / Generalist "data hands" look. Each jaw is now TWO prints:
//   * a stiff PETG ROOT: the same link, gear sector, pivot and horn holes as
//     gen_00, a short block your digit presses on (strap slot kept), and a
//     tongue on top;
//   * a TPU 95A FIN-RAY FINGER that slides over the tongue and is held by one
//     M3 bolt. Thin walls joined by slanted ribs: pressed by an object, the
//     gripping face wraps around it instead of pushing it away. That is the
//     compliance a fingertip pad gives you, so the jaw itself is the soft pad.
// One jaw pair instead of two (A / B): swapping the TPU fingers is the new
// interchangeable interface; the gen_00 jaws still fit the same hub.
// No camera on the gripper: vision is two stereo cameras at eye height
// (plans/hand_1_0.md "Mirror a human").
use <../hand_gripper/hand_gripper.scad>
part = "assembly";
variant = "A";   // unused; kept so the shared validate.py can pass it
angle = 18;
skew = 0;
print_pose = false;
sensor_pockets = false;  // reserve: four fingertip sensor seats, two per finger (not designed yet)
$fn = 48;
pivot = 12;
d = 10;                  // root depth behind the gripping face
w_jaw = [16, 22];        // thumb, fingers (Y, growing toward +Y from the flat Y=-5 bed face)
wall = 1.6;              // TPU wall: two 0.4 mm perimeters each side
rib = 1.2;
root_z = [24, 50];
tongue = [[2, 8], [50, 60]];   // x, z of the PETG tongue the finger slides over
tip_z = 108;
fit = 0.2;               // TPU pocket clearance round the tongue

// [piece, label, colour, explode offset, material, bed-oriented print]
PARTS = [
 ["left_finger", "Left fin-ray finger · TPU 95A", "#f0a43a", [-42,0,60], "TPU 95A", true],
 ["right_finger", "Right fin-ray finger · TPU 95A", "#f0a43a", [42,0,60], "TPU 95A", true],
 ["left_root", "Left root / thumb · PETG", "#3f6fb5", [-34,0,20], "PETG", true],
 ["right_root", "Right root / fingers · PETG", "#3f6fb5", [34,0,20], "PETG", true],
 ["hub", "Shared pivot hub · PETG", "#454e60", [0,0,-35], "PETG", false],
 ["pivot_insert", "Handheld pivot insert · PLA", "#bdc6d4", [0,-25,0], "PLA", false],
 ["so101_mount", "SO-101 cradle · arm only · PETG", "#454e60", [0,-50,-45], "PETG", false]
];

function jw(thumb) = w_jaw[thumb ? 0 : 1];
// Profile of the finger in the jaw's XZ plane (finger jaw, closed): flat
// gripping face at x=0.4, an outer flank that bulges then curves in to the tip.
module fin_outline() {
 polygon([[0.4,50],[d,50],[d,62],[13,70],[13.6,78],[12,88],[7.5,99],[3,106],[0.4,tip_z]]);
}
// Hollow between the solid base (z<64) and the solid tip (z>98), crossed by
// ribs that rise toward the gripping face: the fin-ray structure.
module fin2d() {
 difference() {
  fin_outline();
  intersection() { offset(delta=-wall) fin_outline(); translate([-1,64]) square([30,34]); }
 }
 intersection() {
  fin_outline();
  for(z=[69:7:95]) hull() { translate([0.4,z]) circle(rib/2); translate([15,z-5]) circle(rib/2); }
 }
}
// Same idea as gen_00's straight-flank teeth with the root extended so no
// half-phase tooth is left detached.
module connected_sector(thumb) {
 gear_sector2d(thumb ? 11.25 : 0);
 translate([12,0]) intersection() {
  circle(10.35);
  polygon([[0,0],for(a=[125:5:235]) 40*[cos(a),sin(a)]]);
 }
}
module slab(thumb, z0, z1, tip_w=10) {
 // full jaw width at z0, narrowing toward tip_w at z1; flat face stays at Y=-5
 hull() {
  translate([-1,-5,z0]) cube([20,jw(thumb),0.01]);
  translate([-1,-5,z1]) cube([20,tip_w,0.01]);
 }
}
module root(thumb, teeth=true) {
 w = jw(thumb);
 difference() {
  union() {
   xz() jaw_link2d(!thumb);
   if(teeth) xz() connected_sector(thumb);
   translate([0,w-5,0]) rotate([90,0,0]) linear_extrude(w)
     polygon([[0.4,root_z[0]+4],[d,root_z[0]],[d,root_z[1]],[0.4,root_z[1]]]);
   translate([tongue[0][0],-3,tongue[1][0]-0.01]) cube([tongue[0][1]-tongue[0][0],w-4,tongue[1][1]-tongue[1][0]]);
  }
  along_y(12,0,1.65,-6,40);
  if(!thumb) for(dx=[-1,1],dz=[-1,1]) {
   along_y(12+dx*4.95,dz*4.95,1.6,-6,6);
   along_y(12+dx*4.95,dz*4.95,2.9,2,6);
  }
  // Strap loop: a 20 mm strap threads the 3 x 22 mm slot and wraps the digit,
  // whose pad presses on the flat back of the root.
  translate([d-5,-6,root_z[0]+2]) cube([3,40,22]);
  along_y(5,55,1.65,-6,40);   // finger retaining bolt, M3
  if(sensor_pockets) translate([-0.6,(w-5)/2-6-1,root_z[1]-12]) cube([1.8,12,8]);
 }
}
module finger(thumb) {
 w = jw(thumb);
 difference() {
  intersection() {
   translate([0,w-5,0]) rotate([90,0,0]) linear_extrude(w) fin2d();
   union() { translate([-1,-5,49]) cube([20,w,13.01]); slab(thumb,62,tip_z); }
  }
  // pocket over the PETG tongue, open at the bottom only
  translate([tongue[0][0]-fit,-3-fit,tongue[1][0]-1]) cube([tongue[0][1]-tongue[0][0]+2*fit,w-4+2*fit,tongue[1][1]-tongue[1][0]+1+fit]);
  along_y(5,55,1.65,-6,40);
  if(sensor_pockets) translate([-0.6,-4,tip_z-14]) cube([1.8,8,8]);
 }
}
module jaw(thumb, teeth=true) { root(thumb,teeth); finger(thumb); }
module placed(q, thumb, a=0, teeth=true) {
 if(thumb) swing_thumb(a) mirror([1,0,0]) children();
 else swing_finger(a) children();
}
module placed_jaw(v, thumb, a=0, teeth=true) {
 placed("", thumb, a) jaw(thumb, teeth);
}
// Hub, insert: unchanged from gen_00.
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
module pair(a=angle) {
 for(t=[false,true]) placed("",t,a) { color("#3f6fb5") root(t); color("#f0a43a") finger(t); }
}
module physical(arm=false) { core(!arm,arm); pair(); if(arm) servo_ghost(); }
module raw_piece(q) {
 if(q=="left_finger") placed("",true) finger(true);
 else if(q=="right_finger") placed("",false) finger(false);
 else if(q=="left_root") placed("",true) root(true);
 else if(q=="right_root") placed("",false) root(false);
 else if(q=="hub") slim_hub();
 else if(q=="pivot_insert") pivot_insert();
 else if(q=="so101_mount") so101_mount();
}
function parked(q) = q=="so101_mount" ? [0,-85,0] : [0,0,0];
module project(explode=0) {
 for(r=PARTS) color(r[2]) translate(parked(r[0])+explode*r[3]) raw_piece(r[0]);
}
module hand_ghost() {
 // Schematic only; digit pads rest on the back of each root, over the strap.
 color([0.86,0.65,0.49,0.55]) {
  for(y=[3,15]) hull() {
   swing_finger(angle) translate([d+7,y,37]) sphere(8);
   translate([30,y,-20]) sphere(9);
  }
  hull() {
   swing_thumb(angle) translate([-d-9,3,37]) sphere(10);
   translate([-30,-8,-26]) sphere(12);
  }
  hull() {
   translate([-30,-8,-26]) sphere(12);
   translate([30,9,-20]) sphere(13);
   translate([5,-10,-68]) sphere(19);
  }
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
 // a finger must sit on its root without overlapping it
 for(t=[false,true]) intersection() { root(t); finger(t); }
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
