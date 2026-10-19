# Generalist Gripper · Generation 12 — the tweezer (built by Opus 5.5)

Jake (voice-438af2a9): *"Do another version. It should be basically a set of tweezers that can
follow the fingers. Pretty similar to what we have now, but significantly smaller at the end, and
more tweezer-like."* Only the two yellow fingers, as in Gens 7–11. Every hole goes through.

## Starting point

Gen 12 starts from **Gen 11 r4** (`v011_generalist_fingers_opus`), the version with Gen 10's fuller
beak and grooves on the jaw only. It keeps the same root: the honeycomb, the hook lip, the black
dot, the pivot frame and the open/close swing. Each finger still swings about its own pivot, so
the pair follows thumb and index the same way Gen 11 does. Earlier generations are unchanged.

## What changed from Gen 11

- **Tine.** Past the black dot (z = 80 mm), the outer edge tapers along
  `(1−f)^1.6` (`tine_out`) to a **1.4 mm** tip. Gen 11's blade was ~11 mm across at the dot and
  came to a point. At z = 100 the tine is now ~3 mm deep, and at z = 104 ~1.8 mm. The reach is
  the same as Gen 11 (~107 mm from the pivot).
- **Flat land, tips meet.** The jaw edge runs dead straight at `land_x = −27.1` over the last
  ~11 mm (z 96 → 107), so the two lands **close flat against each other** at angle 0
  (`tip_gap = 0`; Gen 11 left a 1 mm gap between points). The pivot spacing moves from
  ±27.672 to ±27.1 mm.
- **Flatter blade.** The thickness along Y now thins along `(1−f)^1.5` (Gen 11: `1−f²`, a beak).
  It thins early and levels off, so the tip is a flat 2.4 × 1.4 mm pad with a rounded end,
  not a point.
- **Serration along the whole inner edge (r2).** Fine cross-cuts (0.4 mm deep, 0.5 mm wide,
  1 mm pitch) run from the head corner down the entire inner edge and along the land, stopping
  1 mm short of the tip. Jake: the closed reference photo shows the serration spanning
  essentially the entire inner edge (r1 had cut only 7 grooves near the tip). The traced edge's
  stations come from `trace_photo.py` (`RIDGE_FROM` is the head corner); the land's are straight
  cuts in `ridges2d`. Each groove keeps 0.6 mm of wall to every hole.
- **Slots.** Gen 11's last three blade slots don't fit in the slender tine, so they are dropped
  (`slots_kept`). That leaves 30 designed through-holes (Gen 11: 33).

## Files and checks

- `python3 export_models.py` writes the STLs (each watertight and one body),
  `viewer_parts.json` and `previews/`. `previews/closed.png` shows the two tips meeting.
- `python3 genus.py` checks that the right finger has exactly the designed 30 through-holes.
- `python3 check_geometry.py` checks:
  - no collision from 1 to 30°;
  - at 0° the lands touch with no overlap (a ≤ 1 µm float sliver is allowed);
  - two positive controls: pushed 0.05 mm together, the fingers overlap, and the overlap
    runs along the tip region.
- `python3 trace_photo.py` regenerates `trace_px.scad`, the photo trace of the root.
  `python3 photo_match.py` draws the model over the photo; the tine now deliberately departs
  from the photo.

Scale is assumed (0.2 mm/px), as in Gens 7–11. No real part was measured, and there is no
mount, drive or spring. A 1.4 mm PLA tine about 25 mm long will flex. That suits tweezers, but
it hasn't been tested.

In the gallery, the open/close slider uses `cad/mobile_gallery/poses.js`, with the pivot at
±27.1 mm.
