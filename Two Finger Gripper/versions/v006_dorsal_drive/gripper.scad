/* GENERALIST GRIPPER — GENERATION 6 / original inspection CAD, mm.
   Everything that is not a finger lives ABOVE the hand: housing, gears and servo sit
   on the back of the hand (+Y), and only two pivot columns drop into the thumb-index
   plane. Fingers copy the Generalist target photo: yellow crescent
   plates with rows of small blind hex perforations, a scalloped inner grip edge, a small
   step before the blade, a solid pad with a grey dot, and a small black point.
   ONE servo -> right gear -> left gear, 1:1 counter-rotation. No sensor.
   Axes: X across (right jaw +X), Z along the fingers (tips +Z), +Y = dorsal / up. */
$fn=48;
part="assembly"; // assembly | left | right | left_gear | right_gear | left_tip | right_tip | housing_base | housing_lid | motor | collision | none | viewer_...
angle=15;
show_motor=true;
max_angle=22;
teeth=24;
module_m=1.2;
pitch_r=teeth*module_m/2;
pivot=pitch_r;
pressure=20;
plate=10;                 // finger plate thickness, centred on Y=0 (the hand plane)
lower_plate=[13,17];      // housing floor, Y range
gear_y=[18,23];           // gear layer between housing plates
upper_plate=[24,28];      // housing roof
column_d=10;              // jaw pivot column, runs in the housing floor bore
bore_clear=0.6;
shoulder_d=14;            // stops the jaw rising into the housing floor
hex_af=8;                 // jaw column hex that keys the gear
hex_clear=0.3;
pin_d=4;                  // steel axle pin, not modeled
cell=2.4;                 // perforation: small blind hex pockets, across flats
cell_wall=1.5;
pocket=3.5;               // pocket depth from each face; leaves a 3 mm centre web
rim=1.2;                  // solid border around the perforated band
tip_start=104;            // small black tip insert begins here
magnets=[[7,52],[-3.5,84]];    // grey dots in the photos; 4x2 mm disc pockets
pads=[[[-12,78],[6,92]]];      // solid flat on the lower blade around the lower dot (ziptie_1)
straps=[[11,22],[13,40]];      // finger strap slots near the outer edge
tip_hole=[-9.5,99];            // small through hole near the point (target photo)

function inv(t)=tan(t)-t*PI/180;
function flank_angle(r)=90/teeth+(inv(pressure)-inv(acos(pitch_r*cos(pressure)/r)))*180/PI;
function polar(r,a)=[r*cos(a),r*sin(a)];
function bezier(p0,p1,p2,p3,t)=[for(k=[0,1]) pow(1-t,3)*p0[k]+3*pow(1-t,2)*t*p1[k]+3*(1-t)*t*t*p2[k]+t*t*t*p3[k]];
function curve(p0,p1,p2,p3)=[for(i=[0:15])bezier(p0,p1,p2,p3,i/16)];
module xz(h,c=true) {rotate([-90,0,0]) mirror([0,1,0]) linear_extrude(h,center=c) children();}
module ycyl(d,y0,y1,fn=48) {translate([0,y0,0]) rotate([-90,0,0]) cylinder(d=d,h=y1-y0,$fn=fn);}
module round_box(size,r=1) {
    hull() for(x=[-1,1],y=[-1,1],z=[-1,1])
        translate([x*(size[0]/2-r),y*(size[1]/2-r),z*(size[2]/2-r)]) sphere(r=r,$fn=16);
}
module gear2d(phase=0) {
    rb=pitch_r*cos(pressure);ra=pitch_r+module_m;rr=pitch_r-1.25*module_m;
    rotate(phase) union() {
        circle(r=rr,$fn=96);
        for(n=[0:teeth-1]) rotate(n*360/teeth) polygon(concat(
           [polar(rr,-flank_angle(rb)+0.2)],
           [for(k=[0:12])let(r=rb+(ra-rb)*k/12)polar(r,-flank_angle(r)+0.2)],
           [for(k=[12:-1:0])let(r=rb+(ra-rb)*k/12)polar(r,flank_angle(r)-0.2)],
           [polar(rr,flank_angle(rb)-0.2)]));
    }
}

