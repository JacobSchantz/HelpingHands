# Hand 1.0 — a paper-handling gripper that mounts to the arm or fits your fist

Status: DESIGN, on paper only (2026-09-13). No CAD, no code, nothing ordered.

See `plans/gripper_bet.md` for why this exists. Hand 1.0 is the conventional,
buildable foundation named there.

## What it is

One gripper unit with a camera on it, usable two ways:

1. **Arm-mounted** — bolted to the SO-101 follower's wrist, driven by the robot.
2. **Handheld** — detached, held in your fist, squeezed by a trigger.

Same body, same jaws, same camera, same servo, both modes. First target task:
**handling paper.**

## Why the two modes matter (the identity thesis at 1.0)

`plans/gripper_bet.md` argues that the real breakthrough is humans driving the
hardware, and that the sharp idea is making the demonstration instrument and the
execution instrument *the same object*. Hand 1.0 is the first cheap test of that
at the end effector:

- **No visual domain gap.** The camera that records your demonstration is the
  camera that sees at execution — same lens, same mount, same viewpoint relative
  to the fingertips. The policy never has to bridge two camera rigs.
- **No action retargeting.** If the handheld trigger is the *same servo part* as
  the gripper (see "Trigger" below), the recorded `gripper.pos` is already in the
  follower's units. Nothing is translated.

This is the Hand 2.0 identity claim in its weakest, testable form. Hand 1.0 is
also the baseline Hand 2.0 gets measured against.

## 1. Mounting to the SO-101 — what the repo pins down, and what it doesn't

**What the repo actually gives us** is the *electrical* interface, not the
mechanical one:

- Six bus servos; `gripper` is motor **ID 6** (`lerobot_calibration/follower_right.json`).
- Current gripper travel is calibrated to **1594–3018** ticks of 4096, with
  `homing_offset` −1636. New jaws change this mapping.
- `wrist_roll` (ID 5) is calibrated **0–4095 — a full unrestricted turn.**
- The scripts (`teleop.sh`, `record_actions.sh`) drive it over a single serial
  bus with `gripper.pos` as one of six joint channels.

**What the repo does not contain:** any mechanical geometry. There is no CAD, no
STL, no bolt pattern, no dimensioned drawing. `open_claw_setup.txt` is Pi/network
notes, and `plans/tool-caddy.blend` is a concept scene with no arm model in it.
So **the mounting geometry has to be measured off the physical arm**, not
inferred from this repo. Do not let anyone invent these numbers.

**Measure before drawing anything:**

| # | Measurement | Why |
|---|---|---|
| 1 | Wrist output flange: bolt count, hole Ø, pitch circle | the adapter plate's only job |
| 2 | Flange face → wrist_roll axis offset, and any locating boss Ø | keeps the jaw axis centered |
| 3 | Where the gripper servo lives — in the wrist, or driving through a linkage? | decides whether we reuse ID 6's servo or add our own |
| 4 | Servo horn spline/type and horn screw | the jaw drive coupling |
| 5 | Bus connector type and free lead length at the wrist | umbilical design |
| 6 | Payload margin at full extension, with the current gripper's mass as the datum | Hand 1.0 must not be heavier than what the arm already carries |
| 7 | Clearance swept by the jaws at wrist_flex limits | so it can still reach a tabletop |

**Design rule that falls out of this:** the *only* part that touches the arm is a
thin **adapter plate**. The gripper body bolts to the plate with our own pattern.
If the arm changes, or we build a second one for the leader, one cheap printed
plate changes and the body does not. It is also what lets the identical body be
held in a hand.

**Flagged now:** `wrist_roll` turning freely through 4096 ticks will **wind up any
cable** running to a tethered end effector. Today's gripper has no camera and no
umbilical, so this has never bitten. With a USB camera on the wrist it will.
Either software-limit wrist_roll's range, add a service loop with a hard stop, or
accept a slip ring (not printable). This is a decision Jake has to make, not a
detail.

## 2. The gripper: getting a flat sheet off a flat table

