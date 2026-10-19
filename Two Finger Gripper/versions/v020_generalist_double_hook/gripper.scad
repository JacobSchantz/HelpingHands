/* GENERALIST GRIPPER — VERSION 1.20, DOUBLE HOOK / two yellow fingers + a black handle blank each, mm.
   1.20 (voice-483f28b9) builds on 1.19. Jake: "the gripper should have a hook at both the bottom AND the top along the flat
   face, so the handle piece slides in and is held by both hooks." So:
     * the outline gains a second hook at the top of the straight outer edge: trace_photo.py top_hook() mirrors the base
       J-hook end for end about the middle of the edge, so the two notches face each other, 39.8 mm apart floor to floor
       (hook_floor_u); the rest of the finger is 1.19's;
     * a handle blank (black, handle_t thick, the finger's plate tall) lies against the outer edge with a foot in each notch.
       The hooks face each other, so it cannot drop in along the edge: it slides in sideways, across the finger's thickness
       (Y), and is then held along the edge by both notch floors and against outboard pull by both prongs. It is a fit blank,
       not 2.x's strap handle: no strap slots (the loops are the 2.x line).
   1.19 (voice-13bdab11) builds on 1.18. Jake: "make the section from where the finger starts rounding to the tip much
   thicker. Extend the width outward through that rounded section, but it should still come to a point at the tip." The
   plan outline past the black dot is wider on the outer side (trace_photo.py OUTER), the point and inner edge are 1.18's;
   contact_back is re-measured. Everything in this file is otherwise 1.18's.
   1.18 (voice-07e1e6a1) corrects 1.17 (Gen 17). Jake: "the fingers SHOULD taper in thickness toward the tip like the
   Generalist reference gripper does. But keep one face flat so it's easy to 3D print: the taper goes down from one side
   only (a flat bottom with the top sloping down toward the tip), not a symmetric taper toward the midplane." So:
     * from the black dot to the point the dorsal (+Y) face slopes down on Gen 16 r2's parabola to tip_thick at the point;
       the ventral (-Y) face stays one flat plane from base to point (flat_taper), so a finger prints lying on it;
     * gripper only (the 1.x line): 1.17's lug and strap slide are left out; the loops live in the 2.x line;
     * the plan view, holes, grooves and closed contact are Gen 16 r3's, unchanged.
   Gen 17's notes (the full-thickness finger and the strap slide this version drops) are in v017_generalist_strap_slide.
   GENERATION 16, ROUNDED POINT.
   Gen 16 (voice-1fc7e062) combines Gen 15 and Gen 9. Jake: "keep Gen 15's length; keep the ridges but make them
   shallower, about 1 mm, less pronounced; make it more rounded like Gen 9; have it come to a nice point like Gen 9
   does, but the two sides should actually touch at the point; remove the black tip, so it is all yellow."
     * plan view (trace_photo.py): Gen 15's beak, length and point contact; Gen 9's smoothed contour, rounded blade
       root and J-hook; the two square inner-edge knobs are now rounded 1 mm swells on a smooth ramp;
     * side view: a parabola from the dot to a thick tip_thick point (r1: Gen 9's eased needle; Gen 15: 1.6 mm);
     * one yellow body per finger: Gen 15's dark tip pad is gone.
   r2 (Jake; key reference cad/reference/generalist_gripper_gen6_closed.png): the two knobs much rounder; closed, only the
   points touch and a 30 deg V opens right behind them (r1: 6.8); the outer edge rounds in to a thick tip in plan (NOSE) and
   side view (tip_thick 2.4).
   r3 (Jake): closed, the jaws form a triangle into the point, never parallel (trace_photo.py TRIANGLE); the outer edge runs
   nearly straight to the point (OUTER); the joins at the dot are smoothed. Gen 15's notes follow.
   GENERATION 15, LONG JAW.
   Gen 15 (voice-8673a6b6) is Gen 14 with the beak past the black dot 1.7x longer (trace_photo.py BEAK_STRETCH), so dot ->
   point is a third of the finger: Jake, "that thick end section should be quite a bit longer, about a third of the total
   finger length". Everything behind the dot, the contact spec and this file's modelling are Gen 14's; contact_back is
   re-measured. Gen 14's notes follow.
   GENERATION 14, ONLY THE POINTS TOUCH.
   A refinement pass on Gen 13 (voice-fe67959c). Jake: "just the tip contacts. I think there's a little
   too much contact leading up to the tip, maybe not quite a tight, sharp enough contact angle", and "from
   the photos, see if there's anything that can be improved ... for example, the tips."
   Everything is Gen 13's (designed closed from cad/reference/generalist_gripper_gen6_closed.png, serration
   along the inner edge, beak, through-holes) except:
     * the contact: closed, each inner edge leaves the point at 4 deg (trace_photo.py WEDGE) to a 0.35 mm
       gap, then follows the photo's curve +0.1 mm, so the jaws open right behind the point instead of
       staying ~0.01 mm apart for 8 mm;
     * the point: rounded at tip_r=0.3 mm in plan, not Gen 13's ~1 mm nubs, so it is the point that meets;
     * the dark tip: every photo shows a dark nub at each point (closed, robot, top, two-hands). The last
       pad_len mm is a separate body ("tip pad", dark) for a two-material print; finger + pad = the full
       finger, so every contact check runs on the two together;
     * the grooves stop behind the pad (trace_photo.py RIDGE_STOP_PX).
   Gen 13's notes: trace_closed.py traces both closed fingers (closed_sketch.png) and measures the gap
   between the jaws; trace_photo.py shapes Gen 11 r4's beak to it. The plan-view shape, honeycomb, dot and
   slots are still Gen 11 r4's trace of the two-hands photo (trace_photo.py -> trace_px.scad).
   Axes: X across (right finger +X), Z along the fingers (tips +Z), +Y = dorsal. */
