

Helping Hands Readme

iBackpack

Consists of a hardware product. 

A wearable robot set of arms. The arms will be in leader mode 
while wearable and follower mode while not on a user.

The goal: Determine the minimum viable hardware.

If you can successfully operate the arms, to produce more economic value 
than the cost of the hardware, then you have succeeded, from a hardware perspective.

You can subtract the value of the human operator's time, 
because the automation of the humans time is a software problem.

How do you calculate the economic value of a task?

You can use the following formula:

Economic Value = (Revenue - Cost) / Time

So what is the economic value of cooking a meal?

While testing the hardware we will generate two data sets. 

The first is raw video of a human doing a task, no robot involvement.
This data will include the raw video.

The second is data from human operating the robot, doing the same task. 
This data will include the servo positions, and the raw video.

We can then map from the raw video of a human moving their arms, 
to the data set of a human operating the robot. 
And then finally to the robot servo positions. 
In this way, we have a mapping from raw video to servo positions.
This allows teleoperation, with the minimum amount of hardware.

## ⚠️ Teleop: Always Use a Native Terminal

When running `lerobot-teleoperate`, you **must** launch it from a native macOS Terminal.app window, not through any wrapper, pipe, or agent shell (including OpenClaw exec).

### The Jitter Problem

Running teleop through an intermediate process (e.g., OpenClaw's `exec`, a bash subshell with piped output, or any non-TTY context) introduces significant jitter in the control loop. Observed symptoms:

- Loop times fluctuate wildly: 16ms–88ms (12–60 Hz) instead of a steady ~16ms (60 Hz)
- The follower arm stutters and lags behind the leader
- The jitter is noticeable in the arm movement — it's not smooth

### The Fix

Launch directly in Terminal.app using AppleScript or just open a Terminal and paste the command:

```bash
source ~/miniforge3/etc/profile.d/conda.sh && conda activate lerobot && \
lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5AA90242401 \
  --robot.id=follower_right \
  --robot.calibration_dir=/Users/peanut/.openclaw/workspace/HelpingHands/lerobot_calibration \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5AAF2627031 \
  --teleop.id=leader_left \
  --teleop.calibration_dir=/Users/peanut/.openclaw/workspace/HelpingHands/lerobot_calibration
```

Or via AppleScript from an agent:
```bash
osascript -e 'tell application "Terminal" to do script "source ~/miniforge3/etc/profile.d/conda.sh && conda activate lerobot && <command>"'
```

### Why?

The lerobot teleop loop needs consistent, low-latency serial I/O. Any buffering, scheduling overhead, or non-real-time scheduling from intermediate shells introduces enough variance to cause visible jitter in the robot arm movement.
