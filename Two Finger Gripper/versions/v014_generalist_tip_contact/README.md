# Generalist Gripper · Generation 14: only the points touch

A refinement pass on Gen 13 (voice-fe67959c). The item asked for GPT-6 Astra; that model wasn't
available, so Claude Opus 5.5 built it. Jake on Gen 13: *"just the tip contacts. I think there's a little
too much contact leading up to the tip, maybe not quite a tight, sharp enough contact angle"*, and *"from
the photos, see if there's anything that can be improved ... for example, the tips."* Primary reference:
`cad/reference/generalist_gripper_gen6_closed.png`. Gen 13 is unchanged.

Everything is still Gen 13's: designed closed from the closed photo, the closed trace and sketch
(`trace_closed.py`, `closed_sketch.png`), Gen 11 r4's plan shape with Gen 10's fuller beak, serration
along the inner edge, side-view beak, and 33 through-holes. What changed:

## 1. The contact: a sharp V behind the point

Gen 13 followed the photo's gap curve exactly, and that curve is below 0.03 mm for the last ~6 mm. The
photo can't resolve that (~0.5 mm/px across the jaws), and the result was that Gen 13 met along a 6 mm line.
Its included angle 1–2 mm behind the point is ~0°.

`trace_photo.py closed_gap()` now targets a smooth max (power 6) of two curves:

- **the wedge**: each inner edge leaves the contact at **4°** (8° included), levelling off at a
  **0.35 mm** gap;
- **the rear**: the photo's curve **+0.1 mm**.

| mm behind the point | 1 | 2 | 4 | 6–10 | 14 | 18 | 20 |
|---|---|---|---|---|---|---|---|
| Gen 13 model gap, mm | 0.00 | 0.00 | 0.01 | 0.02–0.12 | 0.35 | 0.77 | 1.10 |
| Gen 14 model gap, mm | 0.05 | 0.17 | 0.27 | 0.29–0.30 | 0.42 | 0.85 | 1.17 |

Round 1 kept the whole wedge on, which put the jaw ~0.5 mm above the photo along its whole length. The
reviewer read that as a slit, so round 2 levels it off.

## 2. The point and the dark tip

- **Sharper point**: within 6 mm of the point the plan view is rounded at `tip_r = 0.3 mm`. Elsewhere it
  keeps Gen 13's rounding (the two meet seamlessly, since both are identity on smooth edges). Gen 13's
  ~1 mm round made two nubs with a V in front of the contact. Because the sharper round leaves the
  innermost reach 0.028 mm inside the trace (`contact_back`), the pivots are at **±27.137 mm**.
- **Dark tip pad**: the robot, top, two-hands and closed photos all show a dark nub at each point. The last
  `pad_len = 2.5 mm` is now a separate body, `tip_pad()` (dark grey), and the yellow `finger()` is
  the rest. Together they are exactly the full finger, which is checked. All contact checks run on
  `whole_finger()`. It is meant for a two-material print (yellow + dark TPU). For a single-material
  print, merge the two bodies. Each pad is small (~6.6 mm³). Round 1 used 3.5 mm, which the reviewer read
  as long.
- **Grooves** stop 3.4 mm short of the point (`RIDGE_STOP_PX = 17`), behind the pad. 99 grooves.

## Build-review rounds

A separate reviewer agent judged each round against the closed photo (`previews/compare_closed.png`).

| Round | What changed | Score |
|---|---|---|
| r1 | 4° wedge saturating at ~0.56 mm, 0.3 mm point, 3.5 mm pad | 7.5/10, ship: tips clearly better than Gen 13; the extra gap all along the jaw is a slit, and the pad is a bit long |
| r2 | wedge levels off at 0.35 mm, then photo + 0.1 mm; 2.5 mm pad | 8.5/10, ship: slit gone, tip-only contact at a sharper angle, pad matches the robot/side photos |

Not taken: the reviewer's optional 0.15 mm crown on the pad's inner face (revisit if prints meet along an
edge), and merging the two 0.3 mm point rounds into one. The fingers are separate parts, so each point
keeps its own round, with a ~0.1 mm notch between them in plan.

## Checks

- `python3 check_geometry.py` (all on body + pad):
  - no collision from 1 to 30°;
  - at 0° the fingers touch with no overlap;
  - pushed 0.02 mm together they overlap (positive control), and **only in the last 1.5 mm**. They
    meet over z 105.99–106.23, a 0.24 mm stretch at the point (Gen 13: 6 mm);
  - the included angle 1–2 mm behind the point is **≥ 6°** (6.6°);
  - the closed gap is within 0.12 mm of the target from 1 to 20 mm back (worst 0.08), and never closes
    again;
  - body + pad = the whole finger, and they don't overlap.
- `python3 genus.py`: the right finger body has exactly the designed 33 through-holes.
- `python3 export_models.py`: STLs for both bodies and both pads (watertight, one body each),
  `viewer_parts.json`, and `previews/` (`tip.png` is new: the last ~14 mm, closed).
- `python3 compare_closed.py` → `previews/compare_closed.png`: closed photo | model closed | Gen 13's
  points | Gen 14's points (same camera) | gap: photo, Gen 13, Gen 14 target and model.
- Order: `trace_photo.py` → `export_models.py` → `genus.py` → `check_geometry.py` → `photo_match.py`
  → `compare_closed.py`. `trace_closed.py` and `closed_trace.json` are Gen 13's and unchanged.

## Limits

- The 4° angle and the 0.35 / 0.1 mm values are design choices made from Jake's note, not measurements.
  The photo can't resolve a gap this small.
- The tip pad is a reading of a dark nub in blurred photos. Its real material, length and joint are not
  known, and nothing holds it on except a two-material print or glue.
- The model's actual contact sits ~0.45 mm behind the designed one (`ROUND_BACK`), so the model's gap
  curve trails the target by about that much.
- Plan-view scale is still assumed (0.2 mm/px) as in Gens 7–13. There is no mount, drive or spring.
  In the gallery, the open/close slider uses `cad/mobile_gallery/poses.js` with the pivot at ±27.137 mm.
