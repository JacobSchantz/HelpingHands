# Generalist Gripper · Generation 17: the strap slide

voice-cfdf2d31. Jake: *"build the attachment. It is simply a small, black, flat piece that slides into the gripper and has
two slots for loops (straps)."* Then: *"This is Gen 17. Replace the current Gen 17 ... it isn't really rigged. No camera
attachment. Scope is only how the loops attach. The gripper fingers keep the same thickness along their whole length —
they must not narrow to a point in the thickness direction; the point is only in the closing plane."*

This replaces the old Gen 17 (`v017_generalist_simple`: fingers fused to side pads, a pivot plate and a camera cradle).
That folder is deleted. It is in git history before voice-cfdf2d31.

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

## What changed from Gen 16

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
as plain blocks. `Scripts/render_compare two-finger-gripper-v017-generalist-strap-slide` draws it beside the STLs with the
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

  Gen 17 adds:
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
