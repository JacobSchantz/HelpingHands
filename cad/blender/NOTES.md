# Blender, as a CAD tool for the SO-101 gripper — a working log

Third of three entries in the CAD bake-off (`cad/openscad/`, `cad/build123d/`,
`cad/blender/`). Same brief for all three: rebuild the SO-101 gripper — the
fixed jaw (`Wrist_Roll_Follower_SO101.step`) and the moving jaw
(`Moving_Jaw_SO101.step`) — in a form that stays editable, because this is the
part that becomes the Hand 1.0 paper gripper (`plans/hand_1_0.md` §2;
`plans/gripper_bet.md` says Hand 1.0 is the baseline the whole bet is measured
against, so the baseline had better be modifiable).

## What's here

| file | what it is |
|---|---|
| `so101_gripper.py` | **the source.** A `bpy` script with a ~60-entry `P` parameter block at the top. Re-running it regenerates everything below. |
| `build.sh` | `./cad/blender/build.sh` — the one command that rebuilds `out/`. |
| `measure_step.py` | dependency-free ISO-10303-21 reader; prints radii, plane offsets, fillet radii straight out of the STEP text. |
| `measure_step_ocp.py` | the same via OCCT, adding per-face areas, volumes and exact bounding boxes. |
| `MEASUREMENTS.md` | every parameter, its value, and the STEP entity it was read from. |
| `out/*.png`, `out/*.stl`, `out/so101_gripper.blend` | build artifacts. Never hand-edit them; change a parameter and rebuild. |

Everything in `out/` was produced headlessly:

```sh
./cad/blender/build.sh
./cad/blender/build.sh --set jaw_open_deg=0 --set mj_finger_length=110
```

`cad/build123d/reference/` was opened read-only and is unmodified.

## Time

About two and a half hours. The split is the interesting part:

- **~15 minutes** writing the parametric model once I knew the numbers.
- **~25 minutes** on render/export/assembly plumbing.
- **everything else — well over half the session — was measurement and
  reverse-engineering**, and most of that was trying to work out how the two
  parts actually go together.

That ratio is the honest headline. Modelling was never the bottleneck.

## What was easy

- **Tables and loops.** Both fingers taper. In `P` that's a literal list of
  `(station, width)` pairs read straight off the reference, interpolated at
  build time. Adding a station is one line; there is no sketch to re-solve and
  nothing downstream to repair.
- **Booleans.** Blender's EXACT boolean solver did not fail once across ~40
  cut/union operations, including four-hole bolt patterns through curved walls.
- **Rendering and looking at things.** This is the real one. When I needed to
  know whether my assembly hypothesis was right, I imported the tessellated
  reference, placed it under a candidate transform, and *looked*. Three renders
  and about forty seconds told me more than another hour of reading STEP
  entities would have.
- **Scripted measurement.** Ray-casting the reference mesh to print ASCII
  cross-sections (`#` = solid) is four lines of `bpy` and is how I found the
  Ø10 bore through the fin root and proved the servo cradle is hollow.

## What was painful

- **No STEP import.** Blender simply cannot open the reference files, and no
  OCCT binding ships with it. I ended up installing `cadquery-ocp` into a
  throwaway venv purely to *read* the references — so the honest statement is
  that this Blender model was only possible because a real CAD kernel was
  available alongside it. A `.venv/` next to a `.blend` is a smell.
- **No fillets, no chamfers, no shell — only modifiers that approximate them.**
  `edge_break = 0.75` is a Bevel modifier with an angle limit, not a fillet. It
  cannot be applied to one selected edge, it cannot be a variable radius, and on
  a 48-segment cylinder it produces visible shading facets. For the bolt-head
  counterbores and bearing seats this part is full of, that is a real
  limitation, not a cosmetic one.
