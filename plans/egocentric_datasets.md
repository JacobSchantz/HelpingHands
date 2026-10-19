# Open egocentric manipulation datasets: what exists, and what helps our model

Status: RESEARCH (2026-10-19, voice-50a87f8c). Nothing downloaded, nothing trained.

Question: which open first-person datasets of people manipulating things are
worth using to train the world action model (`world_action_model.md`) that
drives our gripper? For each one: size, license, modalities, and how useful it
is to us.

Source quality: every row links a paper, dataset card or project page. Numbers
come from those pages as of today. Where a primary source didn't state
something (most often the license), the cell says **unstated**. Don't treat a
blank as permission. Check the license again before downloading anything big.

---

## 0. Answer in one paragraph

No public dataset is the robot's own data, so none of them replaces our
gripper demos. They are useful in two ways. **(a) Video pretraining** for the
"predict the future frames" half of the world action model: any large
egocentric video corpus with a usable license helps here. **(b) Action
pretraining**: the dataset needs per-frame camera pose, 3D wrist pose and
finger pose, so a hand trajectory can be retargeted to the gripper (thumb–index
gap becomes gripper opening, wrist pose becomes an end-effector target and goes
through IK to SO-101 joints). Under those two uses and a commercial-use license,
the short list is:

1. **EgoLive**: the closest match to our rig (head-mounted *stereo* RGB, depth,
   MANO hands, sub-task captions, 1,680 h). The license is unstated, so we must
   get it from the publisher (JD Cloud) before relying on it.
2. **Open-AoE**: 2,000 h, smartphone-captured, MANO hands + camera trajectory
   + atomic actions, and the dataset license allows commercial use with
   attribution. Caveat: the hand files are MANO-derived, so the
   **MANO license** also applies (see §3).
3. **Build AI Egocentric-100K**: 100k h, Apache-2.0, but video only (mono
   fisheye, 456×256, factories). It suits video/world-model pretraining and
   nothing else.

**EgoDex** has the best hand-pose quality per hour (Vision Pro native
tracking), but its CC BY-NC-ND license makes it research and evaluation only.
Ego4D and EPIC-KITCHENS are the famous ones, but for us they are the least
useful. They have no 3D hand pose or camera trajectory, and their licenses are
restrictive.

---

## 1. What "useful to us" means

From the README and `hand_1_0.md`, our model sees **two eye-height stereo
cameras** plus robot state and a short instruction, and outputs SO-101 joint
action chunks. Demos come from the same gripper carried in a hand, with the
demonstrator wearing the same stereo pair. So a dataset scores higher when it:

| Criterion | Why it matters for us |
|---|---|
| **Head-mounted, eye height** | Same viewpoint as our demonstrator glasses and the robot's head cameras. All datasets below meet this. |
| **Stereo or depth** | Our model is stereo-in. Mono data can still pretrain video features, but it can't teach the stereo geometry. |
| **3D wrist + finger pose + camera pose** | Needed to turn a human clip into a gripper action trajectory. Without it, the data can only pretrain video. |
| **Language / step labels** | Our layer-1 contract is `act("<instruction>")`. Short-horizon captions map directly onto it. |
| **Tabletop / household tasks** | Matches the skills layer 1 owns (grasp, place, open, pour, wipe). |
| **Commercial-OK license** | Helping Hands is meant to become a product (`rental_operations.md`). NC data is fine for experiments, but a shipped model shouldn't depend on it. |

The **embodiment gap** applies to every row below. These are bare human hands,
and our demos are a gripper held in a hand. Known bridges are retargeting
(above), and masking or inpainting the arm and rendering a virtual parallel-jaw
gripper into the frame (HumanEgo, Ego2Robot, H2R; §4).

---

## 2. The datasets

### 2a. Large, manipulation-focused, with 3D hand pose (the action-pretraining candidates)

