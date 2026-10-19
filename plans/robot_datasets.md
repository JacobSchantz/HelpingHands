# Open robot datasets: what exists, and what helps our model

Status: RESEARCH (2026-10-19, voice-c7c6c5dc). Nothing downloaded, nothing trained.

Companion to `egocentric_datasets.md` (human video). This one covers **robot**
data: teleoperated arms, and handheld grippers that record robot-format
actions. For each dataset: size, license, embodiment, modalities, and how well
it fits the world action model (`world_action_model.md`) that drives our
SO-101 + Hand 1.0 gripper.

Source quality: licenses come from the Hugging Face dataset card metadata
(`cardData.license`, read through the HF API today) unless a row says
otherwise. Where the card and the publisher disagree, or the primary source
says nothing, the cell says so. A license tag on a HF card is what the uploader
typed. Check it again before training a model you plan to ship.

---

## 0. Answer in one paragraph

The only robot data that shares our **joint space** is SO-100/SO-101 data from
the LeRobot community. That makes it the one external robot source we can
train on without retargeting. There are about 250 h of it in curated form
(`lerobot/community_dataset_v3`), plus a larger raw pool that Ai2 listed and
re-captioned for MolmoAct2 (1,220 repos). Everything else is a different arm.
It can teach the *video* half of the world action model and general
manipulation priors, but its actions don't map onto ours. The short list:

1. **LeRobot community SO-100/101 data.** Same arm, LeRobot format, 30 fps,
   tagged Apache-2.0. It is messy: every contributor calibrated differently,
   camera placement varies, and most datasets are under 20 episodes. Filter it
   hard and use it as a mid-training stage before our own demos.
2. **DROID.** The best "eye-height third-person *stereo*" robot video that
   exists: two exterior ZED 2 stereo cameras, 76k trajectories, language for
   95% of successes, and a permissive license. It's a Franka, so we'd use it
   for video/world-model pretraining and evaluation, not for actions.
3. **ABC-130K.** The largest permissive teleop set (≈3,590 h, Apache-2.0,
   gated). It's a bimanual 6-DoF YAM with parallel jaws: the closest
   large-scale embodiment to ours, but still a different arm.

**GenRobot 10Kh-RealOmin** deserves a separate look. It is >13,000 h claimed
(≈1,600 h described in detail) from a **handheld gripper** with gripper width,
end-effector pose and *tactile* arrays. That's the closest public analogue to
our handheld-demo plan (`handheld_gripper.md`). Its CC BY-SA 4.0 license
allows commercial use, but the share-alike term needs a legal read (§3).

**Open X-Embodiment** is the famous one, but for us it adds the least. Every
base model we'd start from (FLUX 3 Action, π0.5, MolmoAct2, SmolVLA's
ancestors) was already pretrained on it, and its licenses are per-subset.

---

## 1. What "fits our gripper" means

Our setup (`hand_1_0.md`, `robot_model_scouting.md`): one **SO-101** arm,
5 joints + gripper = **6 action channels**, Hand 1.0 rides on the gripper
joint. Vision is **two stereo cameras at eye/head height, no wrist camera**.
The model takes a short instruction and outputs joint action chunks, recorded
as LeRobot v3 at 30 Hz. So a dataset scores higher when it has:

| Criterion | Why it matters for us |
|---|---|
| **Same embodiment (SO-100/101)** | Actions transfer as-is. Anything else needs retargeting or is video-only. |
| **6-DoF-ish single arm + parallel gripper** | Closest action structure if we ever retarget from end-effector poses (Franka, WidowX, YAM, UMI-style grippers). |
| **Third-person cameras, stereo if possible** | Our model has no wrist view. Wrist-camera-dominant data teaches the wrong viewpoint. |
| **Language per episode** | Our layer-1 contract is `act("<instruction>")`. |
| **LeRobot format** | Loads straight into `lerobot-train` with no converter. |
| **Commercial-OK license** | Same rule as `egocentric_datasets.md` §3: NC data is for experiments and evals only. |

