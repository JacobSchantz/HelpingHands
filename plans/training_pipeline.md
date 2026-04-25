# Helping Hands — Training Pipeline

## Overview

The goal: record human teleoperation demos, train a neural network policy, then deploy it so the robot can perform the task autonomously.

## Step 1: Record Demonstrations

While teleoperating the leader arm, `lerobot-record` captures the follower arm's joint positions at each timestep. These become your training dataset.

### Prerequisites
- Both arms connected and calibrated (see `robot_config.md`)
- Conda environment activated: `conda activate lerobot`
- A HuggingFace account for dataset storage (optional but recommended)
- A camera (optional — position-only training works too)

### Record Command

```bash
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5AA90242401 \
  --robot.id=follower_right \
  --robot.calibration_dir=/Users/peanut/.openclaw/workspace/HelpingHands/lerobot_calibration \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5AAF2627031 \
  --teleop.id=leader_left \
  --teleop.calibration_dir=/Users/peanut/.openclaw/workspace/HelpingHands/lerobot_calibration \
  --fps 30 \
  --repo-id peanut/helping-hands \
  --tags v1 \
  --warmup-time-s 5 \
  --episode-time-s 60 \
  --reset-time-s 5 \
  --num-episodes 50
```

### Parameters
| Param | Description |
|-------|-------------|
| `--fps` | Capture rate. 30 is standard for SO-101 |
| `--repo-id` | HuggingFace dataset repo (auto-created on push) |
| `--tags` | Version tag for this recording session |
| `--warmup-time-s` | Time before recording starts (get hands in position) |
| `--episode-time-s` | Max length of each demo episode |
| `--reset-time-s` | Time between episodes to reset the scene |
| `--num-episodes` | Number of demos to record. ACT needs ~50-100 for decent results |

### Recording Tips
- Be consistent: same start position, same motion each time
- Consistent lighting and camera angle (if using vision)
- It's OK to have some bad episodes — you can filter later
- The system will prompt you between episodes to reset

### Run in Native Terminal
```bash
osascript -e 'tell application "Terminal" to do script "source ~/miniforge3/etc/profile.d/conda.sh && conda activate lerobot && lerobot-record --robot.type=so101_follower --robot.port=/dev/tty.usbmodem5AA90242401 --robot.id=follower_right --robot.calibration_dir=/Users/peanut/.openclaw/workspace/HelpingHands/lerobot_calibration --teleop.type=so101_leader --teleop.port=/dev/tty.usbmodem5AAF2627031 --teleop.id=leader_left --teleop.calibration_dir=/Users/peanut/.openclaw/workspace/HelpingHands/lerobot_calibration --fps 30 --repo-id peanut/helping-hands --num-episodes 50 --episode-time-s 60"'
```

⚠️ Always run in native Terminal.app (see jitter warning in readme.txt)

---

## Step 2: Train a Policy

### Option A: ACT (Action Chunking with Transformers)
Best for: Manipulation tasks, handles multi-step actions well

```bash
lerobot-train \
  policy=act \
  env=so101 \
  dataset.repo_id=peanut/helping-hands \
  training.offline_steps=100000 \
  training.save_every=10000 \
  training.eval_every=10000
```

### Option B: Diffusion Policy
Best for: Smoother motions, more expressive but slower inference

```bash
lerobot-train \
  policy=diffusion \
  env=so101 \
  dataset.repo_id=peanut/helping-hands \
  training.offline_steps=200000
```

### Hardware Requirements
| Hardware | Training Time (est.) |
|----------|---------------------|
| Mac M-series (MPS) | ~2-4 hours for 100k steps |
| NVIDIA GPU (RTX 3090) | ~30-60 minutes |
| CPU only | ~8-12 hours |

### Monitor Training
Training logs go to `outputs/` directory. You can also use wandb for visualization:
```bash
export WANDB_API_KEY=your_key
lerobot-train ... training.wandb.enable=true
```

---

## Step 3: Evaluate / Deploy

### Run the trained policy on the robot
```bash
lerobot-evaluate \
  -p peanut/helping-hands-act \
  eval.n_episodes=10
```

### Or control manually
```bash
lerobot-control \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5AA90242401 \
  --robot.id=follower_right \
  --policy peanut/helping-hands-act
```

---

## Decision Points

### Do we need a camera?
- **Position-only**: Simpler, works for fixed-position tasks. Trains faster.
- **Vision-based**: More flexible, handles variable positions. Needs camera setup + more data.
- Recommendation: Start position-only, add vision later.

### What task to train on?
Pick something simple and repeatable:
1. Pick up object from position A, place at position B
2. Push a button
3. Open/close a drawer
4. Pour from one container to another

Start with #1 — it's the "hello world" of robot learning.

### How many episodes?
- Minimum viable: 25 episodes
- Good results: 50-100 episodes
- Great results: 100-200 episodes
- Diminishing returns after ~200

---

## Full Pipeline Quick Start

```bash
# 1. Activate environment
conda activate lerobot

# 2. Record 50 demos (run in Terminal.app!)
lerobot-record ... --num-episodes 50

# 3. Train
lerobot-train policy=act env=so101 dataset.repo_id=peanut/helping-hands

# 4. Evaluate
lerobot-evaluate -p peanut/helping-hands-act eval.n_episodes=10
```

---

## References
- [LeRobot Docs](https://huggingface.co/docs/lerobot)
- [ACT Paper](https://arxiv.org/abs/2304.13705)
- [SO-101 Setup Guide](https://github.com/huggingface/lerobot/blob/main/examples/10_use_so100.md)
