# World action model — the new north-star model family

Status: PLAN (2026-09-30). No code yet — this is for sign-off.

**Priority update (2026-09-30):** Jake subsequently chose MolmoAct2 with minimal
hardware changes as the first working milestone. See `molmoact2.md`. This WAM
proposal is retained for a later comparison; it does not supersede that milestone.

The original proposal below would change the model choice. The
goal is unchanged: a camera plus a plain-language instruction drives the SO-101
without us recording a dataset from scratch. What changes is the family: from a
plain VLA (observation → actions) to a **world action model (WAM)** — one
network that jointly predicts future video *and* the action chunk that produces
it.

Everything in `molmoact2.md` §2 (cameras first, NVIDIA wall) and §3 (the app is
the instruction and the eyes, stop button first) still holds. This doc only
covers what's different.

---

## 1. The pick: FLUX 3 Action, SO-101 checkpoint

Released 2026-09-23 by Black Forest Labs.
Checkpoint: **`black-forest-labs/flux-3-action-so101`** (base:
`flux-3-action-base`, 7B).

Why it wins for this repo:

- **Our exact arm, in LeRobot, today.** It's a native LeRobot policy class
  (`lerobot.policies.flux3`), with an SO-101 fine-tune and an SO-101 LoRA
  recipe. Same `lerobot-train` / rollout tooling `teleop.sh` and
  `record_actions.sh` already sit on.
- **Same camera layout we already planned.** Two cameras, keys
  `observation.images.scene` and `observation.images.wrist` — the scene + wrist
  pair from `molmoact2.md` step 1, just with different key names.
- **Best open WAM right now.** First on RoboLab-120 (42.9% vs 36.8% for the
  16B Cosmos 3 Nano), 93% on a third-party 10-task Franka eval vs 66.7% for
  DreamZero and 43% for π0.5.
- **Fits a single consumer card.** BFL lists RTX 5090 as a supported inference
  target; the Qwen text encoder (~8.3 GiB) can be parked on CPU to save VRAM.
- **License works for us.** FLUX Kommunity License v1.0 allows commercial use
  for anyone under US$5M revenue. Not Apache — noted in §4.

### Rejected

| Model | Why not |
|---|---|
| **Cosmos 3 Nano Policy** (NVIDIA, 16B, OpenMDW — the cleanest license) | No SO-101 embodiment and no LeRobot integration; we'd have to train new action heads. 2× the size. Runner-up if the FLUX license ever bites. |
| **DreamZero-SO101** (Vizuara, LoRA on Wan2.1 14B, Apache-2.0) | Only "imagined rollouts" — no closed-loop result on a real arm published. 14B. Useful later as a *simulator*, not a controller. |
| GigaWorld-Policy (1B), Motus, LVP, VideoVLA | No SO-101 support; research code, not a LeRobot policy. |

---

## 2. What we lose and gain vs MolmoAct2

**Lose — be honest about this one: the zero-shot claim.** MolmoAct2-SO100_101
has a published zero-shot number on our arm (56.7%). FLUX 3 Action publishes
no SO-101 zero-shot number; its SO-101 demo was a LoRA on **~200 teleop
episodes** of related pick-and-place. So the switch moves us from "try it with
zero demos, fine-tune to close the gap" to "fine-tune is the expected path."
(The SO-101 checkpoint itself may generalise to our first task — that's the
first thing we test, §3 step 3 — but nobody has claimed it.)

Also lost: Apache-2.0 (now a revenue-capped license), and MolmoAct2's
explicit spatial-reasoning traces.

**Gain:**

- **Better policy quality per demo.** Video pretraining is what makes WAMs beat
  VLAs on the same fine-tuning data; the benchmark gap above is that effect.
  Camera moved between training and rollout still worked; unseen containers
  worked.
- **A preview of what the robot is about to do.** The model can decode the 32
  predicted frames alongside its 32 actions. Normally you skip the decode for
  speed — but for us that's a product feature: the app can show "here's what
  I'm about to do" before the arm moves, and a human taps go or stop. That
  pairs directly with the stop button already called for in `molmoact2.md`.