---

## 2. The datasets

### 2a. Same arm: LeRobot SO-100 / SO-101 community data

| Dataset | Size | License | Cameras / modalities | Fit for us |
|---|---|---|---|---|
| **`lerobot/community_dataset_v3`** (HF, 2026) | 791 datasets, 50,622 episodes, 26 M frames, **251.5 h**, 235 contributors, 46 robot types. ~73% of datasets are SO-100/101 (so100 248, so101_follower 124, so100_follower 121, so101 82) | Apache-2.0 (card) | Contributor-chosen cameras, joint state + action, a task string per dataset | **Highest for actions.** It's the curated superset of v1 (128 sets, 46.9 h) and v2 (340 sets, 46.6 h), the data SmolVLA was pretrained on. |
| **`allenai/MolmoAct2-SO100_101-Dataset`** (Ai2, 2026) | Manifest of **1,220 SO-100/101 repos from 377 users**, with Ai2's per-episode language re-annotation | Manifest + annotations Apache-2.0. Each source repo keeps its own license | Whatever each source repo has. My sample is below | **High.** It's the data behind MolmoAct2's published SO-101 zero-shot number, and the re-written instructions fix the community's worst flaw (task strings like "test"). |
| `lerobot/svla_so101_pickplace`, `svla_so100_*` | ~50 episodes each | Apache-2.0 | 2 cams | Eval sets. They are useful as a sanity check for our own pick-and-place score. |

**What the community data actually looks like.** I sampled 150 of the 1,220
MolmoAct2 repos at random (seed 0) and read each one's `meta/info.json`
(97 were readable; the rest are deleted or gated):

- License tag: 109 Apache-2.0, **41 none**. LeRobot's upload template fills in
  Apache-2.0 by default, so the tag means "didn't change the default" more often
  than "chose a license". A repo with no tag has no license grant at all.
- Robot type: so100 69, so101 18, so100 variants 9, other 1.
- 30 fps in 91 of 97 repos; 20 fps in 6.
- Cameras: 70 have two, 17 have one, 10 have three or four. The names are
  mostly LeRobot's defaults (`laptop` 45, `phone` 40), which say nothing about
  placement. Only 19 of 97 *name* a wrist/gripper camera, but some `phone`
  cameras are wrist-mounted, so the true wrist share is higher.
- Median **10 episodes per repo**; the 97 together come to ~2,800 episodes and
  ~15 h. Extrapolating, the full 1,220-repo pool is in the low hundreds of hours.
- All 97 are LeRobot **v2.1**. SO-100/101 joint units changed between v2.1
  (degrees) and v3 (calibrated ±100 range), and every contributor's
  calibration is their own. Joint values from two repos are not directly
  comparable without per-repo normalisation. This is the same problem as the
  checkpoint calibration in `world_action_model.md` §3 step 5.

### 2b. Large single-arm, other embodiments

