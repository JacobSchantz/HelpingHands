# Generalist Gripper · Version 1.19: wide beak

voice-13bdab11. Jake: *"Make the section from where the finger starts rounding to the tip much thicker. Extend the width
outward through that rounded section, but it should still come to a point at the tip."*

Builds on 1.18 (`v018_generalist_flat_taper`, voice-07e1e6a1). Gripper only (the 1.x line).

## What changed from 1.18

Only the plan-view outer edge from the black dot to the point (`trace_photo.py` `OUTER`, one cubic Bezier):

| | 1.18 | 1.19 |
|---|---|---|
| Edge leaves the dot | along the shank | 15 deg outward (`out_deg`) |
| Near / far handle (x chord) | 0.30 / 0.30 | 0.50 / 0.25 |
| Outward bow at the far handle | 0.04 x chord | 0.20 x chord |
| Beak width at the dot / 25 / 50 / 75 / 90 / 97 % to the point | 7.5 / 7.6 / 5.9 / 3.2 / 1.4 / 0.6 mm | 7.5 / 10.5 / 11.4 / 8.8 / 4.7 / 1.8 mm |
| Outer edge arriving at the point | 25 deg off the axis | 56 deg off the axis |

The inner (jaw) edge, the point itself, the closed triangle and tip-only contact, the holes, grooves and 1.18's flat-bottom
taper (12 mm to 2.4 mm at the point, dorsal face only) are unchanged. The six beak slots stay centred between groove bottoms
and the outer edge, so they move outward with it. `gripper.scad` `contact_back` is re-measured (+0.0005; the wider point
keeps its full reach through the 0.3 mm tip round), so the pivots are 27.2512 mm apart from centre.

## Parts

| Part | STL (assembled pose / print) |
|---|---|
| Right finger | `exports/parts/right.stl` / `exports/print/right.stl` |
| Left finger (mirror) | `exports/parts/left.stl` / `exports/print/left.stl` |

`gripper.scad` `part=` takes `assembly`, `fingers`, `right`, `left`, `collision`. Prints lying on the flat ventral face, no
supports, as 1.18.

## Checks (all pass)

`python3 trace_photo.py` (regenerates `trace_px.scad`), `python3 export_models.py`, `python3 check_geometry.py`,
`python3 genus.py`:

- fingers never collide 1 to 30 deg; closed they touch without overlap, and pushed 0.02 mm together meet only at z 123.3-123.8
  (the last 1.5 mm); 20.7 deg included V behind the point;
- closed gap within 0.056 mm of the target from 1 to 20 mm back;
- flat bottom and one-sided taper as 1.18;
- 33 through-holes, as designed.

`previews/top.png` and `finger.png` show the new beak; `compare_web_stl.md`: web vs STL.

## Not verified

Not printed. The new width is Jake's request read by eye, not measured off the reference photo; the Generalist photo's beak
is slimmer than this.
