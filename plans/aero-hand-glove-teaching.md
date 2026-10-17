# Aero Hand: glove teaching ("transparent mode")

Recorded 2026-10-17 from a voice session with Jake.

## Idea
Teach the hand by moving it. Each servo runs in torque mode with a small constant pull, just enough to
keep its cord taut against the return spring. Then a person can move the fingers both ways:
- Flexing a finger slackens the cord, and the spool winds it in.
- Extending a finger pulls the cord out against the small torque, helped by the spring.

Every servo position stays readable, so the hand records what was done to it. Jake would wear a glove
that holds his hand and the robot hand together, so his finger motions drive the robot fingers
directly (kinesthetic demonstration).

## Why
- The data is collected on the robot's own joints, so there's no retargeting error, unlike camera teleop.
- It pairs with the reBot arm (leader arm for the arm, glove for the hand) to record full demonstrations
  into LeRobot datasets for training. See the arm pebble voice-feeaa556 and the HelpingHands north star (VLA).

## How (firmware already supports it)
- CTRL_TOR (`AeroHand.ctrl_torque`, 0-1000 per servo) switches the servos to current/torque mode,
  pulling in the grasp direction. The firmware applies at least HOLD_MAG = 5, and caps torque at
  500 above 70 °C.
- Read positions while in torque mode with `get_actuations()` / `get_joint_positions_compact()`.

## Steps
1. Bench test: torque ~50 on each finger, stream positions, and move each finger by hand. Check that
   the spool follows in both directions and find the lowest torque that keeps each cord taut.
2. Tune per finger, and by angle if the spring force varies a lot (lookup table: angle -> torque).
3. Build `teach.py`: hold transparent mode, log joint positions at about 100 Hz with timestamps and
   camera frames, and replay a recording in position mode.
4. Design the glove: a thin glove or straps coupling each human finger to the matching robot finger,
   on the left hand to match.
5. Combine with the arm: record a LeRobot dataset with the arm leader, the glove-driven hand, and two
   eye-height cameras.

## Watch out for
- Heat: low torque should stay cool, but log temperatures and respect the 70 °C firmware cutoff.
- Thumb: abduction is a linkage (back-drivable directly); flex and tendon are cords like the fingers.
- Switching back to position mode afterwards (CTRL_POS re-enables ServoMode).

## Bench test 1 (2026-10-17, torque 50 on every servo, 45 s, `scripts/transparent_test.py`)
- Index: followed Jake by hand smoothly through the full range (actuation 48 -> 279 -> 55), both ways.
- Middle: followed the same way (49 -> 216 by the end of the run).
- Ring and pinky: sat curled the whole time (277 / 268). At torque 50 their pull beats their springs,
  so they need a lower per-finger torque.
- Rest point at torque 50 isn't fully open (index/middle settled ~48 of ~288), so 50 is a bit strong
  for those too. Next: sweep torque per finger to find the balance point.
- Temperatures flat (42-49 C) the whole run, so the heat cost is negligible.
