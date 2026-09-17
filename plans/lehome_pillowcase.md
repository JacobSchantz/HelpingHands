# Folding a pillowcase: reproducing the LeHome solution

Goal: get our SO-101 rig doing something visibly useful. The fastest credible
route is not building from scratch — it is reproducing Ilia Larchenko's LeHome
Challenge 2026 solution, which already folds garments bimanually on two
SO-ARM101 arms. 1st of 62 in the simulation round, 2nd in the real-world final.

Everything below was read out of the actual repository, the official challenge
repo, NVIDIA's Isaac Sim requirements, and the Hugging Face APIs on 2026-09-17.
File and line references are to `github.com/IliaLarchenko/lehome_solution`,
cloned locally at `~/lehome_solution`.

---

## The headline, before the detail

**Three things you should know before reading further.**

1. **None of this can run on a Mac.** Not the simulation, not the policy. Isaac
   Sim 5.1 has no macOS build at all, and the policy needs `jax[cuda12]` on an
   NVIDIA GPU. The repo's own `pyproject.toml` declares
   `environments = ["sys_platform == 'linux' and platform_machine == 'x86_64'"]`,
   so `uv` will not even resolve the dependency tree on Apple Silicon. This is a
   hard wall, not a difficulty.

2. **There is no pillowcase.** The challenge has exactly four garment classes —
   `top_long`, `top_short`, `pant_long`, `pant_short` (`src/lehome_solution/constants.py`),
   and the asset pack on Hugging Face contains exactly four garment directories
   to match. The garment class is baked into the policy: a `garment_type_id`
   input, per-class inference configs, and a 21-wide keypoint head sliced per
   class. A pillowcase is out of distribution for both released policies and has
   no simulation asset. That does not kill the plan, but it changes the last
   mile — see "The pillowcase problem" below.

3. **The cheapest useful next step costs about $6.** A rented RTX 4090 at the
   current going rate runs the whole simulation end to end in a few hours. That
   is the decision I need from you, and it is the only one blocking progress.

---

## 1. What the hardware actually has to be

### (a) To RUN the released policy — not train it

| | |
|---|---|
| GPU | NVIDIA, CUDA 12, **>8 GB VRAM** for inference |
| Realistic floor | **16 GB VRAM**; 24 GB comfortable |
| Example | RTX 4090 |

The >8 GB figure is openpi's own published requirements table (openpi is the
π₀.₅ codebase this is built on). Two things push the real number higher:

- `src/lehome_solution/policies/policy_config.py:47` loads the checkpoint as
  bfloat16 specifically "to save memory (12GB vs 24GB)".
- The shipped default inference config runs **3 best-of-N candidates** with
  classifier-free guidance (`DEFAULT_CONFIG` in
  `src/lehome_solution/eval/inference_optimization.py`), which multiplies the
  action-expert cost. The real-robot server path disables the unconditional CFG
  pass for ~2× speed (`cfg_disabled` in `shared/eval_wrapper.py`), so you can
  trade quality for latency, but the weights still have to fit.

The model is π₀.₅: a Gemma-2B language backbone, a SigLIP So400m/14 vision
encoder, and a 300M action expert, predicting 30 actions × 12 dimensions
(6 joints × 2 arms). The checkpoint is a **10.5 GB** download.

**Does a Jetson suffice?** For inference, probably yes on paper and I would not
bet the project on it. JAX does publish `manylinux2014_aarch64` CUDA 12 wheels,
so an AGX Orin 64 GB has both the wheels and the memory. But nobody has done it,
Orin's bf16 throughput is far below a 4090, and the point is moot: **the policy
server talks to the robot over a WebSocket** (`scripts/serve.py`), so the GPU
does not need to be the machine driving the arms. Put a normal desktop GPU on
the LAN instead. That is the design the author intended and it removes the
Jetson question entirely.

**For the simulation, a Jetson is definitively out.** NVIDIA's Isaac Sim 5.1
requirements page lists exactly one aarch64 configuration — DGX Spark — and
notes that **GPUs without RT cores (A100, H100) are not supported** at all.
Isaac Sim minimum spec is Ubuntu 22.04/24.04 x86_64, RTX 4080, 16 GB VRAM,
32 GB RAM, driver 580.65.06.

### (b) Arms and cameras — inference vs data collection

**Cameras: three, and all three are mandatory for inference.** The overhead
camera plus both wrist cameras. `shared/real_robot_config.py` raises on a
missing entry for any of `top`, `left_wrist`, `right_wrist` — there is no
graceful degradation. The real training dataset confirms the exact shapes:
overhead 1280×720, each wrist 640×480.

