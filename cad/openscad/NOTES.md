# OpenSCAD — CAD bake-off, tool 1 of 3

Rebuilding the SO-101 gripper (fixed jaw + moving jaw) parametrically, as a
baseline for comparing three open-source CAD tools. Reading:
[`plans/gripper_bet.md`](../../plans/gripper_bet.md) for why the end effector is
the argument, and [`plans/hand_1_0.md`](../../plans/hand_1_0.md) — §6 of which
already picked OpenSCAD as the source of truth for printable parts and asked for
one shared params file. This is the test of that decision.

**Verdict up front: for this part, the "no B-rep, no fillets, no STEP" limitation
never bit once. Not a hedge — see §4.** The thing that nearly sank the run was
something else entirely, and it is in §3.

---

## What's here

| file | what it is |
|---|---|
| `params.scad` | every dimension, as a named variable, tagged `[STEP]` / `[DERIVED]` / `[GUESS]`, plus the self-checks |
| `common.scad` | two helpers: a rounded rect, and a loft-by-hulling-neighbours |
| `moving_jaw.scad` | the moving jaw |
| `fixed_jaw.scad` | the wrist roll follower — gripper body + fixed jaw, one piece |
| `gripper.scad` | **open this one.** the assembly, with `jaw_opening` in mm |
| `build.sh` | regenerates every STL and PNG below |
| `tools/measure_step.py` | reads dimensions out of a STEP file. stdlib only, no deps |
| `tools/compare_to_step.py` | overlays the rebuild on the reference (needs `cadquery-ocp`) |
| `render/`, `export/` | build outputs. never hand-edit, just re-run `build.sh` |
| `crow/` | a different pair of jaws on this same body and fork: a New Caledonian crow's beak. See [`crow/README.md`](crow/README.md) |

```bash
./build.sh                       # STLs + PNGs
openscad gripper.scad            # or just open it
openscad -D 'jaw_opening=30' -D 'part="assembly"' -o open.stl gripper.scad
```

`render/fidelity_check.png` is the honest picture: reference STEP in blue, this
rebuild in red, same frame, three projections.

---

## 1. Time

**About 15 minutes of wall clock**, start to finish, measured from the session
directory's timestamp — but read that as *agent* minutes, not human minutes. The
number that transfers to the other two tools in this bake-off is the **ratio**,
not the total:

| phase | share | note |
|---|---|---|
| reading the two STEP files well enough to model from | **~55%** | the whole job, basically |
| writing the OpenSCAD | ~20% | 591 lines across five files |
| compile / render / export / fix | ~25% | OpenSCAD itself never took more than 0.3 s |

More than half the run went into *reading a file format OpenSCAD cannot open*.
That split is the single most important number in this document, and §3 is about
it.

## 2. What was easy

- **The language is small enough to hold in your head.** `difference`, `union`,
  `hull`, `linear_extrude`, `translate`. There is no API to look up, no document
  object, no selector syntax for "the edge I want to fillet". I wrote 562 lines
  without consulting a reference once.
- **`hull()` between thin wafers is a loft, and it is free.** Both jaws are
  tapered blades with stepped gripping faces. `loft_y()` in `common.scad` is six
  lines and turns a list of measured cross-sections into a solid. Better still,
  a *repeated* station with different values reads as a step rather than a
  blend, so the gripping-face staircase — the actual functional feature of this
  gripper — came out of the same mechanism as the taper, with no special case.
- **Parametric is the default, not an achievement.** There is no history tree to
  break, so there is nothing to *do* to stay parametric. `mj_blade_profile` is a
  list of `[y, half_height]` pairs; edit a row and the blade changes. That is the
  whole mechanism.
- **The compile loop is instant.** Full CGAL render of the assembly: 0.29 s.
  That matters more than it sounds — I ran it dozens of times.
- **Text in git.** `git diff` on a dimension change is one line. This is the
  argument `plans/hand_1_0.md` §6 makes and it holds up.

## 3. What was painful — and it wasn't OpenSCAD

**OpenSCAD cannot read STEP, and that turned out to be the expensive part of the
run.** The dimensional source of truth is two AP214 STEP files, and the only
thing OpenSCAD can do with them is nothing. So before any modelling could start
I had to build my own instrument: `tools/measure_step.py`, which parses the
STEP text and prints every planar face as a normal-plus-offset and every
cylindrical face as a radius-plus-axis. That is genuinely enough to measure a
part — a plane at `n=(1,0,0) off=-8.3` *is* the gripping face — but it is a
dimension list, not a shape, and turning a dimension list into an understanding
of the shape is slow and error-prone. Two thirds of this run went there.

