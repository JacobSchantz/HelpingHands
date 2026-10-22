# Cooking robot — a two-armed torso that its own gripper can build

Status: PLAN ONLY (2026-10-22, voice-fc9b0f77). No code, CAD or purchases.
Written from a voice discussion with Jake. Builds on `plans/gripper_bet.md`
(humans drive the hardware), `plans/hand_1_0.md` (mirror a human; stereo at
eye height), `plans/handheld_gripper.md` (UMI method) and
`plans/shared_stereo_glasses.md`.

## The idea in one paragraph

A cute, legless robot: a stationary torso with two arms and a stereo head, on
a weighted base that stands on its own and can be put on a counter or a stool.
Its job is cooking. It is designed to be built in the billions, and to help
build itself. The bootstrap is Jake's core insight: **start with zero
automation. People assemble the whole robot, gripper included, and pack it,
using only the handheld version of the robot's gripper (one in each hand).**
If two people-held grippers can build it, two robot-held grippers can too. So
the whole programme reduces to one design, the gripper, and every human build
is also training data, recorded UMI-style from stereo cameras at eye height.

## The rule that falls out of it

> **The gripper-only assembly rule.** Every step of making, assembling,
> testing, packing and repairing the robot must be doable by a person holding
> one copy of the robot's gripper in each hand, wearing the robot's stereo
> cameras at eye height, and nothing else (no fingers, no screwdriver unless
> the gripper can hold and drive it).

Every design choice below is checked against this rule. It is also a
manufacturability rule in disguise: snap-fit from one direction, big keyed
connectors and drop-in modules are what a gripper can do, and they are also
what makes assembly cheap.

## Stages

### Stage 0 — the gripper (now)

The one design everything depends on. Requirements:

1. **Identical in both modes** (the Hand 2.0 identity constraint): the
   handheld and the robot gripper are the same part, same fingers, same
   actuator, so a human demo is a robot demo.
2. **Force without a force sensor**, read from the actuator (see "The force
   question" below). This decides the actuator.
3. **Can assemble itself**: a person with two handheld grippers can put a
   gripper together from its parts. This is the first real bootstrap test and
   it is small enough to run at a desk.
4. **Wipe-clean and food-safe** fingers or finger covers, since the end use is
   a kitchen.

Exit: a gripper that passes rule 3 on a timed run, and a measured answer to
the force question.

### Stage 1 — the handheld bootstrap build

People build complete robots (first the gripper, then an arm, then the whole
torso) and pack them, using only grippers, wearing stereo cameras. Each build
is logged as episodes (stereo video + gripper pose + jaw opening + force
estimate). Measure, per assembly step: can it be done gripper-only, how long it
takes against bare hands, and how often it fails. Every step that fails is a
design change to the robot, not a reason to give the person a tool.

Exit: one complete robot built gripper-only; the step list with times; the
dataset.

### Stage 2 — one robot cell

The robot from stage 1 is the cell: two arms, a stereo head, the weighted
base, set on a bench. Train on stage-1 data (plus some teleop to close the
embodiment gap, as `handheld_gripper.md` recommends) and have it repeat the
same steps, starting with the easiest. Cooking demos run on the same robot in
parallel; it is the same machine.

Exit: the cell does N stage-1 steps at a set success rate.

### Stage 3 — the line

Replace people one station at a time with cells, so a line of identical
two-armed cells passes work down. Cells also tend the part-making machines
(load and unload presses, molding machines and die-casters), wind motors,
inspect and pack. The part-making processes stay as they are; robots take over
assembly and handling. People move to exceptions, teleop rescue and repair.
Robots repair robots by swapping modules (a whole arm, a whole actuator).

Ceiling: what robots cannot make in this line: chips, magnets, raw materials
(resin, steel/aluminium stock, copper). Lock those supply chains early.

### Stage 4 — the product

The same machine sold as an appliance. A cooking service (below) can start as
early as stage 1 and pays for stages 2 and 3.

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

- **Gearbox friction dominates.** Friction in a multi-stage spur train is a
  large, direction-dependent share of output torque, so current tells you the
  motor is working hard, not how hard the jaws push. Expect big hysteresis
  between closing and holding.
- **Not back-drivable** in practice (the C001 hardly at all), so a contact
  shows up late and as a stall, not a smooth rise. Fine for "is it holding
  something", weak for "squeeze an egg / feel a pan handle slip".
- **Coarse readout.** STS3215 reports `Present_Load` (a load estimate, % of
  max) and `Present_Current` (about 6.5 mA per count) over the serial bus at
  the bus's read rate. **Nothing in this repo reads either today**;
  `record_grip.py` reads only `Present_Position`, with torque off so the human
  back-drives the fingers.
- **Handheld mode has no force at all.** With torque off the servo is only an
  encoder. In handheld mode the motor isn't driving, so its current can't tell
  you anything. This affects the dataset as well as the robot.

The alternative is a **quasi-direct-drive (QDD) actuator**: a large-diameter
brushless motor, one planetary stage around 6–10:1, field-oriented control
and a magnetic encoder. At that ratio, motor current maps to output torque
well enough to sense force from it (the MIT Cheetah approach), the joint can
be back-driven by hand, and it can be told to behave like a spring. We already
have one in the repo's parts list: the **RobStride RS00** (10:1 planetary,
5 N·m rated / 14 N·m peak, 310 g, CAN), the B601-RS gripper motor, which
Base 10/11 can already mount (`motor_sts` 0). It is heavy for a hand-held
tool and expensive per unit, but it is exactly the actuator class this plan
wants.

