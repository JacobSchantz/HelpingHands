/* GENERALIST GRIPPER — VERSION 2.4, PARAMETRIC / gripper plus handles, mm.
   2.4 (voice-3211a12d) is 2.3 with every dimension a named, documented parameter: params.json is the one source (params.py
   writes params.scad, included below; trace_photo.py reads the outline ones). At params.json's values the STLs are 2.3's
   byte for byte. New in the params: 1.18's flat-bottom taper (tip_thick < plate), 1.19's outer-edge lean (outer_lean_deg),
   hook_depth, hole/dot scale, the dovetail's neck, flank and depth. The gallery's Tune panel slides them live
   (live_render.py). Make the next version by copying this folder and editing params.json only. 2.3's notes follow.
   GENERALIST GRIPPER — VERSION 2.3, TONGUE AND POCKET / gripper plus handles, mm.
   2.3 (voice-1557d48f) keeps 2.2's black handle (the 28 x 37 x 3.5 mm plate with two strap slots, standing parallel to the
   finger's outer edge face) but drops the yellow lug, the little connector it rode on. Jake: the handle "should slide into
   the gripper": a long, narrow tongue on the handle slides in from the top into a matching pocket running along the finger's
   flat outer face, down to the little hook at its base. So:
     * the plate now lies right against the finger's outer edge face (fit off it), and its bottom end drops into the base
       hook's notch, behind the hook's prong, which holds that end against outboard pull;
     * the tongue runs 23.2 mm along the plate's inboard face, 3.5 mm wide; its lowest head_len mm is a dovetail
       head, the rest a plain bar;
     * the finger's pocket is a keyhole: a dovetail with lips where the head sits fitted, a plain head-wide window just above it
       where the head goes in, and a narrow bar slot above that. Put the head in the window, slide the handle down
       slide_len_in mm: the head goes under the lips and the plate's foot goes behind the hook.
   The finger outline, holes and contact are 2.2's. The pocket opens into the sides of the few honeycomb holes it passes
   (they still go through). 2.2's notes follow.
/* GENERALIST GRIPPER — VERSION 2.2, FLUSH LOOPS / gripper plus handles, mm.
   2.2 (voice-f7f729ac) is 2.1 with each strap slide's plate turned 90 deg about the rail (the finger's outer edge). Jake: the
   flat pieces "shouldn't stick out the way they do"; they lie parallel to the gripper's flat side, flush with it, instead
   of extending outward. The plate now stands against the lug's outer face, parallel to the finger's outer edge face, so it
   adds slide_t (3.5 mm) outboard of the lug instead of 2.1's 33 mm. The two strap slots run through it, one above and one
   below the finger's thickness, and the digit lies against its outer face between them. Finger, lug, dovetail and tongue
   are 2.1's unchanged. 2.1's notes follow.
   GENERALIST GRIPPER — VERSION 2.1, STRAP LOOPS / gripper plus handles, mm.
   2.x is the gripper plus handles (AGENTS.md); 2.1 (voice-4c63021e) is 1.17 (v017_generalist_strap_slide: Gen 16's fingers
   at the full 12 mm thickness to the point) plus the loop attachment: a small, black, flat strap slide with two loop slots
   that slides into a dovetail lug on each finger's outer edge. No camera attachment. Copied, not include'd, from 1.17 so
   later 1.x edits never move 2.1. 1.17's notes follow (its "Gen 17" is this file's 1.17). */
