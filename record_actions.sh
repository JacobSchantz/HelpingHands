#!/bin/bash
# Records follower arm positions while you perform actions with the leader
# Usage: bash record_actions.sh [output_name]
# Recording starts immediately, press Ctrl+C to stop

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

OUTPUT_NAME=${1:-recording_$(date +%s)}
OUTPUT_FILE="$SCRIPT_DIR/recordings/${OUTPUT_NAME}.json"
mkdir -p "$SCRIPT_DIR/recordings"

python3 -c "
import os, time, json, signal, sys
from pathlib import Path
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower

JOINT_KEYS = ['shoulder_pan.pos', 'shoulder_lift.pos', 'elbow_flex.pos', 'wrist_flex.pos', 'wrist_roll.pos', 'gripper.pos']

script_dir = os.environ.get('SCRIPT_DIR', '.')
cal_dir = Path(script_dir) / 'lerobot_calibration'

config = SOFollowerRobotConfig(
    port='/dev/tty.usbmodem5AA90242401',
    id='follower_right',
    calibration_dir=cal_dir,
)
robot = SOFollower(config)
robot.connect()

recording = []
start_time = time.time()
running = True

def stop(signum, frame):
    global running
    running = False
    print('\nRecording stopped')

signal.signal(signal.SIGINT, stop)

print('Recording started — move the leader arm')
print('Press Ctrl+C to stop')
print()

while running:
    state = robot.get_observation()
    elapsed = time.time() - start_time
    positions = {k: state[k] for k in JOINT_KEYS}
    recording.append({'time': round(elapsed, 3), 'positions': positions})
    time.sleep(0.05)  # 20Hz sampling

# Save recording
with open('$OUTPUT_FILE', 'w') as f:
    json.dump({
        'metadata': {
            'num_frames': len(recording),
            'duration_s': round(recording[-1]['time'], 3) if recording else 0,
            'created': time.strftime('%Y-%m-%d %H:%M:%S'),
        },
        'frames': recording
    }, f, indent=2)

robot.disconnect()
print('Saved {} frames to $OUTPUT_FILE'.format(len(recording)))
"
