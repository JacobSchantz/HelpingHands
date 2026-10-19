# Generalist Gripper · Generation 11 — yellow fingers, built by Opus 5.5

Jake (voice-6663a540) asked for Gen 11, starting from the better of Gen 9 and Gen 10. Opus 5.5
builds it first. GPT-6 Astra then does a refinement pass, which goes in its own folder so both
stay viewable. The scope is the same as Gen 7: only the two yellow fingers, with every hole going
through. Jake's notes:

- On the ridges: *"I think they are cuts, but very shallow, maybe one millimeter or even less.
  They travel the whole width of the gripper."*
- On the shape: refine it ever so slightly against the photos, especially skinny, pointed tips.

## Starting point

Gen 11 starts from **Gen 10**. Jake found Gen 9 and Gen 10 "pretty similar". Gen 10's pipeline has
a centred point and the `genus.py` through-hole count, and that count is what keeps the new
grooves from opening any hole.

## What changed from Gen 10

- **Ridges.** 99 grooves, each 0.5 mm deep and 0.5 mm wide, at a 1.0 mm pitch. They run along
  the whole inner (gripping) edge, from the head corner over the step faces to about 1.5 mm from
  the point. Each one is cut straight across the full thickness of the finger, with no lip, as
  `robot.png` and `side.png` show. Gen 10 had 11 grooves on the blade only, inset from each face.
  - `trace_photo.py` (`ridges()`) places each groove square to the local edge.
  - `gripper.scad` (`ridges2d()`) measures the depth from the finished edge and keeps a 0.6 mm
    wall to every hole.
  - A groove is skipped only at a corner sharper than 100°, or where two would converge into a
    loose sliver in an inside corner.
- **Tip.** The blade's width curve gains a (1−f)^Q factor, with Q = 1.15 on the jaw edge and
  1.35 on the outer edge. The mid-blade stays about as full as Gen 10, but the last few mm narrow
  to a needle.
  - A floor of 0.6·d·(1−d/4 mm), where d is the distance to the point, keeps the tip at least
    0.9 mm across 1 mm back, so it doesn't print as a single fragile line.
  - The beak thins to 1.6 mm at the point (Gen 10: 2.0 mm).
- **Slots.** The row moved 0.4 mm inboard so the narrower jaw edge keeps a wall. All 33 designed
  through-holes are intact (`genus.py`).
- **Outline.** Fixed a zero-width spur at the blade root, left by a patch inserted against the
  outline's direction.

## Build-review rounds

A separate reviewer agent judged each round against the photos. Each round's source, renders and
notes are in `rounds/`, and `compare.html` shows them all over the photo.

| Round | What changed | Score |
|---|---|---|
| r1 full-width grooves | 0.6 mm grooves across the full thickness; needle tip; slot row inboard | 7.5/10, yes |
| r2 ribs over steps | grooves from the head corner and over the step faces; 0.5 mm deep; 0.6 mm wall to holes | 8/10, yes |
| r3 printable point | tip floor of at least 0.9 mm at 1 mm back; grooves to ~1.5 mm from the point | 8.5/10, yes |

r3 is the shipped design, and it's the current `gripper.scad`.

- **Rejected.** The reviewer twice suggested ending the yellow in a 3–4 mm flat where the black
  nub sits. That went against Jake's "skinny, pointed tips", so the tip stays a needle, only
  thickened for printing.
- **Still open, for the Astra pass:**
  - one plain band at the inside corner below the beak's shoulder;
  - `side.png` may show the beak tapering from the outer side only, like a chisel (low confidence);
  - the black TPU nub is a separate part and isn't modelled.

## Files and checks

- `python3 trace_photo.py` writes `trace_px.scad` (generated: outline, holes, slots, groove
  stations).
- `python3 export_models.py` writes the STLs (each watertight and one body), `viewer_parts.json`,
  and `previews/`. `previews/jaw.png` is the ribbed inner face.
- `python3 genus.py` checks that the right finger has exactly the designed 33 through-holes.
- `python3 check_geometry.py` checks:
  - no collision anywhere from 0 to 30°;
  - the closed tips don't touch (1 mm gap);
  - a positive control.
- `python3 photo_match.py` writes `previews/photo_match.png`, `python3 compare_page.py` builds
  `compare.html`, and `./save_round.sh <name>` snapshots a round.

Scale is assumed (0.2 mm/px, about 110 mm from pivot to tip), as in Gen 7. No real part was measured.
In the gallery, the open/close slider uses `cad/mobile_gallery/poses.js`, with the pivot at ±27.359 mm.
