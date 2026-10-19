/* GENERALIST GRIPPER — BASE 4, ONE-PIECE DRIVE / gripper plus handles plus base, mm. Gripper 21, Handle 7.
   Base 4 (voice-b7260e73) is Base 3 with fewer pieces. Jake: "Simplify again: there are too many pieces. Focus especially on how
   the base links to the handle; that connection has too many parts." Base 3's chain was finger -> handle (tail + key) -> gear
   cradle (key notch) -> gear axle -> base bushing, plus a stop strip on the handle. So:
     * each HANDLE AND ITS SIDE GEAR ARE ONE PRINT: the handle's tail is fused into the gear hub; no key, no key notch, no cradle
       fit. The finger drops into it from the dorsal side (+y down to -y): its base hook goes between the handle's feet, its base
       corner into a pocket in the hub cut tail_gap off it, and it rests on the gear's web. So the web is the stop and Handle 7's
       stop strip is gone; the handle is exactly the finger's 12 mm (handle_over 0, Handle 7's height);
     * the pinion keeps 3 of the RS00 flange's 6 holes (motor_out_screws) and the base 3 of the front ring's 6
       (motor_front_screws), every other one; the two dowels still locate the base.
   Chain now: finger -> handle-gear -> base bushing. Pieces: 6 printed (2 fingers, 2 handle-gears, 1 pinion, 1 base; Base 3: 8)
   + the RS00 + 6 M3 screws (Base 3: 12) = 13 (Base 3: 21). Base 3's notes follow; its key, cradle and stop strip no longer apply. */
