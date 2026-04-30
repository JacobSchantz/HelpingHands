#!/bin/bash
# Converts a recording JSON to a deterministic playback script
# Usage: bash convert_recording.sh <recording_name> [speed_multiplyer]
# Output: recordings/<recording_name>_playback.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

RECORDING_NAME=$1
SPEED=${2:-1.0}  # multiplier, 1.0 = real-time, 2.0 = 2x speed

if [ -z "$RECORDING_NAME" ]; then
    echo "Usage: bash convert_recording.sh <recording_name> [speed_multiplier]"
    exit 1
fi

INPUT_FILE="$SCRIPT_DIR/recordings/${RECORDING_NAME}.json"
OUTPUT_FILE="$SCRIPT_DIR/recordings/${RECORDING_NAME}_playback.sh"

if [ ! -f "$INPUT_FILE" ]; then
    echo "Recording not found: $INPUT_FILE"
    exit 1
fi

python3 -c "
import json, time

with open('$INPUT_FILE') as f:
    data = json.load(f)

frames = data['frames']
duration = data['metadata']['duration_s']
num_frames = data['metadata']['num_frames']

# Generate playback commands
JOINT_KEYS = ['shoulder_pan.pos', 'shoulder_lift.pos', 'elbow_flex.pos', 'wrist_flex.pos', 'wrist_roll.pos', 'gripper.pos']
JOINT_NAMES = ['shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper']

# Build interpolation steps from frames
# For each consecutive pair, compute time delta and interpolate
steps = []
for i in range(len(frames) - 1):
    t0 = frames[i]['time']
    t1 = frames[i+1]['time']
    dt = t1 - t0
    if dt > 0:
        delay_ms = int((dt / float('$SPEED')) * 1000)
        for name, key in zip(JOINT_NAMES, JOINT_KEYS):
            pos = frames[i]['positions'][key]
            steps.append('bus.write(\"Goal_Position\", \"{}\", {:.1f})'.format(name, pos))
        steps.append('time.sleep({})'.format(delay_ms / 1000.0))

with open('$OUTPUT_FILE', 'w') as f:
    f.write('''#!/bin/bash
# Auto-generated playback script
# Generated from: $RECORDING_NAME
# Duration: {:.1f}s | Frames: {} | Speed: {}x
#
# Run in Terminal.app to avoid jitter

SCRIPT_DIR=\"\$(cd \"\$(dirname \"\$0\")\" && pwd)\"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

python3 -c \"
import time
from pathlib import Path
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower

cal_dir = Path(\"\$SCRIPT_DIR\").parent / \"lerobot_calibration\"
config = SOFollowerRobotConfig(
    port=\"/dev/tty.usbmodem5AA90242401\",
    id=\"follower_right\",
    calibration_dir=cal_dir,
)
robot = SOFollower(config)
robot.connect()
bus = robot.bus

# Set low acceleration for smooth playback
for key in bus.motors.keys():
    bus.write(\"Maximum_Acceleration\", key, 50)
    bus.write(\"Acceleration\", key, 20)

# Playback
print(\"Playing back: $RECORDING_NAME\")

'''.strip() + chr(10))

    # Write interpolation steps
    for step in steps:
        f.write(step + chr(10))

    f.write(chr(10) + '''

print("Playback complete")
robot.disconnect()
"''' + chr(10))

import os
os.chmod('$OUTPUT_FILE', 0o755)
print("Generated: $OUTPUT_FILE")
print("  Duration: {:.1f}s | Speed: {}x".format(duration, '$SPEED'))
print("  Run with: bash {}".format('$OUTPUT_FILE'))
"