| Dataset | Size | License | Embodiment | Cameras / modalities | Fit for us |
|---|---|---|---|---|---|
| **DROID** (2024, updates to Apr 2025) | 76k trajectories, ~350 h, 564 scenes, 86 tasks, 13 institutions | **Inconsistent.** The project page names none; the LeRobot ports (`lerobot/droid_1.0.1`, `cadene/droid_1.0.1`) say Apache-2.0; secondary sources say CC BY 4.0. Both are commercial-OK, but confirm with the authors before relying on it. NVIDIA's `Cosmos3-DROID` re-release is OpenMDW-1.1 | Franka Panda 7-DoF + Robotiq 2F-85 | **2 exterior ZED 2 stereo** + 1 wrist ZED Mini, 1280×720; camera extrinsics (improved for 36k episodes in Apr 2025); depth; 3 language annotations for 75k episodes | **High for the video half.** It's the only big robot set with a stereo third-person pair like ours. Drop the wrist stream. FLUX 3 Action and Cosmos 3 already have DROID checkpoints, so it's also the reference for comparing to them. |
| **Open X-Embodiment** (2023) | >1 M episodes, 22 embodiments, ~60 datasets from 34 labs, RLDS | Code Apache-2.0; "other materials" CC BY 4.0 per the repo; **each sub-dataset keeps its own terms**, some NC | Mostly Franka, WidowX, Google robot, xArm, UR5 | Mixed: 1–4 cameras, many with wrist cams; language on most | **Low marginal value.** Every base model we'd fine-tune has already seen it. Useful only as a source of specific sub-datasets (e.g. BridgeData V2). |
| **BridgeData V2** (in OXE) | ~60k trajectories, 24 environments, 13 skills | CC BY 4.0 per HF derivatives; upstream page not re-checked | WidowX 250 (6-DoF, a hobby-class arm like ours) | Over-the-shoulder + wrist + random cams, language | Low–medium. It's a similar class of arm in toy-kitchen scenes, but it's old and already in OXE. |
| **RoboMIND** (RSS 2025; V2.0 on ModelScope) | 107k trajectories, 479 tasks, 96 object classes, 12.3 TB | Apache-2.0 (gated: share contact) | Franka 53k, UR5e 25k, Tien Kung humanoid 19k, AgileX dual-arm 11k | 1 or 3 RGB + depth, joints, language (frame-level in v1.2) | Medium. It's a big, permissive set of single-arm Franka/UR5e episodes; video pretraining and eval. V2.0's size and license are unverified. |

### 2c. Large bimanual / mobile (biggest hours, furthest embodiment)

| Dataset | Size | License | Embodiment | Cameras / modalities | Fit for us |
|---|---|---|---|---|---|
| **ABC-130K** (`XDOF/ABC-130k`; LeRobot port `lerobot/abc_130k_v3_train`) | 130,703 episodes, **≈3,590 h** (the LeRobot port: 129,225 eps, 3,541 h at 30 fps). About 43k episodes have subtask labels | **Apache-2.0** (gated) | 2 × 6-DoF YAM, parallel jaws | Top + 2 wrist cams, 14-D joint state/action | **Medium–high.** It's the largest permissive teleop set, and a YAM single arm is structurally close to an SO-101 with a gripper. Use one arm's stream for embodiment-adjacent pretraining. The top camera is the only one usable for us. |
| **MolmoAct2-BimanualYAM** (Ai2) | 32,246 eps, **704 h** | Apache-2.0 | Bimanual YAM | top + left + right | Medium. Same as ABC, smaller, with Ai2's language annotations. |
| **AgiBot World Beta** | >1 M trajectories, ~2,976 h, 48.1 TB, 100 robots | **CC BY-NC-SA 4.0** + community license | AgiBot G1 mobile dual-arm, grippers or dexterous hands | Multi-view + depth, tactile on some, language + skill segments | **Research only (NC).** |
| **Galaxea Open-World** | ~500 h, ~9.8k tasks, 11 domains | **CC BY-NC-SA 4.0** | Galaxea R1 Lite mobile dual-arm | Head + wrist cams, language | Research only (NC). |
| **PrimeBot household challenge** (`challenge-2026/challenge_data`, Aug–Sep 2026) | 500+ h teleop + ~205 h UMI so far | **CC BY-SA 4.0** | Bimanual robot (89-D state); plus a bimanual UMI handheld gripper | Head RealSense + 2 wrist ZEDs, 1280×720 @ 30; UMI part: 2 wrist fisheye 960², EE pose + gripper angle, IMU | Low–medium. It's household laundry, frame-level language, LeRobot format. Its UMI half is relevant to handheld demos. |
| **RoboCOIN** (2025–26) | Many per-task repos (AgileX, AgiBot, Alphabot…) | Apache-2.0 per repo | Mostly bimanual | Varies | Low. Bimanual and scattered across many repos. |
| **Unitree G1 / UnifoLM-WBT** | Dozens of per-task repos | Apache-2.0 | G1 humanoid, Dex1/Dex3/Inspire hands | Head + wrist | Low. Humanoid with dexterous hands, not our arm. |

