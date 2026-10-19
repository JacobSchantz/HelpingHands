# Generalist Gripper · Generation 11b — the Astra pass on Gen 11's yellow fingers

Jake (voice-72fa2b1a) asked for a GPT-6 Astra refinement pass on Opus 5.5's Gen 11, kept in its
own folder so both stay viewable in the gallery (Gen 11 and Gen 11b). **GPT-6 Astra was
unavailable, so Opus 5.5 did this pass too.** It starts from Gen 11 Opus r4, a copy of
`v011_generalist_fingers_opus`.

## What changed from Gen 11 Opus

- **Chisel beak, in plan.** `side.png` is a dorsal (plan) view: the slot row and the black dot sit
  near the jaw edge, as they do in `two_hands.png`. So the "one-sided chisel" that Opus left open
  is the plan outline, not an edge-on taper. The jaw edge runs straight to the nub. The outer edge
  stays full, then breaks at a knee into one straight facet.
  - Past the dot, the outer edge is eased up to 0.9 of its half-width at f = 0.77. From there it
    runs straight to the point, about a 22° break (`trace_photo.py` `NEEDLE_CHISEL`).
  - The point stays skinny and printable: the r3 floor is unchanged.
  - The edge-on (thickness) taper stays symmetric.
- **Inside-corner band.** Nothing to change. r4 already starts the grooves at the shoulder's
  inside corner, and the smooth face below it is the shank's inner wall.
- **Grooves** are the same 0.5 mm deep, 0.5 mm wide, 1.0 mm pitch, straight across the full
  thickness. 29 of them run from the shoulder and stop 1.6 mm short of the point
  (`RIDGE_TIP_CLEAR_PX`). Without that stop, the fuller beak let one more tip groove in, and it
  broke through as a pinhole.
- Still 33 through-holes (`genus.py`), one watertight body per finger, and no collision from 0 to 30°.
  The pivot is at ±27.672 mm.

## Astra-pass rounds

| Round | What changed | Score |
|---|---|---|
| a1 chisel beak | straight outer chamfer past f = 0.6 | 7.5/10, yes: still read as one curve |
| a2 knee chisel | full outer edge to a knee at f = 0.77, then a straight facet; grooves stop 1.6 mm short | 8/10, yes |

a2 is the shipped design. Each round's `round.json` has the separate reviewer's notes. `compare.html`
shows Opus's r1–r4 and a1–a2 over the photo.

---

The Gen 11 Opus README follows, for history.

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

- **Ridges.** 29 grooves, each 0.5 mm deep and 0.5 mm wide, at a 1.0 mm pitch. They run along
  the gripping jaw only, from the last step face below the beak shoulder to about 1.5 mm from
  the point (r4; r1–r3 had 99 down the whole inner edge, which read as a serrated saw). Each one is cut straight across the full thickness of the finger, with no lip, as
  `robot.png` and `side.png` show. Gen 10 had 11 grooves on the blade only, inset from each face.
  - `trace_photo.py` (`ridges()`) places each groove square to the local edge.
  - `gripper.scad` (`ridges2d()`) measures the depth from the finished edge and keeps a 0.6 mm
    wall to every hole.
  - A groove is skipped only at a corner sharper than 100°, or where two would converge into a
    loose sliver in an inside corner.
- **Tip.** The blade's width curve gains a (1−f)^Q factor, with Q = 1.05 on the jaw edge and
  1.12 on the outer edge (outer fullness A = 2.8; Gen 10: Q = 1, A = 2.6). The beak is about as
  full as Gen 10 and only the last few mm sharpen to a clean point. r1–r3 used Q = 1.15/1.35 and
  A = 3.0, a needle that lost Gen 10's beak.
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
| r4 jaw grooves, full beak | Jake: r3 read as a saw and lost Gen 10's beak. Grooves on the jaw only; Gen 10's beak fullness back, clean point | 8/10, yes |

r4 is the shipped design, and it's the current `gripper.scad`.

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
In the gallery, the open/close slider uses `cad/mobile_gallery/poses.js`, with the pivot at ±27.672 mm. Gen 11 Opus has the same pivot; its poses.js entry still said 27.359 and is corrected too.
