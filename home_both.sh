#!/bin/bash
# Homes both arms (leader + follower) to safe resting positions smoothly
# Uses servo internal acceleration for smooth motion
# Usage: bash home_both.sh [acceleration] (lower = smoother, default 5)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

ACCEL=${1:-5}

python3 -c "
import os, time
from pathlib import Path
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower
from lerobot.teleoperators.so_leader.so_leader import SOLeader
from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig

# Home positions (degrees) — captured from resting pose
HOME = {'shoulder_pan': -6.5, 'shoulder_lift': -103.9, 'elbow_flex': 94.6, 'wrist_flex': 67.7, 'wrist_roll': 0.3, 'gripper': 0.5}

script_dir = os.environ.get('SCRIPT_DIR', '.')
accel = int(os.environ.get('ACCEL', '5'))
cal_dir = Path(script_dir) / 'lerobot_calibration'

def home_arm(arm, name):
    bus = arm.bus
    motor_keys = list(bus.motors.keys())
    
    # Set low acceleration
    for key in motor_keys:
        bus.write('Maximum_Acceleration', key, accel * 2)
        bus.write('Acceleration', key, accel)
    
    # Write goal positions
    for key, pos in HOME.items():
        if key in bus.motors:
            bus.write('Goal_Position', key, pos)
            print('  {} -> {:.1f}'.format(key, pos))
    
    print('{} homing (accel={})...'.format(name, accel))
    
    # Wait for motion to complete
    settled_count = 0
    for attempt in range(200):
        time.sleep(0.1)
        try:
            if hasattr(arm, 'get_observation'):
                state = arm.get_observation()
            else:
                state = arm.get_action()
            current = {k.replace('.pos', ''): state[k] for k in state}
            max_error = max(abs(current.get(k, pos) - pos) for k, pos in HOME.items() if k in current)
            if max_error < 0.5:
                settled_count += 1
                if settled_count >= 3:
                    print('  {} homed! (error: {:.2f})'.format(name, max_error))
                    break
            else:
                settled_count = 0
        except:
            pass
    
    arm.disconnect()

# Home follower
print('=== Follower ===')
follower_config = SOFollowerRobotConfig(
    port='/dev/tty.usbmodem5AA90242401',
    id='follower_right',
    calibration_dir=cal_dir,
)
follower = SOFollower(follower_config)
follower.connect()
home_arm(follower, 'Follower')

# Home leader
print('=== Leader ===')
leader_config = SOLeaderTeleopConfig(
    port='/dev/tty.usbmodem5AAF2627031',
    id='leader_left',
    calibration_dir=cal_dir,
)
leader = SOLeader(leader_config)
leader.connect()
home_arm(leader, 'Leader')

print('Both arms homed')
" 2>&1
