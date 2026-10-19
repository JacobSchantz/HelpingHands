/* GENERALIST GRIPPER — GENERATION 5 / original inspection CAD, mm.
   ONE jaw(gear_phase) source updates both mirrored finger bodies and interfaces.
   Only tooth phase differs by half a pitch for a REAL external gear mesh.
   ONE servo -> plastic adapter -> right jaw gear -> left jaw gear. No sensor. */
$fn=64;
part="assembly"; // assembly | jaw | left | right | hub | adapter | motor | collision | none | viewer_...
angle=15;
show_motor=true;
max_angle=22;
teeth=24;
module_m=1.2;
pitch_r=teeth*module_m/2;
pivot=pitch_r;
pressure=20;
gear_depth=5;
jaw_depth=18;
channel_radius=8;
channel_depth=5.5;
min_groove_wall=3;
hex_flats=6;
hex_clearance=0.3;

function inv(t)=tan(t)-t*PI/180;
function flank_angle(r)=90/teeth+(inv(pressure)-inv(acos(pitch_r*cos(pressure)/r)))*180/PI;
function polar(r,a)=[r*cos(a),r*sin(a)];
function bezier(p0,p1,p2,p3,t)=[for(k=[0,1]) pow(1-t,3)*p0[k]+3*pow(1-t,2)*t*p1[k]+3*(1-t)*t*t*p2[k]+t*t*t*p3[k]];
function curve(p0,p1,p2,p3)=[for(i=[0:24])bezier(p0,p1,p2,p3,i/24)];
function inner_curve()=concat(
    curve([-12.9,92],[-13.6,90],[-13.9,88],[-13.7,84]),
    curve([-13.7,84],[-13.0,65],[-12.0,43],[-11.5,29]),
    curve([-11.5,29],[-10.8,21],[-7,15],[-4,14]));
