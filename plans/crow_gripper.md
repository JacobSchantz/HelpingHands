# The crow gripper — hook-led, and what that costs at the wrist

Status: **DECISION, no geometry cut yet.** The ask was to work out what a
hook-led end effector means for the SO-101's wrist mount and payload *before*
designing anything, and to say what was decided and why. This is that. The
parameters the hook would add are named in §8 and nothing has been drawn.

Reading order: [`gripper_bet.md`](gripper_bet.md) for why the end effector is
the argument at all, [`molmoact2.md`](molmoact2.md) for the north star,
[`../cad/openscad/crow/README.md`](../cad/openscad/crow/README.md) for the beak
that already exists on the bench model.

---

## 1. First, a correction to the premise — and it changes the design

The brief reasons: *New Caledonian crow → makes and uses hooked tools → so the
end effector should be hook-led.* The middle step is right and the jump is not.

**The New Caledonian crow's bill is not hooked.** It is conspicuously *less*
decurved than other corvids — a nearly straight culmen with an upturned lower
mandible. That straightness is not incidental; it is what lets the bird hold a
stick in line with the force it is applying. The hooks in the story are on the
**tools** the bird manufactures — hooked twigs and barbed pandanus leaves — not
on the animal. The crow's own gripper is a forceps.

So there are two different things the bird licenses, and they are not the same
project:

| reading | what it means here | verdict |
|---|---|---|
| **hooked beak** — put a claw on the end effector | a passive shape that carries load without squeezing | keep the *principle*, reject the literal claw — §5 |
| **hooked tool** — the gripper's job is to hold a hook | a chuck, so the tool is the end effector and it's swappable | already half-built (`crow_opening_for_rod`), and the better long game |

The honest version of "hook-led" is therefore **load carried by shape rather
than by pinch force**, which is a mechanical property, not a silhouette. That is
what the rest of this document decides against, and it turns out the strongest
argument for it has nothing to do with the bird — see §5.

## 2. What the SO-101 wrist actually offers

Everything below is measured geometry in the repo, not recollection. Sources:
`cad/openscad/params.scad` (tagged `[STEP]`/`[DERIVED]`/`[GUESS]`),
`cad/openscad/NOTES.md` §6, `lerobot_calibration/follower_right.json`.

**The mount is one flange and it is not negotiable.** The end effector bolts to
the `wrist_roll` servo horn: a Ø24 × 6 mm recess, Ø5.4 centre, four Ø3.2
clearance holes on a 9.9 mm square inside a Ø14 bolt circle, with Ø6 × 6
counterbores. That pattern, the servo cradle it sits above, the cable bore and
the fork are the entire arm interface. Everything above `fj_body_top_z = 38.0`
is ours to redraw; everything below it is the arm's.

**There is exactly one actuator and one channel.** The gripper is bus servo
**ID 6**, commanded as one number, `gripper.pos`, alongside the other five
joints — calibrated today at **1594–3018 ticks** against the stock jaws. There is
no second channel to add without adding a servo to the bus, and no force or
tactile feedback anywhere in the loop.

**The lever arms, from the pivot at (x 4.4, z 23.375):**

| contact point | height z | radius from pivot | force vs. the tip |
|---|---|---|---|
| fingertip | 105.375 | **83.78 mm** | 1.00× |
| tool notch | 78.0 | **56.69 mm** | 1.48× |
| commissure | 62.0 | **42.1 mm** | 1.99× |

(`crow_tip_arm` and `crow_notch_r` are echoed by the model on every compile; the
commissure figure is `hypot(-12.4 - 4.4, 62 - 23.375)`.)

**The consequence that settles the brief's "fewer actuated parts":** there are
none to remove. The SO-101 gripper is *already* one actuator and one degree of
freedom. The only number below one is zero, and §5 disqualifies zero. **So the
hook cannot pay for itself in part count — it has to pay in force and in
holding, or it does not pay.**

## 3. Payload — what the swap actually costs

The arm is quoted in [`voice-3c221288`](../pebbles/queue/voice-3c221288) at
**~413 mm reach and 0.5 kg payload**. That number is inherited from that plan
and has not been measured here; treat it as the working budget, not as a fact.

**Mass, measured.** A volume integral over the committed STL exports, solid
volume × 1.24 g/cm³ for PLA, and again at a realistic 40 % infill:

| part | volume | solid PLA | @40 % |
|---|---|---|---|
| stock fixed jaw (body + jaw) | 66.36 cm³ | 82.3 g | 37.0 g |
| stock moving jaw | 21.74 cm³ | 27.0 g | 12.1 g |
| **stock pair** | **88.10 cm³** | **109.3 g** | **49.1 g** |
| crow upper mandible (same body) | 66.04 cm³ | 81.9 g | 36.9 g |
| crow lower mandible | 21.02 cm³ | 26.1 g | 11.7 g |
| **crow pair** | **87.05 cm³** | **107.9 g** | **48.6 g** |

**The beak swap is payload-neutral: 1.2 % lighter, and the tip is at z = 105.375
in both, so the mass moment about the wrist is unchanged.** That is the baseline
any hook has to beat or match.

**The lever matters more than the mass.** 0.5 kg at the fingertip is 4.9 N acting
105.4 mm past the wrist_roll flange — 0.52 N·m of wrist pitch, against an
end-effector that weighs a tenth of that load. So the design question for payload
is not "how heavy is the hook" but **"how far out does the load hang"**:

- Load held in a throat at the **tool notch (z 78)** sits **27.4 mm closer** to
  the wrist than a fingertip pinch — a **26 % cut** in the end effector's share
  of the wrist moment.
- At the **commissure (z 62)**, 43.4 mm closer — **41 %**.
- Conversely, every 10 mm a claw adds past z = 105.375 adds ~9.5 % to that share,
  and ~2.4 % to the whole-arm moment at full extension.

**And grip force is free at the same place.** Same servo torque, 1.48× the normal
force at the notch and 1.99× at the commissure (§2). A hook that holds near the
root is both stronger and cheaper on payload, which is a rare direction where
the two constraints agree. **That agreement is the whole design, and it says the
hook goes at the back of the beak, not on the front of it.**

## 4. The grip force the stock arrangement can't give you

`hand_1_0.md` §2 already names the honest problem: the SO-101 is a chain of
position-controlled servos with no force sensing at the tip, so commanding a
position against an object gives you whatever force the geometry and the torque
limit happen to produce. It is not a controlled quantity.

A friction pinch needs it to be. Holding mass *m* on two faces takes normal force
N ≥ mg / 2μ — for 0.5 kg on printed PLA at μ ≈ 0.4, about 6 N, *sustained*, for
as long as the object is held, with a stalled servo and nothing measuring it.

A hook needs none of it. The load sits in a throat and is reacted by the throat's
walls; the actuator only has to keep the gate shut, and a gate that closes past
the load's escape line holds it at essentially zero holding torque. **That is the
real content of "grip by shape and leverage instead of pinch force", and it is a
direct answer to the one thing `hand_1_0.md` calls the least certain part of the
design.**

## 5. The north-star test: what a VLA can actually drive

From [`molmoact2.md`](molmoact2.md): the SO100/101 checkpoint observes **two RGB
streams plus joint positions and nothing else — no force, no tactile** — scores
**56.7 %** zero-shot out of distribution, and the paper calls zero-shot brittle.
Two things follow, and they point opposite ways.

**For the hook.** A model that cannot sense force cannot regulate it. Every gram
of holding that comes from geometry instead of from a commanded squeeze is
holding the policy does not have to close a loop on. On this observation space, a
shape-based grip is *strictly* easier to drive than a friction pinch. This is a
better argument for hook-led than the bird is.

**Against a passive hook.** A 0-DoF hook has no "close". The gripper channel the
policy emits would control nothing, and getting a load into and out of a passive
hook needs a specific approach-hook-lift-and-tilt trajectory. **That is precisely
the "bespoke scripted motion" the brief rules out.** Dropping to zero actuators
does not simplify the robot; it moves the mechanism into the policy, where it is
harder and where we have no way to train it.

**The residual risk, stated plainly:** the checkpoint's community training data
was recorded with the stock stepped jaws in frame. Any reshaped end effector is
an embodiment shift in the wrist camera's view, and we cannot know what it costs
zero-shot until there is a camera and a number. That is not an argument for never
changing the jaws; it is an argument for §6's D7.

## 6. The decision

**D1 — the arm interface does not move.** The horn pocket, bolt pattern, servo
cradle, cable bore, fork and jaw pivot stay exactly as `params.scad` has them,
as the existing beak already does. Changing them invalidates
`lerobot_calibration/` and buys nothing this design needs.

**D2 — one actuator stays, and so do open/close semantics.** Rejecting the 0-DoF
passive hook, on §5. `gripper.pos` keeps meaning "how open", so any policy that
can drive the stock gripper can drive this one. What changes is the actuator's
*job*: from "squeeze hard enough to hold" to "shut the gate".

