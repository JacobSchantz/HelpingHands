/* GENERALIST GRIPPER v003 — original single-pincher geometry study, mm.
   One rack/pinion, two parallel jaws, ONE unselected servo interface.
   Finger saddles are open; ties anchor removable SOFT straps only.
   Motor/horn, compression sensor, bushings and fasteners are placeholders.
   Not a print-ready or validated human-use assembly. */
$fn=48;
part="assembly"; // assembly | frame | left_jaw | right_jaw | pad | pinion | adapter | collision | none
gap=30;
show_hardware=true;
show_sensor=true;
show_soft_straps=true;
min_gap=10;
max_gap=54;
pad_offset=13;
module_m=1.5;
teeth=20;
pitch_r=module_m*teeth/2;
pressure=20;
tooth_backlash=0.10;
rack_length=72;
gear_z=9;
guide_y=27;
guide_z=22;
guide_d=6;
sliding_clearance=0.4; // diametral, NOT a bearing fit specification
finger_radius=13;     // open 26 mm saddle, not measured finger fit
finger_z=52;
sensor_d=10;         // unknown button-compression sensor envelope
sensor_length=6;     // sensor axis X, behind ONE contact pad
sensor_seat_clearance=0.4;
pad_guide_clearance=0.4;
hex_flats=10;        // our own adapter-to-pinion interface; NOT a motor spline
hex_clearance=0.3;

function inv(t)=tan(t)-t*PI/180;
function flank_angle(r)=90/teeth+(inv(pressure)-inv(acos(pitch_r*cos(pressure)/r)))*180/PI;
function polar(r,a)=[r*cos(a),r*sin(a)];
module x_cyl(d,h) { rotate([0,90,0]) cylinder(d=d,h=h,center=true); }
module y_cyl(d,h) { rotate([90,0,0]) cylinder(d=d,h=h,center=true); }
module round_block(size,r=1) {
    hull() for(x=[-1,1],y=[-1,1],z=[-1,1])
        translate([x*(size[0]/2-r),y*(size[1]/2-r),z*(size[2]/2-r)]) sphere(r=r,$fn=16);
}

module pinion() {
    rb=pitch_r*cos(pressure); ra=pitch_r+module_m; rr=pitch_r-1.25*module_m;
    difference() {
        union() {
            translate([0,0,-4.5]) cylinder(d=14,h=4,center=true);
            linear_extrude(5,center=true) union() {
                circle(r=rr);
                for(n=[0:teeth-1]) rotate(n*360/teeth)
                    polygon(concat([polar(rr,-flank_angle(rb)+0.2)],
                        [for(k=[0:10]) let(r=rb+(ra-rb)*k/10) polar(r,-flank_angle(r)+0.2)],
                        [for(k=[10:-1:0]) let(r=rb+(ra-rb)*k/10) polar(r,flank_angle(r)-0.2)],
                        [polar(rr,flank_angle(rb)-0.2)]));
            }
        }
        cylinder(d=(hex_flats+hex_clearance)/cos(30),h=22,center=true,$fn=6);
    }
}

module adapter_blank() {
    // Flange intentionally UNDRILLED: selected servo horn/spline required.
    cylinder(d=22,h=3,center=true);
    translate([0,0,4]) cylinder(d=hex_flats/cos(30),h=6,center=true,$fn=6);
}

module rack() {
    pitch=PI*module_m; root_y=pitch_r+1.25*module_m; tip_y=pitch_r-module_m;
    half_root=pitch/4+1.25*module_m*tan(pressure)-tooth_backlash;
    half_tip=pitch/4-module_m*tan(pressure)-tooth_backlash;
    translate([0,0,gear_z]) linear_extrude(5,center=true) union() {
        translate([-5,root_y]) square([rack_length,5]);
        for(i=[0:floor((rack_length-5)/pitch)]) translate([i*pitch,0])
            polygon([[-half_root,root_y+0.1],[-half_tip,tip_y],[half_tip,tip_y],[half_root,root_y+0.1]]);
    }
}

module carriage_core() {
    difference() {
        union() {
            translate([0,0,guide_z]) round_block([16,69,16]);
            translate([0,0,48]) round_block([10,40,46],1.5);
            translate([0,20,16]) cube([10,6,15],center=true);
        }
        for(y=[-guide_y,guide_y]) translate([0,y,guide_z]) x_cyl(guide_d+sliding_clearance,24);
        // Shallow, fully open finger indent. No rigid ring or finger tunnel.
        translate([-15,0,finger_z]) y_cyl(2*finger_radius,46);
        // Four radiused zip-tie anchor slots, accepting nominal 3 mm ties.
        // Ties fasten soft fabric tabs; never tighten ties directly on skin.
        for(y=[-14,14],z=[finger_z-11,finger_z+11]) translate([0,y,z])
            rotate([0,90,0]) hull() for(t=[-1,1]) translate([0,t*1.4,0]) cylinder(d=2.8,h=18,center=true,$fn=20);
    }
}