Paper is the hard case and it should be said plainly why: a sheet lying flush on
a table presents **no edge to grab**. It is ~0.1 mm thick, it is flexible so it
does not hold a shape you can plan against, it creases permanently under a point
load, and it tears. Almost every pick strategy that works on a mug fails on it.

### The crux: making an edge where there isn't one

Four ways to get a fingertip onto or under a flush sheet:

**(a) Drag-to-buckle — the recommended primary.** Press one fingertip down on the
sheet with a high-friction pad, then drag it a couple of centimetres *toward* the
other finger. The sheet's far side is held by friction against the table, so the
middle buckles upward into a small ridge. Close on the ridge. This is what a
human thumb does without thinking, it needs no extra degrees of freedom (the arm
supplies the lateral motion), and it works mid-sheet — no table edge or corner
required.
**Its cost is that it needs regulated normal force.** Too light and the finger
skates; too heavy and it scuffs or creases. See "The honest problem" below.

**(b) Push-to-edge — the reliable fallback.** Drag the sheet until an edge
overhangs the table, then pinch the overhang. Very robust, needs no force
finesse, but it needs a free table edge and a longer motion. Good first task to
get end-to-end data flowing before (a) is tuned.

**(c) Corner scoop — opportunistic only.** Approach a corner at a shallow angle
with a thin chamfered lower finger and wedge under. Works when the corner already
curls, which paper often does; fails on genuinely flush stock. Keep as a bonus,
never the primary.

**(d) Suction or adhesion — the industry answer, deliberately excluded.** A small
vacuum cup solves flat-sheet picking outright. It is excluded for 1.0 because it
means a pump, tubing and a valve — none of it printable — and it sidesteps the
very contact problem `gripper_bet.md` says is the hard and interesting part.
Recorded here as the escape hatch if (a) and (b) both stall.

### Fingertip geometry

- **Parallel jaws, not angular.** The stock SO-101 gripper rotates its jaw on an
  arc, so the tips both converge *and* rotate as they close — on paper that
  rotation scrapes and creases. Adding a **printed parallelogram linkage** keeps
  the fingertips parallel through the stroke. Pin joints, all printable, one of
  the few places extra mechanism clearly earns its weight.
- **Wide, shallow pads** — roughly 25–30 mm across, so grip load spreads instead
  of concentrating. Point loads are what crease paper.
- **Crown one pad slightly** (a gentle convex curve, the other flat). Two nominally
  flat pads that are half a degree out of parallel meet at one corner and pinch
  there; a crowned pad always meets along a line and tolerates the misalignment
  that a printed part will definitely have.
- **Thin leading edge on the lower finger** for (c) and for sliding under a lifted
  buckle. FDM realistically gets to ~0.6 mm, not the ~0.2 mm that would be ideal.
  If that proves too blunt, the fix is a thin steel shim bonded into a printed
  pocket — the first honest exception to "fully printable," and worth accepting
  before compromising the jaw.

### Surfaces and friction, including stack separation

- **Pads in TPU** (roughly 85–95A), 2–3 mm thick: printable, compliant, grippy on
  paper, and the compliance itself limits force. Smooth, not aggressively
  textured — texture bites and tears.
- **Deliberately asymmetric friction.** Make one pad high-friction TPU and the
  opposing one low-friction smooth PETG. This is exactly how a printer's feed
  roller and retard pad separate sheets: the top sheet keys to the high-friction
  side while the sheet beneath it slips against the low-friction side, so a
  double-feed shears apart instead of travelling together.
- So **yes, single-sheet separation from a stack looks achievable**, and the
  mechanism to do it is a material choice rather than an extra actuator. It is
  the cheapest good idea in this document. It is also untested here, and printer
  feeders get to tune roller pressure precisely, which we cannot yet.

### Limiting grip force so it doesn't crease or tear

Three layers, cheapest first:

1. **Compliance in series** — TPU pads plus a **leaf-spring flexure** in the
   finger. Grip force then follows deflection, which is far more forgiving of
   position error than a rigid jaw closing against a position target. Spring rate
   has to be tuned by printing a few and trying them; there is no point
   calculating it before the pads exist.
