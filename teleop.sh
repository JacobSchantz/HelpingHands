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
# Running teleop through an intermediate process (e.g., OpenClaw's exec, a
# bash subshell with piped output, or any non-TTY context) introduces
# significant jitter in the control loop. Observed symptoms:
#
# - Loop times fluctuate wildly: 16ms–88ms (12–60 Hz) instead of steady ~16ms (60 Hz)
# - The follower arm stutters and lags behind the leader
# - The jitter is noticeable in the arm movement — it's not smooth
#
# THE FIX
#
# Launch directly in Terminal.app using AppleScript or paste the command:
#
#   osascript -e 'tell application "Terminal" to do script "bash /path/to/teleop.sh"'
#
# WHY? The lerobot teleop loop needs consistent, low-latency serial I/O. Any
# buffering, scheduling overhead, or non-real-time scheduling from
# intermediate shells introduces enough variance to cause visible jitter.
#
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

# Play startup sound
afplay "$SCRIPT_DIR/sounds/lobster_click.wav"

lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5AA90242401 \
  --robot.id=follower_right \
  --robot.calibration_dir="$SCRIPT_DIR/lerobot_calibration" \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5AAF2627031 \
  --teleop.id=leader_left \
  --teleop.calibration_dir="$SCRIPT_DIR/lerobot_calibration"