$fn=32;
part="assembly"; // assembly | fingers | left | right | handles | right_handle | left_handle | handle_in | collision | none
                 // | viewer_left | viewer_right | viewer_left_handle | viewer_right_handle
angle=15;        // each finger's swing about its pivot; 0 = closed (the photo pose)
max_angle=30;
handle_slide=0;  // 1.20 handle_in preview: how far the handle blank still has to slide in across the finger (+Y, mm)

// ---------- photo -> mm ----------
include <trace_px.scad>   // outline_px, holes_px, dot_px, slots_px, tip_px: generated by trace_photo.py
mm_per_px=0.2;            // ~110 mm pivot-to-tip; no measured scale, see README
px_pivot=[337,395];       // frame origin only: the photo shows the lip solid, so no bore is cut (the joint is under the carrier)
axis_deg=36.5;            // bisector of the two closed fingers in the photo (27 and 46 deg)
plate=12;                 // finger thickness along Y behind the dot, centred on the hand plane
tip_thick=2.4;            // 1.18: thickness at the point, Gen 16 r2's (Jake: "make the tip thicker"); Gen 17 kept the full 12
tip_gap=0;                // closed: the points touch (Gen 11: 1.0 mm apart)
contact_back=0.0005;      // 1.19: the wider point keeps its full reach through the tip_r round (mesh innermost reach 27.25066 = outline's), so the pivots sit 0.5 um outboard of touching. r3: -0.0651; the triangle point rounds further back: mesh innermost reach 27.1856 vs outline 27.2507, so the pivots move in. How far the smoothed point sits outboard of the traced one (see pivot). Gen 15: the mesh's innermost reach
                          // is 27.2507 mm vs the trace's 27.2500 (Gen 14: -0.028), so the pivots sit 1 um outboard of touching
tip_r=0.3;                // Gen 14: plan-view radius of the point (Gen 13 rounded it ~1 mm, two nubs with a V between)
tip_zone=6.25;            // the sharper rounding applies within this many mm of the point; elsewhere Gen 13's. r3: 6.25, off the 1 mm groove pitch (at 6 a groove wall sat on the cut: non-manifold)

// finger frame (right finger): pivot at origin, inner (gripping) side is -X
function px(q)=let(d=[q[0],q[1]]-px_pivot) mm_per_px*[-(d[0]*sin(axis_deg)-d[1]*cos(axis_deg)), d[0]*cos(axis_deg)+d[1]*sin(axis_deg)];
function pxs(l)=[for(q=l) px(q)];