I also fell back to a throwaway OpenCascade script for cross-sections and face
areas, because "which of these forty planes is the big one" is a question the
text alone won't answer. `tools/compare_to_step.py` is the cleaned-up remnant of
that, and it needs `cadquery-ocp` — the exact dependency OpenSCAD's "one
self-contained file" story is supposed to spare you.

**So the real cost of the mesh-only world is not the output, it is the input.**
build123d and CadQuery both sit on OpenCascade: they can import these STEP files
and interrogate them directly, and they would have started modelling roughly 45
minutes before I did. On a part with an existing STEP, that is the whole
comparison. If the other two tools in this bake-off report a much shorter read
phase, believe them, and note that the gap closes to zero on a part drawn from
scratch.

Smaller pains, for completeness:

- **No named geometry.** You cannot say "fillet that edge" or "the face at
  x=-8.3". Everything is addressed by coordinates you compute yourself. This is
  fine while your coordinates are right and unforgiving when they are not.
- **Debugging a boolean is visual only.** A misplaced `difference()` shows up as
  a hole in a render, not an error. There is no assertion I can write that says
  "this wall should be 3 mm thick".
- **List-comprehension gymnastics.** Straddling a step in the gripping face
  needs two stations at nearly the same coordinate. Building that list is
  awkward in a language with no mutable state; I ended up writing the fixed
  jaw's station list out by hand rather than generating it.

## 4. Did the known limitation actually bite? No — and here is the real verdict

The brief asked whether mesh-only output, no true fillets, and no STEP export
are a real problem **on this part**. Straight answer, feature by feature:

- **No B-rep: didn't matter.** Nothing downstream of this file wants a B-rep. The
  part is 3D printed; the slicer wants a mesh. The only consumer that would want
  B-rep is another CAD tool, and the decision in `plans/hand_1_0.md` §6 is that
  there isn't one.
- **No true fillets: didn't matter, and I was surprised.** I expected this to be
  the sore point. It wasn't, because this part's rounding is almost entirely
  *2D* — rounded cross-sections swept along a blade — and `offset(r=)` on a 2D
  profile does that natively and exactly. The reference part's only real 3D
  fillets are three tori of R3 at the fingertip and six R1 rounds on the moving
  jaw. `hull()` between a rounded wafer and a smaller one at the tip reproduces
  the visible result closely enough that it does not show in
  `render/fidelity_check.png`. **Where it would bite is a different shape: a
  variable-radius blend, or a fillet on an intersection curve between two
  curved surfaces.** Neither appears here.
- **No STEP export: didn't matter for output, mattered enormously for input.**
  See §3. This is the one that is real, and it is the *import* direction, which
  is not how the limitation is usually stated.

**So: not a blocker for Hand 1.0's parts, and the `plans/hand_1_0.md` §6 decision
stands — but the caveat in that section is aimed at the wrong half of the
problem.** It says to keep build123d as the escape hatch "if fillets or precise
fits become the blocker." On the evidence here, the thing to watch is whether
you are *reading* existing CAD. Hand 1.0's adapter plate has to mate with the
SO-101 wrist, and if that geometry ever arrives as a STEP file rather than as
seven caliper measurements, this toolchain pays the §3 tax every time.

The claimed upside is real, with one asterisk. `gripper.scad` plus its four
includes is 562 lines of plain text with no dependency beyond OpenSCAD itself.
The asterisk is that `tools/` is where the dependencies went to hide.

## 5. Modifying this in six months

Good, with one caveat I'd fix now rather than later.

**Good, because the file says what it means.** `params.scad` is not a dump of
constants — every number carries where it came from. Six months from now the
question is never "why is this 8.3?" but "is `mj_face_steps` still what I want?",
which is a design question, not an archaeology question. The variables the brief
asked for are all first-class and all in one place: jaw length
(`mj_blade_len`, `fj_top_z`), jaw opening (`jaw_opening`, in millimetres at the
fingertip, converted to a pivot angle for you), fingertip thickness
(`mj_tip_thickness`, `fj_tip_thickness`), servo horn bore
(`horn_centre_bore_d`, `horn_recess_d`), fasteners (`m3_*` — change `m3_clear_d`
and every hole in both parts follows), wall thickness
(`mj_plate_t_top`, `mj_plate_t_bottom`, and the pocket/boss pair that sets the
cradle wall).

**Good, because the interesting edits are list edits.** Hand 1.0 keeps this
part's wrist_roll horn interface and servo cradle and throws the jaws away —
that is exactly `mj_blade_profile`, `mj_face_steps` and `fj_face_steps`, three
lists. Swapping the SO-101's stepped jaw for the wide TPU-padded parallel
fingertip `plans/hand_1_0.md` §2 asks for is editing rows, not re-drawing.

