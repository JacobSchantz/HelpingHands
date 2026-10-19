# Generalist Gripper · Generation 16: the rounded point

Gen 15 and Gen 9 combined (voice-1fc7e062). Jake: *"keep Gen 15's length; keep the ridges but make them shallower, about
1 mm, less pronounced; make it more rounded like Gen 9; have it come to a nice point like Gen 9 does, but the two sides
should actually touch at the point; remove the black tip, so it is all yellow."* The simple handheld that was Gen 16 is
now Gen 17 (`v017_generalist_simple`, unchanged).

## Key reference image for the finger design

**`cad/reference/generalist_gripper_gen6_closed.png`** is THE key reference image for the Generalist gripper finger
design (Jake, 2026-10-19). It is the "Actual (Generalist)" → "Closed" photo in the design viewer (gallery copy:
`cad/mobile_gallery/reference/closed.png`). What it shows:

- Closed, **only the tips touch**; the gap opens up rapidly right behind the tip.
- Approaching the tip on the outside, the profile **rounds inward** into the final tip.
- The tip itself stays **relatively thick** — not a needle point.

Check every finger revision against this photo first.

## What changed from Gen 15

- **Length, beak, holes, slots and closed contact are Gen 15's.** Dot → point is still ~42 mm. Closed, only the points
  touch, with a 6.8° V behind them.
- **The knobs are rounded.** Gen 15 had two square knobs on the inner edge, mid-shank: a ~6 mm step and a bump. Now
  that edge is one smooth ramp with two rounded swells, 1 mm proud (`trace_photo.py KNOBS`, `KNOB_SWELL_PX`). I read
  "ridges, about 1 mm" as these knobs. The 0.4 mm serration grooves are unchanged.
- **Rounder outline, from Gen 9.** The traced contour is resampled and Gaussian-smoothed (`SMOOTH_SIGMA`), not an RDP
  polygon. The blade root's outer jog is Gen 9's S-curve, and the base hook is Gen 9's rounded J-claw.
- **The point, from Gen 9.** Past the dot the blade thins with Gen 9's eased taper to a 0.5 mm point (`tip_thick`,
  `ease()` in `gripper.scad`). Gen 15 used a parabola to a 1.6 mm blunt end.
- **All yellow.** Gen 15's dark tip pad is gone. Each finger is one body.

`previews/compare_gens.png` shows Gen 9, Gen 15 and Gen 16 at one scale, in plan and edge-on.

## Web vs STL

`web/concept.js` is the three.js vision: the traced outline and holes, extruded and pinched to the taper.
`Scripts/render_compare two-finger-gripper-v016-generalist-rounded-point` draws it beside the STLs with the same cameras →
`previews/compare_web_stl.png`, `compare_web_stl.md`. Overlap: front 97 %, side 100 %, top 100 %, iso 99 %. The front
fringe is the grooves and edge rounding, which only the STL has. `cad/compare/designs.py` now picks up any version folder
that has a `web/concept.js`.

## Checks (all pass)

- `python3 trace_photo.py` → `export_models.py` (every STL is one watertight body) → `genus.py` (33 through-holes, as
  designed) → `check_geometry.py` → `compare_gens.py`.
- `check_geometry.py`:
  - no collision from 1 to 30°;
  - closed, the fingers touch with no overlap;
  - pushed 0.02 mm together, they overlap only at the point (z 123.21–123.43);
  - the gap is within 0.085 mm of Gen 15's target from 1 to 20 mm back;
  - the included angle is 6.8°.
  The gap is read at the ridge tops (innermost over a 1 mm groove pitch) wherever there are grooves. A single cut could
  land in a groove bottom and read 0.8 mm too wide.
- Pivots are at ±27.2517 mm (`cad/mobile_gallery/poses.js`).

## Limits

- Nothing is printed. A 0.5 mm point is one or two extrusion lines thick and may be fragile.
- "About 1 mm" is read as the knob height. If it meant the serration grooves, change `ridge` in `gripper.scad`.
- The knob ramp and swells are hand-drawn in photo px, not traced.