tip=px(tip_px);
dot_z=px(dot_px)[1];      // 1.18: the taper starts at the black dot, as in Gen 16 (side + robot photos)
pivot=-min([for(p=pxs(outline_px)) p[0]])+contact_back+tip_gap/2;  // half the pivot spacing: the traced point is the innermost reach, so closed the points meet
min_hole=1.8;             // blurred small holes are read no smaller than this
ridge=[1.0,0.5,0.4];      // inner-edge grooves: pitch (set in trace_photo.py), width, depth (mm), across the full thickness.
                          // Gen 12's shallow 0.4 mm; the closed photo shows them along essentially the whole inner edge
ridge_wall=0.6;           // least wall kept between a groove and any hole, so no groove opens into one
slot=[3.0,1.35];          // blade slot length x width, ~2.2:1 like the photo; the last one is ~70%
function frame_deg(img_deg)=90-(img_deg-axis_deg);   // a direction in the photo -> angle in the finger frame

module profile() {     // photo blur -> smooth edges: Gen 13's rounding everywhere, except a sharper tip_r at the point
    tipbox=[[-60,tip[1]-tip_zone],[60,tip[1]-tip_zone],[60,tip[1]+10],[-60,tip[1]+10]];
    union() {
        difference() {profile_body(); polygon(tipbox);}
        intersection() {offset(r=-1.2) offset(delta=1.2) offset(r=tip_r) offset(delta=-tip_r) polygon(pxs(outline_px)); polygon(tipbox);}
    }
}
module profile_body() {   // Gen 13: 0.5 mm on convex corners (r2: 0.35 was a fragile spike), 1.2 mm fillets in concave ones (the shoulder)
    offset(r=-1.2) offset(delta=1.2) offset(r=0.5) offset(delta=-1.0) offset(r=0.5) polygon(pxs(outline_px));
}
module holes2d() {
    for(h=holes_px) translate(px(h))
        circle(d=max(min_hole,(h[2]+h[3])/2*mm_per_px));   // the photo reads every honeycomb hole round (Gen 7 r4 review)
    translate(px(dot_px)) circle(d=dot_px[2]*mm_per_px);
    for(i=[0:len(slots_px)-1]) translate(px(slots_px[i])) rotate(frame_deg(120))   // slanted like a forward slash in the photo, ~35 deg off the row
        scale(i==len(slots_px)-1?0.7:1) hull() for(s=[-1,1]) translate([s*(slot[0]-slot[1])/2,0]) circle(d=slot[1],$fn=16);
}
module ridges2d() {       // one groove per station on the inner edge (ridges_px from trace_photo.py), square to the edge.
    // Its depth is measured from the finished edge (the band between profile() and its inset), and it stops
    // ridge_wall short of every hole, so the grooves are all exactly ridge[2] deep and never open a hole.
    difference() {
        intersection() {
            for(r=ridges_px) let(c=px([r[0],r[1]]), n=px([r[0]+r[2],r[1]+r[3]])-c, a=atan2(n[1],n[0]))
                translate(c) rotate(a) translate([-2*ridge[2],-ridge[1]/2]) square([4*ridge[2],ridge[1]]);
            difference() {offset(delta=1) profile(); offset(r=-ridge[2]) profile();}   // past the edge, so no skin is left
        }
        offset(r=ridge_wall) holes2d();
    }
}
module xz(h) {rotate([-90,0,0]) mirror([0,1,0]) linear_extrude(h,center=true) children();}
module finger() {whole_finger();}   // all yellow, one body
function thick(f)=plate-(plate-tip_thick)*f*f;   // Gen 16 r2's parabola (full to near the dot, easing down to the point), but
                          // the whole drop is on the dorsal face: 1.18 (Gen 16 split it between both faces)