### 2d. Handheld-gripper data (the "demo instrument = robot gripper" family)

These are the closest public match to Hand 1.0's handheld mode
(`handheld_gripper.md`). The demonstrator holds a gripper, and the recording is
end-effector pose + gripper width, not joint angles.

| Dataset | Size | License | Cameras / modalities | Fit for us |
|---|---|---|---|---|
| **GenRobot 10Kh-RealOmin** | >13,000 h / 5 M clips claimed; Stage 1 + 2 described as 950 h + 653 h; 36.9–95 TB (the card gives both) | **CC BY-SA 4.0** (gated) | Gen DAS handheld bimanual gripper. One **fisheye per gripper** (1600×1296, 30 fps), IMU, **gripper width** (0–103 mm encoder), EE pose + velocities, **1 mm tactile array**. MCAP + protobuf, URDF provided | **High as a method reference, medium as data.** It's the only big public set with fingertip tactile, which matches the "four touch sensors" idea in `hand_1_0.md`. But the cameras are gripper-mounted, and our principle forbids that. Its EE trajectories retarget to SO-101 IK (the same path as `handheld_gripper.md`). |
| **FastUMI / FastUMI-100K** | 10–15k demos (FastUMI); >100k trajectories, 54 tasks (100K) | **Not found** in what I read | UMI-style handheld, fisheye, text annotations | Unknown license, so unusable until checked. |
| PrimeBot UMI subset | ~205 h | CC BY-SA 4.0 | See 2c | Small, but in LeRobot v3 with EE pose + gripper angle: the easiest UMI data to load. |

### 2e. Simulation and world-model data

| Dataset | License | What it is | Fit for us |
|---|---|---|---|
| `nvidia/PhysicalAI-Robotics-GR00T-X-Embodiment-Sim` | CC BY 4.0 | Sim demos across embodiments (GR00T training) | Low. No SO-101; sim gap. |
| `nvidia/PhysicalAI-Robotics-Manipulation-Kitchen-Demos` | CC BY 4.0 | Sim kitchen manipulation | Low. |
| `1x-technologies/world_model_*` | Tokenized: Apache-2.0; **raw: CC BY-NC-SA** | Humanoid ego video for world-model challenges | Low. A world-model benchmark, not our robot. |
| `nvidia/PhysicalAI-Robotics-Open-H-Embodiment` | CC BY 4.0 | 750 h of surgical/ultrasound robots | Not relevant. |

---

## 3. License traps (on top of `egocentric_datasets.md` §3)

- **"Apache-2.0" on community LeRobot data is mostly a default.** A
  contributor who didn't touch the template still "granted" it, and 27% of my
  sample have no tag at all. For a shipped model, train only on repos that
  carry an explicit tag, and keep the list of repo IDs + commit hashes we used.
- **Share-alike (CC BY-SA: GenRobot, PrimeBot).** Commercial use is allowed,
  but adapted *data* must be re-shared under the same license. Whether a
  trained model is an "adaptation" is unsettled. Treat as: fine for training
  experiments; get a legal read before a shipped checkpoint depends on it.
- **NC (AgiBot World, Galaxea, 1X raw).** Experiments and evals only.
- **Gated ≠ licensed.** ABC-130K, RoboMIND and GenRobot make you accept terms
  on HF before downloading. Those click-through terms can add restrictions the
  card's license tag doesn't show. Read them at download time.
- **The model license already limits us.** `robot_model_scouting.md` notes
  FLUX 3 Action forbids commercial robotics use, so a permissive dataset
  doesn't make a FLUX-based product shippable on its own.

