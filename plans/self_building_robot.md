# Self-building robot: a two-armed robot whose only job is to build itself

Status: PLAN ONLY (2026-10-22, voice-fc9b0f77). No code, CAD or purchases.
Written from a voice discussion with Jake. **A living plan:** Jake keeps adding
to it; each addition is folded into the sections it changes and logged under
"Additions" at the end. Renamed from `plans/cooking_robot.md` when Jake
reframed it: it is **not** a cooking robot. Builds on `plans/gripper_bet.md`
(humans drive the hardware), `plans/hand_1_0.md` (mirror a human; stereo at
eye height), `plans/handheld_gripper.md` (UMI method) and
`plans/shared_stereo_glasses.md`.

## The idea in one paragraph

A legless robot: a stationary torso with two arms and a stereo head, on a
weighted base that stands on its own on a bench, counter or stool. **Its only
required job is to build itself**: assemble its own arms, grippers, actuators,
the printers that make its parts, and the packaging. Everything else follows,
because assembling robotics parts is varied, precise, two-handed manipulation,
and the skills and data should carry over to useful real-world tasks (cooking
is one of them, now downstream, not the goal). The bootstrap is Jake's core
insight: **start with zero automation. People assemble the whole robot,
gripper included, and pack it, using only the handheld version of the robot's
gripper (one in each hand).** If two people-held grippers can build it, two
robot-held grippers can too. So the programme reduces to one design, the
gripper, and every human build is also training data, recorded UMI-style from
stereo cameras at eye height. The long arc: closing the loop all the way from
raw materials (mining included), with chips the one thing bought in.

## The rule that falls out of it

> **The gripper-only assembly rule.** Every step of making, assembling,
> testing, packing and repairing the robot must be doable by a person holding
> one copy of the robot's gripper in each hand, wearing the robot's stereo
> cameras at eye height, and nothing else (no fingers, no tool unless the
> gripper can pick it up, hold it and use it).

Every design choice below is checked against this rule. It is also a
manufacturability rule in disguise: snap-fits from one direction, keyed
connectors and drop-in modules are what a gripper can do, and they are also
what makes assembly cheap.

## The complexity floor (what stops this being absurd)

A trivially simple machine can "build itself" (three blocks that stack into
three blocks). That proves nothing. So the robot must clear a floor, and the
floor is what makes the self-assembly data worth having:

> **The floor test.** Besides its own robot-friendly parts, the robot must
> assemble things **not designed for it**, using the same gripper: an
> off-the-shelf 3D-printer kit, standard threaded fasteners (M2–M5 screws,
> nuts, heat-set inserts), press-fit bearings, standard wire connectors (JST,
> Dupont, XT30), cable ties and cable routing, and packing a box.

Why this floor (Jake's suggestion, which I think is the right one):

- **It is measurable.** A named kit, a timed build, a pass/fail per step.
- **It guards against cheating by design.** If we make our own parts ever
  easier for the gripper (which the gripper-only rule pushes us to do), the
  floor test still holds the gripper to the messy real world.
- **It is the transfer test.** Useful work is mostly manipulating things
  someone else designed. A robot that can build a stranger's printer kit is
  close to one that can fix a bike or load a dishwasher.
- **It keeps "closure" honest.** The printer kit is the machine that makes
  the robot's parts, so passing it is also a step of real self-replication.

I'd add two more conditions so the floor can't be met by a toy:
**closure** (what the robot builds includes its own gripper and actuators,
not just a shell around bought modules) and a **held-out kit** (one test kit
the training data never saw, swapped each round).

## Where the gripper sits: pinch to hand

Jake's bounds: lower = a single pinch gripper; upper = the human hand (a hand
can't really drive an object more complex than itself, though a robot hand
could be smaller). The spectrum, as I see it:

