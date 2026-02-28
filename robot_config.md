# SO-101 Robot Configuration

## Setup Conda

```bash
# Install Miniforge (if not installed)
curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh
bash Miniforge3-Linux-aarch64.sh

# Add to PATH (run once)
echo 'export PATH="$HOME/miniforge3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

conda create -n lerobot python=3.10 -y
conda activate lerobot
pip install lerobot

## USB Port Assignments

| Arm      | Side  | Port                           |
| -------- | ----- | ------------------------------ |
| Leader   | Left  | `/dev/tty.usbmodem5AAF2627031` |
| Follower | Right | `/dev/tty.usbmodem5AA90242401` |

## Useful Commands

### Find ports

```bash
source ~/miniforge3/etc/profile.d/conda.sh && conda activate lerobot
lerobot-find-port
```

### Setup motors (run once per arm)

```bash
# Follower (right arm)
lerobot-setup-motors \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5AA90242401

# Leader (left arm)
lerobot-setup-motors \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5AAF2627031
```

### Calibrate (run once per arm)

```bash
# Follower (right arm)
lerobot-calibrate \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5AA90242401 \
  --robot.id=follower_right

# Leader (left arm)
lerobot-calibrate \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5AAF2627031 \
  --teleop.id=leader_left
```

### Teleoperate

```bash
lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5AA90242401 \
  --robot.id=follower_right \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5AAF2627031 \
  --teleop.id=leader_left
```

lerobot-teleoperate \
 --robot.type=so101_follower \
 --robot.port=/dev/ttyACM0 \
 --robot.id=follower_right \
 --teleop.type=so101_leader \
 --teleop.port=/dev/ttyACM1 \
 --teleop.id=leader_left