2. **Servo torque limit** on the gripper motor, set low.
3. **Current sensing as a soft stop**, if the bus servo reports present load
   usefully at these very small forces — uncertain, and easy to check on the
   bench before committing to it.

### The honest problem

Strategy (a) wants **regulated normal force at the fingertip**, and the SO-101 is
a chain of **position-controlled** servos with no force sensing at the tip. Commanding
a position against a rigid table gives you whatever force the geometry and the
servo's torque limit happen to produce, which is not a controlled quantity.
The intended answer is to put the compliance in the *mechanism* — a sprung,
slightly over-travelling fingertip, so that pressing "a bit too far" turns into
spring deflection rather than force spiking. That converts a control problem into
a geometry problem, which is the right trade for a printed part.

**But this is the single least certain thing in the design**, and it should be
prototyped on its own — one sprung fingertip, by hand, on a real sheet — before
any full gripper is built around it.

## 3. Camera

**Reading of the ask (confirm this, Jake):** *"a camera on each one"* = **one
camera per gripper unit**, so the handheld unit and the arm-mounted unit produce
the same view. That is what makes the demonstration and execution images
comparable, so it is the reading that serves the thesis. The alternative readings
— one per *arm* (wrist cam), or one per *finger* (stereo at the tips) — are
plausible from the words alone, and stereo at the fingertips in particular is
interesting later. Not assumed here.

- **Mounted rigidly to the gripper body, never to the wrist.** If it moves with
  the arm instead of the gripper, the handheld view and the mounted view stop
  matching and the whole point is lost.
- **Position:** on the spine above the jaw pivot, looking down the jaw axis,
  pitched roughly 20–30° so **both fingertips and the contact patch stay in
  frame** through the full open-to-closed stroke. Offset slightly to the side so
  a closing finger does not eclipse the contact point at the moment it matters.
- **Verify by printing the camera arm first** and just looking at the picture
  while working the jaws by hand. Framing is cheap to get wrong and cheap to
  check.
- **USB UVC module, not CSI.** A UVC camera enumerates identically off a laptop
  in handheld mode and off the robot host when mounted. A CSI module ties you to
  a Pi and breaks mode symmetry. Paper is low-contrast and often white-on-white,
  so favour a sensor that behaves under fixed manual exposure over one with a
  high megapixel count.

## 4. Power, data and the trigger — how the two modes differ

Keep **one umbilical** with **one connector**, carrying: servo bus (data + servo
power) and the camera's USB. What it plugs into is the only thing that changes.

| | Arm-mounted | Handheld |
|---|---|---|
| Servo power/data | arm's existing serial bus | belt-pack: battery + USB-serial adapter |
| Camera | USB to the robot host | USB to the same host (or a laptop) |
| Jaw commanded by | the policy / leader arm, as `gripper.pos` | the trigger, as `gripper.pos` |

**Trigger, handheld — the recommendation:** make the trigger a **second bus servo
of the same type, back-driven**, with a printed lever on its horn. Squeeze it and
read its position; that value already *is* a gripper command in the follower's
own units and range. It is precisely how the SO-101 leader already drives the
follower, so there is no new driver, no new calibration convention, and no
mapping step — the same argument `gripper_bet.md` makes about hands and gloves,
applied to a trigger. It costs one servo over a potentiometer; take that trade.

Fallback if that proves fiddly: a printed lever on a bought potentiometer. Cheaper,
lighter, and it reintroduces exactly the mapping layer the thesis is trying to
delete. Choose it only with that cost in mind.

## 5. 3D printability

**Printable:** body/shell, adapter plate, both fingers, the parallelogram links,
flexure fingers, pads (TPU), camera arm and housing, handle, trigger lever, cable
strain reliefs, jaw pin bushings.

**Must be bought:**

