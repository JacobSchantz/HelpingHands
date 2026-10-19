# Generalist Gripper · Version 2.4: parametric (gripper plus handles)

voice-3211a12d. 2.4 is **2.3** (`v203_generalist_tongue_pocket`) with every meaningful dimension pulled out into named,
documented parameters, so later versions are made by changing parameters only, plus a live slider for each one in the
website preview.

- **One parameter file: `params.json`.** 67 parameters in six groups: finger outline, finger solid, handle plate, strap
  slots, tongue and pocket, and calibration. Each has a value, unit, slider range, step and a one-line doc. `params.py`
  writes `params.scad`, which `gripper.scad` includes. `trace_photo.py` reads the outline parameters (beak length, outer-edge
  lean/fullness/bow, jaw convergence, bump-outs, smoothing, hook depth, slot count, grooves). The calibration group (photo
  scale and frame, traced rail points, contact correction) is documented but has no slider.
- **Same geometry.** At `params.json`'s values, `trace_px.scad` and the STLs are byte-identical to 2.3's, and every 2.3
  check passes.
- **New knobs, off by default:**
  - `tip_thick` below `plate` turns on 1.18's flat-bottom taper, with `taper_power` and `taper_start`.
  - `outer_lean_deg` is 1.19's wide-beak lean.
  - `hook_depth` scales the base J-hook.
  - `hole_scale` and `dot_scale` resize the honeycomb holes and the black dot.
  - The dovetail's `neck_d`, `head_depth` and `flank_deg`.
- **Guard rails.** `gripper.scad` asserts the combinations that can't make a solid: the head must be wider than the tongue,
  the flanks must fit above the head's depth, corner radii must fit, and the slots must fit the plate. The preview shows
  the message.

## Live tuning (the website preview)

Open Gen 2.4 in the HelpingHands Live Preview, tap it to focus, then tap **Tune**. Every non-calibration parameter has a
slider, grouped as in `params.json`. Changed ones turn gold, and tapping a value resets it. Each change posts to
`Scripts/serve_designs.py` `/tune`, which runs `live_render.py`. That renders the four real OpenSCAD parts with the
Manifold backend in a scratch copy, so nothing here is written. The viewer swaps them in without moving the camera.

- A solid-only change takes about 0.1 to 0.2 s.
- An outline change re-traces first and takes about 1 s. Each outline is cached, so dragging back is instant.
- While one render runs, only the newest values wait, so a drag always ends on what the sliders show.
- `?tune=name:value,...` in the URL reproduces a setting.
- **Copy** puts the changed values on the clipboard as JSON. Paste them into a pebble, and the next version is a copy of
  this folder with those values in `params.json`.

## Checks (2.4)

`python3 export_models.py && python3 genus.py && python3 check_geometry.py`: all pass, the same as 2.3. The export
regenerates `params.scad` and `trace_px.scad` from `params.json` first. The live renders are not checked. They are a
preview, and the checks run on the committed values only.

Not verified: nothing is printed. Far slider settings can make thin walls or a groove landing on the tip-zone cut. OpenSCAD
reports those as an error in the panel.

## 2.3 notes

voice-1557d48f. 2.3 is **2.2** (`v202_generalist_flush_loops`) with the yellow lug removed. Jake: keep 2.2's handles but
"drop the little connector". The handle should slide into the gripper itself instead: a long, narrow tongue slides in from
the top into a matching pocket along the finger's flat outer face, down by the little hook at its base.

- **Handle:** 2.2's black plate, unchanged in size (28 × 37 × 3.5 mm, two 21 × 3.5 mm strap slots). It now lies right
  against the finger's outer edge face (0.45 mm off it) instead of against the lug. Its foot reaches down into the base
  hook's notch, behind the hook's prong. The foot is trimmed to the notch's shape with 0.2 mm clearance.
- **Tongue:** on the plate's inboard face. It is 23.2 mm long along the edge and 3.5 mm wide. Its lowest 8 mm is a dovetail
  head (5.5 mm wide, 45° flanks). The rest is a plain bar 1 mm deep.
- **Pocket (keyhole):** cut into the finger's outer edge, running up from the hook:
  - dovetail lips where the head sits when the handle is seated;
  - a plain head-wide window just above the lips;
  - a narrow slot for the bar above the window.

  To fit the handle, drop the head into the window, then slide the handle 8.4 mm down toward the hook. The head goes under
  the lips, and the foot goes behind the hook. To remove it, slide it up and lift it off.
