# Handheld gripper demos — which open system, and what we build

Status: RESEARCH + PLAN (2026-09-30, voice-b4fbc4ee). Nothing bought, nothing built.

Question: what is the best open-source handheld robot-gripper system for
collecting demonstrations that transfer to our SO-101, and do we adopt it or
adapt Hand 1.0 (`plans/hand_1_0.md`)?

**Answer in one line:** adapt Hand 1.0. We should copy UMI's *method*, not
anybody's *hardware*. No existing open design targets a 5-DOF servo arm. Hand 1.0
already has the property that matters most: the same camera and the same gripper
servo are used in both modes. The only things missing are a pose tracker in the
handheld mode and a retargeting step. Both are small.

Source quality: every claim below links to a paper, repo or company post, and
things I could not confirm from a primary source are marked *(unverified)*. The
2025–2026 items were gathered through web summaries, so re-check a link before
spending money on it.

---

## 0. The company reference, verified

"Generalist Robotics" is **Generalist AI** (generalistai.com; Pete Florence, Andy
Zeng, Andrew Barry). This settles the "Unverified" note in `gripper_bet.md`.

- **GEN-0** (Nov 2025): 270,000 h of manipulation data from "1,000s of data
  collection devices and robots", growing 10k h/week; claims a power-law scaling
  of error in data. [blog](https://generalistai.com/blog/nov-04-2025-GEN-0)
- **GEN-1** (Apr 2026): base model trained "without any robot data", using "data
  from low-cost wearable devices on humans"; >500k h; ~1 h of robot data to adapt
  to a task. [blog](https://generalistai.com/blog/gen-1)
- **GEN-1.5** (Aug 2026): one-shot prompting 59% ± 10% across 10 tasks. [blog](https://generalistai.com/blog/gen-1.5)
- **Proprietary, all of it.** No device design, dataset, weights or paper. Every
  number is self-reported on internal evals. The device is called "Data Hands" /
  "UMI-style pincers" in the press only
  ([Humanoids Daily](https://www.humanoidsdaily.com/news/generalist-ai-unveils-gen-1-the-quest-for-robot-mastery-and-intelligent-improvisation)).

What it means for the Gripper Bet: Generalist *is* crediting humans driving
wearable hardware at scale, which is Jake's claim 1. They are not crediting the
pincher as such. The disagreement in `gripper_bet.md` §4 (a two-finger ceiling vs
a hand) is still open. Others doing the same thing, all closed: Sunday Robotics
(a glove matched to the robot hand, "zero robot data",
[blog](https://www.sunday.ai/journal/no-robot-data)), Genesis AI, and Skild (UMI
data in the mix). **Xiaomi-Robotics-1** trained on 100k+ h of UMI-style handheld
data and released its weights and code, but not the data
([arXiv 2607.15330](https://arxiv.org/abs/2607.15330)).

---

## 1. Ranked shortlist of open systems

Ranked by fit for Helping Hands (openness × evidence × SO-101 fit × cost), not by
how impressive they are.

| # | System | What's actually released | Tracking | Cost | Evidence | SO-101 fit |
|---|---|---|---|---|---|---|
| 1 | **UMI** (Chi et al. 2024) — [paper](https://arxiv.org/abs/2402.10329), [code](https://github.com/real-stanford/universal_manipulation_interface) | Code MIT; Onshape CAD + BOM (**no stated hardware license**); the in-the-wild cup dataset + checkpoint | GoPro + ORB-SLAM3, offline, per-scene mapping video | ~$371/unit, 780 g | Strongest: 20/20 cups at 305 demos; 71.7% in the wild at 1,400; ~3× SpaceMouse throughput | Poor as hardware: fingers are matched to a €3.9k WSG-50; 780 g |
| 2 | **Grabette + Gripette** (Pollen / HF, Jul 2026) — [blog](https://huggingface.co/blog/grabette), [repo](https://github.com/pollen-robotics/grabette) | Handheld + robot gripper, exports 6-DoF pose + gripper to LeRobot; license *(unverified)* | OAK-D + RTAB-Map VIO | ~490 € handheld, ~120 € robot gripper | One task: 200 cup-grasp demos on a 7-DoF OpenArm | Medium: robot-agnostic and LeRobot-native, not tried on 5-DOF |
| 3 | **iPhone ARKit family** — Stick-v2/RUM ([paper](https://arxiv.org/pdf/2409.05865)), [AnySense](https://github.com/NYU-robot-learning/AnySense), [UMI-FT](https://github.com/real-stanford/UMI-FT), [MagiClaw](https://arxiv.org/html/2509.19169v1) | Apps + code (AnySense open source); UMI-FT claims open hardware | ARKit VIO, live, ~140 ms latency, drift ~0.02 m/s | ~$25 of parts + a phone we own | Good: RUM zero-shot deployments; UMI-on-Legs 80% with iPhone vs 85% with mocap | **Best**: tracker only needed in the hand (§2); we already ship iOS apps |
| 4 | **UMI-3D** (2026) — [paper](https://arxiv.org/abs/2604.14089), [hardware](https://github.com/Physical-Intelligence-Laboratory/UMI-3D-Hardware) | Hardware Apache-2.0, BOM, ROS Noetic drivers, policy + data repos | Livox MID-360 LiDAR-inertial, hardware-triggered sync | ~$700 | Cups 0.86 seen at 3,500 demos; door 97.5% | Poor: LiDAR mass, ROS Noetic, overkill for a tabletop |
| 5 | **HandUMI** (murobotics) — [shop](https://shop.murobotics.ai/) | Assembled kit; "open-source" software *(repo not found)* | Quest 3 / PICO headset | $749 pair | Seller claims only | SO-101 not listed |

**Rejected:**
- **FastUMI** and **LEGATO** depend on the RealSense T265, which reached end of
  life in 2022.
- **AirExo-2** is CC BY-NC-SA (no commercial use) and built 1:1 to the Flexiv
  arm.
- **DexUMI** is dexterous-hand exoskeletons. It is Hand 2.0 reading, not Hand 1.0.
- **MV-UMI** and **ActiveUMI** have a website only, no code.
- Nothing official exists for SO-101 from TheRobotStudio, HF or Seeed.

**The one on-arm precedent:**
[robotfuel/so101_retargeted_umi](https://huggingface.co/datasets/robotfuel/so101_retargeted_umi).
It is 48 GoPro handheld episodes retargeted into SO-101 *joint space*, trained
with ACT:

| Training data (ACT) | Success |
|---|---|
| 16 teleop | 2/12 (17%) |
| 16 teleop + 16 handheld | 13/20 (65%) |
| 32 teleop | 14/20 (70%) |

So a handheld demo was worth roughly 0.9 of a teleop demo. The trial counts are
tiny, and the retargeting code and CAD are unpublished. It is encouraging, not
proof.

---

## 2. Why adapt Hand 1.0 instead of adopting one of these

Three facts decide it:

1. **The robot never needs the tracker.** The robot knows its own end-effector
   pose from forward kinematics. The pose tracker only has to ride on the
   *handheld* unit. What must match across modes is the **camera** (lens, mount,
   view of the fingertips) and the **fingers**. Hand 1.0 already requires exactly
   that. The tracker can be a heavy, removable clip-on, so the SO-101 wrist never
   carries it. UMI-style designs put the GoPro on both, and 780 g is far beyond
   an SO-101 wrist.
2. **Hand 1.0's trigger servo beats UMI's gripper-width tags.** UMI reads jaw
   width from fiducial tags in the video. Hand 1.0's back-driven STS3215 trigger
   records `gripper.pos` in the follower's own units, with no vision step and no
   mapping.
3. **Our model path wants joint-space data.** `plans/world_action_model.md`
   (FLUX 3 Action) and the ACT path both consume six joint channels, the same as
   teleop. So the handheld pipeline must end in **SO-101 joint space**, as the
   robotfuel precedent did. Handheld and teleop episodes then land in one LeRobot
   dataset with one schema and can be mixed freely.

**What we take from UMI (the parts that are ablated and proven):**
- Relative end-effector action chunks.
- **Latency matching.** Tossing fell from 87.5% to 57.5% without it.
- A wide field of view on the gripper camera, with both fingertips in frame.
- **Filtering demos for the target arm's kinematics.**

**The real constraints (not solvable by picking a better kit):**
- **5 DOF.** The SO-101 has no independent yaw; the gripper always points away
  from the base. A human wrist will produce poses the arm cannot reach. Fix: IK
  that projects the requested orientation onto wrist pitch × roll (LeRobot
  already has placo IK and the SO-101 URDF). Add a **feasibility check** that
  rejects frames whose IK residual is too big
  ([FeasibleCap](https://arxiv.org/abs/2603.07580) does this *live* during
  capture, which is the better version later).
- **Backlash.** Measured STS3215 backlash is 0.6° unloaded and 1.3° loaded
  ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13087586/)). Expect several mm
  at the fingertip. Handheld demos are perfectly tracked, so the policy never
  sees that error. This is the failure the
  [Armstrong π0.5 write-up](https://armstrongrobotics.substack.com/p/fine-tuning-pi05-with-umi-the-promise)
  blames: UMI-only picks were fine, UMI-only places were poor. Keep some teleop
  in every dataset.
- **The human arm in frame.** Handheld images show a human arm; robot images
  don't. Mounting the camera low on the gripper, looking down the jaw axis (Hand
  1.0 §3), minimises this. Measure it rather than assume.
- **Wrist payload.** Budget ≤ 250 g at the wrist for gripper + camera
  *(unverified spec; the arm is marketed at ~500 g)*.

---

## 3. What the evidence does and does not say about data efficiency

**Supported:**
- **Handheld collection is faster than teleop, by roughly 3×.** UMI measured it
  against a SpaceMouse and DexUMI against teleop; FastUMI-100K claims ~5×.
  Handheld is still only 48–64% of bare-hand speed.
- **Diversity beats count, within a task.** In Lin et al., generalisation
  follows a power law in the number of environments and objects. Beyond ~50
  demos per environment–object pair, more demos barely help. Four people
  collected a new task in one afternoon and got 85–92% in unseen settings
  ([arXiv 2410.18647](https://arxiv.org/html/2410.18647)). That work used an
  8×A100 for 75 h, which is not our budget.
- **Speed vs fidelity.** GELLO-style joint teleop (our leader arm is one) is the
  fastest and most successful teleop interface: 92% vs 63% for SpaceMouse
  ([arXiv 2309.13037](https://arxiv.org/html/2309.13037)). **Our teleop
  baseline is already the strong one.** The 3× speed-up above was measured
  against a SpaceMouse, so expect less against our leader arm.

**Not supported, don't promise:**
- That handheld data needs fewer demos per unit of success than teleop. The one
  like-for-like on our arm says it's slightly *worse* per demo (0.9×). The win,
  if there is one, comes from being cheaper and faster per demo and from reaching
  places the rig can't go.
- That egocentric video beats either at our scale. Its big wins (EgoScale,
  HumanScale, PI's transfer result) need thousands of hours plus a large
  pretrained model.
- Company numbers (Generalist, Sunday, Skild, Dyna, Genesis). They come from
  internal evaluations with no published protocol, and none can be compared
  with each other.

Hypothesis this pilot tests: for a fixed hour of human time, handheld + a little
teleop beats teleop alone on our arm.

---

## 4. The pilot

### What we build: Hand 1.0 + one clip-on

| Part | Qty | Note | ~Cost |
|---|---|---|---|
| Hand 1.0 printed body, jaws, TPU pads, camera arm, handle | 2 sets | one handheld, one on the follower wrist — identical | filament |
| USB UVC camera, wide FOV (≥120°), fixed exposure | 2 | **same model on both units**; framing check per `hand_1_0.md` §3 | ~$30–60 each *(unverified)* |
| STS3215 servo for the trigger | 1 | Hand 1.0 §4 recommendation | ~$15–20 *(unverified)* |
| USB-serial bus adapter + battery pack | 1 | handheld mode | ~$20 |
| iPhone (owned) + printed rigid clip on the handheld only | 1 | ARKit pose tracker; never goes on the arm | $0 |
| ArUco board, printed, taped to the table | 1 | registers the phone's world frame to the robot base frame | ~$0 |

That is under ~$150 of new spend beyond what Hand 1.0 already needs. The iPhone
wins over a Quest controller because it has published accuracy on handheld rigs.
It wins over a Vive tracker because SteamVR on macOS is effectively gone
*(unverified)*. It wins over a GoPro + ORB-SLAM3 because the Max Lens Mod 1.0 is
discontinued and SLAM is UMI's "most fragile part".

### Capture → training pipeline

1. **Record.** The laptop records the UVC camera + trigger servo through
   `lerobot-record`, the same code path as teleop. At the same time, a small
   iPhone app (or AnySense) logs ARKit pose at 60 Hz.
2. **Sync.** At the start of each episode, the UVC camera films a millisecond
   QR code on the phone screen. This is UMI's latency-calibration trick, and
   gives one offset per episode. A jaw snap on the trigger is a second check.
3. **Register.** The first frames see the ArUco board, which fixes the
   phone-world → robot-base transform.
4. **Retarget.** Pose → SO-101 joints via LeRobot `RobotKinematics` (placo,
   `so101_new_calib.urdf`), seeded from the previous solution. The trigger
   channel passes straight through as `gripper.pos`.
5. **Write** the result as ordinary LeRobot v3 episodes: six joints, 30 Hz,
   `scene` + `wrist` images. That is FLUX's data contract
   (`world_action_model.md` step 2), and teleop and handheld share one schema.
6. **Train.** ACT on the Mac first: the robotfuel run was 50k steps at batch 8,
   MPS on the M4 *(unverified)*. FLUX LoRA on the rented NVIDIA box once that
   exists.

### Data-quality checks (automated, per episode, before training)

- Tracking: no pose jump > 2 cm between 60 Hz samples, and no ARKit
  "limited"/"not available" tracking state.
- Retarget: IK residual ≤ 1 cm and ≤ 10° on every frame. Any failure drops the
  episode. Report the kept fraction.
- Sync: offset measured, and residual jitter ≤ 1 frame (33 ms).
- Gripper: the trigger range covers the full calibrated follower range. Hand
  1.0's new jaws need recalibration first.
- Open-loop replay: replay 5 random retargeted episodes on the real arm. If the
  arm can't do its own demo blind, the policy won't either.

### Tasks

1. **Pick a small box into a bin**, on the `training_pipeline.md` hello world
   table. This is directly comparable to robotfuel.
2. **Paper, push-to-edge then pinch** (`hand_1_0.md` strategy b). This is the
   task Hand 1.0 exists for.

### The experiment (task 1 first; task 2 only if task 1 passes)

Arms of the experiment, 20 trials each:
- 30 teleop
- 15 teleop + 15 handheld
- 30 handheld
- 15 teleop + 45 handheld (*same human minutes as 30 teleop*, if throughput is 3×)

Log wall-clock collection minutes per arm.

### Success criteria before scaling collection

- ≥ 80% of handheld episodes pass QC; open-loop replay succeeds ≥ 4/5.
- Handheld throughput ≥ 2× teleop demos per hour on the same task. It is lower
  than UMI's 3× because our leader arm is a strong baseline.
- **The decisive one:** at equal human time, the handheld-heavy mix beats 30
  teleop by ≥ 10 points. If it only matches at equal *demo count*, handheld
  isn't worth the extra pipeline on this arm. Stay with the leader arm and put
  the effort into Hand 1.0 as a better wrist gripper.

If it passes, scale by diversity (more tables and objects, following Lin et al.),
not by repeats.

---

## 5. Open decisions for Jake

1. **Tracker: iPhone ARKit (recommended), Quest 3S, or ArUco-only on a fixed
   table?**
2. **Do the pilot before or after the first FLUX zero-shot run?** Recommended:
   after. If the stock SO-101 checkpoint already does pick-and-place, the pilot
   should jump straight to paper.
3. **Hand 1.0 decisions 1–4 (`hand_1_0.md`) still gate the build.** The camera
   and trigger answers assumed here match its recommendations.
