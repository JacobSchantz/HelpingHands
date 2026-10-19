# Generalist Gripper · Generation 13 — designed closed (built by Opus 5.5)

Jake (voice-decf86cd): *"Reference the closed one specifically to make Gen 13. It only touches at the
very tip, and everything from there backs off a little bit. The serration does span the entire length,
except maybe the very tip, and it's more beak-shaped at the tip. Instead of designing it open, design it
from a closed position first, because that's what determines how usable it will be. How it contacts is
key."* Primary reference: `cad/reference/generalist_gripper_gen6_closed.png`. Only the two yellow
fingers, as in Gens 7–12. Every hole goes through. Earlier generations are unchanged.

## 1. The closed sketch first

`trace_closed.py` traces the closed photo and writes `closed_sketch.png` (the photo with the trace on it,
and the gap curve) and `closed_trace.json` (outline, seam, fit).

- **Outline**: both yellow fingers by colour. Closed, they merge into one silhouette where the jaws meet.
- **Seam**: the dark line between the two jaws, row by row. Where it is under a pixel wide, its width is
  read from how dark it is (`FACE − v` summed across it).
- **Contact**: the seam disappears at the beaks (photo px 184.5, 327); nowhere else do the jaws meet.
- **Gap**: fitted as **g(d) = 9.3e-5 · d^3.15 mm**, d = mm behind the contact point: ~0.03 mm at 6 mm,
  0.13 mm at 10 mm, 0.57 mm at 16 mm, 1.1 mm at 20 mm, then the shoulder opens wide.
- Scale: the photo is a perspective view, so across the jaws it uses the dots' spacing (16.9 mm,
  0.48 mm/px) and along them dot-to-point (24.8 mm, 0.59 mm/px), both from Gen 11's geometry.

## 2. The fingers modelled closed

Gen 13 starts from **Gen 11 r4** (Gen 10's fuller beak, the honeycomb root, slots, dot). The finding
that drove it: Gen 11's innermost reach was ~9 mm *behind* its point (x −27.17 at z ≈ 98 vs −26.63
at the point), so closed it would have met mid-jaw, not at the tip.

- **The point leads.** `closed_jaw()` in `trace_photo.py` moves the beak's point in by 0.54 mm to the
  jaw's innermost reach, blending both edges over the last 45% of the beak. That also hooks the beak
  slightly toward the other finger.
- **The jaw backs off along the photo's curve.** The inner edge is x_c + g(d)/2 up to 21 mm behind the
  contact, blending into Gen 11's shoulder by 26 mm, and never comes inside that curve. The contact is
  measured 1.8 mm behind the traced point (`ROUND_BACK`), where the rounded point meets the jaw. The pivots sit at
  ±27.1655 mm so the points touch at angle 0 (`tip_gap = 0`; Gen 11 left 1 mm).
- **Serration** along the whole inner edge, from the head corner to 3 mm short of the point
  (`RIDGE_STOP_PX`), so the contact stretch is smooth: 0.4 mm deep, 0.5 mm wide, 1 mm pitch, across
  the full thickness (Gen 12's shallow grooves; 99 grooves). Each keeps 0.6 mm of wall to every hole.
- **Beak** in side view as Gen 11 (thins along 1 − f² to 1.6 mm at the point).
- **Open pose**: the same closed fingers swung about each pivot (`angle`, 0–30°).

## Build-review rounds

A separate reviewer agent judged each round against the closed photo (`previews/compare_closed.png`).

| Round | What changed | Score |
|---|---|---|
| r1 | Point leads, jaw on the photo's gap curve to 18 mm, grooves to ~1.5 mm from the point | 7/10, no: gap opened too fast 19–24 mm back; grooves too close to the point |
| r2 | Curve followed to 21 mm (1.10 mm gap at 20 mm vs photo 1.14); grooves stop 3 mm short | 8.5/10, yes |

Not taken: the reviewer's optional idea of staggering the two fingers' grooves by half a pitch. The
fingers are exact mirrors, so it would make them two different parts.
The small V past the contact (the two rounded points) is kept; the photo's tips also split there.

## Checks

- `python3 check_geometry.py`:
  - no collision from 1 to 30°;
  - at 0° the fingers touch with no overlap;
  - pushed 0.02 mm together they overlap (positive control), and **only in the last ~6 mm** — the
    contact is the point, not the jaw;
  - the model's closed gap follows the photo's curve within 0.053 mm from 3 to 20 mm back
    (tolerance 0.12 mm) and never closes again.
- `python3 genus.py`: the right finger has exactly the designed 33 through-holes.
- `python3 export_models.py`: STLs (watertight, one body each), `viewer_parts.json`, `previews/`.
- `python3 compare_closed.py` → `previews/compare_closed.png`: closed photo | model closed | points up
  close | gap, photo vs model.
- Order: `trace_closed.py` → `trace_photo.py` → `export_models.py` → `genus.py` → `check_geometry.py`
  → `photo_match.py` → `compare_closed.py`.

## Limits

The closed gap comes from one blurred ~380 px perspective photo; below ~0.1 mm it is an estimate from
seam darkness, not something the photo resolves. Over the last ~5 mm the gap is under 0.01 mm, so a
printed pair will meet along that short stretch, not at a mathematical point. Plan-view scale is
assumed (0.2 mm/px) as in Gens 7–12; no real part was measured, and there is no mount, drive or spring.
In the gallery the open/close slider uses `cad/mobile_gallery/poses.js` with the pivot at ±27.1655 mm.