module jaw(sensed=false) {
    union() {
        difference() {
            carriage_core();
            if(sensed) translate([5,0,finger_z]) x_cyl(sensor_d+sensor_seat_clearance,2);
        }
        rack();
        if(sensed) {
            // Cell pocket has a solid floor at x=4; the normal force enters here.
            translate([4.8,0,finger_z]) difference() {
                x_cyl(15,1.6);
                x_cyl(sensor_d+sensor_seat_clearance,2.2);
            }
            // Guide/retention screw lands outside the central object contact patch.
            for(y=[-16,16]) translate([3.5,y,finger_z]) difference() {
                cube([3,9,9],center=true);
                x_cyl(2.5,7);
            }
        } else {
            // Rigid opposing contact face: same x=13 plane as the sensed pad.
            translate([9,0,finger_z]) round_block([8,24,28],1);
        }
    }
}

module floating_pad() {
    difference() {
        union() {
            translate([11.5,0,finger_z]) round_block([3,24,28],0.6);
            for(y=[-14,14]) translate([10,y,finger_z]) round_block([3,10,9],0.5);
        }
        for(y=[-16,16]) translate([10,y,finger_z]) x_cyl(3+pad_guide_clearance,8);
    }
}

module frame() {
    difference() {
        translate([0,0,-5]) round_block([144,76,4],1);
        cylinder(d=26,h=20,center=true);
        // Generic adapter fastening slots, NOT a selected servo bolt pattern.
        for(y=[-19,19]) hull() for(x=[-12,12]) translate([x,y,-5]) cylinder(d=3.6,h=20,center=true);
    }
    for(x=[-66,66],y=[-guide_y,guide_y]) difference() {
        translate([x,y,9]) round_block([12,16,32],1);
        translate([x,y,guide_z]) x_cyl(guide_d+0.2,20);
    }
    // Closing stop: inner carriage edge at +/-10 when gap=10.
    for(y=[-guide_y,guide_y]) translate([0,y,guide_z]) difference() {
        x_cyl(14,20); x_cyl(guide_d+0.2,24);
    }
    // Opening stop: outer carriage edge at +/-48 when gap=54.
    for(x=[-52,52],y=[-guide_y,guide_y]) translate([x,y,guide_z]) difference() {
        x_cyl(14,8); x_cyl(guide_d+0.2,12);
    }
}

module sensor_hardware() {
    color([0.25,0.75,0.35]) translate([7,0,finger_z]) x_cyl(sensor_d,sensor_length);
    // Shoulder screw heads stay BEHIND the x=13 contact plane. Leave axial
    // float; tightening pad against these guides would bypass the sensor.
    color([0.65,0.68,0.7]) for(y=[-16,16]) {
        translate([7.5,y,finger_z]) x_cyl(3,9);
        translate([12,y,finger_z]) x_cyl(6,0.8);
    }
}

module soft_strap_envelope() {
    // Illustrative removable soft bands, deliberately open at their outer edge.
    // Not a printed part, closed cuff, material specification or proven fit.
    color([0.65,0.37,0.75,0.5]) for(y=[-13,13]) {
        translate([-15,y,finger_z]) rotate([90,0,0]) linear_extrude(4,center=true)
            difference() {
                intersection() {
                    difference() { circle(r=14.5); circle(r=13.3); }
                    translate([-20,-20]) square([20,40]);
                }
                translate([-20,-3]) square([20,6]); // peel-open break
            }
        for(s=[-1,1]) hull() {
            translate([-15,y,finger_z+s*14]) cube([0.8,4,0.8],center=true);
            translate([-5.4,y,finger_z+s*11]) cube([0.8,4,0.8],center=true);
        }
    }
}

module moving(g=gap) {
    pos=g/2+pad_offset;
    color([0.94,0.63,0.17]) translate([-pos,0,0]) jaw(true);
    color([0.25,0.65,0.78]) translate([pos,0,0]) rotate(180) jaw(false);
    color([0.24,0.31,0.33]) translate([-pos,0,0]) floating_pad();
    if(show_sensor) translate([-pos,0,0]) sensor_hardware();
    if(show_soft_straps) {
        translate([-pos,0,0]) soft_strap_envelope();
        translate([pos,0,0]) rotate(180) soft_strap_envelope();
    }
    color([0.85,0.38,0.2]) translate([0,0,gear_z]) rotate(pos/pitch_r*180/PI+90+180/teeth) pinion();
    color([0.6,0.62,0.65]) translate([0,0,1]) rotate(pos/pitch_r*180/PI+90+180/teeth) adapter_blank();
}

module hardware() {
    color([0.7,0.73,0.77]) for(y=[-guide_y,guide_y]) translate([0,y,guide_z]) x_cyl(guide_d,132);
    // ONE generic motor volume only. Body, flange, spline and mounting unknown.
    color([0.22,0.25,0.29]) translate([0,0,-30]) cube([36,28,40],center=true);
    color([0.6,0.63,0.66]) translate([0,0,-6]) cylinder(d=6,h=12,center=true);
}

module collisions(g) {
    pos=g/2+pad_offset;
    intersection() { frame(); moving(g); }
    intersection() { translate([-pos,0,0]) jaw(true); translate([pos,0,0]) rotate(180) jaw(false); }
}

assert(gap>=min_gap && gap<=max_gap,"Gap outside modeled stops");
if(part=="assembly") { color([0.45,0.49,0.53]) frame(); moving(); if(show_hardware) hardware(); }
if(part=="frame") frame();
if(part=="left_jaw") jaw(true);
if(part=="right_jaw") jaw(false);
if(part=="pad") floating_pad();
if(part=="pinion") pinion();
if(part=="adapter") adapter_blank();
if(part=="collision") collisions(gap);