module flat_taper() {     // Y-Z profile: the ventral face y=-plate/2 is flat everywhere; the dorsal face is flat to the dot, then slopes
    L=tip[1]-dot_z; n=48;
    rotate([90,0,90]) linear_extrude(200,center=true)
        polygon(concat([[-plate/2-1,-50],[plate/2+1,-50],[plate/2+1,dot_z]],
                       [for(i=[0:n]) [-plate/2+thick(i/n),dot_z+L*i/n]],
                       [[-plate/2+tip_thick,tip[1]+10],[-plate/2-1,tip[1]+10]]));
}
module whole_finger() {
    difference() {
        intersection() {xz(plate) profile(); flat_taper();}   // 1.18: tapered from the dorsal face only
        xz(plate+2) holes2d();          // every hole goes all the way through (Jake)
        xz(plate+2) ridges2d();         // the grooves run across the full thickness of the gripping face (Jake)
    }
}
// ---------- 1.20: the handle blank between the two hooks ----------
// Rail frame (trace_px.scad rail_mm, as 2.3's): origin on the finger's straight outer edge, local +Z (u) runs along it toward
// the tip, local +X (w) points outboard, Y is the finger's thickness. The finger is w<0; the notch floors are hook_floor_u.
rail_a=atan2(rail_mm[1][0]-rail_mm[0][0],rail_mm[1][1]-rail_mm[0][1]);   // -10.8 deg off the finger axis
fit=0.2;                  // clearance per side, handle to finger
handle_t=3.5;             // the blank's thickness in w (2.3's plate); each prong's curl starts at w ~4.0, so the foot sits under it
handle_w0=0.45;           // its inboard face: fit off the outer edge, which reaches w +0.17 at most (2.3)
handle_h=plate;           // across the finger's thickness: flush with both faces when slid home
module rail_frame() {translate([rail_mm[0][0],0,rail_mm[0][1]]) rotate([0,rail_a,0]) children();}
module handle(dw=0,du=0,dy=0) {   // black. dw moves it outboard, du along the edge, dy across the finger (checks only).
    // A plate from one notch floor to the other, trimmed by the finger outline grown by fit, so each foot fills its notch.
    translate([0,dy,0]) rail_frame() translate([dw,0,du]) difference() {
        translate([handle_w0,-handle_h/2,hook_floor_u[0]-1]) cube([handle_t,handle_h,hook_floor_u[1]-hook_floor_u[0]+2]);
        rotate([0,-rail_a,0]) translate([-rail_mm[0][0],0,-rail_mm[0][1]]) xz(plate+2) offset(r=fit) profile();
    }
}
module placed(s=1,a=angle) {
    translate([s*pivot,0,0]) rotate([0,s*a,0]) if(s<0) mirror([1,0,0]) children(); else children();
}
module piece(q,a=angle) {   // a whole finger: what the contact checks use
    if(q=="left") placed(-1,a) whole_finger();
    if(q=="right") placed(1,a) whole_finger();
}
module clash(a=angle) {intersection(){piece("left",a);piece("right",a);}}
assert(angle>=0&&angle<=max_angle,"Angle outside intended motion");
black="#26272b";
if(part=="assembly") for(s=[-1,1]) placed(s) {color("#efb83b") finger(); color(black) handle();}
if(part=="fingers") color("#efb83b") for(s=[-1,1]) placed(s) finger();
if(part=="handles") color(black) for(s=[-1,1]) placed(s) handle();
if(part=="right") color("#efb83b") finger();
if(part=="left") color("#efb83b") mirror([1,0,0]) finger();
if(part=="right_handle") color(black) handle();
if(part=="left_handle") color(black) mirror([1,0,0]) handle();
if(part=="handle_in") {color("#efb83b") finger(); color(black) handle(dy=handle_slide);}   // 1.20 preview: the right blank sliding in
if(part=="collision") clash();
for(s=[-1,1]) if(part==str("viewer_",s<0?"left":"right")) placed(s) finger();
for(s=[-1,1]) if(part==str("viewer_",s<0?"left":"right","_handle")) placed(s) handle();
// The design numbers web/concept.js draws (export_models.py writes them to web/concept.json): the vision is this plan
// outline and holes extruded to the plate and cut by the flat-bottom taper, with none of the rounding or grooves the solid adds;
// 1.20: plus the handle blank as a plain box between the notch floors.
if(part=="concept") echo(concept=[pxs(outline_px),
    [for(h=holes_px) [px(h)[0],px(h)[1],max(min_hole,(h[2]+h[3])/2*mm_per_px)]],
    [px(dot_px)[0],px(dot_px)[1],dot_px[2]*mm_per_px],
    [for(i=[0:len(slots_px)-1]) [px(slots_px[i])[0],px(slots_px[i])[1],frame_deg(120),(i==len(slots_px)-1?0.7:1)*slot[0],(i==len(slots_px)-1?0.7:1)*slot[1]]],
    pivot,angle,plate,tip_thick,dot_z,tip[1],
    [rail_mm[0][0],rail_mm[0][1],rail_a],[handle_w0,handle_w0+handle_t,hook_floor_u[0]+fit,hook_floor_u[1]-fit,handle_h]]);   // 1.20: the handle blank as a plain (w, u) box