The overhead camera in the reference rig is a RealSense D435 mounted ~65 cm
above the table; the code has D435-specific workarounds (an rgb8 format
override and a cold-start timeout bump in `record_real_dagger.py`). Depth is
**not** used — `use_depth` defaults to false and the policy only consumes RGB.
So any decent 720p camera works for the overhead; the RealSense is not special
here, it is just what he had.

**Arms: two followers, 46 cm apart.** Two leaders are needed for teleoperation
and DAgger corrections, and — importantly — **the shipped runner refuses to
start without them even in pure autonomous mode**. `_leader_ports()` in
`record_real_dagger.py` hard-exits if either `leader_port` is missing or the
device does not exist. Running leader-less would need a small patch. Not hard,
worth knowing.

So: 2 followers + 3 cameras is the true inference minimum, but 2 followers +
2 leaders + 3 cameras is what runs out of the box, and you want the leaders
anyway the moment you start collecting data.

### (c) Control rate and latency tolerance

| | |
|---|---|
| Control loop | **20 Hz** (`--fps`, default 20) |
| Action chunk | 30 actions = 1.5 s of trajectory |
| Actions executed per inference | 5 → a new inference every **250 ms** |
| Denoising steps | 10 |

20 Hz is not arbitrary: the official real dataset is recorded at 20 fps with
`robot_type: bi_so_follower`, 500 episodes and 187,135 frames. The policy is
trained in the robot's native degree units at that rate, and nothing is
converted on the inference path.

**The latency behaviour is more forgiving than it looks, and the failure mode
is not what you would guess.** The control loop resets its frame timer *after*
the inference call returns (`record_real_dagger.py:714`). So a slow policy
server does not cause missed deadlines or dropped frames — it inserts dead time
into the trajectory. The arms stall mid-motion every 250 ms. You get jerky,
hesitant folding rather than a crash or a safety event.

Practical targets: **under 100 ms per chunk keeps motion smooth**, 250 ms is the
break-even point where the robot pauses as long as it moves, and anything past
that is visibly stuttering. The WebSocket does have a real timeout — 5-second
ping interval and 5-second ping timeout — so a network stall over 5 s drops the
connection outright.

---

## 2. The gap, and what it costs to close it

### What you have

- SO-101 arms. The repo carries four distinct calibration files —
  `follower_left`, `follower_right`, `leader_left`, `leader_right`, all with
  different values, so they were each calibrated against real hardware. **That
  reads as 2 followers + 2 leaders already on hand**, which is the full LeHome
  arm complement. Nothing was plugged in when I checked, and `robot_config.md`
  still documents only one leader and one follower, so please confirm.
- A Mac mini M4. (This session is running on an M1 Max / 32 GB, whichever box
  that is — worth confirming which machine is meant to do the work.)

### What is missing

| Gap | Why it blocks | What closes it |
|---|---|---|
| **No NVIDIA GPU** | Isaac Sim and `jax[cuda12]` both require one. Hard wall. | Rent, or buy a Linux desktop |
| **No x86_64 Linux** | Isaac Sim has no macOS build | Same box |
| **3 cameras** | 1 overhead + 2 wrist, all mandatory | ~$150 if you have none |
| **Disk space** | This machine has **13 GB free of 926 GB**. The repo wants 500+ GB for full training. | Not a Mac problem if the work happens on Linux |

### Costed options

**Option A — rent, and buy nothing. Recommended for the simulation.**

Live spot prices I pulled today, single GPU, ≥12 vCPU, ≥150 GB disk:

| GPU | VRAM | Median | Cheapest |
|---|---|---|---|
| RTX 4090 | 24 GB | $0.47/hr | $0.14/hr |
| RTX 5090 | 32 GB | $0.45/hr | $0.31/hr |
| RTX 6000 Ada | 48 GB | $0.46/hr | $0.46/hr |
| L40S | 45 GB | $0.54/hr | $0.54/hr |

Insist on **≥32 GB system RAM and ≥16 vCPU** — the cheapest listings skimp on
both, and the garment cloth physics runs on CPU (`eval_worker.py` hardcodes
`--device cpu` for the Isaac Sim process), so cores set your throughput, not the
GPU.

Realistic first run: ~1 hour install, ~1 hour download, ~2-4 hours evaluating
across all garments. **About $3-6 total.** Even a full week of experimentation
is under $80.

**Option B — buy a workstation. Only needed for the real robot.**

The robot-side machine has to be Linux x86_64 next to the arms, because the
camera and serial plumbing is Linux-specific (`/dev/v4l/by-path`,
`/dev/serial/by-id`, `pyrealsense2`, and a `v4l2` camera backend). Rough BOM,
**estimates — price these before ordering**:

