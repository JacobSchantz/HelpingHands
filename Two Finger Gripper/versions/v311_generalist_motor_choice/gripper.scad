/* GENERALIST GRIPPER — BASE 9, TOP PLATE / gripper plus base, mm. Gripper 21; no separate Handle.
   Base 9 (voice-d96cd30d) is Base 8 with a top plate. Jake: "Add a piece on top so everything stays centered: a top plate similar
   to the bottom base piece, so the geared handle pieces are captured and supported from both sides (above and below), and their
   axles are held at both ends so they stay aligned. Keep it printable without supports, and keep the motor underneath." So:
     * TOP PLATE: a flat plate top_gap above the handle-gears, fingers and pinion, the base's outline (the hull round both pivots
       and the pinion) plus three pillars; it sits on the base on the pillars and 3 countersunk M3 come up through the base into
       them. Each pillar's foot drops into a socket in the base, so the plate is located on the base, not just screwed to it;
     * THE AXLE'S TOP END: the finger's base hook lies over the pivot (Gripper 21), so the post cannot run up through it. Instead
       each handle-gear's hub has a C-shaped groove round the pivot (ring_r), cut down from the top face wherever the finger is
       not, and the top plate carries a matching C-shaped rib that runs in it, shortened by the swing so it never reaches the
       ends. Below, the gear turns on the base's post; above, on the plate's rib: the same axis, held at both ends;
     * captured: the plate is top_gap over the fingers and handle-gears, so neither can lift off (Base 8: only gravity held them);
     * a hole over the pinion keeps its 3 flange screws reachable with the plate on;
     * prints top face down: plate, then the ribs and pillars straight up. Pieces: 7 printed + RS00 + 9 M3 = 17.
   Base 8's notes follow. */
/* GENERALIST GRIPPER — BASE 8, HANDLE-GEAR / gripper plus base, mm. Gripper 21; no separate Handle.
   Base 8 (voice-1f4d3de1) is Base 7 with the Handle part gone. Jake: "The base and handle are starting to become one piece; go
   further that way. The part that curls around should be one piece with the handle. Ditch the separate Handle part entirely: the
   geared pieces become the handles. Each finger's gear and handle (with its strap-loop slots) is a single printed part." So:
     * each side's HANDLE-GEAR is the handle: plate, both hooks' feet, the tail that curls round the base hook, hub, web and teeth,
       one print (as Base 7). It is named a handle-gear, and the live preview drops the Handle picker for a Base that carries one,
       so Base 8 never shows a second, separate handle beside it (Base 7 + Handle 7 did);
     * STRAP-LOOP SLOTS: strap_slots (2) slots side by side along the plate, strap_rib apart (slots_shift 3 toward the top hook, so
       the lower one's mouth clears the base plate), each a tunnel straight through the
       part under the strap boss (Base 7: one). Each is a 2D cut extruded the part's full height, so it prints as a vertical hole:
       no bridge, no support. One loop per slot wraps the boss and the digit on it, so the digit is held in two places;
     * Base 7's print rules, orientations and checks are unchanged. Pieces: 6 printed + RS00 + 6 M3 = 13.
   Base 7's notes follow. */