function groove_x(z)=9.5-0.0051*(z-34)*(z-34);
function smoothstep(t)=let(u=max(0,min(1,t))) u*u*(3-2*u);
function channel_taper(z)=smoothstep((z-60)/22);
function groove_r(z)=channel_radius-2*channel_taper(z);
function groove_depth(z)=channel_depth-2.5*channel_taper(z);
function reference_gap(a)=2*(pivot-12.7*cos(a)+60*sin(a));
module ycyl(d,h) {rotate([90,0,0]) cylinder(d=d,h=h,center=true);}
module xz(h) {rotate([90,0,0]) linear_extrude(h,center=true) children();}
module round_box(size,r=1) {
    hull() for(x=[-1,1],y=[-1,1],z=[-1,1])
        translate([x*(size[0]/2-r),y*(size[1]/2-r),z*(size[2]/2-r)]) sphere(r=r,$fn=16);
}
module capsule2(a,b,r) {hull(){translate(a) circle(r=r);translate(b) circle(r=r);}}
module gear2d(phase=0) {
    rb=pitch_r*cos(pressure);ra=pitch_r+module_m;rr=pitch_r-1.25*module_m;
    rotate(phase) union() {
        circle(r=rr);
        for(n=[0:teeth-1]) rotate(n*360/teeth) polygon(concat(
           [polar(rr,-flank_angle(rb)+0.2)],
           [for(k=[0:12])let(r=rb+(ra-rb)*k/12)polar(r,-flank_angle(r)+0.2)],
           [for(k=[12:-1:0])let(r=rb+(ra-rb)*k/12)polar(r,flank_angle(r)-0.2)],
           [polar(rr,flank_angle(rb)-0.2)]));
    }
}
module finger_profile() {
    // Actively compared to official Generalist photos: narrow arched body and long pointed taper.
    // Tip is a small rounded curve, not a needle and not a separate black insert.
    polygon(concat(
       curve([5,14],[9,24],[10,38],[8,49]),
       curve([8,49],[6,65],[0,81],[-8,90]),
       curve([-8,90],[-10,94],[-12,95],[-12.9,92]),inner_curve()));
}
module taper_limit(inset=0) {
    // X extrusion of the width envelope, also used for side-wall clearance checks.
    rotate([0,90,0]) linear_extrude(80,center=true)
       polygon([[0,-9+inset],[-65,-9+inset],[-96,-4.04+inset],[-100,-4.04+inset],
                [-100,4.04-inset],[-96,4.04-inset],[-65,9-inset],[0,9-inset]]);
}
module finger_blank() {
    intersection() {xz(jaw_depth) finger_profile();taper_limit();}
}
module finger_groove() {
    // Deep main channel blends narrower/shallower near the tapered tip, keeping side lips intact.
    for(z=[28:2:80]) hull() for(q=[z,z+2])
        translate([groove_x(q)+groove_r(q)-groove_depth(q),0,q]) sphere(r=groove_r(q),$fn=80);
}
module side_wall_guard() {
    difference(){finger_blank();taper_limit(1);}
}
module wall_guard() {
    // A protected 3 mm Euclidean band around the actual continuous inner profile.
    path=inner_curve();
    xz(jaw_depth) for(i=[0:len(path)-2]) capsule2(path[i],path[i+1],min_groove_wall);
}
stop_r=1.5;
stop_R=sqrt(15*15+3*3);
stop_delta=asin(2*stop_r/stop_R)+0.05;
opening_stop_delta=asin((3+2*stop_r)/stop_R)-atan(3/15)+0.05;
function stop_point(a)=[15*cos(a)-3*sin(a),-15*sin(a)-3*cos(a)];
module stop_tab() {translate([0,7,0]) xz(3) capsule2([6,-3],[15,-3],stop_r);}
module finger_body() {
    // This body and ALL its bores/channels are identical for both sides before reflection.
    difference() {
        union() {
            finger_blank();
            xz(jaw_depth) union(){circle(r=8);capsule2([0,5],[0,20],4.5);}
            stop_tab();
        }
        finger_groove();
        ycyl(3.4,40); // common round pivot bore
        // Common rear adapter socket: intentionally unused on the passive jaw.
        translate([0,-7,0]) rotate([90,0,0])
            cylinder(d=(hex_flats+hex_clearance)/cos(30),h=6,center=true,$fn=6);
        // Through-Y anchors near the outer spine; leave inner gripping surface continuous.
        for(z=[34,62]) translate([groove_x(z)-9.5,0,z]) xz(30)
            capsule2([0,-1],[0,1],1.4);
    }
}
module jaw(gear_phase=0,with_teeth=true) {
    // ONLY tooth timing is a handed exception. One shared parametric module, not duplicated bodies.
    difference() {
        union() {finger_body();if(with_teeth) xz(gear_depth) gear2d(gear_phase);}
        ycyl(3.4,40);
        translate([0,-7,0]) rotate([90,0,0])
            cylinder(d=(hex_flats+hex_clearance)/cos(30),h=6,center=true,$fn=6);
    }
}
module placed(s=1,a=angle) {
    translate([s*pivot,0,0]) rotate([0,s*a,0]) if(s<0)mirror([1,0,0])children();else children();
}
module hub() {
    union() {
        for(y=[-12,12]) difference() {
            translate([0,y,0]) xz(4) hull() {
                capsule2([-pivot,0],[pivot,0],6);
                translate([0,-21]) square([48,6],center=true);
                if(y>0)for(s=[-1,1],a=[-stop_delta,max_angle+opening_stop_delta])
                   let(p=stop_point(a)) translate([s*(pivot+p[0]),p[1]])circle(r=3);
            }
            for(s=[-1,1])translate([s*pivot,y,0])ycyl(y<0&&s>0?10.4:3.4,8);
        }
        translate([0,0,-21]) round_box([48,28,6],0.8);
        for(s=[-1,1],a=[-stop_delta,max_angle+opening_stop_delta])let(p=stop_point(a))
            translate([s*(pivot+p[0]),9.5,p[1]])ycyl(2*stop_r,5);
    }
}
module adapter() {
    // Plastic blank: rear horn flange UNDRILLED/UNSPLINED; NOT a selected servo interface.
    difference() {
        union() {
            ycyl(20,3);
            translate([0,4,0])ycyl(10,7.4); // rear journal in hub bore
            translate([0,10,0])rotate([90,0,0])cylinder(d=hex_flats/cos(30),h=5.6,center=true,$fn=6);
        }
        // Blind front pilot for selected rotating retainer; dimensions not hardware-qualified.
        translate([0,11,0])ycyl(2.5,10);
    }
}
module motor() {
    // ONE honest off-center servo envelope. Actual body/shaft/horn dimensions pending.
    translate([pivot,-38,-3])round_box([36,38,30],2);
    translate([pivot,-18,0])ycyl(6,5);
}
module piece(q,a=angle) {
    if(q=="hub")hub();
    if(q=="left")placed(-1,a)jaw(180/teeth);
    if(q=="right")placed(1,a)jaw(0);
    if(q=="adapter")translate([pivot,-17,0])rotate([0,a,0])adapter();
    if(q=="motor")motor();
}
module moving(a=angle,teeth_on=true) {
    placed(-1,a)jaw(180/teeth,teeth_on);
    placed(1,a)jaw(0,teeth_on);
}
module gear_pair(a=angle,phase_error=0) {
    intersection() {
        placed(-1,a+phase_error)xz(gear_depth)gear2d(180/teeth);
        placed(1,a)xz(gear_depth)gear2d(0);
    }
}
module clash(a=angle) {
    intersection(){hub();moving(a);}
    intersection(){placed(-1,a)jaw(180/teeth);placed(1,a)jaw(0);}
    intersection(){hub();piece("adapter",a);}
    // Adapter socket engagement is intentional; do not count it as a clearance pair.
}
assert(angle>=0&&angle<=max_angle,"Angle outside intended motion");
echo(jaw_angle_deg=angle,reference_gap_mm=reference_gap(angle));
if(part=="assembly") {
    color("#3d4653")hub();
    color("#efb83b")moving();
    color("#abb4bc")piece("adapter");
    if(show_motor)color("#252e38")motor();
}
if(part=="jaw"||part=="right")jaw(0);
if(part=="left")jaw(180/teeth);
if(part=="hub")hub();
if(part=="adapter")adapter();
if(part=="motor")motor();
if(part=="collision")clash();
for(q=["hub","left","right","adapter","motor"])if(part==str("viewer_",q))piece(q);
