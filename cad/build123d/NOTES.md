# build123d — CAD bake-off, tool 2 of 3

The task was to recreate the SO-101 gripper (the moving jaw and the wrist-roll
follower that carries the fixed jaw) parametrically, from the reference STEP
files, and then say honestly how the tool felt. The geometry is the exercise;
**the verdict is the deliverable.** Context: `plans/gripper_bet.md` (why a
gripper at all) and `plans/hand_1_0.md` §6 (which provisionally picks OpenSCAD
and names build123d as "the escape hatch if fillets or precise fits become the
blocker"). This is that escape hatch, tried on a real part.

## Verdict in one paragraph

build123d earns its dependency. It was the only tool in this bake-off that
could read the reference as **analytic B-rep** and measure it — exact cylinder
radii, exact plane normals, not numbers eyeballed off a mesh — which meant not
one dimension in `params.py` is invented. It exports STEP, it does real
fillets, and because the model and the reference live in the same kernel I can
*score* the model against the original instead of comparing renders by eye
(`FIDELITY.md`: both parts within 3% by volume, every bounding box within
0.2 mm, worst silhouette error on the moving jaw **0.27 mm**). Against that:
OCCT is a hostile runtime. A fillet that does not fit does not raise — it
**segfaults the process**, taking the whole model with it and leaving no
traceback. `is_valid` returned `True` on a solid whose volume was −1.7 × 10¹¹.
Those are not paper cuts; they are the reason an agent working unattended needs
a guard rail around every fillet call. **My recommendation: build123d for the
printable parts, on the condition that every model keeps a fidelity or sanity
check that runs on each build.** Without that check the failures are silent,
and silent is much worse than loud.

## Time

**21 minutes** of agent wall-clock from claim to working geometry (12:54Z →
13:15Z). That number flatters the tool and is worth breaking down, because most
of it was not spent writing build123d:

| | share |
|---|---|
| reverse-engineering the reference (what *is* this shape?) | ~45% |
| writing the parametric model | ~25% |
| fighting OCCT failure modes | ~20% |
| measuring, reporting, writing this file | ~10% |

The reverse-engineering time would be the same in any tool. The 20% lost to
OCCT would not.

## What was easy

**Reading the reference.** `import_step()` loads either file in 0.19 s and
hands back a real solid. From there every dimension is a query:

```python
cyl = BRepAdaptor_Surface(face.wrapped).Cylinder()
cyl.Radius()          # 2.7000000000000  — not 2.6983 off a triangle soup
cyl.Axis().Location() # the exact centre the original author typed
```

That is how `measure_reference.py` produced `MEASUREMENTS.md`, and every
`[STEP]`-tagged number in `params.py` came out of it. The M3 clearance holes
are Ø3.2 because the file says Ø3.2. The horn bolt square is 9.9 mm because the
four cylinder axes sit at (±4.95, ±4.95). Nothing was eyeballed.

**Sectioning as a measuring instrument.** `solid & Plane(...)` gives a real
cross-section, so a tapering blade could be measured station by station and
then rebuilt by lofting through those same stations. The blade taper turned out
to be *convex*, not straight — a two-point taper would have been ~0.4 mm out in
the middle — and that was visible in thirty seconds because the sections are
numbers.

**Lofting.** Both blades are `loft()` through measured rounded-rectangle
sections, one segment per step of the gripping face. That maps almost exactly
onto how the original was drawn, and it means the station tables in `params.py`
*are* the silhouette: edit a row, the shape follows.

**Scoring the result.** `fidelity_check.py` compares model and reference by
volume, by bounding box, by cross-section area at every station, and by
matching up bores (diameter + axis + position). This is the thing I would most
want on the next part, and it is only possible because both shapes are solids
in one kernel.

## What was painful

Ranked by how much damage each can do to an agent working alone.

**1. OCCT aborts the process instead of raising.** `fillet(edges, radius=5.0)`
first raised `BRep_API: command not done`; retrying at 1.0 exited with **signal
139**. No exception, no traceback, no partial model. In a long unattended run
that is a dead worker, and the only clue is the exit code.

**2. `is_valid` is not a validity check.** Lofting the moving jaw's blade all
the way to its real 0.8 mm-half-height tip produced a solid that reported
`is_valid == True` and `volume == -166_502_371_762.0 mm³`. I caught it only
because I was comparing volume against the reference. Anything that trusts
`is_valid` will ship a broken part. (The committed model stops the loft 0.2 mm
short of the true tip and rounds it — see the comment on `MJ_BLADE_PROFILE`.)

**3. A "successful" fillet can leave an invalid shell, and the crash surfaces
somewhere else entirely.** A step fillet that swallowed a Ø1.5 hole 0.33 mm
away returned a solid happily; the failure appeared several steps later as a
segfault inside `project_to_viewport` (hidden-line removal). Fix: cut holes
first, fillet last. Mitigation, in `moving_jaw._fillet_where_possible()`: try a
descending list of radii and accept only a result that passes `is_valid`. Which
means **the fillet radius in this model is a wish, not a parameter** — if the
geometry cannot take 1.2 mm it quietly gets 0.5, or nothing. That is a real
limitation and it is the honest counterweight to "build123d does real fillets".

**4. Booleans against the imported reference do not work.** `model - reference`
silently returned the whole model instead of the difference — OCCT declining to
cut against the reference's 26–34 B-spline faces. So "diff my part against the
original" is not available; `fidelity_check.py` compares cross-sections
instead, which is more informative anyway but was not the first plan.

**5. Silent direction conventions.** `extrude(profile, amount=+n)` on a
`Plane(x_dir=(0,1,0), z_dir=(1,0,0))` extruded along **−X**. The resulting cut
missed the part entirely, and the model still built, still validated, and still
looked plausible in a render. The fidelity table caught it: a cross-section
that should have been 762 mm² came out 871 mm². That is the best argument in
this document for keeping a numeric check in the build.

**6. `ExportSVG` crashed** with `assert start != end` inside `svgpathtools` on a
degenerate ellipse while projecting the moving jaw. Worked around by choosing
different view directions.

## Was the known downside — dependency footprint — real?

Partly, and not in the way I expected.

- **Disk:** the venv is **514 MB**, 219 MB of it OCCT alone. Against OpenSCAD's
  one self-contained file, that is not close.
- **Start-up:** `import build123d` costs **3.2 s** before any geometry happens.
  Every edit round-trips through that.
- **Full rebuild:** measurements + both parts + exports + drawings + fidelity =
  **86 s**. OpenSCAD's F5 preview is interactive; this is not.

But the footprint is a *one-time* cost and it is already paid — the venv was
here, `build123d 0.11.1` on OCCT 7.9.3, and I reused it without installing
anything. Over six months of edits the 514 MB never comes back; the 3.2 s
import and the 5 s rebuild do, every time. **The recurring cost is the loop
speed, not the disk.** And `edit_stress.py` says one part rebuilds in ~5 s,
which is slow next to OpenSCAD's preview but fine next to opening a GUI.

The part of the footprint that *would* worry me is version drift: OCCT is a
large C++ dependency reached through a generated binding, and the failure modes
above are all inside it. Pin the versions and treat an OCCT upgrade as a change
that needs the fidelity check re-run.

## Six months from now

I tested this rather than guessing (`edit_stress.py`, each case an edit
`plans/hand_1_0.md` §2 actually calls for):

| edit | result |
|---|---|
| blade corner radius 1.5 → 3.0 mm | ok, 4.7 s |
| gripping pad 15% wider | ok, 5.4 s |
| gripping face 2 mm closer to the fixed jaw | ok, 5.2 s |
| blade 12% longer (82 → 92 mm) | ok, 6.8 s |

All four regenerate to a valid solid. That is the answer to criterion (2), and
it is a good one — because the model is driven by measured *station tables*
rather than hard-coded profiles, the shape follows the numbers.

Two caveats I would want a future me to know. First, the fillets: a big
dimension change can push a radius past what the geometry allows, and the model
will silently fall back to a smaller one instead of telling you. Second, the
blade-to-fork flare in `MJ_ROOT_SECTIONS` is two hand-measured sections; stretch
the jaw far enough and that flare stops being right and needs re-measuring
against a new reference.

## The other three criteria

**(3) Does it live well in git?** Yes, and better than I expected.
`params.py` is a flat list of named constants — a dimension change is a
one-line diff that says what changed and why. The part files are ordinary
Python functions. A reviewer can read the whole model in a terminal. This is a
genuine tie with OpenSCAD and a rout against a binary `.blend`. The one wart is
that the *exports* are large (STEP 1.4–3.5 MB, STL 0.7–1.6 MB) and regenerate
byte-differently, so they are noise in every diff; they belong in the repo as
deliverables but should not be re-committed casually.

**(4) Can an agent author and revise it?** This is build123d's quiet advantage
and I want to be precise about why. Python is the language an agent writes most
reliably, and build123d's algebra mode (`part - hole`, `loft([...])`) is plain
imperative code — I wrote ~1,400 lines of it in this session without
consulting documentation, which I could not have claimed for OpenSCAD's CSG
idioms. Two hazards, though: the library has **two mutually incompatible
styles** (algebra and Builder) that read alike and get mixed up in examples —
this model is algebra mode throughout, deliberately — and a segfault with no
traceback is close to unrecoverable for an agent working unattended. Both are
manageable with the rule stated at the top: keep a check that runs on every
build.

**(5) Is the output usable for functional printed parts?** Yes, and this is
where it separates from OpenSCAD. Real fillets, STEP in *and* out, exact bores,
and — the thing that matters most for Hand 1.0 — a fastener or bearing seat
whose diameter is a number the kernel honours rather than a faceted
approximation. `FIT_CLEARANCE` in `params.py` is the single place a printer's
fit allowance lands.

**(6) Open source?** Apache-2.0 (build123d) on LGPL-2.1 (OpenCASCADE). Meets
the requirement.

## Where the geometry is approximate — read this before trusting it

The model is a **parametric reconstruction, not a copy.** Both parts match the
reference to within 3% by volume and 0.2 mm on every bounding box, but these
are real and deliberate departures:

1. **Cosmetic B-spline blends are not reproduced.** The originals carry 26 and
   34 B-spline faces respectively — the soft blends an injection-mould-style
   part has everywhere. My model uses lofts, arcs and fillets. This is the main
   source of the residual volume difference.
2. **The follower's servo pocket is fitted, not measured.** Its side faces are
   real (the M2 servo-screw recesses bottom out on them, at y = −16.22 and
   y = +15.78). Its back face, `WR_CAVITY_X0 = -26.0`, was **tuned until the
   model's cross-section areas matched the reference's** at z = 13, 20, 24, 32.
   The real pocket is not a plain box, and the model's is.
3. **A gusset under the follower's base plate is missing.** At z = 3 the
   reference reaches x = −16.56 and y = 21.23; the model has only the Ø24 horn
   boss there. Worst single silhouette error in the whole model, 9.5 mm.
4. **The moving jaw's tip stops 0.2 mm short** (y = −81.8 instead of −82.0) and
   is rounded, because lofting to the true tip produced the degenerate solid
   described above.
5. **The Ø10 bore through the follower** is modelled where measured
   (x −35.2 … −15 at z = 24.35) but now breaks into the fitted servo pocket
   rather than running through solid material as it does in the reference.
6. **The Ø1.5 hole pattern.** Both parts carry a row of Ø1.5 holes marching
   down the blade, alternating between "through the height" and "through the
   thickness, normal to the tapering back face". They are reproduced because
   they are there; **what they are for is not determinable from the geometry.**
   The model omits a blind one at y = −67 on the moving jaw and the
   through-thickness set on the follower's blade.
7. **The assembly mate is reasoned, not measured.** The two STEP files are
   separate solids with no assembly constraints, so nothing states how they
   fit. `JAW_PIVOT_IN_BODY` puts the pivot where the gripping faces meet when
   closed and at the height of the only feature at the right place (the Ø10
   bore). **This is probably not the whole story:** the moving jaw's fork gap
   is 36.4 mm and the follower is 48 mm wide at that height, so the fork cannot
   straddle the body. Either a third part sits between them, or my reading of
   which surfaces mate is wrong. `JAW_OPEN_DEG = 32` is a guess.

## What still needs verifying

- The assembly mate above — resolve it against the physical arm or a third
  reference file, not by staring harder at these two.
- What the Ø1.5 holes are for, before Hand 1.0 inherits them by copying.
- Whether the fitted servo pocket actually clears an STS3215, measured on the
  bench.
- Whether the fillet radii the model *actually got* are the ones intended —
  `_fillet_where_possible` degrades silently, and nothing yet reports which
  radius won.
- The printed fit: no part here has been printed. `FIT_CLEARANCE` is a guess
  until one is.

## Files

| | |
|---|---|
| `params.py` | every dimension, named, tagged `[STEP]` / `[DERIVED]` / `[FITTED]` / `[ASSUMED]` |
| `measure_reference.py` | interrogates the reference B-rep → `MEASUREMENTS.md` |
| `moving_jaw.py`, `fixed_jaw.py` | the two parts |
| `gripper.py` | assembly, STEP + STL exports, SVG/PNG drawings |
| `fidelity_check.py` | model vs. reference → `FIDELITY.md` |
| `edit_stress.py` | criterion (2) as a test |
| `build.sh` | regenerates all of the above |

`reference/*.step` is untouched. `.venv` was reused, not recreated.
