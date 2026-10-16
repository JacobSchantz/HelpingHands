# Agent-led robot research: a plan

Status: PLAN ONLY, for Jake to review. Nothing here is built yet (pebble
voice-8e72ea27, 2026-10-16).

## The goal, and what "done" means

Jake: *"I don't care how it happens, but we need to end up with a model where
we can set a task in front of it and it will just work on the task and get it
done."*

That is two capabilities, and the plan scores them separately:

1. **Doing a task** it was never trained on (generalization).
2. **Working until it is done**: noticing that it failed, retrying, and
   stopping once the task is complete (persistence). A model that succeeds 40%
   of the time per attempt but can see its own failures and retry is worth far
   more than a 60% model that stops after one attempt.

The headline number is therefore **held-out success within a time budget, with
retries allowed**, not single-attempt success. Every round also reports the
single-attempt rate so we can tell which of the two improved.

The rest of the plan follows one rule: **no change counts as progress unless
the scoreboard shows it.** The agent can try anything, but only the scoreboard
decides which changes are kept, and the agent cannot edit the scoreboard.

## 1. The scoreboard comes first

Nothing else gets built until the scoreboard can score MolmoAct2 zero-shot
and agrees with Jake's own judgement.

### 1a. Two suites: dev and exam

| | **Dev suite** | **Exam suite (held out)** |
|---|---|---|
| Who sees it | The agent, every round | Run only by the eval harness; the agent sees the scores, never the videos |
| Purpose | Fast iteration signal | Proof that the model got better at things it was not trained on |
| Training data from it | Allowed | **Never.** Exam objects, spots and wordings are banned from every dataset (enforced by manifest, §1e) |
| How often | Every round | Only when a candidate is up for promotion, at most once a week |
| Who adds tasks | The agent (new ids only) | Jake, privately. The agent never writes exam tasks |

The seed of the dev suite is `robot_eval/tasks.json`: six frozen tasks on a
marked mat. The exam suite holds the same *kinds* of task with things the
model has not seen:

- **Unseen spots**: a second arc of spots F–J, never used in data collection.
- **Unseen objects**: for example a yellow cylinder, a wooden block, an
  envelope instead of the A6 card.
- **Unseen wording**: "drop the cube into the dish" for "put the block in the
  bowl".
