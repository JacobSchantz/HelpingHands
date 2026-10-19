/* Original dual parallel-jaw geometry study. Units mm. NOT a print package.
   Two independent servos, two rack/pinion pairs, four translating jaws.
   Cuff/operator mapping deferred pending clarification. */
$fn=48;
part="assembly"; // assembly | module | drive | carriage | rack | gear | frame | collision
gaps=[24,58];             // independently commanded clear pad gaps, mm
synchronized=false;      // optional command relationship; no shared moving transmission
separation=140;           // distance between grasp stations along a long object
show_hardware=true;
show_sensors=true;
show_labels=true;
module_gap=24;
module_m=1.5;
teeth=20;
pitch_r=module_m*teeth/2;
pressure=20;
tooth_backlash=0.10;
rack_length=80;
guide_y=27;
guide_z=24;
guide_d=6;
sliding_clearance=0.4;    // diametral placeholder; bearings not yet selected
gear_z=9;
pad_offset=10;
min_gap=8;
max_gap=70;

function inv(t)=tan(t)-t*PI/180;
function flank_angle(r)=90/teeth+(inv(pressure)-inv(acos(pitch_r*cos(pressure)/r)))*180/PI;
function polar(r,a)=[r*cos(a),r*sin(a)];

module spur_gear() {
    rb=pitch_r*cos(pressure);
    ra=pitch_r+module_m;
    rr=pitch_r-1.25*module_m;
    difference() {
        union() {
        translate([0,0,-4.5]) cylinder(d=14,h=4,center=true);
        linear_extrude(5,center=true) union() {
            circle(r=rr);
            for(n=[0:teeth-1]) rotate(n*360/teeth)
                polygon(concat(
                    [polar(rr,-flank_angle(rb)+0.2)],
                    [for(k=[0:10]) let(r=rb+(ra-rb)*k/10) polar(r,-flank_angle(r)+0.2)],
                    [for(k=[10:-1:0]) let(r=rb+(ra-rb)*k/10) polar(r,flank_angle(r)-0.2)],
                    [polar(rr,flank_angle(rb)-0.2)]));
        }}
        cylinder(d=6.4,h=20,center=true);
        for(a=[0:90:270]) rotate(a) translate([5,0,0]) cylinder(d=2.7,h=20,center=true);
    }
}

module rack() {
    pitch=PI*module_m;
    root_y=pitch_r+1.25*module_m;
    tip_y=pitch_r-module_m;
    half_root=pitch/4+1.25*module_m*tan(pressure)-tooth_backlash;
    half_tip=pitch/4-module_m*tan(pressure)-tooth_backlash;
    translate([0,0,gear_z]) linear_extrude(5,center=true) union() {
        translate([-5,root_y]) square([rack_length,5]);
        for(i=[0:floor((rack_length-5)/pitch)]) translate([i*pitch,0])
            polygon([[-half_root,root_y+0.1],[-half_tip,tip_y],[half_tip,tip_y],[half_root,root_y+0.1]]);
    }
}

module x_cylinder(d,h) { rotate([0,90,0]) cylinder(d=d,h=h,center=true); }
module carriage() {
    difference() {
        union() {
            translate([0,0,guide_z]) cube([16,2*guide_y+15,16],center=true);
            // Jaw backbone, rigidly attached to the sliding carriage.
            translate([0,0,51]) cube([8,20,48],center=true);
            // Rack attachment bridge: its lower end overlaps the rack body.
            translate([0,20,16]) cube([10,6,15],center=true);
        }
        for(y=[-guide_y,guide_y]) translate([0,y,guide_z]) x_cylinder(guide_d+sliding_clearance,24);
    }
}

module jaw_pad() {
    // Pad is supported ONLY through the sensor envelope, not through the backbone.
    translate([7,0,55]) cube([2,24,30],center=true);
}
module loadcell_envelope() {
    // Replace this envelope with a selected load cell and its actual fastener lands.
    translate([2,0,55]) cube([4,12,14],center=true);
}

module ground() {
    difference() {
        translate([0,0,-5]) cube([172,76,4],center=true);
        cylinder(d=9,h=30,center=true);
        for(x=[-82,82],y=[-24,24]) translate([x,y,-5]) cylinder(d=4.5,h=20,center=true);
        for(x=[-15,15],y=[-15,15]) translate([x,y,-5]) cylinder(d=3.5,h=20,center=true);
    }
    for(x=[-74,74],y=[-guide_y,guide_y]) difference() {
        translate([x,y,9]) cube([12,16,32],center=true);
        translate([x,y,guide_z]) x_cylinder(guide_d+0.2,20);
    }
    // Center collars are physical closing stops, at gap=8 mm.
    for(y=[-guide_y,guide_y]) difference() {
        translate([0,y,guide_z]) x_cylinder(14,12);
        translate([0,y,guide_z]) x_cylinder(guide_d+0.2,16);
    }
    // Outer collars are physical opening stops, at gap=70 mm.
    for(x=[-57,57],y=[-guide_y,guide_y]) difference() {
        translate([x,y,guide_z]) x_cylinder(14,8);
        translate([x,y,guide_z]) x_cylinder(guide_d+0.2,12);
    }
    // Stationary encoder-board support reaches over the pinion, below the slides.
    translate([0,36,5]) cube([4,4,18],center=true);
    translate([0,22,14]) cube([4,28,2],center=true);
}