// ---------- finger: local frame, pivot at origin, inner (gripping) side is -X ----------
tip_point=[-13.3,113];
function wave(z)=-9.2-1.5*sin(360*(z-30)/18);        // scalloped inner grip edge
module finger_profile() {
    // Traced by eye from cad/reference/generalist_gripper_gen6_target.png and ziptie_1.jpg:
    // a crescent that bulges outward to ~16 mm, a scalloped (wavy) inner grip edge, a
    // small step before the blade, then a point. Proportions estimated, not measured.
    union() {
        circle(r=9);
        polygon(concat(
            curve([9,2],[13,14],[16.5,32],[16.5,50]),          // outer crescent
            curve([16.5,50],[16.5,66],[10,84],[0,100]),
            curve([0,100],[-5,105],[-10,110],tip_point),       // into the point
            curve(tip_point,[-13.9,111],[-14,106],[-13.3,100]),
            curve([-13.3,100],[-12.8,97],[-12.2,95],[-11.2,94]),   // step before the blade
            curve([-11.2,94],[-10.4,93.4],[-10,92.6],[-10.1,91.5]),
            [for(z=[90:-1:30]) [wave(z)-(z>84?(z-84)*0.18:0),z]],  // three scallops
            curve([-9.2,30],[-8.4,22],[-7.4,12],[-7,2])));        // inner shank
    }
}
module hex_cell() {rotate(30) circle(d=cell/cos(30),$fn=6);}
module hex_centres() {
    p=cell+cell_wall;
    for(j=[-2:50],i=[-10:10]) translate([i*p+(j%2)*p/2,j*p*sqrt(3)/2]) square(0.02,center=true);
}
module perforation2d() {
    // Rows of small hex pockets inside a solid rim, clear of the pivot, dots, pad,
    // strap slots, tip hole and the tip tongue. Whole cells only: centres are kept
    // where a full cell fits, then each centre is grown back into a hex.
    minkowski() {
        intersection() {
            hex_centres();
            offset(delta=-cell/sqrt(3)) difference() {
                offset(r=-rim) finger_profile();
                circle(r=12);
                translate([-30,tip_start-8]) square([60,40]);
                for(m=magnets) translate(m) circle(r=4.2);
                for(q=pads) translate(q[0]) square(q[1]-q[0]);
                for(s=straps) translate(s) square([6,9.5],center=true);
                translate(tip_hole) circle(r=2.6);
            }
        }
        hex_cell();
    }
}
module tongue2d() {intersection(){offset(r=-2) finger_profile();translate([-30,tip_start-3]) square([60,8]);}}
module finger_plate() {
    difference() {
        union() {
            xz(plate) intersection(){finger_profile();translate([-30,-20]) square([60,tip_start+20]);}
            xz(plate/2) tongue2d();
        }
        for(s=[-1,1]) translate([0,s*(plate/2-pocket/2+0.5),0]) xz(pocket+1) perforation2d();
        for(m=magnets,s=[-1,1]) translate([m[0],s*(plate/2-1),m[1]]) rotate([90,0,0]) cylinder(d=4.2,h=2.2,center=true,$fn=24);
        for(s=straps) translate([s[0],0,s[1]]) xz(plate+2) hull() for(dz=[-2,2]) translate([0,dz]) circle(d=2.8,$fn=16);
        translate([tip_hole[0],0,tip_hole[1]]) xz(plate+2) circle(d=2.2,$fn=16);
    }
}
module tip_insert() {
    // Black TPU point, like the dark tips in the photos. Slides over the jaw's tongue.
    difference() {
        intersection() {
            xz(plate) intersection(){finger_profile();translate([-30,tip_start+0.15]) square([60,30]);} // 0.15 seating gap
            hull() {
                translate([-20,-plate/2,tip_start+0.15]) cube([30,plate,0.5]);
                translate([tip_point[0]+0.6,0,tip_point[1]-0.6]) sphere(r=0.8,$fn=16);
            }
        }
        xz(plate/2+0.3) offset(r=0.15) tongue2d();
    }
}
module jaw() {
    // ONE jaw source; the left jaw is its mirror image. The column climbs out of the hand
    // plane to the housing, so nothing but the column sits in the thumb-index web.
    difference() {
        union() {
            finger_plate();
            ycyl(shoulder_d,plate/2-0.01,lower_plate[0]-0.5);
            ycyl(column_d,plate/2,gear_y[0]-0.3);
            translate([0,gear_y[0]-0.31,0]) rotate([-90,0,0]) cylinder(d=hex_af/cos(30),h=gear_y[1]-gear_y[0]+0.31,$fn=6);
        }
        ycyl(pin_d+0.2,-plate,upper_plate[1]+1,24);
    }
}
module gear(phase=0,drive=false) {
    difference() {
        union() {
            translate([0,gear_y[0],0]) rotate([-90,0,0]) linear_extrude(gear_y[1]-gear_y[0]) gear2d(phase);
            if(drive) ycyl(column_d,gear_y[1]-0.01,upper_plate[1]+0.5); // up through the roof to the servo horn
        }
        translate([0,gear_y[0]-1,0]) rotate([-90,0,0]) cylinder(d=(hex_af+hex_clear)/cos(30),h=gear_y[1]-gear_y[0]+2,$fn=6);
        ycyl(pin_d+0.2,gear_y[0]-1,upper_plate[1]+2,24);
        if(drive) translate([0,upper_plate[1]-4,0]) rotate([-90,0,0]) cylinder(d=6.3/cos(30),h=6,$fn=6); // horn adapter socket, unselected
    }
}
module housing_footprint() {
    hull() {
        for(s=[-1,1]) translate([s*pivot,0]) circle(r=19.5,$fn=96);
        translate([0,-30]) square([46,8],center=true);
    }
}
screws=[[-20,-24],[20,-24],[0,-27]];   // M2 self-tappers, lid into base bosses
module housing_base() {
    // Floor + wall over the back of the hand; gears drop in from above before the lid goes on.
    difference() {
        union() {
            translate([0,lower_plate[0],0]) xz(lower_plate[1]-lower_plate[0],false) housing_footprint();
            translate([0,lower_plate[1]-0.01,0]) xz(upper_plate[0]-lower_plate[1]+0.02,false) union() {
                difference(){housing_footprint();offset(r=-2.5) housing_footprint();}
                for(p=screws) translate(p) circle(d=6.5);
            }
        }
        for(s=[-1,1]) translate([s*pivot,0,0]) ycyl(column_d+bore_clear,lower_plate[0]-1,lower_plate[1]+0.5);
        for(p=screws) translate([p[0],0,p[1]]) ycyl(1.8,lower_plate[0]+2,upper_plate[0]+1,16);
        straps();
    }
}
module housing_lid() {
    difference() {
        translate([0,upper_plate[0],0]) xz(upper_plate[1]-upper_plate[0],false) housing_footprint();
        translate([-pivot,0,0]) ycyl(pin_d,upper_plate[0]-1,upper_plate[1]+1,24);
        translate([pivot,0,0]) ycyl(column_d+bore_clear,upper_plate[0]-1,upper_plate[1]+1);
        for(p=screws) translate([p[0],0,p[1]]) ycyl(2.4,upper_plate[0]-1,upper_plate[1]+1,16);
        straps();
    }
}
module straps() {
    // Hand-strap slots in the rear tongue: a strap round the palm holds the housing on.
    for(s=[-1,1]) translate([s*12-7,lower_plate[0]-1,-31.6]) cube([14,upper_plate[1]-lower_plate[0]+2,3.2]);
}
module housing() {housing_base();housing_lid();}
module motor() {
    // ONE servo envelope lying on the roof, shaft down into the right gear. Unselected.
    translate([pivot,upper_plate[1]+1+15,-9]) round_box([36,30,38],2);
    translate([pivot,0,0]) ycyl(6,upper_plate[1]-3,upper_plate[1]+1.5);
}
module placed(s=1,a=angle) {
    translate([s*pivot,0,0]) rotate([0,s*a,0]) if(s<0) mirror([1,0,0]) children(); else children();
}
module piece(q,a=angle) {
    if(q=="housing_base") housing_base();
    if(q=="housing_lid") housing_lid();
    if(q=="left") placed(-1,a) jaw();
    if(q=="right") placed(1,a) jaw();
    if(q=="left_gear") placed(-1,a) gear(-180/teeth);
    if(q=="right_gear") placed(1,a) gear(0,true);
    if(q=="left_tip") placed(-1,a) tip_insert();
    if(q=="right_tip") placed(1,a) tip_insert();
    if(q=="motor") motor();
}
module moving(a=angle) {for(q=["left","right","left_gear","right_gear","left_tip","right_tip"]) piece(q,a);}
module gear_pair(a=angle,phase_error=0) {
    intersection() {
        placed(-1,a+phase_error) xz(10) gear2d(-180/teeth);
        placed(1,a) xz(10) gear2d(0);
    }
}
module clash(a=angle) {
    intersection(){housing();moving(a);}
    intersection(){motor();moving(a);}
    intersection(){union(){piece("left",a);piece("left_gear",a);piece("left_tip",a);}
                   union(){piece("right",a);piece("right_gear",a);piece("right_tip",a);}}
    intersection(){piece("left",a);piece("left_gear",a);}
    intersection(){piece("right",a);piece("right_gear",a);}
    intersection(){piece("left",a);piece("left_tip",a);}
    intersection(){piece("right",a);piece("right_tip",a);}
}
module web_keepout() {
    // The thumb-index niche: the hand plane band behind the pivots. Must stay empty.
    translate([-60,-12,-80]) cube([120,24,80-9.5]);
}
module everything(a=angle) {moving(a);housing();motor();}
assert(angle>=0&&angle<=max_angle,"Angle outside intended motion");
if(part=="assembly") {
    color("#2b313a") housing_base();
    color("#3a424d") housing_lid();
    color("#efb83b") {piece("left");piece("right");}
    color("#8f969e") {piece("left_gear");piece("right_gear");}
    color("#15181c") {piece("left_tip");piece("right_tip");}
    if(show_motor) color("#252e38") motor();
}
if(part=="right") jaw();
if(part=="left") mirror([1,0,0]) jaw();
if(part=="right_gear") gear(0,true);
if(part=="left_gear") gear(-180/teeth);
if(part=="right_tip") tip_insert();
if(part=="left_tip") mirror([1,0,0]) tip_insert();
if(part=="housing_base") housing_base();
if(part=="housing_lid") housing_lid();
if(part=="motor") motor();
if(part=="collision") clash();
for(q=["housing_base","housing_lid","left","right","left_gear","right_gear","left_tip","right_tip","motor"]) if(part==str("viewer_",q)) piece(q);
