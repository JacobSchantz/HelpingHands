# Generalist Gripper · Generation 8 — Pollen's Grabette and Gripette, exactly as published

Jake (voice-933444c1): *"Gen 8 should just be exactly the Grabette files assembled into
what looks like the Grabette, so I can view it and explode it."* Then: *"For number eight,
I want to include the robotic gripper as well."* So Gen 8 is not a redesign. It is
Pollen Robotics' own two grippers (right-hand versions), built from their files and
placed where their URDFs put each part:

- **Grabette** (left in the viewer): the hand-held gripper a person uses to record demos.
- **Gripette** (right, 320 mm over): the robot-side gripper with the same finger, driven by servos.

Nothing is merged with Gen 6 or Gen 7.

## How each one is driven

**Grabette has no motor.** You hold the handle and close the one finger yourself; it
pivots on bushings against the fixed thumb. Two magnetic angle sensors measure the grip:
a 4×2 mm magnet sits in the handle at the finger's pivot and another in the finger tip at
the knuckle, and two AS5600L sensor boards ride on the finger, one over each magnet. Each
reads one joint angle (proximal and distal) at about 85–100 Hz, and those two angles are
the grip in the recording.

**Gripette is direct drive, with no gears or linkage.** Two Feetech STS3215 serial bus
servos (ID 1 and ID 2, 1 Mbaud, from a Raspberry Pi Zero 2W):
- the **proximal servo (ID 1)** sits in the base, and its horn bolts straight to the finger,
  so it swings the whole finger;
- the **distal servo (ID 2)** rides on the finger, and its horns bolt straight to the tip
  part, so it bends the tip.

The joints match the Grabette's, so the two are a pair: Pollen's teleop
(`packages/grabette/docs/teleop.md`) drives a Gripette live from a Grabette, proximal
sensor to proximal servo and distal sensor to distal servo.

In the viewer the drive parts are recoloured to stand out: **magenta = Gripette servos,
red = Grabette angle sensors and magnets** (their part names start `DRIVE` / `SENSOR`).
`previews/drive.png` shows only those plus the faint frame. Nothing else is recoloured.

## Where it comes from

- Upstream: <https://github.com/pollen-robotics/grabette>, pinned to commit
  `b5bacab06c19109b00acffefe38c3d3b3cb60bfc`, folders `packages/grabette/urdf/grabette_right/`
  (→ `pollen/`) and `packages/gripette/urdf/gripette_right/` (→ `pollen/gripette/`).
  Both were generated from Pollen's Onshape CAD by onshape-to-robot (`config.json` has the link).
- Licence: Apache-2.0, Copyright 2026 Pollen Robotics. `pollen/LICENSE`, `pollen/NOTICE`
  and `pollen/THIRD_PARTY_NOTICES.md` are copied unchanged and cover both (the gripette
  package's LICENSE is the same file).
- `pollen/SOURCE_MANIFEST.json` records the SHA-256 of every upstream file.
- How-it's-driven facts come from Pollen's READMEs, `packages/gripette/docs/motor_setup.md`
  and the two assembly PDFs at the same commit.

The meshes are in Git LFS upstream, and this repo ignores `*.stl`. So the URDFs, licence
files and manifest are committed here, and `python3 fetch_grabette.py` brings the meshes
back byte-for-byte. It refuses to continue if any file differs from the manifest.

## How it is assembled

`export_models.py` reads both `robot.urdf` files and does forward kinematics. Each
`<visual>` becomes one gallery part (73 for Grabette, 79 for Gripette): the upstream STL
with its shape unchanged, moved by the URDF's link, joint and visual transforms (metres to
mm), and coloured with the URDF material. Part names are `<Grabette|Gripette> <body|finger|finger tip> — <part>`.
The only change is a whole-model rotation so the finger joints turn about the gallery's
Y axis (body on top, finger hanging down), plus the 320 mm shift for Gripette.

- **Explode:** each part slides away from the centre of its sub-assembly, and each finger
  slides further away from its body. The offsets are in `viewer_parts.json` and
  `gripper.scad` (`explode=1`); `previews/exploded.png` shows the result.
- **Open/closed slider:** each gripper has one moving finger; its thumb is part of the
  body. Both URDF proximal joints run 90° from wide open (79 mm between the soft tips) to
  tips together. The gallery angle is 0 = closed and 90 = open, and moves both fingers.
  The hinges are in `cad/mobile_gallery/poses.js`. The distal joint is held at 0°.

## Files and checks

- `fetch_grabette.py` — fetches and verifies the upstream files into `pollen/`.
- `export_models.py` — writes `gripper.scad` (the same scene, as OpenSCAD imports),
  `exports/parts/*.stl`, `exports/assembly.stl`, `viewer_parts.json`, `mesh_checks.json`
  and `previews/` (`front`, `side`, `iso`, `closed`, `exploded`, `drive`).
- `check_geometry.py` — for each gripper, checks that the gallery hinge puts every finger
  part where URDF forward kinematics does (error under 0.01 mm at 0/30/60/90°), that closed
  tips nearly meet (~2 mm) and that open is wide (79 mm, the positive control).
