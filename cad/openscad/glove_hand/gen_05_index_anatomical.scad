// label: incomplete original-shell experiment (superseded)
// STOPPED: Jake redirected to actual Aero-piece reconstruction/scaling.
// Current source is not validated; last audit found guide/adjacent-part collisions.
// Exported meshes may precede the last source edits. Do not print this package.
// gen_05, original parametric CAD. No upstream CAD, mesh or traced geometry.
// Functional references and checked source licences: compare/gen_05_research.md.
// A hollow wearable finger, not a scaled robotic finger. Palm/finger pads open.
// Provisional fit: measured outline, guessed thickness and joint positions.
// One flexor tendon, three coaxial pin joints, three recessed torsion springs.
// This is a first fit/bench print, not a validated powered wearable.
use <jake_hand.scad>

part = "assembly";       // assembly | proximal | middle | distal | base | drum | lid | coupon | print | check | path | metadata
piece = "proximal";
bend = [0, 0, 0];
pair = ["printed", "thumb"];
thumb_yaw = 22;
thumb_flex = [0, 0];
middle_flex = [0, 0, 0];
neighbour_grow = 0;
show_hand = false;
show_routes = true;
show_hardware = true;
local_part = false;      // exporters: part in its own joint frame

/* [Fit — change these after the dry fit, not the measured hand source] */
clearance = 1.5;
hinge_skin_gap = 1.05;    // compact radial hinge; deliberately less than shell gap
wall = 2.0;
tip_room = 2;
length_scale = [1, 1, 1]; // remeasure MCP-PIP, PIP-DIP, DIP-tip before powered use
roof_flat = 1.2;         // small planar bed land on a rounded dorsal roof
ulnar_inset = 0.5;       // stays inside index's skin width on the middle-finger side
prox_start = 13;
end_gap = 1.4;
strap_width = 6.6;       // 6 mm soft strap, every phalanx
strap_hole = 1.4;        // 0.6-0.8 mm thin strap

/* [Pins, springs and stops] */
limits = [90, 95, 65];
plate_t = [1.6, 2.0, 1.8];
lap_clearance = 0.3;
hinge_r = [4.5, 4.8, 4.5];
pin_fixed = 1.8;         // 1.75 mm filament, heat headed on the bench only
pin_running = 2.05;
stop_radius = [6.1, 6.4, 6.1];
stop_pin = 1.75;         // separate filament follower, not a fragile printed nub
stop_slot_r = 1.1;
stop_depth = 0.8;
spring_pocket_r = 2.35;  // spring OD <=4.3 mm, coil width <=1.4 mm
spring_pocket_depth = 0.6;
spring_leg_slot = 0.65;

/* [Flexor — 0.5 mm braid in removable PTFE liners] */
cord_d = 0.5;
liner_od = 1.6;
liner_bore = 1.85;       // coupon first; no assumption a 1.85 mm FDM hole fits
boss_d = 4.0;
boss_length = 4.5;
cord_low = [4.05, 5.0, 4.0];
cord_reach = [14, 10, 7.5];

/* [Dorsal base and manual test drum] */
base_back = 52;
base_width = 24;
base_z = 22;
base_thickness = 3;
drum_at = [-3, -30, 29.5]; // local MCP frame, axis along z
spool_r = 8;
spool_width = 5;
flange_r = 11;
flange_t = 1.5;
axle_d = 3.3;
cheek_t = 3;
base_strap = 16.6;

$fn = 48;
F = 0;
M = hand_mcp(F);
W = [for (k=[0:3]) jake("finger_base_w")[F] + (jake("finger_tip_w")[F]-jake("finger_base_w")[F])*k/3];
T = [for (k=[0:3]) jake("finger_base_t")[F] + (jake("finger_tip_t")[F]-jake("finger_base_t")[F])*k/3];
raw_l = jake("finger_len")[F]*jake("phalanx");
E = [raw_l[0]*length_scale[0], raw_l[1]*length_scale[1], (raw_l[2]-min(W[3],T[3])/2+tip_room)*length_scale[2]];