/* GENERALIST GRIPPER — VERSION 3.3, IN-PLANE DRIVE / gripper plus handles plus base, mm. Fingers 1.21.
   3.3 (voice-3b311f32) is 3.2 laid out again. Jake: "Reduce the handle height again: just barely taller than the gripper
   fingers themselves. Rework how the handle attaches to the base and gear system so it attaches much more smoothly. Put the
   gears in the same plane as the gripper fingers (move the gears up), with a single motor centered there. The handle wraps
   around and connects into the gear system." So:
     * the handle plate is plate + 2 x handle_over = 15 mm across the finger (3.2: 29). There is no room for a strap slot
       beside the finger any more, so the strap runs through a TUNNEL instead: a boss on the plate's outer face (where the digit
       lies) with a gap under it, open at both faces of the plate; the webbing goes in one face and out the other, round the digit;
     * the handle's TAIL: a band slide_t thick that follows the finger's outline tail_gap off it, from the plate over the base
       hook's prong, round the hook and on under the finger's base. The handle now wraps the finger's base;
     * the GEARS sit in the finger plane (3.2: stacked under it), centred on the finger's mid-plane, below the fingers. Each side
       gear's hub is a CRADLE: cut to the finger and the tail fit off them, so the finger-and-handle unit drops straight into
       it and the tail is the key that turns it. A web under them reaches in to the pivot axle (the pivot is inside the finger's
       base corner), which turns in a plain bushing in the base;
     * ONE RS00, CENTRED: its PINION sits on the centreline below the side gears and meshes the right gear only; the right and
       left gears mesh each other, so the fingers still counter-rotate (a pinion meshing both would turn them the same way).
       Each side gear carries teeth only where its mates meet it over the swing, so the left one never reaches the pinion;
     * the base is the hull of the motor's disc and the two bushings' discs; the motor bolts up under its centre.
   Printed parts: 2 fingers, 2 handles, 2 gears, 1 pinion, 1 base (3.2: 7). Screws: the motor's 6 flange + 6 front ring M3.
   3.2's notes follow; its drivers, cups and strap slots no longer apply. */
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
part="assembly"; // assembly | drive | gears | inplane | cradle | handle_gear | fingers | slides | base | motor | pinion | right_gear | left_gear | viewer_base | viewer_motor | viewer_pinion | viewer_right_gear | viewer_left_gear | strap_zones | handle_in | handle_sliding | left | right | left_slide | right_slide | collision | none | viewer_left | viewer_right | viewer_left_slide | viewer_right_slide
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
// fit, slide_t, span_over, slide_w0, handle_over, slot_wall, ...: params.scad. Derived here:
strap=[strap_width,strap_thick];   // nominal loop webbing: width, thickness (not measured; not modelled)
strap_slot=[strap[0]+strap_slot_clearance,strap_slot_width];   // 3.3: the strap tunnel: along u, and its gap in w
slide_h=plate+2*handle_over;   // 3.3: the plate's height in y, just past the finger's 12 mm: 15 mm (3.2: 29)
slide_w1=slide_w0+slide_t;   // its outer face; under both prongs' curl (from w ~4.0)
slide_u=[hook_floor_u[0]-span_over,hook_floor_u[1]+span_over];   // 2.5: the plate's ends along u, past both notch floors
slide_len=slide_u[1]-slide_u[0];   // 67.4 mm at the defaults (2.5: 41.8, 2.4: 28)
slots_u=slide_u[0]+slide_len/2-strap_slot[0]/2;   // the strap tunnel's low-u end: centred on the plate
boss_u=[slots_u-slot_wall,slots_u+strap_slot[0]+slot_wall];   // 3.3: the strap boss on the plate's outer face, along u
boss_w1=slide_w1+strap_slot[1]+slot_wall;   // and its outer face, where the digit lies
module rail_frame() {translate([rail_p[0][0],0,rail_p[0][1]]) rotate([0,rail_a,0]) children();}
module rail2d() {translate(rail_p[0]) rotate(-rail_a) children();}   // 3.3: a 2D (w, u) shape into the finger's 2D (x, z) plan
module yu(h,w0) {multmatrix([[0,0,1,w0],[1,0,0,0],[0,1,0,0],[0,0,0,1]]) linear_extrude(h) children();}   // a 2D (y,u) shape, w0..w0+h in w
module wu(h) {multmatrix([[1,0,0,0],[0,0,-1,h/2],[0,1,0,0],[0,0,0,1]]) linear_extrude(h) children();}   // 3.3: a 2D (w,u) shape, y -h/2..h/2
module rounded(r) {offset(r=r) offset(delta=-r) children();}
// 3.3: the tail. A band slide_t thick that follows the finger's outline tail_gap off it, from tail_top_u on the plate, over the
// base hook's prong, round the hook and on under the finger until tail_reach inboard of the edge line: the handle wraps the
// finger's base. Finger frame, 2D (x, z). Base 4: it is fused into the gear hub, so 3.3's key (and the hub's notch for it) is gone.
module tail2d() {
    intersection() {
        difference() {offset(r=tail_gap+slide_t) profile(); offset(r=tail_gap) profile();}
        rail2d() translate([-tail_reach,-60]) square([80,60+tail_top_u]);
    }
}
module handle_body() {   // black, in the finger's frame: plate + strap boss and tunnel + tail (Base 4: no stop strip; the gear web stops the finger)
    difference() {
        union() {
            rail_frame() {
                yu(slide_t,slide_w0) rounded(plate_corner_r) translate([-slide_h/2,slide_u[0]]) square([slide_h,slide_len]);
                wu(slide_h) rounded(slot_corner_r) translate([slide_w1-slide_t/2,boss_u[0]]) square([boss_w1-slide_w1+slide_t/2,boss_u[1]-boss_u[0]]);   // from mid-plate, so its rounding stays inside
            }
            xz(slide_h) tail2d();
        }
        rail_frame() wu(slide_h+2) rounded(slot_corner_r) translate([slide_w1,slots_u]) square([strap_slot[1],strap_slot[0]]);   // the tunnel, y right through
        xz(slide_h+2) offset(r=fit) profile();   // the plate's feet fill both notches; the tail clears the hook
    }
}
module strap_slide(du=0,dw=0,dy=0) {   // the handle where it sits on the right finger. du moves it along the edge, dw outboard,
    // dy across the finger (all three for checks only).
    translate([0,dy,0]) rail_frame() translate([dw,0,du]) rotate([0,-rail_a,0]) translate([-rail_p[0][0],0,-rail_p[0][1]]) handle_body();
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
assert(plate_corner_r<min(slide_len,slide_h)/2,"plate_corner_r is more than half the plate");
assert(slot_corner_r<strap_slot[1]/2,"slot_corner_r must be under half the strap tunnel gap");
assert(strap_slot[0]<slide_len-2,"the strap tunnel is longer than the plate (the top hook is too low for this strap)");
assert(boss_u[0]>tail_top_u+1&&boss_u[1]<hook_floor_u[1]-4,"the strap boss runs into a hook: shorten the strap or move the top hook");
assert(edge_round>0&&fillet_r>0&&tip_r>0,"rounding radii must be positive");
black="#26272b";
if(part=="assembly") {for(s=[-1,1]) placed(s) color("#efb83b") finger(); drive();}   // Base 4: the drive's side gears carry the handles
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
// outline and holes extruded to the plate and cut by the flat-bottom taper, plus the handle plate as a plain box,
// with none of the rounding, grooves, feet, stop strip, strap boss or tail the solid adds. 3.3: no strap slots through the plate.
if(part=="concept") echo(concept=[pxs(outline_px),
    [for(h=holes_px) [px(h)[0],px(h)[1],hole_d(h)]],
    [px(dot_px)[0],px(dot_px)[1],dot_px[2]*mm_per_px*dot_scale],
    [for(i=[0:len(slots_px)-1]) [px(slots_px[i])[0],px(slots_px[i])[1],frame_deg(slot_angle_deg),(i==len(slots_px)-1?last_slot_scale:1)*slot[0],(i==len(slots_px)-1?last_slot_scale:1)*slot[1]]],
    pivot,angle,plate,tip_t,dot_z+taper_start,tip[1],taper_power,[rail_p[0][0],rail_p[0][1],rail_a],[slide_w0,slide_w1,slide_u[0],slide_u[1],slide_h],
    []]);   // slide is w0,w1,u0,u1,height in y

// ---------- 3.3: the drive, in the finger plane (3.1 voice-5b59d3bf, 3.2 voice-e3cd53d6, 3.3 voice-3b311f32) ----------
// Gripper frame as above: X across (right finger +X), Z along the fingers, +Y dorsal. Each side gear turns about its finger's
// pivot axis, Y through (+-pivot, 0, 0); the pinion about Y through pin_c, on the centreline below them. Every number is in params.scad.
// In 2D (x, z) plans an angle is measured from +x toward +z; a finger's swing a turns its gear by -a there.
gear_y1=gear_w/2; gear_y0=-gear_w/2;   // the teeth: centred on the finger's mid-plane
web_y1=-slide_h/2-fit;            // each gear's web, the floor the finger and handle sit fit above
web_y0=web_y1-web_t;
base_y1=web_y0-stack_gap;         // the base plate's top face
base_y0=base_y1-base_t;           // its underside: the motor's front face bolts up against it
flange_y=base_y0+motor_boss_h;    // the motor's output flange face, inside the plate's hole; the pinion's spigot bolts to it
gear_m=2*pivot/gear_teeth;        // module: the side gears' pitch radius = the pivot half-spacing, so they mesh on the centreline
function g_rp(n)=n*gear_m/2;
function g_rb(n)=g_rp(n)*cos(gear_pressure_deg);
function g_ra(n)=g_rp(n)+gear_m;
function g_rf(n)=g_rp(n)-1.25*gear_m;
gear_pitch=360/gear_teeth;
pin_rp=g_rp(pinion_teeth);
pin_theta=acos(pivot/(pivot+pin_rp));   // how far below the pivots' line the pinion meets the right gear, seen from its pivot (60 deg at 34 teeth)
pin_c=[0,-(pivot+pin_rp)*sin(pin_theta)];   // the pinion's axis (x, z): on the centreline
pin_ratio=gear_teeth/pinion_teeth;      // pinion turns per gear turn
// mesh phase: the right gear has a tooth centre every gear_pitch from 180 deg; where it meets the pinion (180 + pin_theta),
// the pinion needs a gap, so its teeth sit half a pitch from the right gear's there
pin_f=(pin_theta/gear_pitch)-floor(pin_theta/gear_pitch);
pin_phase=pin_theta+(pin_f-0.5)*360/pinion_teeth;
spigot_d=motor_boss_d-0.5;        // the pinion's spigot sits on the motor's output boss (35 mm), 0.5 under it so its rim never lies on the boss's
module slab(y0,h) {translate([0,y0+h/2,0]) xz(h) children();}   // a 2D (x, z) shape made solid from y0 to y0+h
module ring(n,pcd,phase=0) {for(i=[0:n-1]) rotate(phase+i*360/n) translate([pcd/2,0]) children();}   // 2D, about the origin
function inv_deg(a)=(tan(a)-a*PI/180)*180/PI;   // the involute function, in degrees
function flank(n,r)=90/n-gear_backlash/2/g_rp(n)*180/PI+inv_deg(gear_pressure_deg)-inv_deg(acos(min(1,g_rb(n)/r)));
module tooth2d(n) {   // one involute tooth of an n-tooth gear (module gear_m) centred on +x, from just inside the root circle to the tip circle
    k=10;r0=max(g_rb(n),g_rf(n));rr=[for(i=[0:k]) r0+(g_ra(n)-r0)*i/k];rin=g_rf(n)-0.5;
    polygon(concat([[rin*cos(-flank(n,r0)),rin*sin(-flank(n,r0))]],[for(r=rr) [r*cos(-flank(n,r)),r*sin(-flank(n,r))]],
        [for(i=[k:-1:0]) let(r=rr[i]) [r*cos(flank(n,r)),r*sin(flank(n,r))]],[[rin*cos(flank(n,r0)),rin*sin(flank(n,r0))]]));
}
module fan2d(a0,a1,r) {polygon(concat([[0,0]],[for(i=[0:24]) let(t=a0+(a1-a0)*i/24) r/cos((a1-a0)/48)*[cos(t),sin(t)]]));}
module gear2d(n,phase,s0=0,s1=360,root=true) {   // teeth centred every 360/n from phase, only those centred within s0..s1 (cut at the gaps either side); root=false: the teeth alone
    p=360/n;i0=ceil((s0-phase)/p);i1=floor((s1-phase)/p);
    intersection() {
        union() {if(root) circle(r=g_rf(n),$fn=96); for(i=[i0:i1]) rotate(phase+i*p) tooth2d(n);}
        if((i1-i0+1)*p<360) fan2d(phase+(i0-0.5)*p,phase+(i1+0.5)*p,g_ra(n)+2);
    }
}
// 3.3: each side gear carries teeth only where a mate meets it over the swing: the other side gear at 180 deg (both sides), and
// the pinion at 180 + pin_theta (the right only); turning by -a, the tooth that meets them at swing a sits a further round
function teeth_span(right)=[180-gear_extra*gear_pitch,180+(right?pin_theta:0)+max_angle+gear_extra*gear_pitch];
module hub2d() {intersection() {circle(r=hub_r,$fn=96); translate([-hub_r-1,-hub_r-1]) square([2*hub_r+2,hub_r+1+hub_top]);}}
module gear_solid(phase=0,right=true) {   // the gear without its handle, in its finger's frame (pivot at the origin), uncut:
    // teeth in the finger plane; inside them a solid fan and the hub; the web under them reaches in to the axle, which turns in the base
    s=teeth_span(right);
    slab(gear_y0,gear_w) gear2d(gear_teeth,180+phase,s[0],s[1],false);   // the teeth; the fan below is their root
    slab(web_y0,gear_y1-web_y0) {intersection() {fan2d(s[0]-gear_pitch/2,s[1]+gear_pitch/2,g_ra(gear_teeth)+2); circle(r=g_rf(gear_teeth),$fn=96);} hub2d();}
    slab(base_y0,web_y0-base_y0+0.01) circle(d=axle_d,$fn=64);
}
module finger_pocket() {slab(web_y1,gear_y1-web_y1+1) offset(r=fit) profile();}   // above the web, fit off the finger: the finger's seat
module gear_core(phase=0,right=true) {difference() {gear_solid(phase,right); finger_pocket();}}   // the gear without its handle (checks)
// Base 4: the side gear and its handle, ONE print (Base 3: a handle with a key in a separate gear's cradle). The handle's tail
// runs into the hub and the finger's pocket is cut through both at once. The left is gear(half a tooth,false) mirrored.
module gear(phase=0,right=true) {difference() {union() {gear_solid(phase,right); handle_body();} finger_pocket();}}
module pinion(a=angle,extra=0) {   // black: on the RS00's output flange, on the centreline; it turns pin_ratio times the right gear, the other way.
    // Base 4: bolted through motor_out_screws of the flange's holes (every other one), not all six
    translate([pin_c[0],0,pin_c[1]]) rotate([0,-(a*pin_ratio+extra),0]) difference() {
        union() {
            slab(gear_y0,gear_w) gear2d(pinion_teeth,pin_phase);
            slab(flange_y,gear_y0-flange_y+0.01) circle(d=spigot_d,$fn=96);
        }
        slab(flange_y-1,gear_y1-flange_y+2) ring(motor_out_screws,motor_out_pcd,gear_bolt_phase_deg) circle(d=screw_clear_d,$fn=16);
        slab(gear_y1-gear_bolt_head_h,gear_bolt_head_h+1) ring(motor_out_screws,motor_out_pcd,gear_bolt_phase_deg) circle(d=gear_bolt_head_d,$fn=24);
    }
}
module base2d() {hull() {for(s=[-1,1]) translate([s*pivot,0]) circle(r=bush_r,$fn=96); translate(pin_c) circle(r=base_r,$fn=96);}}
module base() {   // black: the plate under both gears and the pinion; the motor bolts up under its centre
    difference() {
        slab(base_y0,base_t) base2d();
        for(s=[-1,1]) slab(base_y0-1,base_t+2) translate([s*pivot,0]) circle(d=axle_d+2*base_clear,$fn=64);   // the two plain bushings
        slab(base_y0-1,base_t+2) translate(pin_c) {
            circle(d=motor_boss_d+2*base_clear,$fn=96);   // round the motor boss
            ring(motor_front_screws,motor_front_pcd,motor_front_phase_deg) circle(d=screw_clear_d,$fn=16);   // Base 4: every other hole
            ring(2,motor_front_pcd,motor_dowel_phase_deg) circle(d=motor_dowel_d+2*base_clear,$fn=16);
        }
        slab(base_y1-motor_screw_head_h,motor_screw_head_h+1) translate(pin_c) ring(motor_front_screws,motor_front_pcd,motor_front_phase_deg) circle(d=motor_screw_head_d,$fn=24);
    }
}
module motor(a=angle) {   // RobStride RS00, reference only (bought, not printed): body, output boss, its tapped and dowel holes
    translate([pin_c[0],0,pin_c[1]]) difference() {
        union() {
            slab(base_y0-motor_len,motor_len) circle(d=motor_d,$fn=96);
            slab(base_y0-0.01,motor_boss_h+0.01) circle(d=motor_boss_d,$fn=96);
        }
        rotate([0,-a*pin_ratio,0]) slab(flange_y-motor_out_depth,motor_out_depth+1) ring(motor_out_holes,motor_out_pcd,gear_bolt_phase_deg) circle(d=2.5,$fn=12);
        slab(base_y0-motor_front_depth,motor_front_depth+1) ring(motor_front_holes,motor_front_pcd,motor_front_phase_deg) circle(d=2.5,$fn=12);
        slab(base_y0-motor_dowel_depth,motor_dowel_depth+1) ring(2,motor_front_pcd,motor_dowel_phase_deg) circle(d=motor_dowel_d,$fn=12);
        slab(base_y0-motor_len-1,motor_back_depth+1) ring(motor_back_holes,motor_back_pcd,motor_back_phase_deg) circle(d=2.5,$fn=12);
    }
}
// The screw shanks and dowels the checks use, each only as long as the printed part it passes through (they must clear it)
module motor_cores(a=angle) {
    translate([pin_c[0],0,pin_c[1]]) {
        rotate([0,-a*pin_ratio,0]) slab(flange_y,gear_y1-flange_y) ring(motor_out_screws,motor_out_pcd,gear_bolt_phase_deg) circle(d=3,$fn=12);
        slab(base_y0,base_t) ring(motor_front_screws,motor_front_pcd,motor_front_phase_deg) circle(d=3,$fn=12);
        slab(base_y0,base_t) ring(2,motor_front_pcd,motor_dowel_phase_deg) circle(d=motor_dowel_d,$fn=12);
    }
}
module bolt_access(a=angle) {translate([pin_c[0],0,pin_c[1]]) rotate([0,-a*pin_ratio,0]) slab(gear_y1-gear_bolt_head_h,80) ring(motor_out_screws,motor_out_pcd,gear_bolt_phase_deg) circle(d=gear_bolt_head_d-0.2,$fn=24);}   // checks: the way in to the six flange bolts
// 3.3: the space the strap needs where it leaves the tunnel (right finger's frame): strap_clear past each face of the plate,
// over the tunnel's length and from the plate's outer face to the boss's, plus strap_clear round that. Nothing but the handle may enter it.
module strap_zone() {
    rail_frame() for(s=[-1,1]) translate([slide_w1-strap_clear,s>0?slide_h/2:-slide_h/2-strap_clear,slots_u-strap_clear])
        cube([boss_w1-slide_w1+2*strap_clear,strap_clear,strap_slot[0]+2*strap_clear]);
}
half_tooth=180/gear_teeth;
module left_gear() {mirror([1,0,0]) gear(half_tooth,false);}   // half a tooth out of phase, or the mirrored teeth would meet tip to tip
module gear_piece(q,a=angle,extra=0) {   // a side gear (Base 4: with its handle) where it sits at swing a; extra turns it on its axis (checks only)
    if(q=="right") placed(1,a) rotate([0,extra,0]) gear(0,true);
    if(q=="left") placed(-1,a) rotate([0,extra,0]) gear(half_tooth,false);
}
module core_piece(q,a=angle) {if(q=="right") placed(1,a) gear_core(0,true); if(q=="left") placed(-1,a) gear_core(half_tooth,false);}   // the gear without its handle (checks)
module zone_piece(q,a=angle) {if(q=="left") placed(-1,a) strap_zone(); if(q=="right") placed(1,a) strap_zone();}
module side(q,a=angle) {piece(q,a); gear_piece(q,a);}   // everything that swings with one finger (Base 4: finger + handle-gear)
module drive(a=angle) {
    for(q=["left","right"]) color(black) gear_piece(q,a);
    color(black) pinion(a); color(black) base(); color("#a3a8ad") motor(a);
}
assert(base_r>=motor_front_pcd/2+motor_screw_head_d/2+0.5,"base_r is too small for the motor's 50 mm screw ring");
assert(bush_r>=axle_d/2+base_clear+1.5,"bush_r leaves no wall round a gear bushing");
assert(axle_d/2+1<hub_r,"axle_d is wider than the gear hub");
assert(motor_out_holes%motor_out_screws==0,"motor_out_screws must divide motor_out_holes (the flange's holes)");
assert(motor_front_holes%motor_front_screws==0,"motor_front_screws must divide motor_front_holes (the front ring's holes)");
assert(hub_r<pivot-1,"hub_r: the two hubs would meet on the centreline");
assert(gear_y0>web_y0+0.5,"gear_w is too wide: the teeth run down past the web");
assert(motor_out_pcd/2+gear_bolt_head_d/2<g_rf(pinion_teeth)-1,"the motor bolt heads run into the pinion's tooth roots");
assert(motor_out_pcd/2+gear_bolt_head_d/2<spigot_d/2-0.5,"the motor bolt heads run off the pinion's spigot");
if(part=="drive") drive();
if(part=="gears") {color(black) for(q=["left","right"]) gear_piece(q); color(black) pinion();}
if(part=="inplane") {for(s=[-1,1]) placed(s) color("#efb83b") finger(); for(q=["left","right"]) color("#4a4c52") gear_piece(q); color("#6b6e75") pinion();}   // 3.3: the finger plane without base or motor
if(part=="cradle") {color("#efb83b") finger(); color("#4a4c52") gear();}   // the right finger seated in its handle-gear
if(part=="handle_gear") {color("#efb83b") translate([0,30,0]) finger(); color("#4a4c52") gear();}   // Base 4: the finger lifted 30 mm above its handle-gear, the way it drops in
if(part=="base") color(black) base();
if(part=="motor") color("#a3a8ad") motor(0);
if(part=="pinion") color(black) pinion(0);
if(part=="right_gear") color(black) gear();
if(part=="left_gear") color(black) left_gear();
if(part=="strap_zones") {for(s=[-1,1]) placed(s) {color("#efb83b") finger(); color("#ff3b30",0.4) strap_zone();} drive();}
if(part=="viewer_base") base();
if(part=="viewer_motor") motor();
if(part=="viewer_pinion") pinion();
for(q=["left","right"]) if(part==str("viewer_",q,"_gear")) gear_piece(q);
