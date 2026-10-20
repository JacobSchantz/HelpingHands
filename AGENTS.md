# HelpingHands agent conventions

## Part design versions

Each part has its own simple counter: **Arm N** (the robot arm, imported CAD), **Mount N** (the wrist mounting plate:
hub on the arm's last joint plus a tool plate per end effector), **Aero Hand N** (the Aero Hand as its own end effector),
**Gripper N** (fingers), **Handle N** (strap-loop handles), **Base N** (base/drive assembly: common base the handles plug
into, single motor underneath, gear linkage to the handles). The old dotted "1.x / 2.x / 3.x" names (and the older
"Gen N") are retired; use the new names in pebbles, `VERSIONS.txt`, the catalog and the live preview.

- Every part has its own counter. A change bumps only that part's number (next Gripper after 21 is Gripper 22,
  independent of Arm/Mount/Handle/Base/Aero Hand).
- An assembly is just a selection of part versions (e.g. Arm 1 + Mount 1 + Base 10 + Gripper 21 + Handle 6). It is never
  a version itself; never bump one part to record a change in another, and never name a combined version.
- Each time Jake asks for a design change, make a new version of the part that changed instead of editing it in place.
- A new version builds on the **newest** version of that part (re-check `git pull` / `VERSIONS.txt` right before you
  copy: a parallel pebble may have landed one while you worked) unless the pebble names another base. Its `VERSIONS.txt`
  entry must start by stating what it builds on (`Base 13 (voice-…): Base 11 …`), and the preview picker shows it
  ("Base 13 (from Base 11, …)"). Base 13 builds on Base 11, not Base 12, because both were in flight at once.
- Parts meet through shared interfaces (arm flange to Mount, Mount tool plate to Base or Aero Hand, Handle to Base) so
  any version of one fits any version of its neighbor where possible; the live preview flags incompatible combos.
- Any Handle must fit any Base through the shared handle–base interface.
- Each part is published separately; the live preview has one version picker per part and assembles the selection.
- A `VERSIONS.txt` entry that combines parts names the others it carries (e.g. `Base 3 (voice-…), Gripper 21, Handle 6:`).
  The publisher copies these to the catalog so the live preview's pickers select each part independently.
- Arm, Mount and Aero Hand ride inside a Base folder: its heading names them (`Base 13 (…), Gripper 21, Arm 1, Mount 1, Aero Hand 1:`)
  and the publisher splits those parts out as their own catalog designs. Start each entry's text after the `:` with what it
  builds on (`Base 12 (…), Gripper 21: Base 11 on the STS3215 only, …`): the picker shows it as "Base 12 (from Base 11, on the
  STS3215 only)".
- Existing `versions/vNNN_*` folders still carry the old numbering; renaming them is pebble work (keep history intact).

| Old name | New name | Folder |
| --- | --- | --- |
| Gen N / 1.N (1–20) | Gripper N | `v001`–`v020_*` |
| 1.21 (fingers in 2.6, 3.1–3.3) | Gripper 21 | carried in `v206_*` |
| 2.1 | Handle 1 | `v201_generalist_strap_loops` |
| 2.2 | Handle 2 | `v202_generalist_flush_loops` |
| 2.3 | Handle 3 | `v203_generalist_tongue_pocket` |
| 2.4 | Handle 4 | `v204_generalist_parametric` |
| 2.5 | Handle 5 | `v205_generalist_spanning_handle` |
| 2.6 | Handle 6 | `v206_generalist_single_step` |
| 3.1 | Base 1 | `v301_generalist_base` |
| 3.2 | Base 2 | `v302_generalist_simple` |
| 3.3 | Base 3 | `v303_generalist_inplane` |
| reBot B601-RS import (voice-3cd78d20) | Arm 1 | `cad/arm/rebot_b601_rs/` |
| reBot wrist mount: J6 hub + tool plates, first in Base 10 (voice-3cd78d20) | Mount 1 | carried in `v310_generalist_arm_mount` |
| Aero Hand (left), first posed in Base 13 (voice-c0e340c7) | Aero Hand 1 | `third_party/aero_hand/` |