- **No constraints and no datums.** "The fingertips touch when the jaw is
  closed" is not something you can state; it is arithmetic I had to do by hand
  and hard-code as `mj_closed_lean_deg = 8.84`. Change `mj_finger_length` and
  that number is silently wrong. In build123d or OpenSCAD I'd at least compute
  it in the same expression language as the geometry; here it lives in a comment
  and in `MEASUREMENTS.md`.
- **Meshes, not solids.** A 6 mm hole is a 48-sided prism. Print it and it is
  undersized by (1 − cos(π/48)) × 3 mm ≈ 6 µm — fine — but there is no STEP out,
  no way to check a press fit analytically, and no mass properties beyond what I
  compute myself.
- **`bpy` foot-guns.** `matrix_world` is stale until the depsgraph updates, so
  my first assembly fit silently discarded the placement and produced a
  plausible-looking wrong answer. `bpy.ops.*` needs the right active object.
  None of this is geometry work.

## Did "Blender isn't parametric CAD" actually matter here?

**Yes, but not where I expected.**

It did *not* matter for regeneration. The script-as-source discipline works:
every artifact in `out/` is reproducible from `P`, and `--set` overrides mean I
can sweep a parameter without touching the file. On that narrow test Blender
passes.

It mattered for **intent**. A parametric CAD model records *why* a face is where
it is — "coincident with that plane", "tangent to that arc", "10 mm from the
pivot". This script records only *where*. The measured relationships that make
the part work (grip face 5 mm outboard of the insert holes; fingertips meeting;
horn pocket concentric with the bore) are true by arithmetic I performed once,
not by construction. Six months from now the geometry will still regenerate, and
it will still be my job to notice when a change has quietly broken one of them.

It also mattered for **inspection**. I spent an hour trying to establish which
face of the fixed fin is the gripping face. In a B-rep tool that is a click. Here
it was plane-offset arithmetic and ASCII cross-sections, and I did not fully
settle it (see below).

## Where Blender genuinely wins

Worth saying plainly, because the above reads one-sided:

- **Visualisation is not a side benefit here, it is the debugging tool.** The
  assembly transform is not in either STEP file — they are two isolated part
  files in unrelated poses. I recovered a workable one by rendering candidate
  placements and judging them by eye. No other tool in this bake-off would have
  made that loop as fast.
- **Renders for the plan documents.** `out/so101_gripper.png` is a decent
  figure, produced headlessly in under two seconds with no lighting rig — the
  Workbench engine with cavity shading is a genuinely good free CAD renderer.
- **The Tool Caddy scene already lives in Blender** (`plans/tool-caddy.blend`).
  Showing the gripper handing a drill to a person — the capability argument in
  `plans/gripper_bet.md` §4 — means putting the gripper into that scene, and
  this script can append into it directly with no import step and no unit
  conversion.
- **Everything is scriptable in one language.** Measure, model, assemble,
  animate the jaw through its travel, render, export — all `bpy`, all in one
  file. The jaw-opening animation that would sell the Hand 1.0 design is
  maybe fifteen more lines.

`plans/hand_1_0.md` §6 already draws the line — "nothing printable should
originate" in Blender — and after this exercise I think that line is right, with
one amendment: Blender is the best of the three for *understanding* a part you
did not author.

## Six months from now

Changing a **dimension** would be easy. `jaw_open_deg`, `mj_finger_length`,
`fingertip_thickness`, the bolt pattern, the wall thickness — those are one-line
edits with an obvious blast radius, and `build.sh` tells you in seconds whether
it still builds.

Changing the **shape** would be hard. Adding the parallelogram linkage that
`plans/hand_1_0.md` §2 wants, or a TPU pad pocket with a lip, means writing new
loft/boolean code, not sketching. And there is no solver to catch you: nothing
warns that a longer finger has walked the fingertips past each other.

The thing that will age worst is the pile of **derived constants**
(`mj_closed_lean_deg`, `fin_pivot_to_face`, `fin_tip_s`). They are consequences
of other parameters, computed by hand, frozen as numbers. First job for anyone
picking this up: turn them into expressions.

## What is approximate, and what still needs verifying

