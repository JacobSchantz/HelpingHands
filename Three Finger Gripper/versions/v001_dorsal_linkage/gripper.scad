/*
 Three Finger Gripper — v001, original dorsal four-bar geometry study.
 Units mm. The lane arrangement is a neutral test fixture, NOT fitted anatomy.
 q = three separate output angles. No common moving lever or shaft.
 Open in OpenSCAD; see README.txt before interpreting these dimensions.
*/
$fn = 48;
part = "assembly"; // assembly | frame | cup | input | link | pins | clearance | collision
show_fingers = true;
show_labels = true;
q = [-6, -26, -42];
lane_pitch = 45;
inner_width = 24;       // PLACEHOLDER: measure fingers before adjusting
inner_height = 22;      // PLACEHOLDER
sleeve_depth = 36;      // PLACEHOLDER
wall = 2;
pin_diameter = 3;
bore_clearance = 0.35;  // diametral, untested
axial_clearance = 0.5;  // each side of link
ground_length = 52;     // rear rocker stays behind the proximal insertion envelope
rocker_length = 18;
hinge_z = 24;
link_thickness = 4;
rocker_x = 4.5;
rocker_thickness = 3;
rail_x = 18;
rail_thickness = 3;
scene_z = 48;
check_pair = "all"; // all | frame_cup | frame_input | frame_link | input_link | cup_link | finger

function at_angle(p, a) = [p[0], p[1]*cos(a)-p[2]*sin(a), p[1]*sin(a)+p[2]*cos(a)];
function tip(a) = at_angle([0,0,rocker_length],a)+[0,0,hinge_z];
function station(i) = [(i-1)*lane_pitch,0,scene_z];

module x_cylinder(d,h) { rotate([0,90,0]) cylinder(d=d,h=h,center=true); }
module yz_bar(p1,p2,width,thickness,x=0) {
    hull() for(p=[p1,p2]) translate([x,p[0],p[1]]) x_cylinder(width,thickness);
}
module hole(y,z,length=50,d=pin_diameter+bore_clearance) {
    translate([0,y,z]) x_cylinder(d,length);
}
module ellipse_tube(rx,rz,depth) {
    rotate([-90,0,0]) scale([rx,rz,1]) cylinder(r=1,h=depth);
}

module frame() {
    // Independent fixed rails. Every transverse pin is above the finger space.
    difference() {
        union() {
            for(x=[-rail_x,rail_x])
                yz_bar([-ground_length,hinge_z],[0,hinge_z],9,rail_thickness,x);
            translate([0,-ground_length-7,hinge_z]) cube([39,6,8],center=true);
        }
        hole(-ground_length,hinge_z);
        hole(0,hinge_z);
        // Placeholder mounting holes in the rear bridge, vertical for a common fixture.
        for(x=[-12,12]) translate([x,-ground_length-7,hinge_z]) cylinder(d=3.4,h=20,center=true);
    }
}

