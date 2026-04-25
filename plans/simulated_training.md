# Simulated Training Pipeline

## Goal

Record real teleop demos, then algorithmically generate hundreds of simulated variations to train a policy — without needing a human for each demo.

## Phase 1: Record Real Demos

Use `lerobot-record` to capture teleop sessions. Start with just 5-10 real demos of a single task.

```bash
# Record in Terminal.app (see teleop.sh for jitter warning)
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5AA90242401 \
  --robot.id=follower_right \
  --robot.calibration_dir=lerobot_calibration \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5AAF2627031 \
  --teleop.id=leader_left \
  --teleop.calibration_dir=lerobot_calibration \
  --fps 30 \
  --repo-id peanut/helping-hands \
  --num-episodes 10 \
  --episode-time-s 30
```

Output: A LeRobot dataset with 10 episodes of joint trajectories.

## Phase 2: Augment Demos

Take each recorded episode and generate N synthetic variations:

### Augmentation Strategies

1. **Gaussian noise on joint positions** — ±2-5° jitter per joint per timestep
2. **Temporal scaling** — play back 10-30% faster or slower
3. **Start position offset** — shift all joint angles by a small constant
4. **Trajectory warping** — slight curve modifications via spline interpolation
5. **Mirror** — swap left/right joints (if task is symmetric)

### Target: 10 real demos → 200+ augmented episodes

Script to write: `scripts/augment_demos.py`
- Reads a LeRobot dataset
- Applies augmentation strategies
- Writes augmented dataset in LeRobot format

## Phase 3: Train on Augmented Data

```bash
lerobot-train \
  policy=act \
  env=so101 \
  dataset.repo_id=peanut/helping-hands-augmented \
  training.offline_steps=100000
```

## Phase 4: Evaluate on Real Robot

```bash
lerobot-evaluate -p peanut/helping-hands-act eval.n_episodes=10
```

## What's NOT in scope (yet)
- ❌ Human video → robot pose estimation
- ❌ Simulation environment (Isaac Gym, MuJoCo)
- ❌ Camera/vision-based policies

## Next Steps
1. Pick a simple task (e.g., pick up object, place in bin)
2. Set up recording environment (consistent lighting, camera angle, object positions)
3. Record 10 real demos
4. Write augmentation script
5. Train and evaluate
