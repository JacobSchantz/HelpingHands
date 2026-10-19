/* GENERALIST GRIPPER — VERSION 3.2, SIMPLE / gripper plus handles plus base, mm. Fingers 1.21, handles 2.6 (shrunk).
   3.2 (voice-e3cd53d6) is 3.1 made as simple as it can be. Jake: "much simpler: fewer parts and features, as little as
   needed. Nothing should get in the way of the strap-loop slots; keep them completely clear. Shrink the handles part down."
     * the ARM and its hex-boss interface are gone: each side's gear now carries a short CUP that the handle plate's low end
       drops into, below the strap slots. Gear + cup is one print, the DRIVER; the cup is the handle-base interface;
     * nothing comes within strap_clear of either strap slot or the plate edge beside it, at any swing (3.1's arm channel and
       floor ran under the ventral slot); the gears sit strap_clear below the plate's ventral edge;
     * the handle plate is 29 mm across (3.1: 37): slot_wall 2, slot_gap 18;
     * the base plate is just the motor's disc and the left bushing's: no wrist tab (the RS00's back face is the mount).
   Printed parts: 2 fingers, 2 handles, 2 drivers, 1 base (3.1: 9). Screws: the motor's 6 flange + 6 front ring M3 only.
   3.1's notes follow; its arm, interface, and wrist tab no longer apply. */
/* GENERALIST GRIPPER — VERSION 3.1, BASE AND DRIVE / gripper plus handles plus base, mm. Fingers 1.21, handles 2.6.
   3.1 (voice-5b59d3bf) starts the 3.x line: 2.6's fingers and handles, unchanged, on a common base with one motor underneath.
   Jake (key reference cad/reference/generalist_gripper_gen6_closed.png): "the black handles extend back behind the yellow
   fingers, wrap around, and connect into a common base. A single motor is mounted underneath that base; it spins and drives
   gears attached to the black handles." Motor: a RobStride RS00 (the gripper motor of Seeed's reBot Arm B601-RS; Jake's
   correction, replacing the SO-101 STS3215 and then the Damiao DM-J4310-2EC). Stacked down the ventral side (-y), per finger:
     * the ARM (black, the handle's root): a channel that wraps the 2.x handle plate's ventral edge (it also stops the handle
       sliding back out, which in 2.5/2.6 only friction did) and a floor plate running under it to a hub on the finger's pivot;
     * THE HANDLE-BASE INTERFACE, the one thing every handle version and the base share: on each pivot axis, a hex boss
       (iface_hex across flats, iface_depth deep) on the arm drops into a hex socket on top of that side's gear, held by two
       M3 screws on iface_pcd. Any 2.x handle fits by printing an arm from that version's handle params (rail_p, slide_w0,
       slide_t, slide_h, slide_u) with this boss; the gears, base and motor never change;
     * the GEARS: two equal involute spur sectors, pitch radius = the pivot half-spacing, so they mesh on the centreline and
       counter-rotate 1:1 (the left one is half a tooth out of phase). Each has a spigot down into the base plate;
     * the BASE (black): one plate across both pivots under the gears, with a rear tab of wrist-mount holes;
     * the MOTOR underneath, coaxial with the right pivot: its front ring (6 M3 on 50 mm) bolts up to the base plate, its
       output flange (6 M3 on 27 mm) bolts the right gear's spigot through the plate. The left gear turns in its plate hole
       (a plain bushing) and follows through the mesh. Every RS00 dimension is a params.json entry ("Motor" group).
   Every piece is its own module and STL: finger(), strap_slide(), arm(), gear(), base(), motor(). 2.6's notes follow. */