module cup_body() {
    difference() {
        union() {
            translate([0,2,0]) ellipse_tube(inner_width/2+wall,inner_height/2+wall,sleeve_depth);
            // Two dorsal webs: their lower tips merge into the sleeve roof.
            for(x=[-rocker_x,rocker_x]) {
                yz_bar([5,inner_height/2],[0,hinge_z],8,rocker_thickness,x);
                yz_bar([0,hinge_z],[0,hinge_z+rocker_length],8,rocker_thickness,x);
            }
        }
        // Open rear and a thin closed nose. No axle traverses this cavity.
        translate([0,1,0]) ellipse_tube(inner_width/2,inner_height/2,sleeve_depth-wall+1);
        hole(0,hinge_z,50);
        hole(0,hinge_z+rocker_length,22);
        // Two transverse strap slots; a flexible strap remains a separate unmodeled part.
        for(x=[-1,1]) translate([x*(inner_width/2+wall-0.3),12,0]) cube([wall+2,9,3],center=true);
    }
}
module cup(a=0) {
    translate([0,0,hinge_z]) rotate([a,0,0]) translate([0,0,-hinge_z]) cup_body();
}
module input(a=0) {
    translate([0,-ground_length,hinge_z]) rotate([a,0,0]) {
        difference() {
            union() {
                for(x=[-rocker_x,rocker_x]) yz_bar([0,0],[0,rocker_length],8,rocker_thickness,x);
                // Dorsal cross-web joins the two rocker cheeks below the link eye.
                translate([0,0,7]) cube([12,7,5],center=true);
            }
            hole(0,0,50);
            hole(0,rocker_length,22);
        }
    }
}
module link(a=0) {
    t=tip(a);
    translate([0,t[1],t[2]]) difference() {
        yz_bar([-ground_length,0],[0,0],7,link_thickness);
        hole(-ground_length,0,12);
        hole(0,0,12);
    }
}
module pins(a=0) {
    // Visual pin shanks only: no modeled fastener head/nut or press fit claim.
    for(y=[-ground_length,0]) translate([0,y,hinge_z]) x_cylinder(pin_diameter,42);
    t=tip(a);
    for(y=[t[1]-ground_length,t[1]]) translate([0,y,t[2]]) x_cylinder(pin_diameter,16);
}
module finger_space(a=0) {
    translate([0,0,hinge_z]) rotate([a,0,0]) translate([0,0,-hinge_z])
        translate([0,-28,0]) ellipse_tube(inner_width/2-0.5,inner_height/2-0.5,sleeve_depth+28-wall);
}
module mechanism(a=0) {
    color([0.30,0.35,0.40]) frame();
    color([0.93,0.65,0.18]) cup(a);
    color([0.25,0.65,0.78]) input(a);
    color([0.91,0.39,0.21]) link(a);
    color([0.72,0.76,0.79]) pins(a);
    if(show_fingers) color([0.71,0.86,0.93,0.25]) finger_space(a);
}
module fixed_bridge() {
    // Fixture joining ONLY the grounds. Three moving mechanisms stay separate.
    translate([0,-ground_length-7,scene_z+hinge_z-7]) difference() {
        cube([2*lane_pitch+39,6,6],center=true);
        for(i=[0:2],x=[-12,12]) translate([(i-1)*lane_pitch+x,0,0]) cylinder(d=3.4,h=10,center=true);
    }
}
module collision(a=0) {
    // The first union is intentionally separate pairs, not full union intersection.
    union() {
        if(check_pair=="all" || check_pair=="frame_cup") intersection() { frame(); cup(a); }
        if(check_pair=="all" || check_pair=="frame_input") intersection() { frame(); input(a); }
        if(check_pair=="all" || check_pair=="frame_link") intersection() { frame(); link(a); }
        if(check_pair=="all" || check_pair=="input_link") intersection() { input(a); link(a); }
        if(check_pair=="all" || check_pair=="cup_link") intersection() { cup(a); link(a); }
        if(check_pair=="all" || check_pair=="finger") intersection() { finger_space(a); union() {frame();cup(a);input(a);link(a);pins(a);} }
    }
}

assert(inner_width/2+wall < rail_x-rail_thickness/2, "Widen frame rails for this sleeve width");
assert(hinge_z > inner_height/2+wall+5, "Dorsal hinge needs room above sleeve roof");
assert(rocker_x-rocker_thickness/2 >= link_thickness/2+axial_clearance, "Link cheek clearance is too small");
assert(lane_pitch > 2*(rail_x+rail_thickness/2)+2, "Separate neighbouring modules");
if(part=="assembly") {
    fixed_bridge();
    for(i=[0:2]) translate(station(i)) {
        mechanism(q[i]);
        if(show_labels) color([0.3,0.35,0.4]) translate([0,46,-43]) linear_extrude(0.6)
            text(str(i+1," / ",q[i]," deg"),size=5,halign="center");
    }
}
if(part=="frame") frame();
if(part=="cup") cup();
if(part=="input") input();
if(part=="link") link();
if(part=="pins") pins();
if(part=="clearance") for(i=[0:2]) translate(station(i)) finger_space(q[i]);
if(part=="collision") for(i=[0:2]) translate(station(i)) collision(q[i]);
