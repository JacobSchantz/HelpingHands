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
# significant jitter in the control loop.
#
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

# Play startup sound
afplay "$SCRIPT_DIR/sounds/lobster_click.wav"

python3 -c "
import time, sys, subprocess
from pathlib import Path
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.teleoperators.so_leader.so_leader import SOLeader
from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig

JOINT_KEYS = ['shoulder_pan.pos', 'shoulder_lift.pos', 'elbow_flex.pos', 'wrist_flex.pos', 'wrist_roll.pos', 'gripper.pos']
JOINT_NAMES = ['shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper']
cal_dir = Path('$SCRIPT_DIR/lerobot_calibration')

# Step 1: Read leader position
print('Reading leader position...')
leader_config = SOLeaderTeleopConfig(
    port='/dev/tty.usbmodem5AAF2627031',
    id='leader_left',
    calibration_dir=cal_dir,
)
leader = SOLeader(leader_config)
leader.connect()
leader_action = leader.get_action()
target = {JOINT_KEYS[i]: leader_action[JOINT_KEYS[i]] for i in range(6)}
leader.disconnect()
print('Leader: {}'.format({k: '{:.1f}'.format(v) for k, v in target.items()}))

# Step 2: Connect follower with LOW acceleration, move to leader position
print('Connecting follower (low accel for smooth sync)...')
follower_config = SOFollowerRobotConfig(
    port='/dev/tty.usbmodem5AA90242401',
    id='follower_right',
    calibration_dir=cal_dir,
)
follower = SOFollower(follower_config)
follower.connect()

# Override acceleration to low values after configure sets them to 254
bus = follower.bus
for key in bus.motors.keys():
    bus.write('Maximum_Acceleration', key, 10)
    bus.write('Acceleration', key, 5)

# Write goal positions
for i, name in enumerate(JOINT_NAMES):
    bus.write('Goal_Position', name, target[JOINT_KEYS[i]])

print('Syncing follower to leader (slow)...')

# Wait for motion to complete
settled_count = 0
for attempt in range(200):
    time.sleep(0.1)
    state = follower.get_observation()
    current = [state[k] for k in JOINT_KEYS]
    goals = [target[k] for k in JOINT_KEYS]
    max_error = max(abs(current[i] - goals[i]) for i in range(6))
    if max_error < 0.5:
        settled_count += 1
        if settled_count >= 3:
            print('Synced! Max error: {:.2f}'.format(max_error))
            break
    else:
        settled_count = 0
        if attempt % 10 == 0:
            print('  Waiting... max error: {:.1f}'.format(max_error))
else:
    print('Warning: did not fully settle (max error: {:.1f})'.format(max_error))

# Disconnect so teleop can take over
follower.disconnect()
print('Sync complete, starting teleop...')
sys.stdout.flush()
"

# Step 3: Start teleop (lerobot-teleoperate will set accel back to 254 = fast, which is fine now that we're synced)
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