- **Unseen compositions**: tasks that chain two dev skills ("put the block on
  the card").

The agent iterating on a fixed eval set is how leaderboards get overfit
([this already happened to RoboArena](https://itcanthink.substack.com/p/what-do-robotics-leaderboards-tell)).
Hiding the exam suite is the defence. If the dev score climbs and the exam
score does not, the round failed, whatever the dev number says.

### 1b. Fixed reset start states

Each trial starts from a **start state**: the arm's home pose plus the object
layout. Start states are generated once per task (spot, object rotation in 30°
steps, distractor placement), saved as `start_states/<task>.json`, and given
ids. Every candidate model is run on **the same start-state ids**. This turns
"model A vs model B" into a paired comparison, which needs roughly half the
trials of an unpaired one (§1d).

The arm's home pose is commanded and checked from joint readings. The object
layout is verified by the judge camera before the trial starts (§1c): if the
cube is more than 1 cm from its target, the trial does not start, and the
reset runs again or a human is asked to fix it.

### 1c. Automatic camera-judged pass/fail

- **A judge camera that is not a policy input.** A fixed overhead USB camera
  looking straight down at the mat. It is never fed to the model, so it does
  not break the human-mirror rule, and the model cannot learn to fool it.
  (For lift checks, the head stereo pair adds a side view.)
- **Judge rules are code, not a language model, wherever possible.** The mat
  gets a printed fiducial (ArUco) at each corner, so the overhead image maps
  to mat coordinates. "Block in bowl" is then "red pixels inside the bowl's
  circle". "Lifted 5 cm and held 3 s" comes from the stereo pair. "Card moved
  left 5 cm" is a centroid displacement. Each rubric line in `tasks.json`
  becomes one function.
- **A vision-language model judges only what code cannot**, for example
  "card not crumpled". It gets the before/after frames and a yes/no question,
  and its answers are calibrated like any other judge.
- **The judge must pass before it counts.** Jake labels 100 recorded trials by
  hand (about 30 minutes at 2× speed). The judge must agree on at least 95% of
  them, per task, before that task's automatic scores are used. Every round
  afterwards, 10% of trials go to Jake for a spot audit. If agreement drops,
  the task falls back to human scoring until the judge is fixed.
- **Every trial keeps its full video** (head stereo + judge cam + joint log),
  so any score can be checked later.

### 1d. Enough trials to separate real gains from noise

The current suite runs 5 trials per task. That cannot tell anything apart:
3/5 successes has a 95% interval of **23%–88%**. Numbers for a single task:

| Trials | Observed 50% means the true rate is (95% Wilson) |
|---|---|
| 5 | 23%–88% |
| 30 | 33%–67% |
| 50 | 37%–63% |
| 100 | 40%–60% |

Comparing two models is cheaper when it is **paired**: both run on the same
start states, so only the start states where they disagree carry signal (an
exact McNemar test). Assuming about 30% of start states give discordant
results, a one-sided test at α=0.05 with 80% power needs:

| Real gain | Paired start states needed | Unpaired, for comparison |
|---|---|---|
| +20 points | ~45 | ~75 per model |
| +15 points | ~70 | ~135 per model |
| +10 points | ~120 | ~300 per model |

So:

- **Dev round:** 30 trials on the task being worked on. It shows only large
  changes and catches breakage, and it is cheap.
- **Promotion gate:** the candidate and the current best ("incumbent") each
  run the same **50 exam start states**, interleaved in random order (so
  lighting drift and servo wear hit both equally). That is 100 trials, about
  2.5 hours at ~90 s per trial including reset. It reliably detects a
  20-point gain. Smaller gains are reported as "not shown", and the plan does
  not claim them.
- **Promotion rule:** promote the candidate only if (a) the paired exact test
  gives p < 0.05 on the exam suite, and (b) no previously solved task drops
  by more than 10 points on its dev check. Otherwise the incumbent stays.
- **Re-running the incumbent every gate** is not wasted time. It also
  measures whether the *rig* drifted (worn servo, changed lighting). If the
  incumbent's score moves on its own, the gate is void.
- **Pre-registration.** Before each gate, the agent writes down what it
  changed and the gain it expects. The ledger keeps both, so the agent cannot
  pick, after the fact, the comparison that happened to look good.

### 1e. Trend tracking and data hygiene

- `research/ledger.csv`: one row per trial (round, model hash, task, start
  state, judge verdict, human audit verdict, seconds, retries, human
  interventions, servo max temperature).
- `research/rounds.md`: one entry per round, with the hypothesis, change,
  compute cost, human minutes, and dev and exam results with intervals.
- A chart of exam success rate per promoted model, with 95% intervals, plus a
  separate line for human minutes spent per percentage point gained. It
  extends `robot_eval/leaderboard.py`.
- **Dataset manifest:** every episode used for training is listed with its
  hash, task, objects and spots. Before training starts, a check refuses any
  dataset that contains an exam object, spot or wording. The eval code,
  `tasks.json` and the start states are hashed. Changing them needs Jake's
  sign-off, because an agent that can edit its own exam can make any number
  go up.

## 2. The research loop

```
       ┌──────────── research agent (Claude, with Jake) ────────────┐
       │ read ledger → pick weakest task / failure mode → hypothesis │
       └──┬──────────────┬───────────────┬───────────────┬──────────┘
          │              │               │               │
   human demos     autonomous      scripted/sim      training run
   (human-lane     practice        motions           (rented GPU,
    pebble)        (judge-labelled) (if it helps)     LoRA first)
          └──────────────┴───────┬───────┴───────────────┘
                                 ▼
                   candidate checkpoint → dev round (30)
                                 ▼  looks better?
                   promotion gate (50 paired exam states)
                                 ▼
                 promote or discard → ledger, chart, Jake's weekly note
```

The agent picks its next move by looking at **where the failures are**, using
the per-rubric-line scores (does it fail at reaching, grasping or releasing?)
and the failure videos. Its tools, from cheapest to most expensive:

1. **Prompt and inference settings**: instruction wording, action-chunk
   length, the "Think" depth mode, the camera mapping. No training needed.
2. **Autonomous practice**: run the current model on dev start states
   unattended, let the judge label every rollout, and keep the successes as
   new training data (filtered behaviour cloning). This is the main way to get
   improvement without spending Jake's time, so it gets built early.
3. **Human corrections**: Jake watches a practice run and takes over with the
   leader arm when it is about to fail. The takeover segment is recorded as a
   correction (a DAgger-style intervention). One minute of correction is worth
   more than a minute of fresh demos, because it targets exactly where the
   model goes wrong.
4. **Fresh human demonstrations**: requested through pebbles (§4).
5. **Scripted motions and sim**: scripted grasps for the auto-reset (§3) and
   as cheap data for simple reaches. Sim (`plans/simulated_training.md`,
   `plans/lehome_pillowcase.md`) only if real data turns out to be the
   bottleneck. Sim data still has to show gains on the real exam suite.
6. **Training runs**: LoRA fine-tune of MolmoAct2 first (LeRobot's
   recommended recipe below ~200 demos). Full fine-tunes and other base
   models (SmolVLA, π0.5, from `plans/robot_model_scouting.md`) count as
   candidates too, and go through the same gate.

**"Work until done" is its own layer.** The policy only produces motions. On
top of it, a supervisor loop (the research agent at first, a small model
later) watches the head cameras, asks "is the task done?" using the same
judge functions, and if not, resets the arm to a safe pose and re-issues the
instruction. If needed it breaks the task into sub-instructions ("pick up the
block", then "put it in the bowl"). Exam trials allow retries until the time
budget runs out, and the ledger counts how many were used. A long task we
cannot script a judge for becomes the open-world test at the end (§9,
step 4).

**Jake's input.** Every Monday the agent posts a short note as a pebble: the
chart, what it tried, what worked, what it wants to try next, and what it needs
from Jake (demos, money, a new fixture). Jake approves or redirects. Between
notes the agent works within the budgets below without asking.

## 3. Auto-reset fixtures

Autonomous practice only works if the scene resets itself. A human resetting
every trial caps the loop at what Jake can sit through. Plan, cheapest first:

- **Robot resets itself with a scripted grasp.** The judge camera knows where
  the cube is in mat coordinates (fiducials). For a 3 cm cube on a flat mat,
  a scripted top-down grasp computed by inverse kinematics is reliable, and
  needs no learning. After each trial the arm picks the cube from wherever it
  ended up and places it on the next start state's spot. This works for the
  block tasks.
- **A funnel bowl.** For block-in-bowl, the bowl has a hole and a chute under
  the mat that returns the cube to a fixed pick-up pocket. Success resets
  itself mechanically, and the scripted grasp takes it from the pocket. This
  is a 3D-printed part, and it fits the existing `cad/` workflow.
- **Mat boundary walls** (a 2 cm lip) so a knocked cube cannot leave the
  reachable area.
- **The card tasks are harder.** A flat card can be slid back by a scripted
  push against a printed corner stop, but a crumpled or flipped card needs a
  human. These tasks run with "human resets" at first, and it shows in the
  ledger as human minutes.
- **When the reset fails,** the harness pauses and files a human-lane pebble
  ("cube off the mat, please put it back") instead of continuing with an
  unverified start state.

Target: at least 20 unattended trials in a row on pick_block and
block_in_bowl before relying on autonomous practice.

## 4. The data-request workflow

The agent asks for human time the same way Jake asks the agent for work: as
a pebble. A request is filed in the human lane and looks like this:

> **Record 20 demos: pick_block, spots A–E, cube rotated 0/45°**
> Why: the dev round shows 9/15 grasp failures happen when the cube is
> rotated, and only 2 of our 60 demos have a rotated cube.
> Setup: mat + head stereo rig, leader arm. ~25 min.
> Expected effect: grasp line +15 points on dev. Checked at the next gate.
> Variation sheet: (generated list, one line per demo: spot, rotation,
> distractor)

Rules:

- **Every request names the failure it targets and a predicted gain.** The
  next round's ledger entry reports whether the gain happened. Over time this
  shows which kinds of requests are worth Jake's time.
- **Human-time budget:** at most 2 hours per week of requested human time by
  default. Asking for more needs a line in the Monday note.
- **The recording tool generates the variation sheet** and shows the next
  setup on screen, so demos cover the space and are not 20 copies of the
  easiest layout.
- **Demos are judged as well.** A demo the judge scores as failed is kept as a
  labelled failure, not trained on as a success.
- **Other humans:** the same pebble can be picked up by anyone with a rig. The
  ledger records who demonstrated, so we can see whether one person's demos
  train better than another's.

## 5. Compute budget

Prices seen on 2026-10-16 (`plans/robot_model_scouting.md`): RunPod RTX 4090
24 GB $0.34/h, RTX A6000 48 GB $0.33/h. An H100 for training is about
$2–3/h (unverified; check before renting).

| Use | GPU | Rough hours/week | Rough $/week |
|---|---|---|---|
| Inference during dev rounds, practice and gates | 4090 | 15–25 | $5–9 |
| LoRA fine-tunes (2–3 per week) | A6000 or H100 | 6–15 | $10–40 |
| **Default weekly cap** | | | **$50** |

- **Hard caps in code:** every rental gets `--timeout`, and `rent.py down`
  runs on exit. A training job that goes 2× over its estimate is killed and
  noted in the ledger.
- **The cap is raised only via the Monday note,** with the case for it (for
  example "a full fine-tune is the only thing left to try on X, estimated $60").
- **Ledger tracks $ per promoted percentage point,** next to human minutes per
  point.
- How long a MolmoAct2 LoRA run takes on our data size is **not yet measured**.
  The first training run measures it, and these numbers get corrected.

## 6. Safety and hardware wear

The arm will run for hours with no human holding a leader arm. This is the
part that can hurt someone or destroy a servo.

- **Hard stop that cuts power.** A physical mushroom switch on the servo power
  supply, within reach of the bench. The software stop already in the
  `robot_eval` client is not enough on its own for unattended runs.
- **Workspace box and joint limits** on the Mac side, enforced on every
  action before it reaches the bus. Any action outside the box, too far from
  the current pose (existing first-action guard), or non-finite: stop.
- **Watchdog:** no fresh observation or action for 500 ms → hold position,
  then go to rest pose. Never replay queued actions after a reconnect (already
  the rule in `molmoact2_deployment.md`).
- **Servo telemetry every trial:** temperature, load and voltage from the
  STS3215 registers go into the ledger. Above a temperature threshold the arm
  rests until it cools. (The threshold is to be set from the datasheet; it is
  not chosen yet.) Rest 1 minute every 10 trials by default.
- **Stall detection:** commanded vs actual position error above a threshold
  for over 1 s (pressing into the table, crushing the cube) → torque off.
- **Wear check each gate:** the arm visits 5 calibration poses, and the judge
  camera measures where the gripper actually ends up. Growing error means
  backlash or a slipping horn. The incumbent re-run (§1d) catches this from
  the score side as well.
- **Spares on hand:** two spare STS3215 servos and a spare gripper horn, so a
  worn joint costs an hour and not a week.
- **Unattended only after it is earned.** Supervised runs until there have
  been 10 hours with no safety stop and no stall. After that, unattended runs
  only during hours Jake picks, with the head camera streaming to his phone.
  No person or pet in the workspace while it runs.

## 7. The human-mirror camera setup

From `plans/hand_1_0.md`: the **only policy cameras are two stereo cameras at
eye height.** The demonstrator wears them, and the robot carries the same pair
at head height behind the arm. No wrist camera.

- **One rig, two mounts.** The same stereo module, the same lenses and the same
  baseline, with a head strap for the human and a mast clamp for the robot. The
  mast mount is fixed and pinned so it returns to the same pose after removal.
  Its pose is checked against the mat fiducials at the start of every gate,
  and the gate does not start if the camera moved.
- **Mismatch with MolmoAct2.** The SO-101 checkpoint was trained on top + side
  views, not a near-parallel stereo pair. Zero-shot results with our cameras
  may therefore be worse than published. That is fine: the baseline measures
  it, and fine-tuning on our own camera data is the fix. If the head-camera
  baseline is near zero on every task, the agent may *ask* to add a temporary
  top camera for a diagnostic run. That is Jake's call, since it breaks the
  principle.
- **First milestone uses robot-mounted cameras with leader-arm teleop only.**
  Head-worn human demos with the handheld gripper (`handheld_gripper.md`) add
  a second embodiment gap (human head motion, a human hand in view). They
  come after the loop is shown to climb on the easy case.

## 8. First milestone: prove the loop climbs

Narrow on purpose: **one arm (follower_right), the stock jaw, red cube, mat,
funnel bowl.** Hand 1.0 and paper come later, because the milestone is about
the *loop*, not the hardest task.

**Steps:**

1. **Build the scoreboard:** overhead judge camera, fiducial mat, judge
   functions for `touch_block`, `pick_block` and `block_in_bowl`, start-state
   files, ledger, chart. Jake labels 100 trials, and the judge must reach 95%
   agreement.
2. **Build the auto-reset:** scripted cube grasp, funnel bowl, mat walls.
   Reach 20 unattended resets in a row.
3. **Baseline:** zero-shot MolmoAct2 on the dev and exam suites. This is the
   first point on the chart. Every later gate compares against it.
4. **Three agent-led rounds**, each with a prediction recorded beforehand,
   using any mix of practice, corrections, requested demos and LoRA runs.

**Milestone passes when** a promoted model beats the zero-shot baseline on the
**exam** version of `block_in_bowl` (unseen spots F–J and an unseen object),
with a paired exact test p < 0.05 over 50 start states, and:

- judge agreement on audited trials stays ≥ 95%;
- the gain survives a re-run of both models a week later (so it is not a rig
  artefact);
- total spend is ≤ $150 and ≤ 6 hours of Jake's time across the milestone.

**Milestone fails usefully** if three rounds produce no exam gain. The ledger
then shows which of these it was: the dev score did not move (a data or
training problem), the dev score moved but the exam score did not
(overfitting), or the judge disagreed with Jake (a scoreboard problem). Each
has a different next step.

## 9. After the milestone, toward "any task"

In order, each one only after the previous one shows a gain at the gate:

1. Widen the dev suite: all six `tasks.json` tasks, then new tasks the agent
   proposes (new ids, frozen once scored).
2. Hand 1.0 on paper (`pick_paper`), as its own leaderboard split, the same way
   `leaderboard.py` already separates end effectors.
3. Head-worn human demos through the handheld gripper, to see whether human
   demos are cheaper per point than teleop.
4. **The open-world test:** Jake puts an object and a sentence the system has
   never seen in front of it ("put the pen in the mug"), with no judge code.
   The supervisor loop decides when it is done, and Jake scores it. This is the
   closest measurement of the north-star goal, and it runs every month
   regardless of other results.

## What Jake needs to decide before anything is built

1. **Is "held-out success within a time budget, with retries" the right
   headline number?** It is the plan's reading of "just works on it until
   it's done".
2. **The overhead judge camera:** OK as a scoring-only camera, given the
   human-mirror rule covers only policy cameras?
3. **Default budgets:** $50/week of compute, 2 hours/week of requested human
   time, and the $150 / 6 hour cap for the first milestone.
4. **Jake writes the exam tasks privately.** Is that workable, or should a
   second agent write them in a place the research agent cannot read?
5. **First milestone scope:** a cube with the stock jaw, not paper with
   Hand 1.0. Is that narrow enough, or too far from what matters?

## Unverified assumptions in this plan

- Fine-tune duration and cost for MolmoAct2 LoRA on our data: not measured.
- The H100 price: not checked today.
- That a scripted top-down grasp resets a 3 cm cube reliably: plausible, not
  tested.
- MolmoAct2's zero-shot performance with eye-height stereo cameras: unknown,
  and possibly near zero (§7).
- The ~30% discordance used for the trial counts in §1d is an assumption. The
  first gate measures it, and the trial counts get recomputed from it.
- The servo temperature threshold: to be read from the STS3215 datasheet.