function tr(v) = [[1,0,0,v[0]],[0,1,0,v[1]],[0,0,1,v[2]],[0,0,0,1]];
function rx(a) = [[1,0,0,0],[0,cos(a),-sin(a),0],[0,sin(a),cos(a),0],[0,0,0,1]];
function at(m,p) = let(q=m*[p[0],p[1],p[2],1]) [q[0],q[1],q[2]];
function frame(k,b=bend) = k==0 ? rx(-b[0]) : frame(k-1,b)*tr([0,E[k-1],0])*rx(-b[k]);
function clamp(a,lo,hi) = max(lo,min(hi,a));
function half(k,y,g=0) = let(f=clamp(y/E[k],0,1)) [(W[k]+(W[k+1]-W[k])*f)/2+g,(T[k]+(T[k+1]-T[k])*f)/2+g];
function hx(j) = W[j]/2+hinge_skin_gap;
function child_x(j) = hx(j)+plate_t[j]+lap_clearance;
function groove_x() = child_x(0)+plate_t[0]/2;
function guide(k,y,z) = [half(k,y,clearance)[0]+wall+0.1,y,z];
function ys(k) = [k==0 ? prox_start : end_gap, E[k]-end_gap];
function strap_y(k) = k==0 ? 25 : k==1 ? E[k]/2 : E[k]/2+1.8;
function guide_centers(k) = k==0 ? [guide(0,cord_reach[0],-cord_low[0]),guide(0,E[0]-cord_reach[1],-cord_low[1])]
                       : k==1 ? [guide(1,cord_reach[1],-cord_low[1]),guide(1,E[1]-cord_reach[2],-cord_low[2])]
                       : [guide(2,cord_reach[2],-cord_low[2])];
function route_on(k) = [for(q=guide_centers(k)) each [q-[0,boss_length/2,0],q+[0,boss_length/2,0]]];
function turn_point(a) = [groove_x(),-cord_low[0]*cos(a),-cord_low[0]*sin(a)];
// MCP inlet is a fixed vertical tangent; wrap disappears at 90 degrees.
function mcp_arc(b=bend) = [for(i=[0:16]) turn_point((90-b[0])*i/16)];
function cord_path(b=bend) = concat([[groove_x(),-cord_low[0],base_z+6]],mcp_arc(b),
                            [for(k=[0:2]) for(q=route_on(k)) at(frame(k,b),q)]);
function lead_path() = concat(
    [[drum_at[0]+spool_r+cord_d/2,drum_at[1],drum_at[2]],
     [drum_at[0]+spool_r+cord_d/2,drum_at[1]+6,drum_at[2]+3],
     [groove_x(),-14,38]],
    [for(a=[90:-5:0]) [groove_x(),-14+10*cos(a),28+10*sin(a)]]);
function stop_delta(j) = 2*asin((stop_slot_r-stop_pin/2)/(2*stop_radius[j]));

module rod(a,b,r) { v=b-a; translate(a) rotate([0,acos(v[2]/norm(v)),atan2(v[1],v[0])]) cylinder(r=r,h=norm(v)); }
module path_tube(pts,r) { for(i=[0:len(pts)-2]) hull(){ translate(pts[i]) sphere(r); translate(pts[i+1]) sphere(r); } }
module layer(x,t) translate([x,0,0]) rotate([90,0,90]) linear_extrude(t) children();
module cx(x,y,z,r,h) translate([x,y,z]) rotate([0,90,0]) cylinder(r=r,h=h);
module rounded_box(a,b,r=2) hull() for(x=[a[0]+r,b[0]-r]) for(y=[a[1]+r,b[1]-r])
    translate([x,y,a[2]]) cylinder(r=r,h=b[2]-a[2]);
module segment(k,g=0) hand_segment(E[k],W[k],T[k],W[k+1],T[k+1],g);
module finger(g=0) { for(k=[0:2]) multmatrix(frame(k)) segment(k,g); }
module palm(g=0) translate(-M) hand_palm(g);
module thumb(g=neighbour_grow) translate(-M) hand_thumb(g,0,thumb_yaw,thumb_flex);
module neighbour() translate(hand_mcp(1)-M) hand_finger(1,neighbour_grow,0,middle_flex);

// Rounded, tapered Aero-like phalanx envelope; all dimensions are our own.
// Only dorsum and radial flank are rigid. The underside and ulnar flank open.
module oval_section(k,y,extra) translate([0,y,0]) rotate([90,0,0]) linear_extrude(0.02,center=true)
    scale([half(k,y,extra)[0],half(k,y,extra)[1]+roof_flat]) circle(r=1);
