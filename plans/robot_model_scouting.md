# Robot model scouting + our own mini-leaderboard

Living doc (pebble voice-b797bcf2, first written 2026-10-16). Update the table
when a model ships or we score one; every number links its source. "?" means
not published / not found — do not fill a "?" from memory.

## Is there an "Artificial Analysis for robot models"?

Not really. What exists, closest first:

| Board | What it measures | Useful to us? |
|---|---|---|
| [vla-evaluation-harness leaderboard](https://allenai.github.io/vla-evaluation-harness/leaderboard/) (Ai2, monthly) | Aggregates *self-reported* results: 2,456 models × 18 sim benchmarks (LIBERO, SimplerEnv, VLABench, RoboTwin, CALVIN, RoboCasa) | Best one-stop lookup; sim + self-reported |
| [RoboLab-120](https://research.nvidia.com/labs/srl/projects/robolab/leaderboard.html) (NVIDIA) | Same 120 sim tasks, run in-house, DROID/Franka policies | Fairest apples-to-apples, but Franka not SO-101 |
| [RoboArena](https://robo-arena.github.io/) | Crowd-sourced real-world pairwise Elo on DROID setups | Real robots, but not ours; [has had benchmark-hacking issues](https://itcanthink.substack.com/p/what-do-robotics-leaderboards-tell) |
| [RoboChallenge](https://robochallenge.ai) | Real-robot Table30 suite | Real, fixed robots |
| [MolmoSpaces](https://molmospaces.allen.ai/leaderboard) | Ai2 sim | Sim |
| LIBERO / SimplerEnv / VLABench | Benchmarks, no live board. LIBERO is saturated (96–98%) | Barely separates models |

**None reports SO-101 with head-height cameras only, and nobody has
published a zero-shot SO-101 success rate for any model under that camera
layout.** That gap is why the harness below exists: the leaderboard that
matters to us is the one we score ourselves.

## Comparison (open-weight manipulation models)

Our constraints: SO-101 arm(s) + Hand 1.0 gripper, **two stereo cameras at
eye height, no wrist camera** (human-mirror principle, `hand_1_0.md`).

| Model | License | Size | Inference VRAM / GPU | Latency | SO-101 / LeRobot | Cameras it expects | Zero-shot on us? | Published results |
|---|---|---|---|---|---|---|---|---|
| **MolmoAct2** (Ai2, 2026-05) | Apache-2.0 [doc](https://huggingface.co/docs/lerobot/en/molmoact2) | 5B | <16 GB bf16; 12.1 GiB peak on H100 [doc](https://huggingface.co/docs/lerobot/en/molmoact2) | ~180 ms/call, 790 ms with depth "Think" [blog](https://allenai.org/blog/molmoact2) | ✅ `lerobot/MolmoAct2-SO100_101-LeRobot`, `policy.type=molmoact2`; joint-sign/offset fix built in | **2 third-person views (top+side), order irrelevant** — closest to ours | Plausible for simple in-distribution tasks (docs: "only empirically verified on SO-100 and Franka") | LIBERO 97.2%; real Franka zero-shot 87.1% vs π0.5 45.2% [blog](https://allenai.org/blog/molmoact2); no SO-101 rate |
| **FLUX 3 Action** (BFL, 2026-09-23) | FLUX Kommunity v1.0, gated; **robotics use non-commercial** [license](https://huggingface.co/black-forest-labs/flux-3-action-base/blob/main/LICENSE.md) | 7B + Qwen3-VL-4B encoder | ? (encoder on CPU saves ~8.3 GiB) [doc](https://huggingface.co/docs/lerobot/main/en/flux3) | 41 ms (1 step) – 246 ms on B200 [BFL](https://bfl.ai/models/flux-3-action) | ✅ `black-forest-labs/flux-3-action-so101`, `flux3`, LeRobot from source | scene + **wrist** | Unlikely: no zero-shot claim, camera mismatch; LoRA recipe | RoboLab-120 42.9% (#2) [board](https://research.nvidia.com/labs/srl/projects/robolab/leaderboard.html); real Franka 28/30 vs π0.5 13/30 (BFL's own figures inconsistent) |
| **π0.5** (Physical Intelligence) | Apache-2.0; PaliGemma tokenizer gated | ~3.3B (unverified) | >8 GB (RTX 4090) [openpi](https://github.com/Physical-Intelligence/openpi) | 32 ms on B200 [BFL](https://bfl.ai/models/flux-3-action) | Base only: `lerobot/pi05_base`, `pi05` | base + wrists; `empty_cameras` pads | No — fine-tune | LIBERO 96.9%; RoboLab 28.0% |
| **π0 / π0-FAST** | Apache-2.0 | 3.3B / ? | >8 GB | π0 73 ms on 4090, 3 cams [paper](https://arxiv.org/html/2410.24164) | Base: `lerobot/pi0_base`, `lerobot/pi0fast-base` | 2–3 incl. wrist | No | LIBERO 86.0% / 82.5% (n=1, noisy); RoboLab 5.0% / 15.5% |
| **GR00T N1.7** (NVIDIA) | NVIDIA Open Model License, commercial OK [HF](https://huggingface.co/nvidia/GR00T-N1.7-3B) (N1.5/N1.6 non-commercial) | 3B | ≥16 GB; fine-tune ≥40 GB [repo](https://github.com/NVIDIA/Isaac-GR00T) | 28 ms H100 / 38 ms L40 TensorRT; 86 ms eager | Base only, `groot` (N1.7 only in current LeRobot) | any number of views | No — `new_embodiment`, fine-tune | LIBERO 96.5%; N1.6 RoboLab 7.2% |
| **SmolVLA** (HF, 2025-06) | Apache-2.0 | 450M | small; runs on CPU / Mac | ? (async ≈30% faster tasks) | Base: `lerobot/smolvla_base`, `smolvla` | top / wrist / side | No — ~50 episodes recommended [doc](https://huggingface.co/docs/lerobot/en/smolvla) | SO-100 real 78.3%; SO-101 Lego 90% ID / 50% OOD [paper](https://arxiv.org/html/2506.01844) |
| **X-VLA-0.9B** (Tsinghua AIR, 2025-10) | ? | 0.9B | ? | ? | `xvla`; no single-arm SO-101 ckpt | main + wrist, padding allowed | No | LIBERO 98.1%; Simpler WidowX 95.8 [paper](https://arxiv.org/html/2510.10274) |
| **OpenVLA-OFT** (Stanford) | code MIT; weights Llama-2 terms (unverified) | 7B | 15.9–18 GB | 112 ms A100 [paper](https://arxiv.org/html/2502.19645) | ❌ no SO-101, no LeRobot | third-person-only config exists | No | LIBERO 97.1% |
| **LingBot-VLA v2** (Ant Group, 2026-07) | Apache-2.0 | 6B (v1 4B) | ? | <130 ms on 4090 (press) | ❌ LeRobot dataset format, not a policy type | ? | No | v1 GM-100 17.3% vs π0.5 13.0% [repo](https://github.com/robbyant/lingbot-vla) |
| **RDT2** (Tsinghua) | Apache-2.0 | ~7B base | ~16 GB (4090) [repo](https://github.com/thu-ml/RDT2) | ? | ❌ | UMI **wrist** views, bimanual EE | No — poor fit | none published |
| **Cosmos3-Nano-Policy** (NVIDIA, 2026-05) | OpenMDW-1.1, commercial OK | 16B (Edge: 4B) | RTX PRO 6000 class | Edge 15 Hz on Thor | ❌ DROID only | DROID views | No | RoboLab 36.8%; RoboArena #2 (June) |
| **DreamZero** (NVIDIA GEAR) | **CC-BY-NC-4.0** | 14B | ? | ~7 Hz | ❌ DROID only | DROID | No | RoboLab 25.7% |

Also seen, low priority: WALL-OSS (`wall_x`, Apache-2.0, GM-100 4.05%),
Cosmos Policy 2B (sim checkpoints only), GigaBrain-0.7 (no LeRobot).

**Reading it:** MolmoAct2 is the only model with an SO-101 checkpoint, a
permissive license *and* a two-third-person-camera layout, so it stays the
first zero-shot trial (matches `molmoact2_deployment.md`). Everything else is
"fine-tune on our own demos first"; the cheapest to fine-tune and iterate on
is SmolVLA (450M). FLUX 3 Action is strong but its license forbids commercial
robotics use and it expects a wrist camera we will not have.

## The harness: `robot_eval/`

One contract, any model, one command. Nothing in it is model-specific except
a row in `robot_eval/models.json`.

```
Mac (lerobot env)                               rented GPU (RunPod)
stereo head cams (left, right) ─┐               robot_eval/server.py --model X
SO-101 joint state ─────────────┼─ POST /act ─▶ adapter (LeRobot policy) ─┐
instruction (tasks.json) ───────┘   bearer token                         │
        arm ◀─ rate-limited, validated ◀─ action chunk ◀─────────────────┘
        scores.csv ◀─ operator scores the trial against the rubric
```

- **Interface** (`protocol.py`): request = instruction + SO-101 joint state +
  exactly two JPEGs, `left` and `right`. A wrist camera is rejected by design.
  Response = an action chunk, same width as the state (6 per arm). The client
  refuses late / out-of-order / stale / non-finite / wrong-width replies, and
  a chunk whose first row is far from the current pose (catches unit or joint
  sign mismatches before they hit the motors).
- **Adapters** (`adapters.py`): `lerobot` loads any LeRobot policy type from a
  Hub repo; `camera_map` says which of our eyes feeds which of the model's
  view slots (`blank` for a slot we do not have). `mock` holds pose, for
  testing cameras, transport and scoring with no GPU. Hand 1.0 rides on the
  gripper joint, so the same six channels cover it.
- **Rental** (`rent.py`): RunPod Community, direct TCP port (not the HTTP
  proxy), GPU picked from `min_vram_gb`: RTX 4090 24 GB at $0.34/h for ≤24 GB,
  RTX A6000 48 GB at $0.33/h for ≤48 GB (prices seen 2026-10-16;
  [RunPod pricing](https://www.runpod.io/pricing)). `up`, `status`, `down`.
  Vast.ai is a few cents cheaper but volatile; HF Jobs now exposes ports
  (`--expose-public`) at $0.80/h for an L4. `down` deletes the pod: a stopped
  RunPod pod still bills storage.
- **One command**: `bash robot_eval/try.sh molmoact2_so101 pick_block 1 --stereo-device 0`
  rents (if needed), runs a dry-run trial, asks for the score, then asks
  whether to keep the GPU (default: delete). Add `--execute` to move the arm.
- **Task suite** (`tasks.json`): six fixed tasks on a marked mat (touch, pick,
  block-in-bowl, colour choice, slide paper, pick paper), five trials each on
  spots A–E, three-point rubric each. Frozen once scored: new wording = new id.
- **Leaderboard** (`leaderboard.py`): `scores.csv` → markdown ranking of
  executed trials only (points %, successes, median round trip), split by
  end effector so the stock jaw and Hand 1.0 are never mixed.
- **Tests**: `python3 -m unittest robot_eval/test_robot_eval.py` (stdlib; real
  HTTP round trip with the mock, auth, all rejection paths, rate limiting,
  camera loss, GPU pick, leaderboard maths).

## What is verified and what is not

- Verified locally: everything in the test file, and `client.py --help` in the
  `lerobot` conda env.
- **Not yet run**: a real pod, real model loading, real cameras, the arm.
  Unverified until first launch: the RunPod REST field names
  `dockerEntrypoint`/`dockerStartCmd`, the `pip` extras in `models.json`, and
  the image feature keys for smolvla/pi05 (the server refuses to start if a
  key has no camera, so a wrong guess fails loudly, not silently).
- Units: MolmoAct2 is marked `degrees` (its sample state is in degrees);
  others assume LeRobot's −100..100 range. The first-action guard is the
  backstop; always dry-run a model before `--execute`.

## Next steps

1. Jake: create a RunPod API key (export `RUNPOD_API_KEY`, never commit), add
   ~$10 credit; export `HF_TOKEN` with FLUX 3 / PaliGemma access accepted.
2. Agent: first launch with `mock`, then `molmoact2_so101` dry-run; fix
   whatever the first real pod reveals.
3. Mount the stereo head pair, mark the mat, run MolmoAct2 on all six tasks.
4. Record ~50 head-camera demos and fine-tune SmolVLA as the second entry.
