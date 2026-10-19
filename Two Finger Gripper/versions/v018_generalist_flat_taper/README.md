# Generalist Gripper · Version 1.18: flat-bottom taper

voice-07e1e6a1. Jake: *"Correction to 1.17: the fingers SHOULD taper in thickness toward the tip like the Generalist
reference gripper does. But keep one face flat so it's easy to 3D print: the taper goes down from one side only (a flat
bottom with the top sloping down toward the tip), not a symmetric taper toward the midplane."*

Builds on 1.17 (`v017_generalist_strap_slide`, Gen 17). Gripper only, the 1.x line: 1.17's yellow lug and black strap slide
are left out here; the loop attachment lives in 2.x (`v201`, `v202`).

## Key reference images

`cad/reference/generalist_gripper_gen6_closed.png` (plan view and contact) and `generalist_gripper_gen6_side.png` (the beak
thins toward the tip). See also `references/generalist/`.

## What changed from 1.17

| | 1.17 | 1.18 |
|---|---|---|
| Thickness behind the black dot | 12 mm | 12 mm |
| Thickness at the point | 12 mm (no taper) | 2.4 mm (`tip_thick`, Gen 16 r2's value) |
| Taper | none | Gen 16 r2's parabola, dot (z 82.1) to point (z 124.3), **all on the dorsal (+Y) face** |
| Ventral (-Y) face | flat | flat, one plane from base to point: the print bed |
| Lug + strap slide | yes | no (gripper only) |

Gen 16 tapered both faces toward the midplane (`side_taper`); 1.18's `flat_taper()` puts the whole drop on one face. Plan
view, holes, grooves and the closed point contact are Gen 16 r3's, unchanged.

## Parts

| Part | STL (assembled pose / print) |
|---|---|
| Right finger | `exports/parts/right.stl` / `exports/print/right.stl` |
| Left finger (mirror) | `exports/parts/left.stl` / `exports/print/left.stl` |

`gripper.scad` `part=` takes `assembly`, `fingers`, `right`, `left`, `collision`.

## How it prints

Lay each finger on its flat ventral face. The sloped dorsal face is a top surface (at most ~25 deg off the bed near the
point), so no supports. Holes and grooves run through vertically as before.

## Checks (all pass)

`python3 export_models.py` (STLs, previews, watertight meshes), `python3 check_geometry.py`, `python3 genus.py`:

- fingers never collide 1 to 30 deg; closed they touch only at the point (the last 1.5 mm), 20.7 deg included V behind it;
- closed gap within 0.164 mm of the Gen 14 target from 1 to 20 mm back;
- `flat_bottom_and_one_sided_taper`: the ventral face is at y = -6 at every station from the shank to 3 mm short of the
  point, and the thickness follows the parabola (12 → 3.7 mm at 3 mm short of the point) within each 0.5 mm slab (±0.05 mm);
- the right finger has 33 through-holes, as designed (the slope does not break into any beak hole).

`previews/edge.png` is the finger edge-on: flat face on the left, taper on the right. `compare_web_stl.md`: web vs STL.

## Not verified

Not printed. The taper's shape and the 2.4 mm tip are read from the photos by eye (Gen 16 r2), not measured.