**D3 — the hook is a gated throat, not a claw.** The hook feature is a closed
loop formed *between* the two mandibles when they shut — the upturned lower
mandible and the upper one bounding a pocket — rather than a barb hanging off one
jaw. A claw catches on things when it is open, which is a liability on an arm
driven by a brittle policy; a throat is inert until the gate closes.

**D4 — the throat goes at z ≈ 62–78, not at the tip.** §3: 1.48–1.99× the normal
force and 26–41 % less wrist moment, at the same servo torque and the same mass.
Both constraints point the same way and this is the only place they do.

**D5 — the tip stays at z = 105.375 and stays a working forceps.** The hook is a
*second grip mode at the root*, not a replacement for the tomial line. The tip is
what reaches into a gap and what has any chance on paper (`hand_1_0.md` §2), and
keeping the reach identical is what keeps §3's mass moment neutral and the
workspace unchanged.

**D6 — the existing V notch is the hooked-*tool* half of §1, and it stays.**
`crow_opening_for_rod()` already chucks a Ø6 rod with the beak essentially shut.
The throat sits beside it on the same tomial line, and the long game — the crow's
actual trick — is that the end effector holds a hook rather than being one.

**D7 — nothing gets printed until there is a wrist camera and a stock-jaw
baseline.** `molmoact2.md`'s cheapest-test-first applies here unchanged: the beak
and the hook are both bets against a stock jaw whose success rate on a real task
we have never measured. Printing first means paying for a shape we cannot score.

**What was rejected:** a passive 0-DoF hook (§5), a second servo for a
thumb/latch (fails "as little as possible" for a capability we haven't shown we
need), a claw past the fingertip (§3 payload, §6 D3 snag risk), and any change to
the wrist mount (D1).

## 7. What this does not settle

- **The 0.5 kg / 413 mm figures are inherited, not measured here.** Every
  percentage in §3 is a ratio and survives a correction to the absolute number,
  but the absolute headroom does not.
- **`jaw_pivot_x` / `jaw_pivot_z` are the one inferred pair in the whole model**
  (`NOTES.md` §6). Every lever arm in §2 is built on them. If they are wrong,
  both jaw sets and this entire analysis are wrong together, and calipers settle
  it.
- **No throat geometry exists yet**, so no interference proof exists for it
  either. The closed-form check in `crow_params.scad` assumes radius-from-pivot
  climbs monotonically along the tomium; a throat is a local *dip* in that radius
  and will trip the assert. Extending the proof to a piecewise-monotonic tomium
  is a prerequisite, not a detail.
- **Friction coefficient, spring rate and the real servo torque at ID 6 are all
  guesses.** §4's 6 N is an order-of-magnitude argument, not a spec.
- **Nothing here has touched hardware.** No print, no sheet of paper, no load.

## 8. Next step, and the loop it runs in

`Scripts/cadloop` is the loop for this, as the brief says — and it could not see
the crow model at all: it was hardwired to `cad/openscad/params.scad` and
`gripper.scad`. It now takes a target, so the beak can be iterated by voice on
its own parameters:

```bash
CADLOOP_TARGET=crow node Scripts/cadloop/cadloop.mjs
# "pebbles, design, open the beak 10 millimetres"
```

Only `crow_params.scad`'s own numbers are offered to the edit engine, and it
declares none of the mount dimensions — it `include`s the stock `params.scad` for
those. So **D1's freeze is enforced by the file layout**, not by care: the horn
pocket, the cradle and the pivot are unreachable from the loop by construction.

Wiring it up turned up a real bug in the loop, worth knowing about. `params.mjs`
scored a parameter "live" only if a geometry file named it directly. On the stock
gripper every station table is named directly by `moving_jaw.scad`, so this never
showed. On the beak, `crow_tomium`, `crow_culmen` and `crow_gonys` — the three
lists that *are* the beak's shape — are read only through `crow_tomium_x()` and
its siblings inside `crow_params.scad`, so they scored "indirect" and were never
offered to the edit engine. The loop would have rendered the beak and then
quietly refused to reshape it. Liveness now follows the params file's own
functions transitively. The stock model's seven refused dead names are unchanged
by that, which is the invariant that mattered.

The throat would add roughly five parameters, all to `crow_params.scad`:
`crow_throat_z` (where on the tomium), `crow_throat_d` (the bore it holds),
`crow_throat_depth`, `crow_throat_lip` (how far past the escape line the gate
shuts) and `crow_throat_r` (the root radius, which is where it will crack).

**Say the word and I'll cut it in the loop.** The one thing to react to first is
D4 — the hook at the back of the beak rather than the front of it — because
everything else follows from it.
