#!/bin/bash
# Syncs the follower arm to the leader arm's current position slowly
# Then disables torque so teleop can start smoothly from that position
# Usage: bash sync_arm.sh [speed_deg_per_sec]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

SPEED=${1:-10}  # degrees per second, default 10

python3 -c "
import time, os
from pathlib import Path
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.robots.so_leader.config_so_leader import SOLeaderRobotConfig
from lerobot.robots.so_leader.so_leader import SOLeader

JOINT_KEYS = ['shoulder_pan.pos', 'shoulder_lift.pos', 'elbow_flex.pos', 'wrist_flex.pos', 'wrist_roll.pos', 'gripper.pos']

script_dir = os.environ.get('SCRIPT_DIR', '.')

# Read leader position
leader_config = SOLeaderRobotConfig(
    port='/dev/tty.usbmodem5AAF2627031',
    id='leader_left',
    calibration_dir=Path(script_dir) / 'lerobot_calibration',
)
leader = SOLeader(leader_config)
leader.connect()
leader_state = leader.get_observation()
target = {k: leader_state[k] for k in JOINT_KEYS}
leader.disconnect()
print('Leader position: {}'.format({k: '{:.1f}'.format(v) for k, v in target.items()}))

# Connect to follower and read current position
follower_config = SOFollowerRobotConfig(
    port='/dev/tty.usbmodem5AA90242401',
    id='follower_right',
    calibration_dir=Path(script_dir) / 'lerobot_calibration',
)
follower = SOFollower(follower_config)
follower.connect()
state = follower.get_observation()
current = {k: state[k] for k in JOINT_KEYS}
print('Follower position: {}'.format({k: '{:.1f}'.format(v) for k, v in current.items()}))

# Calculate sync time
max_travel = max(abs(target[k] - current[k]) for k in JOINT_KEYS)
speed = float(os.environ.get('SPEED', '10'))
total_time = max(max_travel / speed, 0.5)
print('Syncing over {:.1f}s (max travel: {:.1f} deg)'.format(total_time, max_travel))

# Interpolate slowly from current to target
steps = int(total_time / 0.05)
for step in range(steps + 1):
    t = step / max(steps, 1)
    action = {k: current[k] + (target[k] - current[k]) * t for k in JOINT_KEYS}
    follower.send_action(action)
    time.sleep(0.05)

# Verify we arrived
final = follower.get_observation()
print('Final position: {}'.format({k: '{:.1f}'.format(final[k]) for k in JOINT_KEYS}))

# Disable torque so arm goes limp — ready for teleop
for key in follower.bus.motors.keys():
    follower.bus.write('Torque_Enable', key, 0)
print('Torque disabled — arm is limp, ready for teleop')

follower.disconnect()
" 2>&1

echo "Arm synced and relaxed."