- **What holds it:** the lips and the hook keep the handle from pulling outboard. The notch bottom stops it sliding
  down. Only friction stops it sliding back up, as in 2.1 and 2.2.
- **Honeycomb:** the pocket opens into the sides of 4 holes near the outer edge, at about u -7.8, -3.7, 0.5 and 8.3 mm.
  The holes still go through. `genus.py` counts them (`BREACHED`).
- **Printing:** print the handle on its outer face with the tongue up; the head's 45° flanks need no support. The finger
  still prints flat. The lips' 45° roof needs no support. The window's roof spans 2.25 mm, and the bar slot's roof spans
  1.2 mm. Both are short unsupported overhangs.
- **Unchanged from 2.2:** the finger outline, holes, grooves, closed contact and full 12 mm thickness.

`previews/pocket.png` shows the empty pocket and hook. `previews/handle_in.png` shows the seated handle. `previews/iso.png`
shows the pair.

## Checks (2.3)

`python3 export_models.py && python3 genus.py && python3 check_geometry.py`: all pass.

- Every STL is watertight and in one piece.
- The finger has 37 holes: the 33 designed holes plus the 4 the pocket opens into.
- The handle has its 2 strap slots.
- All of Gen 16's contact checks still pass.
- The seated handle clears its finger by the 0.2 mm fit.
- Pulled 0.4 mm outboard, seated or lifted 0.4 mm, the handle hits the lips and hook, so it is retained.
- Lifted to the window, it slides down into place without hitting anything, and it lifts straight off outboard.
- No handle hits the other side from 0 to 30°.

Not verified: nothing is printed, and the 0.2 mm fit and the strap and digit sizes are nominal. The hook's prong stands
about 2.6 mm past the plate's outer face, at the bottom of the plate, within the finger's thickness.

## 2.2 notes (where they describe the lug, read 2.3's above)

voice-f7f729ac. 2.2 is **2.1** (`v201_generalist_strap_loops`) with each black strap slide's plate **turned 90° about the
finger's outer edge**. Jake: the flat pieces "shouldn't stick out the way they do in 2.1"; they should lie parallel to the
gripper's flat side, flush with it, instead of extending outward.

- **2.1:** the plate lay in the finger's plane and ran 33 mm outboard of the lug.
- **2.2:** the plate stands against the lug's outer face, parallel to the finger's outer edge face (the 12 mm side). It adds
  only `slide_t` (3.5 mm) outboard of the lug. It is 37 mm tall across the finger's thickness (`slide_h`), so it reaches
  12.5 mm past the dorsal and palmar faces. Its two strap slots sit there, one above and one below the finger, and the digit
  lies against the plate's outer face between them, along the finger.
- **Unchanged from 2.1:** the fingers, the lug, the dovetail groove and tongue, the 0.2 mm fit, the slot and strap sizes and
  every check. `gripper.scad` changes only `strap_slide()` (`yu()`, `slide_h`, `slot_ys()`) and the concept echo.
- **Printing:** lay the slide on the plate's outer face with the tongue up. The tongue's dovetail faces are 45°, so it needs
  no support. 2.1's slide had to stand on its end.

`previews/iso.png` and `previews/slide_fit.png` show the new pose. 2.1's notes follow; where they describe the slide plate
running outboard, read 2.2's above.

## 2.1 notes: Version 2.1, strap loops