module body_envelope(k) {
    y0=ys(k)[0]; y1=ys(k)[1];
    hull(){ oval_section(k,y0,clearance+wall); oval_section(k,y1,clearance+wall);
        if(k==2) translate([0,5,0]) scale([0.82,1,0.82]) oval_section(k,y1,clearance+wall);
    }
}
module body_keep(k) {
    // V relief below the axis; actual limits are in the captive stop tracks.
    y0=ys(k)[0]; y1=ys(k)[1]+(k==2?9:0);
    a=k==0?0:(limits[k]+8)/2;
    d=k==2?0:(limits[k+1]+8)/2;
    layer(-40,80) polygon([[y0,40],[y0,0],[y0+30*tan(a),-30],[y1-30*tan(d),-30],[y1,0],[y1,40]]);
}
module shell_body(k) difference(){
    intersection(){
        body_envelope(k); body_keep(k);
        // The distal roof is a rounded hood, not a cap over the contact pad.
        translate([-W[k]/2+ulnar_inset,-20,-6.5]) cube([60,E[k]+50,60]);
        // planar dorsal land: orientable on the bed after the small taper tilt
        hull() for(y=[-2,E[k]+10])
            translate([-30,y,-30]) cube([60,0.02,30+half(k,y,clearance+wall)[1]]);
    }
    segment(k,clearance);
    // Open underside. Ulnar shell stops above the finger's widest point.
    translate([-40,-20,-40]) cube([40,E[k]+60,40+4]);
    if(k==2) translate([-30,E[k]-1,-30]) cube([60,30,31]);
    // Two true strap slots across the dorsal shoulders; one for each end.
    for(x=[-5.5,5.5]) translate([x-1.0,strap_y(k)-strap_width/2,0]) cube([2.0,strap_width,30]);
}

module ear_shape(j,child=false) {
    r=hinge_r[j];
    union(){
        circle(r=r);
        if(child) hull(){circle(r=r); translate([8,1]) circle(r=2.0);}
        else if(j>0) hull(){circle(r=r); translate([-8,1]) circle(r=2.0);}
        // Parent track is only in the dorsal/anterior quadrant, away from thumb.
        if(!child) for(a=[0:4:94]) hull(){
            translate([stop_radius[j]*sin(a),stop_radius[j]*cos(a)]) circle(r=stop_slot_r+1.5);
            translate([stop_radius[j]*sin(min(a+4,94)),stop_radius[j]*cos(min(a+4,94))]) circle(r=stop_slot_r+1.5);
        }
        if(child) hull(){circle(r=r);translate([0,stop_radius[j]]) circle(r=1.8);}
    }
}
module stop_cut(j,x) {
    aa=-3+stop_delta(j); bb=limits[j]-stop_delta(j);
    for(i=[0:31]) hull(){
        for(a=[aa+(bb-aa)*i/32,aa+(bb-aa)*(i+1)/32])
            cx(x,stop_radius[j]*sin(a),stop_radius[j]*cos(a),stop_slot_r,stop_depth+0.02);
    }
}
module spring_slot(j,child,x) {
    // Two spring legs in face channels: parent points rearward (MCP upward), child forward.
    q=child?[7,0]:(j==0?[0,9]:[-7,0]);
    hull(){ cx(x,0,0,spring_leg_slot/2,spring_pocket_depth+0.02); cx(x,q[0],q[1],spring_leg_slot/2,spring_pocket_depth+0.02); }
}
module ear(j,child=false) difference(){
    layer(child?child_x(j):hx(j),plate_t[j]) ear_shape(j,child);
    cx(hx(j)-1,0,0,(child?pin_running:pin_fixed)/2,2*plate_t[j]+lap_clearance+2);
    // Annular coil recess leaves the central journal and a continuous backing.
    x=child?child_x(j)-0.01:hx(j)+plate_t[j]-spring_pocket_depth;
    difference(){cx(x,0,0,spring_pocket_r,spring_pocket_depth+0.02);cx(x-0.01,0,0,1.18,spring_pocket_depth+0.04);}
    spring_slot(j,child,x);
    // Turn the last 1 mm of each spring leg into the face: it cannot slide out.
    q=child?[7,0]:(j==0?[0,9]:[-7,0]);
    cx(child?child_x(j)-0.01:hx(j)+plate_t[j]-1.1,q[0],q[1],0.4,1.12);
    if(!child) stop_cut(j,hx(j)+plate_t[j]-stop_depth);
    if(child) cx(child_x(j)-1,0,stop_radius[j],pin_fixed/2,plate_t[j]+2);
    // The compact MCP's integral quadrant guide, open at the side for inspection.
    if(j==0 && child) translate([groove_x(),0,0]) rotate([0,90,0]) rotate_extrude($fn=72)
        translate([cord_low[0]+cord_d/2,0]) circle(r=0.58,$fn=20);
}

