# Generalist Gripper · Generation 9 — the yellow fingers only (Sonnet 5.5)

Gen 9 was designed and built by **Sonnet 5.5** for pebble **voice-31ca3e68**. Jake:
*"Make two more versions... Just reference those images and make it look as close as
possible. The tips on these ones don't come to a nice enough point and aren't skinny
enough. But more specifically, reference the images."* Scope is the same as Gen 7: only
the two yellow fingers. There is no housing, gear, servo, carrier, TPU tip or strap. Every
hole goes all the way through, and the inner (gripping) edge of the blade is ridged.

Gen 9 starts from the Gen 7 pipeline (colour trace of the two-hands photo) and changes:

- **Tip (r3).** The distal blade is a needle with a convex belly on the outer edge, a straight inner
  edge and a long taper. The point is under 1 mm wide and under 1 mm thick, and the wedge thins to a
  chisel edge. Measured on the STL (width across the finger x thickness through it):

  | Distance behind the point | Gen 7 | r1 | r2 | r3 |
  |---|---|---|---|---|
  | 0.5 mm | 3.7 x 4.8 mm | 1.4 x 1.5 | 0.3 x 1.4 | 0.4 x 0.6 |
  | 1 mm | 5.4 x 5.0 mm | 2.2 x 1.8 | 0.6 x 1.6 | 0.8 x 0.8 |
  | 2 mm | 7.9 x 5.3 mm | 3.7 x 2.3 | 1.1 x 2.1 | 1.5 x 1.1 |
  | 5 mm | 10.9 x 6.4 mm | 7.1 x 3.8 | 2.6 x 3.7 | 3.6 x 2.4 |

- **Blade width.** About 1.3x the shank at the dot and about 1x further out. The two_hands photo
  shows a wider blade, the top, robot and target photos a narrower dagger; this is the compromise.
- **Ridges.** 21 fine, shallow V teeth (0.35 mm deep, 1 mm pitch) along the inner edge, plus the 6 through-slots.
- **Closed pose.** Angle 0 turns each finger 3.3 degrees outwards of the photo pose: the blades sit 1 mm apart at
  the point and about 3 mm at the first tooth. Turning further to full flush would make the inner shank swells collide.
- **Holes.** All round. The head honeycomb is tighter. The shank holes follow one regular taper.
- **Wedge.** It starts at the black dot with zero slope (`ease()` in `gripper.scad`), so no crease.
- **Outline.** A smoothed contour with hand-drawn spline patches (tip, shoulders, blade root, base
  hook), not a coarse polygon. The base hook is a rounded J-claw.
- `trace_photo.py` is the place to change any of this.

## Where the shape comes from

`trace_photo.py` finds the lower finger of the left-hand device in
`cad/reference/generalist_gripper_gen6_two_hands.png` by colour, smooths its silhouette and
turns each dark blob into a hole. It writes `trace_px.scad` (generated, do not edit).
`gripper.scad` maps photo px to mm at an assumed 0.2 mm/px and cuts the holes, slots and
jaw teeth through the full thickness. The finger is 13 mm thick up to the dot.
No part was measured; the scale is an assumption (change `mm_per_px`).

## Build-review rounds

Each round is kept in `rounds/` with its source, renders and `round.json`. A separate reviewer
compares each round with the photos; the photos are the truth.

| Round | What changed | Reviewer score |
|---|---|---|
| r1 sharp tip | sharp skinny tip, smooth wedge, round holes, narrower slots, smoothed outline | 5.5/10 |
| r2 needle tip | needle tip with long taper, 11-tooth ridge row, tighter honeycomb and regular hole taper, smoothed shoulders, J-claw hook, smoother walls | 7.5/10 |
| r3 belly and chisel | outer belly, chisel tip under 1 mm thick, 21 fine ridges, bigger hole chain, steeper shoulder step, nearly flush closed pose | 8.5/10 (see `rounds/r3_belly_chisel/round.json`) |

`python3 compare_page.py` builds `compare.html` (each round over the photo with a fade
slider, plus a 3D finger beside the robot, side, top and closed photos).
`python3 photo_match.py` writes `previews/photo_match.png` (photo | model | blend).

## Not modelled

How a finger connects. The photo shows the hook lip solid, and the joint sits under the black
carrier, so no pivot bore is cut. The fingers are placed 2·`pivot` apart so the closed tips
sit 1 mm apart.

## Files and checks

- `python3 trace_photo.py` re-traces the photo and writes `trace_px.scad`.
- `python3 export_models.py` writes the STLs (`exports/`, each watertight, one body),
  `viewer_parts.json`, `mesh_checks.json` and `previews/`.
- `python3 check_geometry.py` checks that the fingers never collide from 0 to 30° and that
  the closed jaws do not touch, with a positive control.