module hardware(gap) {
    color([0.72,0.76,0.80]) for(y=[-guide_y,guide_y]) translate([0,y,guide_z]) x_cylinder(guide_d,148);
    // Generic servo package: exact body, flange and shaft await hardware selection.
    color([0.25,0.28,0.32]) translate([0,0,-28]) cube([40,32,40],center=true);
    color([0.40,0.44,0.47]) translate([0,0,-9]) cube([40,40,4],center=true);
    color([0.70,0.73,0.76]) translate([0,0,0]) cylinder(d=6,h=24,center=true);
    // Placeholder output horn and four fasteners carry torque into the pinion.
    color([0.68,0.71,0.74]) translate([0,0,2]) cylinder(d=16,h=2,center=true);
    color([0.7,0.73,0.76]) rotate([0,0,(gap/2+pad_offset)/pitch_r*180/PI+90+180/teeth])
        for(a=[0:90:270]) rotate(a) translate([5,0,6]) cylinder(d=2.5,h=12,center=true);
    // Direct shaft encoder magnet + stationary board are sensing envelopes.
    color([0.65,0.35,0.65]) translate([0,0,12.3]) cylinder(d=6,h=0.6,center=true);
    color([0.2,0.55,0.34]) translate([0,0,14]) cube([18,18,1.6],center=true);
}

module moving(gap,paint=true) {
    pos=gap/2+pad_offset;
    // Upper rack belongs to left carriage. Lower rack is its 180-degree copy.
    for(s=[-1,1]) {
        color(s==-1?[0.94,0.65,0.17]:[0.27,0.65,0.79])
            translate([s*pos,0,0]) if(s==-1) carriage(); else rotate([0,0,180]) carriage();
        color([0.85,0.87,0.89])
            translate([s*pos,0,0]) if(s==-1) rack(); else rotate([0,0,180]) rack();
        // Sensor and pad point inward; the carriage has no rigid pad bypass.
        translate([s*pos,0,0]) if(s==-1) {
            if(show_sensors) color([0.38,0.76,0.43]) translate([4,0,0]) loadcell_envelope();
            color([0.25,0.29,0.31]) translate([2,0,0]) jaw_pad();
        } else mirror([1,0,0]) {
            if(show_sensors) color([0.38,0.76,0.43]) translate([4,0,0]) loadcell_envelope();
            color([0.25,0.29,0.31]) translate([2,0,0]) jaw_pad();
        }
    }
    color([0.88,0.4,0.22]) translate([0,0,gear_z]) rotate([0,0,pos/pitch_r*180/PI+90+180/teeth]) spur_gear();
}

module single_gripper(gap) {
    color([0.4,0.45,0.5]) ground();
    moving(gap);
    if(show_hardware) hardware(gap);
}
module support() {
    for(x=[-82,82]) color([0.42,0.46,0.50]) translate([x,0,-12]) difference() {
        cube([12,260,10],center=true);
        // Repositionable fixture stations; separation is not a locked anatomy choice.
        for(s=[-1,1],y=[26,36,46,56,66,74,84,94,104,114]) translate([0,s*y,0]) cylinder(d=4.5,h=20,center=true);
    }
}

module collisions(gap) {
    pos=gap/2+pad_offset;
    intersection() { ground(); moving(gap); }
    intersection() {
        translate([-pos,0,0]) carriage();
        translate([pos,0,0]) rotate([0,0,180]) carriage();
    }
}

assert(min(gaps)>=min_gap && max(gaps)<=max_gap,"Gap outside modeled hard-stop limits");
assert(separation>=100 && separation<=180,"Use a fixture separation from 100 to 180 mm");
assert((separation-100)%20==0,"Fixture supports 100/120/140/160/180 mm station spacing");
if(part=="assembly") {
    support();
    for(i=[0:1]) translate([0,(i-0.5)*separation,0]) {
        single_gripper(synchronized?gaps[0]:gaps[i]);
        if(show_labels) color([0.3,0.35,0.4]) translate([-68,36,-2]) linear_extrude(0.6)
            text(str("G",i+1,"  ",synchronized?gaps[0]:gaps[i]," mm"),size=5);
    }
}
if(part=="module") single_gripper(module_gap);
if(part=="drive") moving(module_gap);
if(part=="carriage") carriage();
if(part=="rack") rack();
if(part=="gear") spur_gear();
if(part=="frame") ground();
if(part=="collision") collisions(module_gap);