QDD also helps with the handheld problem. A back-drivable motor held in
light impedance mode while the person squeezes reads the person's grip force
from its current, so handheld episodes can record force. A fallback that
needs no motor is compliant fin-ray fingers whose bend, seen by the stereo
cameras or the encoder, gives the force.

**Recommendation:** measure first; don't redesign yet. If the STS3215 at ~300:1
gives a clean, repeatable force signal on a scale test, keep it for stage 0
and 1. If it doesn't (expected), design the gripper around one small QDD
actuator and make that the **same actuator** used in the arm's wrist joints,
with a second, larger QDD for shoulder and elbow. That's the "one or two
actuator designs" target (RS00-class and RS06-class, as on the reBot B601-RS
we already chose).

## Designing for scale

- **Actuators are the cost.** Two designs, reused at every joint, so volume
  on one part drives the cost down. Each actuator is a sealed drop-in module
  with one plug-in connector (power + CAN), which is also the repair unit.
- **Structure:** stamped steel or die-cast aluminium links, injection-molded
  outer shell (the cute part), snap-fit from one direction, no loose wires:
  every module plugs into the one beside it.
- **Head:** the stereo pair at human eye spacing (~63 mm) and a height
  matched to a seated or standing person by the stool/counter choice.
- **Base:** weighted, so it can't tip over with a full payload at full reach;
  it sets the robot's mass and shipping cost (see open questions).
- **Price:** appliance-level. A bill-of-materials (BOM) model per stage (1k / 100k / 10M units) is a first
  pebble; without it "appliance price" is a hope.

## Ideas to evaluate (not decided)

| Idea | For | Against / risk |
| --- | --- | --- |
| **Cooking service first** (a kitchen where people cook with handheld grippers, then cells) | Revenue and cooking data from day one; the same rig as stage 1 | Food-safety licensing, a kitchen to run, slower than bare hands at first |
| **Factory cell = consumer robot** | One design, one dataset, every sold robot is a spare cell; volume on both sides | A kitchen robot's cuteness and safety costs ride along into the factory |
| **Cable-driven arms, motors in the base** | Light, safe arms; all actuators in one swappable module; weight lands in the base, where we want it | Cable stretch, tensioning and wear; threading cables is a hard step for gripper-only assembly; force through cables is noisier |
| **Robots repair robots by swapping modules** | Keeps the line running; follows from plug-in modules | Needs diagnosis to say which module failed |

## Open questions

1. Is STS3215 current/load at ~300:1 clean enough for force, or do we go QDD?
   (First pebble below answers it.)
2. How does a handheld episode record force: QDD impedance mode, finger bend,
   or not at all?
3. Can two parallel-jaw grippers do every assembly step, or does some step
   (cable routing, connectors, fine snaps) need a third finger or a powered
   tool the gripper holds? `gripper_bet.md` §4's two-finger ceiling applies here.
4. Reach, payload and base mass: what payload at what reach (a full pot at
   ~0.5 m?), and how heavy must the base be to stay upright on a counter or stool?
5. Where does the policy run (on the robot or in the cloud), and what does that
   compute cost per unit? Probably the second-largest cost after actuators.
6. Kitchen safety: knives, hot oil, a robot near people. What speed and force
   limits, what shell, what food-contact materials and washdown?
7. Magnets (NdFeB) and chips: which suppliers, and at what volume does lead
   time become the real limit?
8. Is cooking the right first market, or does the factory (robots building
   robots) come first and cooking follow?

## First pebbles to file (gripper and actuator first)

Not filed yet; listed for Jake's sign-off. Each would go to `agent/`.

1. **Measure gripper force from the servo.** Add `Present_Current` and
   `Present_Load` to `record_grip.py` (torque on, position control), squeeze a
   kitchen scale / load cell at several set points, plot reading vs force for
   closing and holding. Answers question 1. Small, code only.
2. **QDD gripper actuator study.** Compare the RS00 against a smaller
   gimbal-motor + single planetary + FOC driver for the hand: mass, cost at
   volume, torque, back-drive feel. Decide the one actuator for gripper + wrist.
3. **Gripper-only assembly audit of Base 15 / Gripper 22.** List every
   assembly step; mark each doable / not with two handheld grippers; propose
   the changes (snaps for screws, keyed plugs). The next Base version applies them.
4. **Second handheld gripper and a two-handed recording rig.** Two grippers,
   one per hand, plus the stereo headset from `shared_stereo_glasses.md`, so a
   bimanual build can be recorded.
5. **Handheld force recording.** Prototype QDD impedance mode, or a finger-bend
   estimate, so handheld episodes carry force.
6. **Torso sizing.** Reach, payload, base mass and tip-over for counter and
   stool heights; output is a block layout, not CAD.
7. **BOM cost model** at 1k / 100k / 10M for two actuator designs plus shell,
   head, compute and base.
8. **Cooking task list and kitchen safety requirements**, including the
   cooking-service option.
9. **Cable-driven vs joint-motor arm** research note.
