# Generalist Gripper · Generation 8 — Pollen's Grabette, exactly as published

Jake (voice-933444c1): *"Gen 8 should just be exactly the Grabette files assembled into
what looks like the Grabette, so I can view it and explode it."* So Gen 8 is not a
redesign. It is Pollen Robotics' own Grabette (right-hand version), built from their
files and placed where their URDF puts each part. Nothing is merged with Gen 6 or Gen 7.

## Where it comes from

- Upstream: <https://github.com/pollen-robotics/grabette>, pinned to commit
  `b5bacab06c19109b00acffefe38c3d3b3cb60bfc`, folder `packages/grabette/urdf/grabette_right/`.
  That folder was generated from Pollen's Onshape CAD by onshape-to-robot
  (`pollen/config.json` has the Onshape link).
- Licence: Apache-2.0, Copyright 2026 Pollen Robotics. `pollen/LICENSE`, `pollen/NOTICE`
  and `pollen/THIRD_PARTY_NOTICES.md` are copied unchanged and stay with the files.
- `pollen/SOURCE_MANIFEST.json` records the SHA-256 of every upstream file.

The 37 meshes (34 MB) are in Git LFS upstream, and this repo ignores `*.stl`. So the
URDF, licence files and manifest are committed here, and `python3 fetch_grabette.py`
brings the meshes back byte-for-byte. It refuses to continue if any file differs from
the manifest.

## How it is assembled

`export_models.py` reads `pollen/robot.urdf` and does forward kinematics. Each of its 73
`<visual>` entries becomes one gallery part: the upstream STL with its shape unchanged,
moved by the URDF's link, joint and visual transforms (metres to mm), and coloured with
the URDF material. There are 48 body parts (shell, grip, Raspberry Pi and box, OAK-D SR
camera, PiSugar battery, fisheye camera, screws and so on), 17 finger parts and 8 finger-tip
parts. The only change is a whole-model rotation so the finger joints turn about the
gallery's Y axis (body on top, fingers hanging down).

- **Explode:** each part slides away from the centre of its sub-assembly (body, finger or
  tip), and the finger slides further away from the body. The offsets are in
  `viewer_parts.json` and `gripper.scad` (`explode=1`); `previews/exploded.png` shows the result.
- **Open/closed slider:** the Grabette has one moving finger. Its thumb is part of the body.
  The URDF's proximal joint runs from 0° (wide open, 79 mm between the soft tips) to −90°
  (tips together). The gallery angle is that value plus 90, so 0 = closed and 90 = open,
  and the hinge is in `cad/mobile_gallery/poses.js`. The distal joint (the tip's passive
  flex) is held at 0°.

## Files and checks

- `fetch_grabette.py` — fetches and verifies the upstream files into `pollen/`.
- `export_models.py` — writes `gripper.scad` (the same assembly, as OpenSCAD imports),
  `exports/parts/*.stl`, `exports/assembly.stl`, `viewer_parts.json`, `mesh_checks.json`
  and `previews/` (`front`, `side`, `iso`, `closed`, `exploded`).
- `check_geometry.py` — checks that the gallery hinge puts every finger part where URDF
  forward kinematics does (error under 0.01 mm at 0/30/60/90°). It also checks that closed
  tips nearly meet (1.8 mm) and that open is wide (79 mm). The open case is the positive control.
