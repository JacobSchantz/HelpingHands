# Generalist Gripper · Generation 7 — the yellow fingers only

Jake (voice-5e5e0497): *"delete everything else, just keep the yellow grippers for
Gen 7, and just focus on getting the yellow part to look as close as possible to
Generalist's yellow part."* So Gen 7 is two yellow fingers and nothing else. It has no
housing, gears, servo, black carriers, TPU tips or straps. (An earlier reading of the
voice note asked for Pollen's Grabette. Jake corrected that, so it was not built.)

## Where the shape comes from

The outline is a **pixel trace** of the lower finger of the left-hand device in
`cad/reference/generalist_gripper_gen6_two_hands.png`. That photo is the flattest,
sharpest profile of a finger in the set. The px coordinates live in `gripper.scad`
(`outline_px`, `root_holes_px`, `dot_px`, the slot row). `px()` maps them to mm. To
re-trace, edit those lists and run `export_models.py`. `previews/overlay.png` draws
the trace back on the photo, so you can see any mismatch directly.

What the photo shows, and what is now modelled:

- a **root gusset**: a wide triangle at the base with nine larger (Ø3) pockets, a
  hooked lip at the end, and a slot under it where the black carrier's tongue slides in;
- a slender **bar** with a staggered honeycomb of Ø2 blind pockets and thin walls;
- **two step teeth** on the inner edge, partway along. The edge drops outward at each
  tooth, which gives the bar its "lightning" look;
- a **knee** where the carrier ends, after which the blade steps outward;
- a **blade** with one black dot (Ø2.6 pocket) and a single row of six slanted slots,
  tapering to a sharp point.

Each finger is 12 mm thick (along Y). Pockets are 3.5 mm deep from each face. One
`finger()` source is used for both sides; the left finger is its mirror image.
Closed (angle 0) is the photo pose, with the tips 1 mm apart.

## How a finger connects

Only a placeholder **Ø3.2 pivot bore** in the solid root lip. The pivots are 52.6 mm
apart (±26.3 mm), because that is where the two finger roots sit in the photo.
Generalist's real joint is hidden under the black body, so it is not modelled. Gen 6's
column/gear/servo stack is deliberately absent.

## Scale, honestly

No dimension was measured from a real part. The scale is assumed to be 0.2 mm/px,
which gives about 110 mm from pivot to tip (Gen 6 was 113 mm). It is consistent with
the pocket size in the photo (about 12 px ≈ 2.3 mm). The Insta360 in the photo is
foreshortened, so it only bounds the scale loosely, to roughly 0.19–0.23 mm/px. To
rescale the whole finger, change `mm_per_px`. The 12 mm thickness is a judgement from
the side and robot photos, not a trace.

## Files and checks

- `gripper.scad` — source. Parts: `left`, `right`, `assembly`; `angle` 0–30°.
- `python3 export_models.py` — writes the STLs to `exports/` (watertight, consistent
  winding, one body each), `viewer_parts.json`, and `previews/` (`top`, `open`, `iso`,
  `finger`, `overlay`, `compare_target`).
- `python3 check_geometry.py` — checks that the fingers never collide from 0 to 30°
  and that the closed tips don't touch, with a positive control.
- The gallery slider uses the hinge in `cad/mobile_gallery/poses.js`.
