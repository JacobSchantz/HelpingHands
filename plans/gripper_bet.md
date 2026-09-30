# The Gripper Bet — humans drive the hardware, and the hand is the glove

Status: THESIS (Jake's, spoken 2026-09-13; the last requirement is cut off).
Roadmap: **Hand 1.0** (SO-101-like, near-term) → **Hand 2.0** (human hand = glove).

## The claim being reacted to

There is talk that a company called **Generalist Robotics** has had "the GPT
moment for robotics" — that they found something true about robotics the way
ChatGPT found that the transformer is true for language models.

> **Unverified.** This is a recollection of industry chatter, not a checked
> fact. The company name, the claim, and the framing are recorded as heard.
> No paper or release has been read, deliberately.
>
> **Update 2026-09-30:** it is **Generalist AI** (GEN-0/GEN-1/GEN-1.5), and
> their data comes from low-cost wearable devices on humans. All proprietary.
> See `plans/handheld_gripper.md` §0.

Their own read on it may be that the breakthrough is the **grippers** —
simple two-finger pinchers, cheap to build and easy to articulate. Jake's
position is that this is the wrong thing to credit.

## 1. The real breakthrough is teleoperation

The thing that is actually true is **the ability to use humans to drive the
hardware**. That is the discovery. Humans supply the policy, in real time,
through the machine — and everything downstream, including which end effector
you bolt on, follows from having that loop work.

The gripper is not the insight. It is a consequence of the insight: once
humans can drive the hardware, you pick whatever end effector makes that loop
cheap and repeatable, and the pincher happens to be that.

## 2. Proprioception at the point of contact

The reason the loop works is that the hardware **knows its own controls and
its position in space**. Tesla knows the car's controls and its position in
space; the gripper likewise knows its controls and its position in space.
Same shape of problem, different scale.

And this matters because **final contact with the world is the hardest part**
of the whole problem. Everything before contact is motion planning in free
space. At contact, the world pushes back, and the only thing that saves you
is knowing exactly where you are and exactly what you commanded. That is
where the difficulty concentrates, so that is where the fidelity has to be.

## 3. Minimal sufficient hardware

The design principle, in his words: **as little as possible, but as much as
you need.**

Applied here: we truly do need grippers — some end effector — to interact
with the world at all. You cannot subtract contact hardware to zero. So the
question is never "can we avoid the hand," it is "what is the least hand that
is still enough."

*This principle is in tension with the next claim, and that tension is the
interesting part of the argument.* Claim 3 pushes toward the simplest thing
that works; claim 4 says the simplest thing is leaving value on the table.
Jake is holding both, which means the real position is: minimal **for the
capability you actually need** — and he thinks the needed capability is
higher than a two-finger gripper delivers.

## 4. Where he departs: hardware capability is undervalued

What Generalist may not be getting right is **the capabilities of that
hardware**. The more capable the end effector is, the more value it provides.
A pincher that can only pinch caps how much of the world the system can touch,
no matter how good the training or the teleop loop gets.

So his bet: **we do need a human hand.** Not a better two-finger gripper — an
actual multi-finger hand, because that is the capability level the tasks
worth doing require.

## The roadmap — Hand 1.0 and Hand 2.0

The bet ships in two named stages. Later documents should just say **Hand
1.0** and **Hand 2.0** and be understood.

| | **Hand 1.0** | **Hand 2.0** |
|---|---|---|
| what | closely modeled on the SO-101 arms | a human hand, identical to the glove |
| fingers | conventional gripper | multi-finger |
| made how | as the SO-101 is made | fully 3D printed, both halves |
| role | the foundation | the bet |

**Hand 1.0** is deliberately conventional — *"something super similar to"* the
SO-101 arms already on the bench. It is the near-term, buildable step, and its
whole job is to get the teleop-and-record loop working end to end on hardware
Jake already understands and already has tooling for: `teleop.sh`,
`record_actions.sh`, and the calibration files in `lerobot_calibration/`. This
is the foundation, not a throwaway prototype. Nothing about it is a placeholder
to be embarrassed by; it is the working system everything else is measured on.

**Hand 2.0** is the human hand with the identical-to-the-glove constraint,
fully 3D printable — the bet described in the two sections below.

**Why 1.0 has to exist first:** with it running, the identity constraint of 2.0
can be tested against a working baseline instead of argued in the abstract.
Hand 1.0 yields a conventional-gripper data pipeline — demos, action spaces,
success rates — and Hand 2.0's claim is precisely that removing the retargeting
layer does better than that. Without the baseline there is nothing to be better
*than*, and the hypothesis in section 5 stays unfalsifiable.

## 5. Hand 2.0: the identity constraint — hand and glove must be identical

This is the sharp idea, and it is the one to test.

The robot hand and the teleoperation glove must be **identical**. Not
similar. Not kinematically mapped. Not "close enough with a calibration
step." He stressed the word: *I literally mean identical.*

Why that is a real claim and not a detail: every teleop stack today has a
**retargeting layer** between the human demonstration and the robot
execution — human joint angles get translated into robot joint angles through
some mapping, and that mapping is where error, loss, and ambiguity live. Two
different mechanisms with different link lengths, different joint limits, and
different numbers of degrees of freedom can never agree exactly, so the
translation is always lossy, and the loss shows up precisely at the moment
that matters most: contact.

If the glove and the hand are the same mechanism, that layer **collapses to
nothing**. What the glove records *is* what the hand does. Joint for joint,
limit for limit, one to one. The demonstration and the execution are the same
trajectory in the same coordinates, so there is nothing left to mistranslate.

That also means the demonstration data is native to the robot. Every
recording is already in the robot's own action space — no post-hoc mapping,
no retargeting error baked into the dataset.

**Treat this as a hypothesis worth testing, not as established fact.** It is
an unusually clean idea, which is exactly why it should be checked rather
than assumed.

## 6. Hand 2.0: fully 3D printable — both halves

Hard requirement on the glove *and* the hand: **fully 3D printable.**

This follows from the identity constraint rather than sitting beside it. If
the two must be identical, the cheapest way to guarantee identity is to print
both from the same source geometry — identity becomes a property of the file,
not of a manufacturing tolerance. Print, test, revise, reprint. Cheap,
reproducible, iterable, and anyone can reproduce the pair.

## What this means for what's already in this repo

- **The teleop scripts are already the right half of the loop.**
  `teleop.sh` and `record_actions.sh` are humans driving hardware and the
  recording of it — exactly the mechanism claim 1 says is the real
  breakthrough. That half is not speculative here; it is running on the
  bench. What this thesis changes is the *end effector* on the far side of
  it, not the loop itself.
- **The SO-101 arm work gets reframed.** The follower's two-finger gripper is
  the pincher under discussion. Under claim 4 it is a capability ceiling, and
  under claim 5 the leader/follower pairing is the closest thing here to the
  identity idea already — a leader arm the human drives and a follower that
  mirrors it. The hand/glove proposal is that same relationship taken to the
  end effector and made exact. Hand 1.0 is this hardware, kept close on
  purpose.
- **`plans/simulated_training.md`** assumes demos recorded through the
  existing gripper. If the hand changes, that pipeline's action space changes
  with it — worth knowing before investing in augmentation built around the
  current one.
- **The Tool Caddy (`plans/tool_caddy.md`)** is where a two-finger hand would
  show its limits first. Handing a drill to a person is a grip the human has
  to be able to take *out*, and that is a capability argument, not a
  simplicity argument. It is a good early test of claim 4.

## Open questions this plan leaves

- **The last requirement is unknown.** The spoken note cuts off mid-sentence
  after "fully 3D printable" — *"So we need to get..."* — and the thought is
  unfinished. More may follow; this document should be updated when it does.
- How many degrees of freedom does "a human hand" mean in practice? Claim 3
  says as little as possible; claim 4 says more capable is more valuable. The
  number that satisfies both is not yet named.
- Identical how, exactly? Same geometry is printable, but the glove must
  *sense* while the hand must *actuate*. Does "identical" mean identical
  kinematics with different internals, or identical parts throughout?
- Can a fully 3D-printed hand survive real contact forces, and for how many
  cycles? Printability and durability pull against each other.
- Does the glove need force feedback, or is position-only enough given that
  the hard part is contact?
- What would actually falsify the identity hypothesis? Worth naming a test
  before building the hand — and the comparison should be against Hand 1.0's
  own numbers.
- How close is "super similar" for Hand 1.0 — the SO-101 gripper as-is, or a
  variant? The closer it stays, the more of the existing calibration and
  scripts carry over unchanged.


## Shared sensing roadmap — Jake's direction, 2026-09-30

The first milestone is the existing SO-101, stock gripper, ordinary RGB
cameras and MolmoAct2; see `molmoact2.md`. The following longer-term design
must not hold up that working baseline.

The eventual wearable capture system should use binocular/stereo cameras in
lightweight glasses and instrumented gloves. Aim to mount the same sensing
hardware on a person or the robot and record comparable observations. Require
accessible timestamped camera streams, calibration and synchronized hand/tool
measurements; consumer “AI glasses” branding alone does not establish these
capabilities. Choose hardware after verifying access to these data.

In parallel, develop the New Caledonian crow-shaped gripper as a device both a
human can hold to manipulate objects and an SO-101 can carry. Preserve the
same contact geometry between demonstration and deployment. Start collecting
human demonstrations with the actual gripper before relying on bare-hand or
glove demonstrations. Track tool pose, grip opening/state and, when available,
contact/force alongside video. Glove data must be mapped to the gripper's
available actions; shared cameras alone do not solve that mapping. Human
reach and motion also need checking against the robot's kinematic limits.

Evaluate task success and the quantity of demonstrations actually needed;
do not assume that this eliminates embodiment differences or guarantees
medium-data learning. Retain open-source model/post-training options and
portable recordings so the cameras and demonstrations outlast one model.

The later outdoor mobile platform may combine batteries, solar panels, a Mac
mini, mounted iPad and connectivity. The separate first mobility milestone is
battery-continuous unplugging, driving and reconnecting to a normal wall
outlet, with cord management. Neither mobility nor solar is a prerequisite
for the tabletop model trial. Existing gripper and mobility pebbles retain
those workstreams.