/* GENERALIST GRIPPER — BASE 7, PRINTABLE / gripper plus handles plus base, mm. Gripper 21, Handle 7.
   Base 7 (voice-fef42307) is Base 4 made printable. Jake: "copy Base 4 with Handle 7 and simplify significantly, with a focus on
   3D printability ... every piece should print on an FDM printer without supports: flat bases, overhangs at 45 deg or less, no
   floating features, sensible split lines, and a print orientation noted for each part." Base 5 and Base 6 are not built on.
   Rule: every printed part is a stack of straight extrusions along Y, each no wider than the one under it, so it prints flat
   on one face with every wall vertical (the fingers' dorsal taper and the screw cones are the only slopes, both <= 45 deg):
     * HANDLE-GEAR (Base 4's one print, kept): the handle plate, strap boss, tail, hub and teeth all run the full height, from
       the web's underside (the bed face) to the finger's top face, one 2D outline; the finger's pocket is cut from the top
       down to the web. Base 4's teeth started 2 mm above the web, the plate 3.2 mm above it and the axle hung under it:
       three floating starts. The handle is 15.2 mm edge-on (Handle 7: 12): the 3.2 mm under the finger is the web's height,
       the price of a flat bottom. The plate's ends are rounded in plan, not edge-on;
     * PIVOT POSTS on the base replace the axles: each handle-gear turns on a post through a bore in its web;
     * PINION: full-height teeth on a narrower spigot, printed teeth face down; its 3 M3 are countersunk, the head on a 45 deg
       cone (Base 4's flat counterbore floor hung in the air printed that way up);
     * BASE: a flat plate with the two posts on top; the 3 motor screws are the same M3 countersunk from the top.
   exports/print/*.stl lie on the bed in their print orientation (z up); check_geometry.py checks every one for overhangs
   past 45 deg and for anything not resting on the bed. Same pieces as Base 4: 6 printed + RS00 + 6 M3 = 13.
   Base 4's notes follow; its axle, bushings, counterbores and stepped gear no longer apply. */
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
web_y1=-plate/2-fit;            // each handle-gear's web, the floor the finger sits fit above
web_y0=web_y1-web_t;              // Base 7: its underside is the handle-gear's bed face; everything on the handle-gear starts here
top_y=plate/2+handle_over;        // and its top face (Handle 7: flush with the finger's dorsal face). The pinion's teeth match
slide_h=top_y-web_y0;             // Base 7: the handle's height in y, the web's underside to the top: 15.2 mm (Handle 7: 12)
slide_w1=slide_w0+slide_t;   // its outer face; under both prongs' curl (from w ~4.0)
slide_u=[hook_floor_u[0]-span_over,hook_floor_u[1]+span_over];   // 2.5: the plate's ends along u, past both notch floors
slide_len=slide_u[1]-slide_u[0];   // 67.4 mm at the defaults (2.5: 41.8, 2.4: 28)
slots_run=strap_slots*strap_slot[0]+(strap_slots-1)*strap_rib;   // Base 8: the strap-loop slots and the ribs between them, along u
slots_u=[for(i=[0:strap_slots-1]) slide_u[0]+slide_len/2-slots_run/2+slots_shift+i*(strap_slot[0]+strap_rib)];   // each slot's low-u end: centred on the plate, then slots_shift toward the top hook
boss_u=[slots_u[0]-slot_wall,slots_u[strap_slots-1]+strap_slot[0]+slot_wall];   // 3.3: the strap boss on the plate's outer face, along u
boss_w1=slide_w1+strap_slot[1]+slot_wall;   // and its outer face, where the digit lies
module rail_frame() {translate([rail_p[0][0],0,rail_p[0][1]]) rotate([0,rail_a,0]) children();}
module rail2d() {translate(rail_p[0]) rotate(-rail_a) children();}   // 3.3: a 2D (w, u) shape into the finger's 2D (x, z) plan
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
// Base 7: the handle as plan outlines (finger frame, 2D x, z), all extruded the handle's full height (slab(), below)
module plate2d() {rail2d() translate([slide_w0,slide_u[0]]) rounded(plate_corner_r) square([slide_t,slide_len]);}
module boss2d() {rail2d() rounded(slot_corner_r) translate([slide_w1-slide_t/2,boss_u[0]]) square([boss_w1-slide_w1+slide_t/2,boss_u[1]-boss_u[0]]);}   // from mid-plate, so its rounding stays inside
module tunnel2d() {for(u=slots_u) rail2d() rounded(slot_corner_r) translate([slide_w1,u]) square([strap_slot[1],strap_slot[0]]);}   // Base 8: one per strap-loop slot
module handle_body() {   // black, in the finger's frame: plate + strap boss and its strap-loop slots + tail (Base 4: no stop strip; the gear web stops the finger)
    difference() {
        slab(web_y0,slide_h) {plate2d(); boss2d(); tail2d();}
        slab(web_y0-1,slide_h+2) {tunnel2d(); offset(r=fit) profile();}   // the tunnel, y right through; the plate's feet fill both notches; the tail clears the hook
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
assert(slot_corner_r<strap_slot[1]/2,"slot_corner_r must be under half the strap tunnel gap");
assert(strap_slots==1||strap_slots==2,"strap_slots is 1 or 2");
assert(slots_run<slide_len-2,"the strap slots are longer than the plate (the top hook is too low for this strap)");
assert(boss_u[0]>tail_top_u+1&&boss_u[1]<hook_floor_u[1]-4,"the strap boss runs into a hook: shorten the strap or move the top hook");
assert(edge_round>0&&fillet_r>0&&tip_r>0,"rounding radii must be positive");
black="#26272b";
if(part=="assembly") {for(s=[-1,1]) placed(s) color("#efb83b") finger(); drive(); if(!sts) mount();}   // Base 11: the reBot wrist mount is the RS00's only   // Base 10: + the wrist mount   // Base 4: the drive's side gears carry the handles
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
gear_y0=web_y0; gear_y1=top_y;   // Base 7: the teeth run the full height, bed face to top (Base 4: gear_w 8, centred, 2 mm above the web)
base_y1=web_y0-stack_gap;         // the base plate's top face
base_y0=base_y1-base_t;           // its underside: the motor's front face bolts up against it
sts=motor_sts==1;                 // Base 11: which motor drives the pinion (0 RobStride RS00, 1 Feetech STS3215, the SO-101 servo)
flange_y=base_y0+(sts?sts_horn_top:motor_boss_h);    // the motor's output flange face (STS3215: its horn's top), inside the plate's hole; the pinion's spigot bolts to it
// Base 11: the pinion's screws, on whichever output it sits: the RS00's flange (motor_out_screws of its 6 M3 on 27) or the STS3215's horn (all 4 M3 on 14)
m_out_pcd=sts?sts_horn_pcd:motor_out_pcd; m_out_holes=sts?sts_horn_holes:motor_out_holes; m_out_screws=sts?sts_horn_holes:motor_out_screws;
post_y1=web_y1-fit;               // Base 7: the pivot posts' tops, fit under the finger
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
spigot_d=(sts?sts_horn_d:motor_boss_d)-0.5;        // the pinion's spigot sits on the motor's output boss (35 mm; STS3215: its 20 mm horn), 0.5 under it so its rim never lies on the boss's
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
    // Base 7: teeth, the solid fan inside them and the hub, one outline the full height (Base 4: teeth on a web on an axle)
    s=teeth_span(right);
    slab(gear_y0,gear_y1-gear_y0) {
        gear2d(gear_teeth,180+phase,s[0],s[1],false);   // the teeth; the fan below is their root
        intersection() {fan2d(s[0]-gear_pitch/2,s[1]+gear_pitch/2,g_ra(gear_teeth)+2); circle(r=g_rf(gear_teeth),$fn=96);}
        hub2d();
    }
}
module post_bore() {slab(web_y0-1,slide_h+2) circle(d=post_d+2*base_clear,$fn=64);}   // Base 7: the handle-gear turns on the base's post
module finger_pocket() {slab(web_y1,gear_y1-web_y1+1) offset(r=fit) profile();}   // above the web, fit off the finger: the finger's seat
module gear_core(phase=0,right=true) {difference() {gear_solid(phase,right); finger_pocket(); post_bore(); ring_groove();}}   // the gear without its handle (checks)
// Base 4: the side gear and its handle, ONE print (Base 3: a handle with a key in a separate gear's cradle). The handle's tail
// runs into the hub and the finger's pocket is cut through both at once. The left is gear(half a tooth,false) mirrored.
// Base 7: prints web face down; every outline runs from the bed to the top, and the pocket is cut down from the top.
module gear(phase=0,right=true) {difference() {union() {gear_solid(phase,right); handle_body();} finger_pocket(); post_bore(); ring_groove();}}   // Base 9: + the top ring's groove
// Base 7: a countersunk M3 hole in a face at y=y_face, going -y if down, else +y: the head's recess, a 45 deg cone, the shank
module csk(y_face,head_d,recess,down=true,len=40) {
    c=(head_d-screw_clear_d)/2; m=down?[0,0,0]:[0,1,0];
    translate([0,y_face,0]) mirror(m) {
        translate([0,0.01,0]) rotate([90,0,0]) cylinder(d=head_d,h=recess+0.01,$fn=24);   // y from just past the face down to -recess
        translate([0,-recess,0]) rotate([90,0,0]) cylinder(d1=head_d,d2=screw_clear_d,h=c,$fn=24);
        rotate([90,0,0]) cylinder(d=screw_clear_d,h=len,$fn=24);
    }
}
module ring3(n,pcd,phase=0) {for(i=[0:n-1]) rotate([0,-(phase+i*360/n),0]) translate([pcd/2,0,0]) children();}   // 3D ring about Y, angles as ring() (2D x, z)
module pinion(a=angle,extra=0) {   // black: on the RS00's output flange (Base 11: or the STS3215's horn), on the centreline; it turns pin_ratio times the right gear, the other way.
    // Base 4: bolted through motor_out_screws of the flange's holes (every other one), not all six.
    // Base 7: full-height teeth (the handle-gears' height) on the spigot; prints teeth face down; countersunk M3 from the top
    translate([pin_c[0],0,pin_c[1]]) rotate([0,-(a*pin_ratio+extra),0]) difference() {
        union() {
            slab(gear_y0,gear_y1-gear_y0) gear2d(pinion_teeth,pin_phase);
            slab(flange_y,gear_y0-flange_y+0.01) circle(d=spigot_d,$fn=96);
        }
        ring3(m_out_screws,m_out_pcd,gear_bolt_phase_deg) csk(gear_y1,gear_bolt_head_d,gear_bolt_head_h);
        if(sts) slab(flange_y-1,sts_horn_screw_head_h+1.3) circle(d=sts_horn_screw_head_d,$fn=32);   // Base 11: over the horn's centre M3 head
    }
}
module base2d() {hull() {for(s=[-1,1]) translate([s*pivot,0]) circle(r=bush_r,$fn=96); translate(pin_c) circle(r=base_r,$fn=96);}}
module base_outline() {hull() {base2d(); pillars2d([0,1]); if(sts) sts_holes2d() circle(d=sts_screw_head_d+3,$fn=32);} hull() {circle(d=pillar_d+2*pillar_rim,$fn=48); pillars2d([2]);}}   // Base 9: + round the top plate's pillars (as top2d); Base 11: + round the STS3215's 4 case screws
module base() {   // black: the plate under both gears and the pinion; the motor bolts up under its centre.
    // Base 7: a pivot post stands up at each pivot (Base 4: bushings for the gears' axles); prints underside down, posts up
    difference() {
        union() {
            slab(base_y0,base_t) base_outline();
            for(s=[-1,1]) translate([s*pivot,0,0]) slab(base_y1-0.01,post_y1-base_y1+0.01) circle(d=post_d,$fn=64);
        }
        if(sts) sts_seat(); else {
        slab(base_y0-1,base_t+2) translate(pin_c) {
            circle(d=motor_boss_d+2*base_clear,$fn=96);   // round the motor boss
            ring(2,motor_front_pcd,motor_dowel_phase_deg) circle(d=motor_dowel_d+2*base_clear,$fn=16);
        }
        translate([pin_c[0],0,pin_c[1]]) ring3(motor_front_screws,motor_front_pcd,motor_front_phase_deg) csk(base_y1,motor_screw_head_d,motor_screw_head_h,len=base_t+2);   // Base 4: every other hole
        }
        for(c=pillar_c) {   // Base 9: a socket for each top-plate pillar's foot, and its M3 countersunk from the underside
            slab(base_y1-pillar_socket,pillar_socket+1) translate(c) circle(d=pillar_d+2*pillar_fit,$fn=48);
            translate([c[0],0,c[1]]) csk(base_y0,motor_screw_head_d,0,down=false,len=base_t+2);
        }
    }
}
module motor(a=angle) {if(sts) sts3215(a); else rs00(a);}   // Base 11: the chosen motor
module rs00(a=angle) {   // RobStride RS00, reference only (bought, not printed): body, output boss, its tapped and dowel holes
    translate([pin_c[0],0,pin_c[1]]) difference() {
        union() {
            slab(base_y0-motor_len,motor_len) circle(d=motor_d,$fn=96);
            slab(base_y0-0.01,motor_boss_h+0.01) circle(d=motor_boss_d,$fn=96);
        }
        rotate([0,-a*pin_ratio,0]) slab(flange_y-motor_out_depth,motor_out_depth+1) ring(motor_out_holes,motor_out_pcd,gear_bolt_phase_deg) circle(d=2.5,$fn=12);   // rs00() only
        slab(base_y0-motor_front_depth,motor_front_depth+1) ring(motor_front_holes,motor_front_pcd,motor_front_phase_deg) circle(d=2.5,$fn=12);
        slab(base_y0-motor_dowel_depth,motor_dowel_depth+1) ring(2,motor_front_pcd,motor_dowel_phase_deg) circle(d=motor_dowel_d,$fn=12);
        slab(base_y0-motor_len-1,motor_back_depth+1) ring(motor_back_holes,motor_back_pcd,motor_back_phase_deg) circle(d=2.5,$fn=12);
    }
    translate([pin_c[0],0,pin_c[1]]) motor_connectors();
}
module motor_connectors() {   // Base 10: the two cable connectors at the back end, side-opposite (Seeed's motor_7 mesh), about the motor axis
    slab(base_y0-motor_len,motor_conn_len) for(s=[-1,1]) rotate(motor_conn_deg+(s<0?180:0))
        translate([(motor_d/2-1+motor_conn_r)/2,0]) square([motor_conn_r-motor_d/2+1,motor_conn_w],center=true);
}
// The screw shanks and dowels the checks use, each only as long as the printed part it passes through (they must clear it)
module motor_cores(a=angle) {
    translate([pin_c[0],0,pin_c[1]]) rotate([0,-a*pin_ratio,0]) slab(flange_y,gear_y1-flange_y) ring(m_out_screws,m_out_pcd,gear_bolt_phase_deg) circle(d=3,$fn=12);
    if(sts) slab(base_y0,base_t) sts_holes2d() circle(d=2,$fn=12);   // Base 11: the 4 M2 case screws
    else translate([pin_c[0],0,pin_c[1]]) {
        slab(base_y0,base_t) ring(motor_front_screws,motor_front_pcd,motor_front_phase_deg) circle(d=3,$fn=12);
        slab(base_y0,base_t) ring(2,motor_front_pcd,motor_dowel_phase_deg) circle(d=motor_dowel_d,$fn=12);
    }
}
module bolt_access(a=angle) {translate([pin_c[0],0,pin_c[1]]) rotate([0,-a*pin_ratio,0]) slab(gear_y1-gear_bolt_head_h,80) ring(m_out_screws,m_out_pcd,gear_bolt_phase_deg) circle(d=gear_bolt_head_d-0.4,$fn=24);}   // checks: the way in to the six flange bolts
// ---------- Base 11: the Feetech STS3215 (the SO-101 servo) in place of the RS00 (motor_sts 1) ----------
// Measured from The Robot Studio's SO-ARM100 CAD (STEP/SO100/STS3215_03a.step, Apache-2.0). In the servo's own plan frame
// (u, w): u from the output axis along the body toward its far end, w across it; sts_body_deg turns that frame in the finger plane
// about the pinion's axis. Its front face is two rails (the four M2 case holes are in them, SO-101: M2x6) either side of a label
// hump; the output end sits sts_face_drop lower. The base bears on the rails (its underside is the rails' plane, base_y0), the hump
// stands up into a window cut straight through the base (so the underside stays flat on the bed: no bridge), and the round
// horn turns inside the base's centre hole with the pinion's spigot on top of it (4 M3 into the horn, as the SO-101 fixes its links).
sts_far=sts_len-sts_near;          // the axis to the far end
module sts_frame2d() {translate(pin_c) rotate(sts_body_deg) children();}   // 2D, (u, w) -> (x, z)
module sts_holes2d() {sts_frame2d() for(u=[sts_screw_u0,sts_screw_u1],s=[-1,1]) translate([u,s*sts_screw_w/2]) children();}
module sts_box2d(u0,u1,w0,w1) {sts_frame2d() translate([u0,w0]) square([u1-u0,w1-w0]);}
module sts_seat() {   // what the base loses to the servo: the horn's hole, the hump's window, the 4 M2 holes with their head recesses
    slab(base_y0-1,base_t+2) {
        translate(pin_c) circle(d=sts_horn_d+2*base_clear,$fn=96);
        sts_box2d(sts_hump_u-base_clear,sts_far+5,-sts_hump_w/2-base_clear,sts_hump_w/2+base_clear);
        sts_holes2d() circle(d=sts_screw_d,$fn=16);
    }
    slab(base_y1-sts_screw_head_h,sts_screw_head_h+1) sts_holes2d() circle(d=sts_screw_head_d,$fn=24);
}
module sts3215(a=angle) {   // reference only (bought, not printed): the case, rails, hump, horns, connector block; the horn turns with the pinion
    difference() {
        union() {
            slab(base_y0-sts_depth,sts_depth-sts_face_drop) sts_box2d(-sts_near,sts_far,-sts_w/2,sts_w/2);
            slab(base_y0-sts_face_drop-1,sts_face_drop+1) difference() {sts_box2d(sts_rail_u,sts_far-0.01,-sts_w/2+0.01,sts_w/2-0.01); sts_box2d(sts_rail_u-1,sts_hump_u,-sts_hump_w/2,sts_hump_w/2);}   // the rails, and the hump up to their plane (0.01 in from the case's sides: a clipped 2D outline lands a hair off them)
            slab(base_y0-1,sts_hump_h+1) sts_hump2d();
            slab(base_y0-sts_face_drop-0.01,sts_face_drop+sts_horn_y0+0.02) translate(pin_c) circle(d=sts_boss_d,$fn=48);
            translate([pin_c[0],0,pin_c[1]]) rotate([0,-a*pin_ratio,0]) slab(base_y0+sts_horn_y0,sts_horn_top-sts_horn_y0) circle(d=sts_horn_d,$fn=96);
            slab(base_y0-sts_depth-sts_idler_h,sts_idler_h+0.01) translate(pin_c) circle(d=sts_idler_d,$fn=96);
        }
        slab(base_y0-4,4+sts_hump_h+1) sts_holes2d() circle(d=1.5,$fn=12);   // the M2 holes in the case
        translate([pin_c[0],0,pin_c[1]]) rotate([0,-a*pin_ratio,0]) slab(flange_y-4,5) ring(sts_horn_holes,sts_horn_pcd,gear_bolt_phase_deg) circle(d=2.5,$fn=12);
    }
    sts_connectors();
    translate([pin_c[0],0,pin_c[1]]) slab(flange_y-0.01,sts_horn_screw_head_h+0.01) circle(d=5.5,$fn=24);   // the horn's centre M3 head
}
module sts_hump2d() {difference() {sts_box2d(sts_hump_u,sts_far-0.01,-sts_hump_w/2,sts_hump_w/2); translate(pin_c) circle(d=sts_horn_d+1,$fn=96);}}   // the STEP's hump reaches 1.1 mm under the horn's rim; cut round it here
module sts_connectors() {slab(base_y0-sts_depth-sts_conn_h,sts_conn_h+0.01) sts_box2d(sts_conn_u0,sts_conn_u1,-sts_conn_w/2,sts_conn_w/2);}
module sts_cable() {slab(base_y0-sts_depth-sts_conn_h-sts_plug_len,sts_plug_len) sts_box2d(sts_conn_u0-2,sts_conn_u1+2,-sts_conn_w/2-2,sts_conn_w/2+2);}   // checks: the plugs and the cable's bend behind them
// 3.3: the space the strap needs where it leaves the tunnel (right finger's frame): strap_clear past each face of the plate,
// over the tunnel's length and from the plate's outer face to the boss's, plus strap_clear round that. Nothing but the handle may enter it.
module strap_zone() {
    rail_frame() for(s=[-1,1],u=slots_u) translate([slide_w1-strap_clear,s>0?top_y:web_y0-strap_clear,u-strap_clear])
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
// ---------- Base 9: the top plate ----------
top_y0=top_y+top_gap;             // the plate's underside, top_gap over the handle-gears, fingers and pinion
top_y1=top_y0+top_t;              // its top face (the bed face when printed)
pillar_c=concat([for(s=[-1,1]) pin_c+pillar_pin_r*[s*sin(pillar_deg),-cos(pillar_deg)]],[[0,pillar_top_z]]);   // two below the pinion, one above the gears' mesh
access_d=m_out_pcd+gear_bolt_head_d+2*top_access_clear;   // the hole over the pinion: its 3 flange screws stay reachable
module annulus(r0,r1) {difference() {circle(r=r1,$fn=96); circle(r=r0,$fn=96);}}
// in each handle-gear's frame (pivot at the origin): the groove is the hub's ring band wherever the finger (plus ring_wall) is not;
// the rib is the band ring_clear narrower each side, and only where the groove is at every swing 0..max_angle, ring_clear short of its ends
module groove2d() {difference() {annulus(ring_r-ring_w/2,ring_r+ring_w/2); offset(r=ring_wall) profile();}}
module rib2d() {   // the right side's rib, world frame at the right pivot; the gear turns by -a in the plan, so the groove does too
    intersection() {
        annulus(ring_r-ring_w/2+ring_clear,ring_r+ring_w/2-ring_clear);
        intersection_for(a=[0:max_angle]) rotate(-a) difference() {circle(r=ring_r+ring_w,$fn=96); offset(r=ring_wall+ring_clear) profile();}
    }
}
module ring_groove() {slab(top_y-ring_depth,ring_depth+1) groove2d();}   // cut down into the handle-gear's top face
module pillars2d(k=[0,1,2]) {for(i=k) translate(pillar_c[i]) circle(d=pillar_d+2*pillar_rim,$fn=48);}
// the plate: a hull round both pivots (top_bush_r: under the base's bush_r, or its corners reach the lower strap slots' keep-out),
// the pinion and the lower pillars, plus a strip up the centreline to the upper pillar (a hull to it would cut across the slots too)
module top2d() {
    hull() {for(s=[-1,1]) translate([s*pivot,0]) circle(r=top_bush_r,$fn=96); translate(pin_c) circle(r=base_r,$fn=96); pillars2d([0,1]);}
    hull() {translate([0,0]) circle(d=pillar_d+2*pillar_rim,$fn=48); pillars2d([2]);}
}
module top_plate() {   // black: over everything that turns; prints top face down, the ribs and pillars standing up
    difference() {
        union() {
            slab(top_y0,top_t) top2d();
            for(s=[-1,1]) translate([s*pivot,0,0]) mirror([s<0?1:0,0,0]) slab(top_y-ring_depth+ring_clear,top_y0-(top_y-ring_depth+ring_clear)+0.01) rib2d();
            for(c=pillar_c) slab(base_y1-pillar_socket,top_y0-base_y1+pillar_socket+0.01) translate(c) circle(d=pillar_d,$fn=48);
        }
        slab(top_y0-1,top_t+2) translate(pin_c) circle(d=access_d,$fn=96);
        for(c=pillar_c) slab(base_y1-pillar_socket-1,top_y1-base_y1+pillar_socket) translate(c) circle(d=pillar_pilot_d,$fn=16);   // the M3 from below cuts its own thread; blind under the top face
    }
}
// ---------- Base 10: the reBot Arm B601-RS wrist mount (voice-3cd78d20) ----------
// Seeed's stock gripper hangs on J6 (an RS00, the same motor as ours) through two CNC parts: Connector A, a 35.6 disc bolted
// to J6's output, and Connector B, a cup bolted to the gripper motor's back face (4 M3 on 38 at 45 deg) that slips over A and
// is held by 3 radial M3 (reBot-DevArm Metal_Parts/2-M6-ROTOR.step, 2-M7-STATOR.step; cad/arm/rebot_b601_rs/). Base 10 keeps
// that interface: the HUB (A's printed twin) stays on the arm, and every tool carries a TOOL PLATE (B's twin). The Aero Hand's
// wrist pad has the same 4 M3 on 38 at 45 deg, so its plate is a tool plate plus a cable spacer; our gripper's motor axis
// runs across the fingers, so its tool plate screws to an L-shaped WRIST BRACKET whose leg bolts to the motor's back face and
// whose foot lies across the J6 axis, the fingers pointing straight out along it. Tool change: 3 radial screws.
// Frame as above (X across, Z along the fingers, +Y dorsal); the J6 axis runs along Z through (0, mount_axis_y).
back_y=base_y0-motor_len;   // the motor's back face
low_z=min(concat([pin_c[1]-max(base_r,motor_d/2,g_ra(pinion_teeth))],[for(c=pillar_c) c[1]-pillar_d/2-pillar_rim]));   // the gripper's lowest point
foot_z1=low_z-mount_gap;          // the bracket foot's top face
tool_z=foot_z1-foot_t;            // its underside = the tool plate's tool face
hub_z0=tool_z-tool_floor-hub_t;   // the hub's arm face = the top of J6's output boss (link6's origin in Seeed's URDF)
axis_c=[0,mount_axis_y];          // the J6 axis in plan (x, y)
back_holes=[for(i=[0:motor_back_holes-1]) let(t=motor_back_phase_deg+i*360/motor_back_holes) pin_c+motor_back_pcd/2*[cos(t),sin(t)]];   // (x, z)
leg_half=max([for(p=back_holes) abs(p[0])])+leg_boss_r;
module teardrop2d(d) {hull() {circle(d=d,$fn=24); polygon([[0,-d/2/sqrt(2)],[d/2*sqrt(2),0],[0,d/2/sqrt(2)]]);}}   // its point toward +x, 45 deg flanks, sharp
// a horizontal hole along the plan angle t from radius r0 to r1 at height z; its teardrop point up (+z) when up>0, else down
module radial_hole(t,z,r0,r1,d,up) {rotate([0,0,t]) translate([r0,0,z]) rotate([0,90,0]) linear_extrude(r1-r0) rotate(up>0?180:0) teardrop2d(d);}
module hub() {   // printed twin of Connector A, in its own frame: arm face at z 0 on J6's boss; prints that face down
    difference() {
        cylinder(d=hub_d,h=hub_t,$fn=96);
        if(hub_bore_d>0) translate([0,0,-1]) cylinder(d=hub_bore_d,h=hub_t+2,$fn=48);
        for(i=[0:hub_screws-1]) rotate(hub_screw_phase_deg+i*360/hub_screws) translate([motor_out_pcd/2,0,0]) {
            translate([0,0,-1]) cylinder(d=screw_clear_d,h=hub_t+2,$fn=24);
            translate([0,0,hub_t-hub_cbore_h]) cylinder(d=hub_cbore_d,h=hub_cbore_h+1,$fn=24);   // heads sink into the tool face
        }
        for(i=[0:radial_n-1]) let(t=radial_phase_deg+i*360/radial_n) {
            if(hub_relief_d>0) rotate(t) translate([hub_relief_pcd/2,0,-1]) cylinder(d=hub_relief_d,h=hub_t+2,$fn=24);   // A's reliefs, on the radial screws' line
            radial_hole(t,hub_t-radial_h,hub_d/2-radial_pilot_len,hub_d/2+1,radial_pilot_d,1);
        }
        for(i=[0:3]) rotate(tool_screw_phase_deg+i*90) translate([tool_screw_pcd/2,0,-1]) cylinder(d=hub_scallop_d,h=hub_t+2,$fn=32);
    }
}
// the tool plate, in its own frame: the floor's tool face at z 0, the socket below it (open at -tool_t), and spacer (Aero) above
module tool_plate(spacer=0,channel=false) {
    difference() {
        translate([0,0,-tool_t]) cylinder(d=tool_d,h=tool_t+spacer,$fn=96);
        translate([0,0,-tool_t-1]) cylinder(d=tool_bore_d,h=tool_t-tool_floor+1,$fn=96);   // the socket for the hub
        if(tool_center_d>0) translate([0,0,-tool_t-1]) cylinder(d=tool_center_d,h=tool_t+spacer+2,$fn=64);
        for(i=[0:3]) rotate(tool_screw_phase_deg+i*90) translate([tool_screw_pcd/2,0,0]) {
            translate([0,0,-tool_t-1]) cylinder(d=screw_clear_d,h=tool_t+spacer+2,$fn=24);
            translate([0,0,-tool_t-1]) cylinder(d=tool_head_d,h=tool_t-tool_floor+1,$fn=24);   // the head pocket, floor to mouth
        }
        for(i=[0:radial_n-1]) let(t=radial_phase_deg+i*360/radial_n,z=-tool_floor-radial_h) {
            radial_hole(t,z,tool_bore_d/2-1,radial_seat_r+0.01,radial_clear_d,-1);
            radial_hole(t,z,radial_seat_r,tool_d/2+1,radial_head_d,-1);
        }
        if(channel) rotate(aero_channel_deg) translate([0,0,spacer]) rotate([0,90,0]) linear_extrude(tool_d/2+1)   // 2D x = -z here
            polygon([[-0.01,-aero_channel_w/2],[aero_channel_h,-aero_channel_w/2],[aero_channel_h+aero_channel_w/2,0],[aero_channel_h,aero_channel_w/2],[-0.01,aero_channel_w/2]]);
    }
}
module aero_plate() {tool_plate(aero_spacer,true);}   // the Aero Hand's: its hand face at z aero_spacer
module foot2d() {
    hull() {
        translate(axis_c) circle(d=tool_d,$fn=96);
        translate([-leg_half-1,back_y-leg_t-gusset_len]) square([2*leg_half+2,leg_t+gusset_len]);   // 1 mm wider than the leg, so their sides never coincide
        translate([tie_x,back_y+tie_dy]) circle(r=tie_gap/2+tie_slot_t/2+2.5,$fn=32);
    }
}
module leg2d() {hull() {for(p=back_holes) translate(p) circle(r=leg_boss_r,$fn=48); translate([-leg_half,tool_z]) square([2*leg_half,foot_t]);}}   // (x, z)
module bracket() {   // black, in the gripper frame; prints foot down, the leg and gussets standing up
    difference() {
        union() {
            translate([0,0,tool_z]) linear_extrude(foot_t) foot2d();
            slab(back_y-leg_t,leg_t) leg2d();
            if(gusset_len>0) for(s=[-1,1]) translate([s*(leg_half-gusset_t/2-0.05)-gusset_t/2,0,0]) rotate([90,0,90]) linear_extrude(gusset_t)
                polygon([[back_y-leg_t+0.01,foot_z1-0.01],[back_y-leg_t-gusset_len,foot_z1-0.01],[back_y-leg_t+0.01,foot_z1+gusset_len]]);   // (y, z)
        }
        translate([axis_c[0],axis_c[1],tool_z-1]) for(i=[0:3]) rotate(tool_screw_phase_deg+i*90) translate([tool_screw_pcd/2,0,0]) cylinder(d=foot_pilot_d,h=foot_t+2,$fn=16);
        slab(back_y-leg_t-1,leg_t+2) for(p=back_holes) translate(p) rotate(90) teardrop2d(screw_clear_d);   // horizontal when printed: point up
        translate([tie_x,back_y+tie_dy,tool_z-1]) for(s=[-1,1]) translate([0,s*tie_gap/2,0]) linear_extrude(foot_t+2) square([tie_w,tie_slot_t],center=true);
    }
}
module leg_heads() {slab(back_y-leg_t-30,30) for(p=back_holes) translate(p) circle(d=5.8,$fn=24);}   // checks: the leg screws' heads and the hex key's way in
module mount_hub() {translate([axis_c[0],axis_c[1],hub_z0]) hub();}
module mount_tool_plate() {translate([axis_c[0],axis_c[1],tool_z]) tool_plate();}
module mount() {color(black) bracket(); color("#3a3b40") mount_tool_plate(); color("#a3a8ad") mount_hub();}
aero_mesh="../../../third_party/aero_hand/guide/anim41/left_base_link.STL";   // the left Aero Hand's palm (wrist pad at z 0, in m)
module aero_hand() {translate([aero_view_x,0,tool_z+aero_spacer]) scale(1000) import(aero_mesh);}
module aero_station() {translate([aero_view_x,0,tool_z]) aero_plate();}
assert(motor_out_holes%hub_screws==0,"hub_screws must divide motor_out_holes (J6's output flange holes)");
assert(tool_bore_d>hub_d,"tool_bore_d: the hub does not fit the socket");
assert(tool_t-tool_floor>=hub_t,"tool_t: the socket is shallower than the hub is thick");
assert(radial_h<hub_t-radial_pilot_d/2-0.5&&radial_h>radial_pilot_d/2+0.5,"radial_h: the radial screws miss the hub's rim");
assert(radial_seat_r>tool_bore_d/2+1&&radial_seat_r<tool_d/2-1,"radial_seat_r must lie in the tool plate's wall");
assert(tool_screw_pcd/2+tool_head_d/2<tool_d/2-1,"tool_screw_pcd: the head pockets run off the tool plate");
assert(tool_screw_pcd/2-hub_scallop_d/2<hub_d/2,"hub_scallop_d: the scallops miss the hub's edge");
assert(aero_spacer-aero_channel_h-aero_channel_w/2>-tool_floor+1,"the Aero cable channel cuts through the floor: lower aero_channel_h or aero_channel_w, or raise aero_spacer");
assert(foot_z1+gusset_len<min([for(p=back_holes) p[1]])-2.9,"gusset_len: the gussets reach the lower leg screws' heads");
module drive(a=angle) {
    for(q=["left","right"]) color(black) gear_piece(q,a);
    color(black) pinion(a); color(black) base(); color("#a3a8ad") motor(a); color(black) top_plate();
}
assert(ring_r-ring_w/2>post_d/2+base_clear+1,"ring_r: the top ring's groove runs into the post bore");
assert(ring_r+ring_w/2<hub_r-1,"ring_r: the top ring's groove runs off the hub");
assert(ring_r+ring_w/2-ring_clear<top_bush_r-0.5,"top_bush_r: the top ring runs off the top plate");
assert(ring_depth<slide_h-web_t-1,"ring_depth: the groove is deeper than the hub above the web");
assert(pillar_pilot_d<pillar_d-2,"pillar_pilot_d: the pillar wall is too thin");
assert(sts||base_r>=motor_front_pcd/2+motor_screw_head_d/2+0.5,"base_r is too small for the motor's 50 mm screw ring");
assert(bush_r>=post_d/2,"bush_r is smaller than the pivot post");
assert(post_d/2+base_clear+1<hub_r,"post_d is wider than the gear hub");
assert(plate_corner_r<slide_t/2,"plate_corner_r must be under half the plate's thickness (slide_t)");
assert(m_out_holes%m_out_screws==0,"motor_out_screws must divide motor_out_holes (the flange's holes)");
assert(motor_front_holes%motor_front_screws==0,"motor_front_screws must divide motor_front_holes (the front ring's holes)");
assert(hub_r<pivot-1,"hub_r: the two hubs would meet on the centreline");
assert(m_out_pcd/2+gear_bolt_head_d/2<g_rf(pinion_teeth)-1,"the motor bolt heads run into the pinion's tooth roots");
assert(gear_bolt_head_h+(gear_bolt_head_d-screw_clear_d)/2<gear_y1-flange_y-2,"the pinion's screw recess is deeper than the pinion");
// Base 11: only what of the screw reaches the spigot must fit it: the head's recess and cone if they get that far down, else the shank
assert(m_out_pcd/2+(gear_y1-gear_bolt_head_h-(gear_bolt_head_d-screw_clear_d)/2>gear_y0?screw_clear_d:gear_bolt_head_d)/2<spigot_d/2-0.5,"the motor bolt heads run off the pinion's spigot");
assert(!sts||sts_horn_pcd/2+screw_clear_d/2<sts_horn_screw_head_d/2+0.5||sts_horn_pcd/2-screw_clear_d/2>sts_horn_screw_head_d/2+0.5,"sts_horn_screw_head_d: the centre screw's recess runs into the horn screws");
assert(!sts||norm([sts_screw_u0,sts_screw_w/2])-sts_screw_head_d/2>sts_horn_d/2+base_clear+0.5,"sts_screw_u0: the near M2 heads run into the horn's hole");
assert(!sts||sts_screw_w/2-sts_screw_head_d/2>sts_hump_w/2+base_clear+0.5,"sts_screw_w: the M2 heads run into the hump's window");
assert(!sts||sts_horn_top<base_t-1,"sts_horn_top: the horn stands above the base");
assert(!sts||sts_hump_h<base_t,"sts_hump_h: the hump stands out of the base");
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
if(part=="viewer_top_plate") top_plate();
if(part=="top_plate") color(black) top_plate();
if(part=="top_ring") translate([-pivot,0,0]) {placed(1) color("#efb83b") finger(); gear_piece("right"); color("#ff3b30") intersection() {top_plate(); translate([pivot,0,0]) slab(top_y-ring_depth,ring_depth) circle(r=hub_r);}}
if(part=="viewer_pinion") pinion();
for(q=["left","right"]) if(part==str("viewer_",q,"_gear")) gear_piece(q);
// Base 10: the wrist mount's parts
if(part=="mount") mount();
if(part=="viewer_bracket") bracket();
if(part=="viewer_tool_plate") mount_tool_plate();
if(part=="viewer_hub") mount_hub();
if(part=="viewer_aero_plate") aero_station();
if(part=="viewer_aero_hand") aero_hand();
if(part=="aero_station") {color("#3a3b40") aero_station(); color("#d9dce1") aero_hand();}
// the whole picture (preview only: Seeed's meshes are not closed solids): the arm as export_models.py posed it, the gripper on it, the Aero Hand beside
arm_colors=[["anodized_silver","#b8c2ba"],["motor_black","#2b2f2e"],["base_black","#1d2120"],["pla_black","#2f3533"],["seeed_green","#b9d51e"],["wordmark_black","#111311"]];
if(part=="arm_view") {
    for(c=arm_colors) color(c[1]) import(str("exports/parts/arm_",c[0],".stl"));
    for(s=[-1,1]) placed(s) color("#efb83b") finger(); drive(); mount();
    color("#3a3b40") aero_station(); color("#d9dce1") aero_hand();
}
if(part=="tool_plate") color("#3a3b40") tool_plate();
if(part=="aero_plate") color("#3a3b40") aero_plate();
if(part=="hub") color("#a3a8ad") hub();
if(part=="bracket") color(black) bracket();
if(part=="servo_seat") {color(black) base(); color("#a3a8ad",0.5) translate([0,-0.2,0]) motor(0);}   // Base 11: the base from below, the servo's outline under it
if(part=="viewer_right") echo(arm_flange=[axis_c[0],axis_c[1],hub_z0]);   // export_models.py places the arm here
// Base 7: each printed part as it lies on the bed, z up (exports/print/*.stl; check_geometry.py checks them for overhangs)
module bed_up(y0) {translate([0,0,-y0]) rotate([90,0,0]) children();}     // the face at y=y0 on the bed, building +y
module bed_down(y1) {translate([0,0,y1]) rotate([-90,0,0]) children();}   // the face at y=y1 on the bed, building -y
module print_part(k) {
    if(k=="right") bed_up(-plate/2) finger();                  // fingers: flat ventral face down, the taper on top
    if(k=="left") bed_up(-plate/2) mirror([1,0,0]) finger();
    if(k=="right_gear") bed_up(web_y0) gear();                 // handle-gears: web face down, the finger pocket open on top
    if(k=="left_gear") bed_up(web_y0) left_gear();
    if(k=="pinion") bed_down(gear_y1) pinion(0);              // pinion: teeth face down, the spigot on top, screw cones opening at the bed
    if(k=="base") bed_up(base_y0) base();                      // base: underside down, the posts up
    if(k=="top_plate") bed_down(top_y1) top_plate();           // Base 9: top face down, the ribs and pillars up
    if(k=="bracket") translate([0,0,-tool_z]) bracket();        // Base 10: foot down, leg and gussets up
    if(k=="tool_plate") rotate([180,0,0]) tool_plate();         // tool face down, the socket open on top (print one per tool)
    if(k=="aero_plate") rotate([180,0,0]) translate([0,0,-aero_spacer]) aero_plate();   // hand face down, the socket on top
    if(k=="hub") hub();                                          // arm face down
    if(k=="motor") motor(0);                                    // not printed: the reference model as before
}
for(k=["right","left","right_gear","left_gear","pinion","base","top_plate","bracket","tool_plate","aero_plate","hub","motor"]) if(part==str("print_",k)) print_part(k);
// the printed parts on one bed (Base 10: + bracket, tool plate, Aero plate, hub) (previews/print_bed.png)
if(part=="print_bed") {
    color("#efb83b") {translate([-140,0,0]) print_part("left"); translate([-80,0,0]) print_part("right");}
    color("#4a4c52") {translate([0,0,0]) print_part("left_gear"); translate([62,0,0]) print_part("right_gear");
                      translate([125,52,0]) print_part("pinion"); translate([125,-112,0]) print_part("base"); translate([250,-60,0]) print_part("top_plate");
                      if(!sts) {translate([400,40,0]) print_part("bracket"); translate([400,-110,0]) print_part("tool_plate"); translate([480,-110,0]) print_part("aero_plate"); translate([480,-40,0]) print_part("hub");}}   // Base 11: the mount parts with the RS00 only
}
if(part=="print_pinion_flipped") bed_up(flange_y) pinion(0);         // checks only: the wrong way up (spigot down), which must fail the overhang check