/* GENERALIST GRIPPER — VERSION 2.6, SINGLE STEP / gripper plus handles, mm. Its fingers are 1.21.
   2.6 (voice-72840084) is 2.5 with the top hook moved up the outer edge to where 1.20's edge started going out again. Jake:
   "Extend the black piece where my finger rests all the way up to where the profile starts to go out again. Where it goes
   out again, make it more of a single jump out: no double indent, just out and then back in." So (trace_photo.py top_hook):
     * the outer edge runs straight from the base hook up to the top notch (top_notch_u, floor u 54; 2.5: 28.4), filling
       1.20's 1 mm dip between u 36 and 56;
     * there the mirrored J-hook curls out to its crest (6.6 mm out), and the edge stays out there, level, until the beak's
       outer edge comes back up to it (top_step_back 0): 1.20's top notch, its ramp back in, the dip and the blade-root
       S-curve's climb are now one step out, which the beak then carries on and rounds back in to the point;
     * the handle plate spans floor to floor as in 2.5, now 67.4 mm (2.5: 41.8); same feet, stop strip and slide-in.
   2.5's notes follow.
   GENERALIST GRIPPER — VERSION 2.5, SPANNING HANDLE / gripper plus handles, mm.
   2.5 (voice-56f9d73f) is 2.4 (params.json, the Tune panel) on 1.20's fingers (voice-483f28b9: 1.19's wide beak, 1.18's
   flat-bottom taper, and a top hook mirroring the base J-hook). Jake: "bring the handles down further, and make the handle
   piece extend higher up, so it spans between the gripper's bottom and top hooks and slides in to be captured by both." So:
     * the black handle plate now runs the whole straight outer edge, from the base notch's floor to the top notch's (+span_over
       each end), 41.8 mm (2.4: 28, its foot only partly in the base notch); a foot at each end fills one notch;
     * the two hooks face each other, so nothing can slide in along the edge any more: 2.3's tongue and keyhole pocket are
       gone (the hooks now do their job: hold the handle along the edge and against outboard pull) and the handle slides in
       across the finger's thickness (Y), from the flat ventral face's side, as 1.20's blank does;
     * a stop strip (stop_depth, stop_width) on the plate's inboard face, along its ventral side, butts against the ventral
       face when the handle is home, so it cannot slide on through (1.20 had only friction).
   The finger outline is 1.20's bit for bit (trace_px.scad); top_hook_mirror_u slides the top hook (and the handle's length).
   2.4's notes follow.
   GENERALIST GRIPPER — VERSION 2.4, PARAMETRIC / gripper plus handles, mm.
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
part="assembly"; // assembly | drive | fingers | slides | drivers | base | motor | right_driver | left_driver | viewer_base | viewer_motor | viewer_right_driver | viewer_left_driver | strap_zones | handle_in | handle_sliding | left | right | left_slide | right_slide | collision | none | viewer_left | viewer_right | viewer_left_slide | viewer_right_slide
angle=15;        // each finger's swing about its pivot; 0 = closed (the photo pose)
handle_slide=9;   // 2.5 handle_sliding preview: how far the handle still has to slide in across the finger (from the ventral side, mm)
include <params.scad>   // 2.4: every dimension, by name, generated from params.json by params.py (one source; the live preview's sliders)

// ---------- photo -> mm ----------
include <trace_px.scad>   // outline_px, holes_px, dot_px, slots_px, tip_px, rail_mm, hook_floor_u: generated by trace_photo.py
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
module finger() {whole_finger();}   // Gen 16: all yellow, one body (Gen 15 split off a dark tip pad)

// ---------- the handle (2.5: one plate spanning the base and top hooks, slid in across the finger) ----------
// Rail frame: origin on the finger's outer edge, local +Z (u) runs along the edge toward the tip, local +X (w) points
// outboard, Y is the finger's thickness. The finger is w<0. The base hook's notch floor is at u hook_floor_u[0] (-11.4),
// open toward +u; the top hook's at hook_floor_u[1] (2.6: top_notch_u, 54; 1.20: 28.4), open toward -u; both prongs stand w 4.3..6.6.
// rail_p (params.scad, = trace_px.scad rail_mm): two outer-edge points where the edge is straight within 0.3 mm (u -10 to 36; 2.6: trace_photo.py runs it straight on to the top hook)
rail_a=atan2(rail_p[1][0]-rail_p[0][0],rail_p[1][1]-rail_p[0][1]);   // -10.8 deg off the finger axis
// fit, slide_t, span_over, slide_w0, slot_wall, slot_gap, stop_depth, stop_width, ...: params.scad. Derived here:
strap=[strap_width,strap_thick];   // nominal loop webbing: width, thickness (not measured; not modelled)
strap_slot=[strap[0]+strap_slot_clearance,strap_slot_width];   // strap slot along u, across y
slide_h=2*slot_wall+2*strap_slot[1]+slot_gap;   // the plate's height in y, across the finger's 12 mm thickness: 37 mm
slide_w1=slide_w0+slide_t;   // its outer face, where the digit lies; under both prongs' curl (from w ~4.0)
slide_u=[hook_floor_u[0]-span_over,hook_floor_u[1]+span_over];   // 2.5: the plate's ends along u, past both notch floors
slide_len=slide_u[1]-slide_u[0];   // 67.4 mm at the defaults (2.5: 41.8, 2.4: 28)
slots_u=slide_u[0]+slide_len/2-strap_slot[0]/2;   // both strap slots' low-u end: centred on the plate
neck_over=0.5;            // the stop strip runs this far into the plate, so the two fuse (an overlap, not a dimension)
module rail_frame() {translate([rail_p[0][0],0,rail_p[0][1]]) rotate([0,rail_a,0]) children();}
module yu(h,w0) {multmatrix([[0,0,1,w0],[1,0,0,0],[0,1,0,0],[0,0,0,1]]) linear_extrude(h) children();}   // a 2D (y,u) shape, w0..w0+h in w
function slot_ys()=[-slide_h/2+slot_wall,slide_h/2-slot_wall-strap_slot[1]];   // each slot's low-y side
module strap_slide(du=0,dw=0,dy=0) {   // black: plate + stop strip, two strap slots. du moves it along the edge, dw outboard,
    // dy across the finger (all three for checks only). The plate is trimmed by the finger outline grown by fit, swept the
    // whole plate height in y (the path it slides in on), so each end is a foot that fills its hook's notch.
    translate([0,dy,0]) rail_frame() translate([dw,0,du]) {
        difference() {
            yu(slide_t,slide_w0) offset(r=plate_corner_r) offset(delta=-plate_corner_r) translate([-slide_h/2,slide_u[0]]) square([slide_h,slide_len]);
            for(y=slot_ys())   // the slot cutter runs 1 mm past both plate faces
                yu(slide_t+2,slide_w0-1) translate([y,slots_u]) offset(r=slot_corner_r) offset(delta=-slot_corner_r) square([strap_slot[1],strap_slot[0]]);
            rotate([0,-rail_a,0]) translate([-rail_p[0][0],0,-rail_p[0][1]]) xz(slide_h+2) offset(r=fit) profile();
        }
        if(stop_depth>0)   // 2.5: trails the slide-in (it goes in moving +y), so it never crosses the finger; home, it meets the ventral face
            yu(stop_depth+slide_w0+neck_over,-stop_depth) translate([-plate/2-fit-stop_width,hook_floor_u[0]+fit])
                square([stop_width,hook_floor_u[1]-hook_floor_u[0]-2*fit]);
    }
}
module whole_finger() {
    difference() {
        tapered() xz(plate) profile();  // 1.18's flat-bottom taper (tip_thick < plate). 2.5: no pocket (2.3's tongue is gone)
        xz(plate+2) holes2d();          // every hole goes all the way through (Jake)
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
assert(stop_width<(slide_h-plate)/2-fit,"stop_width runs past the plate's ventral edge");
assert(plate_corner_r<min(slide_len,slide_h)/2,"plate_corner_r is more than half the plate");
assert(slot_corner_r<strap_slot[1]/2,"slot_corner_r must be under half the strap slot width");
assert(strap_slot[0]<slide_len-2,"the strap slots are longer than the plate (the top hook is too low for this strap)");
assert(edge_round>0&&fillet_r>0&&tip_r>0,"rounding radii must be positive");
black="#26272b";
if(part=="assembly") {for(s=[-1,1]) placed(s) {color("#efb83b") finger(); color(black) strap_slide();} drive();}   // 3.1: plus the base and drive (3.2: drivers, base, motor)
if(part=="fingers") color("#efb83b") for(s=[-1,1]) placed(s) finger();
if(part=="slides") color(black) for(s=[-1,1]) placed(s) strap_slide();
if(part=="right") color("#efb83b") finger();
if(part=="left") color("#efb83b") mirror([1,0,0]) finger();
if(part=="right_slide") color(black) strap_slide();
if(part=="left_slide") color(black) mirror([1,0,0]) strap_slide();
if(part=="collision") clash();
if(part=="handle_in") {color("#efb83b") finger(); color(black) strap_slide();}   // 2.5 preview: the right handle seated between the hooks
if(part=="handle_sliding") {color("#efb83b") finger(); color(black) strap_slide(dy=-handle_slide);}   // and part way in, from the ventral side
if(part=="viewer_right") echo(pivot=pivot);   // 2.4: live_render.py reads the hinge from this (the outline moves it)
for(s=[-1,1]) if(part==str("viewer_",s<0?"left":"right")) placed(s) finger();
for(s=[-1,1]) if(part==str("viewer_",s<0?"left":"right","_slide")) placed(s) strap_slide();
// The design numbers web/concept.js draws (export_models.py writes them to web/concept.json): the vision is this plan
// outline and holes extruded to the plate and cut by the flat-bottom taper, plus the handle plate as a plain box with its slots,
// with none of the rounding, grooves, feet or stop strip the solid adds.
if(part=="concept") echo(concept=[pxs(outline_px),
    [for(h=holes_px) [px(h)[0],px(h)[1],hole_d(h)]],
    [px(dot_px)[0],px(dot_px)[1],dot_px[2]*mm_per_px*dot_scale],
    [for(i=[0:len(slots_px)-1]) [px(slots_px[i])[0],px(slots_px[i])[1],frame_deg(slot_angle_deg),(i==len(slots_px)-1?last_slot_scale:1)*slot[0],(i==len(slots_px)-1?last_slot_scale:1)*slot[1]]],
    pivot,angle,plate,tip_t,dot_z+taper_start,tip[1],taper_power,[rail_p[0][0],rail_p[0][1],rail_a],[slide_w0,slide_w1,slide_u[0],slide_u[1],slide_h],
    [for(y=slot_ys()) [y,slots_u,strap_slot[1],strap_slot[0]]]]);   // slide is w0,w1,u0,u1,height in y; slots are (y,u)

// ---------- 3.2: the base and drive (3.1 voice-5b59d3bf, simplified in voice-e3cd53d6) ----------
// Gripper frame as above: X across (right finger +X), Z along the fingers, +Y dorsal. Each pivot axis is Y through
// (+-pivot, 0, 0). The drive stacks down the ventral side (-y); every number is in params.scad.
// cup_*, strap_clear, gear_*, base_*, bush_r, motor_*, stack_gap, screw_clear_d: params.json.
gear_y1=-slide_h/2-strap_clear;   // the gears' top face: strap_clear below the handle plate's ventral edge (y -17.5)
gear_y0=gear_y1-gear_w;
base_y1=gear_y0-stack_gap;        // the base plate's top face
base_y0=base_y1-base_t;           // its underside: the motor's front face bolts up against it
flange_y=base_y0+motor_boss_h;    // the motor's output flange face, inside the plate's hole; the right spigot bolts to it
gear_m=2*pivot/gear_teeth;        // module: pitch radius = the pivot half-spacing, so the two gears mesh on the centreline
gear_rp=pivot; gear_rb=gear_rp*cos(gear_pressure_deg); gear_ra=gear_rp+gear_m; gear_rf=gear_rp-1.25*gear_m;
spigot_d=motor_boss_d-0.5;        // each gear's spigot sits on the motor's output boss (35 mm), 0.5 under it so its rim never lies on the boss's
module slab(y0,h) {translate([0,y0+h/2,0]) xz(h) children();}   // a 2D (x, z) shape made solid from y0 to y0+h
module ring(n,pcd,phase=0) {for(i=[0:n-1]) rotate(phase+i*360/n) translate([pcd/2,0]) children();}   // 2D, about the origin
function inv_deg(a)=(tan(a)-a*PI/180)*180/PI;   // the involute function, in degrees
function flank(r)=90/gear_teeth-gear_backlash/2/gear_rp*180/PI+inv_deg(gear_pressure_deg)-inv_deg(acos(min(1,gear_rb/r)));
module tooth2d() {   // one involute tooth centred on +x, from just inside the root circle to the tip circle
    n=10;r0=max(gear_rb,gear_rf);rr=[for(i=[0:n]) r0+(gear_ra-r0)*i/n];rin=gear_rf-0.5;
    polygon(concat([[rin*cos(-flank(r0)),rin*sin(-flank(r0))]],[for(r=rr) [r*cos(-flank(r)),r*sin(-flank(r))]],
        [for(i=[n:-1:0]) let(r=rr[i]) [r*cos(flank(r)),r*sin(flank(r))]],[[rin*cos(flank(r0)),rin*sin(flank(r0))]]));
}
module gear2d(phase=0) {   // the toothed sector, facing the other pivot (-x for the right gear), plus the hub disc
    sector=[[0,0],for(i=[0:24]) let(t=180-gear_sector_deg/2+gear_sector_deg*i/24) (gear_ra+2)*[cos(t),sin(t)]/cos(gear_sector_deg/48)];
    union() {
        intersection() {
            union() {circle(r=gear_rf,$fn=96); for(i=[0:gear_teeth-1]) rotate(phase+180+i*360/gear_teeth) tooth2d();}
            if(gear_sector_deg<360) polygon(sector);
        }
        circle(d=gear_hub_d,$fn=96);
    }
}
cup_u=[slide_u[0],slide_u[0]+cup_len];    // the cup's run along the edge, from the plate's low end
cup_w=[slide_w0-fit-cup_wall,slide_w1+fit+cup_wall];
module driver(phase=0,cup=cup_len) {   // the right driver in its finger's frame (pivot at the origin): gear sector + spigot + cup.
    // The left is driver(half a tooth) mirrored. cup is for checks only (a longer cup must hit the strap keep-out).
    difference() {
        union() {
            slab(gear_y0,gear_w) gear2d(phase);
            slab(flange_y,gear_y0-flange_y+0.01) circle(d=spigot_d,$fn=96);
            rail_frame() translate([cup_w[0],gear_y1-0.01,cup_u[0]]) cube([cup_w[1]-cup_w[0],-slide_h/2+cup_depth-gear_y1+0.01,cup]);   // the cup
        }
        rail_frame() translate([slide_w0-fit,-slide_h/2-fit,cup_u[0]-1]) cube([slide_t+2*fit,slide_h,cup+2]);   // the handle plate's slot
        slab(flange_y-1,gear_y1-flange_y+2) ring(motor_out_holes,motor_out_pcd,gear_bolt_phase_deg) circle(d=screw_clear_d,$fn=16);
        slab(gear_y1-gear_bolt_head_h,gear_bolt_head_h+1) ring(motor_out_holes,motor_out_pcd,gear_bolt_phase_deg) circle(d=gear_bolt_head_d,$fn=24);
    }
}
module base2d() {hull() {translate([pivot,0]) circle(r=base_r,$fn=96); translate([-pivot,0]) circle(r=bush_r,$fn=96);}}
module base() {   // black: the plate under both drivers; the motor bolts up under the right pivot
    difference() {
        slab(base_y0,base_t) base2d();
        for(s=[-1,1]) slab(base_y0-1,base_t+2) translate([s*pivot,0]) circle(d=(s>0?motor_boss_d:spigot_d)+2*base_clear,$fn=96);   // right: round the motor boss; left: the bushing
        slab(base_y0-1,base_t+2) translate([pivot,0]) ring(motor_front_holes,motor_front_pcd,motor_front_phase_deg) circle(d=screw_clear_d,$fn=16);
        slab(base_y1-motor_screw_head_h,motor_screw_head_h+1) translate([pivot,0]) ring(motor_front_holes,motor_front_pcd,motor_front_phase_deg) circle(d=motor_screw_head_d,$fn=24);
        slab(base_y0-1,base_t+2) translate([pivot,0]) ring(2,motor_front_pcd,motor_dowel_phase_deg) circle(d=motor_dowel_d+2*base_clear,$fn=16);
    }
}
module motor(a=angle) {   // RobStride RS00, reference only (bought, not printed): body, output boss, its tapped and dowel holes
    translate([pivot,0,0]) difference() {
        union() {
            slab(base_y0-motor_len,motor_len) circle(d=motor_d,$fn=96);
            slab(base_y0-0.01,motor_boss_h+0.01) circle(d=motor_boss_d,$fn=96);
        }
        rotate([0,a,0]) slab(flange_y-motor_out_depth,motor_out_depth+1) ring(motor_out_holes,motor_out_pcd,gear_bolt_phase_deg) circle(d=2.5,$fn=12);
        slab(base_y0-motor_front_depth,motor_front_depth+1) ring(motor_front_holes,motor_front_pcd,motor_front_phase_deg) circle(d=2.5,$fn=12);
        slab(base_y0-motor_dowel_depth,motor_dowel_depth+1) ring(2,motor_front_pcd,motor_dowel_phase_deg) circle(d=motor_dowel_d,$fn=12);
        slab(base_y0-motor_len-1,motor_back_depth+1) ring(motor_back_holes,motor_back_pcd,motor_back_phase_deg) circle(d=2.5,$fn=12);
    }
}
// The screw shanks and dowels the checks use, each only as long as the printed part it passes through (they must clear it)
module motor_cores(a=angle) {
    translate([pivot,0,0]) {
        rotate([0,a,0]) slab(flange_y,gear_y1-flange_y) ring(motor_out_holes,motor_out_pcd,gear_bolt_phase_deg) circle(d=3,$fn=12);
        slab(base_y0,base_t) ring(motor_front_holes,motor_front_pcd,motor_front_phase_deg) circle(d=3,$fn=12);
        slab(base_y0,base_t) ring(2,motor_front_pcd,motor_dowel_phase_deg) circle(d=motor_dowel_d,$fn=12);
    }
}
module bolt_access() {slab(gear_y1-gear_bolt_head_h,80) ring(motor_out_holes,motor_out_pcd,gear_bolt_phase_deg) circle(d=gear_bolt_head_d-0.2,$fn=24);}   // checks: a driver's way in to the six flange bolts
// 3.2: the space each strap needs round its slot (right finger's frame): the slot itself, the plate wall outside it, and
// strap_clear round both, on both faces of the plate. Nothing but the handle may enter it, at any swing.
module strap_zone() {
    rail_frame() for(y=slot_ys()) let(y0=y<0?-slide_h/2-strap_clear:y-strap_clear, y1=y<0?y+strap_slot[1]+strap_clear:slide_h/2+strap_clear)
        translate([slide_w0-strap_clear,y0,slots_u-strap_clear]) cube([slide_t+2*strap_clear,y1-y0,strap_slot[0]+2*strap_clear]);
}
half_tooth=180/gear_teeth;
module left_driver() {mirror([1,0,0]) driver(half_tooth);}   // half a tooth out of phase, or the mirrored teeth would meet tip to tip
module driver_piece(q,a=angle,extra=0,cup=cup_len) {   // a driver where it sits at swing a; extra turns it on its axis (checks only)
    if(q=="right") placed(1,a) rotate([0,extra,0]) driver(0,cup);
    if(q=="left") placed(-1,a) rotate([0,extra,0]) driver(half_tooth,cup);
}
module zone_piece(q,a=angle) {if(q=="left") placed(-1,a) strap_zone(); if(q=="right") placed(1,a) strap_zone();}
module side(q,a=angle) {piece(q,a); slide_piece(q,a); driver_piece(q,a);}   // everything that swings with one finger
module drive(a=angle) {
    for(q=["left","right"]) color(black) driver_piece(q,a);
    color(black) base(); color("#a3a8ad") motor(a);
}
assert(base_r>=motor_front_pcd/2+motor_screw_head_d/2+0.5,"base_r is too small for the motor's 50 mm screw ring");
assert(bush_r>=spigot_d/2+base_clear+1.5,"bush_r leaves no wall round the left bushing");
assert(gear_hub_d/2<gear_rf-0.5,"gear_hub_d reaches the tooth roots");
assert(gear_hub_d>=spigot_d,"gear_hub_d must cover the spigot (the motor boss)");
assert(motor_out_pcd/2+gear_bolt_head_d/2<spigot_d/2-0.5,"the motor bolt heads run off the spigot");
assert(gear_sector_deg>=2*max_angle+4*360/gear_teeth,"gear_sector_deg is too short for the 0-30 deg swing");
assert(cup_u[1]<=slots_u-strap_clear,"the cup runs into the strap slots' keep-out: shorten cup_len");
assert(-slide_h/2+cup_depth<-plate/2-fit-stop_width-0.3,"cup_depth reaches the handle's stop strip");
if(part=="drive") drive();
if(part=="drivers") color(black) for(q=["left","right"]) driver_piece(q);
if(part=="base") color(black) base();
if(part=="motor") color("#a3a8ad") motor(0);
if(part=="right_driver") color(black) driver();
if(part=="left_driver") color(black) left_driver();
if(part=="strap_zones") {for(s=[-1,1]) placed(s) {color("#efb83b") finger(); color(black) strap_slide(); color("#ff3b30",0.4) strap_zone();} drive();}
if(part=="viewer_base") base();
if(part=="viewer_motor") motor();
for(q=["left","right"]) if(part==str("viewer_",q,"_driver")) driver_piece(q);