module guide_boss(q,anchor=false) difference(){
    hull(){ translate(q) rotate([90,0,0]) cylinder(d=anchor?5:boss_d,h=boss_length,center=true);
           translate(q+[-2,0,1.6]) rotate([90,0,0]) cylinder(d=3,h=boss_length,center=true); }
    translate(q) rotate([90,0,0]) cylinder(d=liner_bore,h=boss_length+2,center=true);
    if(anchor) translate(q+[0,boss_length/2-1.1,0]) rotate([-90,0,0]) cylinder(d=3.2,h=1.3);
}
module saddle(k) union(){
 difference(){ union(){
    shell_body(k);
    ear(k,true);
    // Raised narrow bridge keeps the MCP shell out of the palm knuckle dome.
    if(k==0) hull(){ layer(child_x(0),plate_t[0]) translate([7,1]) circle(r=2);
        translate([half(0,prox_start+3,clearance)[0]+0.5,prox_start+3,3]) sphere(r=2.2); }
    if(k>0) hull(){layer(child_x(k),plate_t[k]) translate([8,1]) circle(r=2);
        translate([half(k,9,clearance)[0]+0.5,9,3]) sphere(r=2.2);}
    if(k<2) translate([0,E[k],0]) { ear(k+1,false);
        hull(){layer(hx(k+1),plate_t[k+1]) translate([-8,1]) circle(r=2);
            translate([half(k,E[k]-9,clearance)[0]+0.5,-9,3]) sphere(r=2.2);}}
  }
  // Fixed-size clearance about the wearer, including neighbouring knuckle domes.
  segment(k,clearance);
  if(k==0) palm(clearance+0.2);
  // Swept radial relief around the adjoining cheek plates. The dorsal roof
  // remains continuous; nothing is pinched between overlapping side walls.
  cx(hx(k)-0.3,0,0,10.0,plate_t[k]+0.6);
  if(k<2) cx(child_x(k+1)-0.4,E[k],0,12.0,12);
  // Main pins stay at 1.05 mm radial skin clearance; do not erase their journals.
 }
 for(q=guide_centers(k)) guide_boss(q,k==2);
}

