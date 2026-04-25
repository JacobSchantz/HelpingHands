#!/bin/bash
# Syncs the follower arm to the leader arm's current position smoothly
# Uses servo internal acceleration for smooth motion, then disables torque
# Usage: bash sync_arm.sh [acceleration] (lower = smoother, default 5)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

ACCEL=${1:-5}

python3 -c "
import os
from pathlib import Path
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.teleoperators.so_leader.so_leader import SOLeader
from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig

JOINT_KEYS = ['shoulder_pan.pos', 'shoulder_lift.pos', 'elbow_flex.pos', 'wrist_flex.pos', 'wrist_roll.pos', 'gripper.pos']
HOME_NAMES = ['shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper']

script_dir = os.environ.get('SCRIPT_DIR', '.')
accel = int(os.environ.get('ACCEL', '5'))

# Read leader position
leader_config = SOLeaderTeleopConfig(
    port='/dev/tty.usbmodem5AAF2627031',
    id='leader_left',
    calibration_dir=Path(script_dir) / 'lerobot_calibration',
)
leader = SOLeader(leader_config)
leader.connect()
leader_action = leader.get_action()
target = {JOINT_KEYS[i]: leader_action[JOINT_KEYS[i]] for i in range(6)}
leader.disconnect()
print('Leader: {}'.format({k: '{:.1f}'.format(v) for k, v in target.items()}))

# Connect to follower
follower_config = SOFollowerRobotConfig(
    port='/dev/tty.usbmodem5AA90242401',
    id='follower_right',
    calibration_dir=Path(script_dir) / 'lerobot_calibration',
)
follower = SOFollower(follower_config)
follower.connect()
bus = follower.bus

# Set low acceleration on all motors for smooth motion
for key in bus.motors.keys():
    bus.write('Maximum_Acceleration', key, accel * 2)
    bus.write('Acceleration', key, accel)

# Write goal positions — servos handle smooth interpolation internally
for i, name in enumerate(HOME_NAMES):
    bus.write('Goal_Position', name, target[JOINT_KEYS[i]])
    print('{} -> {:.1f}'.format(name, target[JOINT_KEYS[i]]))

print('Syncing (accel={})...'.format(accel))

# Wait for motion to complete — poll until positions settle
import time
time.sleep(1)
for _ in range(50):
    state = follower.get_observation()
    current = [state[k] for k in JOINT_KEYS]
    goals = [target[k] for k in JOINT_KEYS]
    if all(abs(current[i] - goals[i]) < 1.0 for i in range(6)):
        break
    time.sleep(0.2)

# Disable torque — arm goes limp, ready for teleop
for key in bus.motors.keys():
    bus.write('Torque_Enable', key, 0)
print('Torque disabled — ready for teleop')

follower.disconnect()
" 2>&1

echo "Arm synced and relaxed."