---

## 4. Suggested next steps (not started)

1. **Build the SO-101 filter** over the MolmoAct2 manifest +
   `community_dataset_v3`: keep `so101*` (and `so100*` if joint conventions
   match after normalisation), an explicit license tag, ≥20 episodes, 30 fps,
   and at least one camera that isn't on the wrist. Keep Ai2's re-annotated
   instructions. Report the surviving hours. My guess from the sample is tens
   of hours, not hundreds.
2. **Normalise per repo** (each repo's own quantiles, the way MolmoAct2 does)
   rather than trusting raw joint values. Spot-check five repos on our arm
   with replay, at low torque, before training on any of them.
3. **Mid-train, then LoRA.** Community SO-101 subset → our ~50 head-camera
   demos → score on the same eval (`world_action_model.md` §3 step 4). Keep
   it only if it beats the demos-only baseline.
4. **DROID's two exterior stereo streams** become our offline eval for the
   video half: does the model's predicted future match the real future from a
   head-height stereo viewpoint?
5. **Pull the GenRobot Stage 1 sample** once the gated terms are read. Use it
   to test the handheld-gripper → SO-101 IK retargeter from
   `handheld_gripper.md` on someone else's data, and to see what a 1 mm
   tactile array actually records during grasps.

## Sources

- LeRobot community v3: https://huggingface.co/datasets/lerobot/community_dataset_v3 · v2: https://huggingface.co/datasets/HuggingFaceVLA/community_dataset_v2 · v1: https://huggingface.co/datasets/HuggingFaceVLA/community_dataset_v1
- MolmoAct2 SO-100/101 manifest: https://huggingface.co/datasets/allenai/MolmoAct2-SO100_101-Dataset · BimanualYAM: https://huggingface.co/datasets/allenai/MolmoAct2-BimanualYAM-Dataset
- SmolVLA paper (481 community datasets): https://arxiv.org/abs/2506.01844 · VLAb: https://github.com/huggingface/VLAb
- DROID: https://droid-dataset.github.io/ · https://arxiv.org/abs/2403.12945 · https://huggingface.co/datasets/lerobot/droid_1.0.1 · https://huggingface.co/datasets/nvidia/Cosmos3-DROID
- Open X-Embodiment: https://github.com/google-deepmind/open_x_embodiment · https://arxiv.org/abs/2310.08864
- BridgeData V2: https://rail-berkeley.github.io/bridgedata/
- RoboMIND: https://huggingface.co/datasets/x-humanoid-robomind/RoboMIND · https://arxiv.org/abs/2412.13877
- ABC-130K: https://huggingface.co/datasets/XDOF/ABC-130k · https://huggingface.co/datasets/lerobot/abc_130k_v3_train
- AgiBot World: https://huggingface.co/datasets/agibot-world/AgiBotWorld-Beta
- Galaxea Open-World: https://huggingface.co/datasets/OpenGalaxea/Galaxea-Open-World-Dataset
- PrimeBot challenge: https://huggingface.co/datasets/challenge-2026/challenge_data · https://arxiv.org/abs/2609.03591
- GenRobot 10Kh-RealOmin: https://huggingface.co/datasets/genrobot2025/10Kh-RealOmin-OpenData
- FastUMI: https://arxiv.org/abs/2409.19499 · FastUMI-100K: https://arxiv.org/abs/2510.08022
- RoboCOIN: https://huggingface.co/RoboCOIN · Unitree: https://huggingface.co/unitreerobotics
- NVIDIA PhysicalAI datasets: https://huggingface.co/nvidia · 1X: https://huggingface.co/1x-technologies

Nothing is vendored. No data or weights are in the repo. The community-data
sample stats (§2a) came from a throwaway script that read 150 `meta/info.json`
files over the HF API. Re-run it with a fresh random sample if they matter.