**Half-fixed: the model now checks itself, but only partly.** The bottom of
`params.scad` asserts the relationships an edit must not break — the fork has to
stay wider than the boss it straddles, the fingertip pads have to still meet at
`jaw_opening = 0`, the staircases have to climb toward the tip, the servo pocket
has to leave a wall. A bad parameter now stops the render with a message instead
of quietly producing a part that cannot be assembled. That compile also echoes
`wall thickness above the fork line: 1.682 mm`, which is open question (2) in §6
reporting itself on every build rather than sitting in a document.

**Still missing: an interference test.** Nothing checks that the two jaws stay
out of each other through the stroke. `intersection()` of the two parts at
several openings should be empty and isn't asserted — and at `jaw_opening_max`
it currently isn't empty (see §6, item 5). That is the next thing to write.

*(Written since: `crow/` — a crow-beak jaw pair on this same body and fork — has
both halves of that test. `crow/crow_params.scad` asserts it in closed form, and
`crow/check_interference.sh` sweeps the stroke and reports the overlap volume.
Neither has been back-ported to these jaws.)*

## 6. State plainly: what is approximate, and what still needs verifying

**Measured, and I'd build to it.** Every `[STEP]`-tagged number in
`params.scad`. Both horn bolt patterns (4 × Ø3.2 on a 9.9 mm square, Ø14 bolt
circle, with the counterbores). The wrist_roll interface at the base
(Ø24 × 6 recess, Ø5.4 centre, Ø6 × 6 counterbores). Both gripping-face
staircases, step by step. Both blade tapers. The fork's 48 mm outer / 36.4 mm
inner. The overall envelopes.

**Derived, and I believe it, but it is inference.** *The assembly transform.*
The two STEP files are separate solids in separate frames — the export carries
no assembly — so `jaw_pivot_x = 4.4` / `jaw_pivot_z = 23.375` was solved, not
read. The evidence: with that transform the moving jaw's last step (face
x=−12.3, spanning y −72…−82) lands exactly on the fixed jaw's last step (face
x=−7.9, spanning z 95.375…104.4) — same plane, same 10 mm run, and both
fingertips at z=105.375. Four numbers agreeing at once is strong, and it means
`jaw_opening = 0` is the real closed position with the pads touching. But it is
still the one load-bearing inference in the file.

**Approximated on purpose — the cosmetic shell.** The reference body has organic
swept corners that I replaced with hulled rounded rectangles. Visible in
`render/fidelity_check.png` as red-outside-blue at the front-right corner, and
as a missing ear at y≈27.8. Nothing functional is there, but nothing is exact
there either.

**Not modelled at all.** The "W" notch between the top two bolt holes on the
moving jaw's fork plates. The chamfers on the neck's outer faces (the reference
tapers from 48 mm to ~43 mm; mine tapers, but on a straight line rather than the
reference's two-plane blend). The hairline split faces on both blades — those
are artifacts of how the original was modelled, ~0.2 mm wide, and correctly
ignored.

**Genuinely unresolved — needs the physical part or a better look:**

1. **A 1.3 mm slot at mid-height on the moving jaw's back face**, running most of
   the blade's length, roughly 11 mm deep. It is real geometry, not an artifact.
   I do not know what it is for and did not model it. If it is structural or a
   pad retainer, this rebuild is wrong there.
2. **The side walls come out ~1.5 mm thick above `fj_fork_clear_z`.** That falls
   out of a measured pocket half-width of 16.0 and a measured boss face at 17.5.
   1.5 mm is thinner than I'd expect for a servo cradle, so either my pocket
   width or my fork-clearance height is off by a couple of millimetres. Calipers
   settle it in thirty seconds.
3. **`fj_fork_clear_z = 14.0` is a guess.** It is the height at which the body
   steps in so the jaw fork can sweep over it. I inferred it from the fork's
   travel, not from a face.
4. **The gripper servo itself is not modelled and its exact pocket is unconfirmed.**
   I never positively identified an STS3215-shaped cavity in the follower; I
   modelled the cradle as a C-section open toward +X, which matches the
   cross-sections but is not proof.
5. **`jaw_opening_max = 55` is invented.** Real travel is set by the servo's
   calibrated range, not by the plastic — `plans/hand_1_0.md` records
   1594–3018 ticks for `gripper.pos` today. At 55 mm the jaw's hub clips the
   cable tab in `render/gripper_open.png`, which is either a real limit worth
   knowing or an artifact of guess (3). Do not trust this number.
6. **Nothing here has been printed or measured against hardware.** Every number
   traces to a STEP file, and the STEP file is not the arm on the bench.
