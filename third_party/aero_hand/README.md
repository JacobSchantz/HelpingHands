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
  the Mac mic tracks tempo, beat and loudness, and the hand cycles wave / bounce / pinch walk / pose hits every
  8 bars, smoothed and speed-limited, until the track ends. Shrinks above 50 °C, stops at 60 °C. `--dry-run`
  just listens and prints; `--routine` plays the old fixed routine. Needs Microphone access for the terminal.
- `scripts/pose.sh <name>` – jumps straight to a named pose: open, fist, peace, flip off, rock on,
  shaka ("surf's up"), i love you, love, 666, and Chinese one-hand numbers one..ten (`pose.sh seven`).
  `pose.sh count to ten` counts 1..10, about a second on each. `--list` shows aliases; add a pose with one
  line in `POSES` in `pose.py`.
- `scripts/teleop.sh` – webcam teleop: the hand copies your hand live (Esc quits, `--dry-run` only shows
  tracking, `--camera N`). Needs `pip install mediapipe opencv-python` in the venv; the model downloads to
  `~/HelpingHands-tools/aero/hand_landmarker.task` on first run. Port of upstream's ROS 2 webcam teleop
  (`ros2/src/webcam_mocap` + `mediapipe_retargeting.py`) without ROS; upstream also has Vision Pro and Manus
  glove teleop under `ros2/`.

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