- **From Handle 4 (old 2.4) on, a version is its `params.json`.** `v204_generalist_parametric` names every dimension there (finger outline,
  solid, handles, tongue/pocket). To make the next version, copy the latest parametric folder, change values in `params.json`
  only, run `python3 export_models.py && python3 genus.py && python3 check_geometry.py`, and add it to
  `Scripts/publish_designs.py` (generations) and `cad/mobile_gallery/poses.js` (pivot: `ECHO: pivot` from
  `part="viewer_right"`). Add a new parameter to `params.json` (with its doc and slider range) rather than a literal in
  `gripper.scad`. Jake tunes these live in the preview's Tune panel and pastes the copied JSON into a pebble.

## Hardware

- **Arm: Seeed reBot Arm B601-RS** (RobStride motors, 48 V), not the B601-DM (Damiao). Jake confirmed 2026-10-19. Plan: `plans/aero_hand_on_b601.md`.
- **B601-RS motors:** 3× RobStride RS06 (shoulder_pan, shoulder_lift, elbow_flex) + 4× RobStride RS00 (wrist_flex, wrist_yaw, wrist_roll, **gripper**). Sources: [reBot-DevArm RS BOM](https://github.com/Seeed-Projects/reBot-DevArm/blob/main/hardware/reBot_B601_RS/README.md), [LeRobot plugin motor map](https://github.com/Seeed-Projects/lerobot-robot-seeed-b601/blob/main/lerobot_robot_seeed_b601/seeed_b601_rs_follower.py).
- **Base motor (Base N, old 3.x) = RobStride RS00** (the B601-RS gripper motor; do not use the Damiao DM-J4310-2EC, which is the B601-DM's). 10:1 planetary, 48 V (24–60 V), 5 N·m rated / 14 N·m peak, 315 rpm, CAN 1 Mbps, 310 g. Body Ø57 × 51 ±1 mm, output boss Ø35 × 1 mm. Drawing (verify against the STEP): output flange 6× M3 ×5 blind on Ø27 PCD at 60°, 2× Ø3 dowel ×5 and 3× Ø3 on Ø24.46; front housing 6× M3 on Ø50 PCD; back face 4× M3 ×4 on Ø38 PCD at 45°. Every motor dimension stays a `params.json` entry (Tune panel). Sources: [Seeed dimension drawing](https://media-cdn.seeedstudio.com/media/wysiwyg/111-photo/100083284--01.png), [RobStride STEP](https://github.com/RobStride/Product_Information/blob/main/Product%20Literature/CAN2.0/RS00/RS00.step), [RS00 manual](https://github.com/RobStride/Product_Information/blob/main/Product%20Literature/CAN2.0/RS00/RS00User%20Manual260713.pdf), [OpenELAB specs](https://openelab.io/products/robstride00-qdd-14n-m-integrated-joint-motor-module), [Seeed product page](https://www.seeedstudio.com/Robostride-00-Actuator-p-6664.html).
- **Alternative base motor: Feetech STS3215** (the SO-101 servo), from Base 11 (`v311_generalist_motor_choice`): `params.json` `motor_sts` 0 = RS00 (Base 10 exactly, with the reBot wrist mount), 1 = STS3215 (hand-held, no wrist mount). Dimensions from The Robot Studio's [SO-ARM100 STEP](https://github.com/TheRobotStudio/SO-ARM100/blob/main/STEP/SO100/STS3215_03a.step) (Apache-2.0): pinion on the Ø20 horn with 4 M3 on Ø14, base on the case's front rails with 4 M2. `record_grip.py` there reads the back-driven servo through LeRobot's Feetech bus for data collection; for hand use buy the leader-arm gearing (C046 1/147 or C044 1/191, SO-ARM100 BOM), the C001 1/345 follower one is stiff to back-drive.
- **Arm CAD and wrist interface:** Seeed's B601-RS URDF + meshes (CERN-OHL-W-2.0) are in `cad/arm/rebot_b601_rs/` (pinned commit, `arm_pose.py` poses them as mm STLs). The stock gripper mounts via Seeed's Connector A (on J6's output) and Connector B (on the gripper motor's back face, slips over A, 3 radial M3). Base 10 (`v310_generalist_arm_mount`) keeps that interface: a hub on J6, a tool plate per tool (our gripper via an L bracket on its RS00's back face, or the Aero Hand, whose wrist inserts are also 4 M3 on Ø38 at 45°). New end effectors should carry a tool plate, not a new arm flange.
