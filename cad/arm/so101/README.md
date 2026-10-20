# SO-101 arm (Arm 2) — CAD (voice-790aa455)

The Robot Studio's SO-101 follower arm (six Feetech STS3215, the LeRobot arm), as they publish it, for OpenSCAD and the live
preview. Arm 1 is the reBot B601-RS (`../rebot_b601_rs/`); Mount 2 (`Two Finger Gripper/versions/v315_generalist_so101_mount`) puts
our gripper on this one.

- **Source:** [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) at commit
  [`a758567`](https://github.com/TheRobotStudio/SO-ARM100/tree/a758567c3978dfeefe282ede0500085a48fe8f78) (main on 2026-10-20):
  `Simulation/SO101/` (URDF + meshes, made by onshape-to-robot from their Onshape model) and two wrist STEPs from `STEP/SO101/`.
- **Licence:** Apache-2.0 (`LICENSE`, copied from the repo root). Keep it and this source note with any copy. Our parts that mate
  to it (Mount 2's hub) are new designs that take its dimensions.

| Path | What | Changed? |
| --- | --- | --- |
| `so101_new_calib.urdf` | the follower, "new calibration" (each joint's zero mid-range): 5 arm joints + the gripper | byte for byte |
| `assets/*.stl` | the meshes the URDF names, in metres | decimated to 20% where over 12k triangles (`assets/decimation.json`) |
| `assets_preview/` | the same, lighter, for the live preview | new |
| `interface/Wrist_Roll_Pitch_SO101.step` | the wrist part that holds the wrist-roll STS3215 (and rings its horn with a collar) | byte for byte |
| `interface/Wrist_Roll_Follower_SO101.step` | the stock fixed jaw on that horn: what Mount 2 replaces | byte for byte |
| `vendor.py` | re-downloads all of the above at the pinned commit and redoes the decimation (`--full`: undecimated) | ours |
| `so101_pose.py` | forward kinematics from the URDF; writes the posed arm as mm STLs (one per material) in a tool's frame | ours |

## The wrist, measured (what Mount 2 mates to)

In `gripper_link`'s frame (the URDF's wrist_roll child; +z toward the arm, the stock jaw points −z), on the meshes:

- **Wrist-roll STS3215** (in `wrist_link`, `sts3215_03a_no_horn`): its output spline ends at z −1.5 on the roll axis; its round horn
  (Ø20, 2.5 thick, 4 M3 on Ø14, an M3 centre screw; not in the URDF's meshes) sits on it.
- **The stock fixed jaw** (`wrist_roll_follower`) seats on the horn's face at **z −3.0**, a flat floor with 4 counterbored holes on
  **Ø14** at 45° (Ø5.7 counterbores) and a Ø5.2 centre hole, centred at x −0.7 (the URDF's roll axis runs 0.7 mm off the jaw's screw
  circle). It carries the jaw's own STS3215 and the moving jaw; `so101_pose.py` leaves all of that out.
- **The collar:** `wrist_roll_pitch` rings the horn from r 15.2 (r 14 level with the case) and reaches z −4.7, 1.7 mm past the horn
  face. Anything that rolls with the tool must stay inside r ~14 until it is past z −4.7.

## Use

```bash
python3 cad/arm/so101/so101_pose.py --out /tmp/so101 --horn 0,0,-83.5 --roll 0     # numpy only
python3 cad/arm/so101/so101_pose.py --fit                                          # the wrist_flex that holds the tool upright
cad/blender/.venv/bin/python cad/arm/so101/vendor.py                               # trimesh + fast_simplification
```

`--horn` is where the horn's face goes in your frame, the roll axis along your +z. The default pose (`UPRIGHT`: shoulder_lift 0.6,
elbow_flex −1.1, wrist_flex −1.071 rad) holds the tool straight up, the arm reaching in from its base, which is how the gripper
versions are drawn. Mount 2's `export_models.py` calls `so101_pose.export()` with its hub's horn socket floor.
