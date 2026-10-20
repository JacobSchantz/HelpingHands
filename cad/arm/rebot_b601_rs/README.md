# Seeed reBot Arm B601-RS — CAD (voice-3cd78d20)

The arm Jake bought (B601-RS, RobStride motors; see `AGENTS.md` → Hardware), as Seeed publishes it, for OpenSCAD and the live
preview.

- **Source:** [Seeed-Projects/reBot-DevArm](https://github.com/Seeed-Projects/reBot-DevArm) at commit
  [`9e8634c`](https://github.com/Seeed-Projects/reBot-DevArm/tree/9e8634ca0b20403c580903b771da952b17361c27) (main on 2026-10-20):
  `Rebot_Arm_description/RS/` (URDF + meshes) and `hardware/reBot_B601_RS/Metal_Parts/` (the two gripper connectors).
- **Licence:** hardware design © 2026 Seeed Studio Co., Ltd., CERN-OHL-W-2.0 (`LICENSE`, copied from the repo root; its README's
  licence section). Seeed's firmware/software is Apache-2.0 and none of it is copied here. Keep this
  folder's `LICENSE` and this source note with any copy. Our own parts that mate to it (Base 10's hub and tool plates) are new
  designs that take its dimensions.

| Path | What | Changed? |
| --- | --- | --- |
| `urdf/ReBot_Arm_RS.urdf` | Seeed's RS model: 6 revolute joints + the stock gripper (2 prismatic) | byte for byte |
| `meshes/{shared,visual}/*.STL` | the meshes the URDF names, in metres | decimated to 20% where over 12k triangles (`meshes/decimation.json`; 1–3 mm off the originals) |
| `meshes_preview/` | the same, decimated to 5%, for the live preview | new |
| `interface/2-M6-ROTOR.step` | Seeed's "Gripper Connector A": bolts to J6's RS00 output | byte for byte |
| `interface/2-M7-STATOR.step` | Seeed's "Gripper Connector B": bolts to the stock gripper motor's back face, slips over A | byte for byte |
| `vendor.py` | re-downloads all of the above at the pinned commit and redoes the decimation (`--full`: undecimated, ~70 MB, not committed) | ours |
| `arm_pose.py` | forward kinematics from the URDF; writes the posed arm as mm STLs (one per material) in a tool's frame | ours |

The full arm assembly STEP (`hardware/reBot_B601_RS/reBot_B601_RS_v1.0_20260625.step`, 38 MB) isn't copied; fetch it from the
link above if needed.

## The wrist, measured (what Base 10 mates to)

In `link6`'s frame (the URDF's J6 child; +z the roll axis, out of the arm):

- **J6 output** (an RS00): boss Ø35 × 1, its top at z 0. Output M3 on Ø27 (`AGENTS.md`).
- **Connector A** (Ø35.6 × 6, z 0–6): 4 M3 counterbored (Ø3.2 / Ø6) on Ø27 at 60/120/240/300°, centre bore Ø14, 3 × Ø4 reliefs
  on Ø24.46 at 30/150/270°, 3 radial tapped M3 on those same angles at mid-thickness, and 4 × Ø7.06 edge scallops on Ø38 at 45°.
- **Connector B** (Ø56.8 × 9.5, z −0.5–9.0): socket Ø36 × 6.5 open toward the arm, floor 3, centre hole Ø26.2, 4 M3 (Ø3.2,
  head pockets Ø6.2) on Ø38 at 45° into the stock gripper motor's back face at z 9.0, 3 radial Ø3.5 with Ø5.8 counterbores to
  spot faces at r 21.9.
- The stock gripper's motor (motor 7, RS00) is coaxial with J6. Its two connectors stand out radially, side-opposite, over the
  last ~13 mm of the body (to r 41.5, 26 wide). The link6 mesh is A + B. `gripper_end`, `gripper_left` and `gripper_right` are the
  stock gripper.

## Use

```bash
python3 cad/arm/rebot_b601_rs/arm_pose.py --out /tmp/arm --flange 0,0,-98 --roll 0          # numpy only
cad/blender/.venv/bin/python cad/arm/rebot_b601_rs/vendor.py                               # trimesh + fast_simplification
```

`--flange` is where J6's boss top goes in your frame. The default pose (`UPRIGHT`) holds the tool straight up (link6 +z = +z),
which is how the gripper versions are drawn. Base 10's `export_models.py` calls `arm_pose.export()` with its hub's position.
