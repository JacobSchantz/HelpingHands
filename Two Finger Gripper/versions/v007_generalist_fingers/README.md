# Generalist Gripper · Generation 7 — the yellow fingers only

Jake (voice-5e5e0497): *"delete everything else, just keep the yellow grippers for
Gen 7, and just focus on getting the yellow part to look as close as possible to
Generalist's yellow part."* So Gen 7 is two yellow fingers and nothing else. It has no
housing, gears, servo, black carriers, TPU tips or straps. (An earlier reading of the
voice note asked for Pollen's Grabette. Jake corrected that, so it was not built here.)

## Where the shape comes from

`trace_photo.py` finds the finger **by colour**. It picks out the yellow pixels of the
lower finger of the left-hand device in `cad/reference/generalist_gripper_gen6_two_hands.png`,
simplifies that silhouette into an outline, and turns every dark blob inside it into a hole
with its own position, size and (for ovals) angle. The result is written to `trace_px.scad`,
which is generated and should not be hand-edited. A few spots are patched by hand, and each
patch is listed with its reason at the top of `trace_photo.py`:

- the seam where the two blades touch;
- the root corner hidden by the body, and the hole under it;
- the blurred tip;
- the blend where the blade starts;
- three holes the blur misreads.

`gripper.scad` maps photo px to mm (`px()`, 0.2 mm/px), smooths the edges by 0.4 mm and
cuts **every hole all the way through**:

- 25 round or oval holes;
- the 17 px blade dot;
- 6 slanted slots, the last one smaller.

The inner (gripping) edge of the blade is ribbed. Jake asked for "ridges on the inside", and
the side photo shows the jaw faces ribbed across their width. So 10 grooves (1.6 mm pitch,
0.8 mm wide, 0.6 mm deep) are notched square to the jaw edge, from where the blade starts to
the tip, and run through the full thickness (`jaw_px`, `ridge`).

The finger is 13 mm thick. From the black dot it wedges down to 4 mm at the point, as the
side and robot photos show.

## Build-review rounds

Each round is kept in `rounds/` with its source, renders and the reviewer's notes
(`round.json`). Jake asked for three rounds. A separate reviewer agent compared each round
with the photos; the photos are the truth.

| Round | What changed | Reviewer score |
|---|---|---|
| r1 hand trace | first Gen 7, points clicked by eye, blind pockets | not reviewed |
| r2 colour trace | colour trace, real hole positions, through-holes, tapered blade | 7/10 |
| r3 review fixes | smooth edges, slot angle, dot size, ovals, no visible bore | 7.5/10 |
| r4 wedge tip | 13 mm with a wedge from the dot, narrow tip, fatter slots | see `rounds/r4_wedge_tip/round.json` |

`python3 compare_page.py` builds `compare.html`. It is one self-contained page that shows
each round on top of the photo, in the photo's own pixels, with a fade slider. It also shows
the 3D finger beside the robot, side, top and closed photos, with camera presets. To make
the overlay on its own, run `python3 photo_match.py`, which writes `previews/photo_match.png`
(photo | model | blend).

## How a finger connects

Not modelled. The photo shows the hook lip solid, and Generalist's joint sits under the black
carrier, so no pivot bore is cut. `px_pivot` is only the origin of the finger frame. The
fingers are placed 2·`pivot` apart, so that the closed jaws sit 1 mm apart in the photo pose.

## Scale

No dimension was measured from a real part. The scale is assumed at 0.2 mm/px, which gives
about 110 mm from pivot to tip. The 13 mm thickness and the wedge are read from the side and
robot photos. To rescale, change `mm_per_px`.

## Files and checks

- `python3 trace_photo.py` re-traces the photo and writes `trace_px.scad`.
- `python3 export_models.py` writes:
  - STLs to `exports/` (each watertight, one body);
  - `viewer_parts.json`;
  - `previews/` (`top`, `open`, `iso`, `finger`, `edge`, `overlay`, `compare_target`).
- `python3 check_geometry.py` checks that the fingers never collide from 0 to 30° and that
  the closed jaws don't touch, with a positive control.
- `python3 photo_match.py` and `python3 compare_page.py` build the comparisons.
