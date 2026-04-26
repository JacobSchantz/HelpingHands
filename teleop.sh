#!/bin/bash
# ============================================================================
# TELEOP NOTES — Read before running
# ============================================================================
#
# ⚠️ ALWAYS USE A NATIVE TERMINAL
#
# When running `lerobot-teleoperate`, you MUST launch it from a native macOS
# Terminal.app window, not through any wrapper, pipe, or agent shell
# (including OpenClaw exec).
#
# THE JITTER PROBLEM
#
# Running teleop through an intermediate process introduces significant
# jitter in the control loop.
#
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

# Play startup sound
afplay "$SCRIPT_DIR/sounds/lobster_click.wav"

# Sync before teleop (uncomment if needed — run sync_arm.sh separately)
# bash "$SCRIPT_DIR/sync_arm.sh" 5

lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5AA90242401 \
  --robot.id=follower_right \
  --robot.calibration_dir="$SCRIPT_DIR/lerobot_calibration" \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5AAF2627031 \
  --teleop.id=leader_left \
  --teleop.calibration_dir="$SCRIPT_DIR/lerobot_calibration"

# Disable torque on both arms after teleop stops
python3 -c "
from pathlib import Path
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.teleoperators.so_leader.so_leader import SOLeader
from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig

cal_dir = Path('$SCRIPT_DIR/lerobot_calibration')

try:
    f = SOFollower(SOFollowerRobotConfig(port='/dev/tty.usbmodem5AA90242401', id='follower_right', calibration_dir=cal_dir))
    f.connect()
    for k in f.bus.motors.keys():
        f.bus.write('Torque_Enable', k, 0)
    f.disconnect()
    print('Follower torque off')
except: pass

try:
    l = SOLeader(SOLeaderTeleopConfig(port='/dev/tty.usbmodem5AAF2627031', id='leader_left', calibration_dir=cal_dir))
    l.connect()
    for k in l.bus.motors.keys():
        l.bus.write('Torque_Enable', k, 0)
    l.disconnect()
    print('Leader torque off')
except: pass
"
