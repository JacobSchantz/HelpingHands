# HelpingHands agent conventions

## Gripper design versions

- **1.x — gripper only.** The old "Gen N" numbering maps to 1.N (e.g. Gen 16 = 1.16, `Two Finger Gripper/versions/v016_generalist_rounded_point`).
- **2.x — gripper plus handles** (strap-loop attachment). 2.1 builds on 1.17.
- **3.x — gripper plus handles plus base** (the base/drive assembly: common base the handles plug into, single motor underneath, gear linkage to the handles). Any 2.x handle must fit the base through the shared handle–base interface.
- Each time Jake asks for a change to the gripper design, make a new version (bump the minor number within its line) instead of editing the current one in place.
- Existing `versions/vNNN_*` folders still use the old Gen numbering; workers may rename them to the new scheme as part of their pebble.
- **From 2.4 on, a version is its `params.json`.** `v204_generalist_parametric` names every dimension there (finger outline,
  solid, handles, tongue/pocket). To make the next version, copy the latest parametric folder, change values in `params.json`
  only, run `python3 export_models.py && python3 genus.py && python3 check_geometry.py`, and add it to
  `Scripts/publish_designs.py` (generations) and `cad/mobile_gallery/poses.js` (pivot: `ECHO: pivot` from
  `part="viewer_right"`). Add a new parameter to `params.json` (with its doc and slider range) rather than a literal in
  `gripper.scad`. Jake tunes these live in the preview's Tune panel and pastes the copied JSON into a pebble.

## Hardware

- **Arm: Seeed reBot Arm B601-RS** (RobStride motors, 48 V), not the B601-DM (Damiao). Jake confirmed 2026-10-19. Plan: `plans/aero_hand_on_b601.md`.
- **B601-RS motors:** 3× RobStride RS06 (shoulder_pan, shoulder_lift, elbow_flex) + 4× RobStride RS00 (wrist_flex, wrist_yaw, wrist_roll, **gripper**). Sources: [reBot-DevArm RS BOM](https://github.com/Seeed-Projects/reBot-DevArm/blob/main/hardware/reBot_B601_RS/README.md), [LeRobot plugin motor map](https://github.com/Seeed-Projects/lerobot-robot-seeed-b601/blob/main/lerobot_robot_seeed_b601/seeed_b601_rs_follower.py).
- **Gripper 3.x base motor = RobStride RS00** (the B601-RS gripper motor; do not use the Damiao DM-J4310-2EC, which is the B601-DM's). 10:1 planetary, 48 V (24–60 V), 5 N·m rated / 14 N·m peak, 315 rpm, CAN 1 Mbps, 310 g. Body Ø57 × 51 ±1 mm, output boss Ø35 × 1 mm. Drawing (verify against the STEP): output flange 6× M3 ×5 blind on Ø27 PCD at 60°, 2× Ø3 dowel ×5 and 3× Ø3 on Ø24.46; front housing 6× M3 on Ø50 PCD; back face 4× M3 ×4 on Ø38 PCD at 45°. Every motor dimension stays a `params.json` entry (Tune panel). Sources: [Seeed dimension drawing](https://media-cdn.seeedstudio.com/media/wysiwyg/111-photo/100083284--01.png), [RobStride STEP](https://github.com/RobStride/Product_Information/blob/main/Product%20Literature/CAN2.0/RS00/RS00.step), [RS00 manual](https://github.com/RobStride/Product_Information/blob/main/Product%20Literature/CAN2.0/RS00/RS00User%20Manual260713.pdf), [OpenELAB specs](https://openelab.io/products/robstride00-qdd-14n-m-integrated-joint-motor-module), [Seeed product page](https://www.seeedstudio.com/Robostride-00-Actuator-p-6664.html).
