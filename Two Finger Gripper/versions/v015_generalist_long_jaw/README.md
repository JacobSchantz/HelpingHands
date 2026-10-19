# Generalist Gripper · Generation 15: the long jaw

Gen 14 with a longer beak (voice-8673a6b6). Jake: *"that thick end section should be quite a bit longer, about a third of
the total finger length"*, checked against the reference photos. This replaces the old printable Gen 15, which was
deleted (it is in git at `97850a1`; Gen 16 was built from it and stands alone). Gen 14 is unchanged.

## What changed

- **The beak past the black dot is 1.7× longer** (`trace_photo.py BEAK_STRETCH`). Dot → point goes from **24.8 mm (23 %)** to
  **42.2 mm (33 %)** of the finger. The finger grows from 109.4 to 126.8 mm. In the closed photo
  (`cad/reference/generalist_gripper_gen6_closed.png`) the dots-to-point section reads ~38 % of the finger, so Gen 14's was
  short.
- The point keeps Gen 14's x, so the beak gets longer, not wider. At each fraction of its length it has Gen 14's width, which
  makes it slimmer per mm. The six slots keep their fraction of the beak's length and width (`beak_slots()`).
- Everything behind the dot is Gen 14's: the arm, root, honeycomb, shoulder bump and the dot itself.
- The contact spec is Gen 14's: only the points touch, the jaws open in a V behind them, then follow the photo's gap curve.
  Two values were re-tuned for the slimmer point:
  - `ROUND_BACK` 0.4 → 1.0 mm. The 0.3 mm point round now takes ~1 mm off the length, measured on the mesh.
  - The V is now 4.5° per side to a 0.40 mm gap (Gen 14: 4° to 0.35 mm). With the model on target, Gen 14's values only
    give 5.7° included 1–2 mm back. Gen 14's model read 6.6° only because it met ~0.6 mm behind its designed contact.
- The pivots are at **±27.251 mm** (Gen 14: ±27.137), in `cad/mobile_gallery/poses.js`.

`previews/compare_gen14.png` shows Gen 14 and Gen 15 closed at the same scale. Red marks the dot, blue the point.

## Checks (all pass)

- `python3 check_geometry.py`:
  - no collision from 1 to 30°;
  - at 0° the fingers touch with no overlap;
  - pushed 0.02 mm together they overlap only at the point (z 123.22–123.43);
  - the closed gap is within 0.003 mm of target from 1 to 20 mm back;
  - 6.4° included 1–2 mm behind the point;
  - body + pad = the whole finger.
  The gap is now measured by slicing the mesh at each z. Vertices are ~0.9 mm apart along the longer beak, so Gen 14's
  vertex window missed rows.
- `python3 genus.py`: 33 through-holes, as designed.
- `python3 export_models.py`: every STL is one watertight body.
- `python3 compare_gen14.py` → `previews/compare_gen14.png`.
- Order: `trace_photo.py` → `export_models.py` → `genus.py` → `check_geometry.py` → `compare_gen14.py`.
  `photo_match.py` and `compare_closed.py` still run. They now show the longer beak running past the two-hands trace on purpose.

## Limits

- 1.7× is set from the one-third target, not measured. No photo gives a true scale, and the closed photo is foreshortened.
- The two-hands photo (Gen 11's trace source) shows a shorter beak than this. Gen 15 departs from it on purpose.
- Nothing is printed. A longer, slimmer beak bends more under the same tip force; no stiffness check is done.
- No three.js concept: the web-vs-STL compare (`cad/compare`, `Scripts/render_compare`) only covers `cad/openscad/<family>/gen_NN`
  designs, and no Two Finger Gripper generation has one. The gallery's three.js viewer draws these STLs directly.