| Item | Estimate |
|---|---|
| RTX 4090 24 GB (or 5090 32 GB) | $1,800-2,400 |
| Ryzen 9 / Core i9, 16+ cores | $500-700 |
| 64 GB DDR5 | $200-300 |
| 2 TB NVMe | $150-200 |
| PSU 1000 W, case, board | $450-600 |
| **Total** | **~$3,100-4,200** |

**Option C — DGX Spark.** The only aarch64 machine Isaac Sim supports, ~$4,000,
128 GB unified memory. Tidy in principle but with documented Isaac Sim
limitations (no cuRobo, no livestreaming, no OBJ import). I would not make it
the first purchase.

**Recommendation: A now, B later, and only if the simulation result justifies
it.** Do not buy a GPU to find out whether the simulation works.

---

## 3. Getting the simulation running

`Scripts/lehome_sim_bootstrap.sh` in this repo takes a fresh Ubuntu 24.04 + RTX
box from nothing to a folding video. It refuses to run on anything that cannot
work and says why — including on this Mac, which I verified.

```bash
# on the rented box
scp Scripts/lehome_sim_bootstrap.sh <host>:~
ssh <host> 'bash lehome_sim_bootstrap.sh'
```

It clones with submodules, runs the upstream `setup.sh` (apt deps, uv, both
venvs, Isaac Sim 5.1, the IsaacLab fork, and the 1.0 GB garment assets), pulls
the 10.5 GB `lehome_sim` checkpoint, and runs two evaluations: a fast
metrics-only benchmark across all garments, then one garment with video.

Two deliberate savings: it skips the **18.9 GB behavioural-cloning dataset**,
which is only needed for training, and it does not pass `setup.sh --no-data`,
because that flag would also skip the garment meshes the evaluation needs.
Total download ~12 GB, all public, no Hugging Face token required.

**The number to check:** 80%+ average success on seen garments. If the first
run lands far below that, the install is wrong — do not start tuning
hyperparameters.

### Honest status

**I have not run this.** No machine here can. I read the repository, verified
every claim above against source, pinned the download sizes against the Hugging
Face API, pulled live GPU prices, and wrote and syntax-checked the bootstrap.
What is left is renting a box — which is a purchase, and you said not to buy
anything, so it is yours to approve.

---

## 4. Real-robot bring-up, after the simulation works

Sequenced deliberately. Do not start step 1 before the simulation gives 80%+.

**Step 1 — Camera rig.** Overhead camera ~65 cm above the table; followers
46 cm apart. Align against the official real dataset using
`scripts/real_camera_align.py`. **This is the step most likely to silently cost
you everything.** The policy was trained on one specific viewpoint; camera
placement error looks exactly like a bad policy.

**Step 2 — Hardware mapping.** Fill in `configs/real_robot.yaml` with your four
serial ports and three camera devices. Ports must be stable across reboots —
use `/dev/serial/by-id`, not `/dev/ttyACM*`.

**Step 3 — Zero-shot attempt.** Policy server on the GPU box, robot runner on
the Linux box by the arms, pointed at `ws://<gpu-box>:8000`. Run
`record_real_dagger.py` with a real t-shirt. Expect it to be mediocre — the
reference rig is not your rig — but it tells you the whole pipeline is live.

**Step 4 — DAgger.** Autonomous rollout, human takes over with the leaders when
it fails, everything recorded with per-frame human/policy labels so training can
up-weight the corrections. A foot pedal bound to space/left/right is strongly
recommended by the author and looks worth the $30.

**Step 5 — Fine-tune.** `configs/train_real_bc.yaml`, starting from the
`lehome_real` checkpoint. This is where the 500 GB and the serious GPU hours go.

---

## 5. The pillowcase problem

You asked for a pillowcase. The system knows four garments, none of which is one.

Three ways through, cheapest first:

**Try it zero-shot as `top_short`.** A pillowcase is a flat rectangle — the
simplest thing in the space. The policy conditions on garment class but also
predicts it, so it may cope. Costs one afternoon once the rig is up. Do this
first.

**Teach it by demonstration.** Collect pillowcase episodes with the leaders,
label them `top_short`, fine-tune from `lehome_real`. This is the path the
author's own sim-to-real recipe is built for, and it is the one I would expect
to work.

**Author a pillowcase simulation asset.** A new garment mesh, new keypoint
success conditions, and a new head slice. Most work, only worth it if you want
to train in simulation rather than on demonstrations.

Worth saying plainly: **step 5 of the bring-up is where a folded pillowcase
actually comes from.** Everything before it is making the machine that can learn
one.

---

## What I need from you

One decision: **approve roughly $6 of rented GPU time** (an RTX 4090 for a few
hours) so the simulation can actually run. Nothing else is blocking.

And one confirmation: **do you have four SO-101 arms or two?** Four calibration
files say four; `robot_config.md` says two. If it is two, add one follower and
one leader to the bill of materials.
