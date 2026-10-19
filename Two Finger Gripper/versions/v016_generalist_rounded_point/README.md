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

## Round 3 (Jake: smooth the dot, straighter outside, a triangle)

*"At the large circle toward the end of the fingers there's an indent — smooth it out. The outside profile running in
toward the tip should be more of a straight line — it can round slightly. Near the tip the two fingers should never run
parallel ... so the closed shape reads like a triangle coming to the point."* `previews/closed_full.png` (whole closed
pair) and `previews/compare_closed_photo.png`.

- **Triangle.** r2's V levelled off at a 2 mm gap 6 mm back and then ran parallel for ~20 mm. Now each jaw edge runs from
  the point all the way back to the crest of the second knob swell, just behind the dot, as half-gap `H (d/D)^0.85`
  (`TRIANGLE`; H 5.4 mm at D 41 mm). The gap widens at every distance: 20.7° included 1–2 mm back, easing to ~15°
  further back. It never runs parallel.
- **The indent at the dot.** It came from two joins: on the inner edge, the beak's edge dipped in at the dot before the
  knob swell; on the outer edge, there was a 0.6 mm step. The inner edge now runs straight into the knob crest, and both
  joins are Gaussian-smoothed (`JOIN`, `soften()`).
- **Straighter outside.** From the dot the outer edge is one nearly straight Bezier into the point, bowed out 4 % of
  its length (`OUTER`). It replaces r2's bulge and rounded `NOSE`.
- **Knock-ons.** The slots are centred across the slimmer beak (otherwise three broke through). `tip_zone` 6 → 6.25 mm,
  because a groove wall landed on the 6 mm cut and left a non-manifold edge. The sharper plan point rounds back
  further: `ROUND_BACK` 1.0 → 1.5 and `contact_back` −0.065, so the pivots are now ±27.1856 (`poses.js`).
  `check_geometry` `GAP_TOL` 0.12 → 0.20: the model runs a steady 0.13 mm under the target, which is that rounding.

## Round 2 (Jake: edit Gen 16 in place)

*"Round the two bump-outs along the length even further — really rounded. Make the tip thicker; it should still come to
a single point where the two sides touch. Behind the tip the two sides should diverge at a sharper angle ... much
wider."* Matched to the closed photo above. `previews/compare_closed_photo.png`: photo, closed top view, closed tip, edge.

- **Knobs.** Each swell is ~2.3× wider (`KNOBS` half-widths 30/28 px, was 13/11) and 1.2 mm high, so the crest radius is
  ~4 mm (was ~1.4). The ramp under them is smoothed first (`KNOB_BASE_SIGMA`), so their feet have no corners.
- **The V.** Closed, each inner edge leaves the point at 15° (30° designed, 26° measured 1–2 mm back; was 6.8°) and the
  gap levels off at 2 mm (`WEDGE`), about what the jaw already has 25 mm back, so it never narrows again.
- **Thick tip, plan view.** The outer edge moves out by whatever the wider V cuts from the inner edge (`KEEP_WIDTH`), so
  the beak keeps its width. Its last 7 mm is a rounded nose (`NOSE`) that arrives at the point 65° off the axis, not r1's
  straight 45° run in.
- **Thick tip, side view.** `tip_thick` 0.5 → 2.4 mm, with a parabola taper (full until near the point, then rounding in)
  in place of Gen 9's concave `ease()` needle.
- Slots keep their place across the beak, measured on r1's beak (`beak_slots`); otherwise the wider V broke two through.

## What changed from Gen 15 (round 1)

- **Length, beak, holes, slots and closed contact are Gen 15's.** Dot → point is still ~42 mm. Closed, only the points
  touch, with a 6.8° V behind them (r2: 30°).
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
`previews/compare_web_stl.png`, `compare_web_stl.md`. Overlap: front 98 %, side 100 %, top 100 %, iso 99 %. The front
fringe is the grooves and edge rounding, which only the STL has. `cad/compare/designs.py` now picks up any version folder
that has a `web/concept.js`.

## Checks (all pass)

- `python3 trace_photo.py` → `export_models.py` (every STL is one watertight body) → `genus.py` (33 through-holes, as
  designed) → `check_geometry.py` → `compare_gens.py`.
- `check_geometry.py`:
  - no collision from 1 to 30°;
  - closed, the fingers touch with no overlap;
  - pushed 0.02 mm together, they overlap only at the point (z 123.31–123.86);
  - the gap is within 0.033 mm of the `WEDGE` target from 1 to 20 mm back;
  - the included angle is 26.4° (check: ≥ 20°).
  The gap is read at the ridge tops (innermost over a 1 mm groove pitch) wherever there are grooves, and the target is
  read the same way (r2: the 30° wedge changes 0.5 mm across that window). A single cut could land in a groove bottom.
- Pivots are at ±27.1856 mm (`cad/mobile_gallery/poses.js`; r2: 27.2517).

## Limits

- Nothing is printed. r2's 2.4 mm tip is sturdier than r1's 0.5 mm.
- The 30° V and 2 mm gap are read by eye from the closed photo, not measured (`closed_trace.json`'s fitted gap is far
  narrower; the photo can't resolve it).
- "About 1 mm" is read as the knob height. If it meant the serration grooves, change `ridge` in `gripper.scad`.
- The knob ramp and swells are hand-drawn in photo px, not traced.
