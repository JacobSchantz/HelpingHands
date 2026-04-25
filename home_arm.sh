#!/bin/bash
# Homes the follower arm to a safe position slowly
# Uses servo internal acceleration control for smooth motion
# Usage: bash home_arm.sh [acceleration] (default: 5, lower = smoother)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

ACCEL=${1:-5}

python3 -c "
import os
from pathlib import Path
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower

# Home position (degrees) — captured from arm's resting pose
HOME = {'shoulder_pan': -6.5, 'shoulder_lift': -103.9, 'elbow_flex': 94.6, 'wrist_flex': 67.7, 'wrist_roll': 0.3, 'gripper': 0.5}

script_dir = os.environ.get('SCRIPT_DIR', '.')
accel = int(os.environ.get('ACCEL', '5'))

config = SOFollowerRobotConfig(
    port='/dev/tty.usbmodem5AA90242401',
    id='follower_right',
    calibration_dir=Path(script_dir) / 'lerobot_calibration',
)

robot = SOFollower(config)
robot.connect()

bus = robot.bus
motor_keys = list(bus.motors.keys())

# Enable torque, set low acceleration, then write goal positions
for key in motor_keys:
    try:
        bus.write('Torque_Enable', key, 1)  # enable torque first
        bus.write('Maximum_Acceleration', key, accel * 2)
        bus.write('Acceleration', key, accel)
    except Exception as e:
        print('{} setup error: {}'.format(key, e))

# Write goal positions — servos handle smooth interpolation
for key, pos in HOME.items():
    bus.write('Goal_Position', key, pos)
    print('{} -> {:.1f}'.format(key, pos))

print('Homing (accel={})...'.format(accel))
robot.disconnect()
" 2>&1