| Dataset | Size | License (dataset) | Capture / modalities | Useful to us? |
|---|---|---|---|---|
| **EgoLive** (Apr 2026) | ~1,680 h, 65,866 episodes, 346 real-world tasks (homes, retail, work) | **Unstated** in the paper (the paper itself is CC BY 4.0). Distributed via JD Cloud's robot-data market | Custom head-mounted **stereo RGB** (2 × 2160², 60 fps, 130° FOV), 200 Hz IMU, **depth** from FoundationStereo (≈3 mm error at 0.5 m), 6-DoF wrist + hand joints, MANO, 2D/3D keypoints, hand/object masks, sub-task segments with VLM-written captions | **Highest.** It is the only big dataset whose sensor rig resembles ours. If the license works, it's the first one to try retargeting on. |
| **Open-AoE** (Jul 2026, Ant/inclusionAI) | ~2,000 h, 8,000+ tasks, 500+ contributors, 23 TB | **Open-AoE dataset license:** research **and commercial** use with attribution. The MANO license also applies to `hands.npz` / `camera_traj.npz`. Code is Apache-2.0 | Smartphone video (400+ phone models, not head-worn glasses), MANO hand poses, camera trajectory, temporally localised atomic actions, EN/ZH text. Ships a retargeting + training toolchain | **High.** It has the clearest commercial terms of any dataset with hand pose. It is mono and phone-held, so the viewpoint matches ours less well than EgoLive's. |
| **EgoDex** (Apple, ICLR 2026) | 829 h, 338k demos, 194 tabletop tasks, 90M frames, ~1.7 TB | **CC BY-NC-ND 4.0** | Apple Vision Pro, 1080p 30 Hz mono RGB, native SE(3) for head, upper body and 25 joints per hand, per-joint confidence, intrinsics, language descriptions | **High for research, unusable for a product.** Its hand poses are the cleanest here. The ND term arguably also bars publishing a retargeted derivative. Use it to prototype the retargeting pipeline and as an eval set. |
| **EgoVerse** (RSS 2026, multi-lab) | 1,362 h, 80k episodes, 1,965 tasks, 240 scenes, 2,087 demonstrators | **Unstated** on egoverse.ai and in the abstract | Camera pose, 3D head tracking, 21-keypoint hands per hand, dense language. Transfer studies run across several robot embodiments (GT, Stanford, UCSD, ETH) | **Medium–high.** Its main contribution is the paper's finding that robot gains scale with human data only when that data is aligned with the robot task. Its tooling (EgoDB) is worth reading before we build our own. |
| **EgoScale** (NVIDIA, Feb 2026) | 20,854 h used for pretraining | **Not released as a dataset** as far as I can find (it's a training recipe over aggregated video) | Wrist motion + retargeted hand actions | **As a recipe, not data:** human pretraining → 50 h human + 4 h robot "mid-training" gave +54% on a 22-DoF hand, and it also transferred to hands with fewer DoF. This mirrors our plan. |

### 2b. Huge, video-only (world-model / video pretraining only)

| Dataset | Size | License | Modalities | Useful to us? |
|---|---|---|---|---|
| **Build AI Egocentric-100K** | 100,405 h, 2.0M clips, 10.8B frames, ~25 TB; 14,228 factory workers | **Apache-2.0** (HF gated: share contact info) | Mono head-mounted fisheye, **456×256**, 30 fps, intrinsics per worker. No hands, no labels, no audio | **Medium.** It is the biggest truly permissive egocentric corpus, but it only fits the video half of the world action model. Low resolution and factory scenes are not a home setting. |
| **Build AI Egocentric-10K** | ~10,000 h, 2,153 workers, 16.4 TB | **Apache-2.0** (gated) | Same as above | Subsumed by 100K. A blog claims an "Egocentric-1M" release (Apr 2026), but it is **not** on Build AI's HF page, so treat it as unverified. |
| **Ego4D** (Meta + consortium) | 3,670 h, 923 wearers, 7 camera types | **Ego4D License Agreement** (application required). Secondary sources disagree on how far commercial model training is allowed, and redistribution is restricted. Read the [agreement PDF](https://ego4d-data.org/pdfs/Ego4D-Licenses-Draft.pdf) before using it | Mono video, narrations, FHO benchmark annotations (2D hand/object boxes, state changes). Some subsets have audio, 3D scans, eye gaze, stereo | **Low–medium.** It's broad daily-life video, but mostly not manipulation and it has no 3D hand pose. Many existing models already pretrained on it, so it adds little on top of the FLUX 3 Action base. |
| **EPIC-KITCHENS-100** (Bristol) | 100 h, 45 kitchens, ~90k action segments | **CC BY-NC 4.0** (commercial use needs a separate Bristol license) | Head-mounted GoPro mono video, verb/noun action labels, narrations, VISOR masks | **Low.** It's kitchen-specific and NC, and it has no 3D hands. It is good for *evaluating* "does the model understand this action". |

### 2c. Small, precise, Project Aria-based (calibration, eval, retargeting ground truth)

These are hours, not thousands of hours. Their value is ground truth that is
accurate enough to check a retargeting pipeline against.

| Dataset | Size | License | Modalities | Useful to us? |
|---|---|---|---|---|
| **Ego-Exo4D** | ~1,286 h (ego + exo) *(from memory, check)* | Ego4D-style agreement | Aria (RGB + 2 mono SLAM cams + IMU + gaze), exocentric views, 3D body/hand pose, keysteps, expert commentary | Low–medium. It's skilled activities, not much tabletop manipulation. |
| **HOT3D** (Meta) | ~3.7 M images across multi-view Aria + Quest 3 sequences, 19 subjects | Mixed: sequences **CC BY-SA**, **hand annotations CC BY-NC-SA**, object models CC BY-SA + no-sale | Aria (RGB + 2 mono) and Quest 3 (2 mono 1280×1024 = a **stereo pair**), mm-accurate hand (UmeTrack / MANO) + object 6-DoF poses | **Medium for eval.** It is the best ground truth for "is our stereo hand/object tracking right", but the hand labels are NC. |
| **HD-EPIC** (Bristol, CVPR 2025) | 41 h, 9 kitchens | **Unstated** in what I found (EPIC lineage suggests NC) | Aria, digital twins of 400+ fixtures, ~59k fine-grained actions, 3D object movement | Low. It's a strong benchmark but tiny. |
| **Nymeria** (Meta) | 300 h, 264 people, 50 locations | **Conflict:** the project page says CC BY-NC 4.0, the HF card says Apache-2.0 | Aria + full-body mocap, language narrations | Low. It's whole-body motion, not manipulation. |
| **Aria Everyday Activities / Aria Digital Twin** | small | Meta non-commercial research license | Aria streams + (ADT) object/scene ground truth | Low. |

Aggregators (not new data): **OpenEgo** unifies CaptainCook4D (Apache-2.0),
HOI4D (CC BY-NC), HoloAssist (CDLA-v2), EgoDex (BY-NC-ND), HOT3D (mixed) and
HO-Cap (CC BY) into one hand format. Each source keeps its own license, so the
combination is effectively NC. Lightwheel's **EgoSuite-Open10K / Open100K** are
separate from Build AI's datasets, and some repos are gated with their own
terms. I didn't verify them.

---

## 3. License traps

- **MANO.** The MANO hand model's own license is non-commercial research.
  Commercial use needs a separate license from Meshcapade/MPI. Any dataset that
  ships MANO *parameters* (Open-AoE, EgoLive, HOT3D) inherits that question
  even when the video license is permissive. Open-AoE says so explicitly. One
  workaround is to retarget from 3D keypoints, not MANO parameters, and never
  load the MANO model. This needs a legal read, not just an engineering one.
- **NC and models.** It is unsettled whether a model trained on CC BY-NC data
  is itself encumbered. Keep the line simple: NC data is for experiments and
  evals, and a shipped checkpoint gets trained only on commercial-OK data.
- **FLUX 3 Action** is already under the FLUX Kommunity License (under US$5M
  revenue, `world_action_model.md` §4). Data licenses stack on top of that.

---

## 4. How the transfer has been done (2026 papers worth copying)

- **EgoScale** (NVIDIA): large human-video pretraining with wrist + retargeted
  hand actions, then a small aligned human + robot mid-training. This is the
  same shape as "human data → our gripper data → LoRA" in our plan.
- **EgoVerse**: gains scale with human data only when it's aligned with the
  robot objective. So filter for our task family (tabletop, single-arm,
  grasp-and-place), don't just pour everything in.
- **HumanEgo** (arXiv 2605.24934): Aria video, arm removed with SAM2 + LaMa
  inpainting, and a virtual parallel-jaw gripper rendered from thumb–index
  keypoints. A secondary write-up reports ~75% success from ~15 min of human
  data. Its limits are a quasi-static scene and a ~1 cm precision plateau.
- **Ego2Robot** (arXiv 2608.02580), **H2R** (arXiv 2505.11920): turn ego video
  into robot-looking training data for VLA pretraining. Both are parallel-jaw
  only, which suits our two-finger gripper.

Our edge here is that our demonstrations already put a *real* gripper in the
human hand, in front of the same stereo cameras. Public bare-hand data
needs the rendering trick, and ours doesn't.

---

## 5. Suggested next steps (not started)

1. **Get EgoLive's license** from the JD Cloud market page. If it's
   commercial-OK, it becomes the primary external dataset.
2. **Download EgoDex's 16 GB test split** and build the retargeter on it
   (hand keypoints → gripper aperture + wrist pose → SO-101 IK). It's research
   use and the cheapest clean hand data available. Score the retargeter on how
   often the IK target is reachable for the SO-101 workspace.
3. **Re-run the retargeter on an Open-AoE slice** (commercial-OK path), using
   keypoints rather than MANO parameters.
4. Only after our own gripper data gives a baseline LoRA score
   (`world_action_model.md` §3 step 4), **try a human-data mid-training stage**
   and compare with the same eval. If it doesn't beat the baseline, we stop
   spending time on external data.
5. Egocentric-100K is a later option, and only if we ever train the video half
   ourselves rather than starting from the FLUX base.

## Sources

- EgoLive: https://arxiv.org/abs/2604.23570 · data: https://robotdata-market.jdcloud.com/console/market
- Open-AoE: https://arxiv.org/abs/2607.14183 · https://huggingface.co/datasets/inclusionAI/OpenAoE-2000h · https://github.com/ant-research/Open-AoE
- EgoDex: https://arxiv.org/abs/2505.11709 · https://github.com/apple/ml-egodex
- EgoVerse: https://arxiv.org/abs/2604.07607 · https://egoverse.ai/
- EgoScale: https://arxiv.org/abs/2602.16710 · https://research.nvidia.com/labs/gear/egoscale
- Build AI: https://huggingface.co/datasets/builddotai/Egocentric-100K · https://huggingface.co/datasets/builddotai/Egocentric-10K
- Ego4D: https://ego4d-data.org/ · license PDF https://ego4d-data.org/pdfs/Ego4D-Licenses-Draft.pdf
- EPIC-KITCHENS-100: https://arxiv.org/abs/2006.13256 · Bristol licensing https://express-licences.bristol.ac.uk/products/Softwareanddata/list
- HOT3D: https://arxiv.org/abs/2411.19167 · license https://projectaria.com/datasets/hot3D/license
- HD-EPIC: https://arxiv.org/abs/2502.04144
- Nymeria: https://www.projectaria.com/datasets/nymeria/ · AEA license https://www.projectaria.com/datasets/aea/license/
- OpenEgo: https://arxiv.org/abs/2509.05513
- HumanEgo: https://arxiv.org/abs/2605.24934 · Ego2Robot: https://arxiv.org/abs/2608.02580 · H2R: https://arxiv.org/abs/2505.11920

Nothing is vendored. No data or weights are in the repo.