module base_raw() union(){
    rounded_box([-base_width/2,-base_back,base_z],[base_width/2,-5,base_z+base_thickness],4);
    // Dorsal bridge approaches MCP from directly above; no low thumb-web post.
    hull(){translate([7,-6,base_z]) cube([5,4,3]);layer(hx(0),plate_t[0]) translate([0,17]) circle(r=2.2);}
    layer(hx(0),plate_t[0]) hull(){circle(r=hinge_r[0]);translate([0,17]) circle(r=2.2);}
    ear(0,false);
    // Vertical PTFE lead-in aligned with the MCP rear tangent.
    hull(){translate([groove_x(),-cord_low[0],base_z+2]) cylinder(d=4.2,h=6);
        translate([9,-5,base_z]) cube([3,3,3]);}
    // Continuous vertical journal; the cap clamps onto this boss, not the drum.
    translate([drum_at[0],drum_at[1],base_z]) cylinder(d=5.0,h=12.2);
}
module base() difference(){
    base_raw();
    palm(clearance);
    translate([drum_at[0],drum_at[1],base_z-1]) cylinder(d=2.5,h=16);
    translate([groove_x(),-cord_low[0],base_z-1]) cylinder(d=liner_bore,h=13);
    for(y=[-base_back+9,-10]) for(x=[-9,9]) translate([x-1.2,y-base_strap/2,base_z-1]) cube([2.4,base_strap,8]);
    // Drill continuous pin hole after joining the base strut and the parent ear.
    cx(hx(0)-1,0,0,pin_fixed/2,plate_t[0]+2);
    // The strut must not fill the recessed spring / captive-stop track.
    difference(){cx(hx(0)+plate_t[0]-spring_pocket_depth,0,0,spring_pocket_r,spring_pocket_depth+0.02);
        cx(hx(0)-1,0,0,1.18,plate_t[0]+2);}
    spring_slot(0,false,hx(0)+plate_t[0]-spring_pocket_depth);
    cx(hx(0)+plate_t[0]-1.1,0,9,0.4,1.12);
    stop_cut(0,hx(0)+plate_t[0]-stop_depth);
}
module drum() translate(drum_at) difference(){union(){
    translate([0,0,-spool_width/2]) cylinder(r=spool_r,h=spool_width);
    for(z=[-spool_width/2-flange_t,spool_width/2]) translate([0,0,z]) cylinder(r=flange_r,h=flange_t);
    for(a=[0:30:330]) translate([10*cos(a),10*sin(a),spool_width/2]) cylinder(r=1.8,h=flange_t+0.6);
  }
  translate([0,0,-10]) cylinder(d=5.4,h=30);
  translate([spool_r-1.2,0,-10]) cylinder(d=1.0,h=30);
}
module lid() translate([drum_at[0],drum_at[1],base_z+12.3]) difference(){
    cylinder(d=8.8,h=2.0);
    translate([0,0,-1]) cylinder(d=3.3,h=4);
}
module hardware(k) {
    // Main pivot and captive-stop follower: bounded actual filament envelopes.
    cx(hx(k)-0.3,0,0,0.875,2*plate_t[k]+lap_clearance+0.6);
    translate([0,0,stop_radius[k]]) cx(hx(k)+plate_t[k]-0.68,0,0,0.875,plate_t[k]+lap_clearance+0.98);
}
module spring(k) {
    // Visual/integrity envelope only; rate is not claimed from this geometry.
    x=hx(k)+plate_t[k]-0.4;
    for(i=[0:95]) let(a=1080*i/96,b=1080*(i+1)/96)
        rod([x+1.1*i/96,1.65*cos(a),1.65*sin(a)],[x+1.1*(i+1)/96,1.65*cos(b),1.65*sin(b)],0.16);
}
module printed(){base();drum();lid();for(k=[0:2]) multmatrix(frame(k)) saddle(k);}
module route(){ path_tube(concat(lead_path(),cord_path()),cord_d/2); }
module named(n){
    if(n=="base")base(); if(n=="drum")drum(); if(n=="lid")lid();
    if(n=="proximal")multmatrix(frame(0))saddle(0);
    if(n=="middle")multmatrix(frame(1))saddle(1);
    if(n=="distal")multmatrix(frame(2))saddle(2);
    if(n=="printed")printed();
    if(n=="finger")finger(0); if(n=="comfort")finger(clearance); if(n=="palm")palm(clearance);
    if(n=="thumb")thumb(); if(n=="neighbour")neighbour(); if(n=="cord")route();
    if(n=="hardware")for(k=[0:2])multmatrix(frame(k))hardware(k);
}
module coupon(){
    // Four ream/fit diameters plus a short working lap joint with the real recesses.
    difference(){rounded_box([0,0,0],[34,12,3],2);
        for(i=[0:3]) translate([5+8*i,6,-1]) cylinder(d=[1.75,1.8,2.05,1.85][i],h=5);}
    translate([0,24,0]) rotate([0,-90,0]) translate([-hx(1),0,0]) ear(1,false);
    translate([22,24,0]) rotate([0,-90,0]) translate([-child_x(1),0,0]) ear(1,true);
}
module one_local(n){if(n=="proximal")saddle(0);else if(n=="middle")saddle(1);else if(n=="distal")saddle(2);else named(n);}
module print_orientation(n){
    if(n=="proximal"||n=="middle"||n=="distal") {
        k=n=="proximal"?0:n=="middle"?1:2;
        // Dorsal land toward bed. The exporter translates the final mesh to z=0.
        tilt=atan((T[k+1]-T[k])/(2*E[k]));
        rotate([180-tilt,0,0]) one_local(n);
    } else if(n=="drum")drum();
    else if(n=="lid")lid();
    else if(n=="coupon")coupon();
    else base();
}

if(part=="assembly")translate(M){
    color("LightSlateGray")base();color("SlateGray")lid();color("SteelBlue")drum();
    for(k=[0:2])multmatrix(frame(k)){color("Ivory")saddle(k);if(show_hardware){color("DimGray")hardware(k);color("Silver")spring(k);}}
    if(show_routes){color("OrangeRed")route();color([0.8,0.83,0.9,0.45])path_tube(lead_path(),liner_od/2);}
    if(show_hand){color([0.85,0.65,0.5,0.3])finger();color([0.85,0.65,0.5,0.2])palm();color([0.85,0.65,0.5,0.3])thumb();}
}
else if(part=="print")print_orientation(piece);
else if(part=="coupon")coupon();
else if(part=="check")intersection(){named(pair[0]);named(pair[1]);}
else if(part=="path")echo(cord=cord_path(),lengths=E,origin=M);
else if(part=="metadata")echo(lengths=E,widths=W,thicknesses=T,origin=M,limits=limits,
    hinge_x=[for(j=[0:2])hx(j)],child_x=[for(j=[0:2])child_x(j)],groove_x=groove_x(),
    guides=[for(k=[0:2])route_on(k)],stop_radius=stop_radius,plate_t=plate_t,
    drum_at=drum_at,spool_r=spool_r,clearance=clearance,cord_low=cord_low,cord_d=cord_d,lead_path=lead_path(),
    guide_centers=[for(k=[0:2])guide_centers(k)],spring_pocket_r=spring_pocket_r);
else if(local_part)one_local(part);
else translate(M)named(part);
