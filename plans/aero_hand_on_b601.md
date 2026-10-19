# Aero Hand Open on the reBot Arm B601

**2026-10-17 update: Jake is buying the B601-RS (48 V, 2.5 kg rated), not the
DM.** The integration plan he set is in §A, just below. §0–§7 are the
original 2026-10-16 desk research, written for the B601-DM. Where the RS
changes a number there, §A says so.

Status: desk research only, 2026-10-16. Nothing here has been mounted, wired or
run. Prompted by Jake: "Chestnut Robotics (Tether AI at the time) makes an open
source Aero Hand, we have that. I'm interested in attaching it to the reBot arm
B601. How would that work, would it work well, what payload could it carry,
and what tasks would it do? I'm specifically interested in automated kitchen
food prep."

**Short verdict: yes, it bolts on and it'll move, but it's a ~1 kg-at-the-hand
light-duty setup. It's good for picking and placing produce, opening jars and
lids, light stirring and pouring from small containers, and plating. It's poor
at knife work, heavy pots and anything wet or greasy for long. For real food
prep, plan on a second arm, either with the stock parallel gripper or with a
tool-changer.**

---

## A. Integration plan: Aero Hand (left) on the B601-RS

Jake's six steps, in build order. Under each one: what to buy or write, and
what I checked or still need to confirm. Nothing here has been built yet.

### A1. 3D-printed adapter plate on the wrist flange, in place of the gripper

- A printed plate (PETG or PLA+, ≥ 5 mm thick with ribs) bolts to the J6
  output where the gripper connector would go. Its other face takes the
  Aero's four M3 inserts. Keep the standoff as short as possible, because
  every centimetre adds wrist torque.
