# Aero Hand Open on the reBot Arm B601-DM

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
