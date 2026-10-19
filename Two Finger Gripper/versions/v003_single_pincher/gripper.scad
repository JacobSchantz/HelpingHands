/* GENERALIST GRIPPER — GENERATION 3 / original reference-informed concept.
   ONE opposed jaw pair, ONE unselected servo. Units mm. No hard finger rings.
   Official Generalist images inform silhouette/handling only, NOT hidden mechanics.
   Local normal-force sensing provision is a placeholder, not a calibrated result. */
$fn=48;
part="assembly"; // assembly | jaws | hub | thumb | index | sensor_pad | adapter | collision | gear_collision | none
angle=18;
show_motor=true;
show_straps=true;
show_sensor=true;
min_angle=0;
max_angle=22;
pivot=12;
module_m=1.2;
teeth=20;
pitch_r=module_m*teeth/2;
pressure=20;
hex_flats=10;
hex_clearance=0.3;
thumb_radius=16; // open saddle placeholder; NOT measured fit
index_radius=13;
pad_z=50;

function inv(t)=tan(t)-t*PI/180;
function flank_angle(r)=90/teeth+(inv(pressure)-inv(acos(pitch_r*cos(pressure)/r)))*180/PI;
function polar(r,a)=[r*cos(a),r*sin(a)];
function patch_gap(a)=2*(pivot-10*cos(a)+pad_z*sin(a));
stop_r=1.5;
stop_sweep_r=sqrt(15*15+3*3);
// A small angular allowance avoids making faceted stop surfaces overlap at limits.
stop_delta=asin(2*stop_r/stop_sweep_r)+0.05;
opening_stop_delta=asin((3+2*stop_r)/stop_sweep_r)-atan(3/15)+0.05;
function stop_point(a)=[15*cos(a)-3*sin(a),-15*sin(a)-3*cos(a)];
module y_cyl(d,h) { rotate([90,0,0]) cylinder(d=d,h=h,center=true); }
module x_cyl(d,h) { rotate([0,90,0]) cylinder(d=d,h=h,center=true); }
module xz(h) { rotate([90,0,0]) linear_extrude(h,center=true) children(); }
module rounded(size,r=1) {
    hull() for(x=[-1,1],y=[-1,1],z=[-1,1])
        translate([x*(size[0]/2-r),y*(size[1]/2-r),z*(size[2]/2-r)]) sphere(r=r,$fn=16);
}
module gear2d(phase=0) {
    rb=pitch_r*cos(pressure); ra=pitch_r+module_m; rr=pitch_r-1.25*module_m;
    rotate(phase) union() {
        circle(r=rr);
        for(n=[0:teeth-1]) rotate(n*360/teeth) polygon(concat(
            [polar(rr,-flank_angle(rb)+0.2)],
            [for(k=[0:10]) let(r=rb+(ra-rb)*k/10) polar(r,-flank_angle(r)+0.2)],
            [for(k=[10:-1:0]) let(r=rb+(ra-rb)*k/10) polar(r,flank_angle(r)-0.2)],
            [polar(rr,flank_angle(rb)-0.2)]));
    }
}
module finger2d() {
    // Curved taper and lightening apertures; not a copied/proven fin-ray finger.
    difference() {
        polygon([[-10,27],[-5,22],[7,26],[10,38],[8,52],[4,68],[-3,84],[-9,88],[-11,85],[-7,70],[-3,62],[-3,40],[-7,34]]);
        for(row=[[2,30],[5,38],[5,46],[3,56],[0,66],[-4,76]])
            translate(row) rotate(30) circle(d=3.8,$fn=6);
    }
}
module jaw(s=1,with_teeth=true) {
    radius=s<0?thumb_radius:index_radius;
    difference() {
        union() {
            if(with_teeth) xz(5) gear2d(s<0?180/teeth:0);
            xz(18) union() {
                circle(r=8);
                hull() { translate([0,5]) circle(r=5); translate([1,26]) circle(r=6); }
                finger2d();
            }
            // Front journal of the driven jaw; rear coupling stays on servo side.
            if(s==1) translate([0,11,0]) y_cyl(6,4);
            if(s==1) {
                translate([-8.5,0,pad_z]) rounded([3,18,22],0.6);
                translate([-4.9,0,pad_z]) cube([4.4,10,14],center=true);
            }
        }
        // Finger presses on a shallow OPEN outer saddle, entering along Y.
        translate([radius+5,0,50]) y_cyl(2*radius,28);
        for(side=[-1,1]) translate([radius+5,side*8,50]) rotate([side*90,0,0])
            cylinder(d1=2*(radius+1.2),d2=2*radius,h=2.2,center=true);
        // Four 3 mm zip-tie anchor slots: tie SOFT tabs, never a bare finger.
        for(y=[-5,5],z=[32,68]) translate([1,y,z]) rotate([0,90,0])
            hull() for(t=[-1,1]) translate([0,t,0]) cylinder(d=2.8,h=32,center=true,$fn=20);
        if(s<0) y_cyl(3.4,32);
        else {
            // Rear hex socket is OUR removable adapter interface, not a servo spline.
            translate([0,-4,0]) rotate([90,0,0]) cylinder(d=(hex_flats+hex_clearance)/cos(30),h=14,center=true,$fn=6);
            translate([0,11,0]) y_cyl(2.5,8); // front retainer pilot, unselected fastener
        }
        // Left/thumb jaw receives the real sensor, with a floor at local x=-3.
        if(s<0) translate([-4,0,pad_z]) x_cyl(8.4,2);
    }
}
module sensor_pad() {
    // Local normal contact patch, not whole-finger/tangential force measurement.
    difference() {
        union() {
            translate([-8.5,0,pad_z]) rounded([3,18,22],0.6);
            for(y=[-11,11]) translate([-7,y,pad_z]) rounded([3,8,8],0.5);
        }
        for(y=[-11,11]) translate([-7,y,pad_z]) x_cyl(3.4,8);
    }
}
module sensor_package() {
    color([0.25,0.75,0.35]) translate([-5,0,pad_z]) x_cyl(8,4);
    color([0.65,0.69,0.73]) for(y=[-11,11]) {
        translate([-4.5,y,pad_z]) x_cyl(3,9);
        translate([-9,y,pad_z]) x_cyl(6,0.8); // recessed behind contact face x=-10
    }
}
module guide_lands() {
    for(y=[-11,11]) translate([0,y,pad_z]) difference() {
        rounded([6,7,8],0.5);
        x_cyl(2.5,10);
    }
}
module placed(s,a=angle) {
    translate([s*pivot,0,0]) rotate([0,s*a,0]) if(s<0) mirror([1,0,0]) children(); else children();
}
module hub() {
    for(y=[-12,12]) difference() {
        translate([0,y,0]) xz(4) hull() {
            for(x=[-pivot,pivot]) translate([x,0]) circle(r=9);
            translate([0,-18]) square([40,8],center=true);
            if(y>0) for(s=[-1,1],a=[-stop_delta,max_angle+opening_stop_delta])
                let(p=stop_point(a)) translate([s*(pivot+p[0]),p[1]]) circle(r=3);
        }
        translate([-pivot,y,0]) y_cyl(3.4,8);
        translate([pivot,y,0]) y_cyl(y<0?16:6.4,8);
    }
    translate([0,0,-18]) rounded([40,28,8],1);
    // Fixed physical angular stop shoulders. Moving tabs touch at 0/22 degrees.
    for(s=[-1,1],a=[-stop_delta,max_angle+opening_stop_delta]) let(p=stop_point(a))
        translate([s*(pivot+p[0]),9.5,p[1]]) y_cyl(2*stop_r,5);
}
module stop_tab(s) {
    translate([0,7,0]) xz(3) hull() for(x=[6,15]) translate([x,-3]) circle(r=stop_r);
}
module adapter_blank() {
    // Undrilled flange: actual horn/spline dimensions MUST replace this blank.
    y_cyl(20,3);
    translate([0,8,0]) rotate([90,0,0]) cylinder(d=hex_flats/cos(30),h=13,center=true,$fn=6);
}
module soft_strap(s) {
    r=s<0?thumb_radius:index_radius;
    // Soft envelope has an outward peel-open break; never print as a hard cuff.
    color([0.65,0.35,0.75,0.5]) {
        translate([r+5,0,50]) rotate([90,0,0]) linear_extrude(8,center=true) difference() {
            intersection() {
                difference() { circle(r=r+1.5); circle(r=r+0.3); }
                translate([0,-25]) square([25,50]);
            }
            translate([0,-3]) square([26,6]);
        }
        for(t=[-1,1]) hull() {
            translate([r+5,0,50+t*(r+1)]) cube([1,8,1],center=true);
            translate([7,0,50+t*18]) cube([1,8,1],center=true);
        }
    }
}
module moving(a=angle,teeth_on=true) {
    for(s=[-1,1]) placed(s,a) {
        color(s<0?[0.96,0.7,0.16]:[0.98,0.78,0.24]) union() {
            jaw(s,teeth_on);
            if(s<0) guide_lands();
            stop_tab(s);
        }
        if(s<0) {
            color([0.2,0.25,0.28]) sensor_pad();
            if(show_sensor) sensor_package();
        }
        if(show_straps) soft_strap(s);
    }
}
module motor_envelope() {
    // ONE unselected servo volume. No claim about HLS3606M/STS3215 fit/backdrive.
    actuator_envelope();
    color([0.6,0.65,0.7]) translate([pivot,-16,0]) rotate([0,angle,0]) adapter_blank();
    color([0.65,0.69,0.73]) translate([-pivot,0,0]) y_cyl(3,32);
}
module actuator_envelope() {
    color([0.22,0.25,0.29]) translate([pivot,-39,-3]) rounded([36,40,30],2);
    color([0.6,0.65,0.7]) translate([pivot,-20,0]) y_cyl(6,8);
}
module sensor_screw(y) {
    translate([-4.5,y,pad_z]) x_cyl(3,9);
    translate([-9,y,pad_z]) x_cyl(6,0.8);
}
module viewer_piece(q) {
    if(q=="hub") hub();
    if(q=="thumb") placed(-1) union(){jaw(-1);guide_lands();stop_tab(-1);}
    if(q=="index") placed(1) union(){jaw(1);stop_tab(1);}
    if(q=="pad") placed(-1) sensor_pad();
    if(q=="sensor") placed(-1) translate([-5,0,pad_z]) x_cyl(8,4);
    if(q=="guide_front") placed(-1) sensor_screw(-11);
    if(q=="guide_rear") placed(-1) sensor_screw(11);
    if(q=="adapter") translate([pivot,-16,0]) rotate([0,angle,0]) adapter_blank();
    if(q=="motor") actuator_envelope();
    if(q=="pivot_pin") translate([-pivot,0,0]) y_cyl(3,32);
    if(q=="thumb_strap") placed(-1) soft_strap(-1);
    if(q=="index_strap") placed(1) soft_strap(1);
}
module clash(a=angle) {
    intersection() { hub(); moving(a,false); }
    intersection() { placed(-1,a) union(){jaw(-1,false);guide_lands();} placed(1,a) jaw(1,false); }
}
assert(angle>=min_angle && angle<=max_angle,"Angle outside intended travel");
echo(contact_patch_gap_mm=patch_gap(angle));
if(part=="assembly") { color([0.25,0.29,0.34]) hub(); moving(); if(show_motor) motor_envelope(); }
if(part=="jaws") moving();
if(part=="hub") hub();
if(part=="thumb") union(){jaw(-1);guide_lands();stop_tab(-1);}
if(part=="index") union(){jaw(1);stop_tab(1);}
if(part=="sensor_pad") sensor_pad();
if(part=="adapter") adapter_blank();
if(part=="collision") clash();
if(part=="gear_collision") intersection() { placed(-1) xz(5) gear2d(180/teeth); placed(1) xz(5) gear2d(); }
// Viewer pieces are individually exported in ASSEMBLED WORLD coordinates.
for(q=["hub","thumb","index","pad","sensor","guide_front","guide_rear","adapter","motor","pivot_pin","thumb_strap","index_strap"])
    if(part==str("viewer_",q)) viewer_piece(q);