Stated plainly, because some of it matters.

**Verified.** Both parts match the reference bounding boxes to about 0.1 mm —
fixed jaw 65.20 × 52.00 × 105.35 (reference 65.200 × 52.000 × 105.425), moving
jaw 22.36 × 92.00 × 48.00 (reference 22.300 × 92.000 × 48.000). Every hole
diameter, bolt pattern, pocket depth, plate thickness and face angle is a number
read out of the STEP.

**Approximate by choice.**

1. **Organic blends are gone.** The reference parts carry 26 and 34 B-spline
   faces — the sculpted transitions from hub to finger and the curved back of
   the fin. My version uses straight tapers between measured stations, so the
   silhouette is right and the surface is faceted where the original is smooth.
   Visible as a shoulder at the moving jaw's root.
2. **The 10 mm-pitch stepped faces are not modelled.** Both reference parts have
   a staircase of ±45° faces at exactly 10.0 mm pitch along the finger, opposite
   the flat face. I measured them but left them out.
3. **The servo cradle is a plain U.** Real internal ribs, cable channels and
   the exact servo pocket were not reproduced; the walls are at the measured
   ±16.0 mm with the measured 2.2 mm thickness and the measured M2 hole pattern,
   and nothing more.
4. **The wrist-roll interface is modelled as a Ø24 × 6 pocket** with 4 × M3 on
   a 14 mm PCD and a Ø5.4 central bore. The reference's bottom face is at
   z = −0.05, so a pocket is the reading that fits; a protruding spigot is not.

**Needs verifying — and this is the one that matters.**

**I could not determine, from the two files alone, which face of each finger is
the gripping face, and therefore how the jaws truly close.** The evidence cuts
both ways and I want the next person to see it rather than inherit my guess:

- Each part has one large flat face (642 mm² on the fin, 656 mm² on the moving
  jaw) with a line of five Ø1.5 mm holes exactly 5.0 mm in from it. That reads
  like a pad-retention pattern, which argues the flat face is the gripping face.
- Each part *also* has, on the opposite side, a staircase of faces at exactly
  the same 10.0 mm pitch as those holes. Serrations facing the workpiece is the
  classic gripper jaw, which argues the other way.

I took the **flat faces** as the gripping faces. The consequence is visible in
`out/so101_gripper_closed.png`: at `jaw_open_deg = 0` the fingertips meet
correctly, but the two fingers overlap towards the root, because the flat face
sits 10.06 mm from the moving jaw's pivot and about 26 mm from the fixed jaw's.
Those two numbers cannot both be right for a jaw that closes flush. Either the
pivot is further outboard than I placed it, or the stepped faces are the
gripping faces and the moving jaw swings on the other side of the fin.

Also unverified:

- **The assembly transform is fitted, not read.** Two isolated part files carry
  no relative pose. I fixed the pivot at z = 24.35 (the midplane of the servo's
  own M2 holes) and y = −0.218 (the wrist-roll centreline) — both measured — and
  then *chose* `pivot_x = −25.54` so the fingertips meet. A ±3 mm error there
  changes nothing about either part and everything about the closed pose.
- **The gripper servo is not modelled**, so nothing checks that it fits the
  cradle or that the moving jaw's 33.4 mm fork clears it. It does not clear the
  body as placed.
- **`fin_width_table` is sampled, not analytic** — Y extents of the tessellated
  reference in 5 mm Z bands. Good to a few tenths, no better.
- **Jaw travel is not bounded.** `plans/hand_1_0.md` records the gripper servo
  calibrated to 1594–3018 of 4096 ticks; nothing here maps `jaw_open_deg` to
  ticks, and that mapping is invalidated by any change to these parts anyway.

**One measurement would settle most of this:** put a rule on the assembled arm
and record where the gripper servo's output axis sits relative to the fixed
jaw's face. That is measurement #3 and #4 on the list in `plans/hand_1_0.md` §1,
which is already waiting on the physical arm.