/* GENERALIST GRIPPER — GENERATION 17, STRAP SLIDE / two yellow fingers + two black strap slides, mm.
   Gen 17 (voice-cfdf2d31) is Gen 16 plus how the loops (straps) attach. Jake: "a small, black, flat piece that slides
   into the gripper and has two slots for loops"; "no camera attachment"; "the fingers keep the same thickness along their
   whole length ... the point is only in the closing plane". So:
     * each finger is the full plate thick to the very point (Gen 16 thinned past the dot to tip_thick 2.4: side_taper);
       the plan view, holes, grooves and closed contact are Gen 16 r3's unchanged;
     * a yellow lug on each finger's outer edge, mid-shank (rail_p), holds a dovetail groove, closed at the base end;
     * the strap slide (black, 3.5 mm flat plate) has a dovetail tongue on its inboard edge that slides down the groove from the
       tip end, and two 21 x 3.5 mm strap slots either side of where the digit lies under it (slot_gap).
   Every piece is its own module and STL: finger(), lug(), strap_slide(). Gen 16's notes follow.
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
part="assembly"; // assembly | fingers | slides | handle_in | left | right | left_slide | right_slide | collision | none | viewer_left | viewer_right | viewer_left_slide | viewer_right_slide
angle=15;        // each finger's swing about its pivot; 0 = closed (the photo pose)
include <params.scad>   // 2.4: every dimension, by name, generated from params.json by params.py (one source; the live preview's sliders)

// ---------- photo -> mm ----------
include <trace_px.scad>   // outline_px, holes_px, dot_px, slots_px, tip_px: generated by trace_photo.py
// mm_per_px, px_pivot, axis_deg (photo frame), plate, tip_thick, taper_*, tip_gap, contact_back, tip_r, tip_zone: params.scad

// finger frame (right finger): pivot at origin, inner (gripping) side is -X
function px(q)=let(d=[q[0],q[1]]-px_pivot) mm_per_px*[-(d[0]*sin(axis_deg)-d[1]*cos(axis_deg)), d[0]*cos(axis_deg)+d[1]*sin(axis_deg)];
function pxs(l)=[for(q=l) px(q)];

tip=px(tip_px);
pivot=-min([for(p=pxs(outline_px)) p[0]])+contact_back+tip_gap/2;  // half the pivot spacing: the traced point is the innermost reach, so closed the points meet
ridge=[groove_pitch,groove_width,groove_depth];   // inner-edge grooves: pitch (trace_photo.py places them), width, depth, across the full thickness
ridge_wall=groove_wall;   // least wall kept between a groove and any hole, so no groove opens into one
slot=[slot_len,slot_width];   // blade slot length x width, ~2.2:1 like the photo; the last one is last_slot_scale of it
function frame_deg(img_deg)=90-(img_deg-axis_deg);   // a direction in the photo -> angle in the finger frame

module profile() {     // photo blur -> smooth edges: Gen 13's rounding everywhere, except a sharper tip_r at the point
    tipbox=[[-60,tip[1]-tip_zone],[60,tip[1]-tip_zone],[60,tip[1]+10],[-60,tip[1]+10]];
    union() {
        difference() {profile_body(); polygon(tipbox);}
        intersection() {offset(r=-fillet_r) offset(delta=fillet_r) offset(r=tip_r) offset(delta=-tip_r) polygon(pxs(outline_px)); polygon(tipbox);}
    }
}
module profile_body() {   // Gen 13: edge_round (0.5) on convex corners (r2: 0.35 was a fragile spike), fillet_r (1.2) in concave ones (the shoulder)
    offset(r=-fillet_r) offset(delta=fillet_r) offset(r=edge_round) offset(delta=-2*edge_round) offset(r=edge_round) polygon(pxs(outline_px));
}
function hole_d(h)=max(min_hole,(h[2]+h[3])/2*mm_per_px*hole_scale);
module holes2d() {
    for(h=holes_px) translate(px(h))
        circle(d=hole_d(h));   // the photo reads every honeycomb hole round (Gen 7 r4 review)
    translate(px(dot_px)) circle(d=dot_px[2]*mm_per_px*dot_scale);
    for(i=[0:1:len(slots_px)-1]) translate(px(slots_px[i])) rotate(frame_deg(slot_angle_deg))   // slanted like a forward slash in the photo, ~35 deg off the row
        scale(i==len(slots_px)-1?last_slot_scale:1) hull() for(s=[-1,1]) translate([s*(slot[0]-slot[1])/2,0]) circle(d=slot[1],$fn=16);
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
module finger() {whole_finger();}   // Gen 16: all yellow, one body (Gen 15 split off a dark tip pad); 2.3: the pocket is cut in

// ---------- the handle (2.3: no lug; a tongue in a keyhole pocket in the finger's outer edge) ----------
// Rail frame: origin on the finger's outer edge, local +Z (u) runs along the edge toward the tip, local +X (w) points
// outboard, Y is the finger's thickness. The finger is w<0; the base hook's notch is at u -11.4..-9.2, w 0..4.3, open toward +u.
// rail_p (params.scad): two outer-edge points of the traced outline (web/concept.json), where the edge is straight within
// 0.3 mm from the hook (u -10) to u 29
rail_a=atan2(rail_p[1][0]-rail_p[0][0],rail_p[1][1]-rail_p[0][1]);   // -10.8 deg off the finger axis
// fit, slide_t, slide_len, slide_u0, slide_w0, slot_wall, slot_gap, head_len, bar_d, ...: params.scad. Derived here:
strap=[strap_width,strap_thick];   // nominal loop webbing: width, thickness (not measured; not modelled)
strap_slot=[strap[0]+strap_slot_clearance,strap_slot_width];   // strap slot along u, across y
slide_h=2*slot_wall+2*strap_slot[1]+slot_gap;   // the plate's height in y, across the finger's 12 mm thickness: 37 mm
slide_w1=slide_w0+slide_t;   // its outer face, where the digit lies; the hook's prong (w 4.3..6.6) stands 2.6 mm past it
slots_u=slide_u0+slide_len/2-strap_slot[0]/2;   // both strap slots' low-u end
tongue_n=tongue_width/2;  // the tongue's half width in y (3.5 mm: long and narrow, Jake)
tongue_h=head_width/2;    // the dovetail head's half width
tongue_u=[tongue_start,tongue_start+tongue_length];   // the tongue's ends along u, installed; the pocket ends 0.5 mm above where the edge turns into the notch
neck_over=0.5;            // the tongue's neck runs this far into the plate, so the two fuse (an overlap, not a dimension)
flank_d=neck_d+(tongue_h-tongue_n)/tan(flank_deg);   // depth where the flanks reach the head's full width (2.3: 1.4)
slide_len_in=head_len+2*fit;   // how far the handle slides down from where its head drops into the window
module rail_frame() {translate([rail_p[0][0],0,rail_p[0][1]]) rotate([0,rail_a,0]) children();}
module yu(h,w0) {multmatrix([[0,0,1,w0],[1,0,0,0],[0,1,0,0],[0,0,0,1]]) linear_extrude(h) children();}   // a 2D (y,u) shape, w0..w0+h in w
module along(u0,u1) {translate([0,0,u0]) linear_extrude(u1-u0) children();}   // a 2D (w,y) section, from u0 to u1
module head2d(c=0) {      // the dovetail, in (w,y): neck to w -neck_d, flank_deg out to the head at -flank_d, flat to -head_depth
    offset(delta=c) polygon([[slide_w0+neck_over,tongue_n],[-neck_d,tongue_n],[-flank_d,tongue_h],[-head_depth,tongue_h],
                             [-head_depth,-tongue_h],[-flank_d,-tongue_h],[-neck_d,-tongue_n],[slide_w0+neck_over,-tongue_n]]);
}
module bar2d(c=0) {translate([-bar_d-c,-tongue_n-c]) square([slide_w0+neck_over+bar_d+c,2*(tongue_n+c)]);}
module pocket() {         // cut from the finger: lips where the head sits, the window above it, the bar slot above that
    rail_frame() {
        h0=tongue_u[0]; h1=h0+head_len;
        along(h0-fit,h1+fit) head2d(fit);
        along(h1+fit-cut_eps,h1+slide_len_in+fit) translate([-head_depth-cut_eps-fit,-tongue_h-fit-cut_eps])
            square([head_depth+cut_eps+fit+2,2*(tongue_h+fit+cut_eps)]);   // cut_eps roomier than the lips: no shared faces; +2 runs out past the edge
        along(h0+1,tongue_u[1]+slide_len_in+fit) bar2d(fit);   // starts 1 mm into the head's cut: cutters overlap, never share a face (non-manifold seams)
    }
}
function slot_ys()=[-slide_h/2+slot_wall,slide_h/2-slot_wall-strap_slot[1]];   // each slot's low-y side
module strap_slide(du=0,dw=0) {   // black: plate + tongue, two strap slots. du lifts it along the edge, dw moves it outboard
    // (both for checks only). The plate is trimmed by the finger outline grown by fit, so its foot fits the hook's notch.
    rail_frame() translate([dw,0,du]) {
        difference() {
            yu(slide_t,slide_w0) offset(r=plate_corner_r) offset(delta=-plate_corner_r) translate([-slide_h/2,slide_u0]) square([slide_h,slide_len]);
            for(y=slot_ys())   // the slot cutter runs 1 mm past both plate faces
                yu(slide_t+2,slide_w0-1) translate([y,slots_u]) offset(r=slot_corner_r) offset(delta=-slot_corner_r) square([strap_slot[1],strap_slot[0]]);
            rotate([0,-rail_a,0]) translate([-rail_p[0][0],0,-rail_p[0][1]]) xz(plate+0.01) offset(r=fit) profile();
        }
        along(tongue_u[0],tongue_u[0]+head_len) head2d();
        along(tongue_u[0]+head_len-0.01,tongue_u[1]) bar2d();
    }
}
module whole_finger() {
    difference() {
        tapered() xz(plate) profile();  // Gen 17: full thickness to the point unless tip_thick < plate (2.4: 1.18's flat-bottom taper). 2.3: no lug
        xz(plate+2) holes2d();          // every hole goes all the way through (Jake)
        pocket();                       // 2.3: the handle's keyhole pocket in the outer edge
        xz(plate+2) ridges2d();         // the grooves run across the full thickness of the gripping face (Jake)
    }
}
dot_z=px(dot_px)[1];      // the black dot along the finger: where 1.18's taper starts (+ taper_start)
tip_t=min(tip_thick,plate);
function thick(f)=plate-(plate-tip_t)*pow(f,taper_power);   // taper_power 2 = Gen 16 r2's parabola; the drop is all on the dorsal face (1.18)
module tapered() {        // 2.4: 1.18's taper as a parameter. tip_thick >= plate leaves the solid alone (2.3, bit for bit)
    if(tip_t>=plate) children();
    else intersection() {
        children();
        z0=dot_z+taper_start; L=tip[1]-z0; n=48;   // the ventral face y=-plate/2 stays flat; the dorsal face slopes from z0 to the point
        rotate([90,0,90]) linear_extrude(200,center=true)   // a (y, z) profile, swept across x
            polygon(concat([[-plate/2-1,-50],[plate/2+1,-50],[plate/2+1,z0]],[for(i=[0:n]) [-plate/2+thick(i/n),z0+L*i/n]],
                           [[-plate/2+tip_t,tip[1]+10],[-plate/2-1,tip[1]+10]]));
    }
}
module placed(s=1,a=angle) {
    translate([s*pivot,0,0]) rotate([0,s*a,0]) if(s<0) mirror([1,0,0]) children(); else children();
}
module piece(q,a=angle) {   // a whole finger: what the contact checks use
    if(q=="left") placed(-1,a) whole_finger();
    if(q=="right") placed(1,a) whole_finger();
}
module slide_piece(q,a=angle) {if(q=="left") placed(-1,a) strap_slide(); if(q=="right") placed(1,a) strap_slide();}
module clash(a=angle) {intersection(){piece("left",a);piece("right",a);}}
assert(angle>=0&&angle<=max_angle,"Angle outside intended motion");
// 2.4: combinations of params that make no solid; the live preview shows these messages instead of a broken mesh
assert(head_width>tongue_width,"head_width must be wider than tongue_width (the lips hold the head)");
assert(flank_d<head_depth-0.1,str("the dovetail flanks need head_depth > ",flank_d+0.1," mm at this head width and flank angle"));
assert(head_len<tongue_length-1,"head_len must be shorter than tongue_length");
assert(plate_corner_r<min(slide_len,slide_h)/2,"plate_corner_r is more than half the plate");
assert(slot_corner_r<strap_slot[1]/2,"slot_corner_r must be under half the strap slot width");
assert(strap_slot[0]<slide_len-2,"the strap slots are longer than the plate");
assert(edge_round>0&&fillet_r>0&&tip_r>0,"rounding radii must be positive");
black="#26272b";
if(part=="assembly") for(s=[-1,1]) placed(s) {color("#efb83b") finger(); color(black) strap_slide();}
if(part=="fingers") color("#efb83b") for(s=[-1,1]) placed(s) finger();
if(part=="slides") color(black) for(s=[-1,1]) placed(s) strap_slide();
if(part=="right") color("#efb83b") finger();
if(part=="left") color("#efb83b") mirror([1,0,0]) finger();
if(part=="right_slide") color(black) strap_slide();
if(part=="left_slide") color(black) mirror([1,0,0]) strap_slide();
if(part=="collision") clash();
if(part=="handle_in") {color("#efb83b") finger(); color(black) strap_slide();}   // 2.3 preview: the right handle seated
if(part=="viewer_right") echo(pivot=pivot);   // 2.4: live_render.py reads the hinge from this (the outline moves it)
for(s=[-1,1]) if(part==str("viewer_",s<0?"left":"right")) placed(s) finger();
for(s=[-1,1]) if(part==str("viewer_",s<0?"left":"right","_slide")) placed(s) strap_slide();
// The design numbers web/concept.js draws (export_models.py writes them to web/concept.json): the vision is this plan
// outline and holes extruded to the full plate (Gen 17: no taper), plus the handle plate as a plain box with its slots and
// the tongue as a plain bar, with none of the rounding, grooves, pocket or dovetail head the solid adds.
if(part=="concept") echo(concept=[pxs(outline_px),
    [for(h=holes_px) [px(h)[0],px(h)[1],max(min_hole,(h[2]+h[3])/2*mm_per_px)]],
    [px(dot_px)[0],px(dot_px)[1],dot_px[2]*mm_per_px],
    [for(i=[0:len(slots_px)-1]) [px(slots_px[i])[0],px(slots_px[i])[1],frame_deg(120),(i==len(slots_px)-1?0.7:1)*slot[0],(i==len(slots_px)-1?0.7:1)*slot[1]]],
    pivot,angle,plate,[rail_p[0][0],rail_p[0][1],rail_a],[-bar_d,slide_w0,tongue_u[0],tongue_u[1],2*tongue_n],[slide_w0,slide_w1,slide_u0,slide_u0+slide_len,slide_h],
    [for(y=slot_ys()) [y,slots_u,strap_slot[1],strap_slot[0]]]]);   // 2.3: tongue is w0,w1,u0,u1,width in y; slide is w0,w1,u0,u1,height in y; slots are (y,u)
