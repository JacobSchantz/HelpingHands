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

## teach.py, first version (2026-10-17, voice-563b984c)
- `scripts/teach.sh record` / `replay [take|last]`, and Record / Replay last buttons in the app's Teach section
  (Stop ends a recording and saves it). Takes: `~/HelpingHands-tools/aero/takes/*.json`
  (`samples` = `[t, 7 actuations]` at 100 Hz, `temps` once a second, plus the torques used).
- Starting torques `[10, 30, 30, 40, 40, 25, 25]` (thumb abd, flex, tendon, index, middle, ring, pinky).
  Smoke test with nobody touching the hand: index/middle at 40 stay wherever they are, curled or open (good,
  that's what transparent should feel like). Ring/pinky at 25 drift open slowly from a fist (~15° per second).
  Thumb abduction at 10 and thumb tendon at 30 drift toward closed, so those two are still too strong.
- The recording is the spool angle, not the finger: if Jake flexes faster than the spool can wind in at its
  small torque, the cord goes slack and the take lags his finger. So "lowest torque that keeps the cord taut"
  has to hold at teaching speed, not just at rest.
- Replay sends CTRL_POS at 100 Hz. That holds the servo bus, so the firmware's own 100 Hz position read skips
  cycles and readings go stale until the bus is quiet; teach.py waits 0.5 s before the end-of-replay hold.

## Glove options (left hand)
1. **Velcro finger straps (recommended first).** One loop per finger around Jake's middle segment and the
   robot's matching link, plus one strap around both palms. No elastic force of its own, so the torque tuning
   stays as tuned bare, and each finger can be loosened alone. Cheap and works today.
2. **Stretchy knit ("magic") winter glove over both hands.** Grips well and holds everything together, but the
   knit is a spring: it pulls fingers toward its own rest shape and lets Jake's fingers lag the robot's by
   the stretch. Expect to re-tune (likely lower torques on fingers it pulls closed).
3. **XL nitrile.** Thin and doesn't stretch much, but probably won't fit over a human hand plus the robot hand,
   and it's slippery against the printed parts, so fingers slide instead of coupling. Fine as an inner layer
   under straps for grip.
Any glove that adds force changes the balance point, so re-run a record with the glove on and nobody moving:
a finger that drifts needs its torque nudged.

## Replay v2 (2026-10-17, voice-563b984c)
- Jake saw the other fingers shake and strain while replaying an index-only take. The take itself was clean
  (the still servos moved <1.5° sample to sample, with only a slow ~14° drift as the low pull settled), so the
  cause was the replay: every servo got a fresh goal 100 times a second at move torque 700. Same take, measured
  on the hand: old way ring/pinky/thumb-tendon position sd 1.2-1.7°, new way 0.03-0.13°; index current halved.
- Now every take is cleaned first: resampled to 25 Hz, 0.15 s moving average, the first 0.5 s (cords going taut)
  dropped, and any servo that travelled < 20° held still at its median. Replay sends at 25 Hz; moving servos
  get torque 500, still ones 200 (guesses that held fine on the bench; not tuned against a load).
- Two modes. Motion (Play, the default): per servo, turning points that swing back ≥ 25% of its travel (≥ 30°)
  plus pauses ≥ 0.6 s partway through a move; the union becomes key poses, driven between with eased moves whose
  peak stays under the speed cap, resting 0.25 s on each. The index take becomes 3 poses: open, full curl, open.
  Full (long-press Play, or right-click): the cleaned take at its recorded timing.
- Auto-label on save from the same turning points: "Index finger curled in, index finger extended". The thumb's
  three servos read as one thumb, described by whichever moved furthest. Rename (now by voice in the app, or
  `teach.sh rename last <name>`) overrides it.

## Labels in time order, audio, lower pull (2026-10-17, voice-563b984c)
- take-20261017-170553 moved one finger at a time (thumb 0-25 s, then index, middle, ring, pinky) but was labelled
  "Index, middle, pinky, ring and thumb curled in, …": every finger's first move was timed from the take's start
  (its first key point), so they all looked simultaneous. Moves are now timed where they cross halfway, runs of
  one finger read as one phrase, and fingers taking turns at the same thing share one: "Thumb, index, middle, ring
  and pinky each curled and extended". Labels are joined with ", then ". The index take: "Index finger curled and
  extended".
- The "one-sample" thumb abduction jump at 10.7 s isn't one sample: abduction ramps 100 → 0 over 9.2-10 s, sits
  near 0 for 2 s and ramps back by 13 s (no step over 8° between samples anywhere in 0-26 s). It reads like a real
  swing, so nothing filters it; the 0.15 s smoothing already flattens true single-sample spikes below a swing.
- Audio: the app records the default input for the whole take (AVAudioRecorder, AAC mono), transcribes it on the
  device (SFSpeechURLRecognitionRequest) and runs `teach.sh audio <take> <sidecar>`, which keeps
  `take-….m4a` next to the take and stores `audio.offset` (wall-clock gap between mic start and the take's t=0),
  `transcript` and `words` on the take's clock. When there's narration, it becomes the name (the motion label
  stays in `motion`). Replay full prints `audio <file> <seconds in> <rate>` as the first frame goes out and the
  app plays it at 1/stretch (clamped to 0.5-2x).
- Torque `[10, 30, 30, 40, 40, 25, 25]` → `[8, 22, 20, 30, 30, 18, 18]`. Release test with nobody touching: curl
  to 60% in position mode, switch to the pull, read after 3 s. Fingers stayed at exactly 171 of 288 at 1x, 0.75x,
  0.5x and 0.35x, so the springs can't back-drive the spools and a finger rests where it's left; resting 8-15%
  curled after a take is where Jake's hand let go, not the pull. The torque-0 control didn't run (the hand
  dropped off USB).
