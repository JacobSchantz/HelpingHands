/* GENERALIST GRIPPER / GENERATION 4 — original symmetric pincher concept.
   ONE centered servo envelope, one crank/yoke, ONE opposed mirror jaw pair.
   Units mm. No force sensor, straps, hard cuffs, or claims of selected hardware fit. */
$fn=64;
part="assembly"; // assembly | hub | jaw | yoke | crank | motor | collision | none | viewer_...
angle=15;
show_motor=true;
min_angle=0;
max_angle=22;
pivot=16;
jaw_depth=18;
channel_radius=10;
channel_depth=3;
yoke_y=-14;
yoke_depth=4;
crank_y=-20;
crank_z=-30;
crank_r=6;
slider_mid=2+10*sin(max_angle);
slot_base=crank_z-slider_mid;

function slider_z(a)=2+20*sin(a);
function crank_angle(a)=asin((slider_z(a)-slider_mid)/crank_r);
function follower(a)=[pivot-10*cos(a)-10*sin(a),10*sin(a)-10*cos(a)];
function gripping_gap(a,z=60,x=-7)=2*(pivot+x*cos(a)+z*sin(a));
module ycyl(d,h) {rotate([90,0,0]) cylinder(d=d,h=h,center=true);}
module xz(h) {rotate([90,0,0]) linear_extrude(h,center=true) children();}
module round_box(size,r=1) {
    hull() for(x=[-1,1],y=[-1,1],z=[-1,1])
        translate([x*(size[0]/2-r),y*(size[1]/2-r),z*(size[2]/2-r)]) sphere(r=r,$fn=16);
}
module capsule2(a,b,r) {hull(){translate(a) circle(r=r);translate(b) circle(r=r);}}
module placed(s=1,a=angle) {
    translate([s*pivot,0,0]) rotate([0,s*a,0]) if(s<0) mirror([1,0,0]) children(); else children();
}
function bezier(p0,p1,p2,p3,t)=[for(k=[0,1]) pow(1-t,3)*p0[k]+3*pow(1-t,2)*t*p1[k]+3*(1-t)*t*t*p2[k]+t*t*t*p3[k]];
function curve(p0,p1,p2,p3)=[for(i=[0:24])bezier(p0,p1,p2,p3,i/24)];
module smooth_finger_2d() {
    // Continuous rounded contour. Near-closure is about 1.2 mm at the inward tip.
    polygon(concat(
      curve([5,13],[9,20],[11,29],[10,40]),
      curve([10,40],[10,62],[4,79],[-3,88]),
      curve([-3,88],[-8,96],[-16,94],[-15.4,83]),
      curve([-15.4,83],[-14.8,65],[-14.4,43],[-13.8,28]),
      curve([-13.8,28],[-13,20],[-7,15],[-4,12])));
}
function groove_x(z)=10-0.0042*(z-38)*(z-38);
module finger_groove() {
    // A continuous longitudinal outer channel: tip toward pivot, not a crosswise hole.
    for(z=[28:1:81]) hull() for(q=[z,z+1])
        translate([groove_x(q)+channel_radius-channel_depth,0,q]) sphere(r=channel_radius,$fn=96);
}
module jaw() {
    difference() {
        union() {
            xz(jaw_depth) union(){circle(r=7);smooth_finger_2d();capsule2([0,4],[0,19],4.5);}
            // Rear crank follower: integral boss/stud; separate removable retention not selected.
            xz(9) capsule2([0,0],[-10,-10],2.7);
            translate([-10,-6.75,-10]) ycyl(5.5,8.5); // support reaches the rear face of the jaw
            translate([-10,-14,-10]) ycyl(3,8);  // d3 follower in a 3.5 mm cam slot
        }
        ycyl(3.4,48);
        finger_groove();
        // Two through-Y tie slots near the OUTER spine; the inner gripping face stays unbroken.
        for(z=[34,66]) translate([groove_x(z)-6,0,z]) xz(32)
            capsule2([0,-1],[0,1],1.4);
    }
}
module cam_slots() {
    // Right slot z=x-18; left is its exact X reflection. Follower radius 1.5, slot radius 1.75.
    for(s=[-1,1]) xz(12) capsule2([s*1.5,1.5-18],[s*7.5,7.5-18],1.75);
}
module yoke() {
    difference() {
        translate([0,yoke_y,0]) xz(yoke_depth)
            offset(r=1,$fn=24) offset(delta=-1) polygon([
              [-10,-40], [10,-40], [10,-8], [7,-8], [0,-13], [-7,-8], [-10,-8]]);
        translate([0,yoke_y,0]) cam_slots();
        translate([0,yoke_y,slot_base]) xz(12) capsule2([-7,0],[7,0],1.75);
        // Large center opening reduces mass without interrupting guide edges.
        translate([0,yoke_y,-24]) xz(12) offset(r=1) square([10,8],center=true);
    }
}
module crank() {
    // Own blank output interface: unselected horn/spline. No fake second motor.
    difference() {
        union() {
            ycyl(17,3);
            translate([0,-2.5,0]) ycyl(10,4);
            translate([crank_r,4,0]) ycyl(3,8);
        }
        ycyl(2.5,18); // unselected horn retainer pilot only, NOT a servo spline
    }
}
module guide(s) {
    // Open-front L guide: 0.3 mm side/rear clearance; insert yoke along Y.
    // Selected crank-pin retainer must hold the yoke against these guide backs.
    difference() {
        translate([s*12.5,yoke_y,-18]) round_box([7,8,18],0.6);
        translate([s*5.15,-8.15,-18]) cube([10.3,16.3,24],center=true);
    }
}
module stop_lugs() {
    // Slider shoulders stop a little outside the intended 0..22 degree interval.
    // Pin in horizontal slot must still move freely at those intended limits.
    for(s=[-1,1]) {
        translate([s*8,-19.5,slider_z(0)-40-0.35-1]) cube([4,15,2],center=true);
        translate([s*8,-19.5,slider_z(22)-8+0.35+1]) cube([4,15,2],center=true);
    }
}
module hub() {
    union() {
        for(y=[12,-24]) difference() {
            translate([0,y,0]) xz(4) union() {
                capsule2([-pivot,0],[pivot,0],6);
                for(s=[-1,1]) capsule2([s*23,-5],[s*23,-42],3);
                capsule2([-23,-42],[23,-42],3);
                if(y<0) hull(){translate([0,crank_z]) circle(r=11);translate([0,-42]) square([30,5],center=true);}
            }
            for(s=[-1,1]) translate([s*pivot,y,0]) ycyl(3.4,8);
            if(y<0) translate([0,y,crank_z]) ycyl(10.4,8);
        }
        // Front/back cheek spacers stay below the jaw sweep.
        for(s=[-1,1]) translate([s*23,-6,-42]) round_box([6,40,6],0.7);
        for(s=[-1,1]) guide(s);
        // Bridge guide rails to the rear cheek, outside the crank disk and jaw sweep.
        for(s=[-1,1]) translate([s*18.5,-20,-18]) cube([13,10,8],center=true);
        stop_lugs();
    }
}
module motor() {
    // One centered 36 x 32 x 30 volume only. Motor/horn/mount selection pending.
    translate([0,-43,crank_z]) round_box([36,32,30],2);
    translate([0,-25,crank_z]) ycyl(6,5);
}
module piece(q,a=angle) {
    if(q=="hub") hub();
    if(q=="left") placed(-1,a) jaw();
    if(q=="right") placed(1,a) jaw();
    if(q=="yoke") translate([0,0,slider_z(a)]) yoke();
    if(q=="crank") translate([0,crank_y,crank_z]) rotate([0,-crank_angle(a),0]) crank();
    if(q=="motor") motor();
}
module moving(a=angle) {
    for(s=[-1,1]) placed(s,a) jaw();
    translate([0,0,slider_z(a)]) yoke();
    translate([0,crank_y,crank_z]) rotate([0,-crank_angle(a),0]) crank();
}
module clash(a=angle) {
    intersection(){hub();moving(a);}
    intersection(){placed(-1,a) jaw();placed(1,a) jaw();}
    intersection(){for(s=[-1,1]) placed(s,a) jaw();translate([0,0,slider_z(a)]) yoke();}
    intersection(){translate([0,0,slider_z(a)]) yoke();translate([0,crank_y,crank_z]) rotate([0,-crank_angle(a),0]) crank();}
}
assert(angle>=0 && angle<=22,"Angle outside intended motion");
echo(jaw_angle_deg=angle,slider_z_mm=slider_z(angle),servo_angle_deg=crank_angle(angle));
if(part=="assembly") {
    color("#3d4653") piece("hub");
    color("#efb83b") {piece("left");piece("right");}
    color("#abb4bc") piece("yoke");
    color("#687887") piece("crank");
    if(show_motor) color("#252e38") piece("motor");
}
if(part=="jaw") jaw();
if(part=="hub") hub();
if(part=="yoke") yoke();
if(part=="crank") crank();
if(part=="motor") motor();
if(part=="collision") clash();
for(q=["hub","left","right","yoke","crank","motor"]) if(part==str("viewer_",q)) piece(q);
