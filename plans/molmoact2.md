# MolmoAct2 — the VLA north star, checked against this repo

Status: FINDINGS + RECOMMENDATION (2026-09-20). No code written yet, by request.

Prompted by Jake's note: "this video is the direction" —
https://www.youtube.com/watch?v=itGeItWc2rw, *"Can this VLA Work with no
Dataset? I Put MolmoAct2 to Test"*.

Sources read for this: the MolmoAct2 paper (arXiv 2605.02881), Ai2's release
post, and — the useful one — LeRobot's own MolmoAct2 policy page,
https://huggingface.co/docs/lerobot/main/en/molmoact2, which documents real
hardware deployment on SO-100/101. **I could not get a transcript of the
video**, so the answer to its title question below comes from the paper, not
from whatever the creator found. If the video shows something different, this
doc is wrong at the top and should be redone.

---

## 1. The video's question already has an answer in the paper, and it is "not yet"

Ai2 reports MolmoAct2's out-of-distribution zero-shot real-world success —
unseen objects, randomly initialised camera poses — as:

| Checkpoint | Zero-shot OOD success |
|---|---|
| MolmoAct2-DROID (Franka) | 87.1% |
| **MolmoAct2-SO100/101 (our arms)** | **56.7%** |

And the paper says so itself, in its own limitations: zero-shot performance
"remains brittle," and success rates on realistic tasks "fall well below the
threshold required for dependable deployment" without task-specific adaptation.

**Second thing, and it's the one the video's framing hides: "no dataset" means
"no dataset for *your* task."** `MolmoAct2-SO100_101` is not an un-finetuned
model. It is a checkpoint fine-tuned on a large corpus of community SO-100/101
data that Ai2 had to put through a four-stage filter to strip mislabelled and
low-quality trajectories. There is still a dataset. It just isn't ours, and we
didn't have to record it.

That distinction is the whole value, and it's real: **the 50–200 demos per task
in `plans/training_pipeline.md` and `plans/simulated_training.md` stop being the
price of admission.** You get a first attempt for free and pay demos only to
close the gap. That is a genuine change in what this project has to do. It is
not "point a camera at it and speak."

---

## 2. Three hard requirements this repo does not currently meet

### a) Cameras. We have zero.

This is the big one. `record_actions.sh` records six joint floats at 20 Hz and
nothing else. `training_pipeline.md` says, in as many words, *"Recommendation:
Start position-only, add vision later."*

A vision-language-action model without vision is nothing. MolmoAct2-SO100_101
expects **two RGB streams** — `observation.images.cam0` (primary/scene) and
`cam1` (secondary, typically wrist) — at 640×480/30fps. So the standing
recommendation in `training_pipeline.md` inverts: **vision goes from "later" to
"first," and it is the only thing blocking every other step below.**

Note this also lines up with `plans/hand_1_0.md`, which already specs a camera
on the gripper for exactly the no-domain-gap reason. The wrist cam MolmoAct2
wants and the Hand 1.0 cam are plausibly the same camera.

### b) An NVIDIA GPU. We have none, and this is a wall, not a difficulty.

LeRobot's page is blunt: *"To run the models in this repository, you need an
NVIDIA GPU."* It's a 4B-parameter Molmo2-ER backbone plus a 36-layer
flow-matching action expert; the port's own training note quotes 55 GiB peak.
There is no Apple Silicon path — the same wall already documented in
`Scripts/lehome_sim_bootstrap.sh` and `plans/lehome_pillowcase.md`.

The mitigating detail: **we only need inference**, and MolmoAct2 emits action
*chunks* rather than one action per frame, so the arm's serial loop and the
policy don't have to live on the same machine. A rented Linux box running the
policy, with the Mac keeping the 30 Hz serial control loop, fits the existing
"control loop stays in native Terminal.app" rule in `teleop.sh` rather than
fighting it.

### c) A calibration gotcha that will drive the arm backwards

The SO-100/101 checkpoint was trained under the pre-0.5.0 LeRobot joint
convention. Without a frame correction the arm moves the wrong way. The fix,
per LeRobot's docs:

- `joint_signs: [1, -1, 1, 1, 1, 1]` (flips `shoulder_lift`)
- `joint_offsets: [0, 90, 90, 0, 0, 0]` (shifts `shoulder_lift`, `elbow_flex`)

**The converted checkpoint `lerobot/MolmoAct2-SO100_101-LeRobot` already bakes
this into its processor. The raw `allenai/MolmoAct2-SO100_101` does not.** Use
the LeRobot one, or expect a confusing first session with a healthy arm doing
the wrong thing.

---

## 3. What the app's job becomes

`HelpingHands/ContentView.swift` is today a static dashboard: two arm-config
cards, a plans link, a CAD link. There is no `URLSession` anywhere under
`HelpingHands/` — **the app has never talked to the robot.** All control is
shell scripts on the Mac.

