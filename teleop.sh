#!/bin/bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

# Play T-Rex roar when teleop starts
afplay "$(dirname "$0")/trex_roar.mp3" &

# Play a second roar after teleop connects (3s delay)
(sleep 3 && afplay "$(dirname "$0")/trex_roar.mp3") &

lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5AA90242401 \
  --robot.id=follower_right \
  --robot.calibration_dir=/Users/peanut/.openclaw/workspace/HelpingHands/lerobot_calibration \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5AAF2627031 \
  --teleop.id=leader_left \
  --teleop.calibration_dir=/Users/peanut/.openclaw/workspace/HelpingHands/lerobot_calibration
