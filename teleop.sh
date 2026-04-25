#!/bin/bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

# Play backhoe dig sound when teleop starts
afplay "$(dirname "$0")/backhoe_dig.wav"

lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5AA90242401 \
  --robot.id=follower_right \
  --robot.calibration_dir=/Users/peanut/.openclaw/workspace/HelpingHands/lerobot_calibration \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5AAF2627031 \
  --teleop.id=leader_left \
  --teleop.calibration_dir=/Users/peanut/.openclaw/workspace/HelpingHands/lerobot_calibration
