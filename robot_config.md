# SO-101 Robot Config

## Arms

| Role    | ID             | Type           | Port                           |
|---------|----------------|----------------|--------------------------------|
| Leader  | leader_left    | so101_leader   | /dev/tty.usbmodem5AAF2627031  |
| Follower | follower_right | so101_follower | /dev/tty.usbmodem5AA90242401  |

## Calibration

Calibration files: `lerobot_calibration/`
- `leader_left.json`
- `follower_right.json`

## Find Ports

```bash
source ~/miniforge3/etc/profile.d/conda.sh && conda activate lerobot
lerobot-find-port
```

## Setup Motors (run once per arm)

```bash
# Follower
lerobot-setup-motors --robot.type=so101_follower --robot.port=/dev/tty.usbmodem5AA90242401

# Leader
lerobot-setup-motors --teleop.type=so101_leader --teleop.port=/dev/tty.usbmodem5AAF2627031
```

## Calibrate (run once per arm)

```bash
# Follower
lerobot-calibrate --robot.type=so101_follower --robot.port=/dev/tty.usbmodem5AA90242401 --robot.id=follower_right

# Leader
lerobot-calibrate --teleop.type=so101_leader --teleop.port=/dev/tty.usbmodem5AAF2627031 --teleop.id=leader_left
```

## Teleoperate

```bash
bash teleop.sh
```

⚠️ Always run in native Terminal.app — see jitter warning in readme.txt

## Raspberry Pi Setup

The arms can also run on a Pi with ports `/dev/ttyACM0` and `/dev/ttyACM1`:

```bash
lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower_right \
  --teleop.type=so101_leader \
  --teleop.port=/dev/ttyACM1 \
  --teleop.id=leader_left
```

SSH into Pi: `ssh yacsclaw@192.168.0.28`
