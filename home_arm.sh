#!/bin/bash
# Homes the follower arm to a safe position slowly
# Usage: bash home_arm.sh [speed_deg_per_sec]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

SPEED=${1:-10}  # degrees per second, default 10

python3 -c "
import time, os
from pathlib import Path
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower

# Home position (degrees) — captured from arm's resting pose
HOME = [-6.5, -103.9, 94.6, 67.7, 0.3, 0.5]
JOINT_NAMES = ['shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper']

script_dir = os.environ.get('SCRIPT_DIR', '.')
config = SOFollowerRobotConfig(
    port='/dev/tty.usbmodem5AA90242401',
    id='follower_right',
    calibration_dir=Path(script_dir) / 'lerobot_calibration',
)

robot = SOFollower(config)
robot.connect()

# Read current positions
state = robot.get_observation()
current = [state[name + '.pos'] for name in JOINT_NAMES]
print('Current: {}'.format(['{:.1f}'.format(v) for v in current]))

# Calculate homing time
max_travel = max(abs(HOME[i] - current[i]) for i in range(6))
speed = float(os.environ.get('SPEED', '10'))
total_time = max(max_travel / speed, 1.0)
print('Homing over {:.1f}s (max travel: {:.1f} deg)'.format(total_time, max_travel))

# Interpolate slowly
steps = int(total_time / 0.05)
for step in range(steps + 1):
    t = step / max(steps, 1)
    target = {JOINT_NAMES[i]: current[i] + (HOME[i] - current[i]) * t for i in range(6)}
    robot.send_action(target)
    time.sleep(0.05)

print('Home position reached')
robot.disconnect()
" 2>&1

echo "Arm homed."
