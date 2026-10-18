# Aero Hand Open (TetherIA / Chestnut Robotics) – vendored firmware, SDK and bring-up tools

Docs: https://docs.tetheria.ai · Upstream: https://github.com/chestnut-robotics/aero-hand-open
(commit `7bb2f23485a7d440960c21046da642de132b7745`, 2026-09-15). `upstream/` is an unmodified
copy of that repo's `firmware/` and `sdk/` folders (Apache-2.0, see `upstream/LICENSE.md`).

## Tooling (not in git)
```
python3 -m venv ~/HelpingHands-tools/aero/venv
~/HelpingHands-tools/aero/venv/bin/pip install third_party/aero_hand/upstream/sdk   # aero-open-sdk 0.1.0.dev1 + esptool 5.6.0
~/HelpingHands-tools/aero/venv/bin/pip install platformio                          # only for tools/bus_diag
```
`aero-open-gui` is the GUI (needs Tk). Factory Seeed flash backup (8 MB, full chip):
`~/HelpingHands-tools/aero/backup/seeed_factory_full.bin` (restore: `esptool write-flash 0 <file>`).

## Flashing (documented method: app image at 0x10000, 921600 baud)
```
V=~/HelpingHands-tools/aero/venv/bin
$V/python -m esptool --chip auto -p /dev/cu.usbmodem101 -b 921600 --after no-reset \
  write-flash 0x10000 third_party/aero_hand/upstream/firmware/main/bin/firmware_v0.2.0_righthand.bin
$V/python third_party/aero_hand/scripts/capture.py 3 --reset    # expect "[BOOT] Hand Type: RIGHT_HAND"
```
`--after no-reset` + `capture.py --reset` gives a USB/JTAG reset, which the firmware treats as a
*non-power* reset and **skips homing**. A real power-on (USB plug-in) or brownout **auto-homes**
in v0.2.0 (`firmware.ino` `setup()`).

## Moving the hand
- `scripts/performance.sh [song]` – starts a song (random from the ¿? playlist), then the hand dances to it:
  the Mac mic tracks tempo, beat, loudness, brightness, busy highs and hard lows, and at each bar line the hand
  picks the move that fits (quiet → slow sway, loud with heavy kicks → pose hits, busy hats → flutter, kicks →
  bounce, bright → pinch walk, else wave), while each finger also flicks with hits in its own band (index highs,
  middle/ring mids, pinky lows). Smoothed, speed-limited, half time when a beat is too quick for the 50% cap.
  Shrinks above 50 °C, stops at 60 °C. `--dry-run` just listens and prints; `--wav song.wav` dances to a file
  offline and prints the moves; `--routine` plays the old fixed routine. Needs Microphone access (Helping Hands
  or the terminal); it prints MICROPHONE IS SILENT if macOS is blocking it.
- `scripts/pose.sh <name> [--hold auto|medium|firm]` – jumps straight to a named pose: open, fist, peace,
  flip off, rock on ("i love you"), 666 ("shaka", "surf's up"), thumbs up ("good job"). Chinese one-hand numbers one..ten are in
  `NUMBERS` for `pose.sh count to ten` (about a second on each; `pose.sh seven` still works) and have no
  buttons. `--list` shows the button poses and aliases; add one with a line in `POSES` in `pose.py`.