voice-4c63021e. Versioning (AGENTS.md): 1.x is the gripper only, 2.x is the gripper plus handles. 2.1 is **1.17**
(`v017_generalist_strap_slide`, Gen 16's fingers at the full 12 mm thickness to the point) **plus the loop attachment**:
*"a small, black, flat piece that slides into the gripper and has two slots for loops (straps)"*. No camera attachment.

Folder name: `v201` = version 2.01, so `cad/compare` (which needs a `vNNN_` folder) still finds it; 1.17 is `v017`.

The design is 1.17's, copied, not `include`d, so a later 1.x change never moves 2.1. When the fingers or the slide
change, that is 2.2.

## Key reference image for the finger design

**`cad/reference/generalist_gripper_gen6_closed.png`**: closed, only the tips touch, and the gap opens quickly behind
them (see the Gen 16 README). The strap slide follows `generalist_gripper_gen6_two_hands.png` and `_closed.png`. In both
photos a black flat block sits outboard of each yellow finger, mid-shank, and a black loop passes through it around the
operator's digit.

## Four printed parts, each its own module and STL

| Part | Module | STL (assembled pose / print) | Colour |
|---|---|---|---|
| Right finger | `finger()` (with `lug()` fused on) | `exports/parts/right.stl` / `exports/print/right.stl` | yellow |
| Left finger | mirror of the right | `exports/parts/left.stl` / `exports/print/left.stl` | yellow |
| Right strap slide | `strap_slide()` | `exports/parts/right_slide.stl` / `exports/print/right_slide.stl` | black |
| Left strap slide | mirror of the right | `exports/parts/left_slide.stl` / `exports/print/left_slide.stl` | black |

`gripper.scad` `part=` takes `assembly`, `fingers`, `slides`, `right`, `left`, `right_slide` and `left_slide`. The viewer
(`viewer_parts.json`) shows all four, alone or together. They open and close on the gallery hinge, and each slide rides
with its finger.

## What 2.1 adds to the gripper (and what 1.17 changed from Gen 16)

- **Constant thickness.** Each finger is the full 12 mm plate from base to point. Gen 16's `side_taper` (thinning past the
  dot to a 2.4 mm tip) is gone. The point is only in plan, the closing plane. Plan outline, holes, grooves and the closed
  tip contact are unchanged from Gen 16 r3. `previews/edge.png` shows the finger edge-on.
- **Lug.** A yellow block (24 × 8 mm, full 12 mm thick) is fused to each finger's outer edge, mid-shank, where that edge is
  straight within 0.2 mm (`rail_p`, 10.8° off the finger axis). It carries a dovetail groove that is closed at the base
  end (2.5 mm stop) and open at the tip end.
- **Strap slide.** A black plate, 3.5 mm thick and 28 × 37 mm, with a dovetail tongue along its inboard edge. Hold it against
  the finger just above the lug and slide it down the groove toward the hook until it hits the stop. It has two 21 × 3.5 mm
  strap slots (for 20 mm webbing), 24 mm apart. The digit lies under the plate between them, and one loop goes down
  through one slot, around the digit and up through the other. Straps are not modelled.

## How it prints

- Every dovetail face is flat or at 45°. In the finger, printed flat, the groove roof is two 45° slopes and a 1.5 mm
  bridge, so it needs no support.
- Print the slide standing on one end (the tongue runs straight along that axis). The tongue's head is 6 mm tall and the
  plate is 3.5 mm, so the slide cannot lie flat without support.
- Clearance is 0.2 mm per side (`fit`).

## Dual render (STL is truth)

`web/concept.js` is the three.js vision: the traced outline extruded full thickness, and the lug and slide (with its slots)
as plain blocks. `Scripts/render_compare two-finger-gripper-v201-generalist-strap-loops` draws it beside the STLs with the
same cameras and writes `previews/compare_web_stl.png` and `compare_web_stl.md`. Overlap: front 98 %, side 99 %, top 100 %,
iso 99 %, exploded 95 % (the exploded gap is the tongue, which only the STL has).

## Checks (all pass)

Rebuild: `python3 export_models.py && python3 genus.py && python3 check_geometry.py`.

- `export_models.py`: every STL is one watertight, consistently wound body.
- `genus.py`: the finger has its 33 designed through-holes (the groove is blind), and the slide has 2.
- `check_geometry.py`: Gen 16's contact checks, all still passing:
  - no finger collision from 1 to 30°;
  - closed, the fingers touch only at the point;
  - the gap stays within 0.164 mm of the triangle target;
  - the included angle is 20.7°.

  2.1 adds:
  - each slide clears its own finger;
  - pulled 0.4 mm outboard, the slide hits the dovetail (it is retained);
  - no slide hits the other finger or slide from 0 to 30°;
  - the finger is 12 mm thick at every station from z 20 to 121 (3 mm short of the point).

## Not verified

- Nothing is printed. The 20 mm webbing, the 24 mm digit gap, the 0.2 mm fit and the lug position are nominal. None of
  them is measured on Jake's hand or straps.
- The slide is held only by the dovetail and the end stop. Nothing stops it sliding back out toward the tip. Strap tension
  pulls it outboard, which the dovetail resists, but a snap or detent may be needed once it is printed.
- The 12 mm thick point is blunter edge-on than Gen 16's 2.4 mm tip. That is what Jake asked for.
