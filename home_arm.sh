#!/bin/bash
# Homes the follower arm to a safe position slowly
# Usage: bash home_arm.sh [speed_deg_per_sec]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

SPEED=${1:-10}  # degrees per second, default 10

python3 << 'PYEOF'
import time
import math
from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus

# Home position (degrees) — adjust these to your safe position
HOME = [0.0, -90.0, 90.0, 0.0, 0.0, 0.0]

# Motor IDs for SO-101 follower
MOTOR_IDS = [1, 2, 3, 4, 5, 6]
MOTOR_NAMES = {1: "shoulder_pan", 2: "shoulder_lift", 3: "elbow_flex",
               4: "wrist_flex", 5: "wrist_roll", 6: "gripper"}

bus = FeetechMotorsBus(
    port="/dev/tty.usbmodem5AA90242401",
    motors={i: (i, 777) for i in MOTOR_IDS},
)

try:
    bus.connect()
    print("Connected to follower arm")

    # Read current positions
    current = bus.read("Present_Position", MOTOR_IDS)
    print(f"Current positions: {current}")

    # Calculate max travel distance to determine total time
    max_travel = max(abs(HOME[i] - current[i]) for i in range(len(MOTOR_IDS)))
    total_time = max_travel / float("${SPEED}") if max_travel > 0 else 1.0
    total_time = max(total_time, 1.0)  # at least 1 second

    print(f"Homing over {total_time:.1f}s (max travel: {max_travel:.1f}°)")

    # Interpolate slowly
    steps = int(total_time / 0.05)  # 50ms per step
    for step in range(steps + 1):
        t = step / max(steps, 1)
        positions = [current[i] + (HOME[i] - current[i]) * t for i in range(len(MOTOR_IDS))]
        bus.write("Goal_Position", {mid: positions[i] for i, mid in enumerate(MOTOR_IDS)})
        time.sleep(0.05)

    print("Home position reached ✓")

except Exception as e:
    print(f"Homing failed: {e}")
finally:
    try:
        bus.disconnect()
    except:
        pass
PYEOF