- **Low-power holding** (`scripts/hold.py`, used by `pose.py` and `grip.py`, so the app's pose buttons too):
  the servos have no brake, so a held pose costs current for as long as it's held. After a pose is reached
  each servo is told to hold where it actually settled (a finger that stopped short of its target, e.g. on
  the palm, otherwise pushes at its full torque limit forever), then its torque limit (SET_TOR) steps down
  450 → 10 until it sags more than 2°; it keeps 1.5× the lowest level that held (floor 30). This takes about
  4 s after the pose and you barely see it. The next move raises every servo back to 700 (firmware default).
  In `grip.py` a finger stalled on the object keeps half the grip torque instead, so the object isn't let
  go (not yet tried with a real can). Speed stays 50%.
  **Hold modes** (`AERO_HOLD`, `--hold` on pose.py/grip.py, the app's Hold menu): `auto` is the search
  above (default); `medium` keeps every servo at torque 350 (light objects); `firm` at 1000 (tools like a
  hammer, hottest; grip.py also closes at 1000). Both push on toward the target, so a finger on the palm
  draws current the whole time. Neither has been measured on a held object yet.
- `scripts/teleop.sh` – webcam teleop: the hand copies your hand live (Esc quits, `--dry-run` only shows
  tracking, `--camera N`). Needs `pip install mediapipe opencv-python` in the venv; the model downloads to
  `~/HelpingHands-tools/aero/hand_landmarker.task` on first run. Port of upstream's ROS 2 webcam teleop
  (`ros2/src/webcam_mocap` + `mediapipe_retargeting.py`) without ROS; upstream also has Vision Pro and Manus
  glove teleop under `ros2/`.

- `scripts/teach.sh record` – teach by moving the hand: transparent torque mode (a small per-servo pull, `TORQUE`
  in `teach.py`, `--torque` to override) while all 7 actuations are logged at 100 Hz until Stop; the hand then
  relaxes and the take is saved to `~/HelpingHands-tools/aero/takes/take-<time>.json`, auto-named from its motion
  in time order ("Thumb, index, middle, ring and pinky each curled and extended"; `teach.sh label [file|last]`
  prints it). Recording from the app also records the mic: the take gets `take-<time>.m4a`, a transcript (which
  names the take when Jake narrates) and plays the audio during Replay full (`teach.sh audio` attaches it). `teach.sh replay
  [file|last]` smooths the take, holds thumb abduction/flexion under 5° and tendon actuators under 20° still, and drives between its key poses
  (simplified simultaneous samples, preserving finger order and pauses) as smooth moves at the speed setting;
  `--full` plays the recorded timing instead. Compression retains the observed coordination: a finger
  waiting its turn stays still instead of interpolating toward its eventual peak from the take's start.
  New takes also save timestamped motor currents at at most 10 Hz, separately from the nominal
  100 Hz position samples. Missing current reads are omitted; signed values are in mA. Motor current
  is diagnostic telemetry, **not calibrated fingertip force**. Recording's low torque settings keep
  tendons taut; they do not encode the pressure a person applied while demonstrating a grasp.
  Existing position-only takes still replay. Replaying a grasp posture reproduces its positions;
  it does not reproduce contact pressure or keep holding after a recorded release.
  Motion mode uses a continuous-velocity, monotone cubic path with no artificial stop at each key pose.
  Both that path and the initial glide respect the configured speed cap and an acceleration cap
  equivalent to taking at least 0.5 seconds to reach that speed. Replay may take longer to meet those bounds.
  Both send at 25 Hz with moving servos at torque 500 and still ones at 200, hold the last pose low-power, and stop
  and relax at 60 °C. `replay --dry-run` prints the key poses.
  Record and replay now capture the camera automatically (including replay's initial glide and final hold).
  Agents can call `scripts/teach.sh replay take-20261017-170553.json --camera 0` (or `last`);
  `--full` keeps recorded timing. `--dry-run` opens neither camera nor hand; `--no-video` explicitly
  disables capture. `--camera N` or `AERO_CAMERA=N` selects the OpenCV camera (default 0).
  Capture requests 1280×720 at 30 fps to reduce camera transport load; the actual frame size and
  reported device rate are logged in the result. Override with `AERO_CAMERA_WIDTH`,
  `AERO_CAMERA_HEIGHT`, and `AERO_CAMERA_FPS` when diagnosing a device. A USB stream loss
  still aborts motion; the recorder does not silently reconnect or switch cameras mid-replay.
  Video requires the existing `opencv-python` dependency and camera permission for the calling app.
  Each invocation saves a unique MP4 and JSON result under `~/HelpingHands-tools/aero/takes/videos/`
  (`--video-dir DIR` overrides). The final `capture_result` JSON line gives absolute artifact paths,
  source take, action and completed/failed status; the sidecar also contains wall-clock start time and
  actual frame timestamps (MP4 plays at 25 fps, so consult timestamps if the camera runs slower).
  Camera startup must succeed before connecting to the hand; camera loss during replay aborts and relaxes
  it. A missing camera frame is retried for up to one second. During teaching, a capture failure
  saves the collected motion as an interrupted take before reporting failure; startup failure saves
  no take because the hand has not connected. The app displays capture failures above the take list.
  Interrupted replays retain partial video and report failure. Videos have no audio track; existing
  app take audio remains separate. Replay videos do not overwrite the original teaching take.
  Every replay also gets a durable run under `takes/runs/<take-stem>/`, including runs without video
  and failures before the hand connects. Its JSON manifest links the source take (with SHA-256),
  camera result, video, status/error, and a `.hand.jsonl` stream. That stream distinguishes planned
  targets, submitted actuator/joint commands, and measured encoder positions; commands are not
  proof of achieved motion. Additional encoder polls run at at most 5 Hz; existing hold reads
  are logged too. Timestamps use seconds since the manifest's wall-clock start. Partial logs
  remain on interruption, and each run has a unique ID. The original take is never rewritten.
  `teach.sh list` includes `replay_runs` for the app item's History button, with links to video and
  data. Older camera-only captures and source-recording videos appear with their actual evidence
  type; no hand measurements are invented for old runs. New record captures are indexed even
  when using a custom video directory. The CLI emits `replay_result` after the camera finalizes.
  `teach.sh list` prints one JSON line per take (the app's Recordings list), `rename <file|last> <name>` names one, and
  `delete <file>` moves it to `takes/deleted`. While recording it prints `pos` lines (each servo 0–100% of its
  range) that the app draws as live bars.
  Plan and glove notes: `plans/aero-hand-glove-teaching.md`.
- `scripts/home.sh` – firmware homing on all seven servos (port auto-detected).
- **Helping Hands Mac app** (⇧⌘H, or Workshop › Aero Hand controls) – every command above as a button, with
  a Speed dropdown (25/50/60/80/100%, back to 50% each launch, applies to every command), a Hold dropdown
  (Auto/Medium/Firm, back to Auto each launch), Relax (zero torque) as the last Poses button, and a Stop
  button (Esc). The app runs these
  scripts as its children, so camera, mic and Music permissions belong to Helping Hands, not Terminal.
  `scripts/app.sh dance|test|pose <name>|count|teleop|record|replay|home|relax|stop|speed <pct>|hold <mode>` presses the same
  buttons from a shell or the voice session (it opens `helpinghands://aero/<command>/<arg>`). The app
  looks for scripts in `~/HelpingHands/third_party/aero_hand/scripts`
  (`defaults write com.helpinghands.app aeroScriptsDir <path>` to move it).

## Testing the board
- `scripts/setid_check.py PORT ID LIMIT` – documented Set ID flow via the SDK. Scans IDs 0–253
  at 1 Mbps; `Old_id: 255` = no servo answered (nothing is written in that case). If a servo
  answers it **writes** its ID and current limit (GUI default 1023).
- `scripts/aero_probe.py PORT` – boot log plus GET_POS/CURR/TEMP/VEL. With fewer than 7 servos
  these are always 0: the firmware's SyncRead task gives up when any of IDs 0–6 is missing.
- `tools/bus_diag/` – read-only PlatformIO sketch (`pio run`, then flash `.pio/build/*/firmware.bin`
  at 0x10000). It checks the XIAO pin joints against the board's pull-ups, pings at 8 baud rates,
  reads EEPROM/telemetry (voltage, temperature) every second. It never writes to a servo.
  Reflash the official .bin afterwards.
- `scripts/pcbnets.py <file.kicad_pcb>` – per-pad netlist from the upstream KiCad PCB.

Board nets (left and right PCBs are the same): XIAO pad 2 GPIO2/D1 = RX from bus (U2 LVC1G125,
R5 10k pull-up, TP2), pad 3 GPIO3/D2 = TX (U1 LVC1G126, R4 10k pull-up, R6/Q1 auto-direction,
TP1), pad 12 3V3, pad 13 GND. The XIAO 5V pad is unconnected and servo V+ comes only from the XT30.

## Bring-up log 2026-10-16 (board with Jake's hand-soldered XIAO, one HLS servo, 6 V on)
- Flashed v0.2.0 right-hand firmware. It boots, skips homing, and answers every opcode.
- Set ID scan: `{'Old_id': 255, 'New_id': 1, 'Current_limit': 0}`, so no servo answered.
- bus_diag: GPIO3 reads HIGH (3148 mV) through R4, so **pad 3 and pad 12 (3V3) are good**.
  GPIO2 reads whatever its own internal pull is set to (pull-up HIGH, pull-down LOW), even with
  U2 tri-stated and R5 10k to 3V3. **Pad 2 (GPIO2/D1) has no connection to the board:** open
  or cold joint. The servo was silent at every baud rate from 38.4k to 1M.
- Action: reflow XIAO pad 2 (D1, second pin from the USB end on the D0–D6 side), then rerun
  `setid_check.py` or bus_diag. Pad 13 (GND) and the 6 V path can't be checked until RX works.
- Round 2 (after Jake reflowed pad 2 and plugged in the 6 V supply): all pin tests HIGH, so
  **pad 2 is fixed**. The servo answered at 1 Mbps: id=1, fw 3.43, model 2570, 6.3 V, 28 °C,
  pos 3114. That proves RX, TX, GND, 3V3 and the 6 V path. Official v0.2.0 restored.
- Servo IDs set 2026-10-16 with `setid_check.py PORT <id> 1023`, one servo at a time. All seven came
  from the factory as ID 1. Now 0 thumb_abduction, 1 thumb_flex, 2 thumb_tendon, 3 index, 4 middle,
  5 ring, 6 pinky, each with current limit 1023 (the docs' recommendation). Jake's labels match the IDs.

## Hand side (2026-10-16)

We are building the **LEFT** hand. The board currently has the right-hand v0.2.0 firmware; flash `upstream/firmware/main/bin/firmware_v0.2.0_lefthand.bin` before the first powered move. ID map is the same on both hands: 0 thumb abduction, 1 thumb flex, 2 thumb tendon, 3 index, 4 middle, 5 ring, 6 pinky.

2026-10-17: flashed firmware_v0.2.0_lefthand.bin (port /dev/cu.usbmodem2101), no reset yet — next boot homes all 7 servos.

2026-10-17 servo EEPROM limits (bus_diag readAllLimits, read-only), all 7 servos: maxTemp 80 C, maxV 10.0 V, minV 4.0 V, protection current 1023. Left-hand firmware restored afterwards.

2026-10-17 holding baseline (Jake gripping the hand while it held a pose, full torque): currents ~2000-2400 on thumb flex, ring, pinky; ring/pinky at 63-65 C and rising ~1 C per 3 s. Relaxed afterwards.

## Holding power benchmark (2026-10-17)

`scripts/hold_bench.py <label>` relaxes the hand, waits until every servo is ≤ 50 °C, runs the real
command (`pose.py fist`, `pose.py peace`, `grip.py close` = can grip), then logs current and temperature
for 60 s in free air. Raw data: `bench/hold_baseline.json`, `bench/hold_lowpower.json`. Heat safety: any
servo at 68 °C relaxes everything and aborts that pose; nothing starts above 54 °C. Baseline was taken
at move torque 700 (the firmware boot default) on every servo.

Total mean current over the 60 s hold (sum of all 7 servos) and the hottest finger's temperature rise:

| pose  | before (mA) | after (mA) | saved | ring / pinky before | ring / pinky after |
|-------|------------:|-----------:|------:|--------------------:|-------------------:|
| fist  | 12124 | 3068 | 75% | +13 / +13 °C/min (to 62 / 64 °C) | +0 / +0 °C/min |
| peace |  8877 | 2212 | 75% | +12 / +14 °C/min (to 61 / 64 °C) | +0 / +0 °C/min |
| can   |  5938 | 1798 | 70% |  +3 / +3 °C/min | −1 / +0 °C/min |

Per servo, fist: thumb flex 2301 → 967 mA, index/middle/ring/pinky ~2060 → 340-490 mA each. Before, the
curled fingers sat at their torque limit (~3 mA per torque unit), i.e. stalled short of 90°. The thumb flex
is now the biggest draw (~960 mA at torque 150; it sags at 75), so it's the next thing to look at.