If a VLA does perception and planning, the app's job is **to be the instruction
and the eyes — not the controller.**

- **The instruction is the product surface.** `lerobot-rollout` takes
  `--task="pick up the red cube"`. That string is the entire user interface of a
  VLA robot. We already have the voice half built and working:
  `Plans/PlanVoiceControl.swift` and `PlanNarrator.swift` do hands-free speech
  in this app today.
- **The phone is a camera.** An iPhone is a better `cam0` than a USB webcam and
  it's already in the room. Worth testing, though a wired webcam is the
  lower-risk first move for latency reasons.
- **What it must gain is a stop button and a live readout.** Right now the only
  way to stop the arm is Ctrl+C in a Terminal window. An autonomous policy
  moving a real arm raises that from a papercut to the first thing to build.
- **What it does not become is a teleop UI.** It never was one, and the jitter
  warning in `teleop.sh` says it shouldn't be.

---

## 4. What this does NOT change — the gripper bet survives

`plans/gripper_bet.md` argues the breakthrough is humans driving hardware, and
that **final contact with the world is the hardest part**. Nothing in MolmoAct2
touches that. Its observation space is RGB plus joint positions — **there is no
force or tactile input anywhere in it** — and its brittleness shows up exactly
at contact. Hand 1.0 and the teleop loop are not obsoleted. What the VLA
replaces is the *dataset-per-task middle*, not the end-effector thesis.

**One real tension worth Jake's call, though.** `plans/iBackpack.md` proposes
recording human-arm video and human-teleop data in order to learn a mapping from
raw video → servo positions. That is, in effect, building a VLA from scratch.
MolmoAct2 is that mapping, already trained, Apache-2.0, with our exact arms
supported. Those two are now competing for the same effort, and I don't think
both should be funded. My read: the iBackpack *hardware* thesis (minimum viable
wearable arms, economic value per task) stands; the iBackpack *video→servo
learning pipeline* is the part MolmoAct2 makes redundant.

---

## 5. Recommendation — cheapest honest test first

1. **Buy and mount two USB webcams** — one scene view, one on the wrist — and
   wire them into `teleop.sh` / `record_actions.sh` so every demo from here on
   carries RGB alongside the joint data. Cheapest step, unblocks everything, and
   pays off even if MolmoAct2 disappoints: the ACT and diffusion policies in
   `training_pipeline.md` are all better with vision too.
2. **Rent a Linux + NVIDIA box** (not an A100/H100 for the sim work per
   `lehome_pillowcase.md`, though for MolmoAct2 inference alone any modern
   NVIDIA card with enough VRAM is fine). Rent before buying.
3. **Run exactly one command** and find out:
   ```bash
   lerobot-rollout \
     --policy.path=lerobot/MolmoAct2-SO100_101-LeRobot \
     --rename_map='{"observation.images.scene":"observation.images.cam0",
                    "observation.images.wrist":"observation.images.cam1"}' \
     --robot.type=so101_follower \
     --robot.port=/dev/tty.usbmodem5AA90242401 \
     --robot.id=follower_right \
     --robot.cameras='{scene:{type:opencv,index_or_path:0,width:640,height:480,fps:30},
                       wrist:{type:opencv,index_or_path:2,width:640,height:480,fps:30}}' \
     --task="pick up the sheet of paper" --duration=30
   ```
   That is the whole test of the video's claim on our hardware.
4. **Score it honestly on our own task** — pick-and-place first, the "hello
   world" from `training_pipeline.md`; then paper, per
   `plans/paper_manipulator.md`. Write the success rate down. If it lands near
   the paper's 56.7%, the answer is "fine-tune, don't deploy."
5. **Then decide what happens to `record_actions.sh`.** The likely outcome is it
   doesn't die — it becomes the *fine-tuning* data collector. LeRobot's own
   guidance is that under 200 real demos with `train_mode_vlm=lora` at batch
   16–32 is the recommended recipe, and that is exactly our scale. Fifty demos
   to fine-tune a VLA is a much better deal than fifty demos to train an ACT
   policy from scratch.
6. **Don't rewrite the app yet.** Nothing about `ContentView.swift` should
   change before step 4 produces a number. The one exception worth doing early
   is the stop button, because that's a safety item, not a bet.

## Reference links

- Paper: https://arxiv.org/abs/2605.02881
- Blog: https://allenai.org/blog/molmoact2
- Upstream: https://github.com/allenai/molmoact2 (Apache-2.0)
- **LeRobot policy docs (the practical one):**
  https://huggingface.co/docs/lerobot/main/en/molmoact2
- Deployable checkpoint: `lerobot/MolmoAct2-SO100_101-LeRobot`

Nothing is vendored here — no weights, no datasets, no upstream code copy.