- **A path to a learned simulator.** A WAM rolled out in imagination is a
  cheap way to score a policy without the arm. Relevant to the no-NVIDIA-sim
  wall in `lehome_pillowcase.md`. Later, not now.

**Unchanged:** still no force/tactile input — `gripper_bet.md` stands exactly
as `molmoact2.md` §4 says. Still NVIDIA-only; no Apple Silicon path (the Video
VAE needs a CUDA NATTEN wheel).

---

## 3. What replaces the MolmoAct2 path — steps

1. **Cameras (unchanged from before).** Scene + wrist USB webcams, recorded
   into every demo. Name them `scene` and `wrist` from the start so no
   `--rename_map` is needed.
2. **Switch recording to FLUX's data contract.** `record_actions.sh` today
   writes six joint floats at 20 Hz. FLUX needs a **LeRobot v3 dataset at
   30 Hz**: six commanded-action channels + six measured-state channels, same
   joint order, gripper last, raw values, plus a `task` string per episode.
   That means recording through `lerobot-record` with both cameras instead of
   our custom script. This is the one real code change in the repo.
3. **Rent one NVIDIA box and run the stock SO-101 checkpoint first** —
   `black-forest-labs/flux-3-action-so101`, our hello-world pick-and-place,
   ~10 attempts, write the number down. This is the cheap test of whether we
   get anything zero-shot.
4. **Record ~50 demos, LoRA, re-score.** Stock recipe:
   ```bash
   python -m lerobot.scripts.lerobot_train \
     --config_path=examples/flux3/lora.json \
     --policy.path=black-forest-labs/flux-3-action-so101 --policy.device=cuda \
     --dataset.repo_id=<us>/helpinghands_pickplace \
     --output_dir=outputs/so101_lora
   ```
   One GPU, 10k microsteps. BFL used ~200 demos; start at 50 and see where the
   curve is before recording more. Compare the raw and EMA adapters — BFL says
   EMA was mixed on SO-101.
5. **Calibration check before the arm moves under the policy.** The checkpoint's
   normalisation quantiles "assume its joint order, units and calibration" — not
   ours. MolmoAct2 had a known sign flip; FLUX doesn't document one, which
   means we find out on the arm. First rollout: low torque, hand on the stop.
6. **App: the stop button, then the preview.** Stop first (safety, unchanged).
   Then, once a policy scores, add the decoded-frames preview as the approval
   step. No other `ContentView.swift` changes until step 4 produces a number.

What goes away from `molmoact2.md`: the `joint_signs` / `joint_offsets`
correction and the `cam0`/`cam1` rename. What stays: everything else.

---

## 4. Risks I can't close from here

- **Unvalidated integration.** LeRobot's own page says this exact revision
  "still needs GPU and robot validation." Brand-new (one week old). Expect rough
  edges; pin the LeRobot commit that works.
- **VRAM for inference isn't published.** "Runs on RTX 5090" is the only
  consumer data point. Rent a 5090 or bigger for step 3, not a 4090.
- **License.** Fine while Helping Hands is under $5M revenue. If it ever
  isn't, Cosmos 3 Nano is the fallback and costs us an embodiment port.
- **No async inference.** RTC/asynchronous inference isn't supported, so the
  policy runs synchronously with the arm — the "policy on a rented box, serial
  loop on the Mac" split from `molmoact2.md` §2b needs checking for latency.

## Sources

- FLUX 3 Action in LeRobot (the practical one): https://huggingface.co/docs/lerobot/main/en/flux3
- BFL blog: https://huggingface.co/blog/black-forest-labs/flux-3-action
- Model page: https://bfl.ai/models/flux-3-action
- Code: https://github.com/black-forest-labs/flux-action
- License: https://huggingface.co/black-forest-labs/flux-3-action-droid/blob/main/LICENSE.md
- Cosmos 3 Nano Policy: https://huggingface.co/nvidia/Cosmos3-Nano-Policy-DROID
- DreamZero-SO101: https://vizuara-ai-lab.github.io/dreamzero-so101/
- WAM survey list: https://github.com/OpenMOSS/Awesome-WAM

Nothing is vendored — no weights, datasets, or upstream code.