| Point | DoF per hand | Can it pass the floor test? |
| --- | --- | --- |
| Parallel-jaw pinch (today's Gripper 22 class) | 1 | Mostly, but wide jaws block the view and can't reach into a printer frame or a connector housing |
| **Needle-nose pliers** (narrow, long tips; Jake's pick from building the Aero Hand) | 1 | **Most of it**: screws held in a tip notch, connectors, bearings, wires. Weak at big objects and at turning screws without a wrist |
| Pliers + powered wrist roll + tip features | 1 + wrist | Nearly all of it: the wrist drives a screwdriver held in the jaws |
| Two articulated fingers (2–3 joints each) | 4–6 | All of it, plus in-hand regrasp; much harder to build, to identical-mirror in handheld mode, and to self-assemble |
| Three or more fingers | 9+ | Same, more so |
| Human hand | ~20 | The ceiling: anything a person does |

**Recommendation: a 1-DoF needle-nose-pliers gripper**, used in pairs, with a
powered wrist roll on the robot side (the person's own wrist does it in
handheld mode). Reasons:

1. **It is what people actually used.** Building the Aero Hand needed tweezers
   and pliers far more than a squeeze grip. Small manufacturing and assembly is
   pinch-at-the-tip work.
2. **It stays out of the way in handheld mode.** Slim jaws don't block the
   cameras or the person's view, and pliers handles are intuitive: nobody has
   to learn them.
3. **It keeps the identity constraint cheap.** One joint is easy to make
   identical in handheld and robot form (a person squeezes the handles; a
   motor drives the same pivot). Every extra finger joint is a joint the
   handheld tool has to mirror and record.
4. **It is the easiest thing to self-assemble**, and self-assembly of the
   gripper is the first bootstrap test.
5. **Tip features buy a lot of capability for free**, without joints: a flat
   pad and a serrated pad, a V-notch for round parts and screws, a hex pocket
   that holds a screwdriver bit, and a wire cutter at the jaw root (wiring is
   a big share of assembly).

The known cost: **pliers can't cook** or handle big, heavy or soft things (a
pot, a towel). Under the reframe that is an accepted trade, not a flaw. If a
later step needs it, add a second tool the pliers pick up (a spatula with a
pliers-friendly tab), or move one notch up the table, not straight to a hand.

### Why two arms

- **Hold and work.** Almost every assembly step is one hand holding the part
  and the other inserting, screwing or plugging. One arm needs a jig for each
  part instead, and every jig is a tool the robot must also build.
- **The human demo has two hands.** The bootstrap is a person with a gripper
  in each hand; a one-armed robot couldn't replay half the episodes.
- **Hand-offs and regrasps.** With 1-DoF grippers, turning a part around means
  passing it between hands. Two simple grippers replace one dexterous one.
- **Why not three or more?** People do assembly with two; more arms add cost
  and collisions without a demonstrator to learn from.

## Stages

### Stage 0: the gripper (now)

The one design everything depends on. Requirements:

1. **Identical in both modes** (the Hand 2.0 identity constraint): the
   handheld and the robot gripper are the same part, same jaws, same
   actuator, so a human demo is a robot demo.
2. **Needle-nose-pliers form** with tip features (above).
3. **Force without a force sensor**, read from the actuator (see "The force
   question" below). This decides the actuator.
4. **Can assemble itself**: a person with two handheld grippers can put a
   gripper together from its parts. The first real bootstrap test, and small
   enough to run at a desk.
5. **Printed** (see "Materials"): every structural part comes off the
   printers, so the gripper is also the first test of the print rules.

Exit: a gripper that passes requirement 4 on a timed run, and a measured
answer to the force question.

### Stage 1: the handheld bootstrap build

People build complete robots (gripper, then an arm, then the whole torso), a
printer kit (the floor test) and pack them, using only grippers, wearing
stereo cameras. Each build is logged as episodes (stereo video + gripper pose
+ jaw opening + force estimate). Per step: can it be done gripper-only, how
long it takes against bare hands, how often it fails. Every step that fails is
a design change to the robot, not a reason to give the person a tool.

Exit: one complete robot and one printer kit built gripper-only; the step list
with times; the dataset.

### Stage 2: one robot cell

The robot from stage 1 is the cell: two arms, a stereo head, the weighted
base, on a bench. Train on stage-1 data (plus some teleop to close the
embodiment gap, as `handheld_gripper.md` recommends) and have it repeat the
same steps, easiest first.

Exit: the cell does N stage-1 steps at a set success rate, including floor-test
steps.

### Stage 3: the line and the printer farm

Replace people one station at a time with cells, so a line of identical
two-armed cells passes work down. Parts come from a **printer farm**: cells
clear prints, swap plates, feed pellets, wind motors, inspect and pack. The
cells also **build more printers**, mostly from printed parts, so the farm
grows itself (RepRap-style, robot-assembled). People move to exceptions,
teleop rescue and repair. Robots repair robots by swapping modules (a whole
arm, a whole actuator).

### Stage 4: closing the loop to raw materials

Full self-replication starts at the mine. Close it in steps, each one removing
a bought input. **Chips are bought** (Jake's decision): semiconductors are out
of scope; everything else should close.

| Step | New capability | Removes from the bought list | Machines the cells must build |
| --- | --- | --- | --- |
| C0 | Assembly (stages 1–3) | Assembly labour | Printers |
| C1 | Plastic from recycled scrap or pellets the farm makes | Bought pellets | Shredder, pelletiser, pellet extruder |
| C2 | Metal from scrap: melt, cast, machine, draw wire, wind motors | Bought motors, fasteners, structure | Crucible furnace, sand-casting kit, lathe and mill (Gingery-style shop-from-scrap), wire-draw bench, coil winder, lamination stamping or cutting |
| C3 | Refining from ore: iron, aluminium, (copper) | Scrap metal | Electric arc or induction furnace, electrolysis cells, kilns for ferrite |
| C4 | Mining and mineral processing | Ore | Excavators, crushers, ball mills, magnetic and flotation separation |

**A pliers gripper won't mine.** It doesn't need to: the robots build the
bigger machines that do (an excavator is an assembly job), which is the same
step-by-step scale-up as the sizes section below. Each step is gated by
whether the cells can build that step's machines from what the previous steps
make.

**Prior art to study before designing C2–C4:**

- **NASA / ASEE 1980 summer study, "Advanced Automation for Space Missions"**
  (Freitas and Gilbreath, eds.): a self-replicating lunar factory grown from
  a seed of roughly 100 t, with a small share of hard-to-make parts (chips)
  imported from Earth. It is the closest worked example of closure ratios and
  of which processes a factory needs to copy itself. (From memory; the
  research pebble checks the numbers.)
- **RepRap** (Bowyer, 2005 on): the printer that prints its own plastic parts;
  real data on what share closes and what stays bought.
- **Gingery, "Build Your Own Metal Working Shop From Scrap"**: a lathe, mill
  and foundry bootstrapped from a charcoal furnace and scrap aluminium. Close
  to step C2 done by hand.
- **Open Source Ecology's Global Village Construction Set**: ~50 machines
  meant to build each other and a small economy.
- **Von Neumann's universal constructor** and **Chirikjian's lunar
  self-replicating robot work**: theory and small physical demos.

## Sizes: scale in steps, not jumps

Once the robot builds itself, robots can build larger or smaller copies of the
same design (Feynman, "There's Plenty of Room at the Bottom", 1959: machines
building smaller machines, each a step down). Jake's rule: **one size step per
generation.** A large robot building a tiny one is hard; large builds medium,
medium builds small, small builds tiny.

**Step ratio: about 2× in length per generation** (8× in mass) is my starting
estimate, to be tested. Reasoning: a builder handles parts comfortably down to
roughly 1/50–1/100 of its own size (a person, ~1.7 m, handles M2 screws with
tweezers). A 2× smaller child's smallest parts are half the parent's, still
inside what the parent's grip and cameras resolve; a 4× step pushes the
parent to its precision limit on every part. Larger ratios may work on the way
up, where the parent mostly lifts and positions.

What changes with size (square-cube law):

- **Going up (each 2× step):** mass grows 8×, cross-sections 4×, so stresses
  in the structure double. Joint torque needed grows ~16× (mass × lever arm),
  but motor torque grows only ~8× with motor volume, so torque-to-weight
  halves per step. Expect printed plastic to give way to steel, and electric
  gearmotors to give way to hydraulics, somewhere around 2–4× human scale.
- **Going down:** gravity (∝ L³) loses to surface forces: friction and
  stiction (∝ L²) and adhesion and static (∝ L). Parts stick to the jaws, so
  release needs a push or a shake. Electromagnetic motors lose efficiency fast
  below about a centimetre (copper losses dominate), so piezo or electrostatic
  drives take over.
- **What each size can still source or make:** fasteners exist down to about
  M1 (watch screws smaller), bearings to ~1 mm bore, motors to ~4–6 mm
  (micro steppers, coreless), FDM features to ~0.4 mm (resin printers ~0.05
  mm). Below that, snaps, adhesives and welding replace screws, and resin
  printing or lithography replaces FDM.

**How far the identical design stretches: roughly ¼× to 2–4× human scale**
(an arm of ~10 cm to ~1–2 m). Past that, the design must change, not just
scale: different actuators, materials and joining. Each generation is still
built by the one before it.

## The force question (decides the actuator)

Today's gripper (Gripper 22 on Base 15, `v316_generalist_post_cap`) is an
STS3215 driving a 16-tooth pinion into 34-tooth handle-gears (2.125:1).
Overall ratio depends on which STS3215 gearbox is fitted:

| STS3215 variant | internal | overall with 16:34 |
| --- | --- | --- |
| C046 (leader-arm gearing) | 1:147 | ~312:1 (the "about 300:1") |
| C044 | 1:191 | ~406:1 |
| C001 (follower, stiff) | 1:345 | ~733:1 |

At those ratios, current-based force is poor:

- **Gearbox friction dominates.** Current tells you the motor is working hard,
  not how hard the jaws push. Expect big hysteresis between closing and holding.
- **Not back-drivable** in practice, so contact shows up late, as a stall.
- **Coarse readout.** STS3215 reports `Present_Load` (% of max) and
  `Present_Current` (about 6.5 mA per count). **Nothing in this repo reads
  either today**; `record_grip.py` reads only `Present_Position`, with torque
  off so the person back-drives the fingers.
- **Handheld mode has no force at all.** With torque off the servo is only an
  encoder.

The alternative is a **quasi-direct-drive (QDD) actuator**: a large-diameter
brushless motor, one planetary stage around 6–10:1, field-oriented control
and a magnetic encoder. Current then maps to torque well enough to sense force
(the MIT Cheetah approach), the joint back-drives by hand, and it can act like
a spring. The **RobStride RS00** (10:1, 5 N·m rated, 310 g, CAN) is one;
it is heavy and costly for a pliers-sized hand tool. Pliers tips need little
force, so a small gimbal motor on the jaw pivot with one small stage may do.

QDD also helps handheld mode: a back-drivable motor in light impedance mode
reads the person's squeeze from its current. A fallback with no motor:
compliant jaws whose bend the cameras or encoder read.

The motor type interacts with materials (below): a QDD needs magnets, and the
choice of ferrite vs no-magnet switched reluctance changes how clean the
current-to-force map is (reluctance torque is non-linear in current).

**Recommendation:** measure first. If the STS3215 gives a clean, repeatable
force signal on a scale test, keep it for stages 0 and 1. If not (expected),
design the pliers around one small QDD actuator and reuse it in the wrist,
with a second, larger one for shoulder and elbow: the "one or two actuator
designs" target.

## Designing for scale

- **Actuators are the cost.** Two designs, reused at every joint. Each is a
  sealed drop-in module with one plug-in connector (power + CAN), which is
  also the repair unit.
- **Structure:** printed links and shell, snap-fit from one direction, no
  loose wires: every module plugs into the one beside it.
- **Head:** the stereo pair at human eye spacing (~63 mm) and eye height.
- **Base:** weighted so it can't tip at full reach and payload.
- **Price:** appliance-level. A BOM model per stage (1k / 100k / 10M units)
  is a first pebble; without it "appliance price" is a hope.

## Materials

### Print by default

**Default to 3D printing, not stamping or molding.** Presses, die-casters and
injection molders are huge machines the robots cannot build early on, so they
cap how fast the factory grows. A 3D printer is mostly printable parts plus a
short list of bought ones, and a cell can assemble it, so the farm can copy
itself and grow exponentially, limited by printer-hours, cell-hours per
printer, and the bought-parts supply.

- **Pellet extrusion at scale**, not filament: roughly 10× cheaper per kg,
  faster and larger. Filament printers are fine for stages 0–1.
- **Heat:** PETG (softens ~80 °C), ASA (~100 °C) or PA-CF by zone. With
  cooking no longer the goal, **PLA is back in play** for parts that stay
  cool (motor-adjacent parts still need the higher-rated plastics), which
  matters because PLA is the plastic we can make from plants (below).
- **Food contact** (only if a cooking application is built later): sealed,
  smoothed or covered surfaces, since layer lines trap bacteria.
- **Mold or stamp only when volume clearly pays for the tooling**, or print
  the mold, and only if the cells can build that tooling.
- **Print rules join the gripper-only rule:** support-free in a set
  orientation, fits the build volume, liftable by the gripper off the plate,
  snaps sized for creep and layer direction. Printed parts are weaker, so
  links get thicker sections or a tube spine; the actuators carry the
  precision. Printer-hours per robot is a BOM line.

### The smallest material set that closes the loop

Jake's constraints: no rare earths; go from raw material up; chips are bought.
The candidates:

- **Magnets: ferrite or none.** Ferrite is iron oxide plus a little strontium
  (or barium) carbonate, sintered in a kiln, so it is *not* pure iron: it adds
  one mineral. Its field is about a third of NdFeB's (~0.4 T vs ~1.3 T),
  which a Halbach arrangement partly makes up by concentrating flux on the
  working side. Tesla said in 2023 that its next drive unit would use no rare
  earths, which shows the ferrite route working at scale (in a car-sized
  motor, which has more room than a pliers joint).
- **Switched-reluctance motors (SRM): no magnets at all**, only steel
  laminations and copper or aluminium windings. Simple to make and wind;
  costs: torque ripple, noise, lower torque density, and a non-linear
  current-to-torque map that makes force sensing harder. The controller is
  chips, which we buy anyway.
- **Iron-centric design:** steel for anything printed plastic can't do
  (shafts, laminations, cores, fasteners, bearing balls), iron oxide for
  ferrite. Iron is the easiest metal to refine at scale and the most common.
- **Aluminium vs copper conductors:** aluminium conducts ~60% as well as
  copper, so windings are ~1.6× the cross-section for the same loss, but it is
  a third the density and far more abundant. Refining it needs a lot of
  electricity (electrolysis). A neat option to evaluate: **anodised aluminium
  winding wire or foil**, whose oxide skin is the insulation, so windings need
  no polymer enamel. Copper is easier to smelt but its ores are scarcer.
- **Plastics:** petrochemical plastics need an oil refinery, which the robots
  won't build any time soon. **Bio-based PLA** (plant starch → fermentation →
  lactic acid → PLA) closes the loop with farming instead. Or shrink plastic
  to what recycling covers. Or go metal-only, which gives up the printer farm.
- **Electronics:** bought for the long term (chips), plus the copper or
  aluminium traces and boards around them.

**Recommendation (to test, not decided): iron + aluminium + one bio-plastic,
plus bought chips.**

- **Iron/steel**: structure where print isn't enough, laminations, cores,
  shafts, fasteners, bearings.
- **Aluminium**: windings (anodised, no enamel), castings, light structure.
- **PLA (bio) or recycled plastic**: printed parts and shell.
- **Motors: switched reluctance for the big joints** (no magnets at all), and
  **ferrite (Halbach) for the gripper/wrist QDD** where clean force sensing
  matters. Ferrite's strontium is the one extra mineral; if SRM force sensing
  proves good enough, drop ferrite and the set is three materials plus chips.

The research pebble below checks the pieces (laminations from plain vs silicon
steel, ferrite kiln temperatures, anodised-winding feasibility, PLA heat limits
in a motor housing).

## Ideas to evaluate (not decided)

| Idea | For | Against / risk |
| --- | --- | --- |
| **Cooking (or another service) as a revenue and data source** | Pays for stages 2–4; tests transfer to real tasks | Off the critical path now; pliers can't cook without a held tool |
| **Factory cell = consumer robot** | One design, one dataset, every sold robot is a spare cell | Consumer polish (cute shell, safety) rides into the factory |
| **Cable-driven arms, motors in the base** | Light arms; all actuators in one swappable module | Cable stretch and wear; threading cables is a hard gripper-only step; noisier force |
| **Robots repair robots by swapping modules** | Keeps the line running; follows from plug-in modules | Needs diagnosis of which module failed |

## Open questions

1. Is STS3215 current/load at ~300:1 clean enough for force, or do we go QDD?
2. How does a handheld episode record force: impedance mode, jaw bend, or not
   at all?
3. Can two needle-nose grippers plus a wrist roll do every floor-test step,
   or does some step need a second finger joint? `gripper_bet.md` §4's
   two-finger ceiling applies.
4. Which printer kit is the floor test, and which is the held-out kit?
5. Size step: is 2× per generation right, and what is the smallest part each
   size can make and handle (measure it at our size first)?
6. Where does the policy run, and what does compute cost per unit?
7. Ferrite vs switched reluctance at gripper scale: torque density and force
   sensing, measured.
8. Can aluminium be the only conductor (windings, wiring, boards)?
9. Printer-farm doubling time, and which bought part runs out first.
10. Which of C1–C4 is the first that needs a machine the cells can't yet build,
    and what is the smallest version of it?

## First pebbles to file (gripper and actuator first)

Not filed yet; listed for Jake's sign-off. Each would go to `agent/`.

1. **Measure gripper force from the servo.** Add `Present_Current` and
   `Present_Load` to `record_grip.py` (torque on), squeeze a scale or load cell
   at several set points, plot reading vs force for closing and holding.
   Small, code only.
2. **Needle-nose pliers gripper, version 1.** A new Gripper version: a 1-DoF
   pliers with long narrow jaws, tip features (flat and serrated pads, V-notch,
   bit pocket, root cutter), handheld handles, encoder on the pivot. Printed,
   gripper-only assemblable.
3. **Pliers actuator study.** Small gimbal motor + one stage + FOC driver vs
   RS00 vs STS3215 for the pliers pivot: mass, cost, torque, back-drive feel,
   force signal. Pick the one actuator for gripper + wrist.
4. **Floor-test kit and protocol.** Pick the off-the-shelf printer kit (and a
   held-out one), list every step, and run a first bare-hands vs two-pliers
   timing on a few steps.
5. **Gripper-only assembly audit of Base 15 / Gripper 22**: every step, doable
   or not with two handheld grippers, and the changes (snaps for screws, keyed
   plugs).
6. **Second handheld gripper and a two-handed recording rig** with the stereo
   headset from `shared_stereo_glasses.md`.
7. **Self-replicating printer pick:** an open printer with a high printed share
   and few bought parts, ideally pellet-fed; gripper-only audit of it.
8. **Closure research note:** the NASA 1980 study, RepRap, Gingery and OSE's
   numbers on closure ratio, seed size and the process list; draft the C0–C4
   machine list and check the 100 t figure.
9. **Material-set research note:** ferrite vs SRM at gripper and shoulder
   scale, aluminium windings (anodised), plain vs silicon steel laminations,
   PLA in motor housings; confirm or change the iron + aluminium + PLA pick.
10. **Size-step study:** the smallest part we can make and handle at our scale,
    and what that implies for a ½× and a 2× generation.
11. **Torso sizing** for a bench-mounted assembly cell (reach, payload, base
    mass); a block layout, not CAD.
12. **BOM cost model** at 1k / 100k / 10M with printer-hours and grams per part.

Dropped from the cooking version: the kitchen safety pebble (cooking is no
longer the goal). Folded in: print rules and material map now sit inside
pebbles 2 and 9.

## Additions

- 2026-10-22, first plan (as `cooking_robot.md`).
- 2026-10-22, materials: default to 3D printing so the printer farm can
  self-replicate; pellets at scale, heat-rated materials, mold or stamp only
  where volume pays.
- 2026-10-22, **reframe**: not a cooking robot; the only job is building
  itself. Renamed the plan; added the complexity floor (assemble things not
  designed for it), the pinch-to-hand spectrum with a needle-nose-pliers
  recommendation, why two arms, scaling in size steps with the square-cube
  limits, stage 4 (closure to raw materials, mining via bigger machines the
  robots build, prior art), and the smallest material set (no rare earths;
  iron + aluminium + bio-plastic; chips bought, per Jake). PLA allowed again
  away from heat; food-contact rules apply only to a later cooking add-on.
  Pebble list rewritten (12).