- **Open question for Seeed:** the **RS Body Structure Kit is sold "without
  gripper"**, and its published parts list (17 metal parts, 19 prints,
  bearings, screws) doesn't name a wrist plate or end flange
  ([OpenELAB listing](https://openelab.io/products/seeed-studio-rebot-arm-b601-rs-body-structure-kit)).
  Ask Seeed: *"Does the RS structure kit include the J6 output flange or wrist
  plate the gripper bolts to? Can we get its STEP file and bolt pattern?"*
  If it isn't included, we print it too, using the J6 motor's output bolt
  pattern from the RobStride datasheet.
- **RS motor map (confirmed 2026-10-19):** J1–J3 are RobStride RS06; wrist
  J4–J6 and the gripper (motor 7) are RobStride RS00 (Ø57 × 51 mm, 310 g,
  5 / 14 N·m). Output flange 6× M3 on Ø27 PCD. Details and sources in
  `AGENTS.md` → Hardware.
- Get the M3 hole spacing from the Aero Onshape CAD. The docs' mechanical
  page is still a placeholder.
- **Payload on the RS:** 2.5 kg rated, minus ~0.4 kg for the hand and
  ~0.05 kg for the plate and cables, leaves **≈ 2 kg** for the object within
  ~70 % of reach. That's double the DM's ≈ 1 kg (§3). The wrist-torque check
  in §3 assumed a DM4310, so re-run it against the RS's wrist RobStride
  model. Even so, the hand's thermal limit (torque ≤ 500 for long holds)
  doesn't change, and it is now the tighter limit for most kitchen tasks.

### A2. 48 V → 6 V buck converter on the arm, fed from the arm's supply

- The hand needs **6 V, 8 A max, 10 A to be safe**, which is about 60 W. Use a
  48 V-input (≥ 60 V max input) → 6.0 V, **≥ 10 A** step-down module, mounted
  on the forearm or upper arm close to the hand. The servos' EEPROM accepts
  4–10 V (read from our servos 2026-10-17, `third_party/aero_hand/README.md`),
  so 6.0 V leaves plenty of margin.
- Then only the arm's 48 V pair runs along the arm. The 6 V run is just the
  short hop from the converter to the hand, so it can use thin wire. At 48 V,
  the hand draws only about 1.3 A from the arm's supply. **Check that the
  48 V supply we buy has ~60 W of headroom** above what the arm itself uses.
  Seeed doesn't bundle a supply with the RS.
- Add a fuse (~3 A) on the 48 V input to the converter, and a bulk capacitor
  on the 6 V side. A brownout makes the hand **re-home on power-up** (v0.2.0
  firmware), so dips while the arm accelerates would make the hand spasm.
- A non-isolated converter shares ground with the arm. That's fine, because
  the hand's only other connection is USB to the same computer (A3).

### A3. Small USB hub on the arm: the hand's USB plus the arm's USB-CAN

- Use a 4-port USB 2.0 hub, bus-powered or fed with 5 V from a second small
  buck off the 48 V. Zip-tie it at the arm's base or shoulder. Plug in the
  Aero's ESP32 (921600-baud serial) and the arm's USB-CAN adapter. **One USB
  cable goes to the computer.** Both devices are low-bandwidth, so they share
  a USB 2.0 hub without trouble. Keep the run to the computer under ~3 m.
- Put the hub at the base, not the wrist. Only the hand's USB cable and its
  6 V pair then cross the J6 roll joint, so cap J6 to about ±180° in software
  to stop them winding up (§2).
- **Caveat: the computer.** Seeed's RS LeRobot path uses **SocketCAN
  (`can0`)**, which is Linux-only. The plugin's `robstride` adapter option is
  "registered but not yet supported" in its SDK, and the RS config is "still
  being refined"
  ([plugin](https://github.com/Seeed-Projects/lerobot-robot-seeed-b601),
  [wiki](https://wiki.seeedstudio.com/rebot_arm_b601_rs_lerobot/)). Our
  MacBook can't open `can0`. **Plan on a Linux host for the arm** (a Linux
  box, a Pi 5 or a Jetson), or confirm with Seeed that there is a Mac-capable
  serial-bridge adapter for the RS. The hub idea still works with either.

### A4. LeRobot robot class: reBot RS + Aero Hand, two eye-height cameras

- Seeed already ships the arm as a LeRobot plugin
  (`lerobot-robot-seeed-b601`, type `seeed_b601_rs_follower`). Write one new
  plugin, **`aero_b601_rs_follower`**, that **wraps** that class and the Aero
  SDK (`aero_open_sdk`, vendored at `third_party/aero_hand/upstream/sdk`)
  instead of forking them:
  - `connect()` opens Seeed's follower and the Aero serial port, and auto-
    detects the port the same way `teleop.py` does.
  - Observation: 6 arm joints + 7 hand actuator positions (+ hand
    temperature, logged but not given to the policy) + 2 camera images.
  - Action: **13 numbers** (6 arm + 7 hand, in the hand's 0–1 normalized
    units). The gripper channel is dropped. Optionally, a
    `hand_mode=primitives` flag maps a single scalar to open / power / pinch
    / tripod, for the cheap first policies (§6).
  - `send_action()` writes the arm over CAN and the hand over serial in the
    same tick, clamps the hand's torque (≤ 500 for holds, using the existing
    low-power hold logic in `scripts/hold.py`), and releases the hand if any
    servo goes above 60 °C.
- **Cameras: two at eye height, no wrist camera** (the human-mirror principle,
  `hand_1_0.md` and `agent_led_research.md` §7). The same stereo pair is
  pinned on a mast behind the arm at head height, with the keys `left_eye` and
  `right_eye`. A wrist camera would also add a third cable through J6.
- Our hand is a **left** hand (flashed `lefthand` firmware, 2026-10-17). So
  mount the arm as a left arm, to the demonstrator's left, which keeps the
  mirror honest.

### A5. Teleop: the Star Arm 102 drives the arm, the webcam (`teleop.py`) drives the hand

- The Star Arm 102 is Seeed's leader for both the DM and the RS
  ([RobotShop](https://www.robotshop.com/products/star-arm-102-rebot-b601-dmrs-leader-arm),
  $258.90, 420 mm reach, USB-UART on `/dev/ttyUSB*`, needs its own 12 V
  supply). It already has a LeRobot teleoperator (`rebot_arm_102_leader`,
  `lerobot-teleoperator-rebot-arm-102`).
- Write a matching **`aero_b601_leader`** teleoperator that combines the
  Star Arm 102's 6 joints with `teleop.py`'s retargeted 7 hand values. To do
  that, refactor `teleop.py` so the MediaPipe → joint-angle part is an
  importable function and the CLI stays a thin wrapper.
- **The catch: the hand that holds the leader arm can't also make finger
  shapes for the webcam.** Two ways around it:
  1. **(Recommended) Strap on, don't grip.** Swap the leader's gripper handle
     for a printed forearm cuff, so the demonstrator's left forearm moves the
     leader and the fingers stay free. The webcam (a third camera, used only
     for teleop and never seen by the policy) watches that same left hand. One
     human arm drives one robot arm and hand, so the demos look like human
     motion.
  2. Right hand on the leader, left hand in front of the webcam. It works
     with no new hardware, but the arm and the fingers come from different
     human arms, and coordinated grasps are harder to demonstrate.
- Smooth the webcam signal, as `teleop.py` already does (EMA 0.7), and hold
  the last value when tracking drops, so the hand doesn't fall open mid-grasp.

### A6. Record demonstrations into LeRobot datasets, then train

- Record with the stock `lerobot-record`, now taking the two new types:
  ```
  lerobot-record --robot.type=aero_b601_rs_follower --robot.port=can0 \
    --robot.cameras='{left_eye: {...}, right_eye: {...}}' \
    --teleop.type=aero_b601_leader --teleop.port=/dev/ttyUSB0 \
    --dataset.repo_id=helpinghands/aero_b601_<task> \
    --dataset.single_task="Pick the tomato into the bowl" \
    --dataset.push_to_hub=false
  ```
- First task, unchanged from §7: **pick a vegetable into a bowl**, gloved,
  ~50 demos, ACT on one GPU. After that: SmolVLA / pi0.5, then GR00T N1.7 on
  a rented GPU at ~200 demos per task for full finger control (§6).
- Score it with the same agent-led loop as the SO-101 work
  (`agent_led_research.md`): the same judge camera, fixed start states and
  ledger.

### Shopping and questions list

| Item | Status |
|---|---|
| B601-RS (+ 48 V supply, sized for arm + ~60 W) | Jake buying |
| Star Arm 102 leader + its 12 V supply | buy |
| 48 → 6 V ≥ 10 A buck, fuse, capacitor | buy (~$20) |
| 4-port USB 2.0 hub | buy (~$10) |
| Adapter plate, forearm cuff | print |
| Linux host for SocketCAN, or Seeed's Mac answer | **confirm** |
| Does the RS structure kit include the wrist plate / J6 flange (+ STEP)? | **ask Seeed** |
| Aero M3 hole spacing | pull from Onshape |

---

## 0. Two corrections to the brief

1. **The 2.5 kg payload belongs to the other model.** Seeed's README lists
   **B601-DM: 1.5 kg** and **B601-RS: 2.5 kg** (the RS uses Robstride motors and
   runs on 48 V, and weighs 6.7 kg instead of 4.5 kg).
   [README](https://github.com/Seeed-Projects/reBot-DevArm/blob/main/README.md)
2. **The linked page is the Body Motor Kit, not the assembled arm.** It holds six
   Damiao motors and no structure or gripper, and lists at $994.80 today
   ([Seeed](https://www.seeedstudio.com/reBot-Arm-B601-DM-Body-Motor-Kit-p-6752.html)).
   At pre-order, CNX listed the assembled arm with gripper at $1,499 and the
   full DIY bundle at $1,197
   ([CNX](https://www.cnx-software.com/2026/04/17/rebot-arm-b601-dm-an-open-source-61-dof-robotic-arm-for-embodied-ai-and-teleoperation-applications/)).
   I couldn't confirm a current Seeed price for the assembled arm. Resellers
   vary (Pakronics lists A$3,204). Treat ~US$1,899 as unconfirmed.

## 1. Spec sheet, both halves

| | reBot B601-DM | Aero Hand Open |
|---|---|---|
| DoF | 6 + 1 (gripper) | 7 actuators driving 16 joints by tendon; 3 of the actuators are in the thumb |
| Payload / force | **1.5 kg, without the gripper, within 70 % of reach** | ~10–12 N per fingertip; no rated payload ([docs](https://docs.tetheria.ai/docs/mechanical_overview), [site](https://chestnut-robotics.github.io/aero-hand-open/)) |
| Reach | 767 mm with gripper, 607 mm without | hand is 198 × 95 × 53.5 mm |
| Mass | ≈ 4.5 kg | **< 400 g** (third-party listings say 375–450 g) |
| Motors | 4× DM-J4310 + 3× DM-J4340P; wrist joints ~7 N·m peak per CNX | 7 serial-bus servos, stall current 1.3–1.5 A each |
| Power | 24 V DC (a 4.5 A adapter, sold separately) | **6 V DC, 10 A regulated** supply; whole hand 8 A max ([setup](https://docs.tetheria.ai/docs/hardware_setup)) |
| Bus | CAN through a USB-CAN board; MIT/speed/position modes | USB serial to an ESP32-S3 at 921600 baud ([GUI](https://docs.tetheria.ai/docs/GUI)) |
| Software | ROS1/2, **LeRobot (done)**, Pinocchio, Isaac Sim, Python SDK "Motorbridge", PICO 4 VR teleop | ROS 2 Humble packages, webcam (MediaPipe) and Manus-glove teleop, RL deploy node ([ROS2](https://docs.tetheria.ai/docs/ros2)); **no LeRobot driver** |
| Mount | Stock gripper attaches through "Gripper Connector A/B" CNC parts (STEP files in the repo) | "Flat wrist pad with four M3 threaded inserts"; hole spacing is in the Onshape CAD |
| License | HW CERN-OHL-W-2.0, SW Apache-2.0 | software permissive; hardware files reportedly non-commercial (unverified) |

## 2. Would it work?

**Mechanically: yes, with one printed or machined adapter.** Remove the gripper
assembly (its rail, rack and the 7th Damiao 4310) and design a plate that bolts
to the joint-6 output where Gripper Connector A/B currently attach, with the
Aero Hand's four M3 inserts on the other face. Both sides have open CAD
([reBot hardware BOM](https://github.com/Seeed-Projects/reBot-DevArm/blob/main/hardware/reBot_B601_DM/readme.md),
Aero Onshape), so this is an afternoon in CAD followed by one print. Keep the
plate short. Every centimetre of standoff adds wrist torque (§3).

**Wiring: two new runs along the arm.**
- *Power:* the hand wants 6 V at up to 8–10 A, and the arm only carries 24 V.
  Two options. (a) Run a 6 V pair from a supply at the base (thick wire
  because of the current, about 18 AWG for roughly 1 m). (b) Put a 24 V → 6 V,
  ≥10 A buck converter on the forearm and tap the arm's 24 V. Option (b) is
  neater, but the arm's 4.5 A adapter then has to carry both, so it would need
  upsizing. **I recommend (a) for the first try:** it's simplest and keeps the
  supplies separate.
- *Data:* one USB cable to the hand's ESP32. USB is fine at about 2 m. Use a
  flexible cable and leave a service loop at the wrist.
- *Wrist roll:* both new cables twist with joint 6, so cap J6's range in
  software (e.g. ±180°) to stop it winding them up.

**Control: two buses, one new LeRobot robot class.** The arm runs over
CAN/Motorbridge and the hand over USB serial. Neither vendor ships a combined
driver, and the hand has no LeRobot integration at all. The work is a LeRobot
`Robot` subclass that:
- opens both buses;
- exposes a **13-D state and action** (6 arm joints + 7 hand actuators, in the
  0–1 normalized hand units); and
- substitutes the hand for the gripper channel.

The hand's protocol is simple: 14-byte position frames, plus telemetry for
position, velocity, current and temperature. Expect about a day of work to write
the class and debug it. In ROS 2 the shortcut is to run both vendors' nodes side
by side, but our pipeline is LeRobot, so go that way.

**Teleop for collecting data is the real integration problem.** The B601's
leader arm can't drive 7 finger actuators. The most practical rig: Seeed's
leader arm or the PICO 4 VR setup for the arm, plus the Aero's **webcam
MediaPipe retargeting** for the fingers (we have a webcam already; Manus gloves
are the expensive upgrade). Doing both with one human at once is awkward, which
is the classic dexterous-teleop bottleneck. A useful middle ground is to start
with the hand running a few **fixed grasp primitives** (open, power grasp,
pinch, tripod), driven by one scalar, so the policy treats it like a smarter
gripper.

## 3. Usable payload at the hand

**Arm budget:** the 1.5 kg rating excludes the gripper and assumes ≤ 70 % of
reach.

```
  1.5  kg  rated
− 0.40 kg  Aero Hand
− ~0.05 kg adapter plate + cable share at the wrist
≈ 1.0  kg  object, held within ~70 % of reach (~0.5 m from the base)
```

The stock gripper (a Damiao 4310 at ~300 g plus a rail, rack and CNC parts) is
probably at least as heavy as the hand. **Swapping to the hand most likely costs
no payload compared with the stock setup.** That's an estimate, because Seeed
doesn't publish the gripper's mass.

**Wrist torque is the tighter limit when the hand is held out horizontally.**
Rough lever arms: object about 0.2–0.25 m from the wrist pitch axis, hand
centre of mass about 0.1 m. For a 1 kg object that's ≈ 9.8 × 0.23 + 0.4 × 9.8
× 0.1 ≈ **2.6 N·m**, which is close to the 4310's continuous rating
(3–3.5 N·m depending on revision). Lifting 1 kg with the wrist level is at
the limit. Keeping the wrist pointing down (hand vertical) is comfortable.
**A realistic working load is 0.5–0.8 kg for sustained handling, with 1 kg
for short lifts.**

**The hand's own grip is the third limit, and it's thermal, not force.**
- Force: ~10–12 N per fingertip. A thumb–index pinch with silicone pads
  (μ≈0.5–0.8) holds roughly 1–2 kg. An enveloping power grasp holds more, and
  the demo shows it lifting a ~18 kg water jug (that's a hang test, not a
  rating). **For anything the arm can lift, the grip is not the bottleneck.**
- Heat: the docs say that at a continuous stall the servos reach 80 °C in
  **~20 s at torque 1000, ~2 min at the default 700, and >10 min at 500**.
  At 80 °C they stop accepting commands and the hand may spring open
  ([hardware FAQ](https://docs.tetheria.ai/docs/hardware_faq)). **Any task
  that clamps something for minutes (holding a knife, a pot handle, a bowl
  while stirring) needs torque ≤ 500 and duty-cycling.** That's the
  most kitchen-relevant number in this whole doc.

## 4. Kitchen food prep: good, bad, and what needs a second arm

| Task | Fit | Why |
|---|---|---|
| Pick produce (tomato, onion, pepper, apple, bunch of herbs) | **Good** | Backdrivable tendon fingers conform to irregular shapes; ≤ 0.5 kg each. Being compliant is a bonus with soft fruit. |
| Plating / placing portions, garnishing | **Good** | Light, precision pinch. Better than a parallel jaw for herbs and irregular pieces. |
| Opening containers: jar lids, deli tubs, soda can | **Good, but needs two hands** | The hand can twist a lid and open a can (demoed), but something has to hold the jar. Pair it with a fixture or a second arm. |
| Pouring from a cup, small jug, measuring cup | **OK** | Fine up to ~0.5 kg full. A full 2 L jug or a pot is over budget. |
| Stirring a pot | **OK, short bursts** | The spoon is light, but stirring is a sustained grip, so torque ≤ 500 and stopping regularly. Also note the steam (§5). |
| Holding a knife and cutting | **Poor** | Sustained high grip (thermal limit). The fingers flex, so the blade twists, and the arm's 1.5 kg / 7 N·m wrist can't push through a carrot or squash. Also a safety issue. Use a **fixed knife end effector or a powered slicer** instead of a hand holding a knife. |
| Holding produce steady for a cut | **Needs a second arm** | One arm holds, the other cuts. That's two arms, not one hand. |
| Peeling, cracking eggs | **Hard, but plausible later** | Needs bimanual coordination and a lot of demonstrations. A fun stretch goal, not a first task. |
| Moving pots, pans, full mixing bowls | **No** | Over the 1–1.5 kg budget. |
| Anything wet, oily, hot | **No (as-is)** | See §5. |

**Second-arm or end-effector conclusions:**
- **Cutting:** a dedicated, rigidly mounted knife or slicer, not the hand.
- **Holding a container while the hand works:** a second B601 with its stock
  parallel gripper. That's cheaper and stronger than a second hand, and the
  gripper is good at holding a jar or bowl still.
- **Heavier loads (pot, bowl, jug):** the B601-RS (2.5 kg) or a bigger arm.

## 5. Kitchen-specific risks the spec sheet doesn't cover

- **Food safety.** The hand is 3D-printed PLA with exposed tendons and pulleys.
  You can't wash it, and it isn't food-contact safe. **It needs a glove**: a
  nitrile or food-service glove over the hand, or a fitted silicone sleeve. A
  glove will change how grasping works and will add friction to the tendons.
  Collect training data with the glove on.
- **Heat and steam.** PLA softens around 55–60 °C. Keep it away from steam
  over a boiling pot and from hot pan handles.
- **Water and grease.** The servos and the ESP32 board aren't sealed.
- **Tendon derailment.** The docs have an FAQ entry on cables slipping off
  pulleys. Expect occasional maintenance.

## 6. Which open models can drive arm + hand, and how much data

None of the open VLA checkpoints know this exact combination (B601 + Aero,
13-D actions). **Every option means fine-tuning on our own demonstrations.**
What differs between them is how cleanly they take a 13-D action.

| Model | Takes a dexterous hand? | Notes |
|---|---|---|
| **GR00T N1.6 / N1.7** (NVIDIA) | **Yes, best fit.** It was built for humanoids with dexterous hands and has a `NEW_EMBODIMENT` tag for custom robots. | There's already a write-up of **GR00T N1.7 on the reBot B601** (with the stock gripper, Jetson Thor, ~100 demos suggested for simple pick-and-place) ([AVerMedia](https://developer.avermedia.com/blog/groot-on-rebot-b601/)). The closest dexterous reference is a G1 + BrainCo-hand fine-tune: **1,598 episodes across 8 pick tasks, ≈200/task** ([HF](https://huggingface.co/JeffrinSam/GR00T-N1.7-G1-BrainCo-Pick)). Fine-tuning needs >48 GB VRAM per Seeed's wiki, which means a rented GPU. |
| **π0 / π0.5** (openpi, also in LeRobot) | **Yes.** Actions are padded to 32-D, so 13-D fits. | We'd write a custom data-transform config. I found no public dexterous-hand π0.5 example. |
| **MolmoAct2** (our current north star, [molmoact2_deployment.md](molmoact2_deployment.md)) | **Not out of the box.** Its checkpoints are SO-100/101 and Franka, both with grippers. | A 13-D action head means fine-tuning a new embodiment, which the docs don't cover. Most effort and least certain. |
| **SmolVLA / ACT / Diffusion Policy** (LeRobot) | **Yes**, any action width. | The cheap baselines. ACT trains on one consumer GPU, so it's the fastest way to prove the rig works before spending on GR00T. |

**Data estimate:**
- Simple pick-and-place with the hand in **2–4 grasp primitives**:
  **~50–100 demos per task**, about the same as a gripper.
- Full **7-actuator finger control**: **~200 demos per task** (the G1 +
  BrainCo data point), more for in-hand manipulation such as lid twisting.
- Rule of thumb: dexterity multiplies the data you need by 2–4×. That's why
  the grasp-primitive shortcut in §2 is worth starting with.

## 7. Recommendation

1. **Do it, as a light-duty "produce and plating" station, not a chef.**
   First milestone: *pick a vegetable off the counter and place it in a bowl*,
   with the hand in a gloved power grasp, ACT policy, ~50 demos.
2. Build order: adapter plate → separate 6 V supply + USB run → LeRobot
   `Robot` class with a 13-D action (or 7-D with a grasp-primitive scalar) →
   webcam finger teleop → ACT baseline → GR00T fine-tune on a rented GPU.
3. Before buying: confirm the current assembled B601-DM price and the stock
   gripper's mass with Seeed, and pull the Aero's M3 hole spacing from Onshape
   for the adapter.
4. For real food prep (cutting, holding while working), budget for **a second
   B601 with its stock gripper** and a **fixed knife or slicer**, rather than
   asking one hand to do everything.

**Not verified:** Seeed's current assembled price; the stock gripper's mass;
whether the 1.5 kg rating holds with the wrist horizontal; the Aero hardware
license terms (one listing says non-commercial); and every data estimate
(these are extrapolated, not measured on this rig).