| Part | Note |
|---|---|
| Bus servo(s) — jaw drive, and one more for the handheld trigger | same family as the arm's, so the bus and tooling stay uniform |
| M3 fasteners + heat-set inserts | printed threads in load paths will not survive iteration |
| Camera module + USB cable | see above |
| Servo bus connector/pigtail | match whatever the arm's wrist actually uses (measurement 5) |
| Battery pack + USB-serial adapter | handheld mode only |
| Thin steel shim | *only* if the printed leading edge is too blunt |
| Small springs | if the printed flexure's rate can't be tuned in plastic |

Everything on that list is a stock part, nothing is custom-machined, and the
printed parts carry the geometry. That is the bar "fully printable" should be
held to for 1.0.

## 6. CAD toolchain

**Decision: OpenSCAD is the source of truth for every printable part. Blender is
for visualization only.** Both are open source, which was the requirement.

**Why OpenSCAD for parts.** It is plain text, so it lives in git the way code
does — real diffs, real history, reviewable changes. That matters here more than
usual, because every part in this design is parametric and will be iterated many
times against **measurements that do not exist yet**. Each of the seven wrist
measurements becomes a named constant; when one lands, that constant changes and
the parts regenerate. It is also directly authorable by an agent, so the geometry
can be iterated by voice alongside this document.

**Why Blender stays, and where the line is.** Blender already holds the Tool
Caddy scene (`plans/tool-caddy.blend`) and is the right tool for renders, layout
and showing how the gripper sits on the arm. **Nothing printable should originate
there.** A mesh edited by hand in Blender does not survive the next parameter
change upstream, and the moment part geometry lives in two places the OpenSCAD
source stops being true.

**The honest caveat.** OpenSCAD outputs meshes, not B-rep solids: no real
fillets, no STEP export. For a gripper with bearing seats, servo mounts and
fastener fits, that is a real limitation, not a stylistic one. The open-source
alternative is **build123d** (or CadQuery) — Python, parametric, proper B-rep,
exports STEP. Start in OpenSCAD because Jake knows it and the loop is faster;
treat build123d as the escape hatch if fillets or precise fits become the
blocker. A note for later, not a reason to delay.

**Repo layout.** Put sources in `cad/` (e.g. `cad/adapter_plate.scad`,
`cad/finger.scad`), with shared dimensions in one `cad/params.scad` that the
parts include — that file is where the wrist measurements land. Generated STLs
are **build artifacts**: regenerate them from source, never hand-edit them, and
keep them out of the way of the sources.

## Open questions and the decisions Jake has to make

**Decisions only Jake can make:**

1. **Camera reading** — one per gripper unit, as assumed here? Or per arm, or per
   fingertip?
2. **wrist_roll cable wind-up** — software-limit the range, service loop with a
   hard stop, or buy a slip ring?
3. **Reuse the arm's existing gripper servo (ID 6), or put our own servo in the
   gripper body?** Own servo keeps the handheld unit self-contained and identical
   in both modes; reuse is lighter and keeps the channel count as the scripts
   already expect it.
4. **Trigger: matched servo (recommended) or potentiometer?**
5. **Is the steel shim acceptable** if a printed edge won't get under a sheet, or
   does "fully printable" win and we live with strategy (b)?

**Genuinely unresolved, to be settled on the bench:**

- Whether drag-to-buckle works with mechanical compliance alone and no force
  sensing. Prototype the sprung fingertip by itself, first, before anything else.
- Whether asymmetric pad friction really separates single sheets without the
  tuned roller pressure a printer feeder gets.
- Whether the bus servo's load reporting is usable at forces this small.
- Which paper: 80 gsm copier stock is the sane default, but glossy, card and
  crumpled sheets behave nothing like it, and "handling papers" may mean any of
  them.
- **Recalibration is unavoidable.** New jaws invalidate the gripper's
  1594–3018 range in `lerobot_calibration/`, so any recordings made before the
  change will have `gripper.pos` values that no longer mean the same opening.
  Existing demo data does not carry over. Better to know that now than after
  recording a dataset.

**Next step:** take the seven measurements, then print one sprung fingertip and
one camera arm. Nothing else until those two answer.
