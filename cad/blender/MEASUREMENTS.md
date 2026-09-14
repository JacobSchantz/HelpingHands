# Where every number in `so101_gripper.py` came from

Blender cannot open STEP, and no OCCT binding ships with it. So the reference
parts were measured **outside** Blender, twice, by two independent readers, and
only the numbers were carried across:

| tool | what it is | what it gives |
|---|---|---|
| `measure_step.py` | ~170 lines of plain Python, no dependencies. Parses the ISO-10303-21 text directly. | vertex bounding box, `CYLINDRICAL_SURFACE` radii + axes, `CIRCLE` radii, `PLANE` offsets, `TOROIDAL_SURFACE` fillet radii, `CONICAL_SURFACE` chamfer angles |
| `measure_step_ocp.py` | OCCT via the `cadquery-ocp` wheel, installed into `cad/blender/.venv/` (gitignored). Used **only as an instrument**. | the same, plus per-face areas, exact optimal bounding boxes, solid volume, centre of mass |

Both were run read-only against `cad/build123d/reference/`; that directory is
untouched (`git status` on it is clean). STEP stores analytic geometry, so a
`CYLINDRICAL_SURFACE` radius *is* the hole radius — nothing here is eyeballed
off a tessellation.

```sh
python3 cad/blender/measure_step.py cad/build123d/reference/*.step
cad/blender/.venv/bin/python cad/blender/measure_step_ocp.py cad/build123d/reference/*.step
```

To recreate the venv: `python3 -m venv cad/blender/.venv && cad/blender/.venv/bin/pip install cadquery-ocp`.

---

## Moving_Jaw_SO101.step

Local frame: pivot axis = Z, finger runs to −Y, +X is the gripping side.
Volume 20 691.5 mm³. Bounding box **22.300 × 92.000 × 48.000 mm**
(X −12.300…10.000, Y −82.000…10.000, Z −24.000…24.000).

| parameter | value | read from |
|---|---|---|
| `mj_hub_span` | 48.0 | Z extent of the solid; outer faces `PLANE` z = ±24 |
| `mj_fork_gap` | 33.4 | inner fork faces `PLANE` z = −17.4 and +16.0 (A = 30 mm² each) |
| `mj_fork_gap_offset` | −0.7 | midpoint of those two faces |
| `mj_hub_r` | 10.0 | bbox Y max = 10.0; matches the Ø20 hub cylinders on the Z axis |
| `mj_finger_length` | 82.0 | pivot (Y=0) to fingertip (Y = −82.0) |
| `mj_back_x` | −12.3 | bbox X min |
| `mj_grip_face_x` | 10.06 | `PLANE` n = (−0.994, 0.105, 0), offset −10.0 → x at y=0 |
| `mj_grip_face_deg` | 6.03 | atan(0.105/0.994) of that plane's normal |
| `horn_bolt_offset` | 4.95 | four Ø3.2 `CYLINDRICAL_SURFACE` at (±4.95, ±4.95) → 14.0 mm PCD |
| `m3_clearance_d` | 3.2 | r = 1.600 cylinders, 8 faces |
| `m3_counterbore_d` | 5.4 | r = 2.700 cylinders on both inner fork faces |
| `servo_horn_bore` | 6.0 | r = 3.000 cylinders on the Z axis |
| `horn_pocket_d` | 20.0 | r = 10.000 cylinders at z = ±24 and the two raised inner rings |
| `horn_pocket_depth` | 6.5 | Ø20 face from z = 24 down to `PLANE` z = 17.5 |
| `bearing_pocket_depth` | 3.6 | z = −24 to `PLANE` z = −20.4 |
| `horn_boss_height` | 1.5 | Ø20 rings z = 16→17.5 and −17.4→−18.9 |
| `pad_hole_d` | 1.5 | r = 0.750 cylinders, axis (0,0,1) |
| `mj_pad_hole_pitch` | 9.944 | Y spacing of those five holes: −18.887, −28.831, −38.776, −48.720, −58.664 |
| `grip_face_inset` | 5.0 | perpendicular distance from the hole line to the gripping plane (5.03) |
| `mj_width_table` | see source | Z extent of each pad hole's cylindrical face = local fork-axis width there |
| `edge_break` | 0.75 | `TOROIDAL_SURFACE` minor radius = 1.0 and the r = 0.75 edge cylinders |

## Wrist_Roll_Follower_SO101.step (the fixed jaw / gripper body)

Body frame: wrist-roll face at z ≈ 0, fin rises in +Z. Volume 56 619.5 mm³.
Bounding box **65.200 × 52.000 × 105.425 mm**
(X −35.200…30.000, Y −24.218…27.782, Z −0.050…105.375).

| parameter | value | read from |
|---|---|---|
| `body_x_min/max`, `body_y_min/max` | −35.2/30.0, −24.218/27.782 | optimal bounding box |
| `wrist_centre_y` | −0.218 | centre of the four Ø3.2 wrist-horn holes and the Ø24 pocket |
| `wrist_boss_d` | 24.0 | r = 12.000 cylinder, axis −Z, 6 mm long |
| `wrist_boss_height` | 6.0 | that cylinder's axial extent; floor is `PLANE` z = 5.95 (A = 1805 mm², the largest face in the part) |
| `wrist_chamfer` | 0.8 | `CONICAL_SURFACE` r = 11.200 / 11.243, half-angle 45° |
| `wrist_bore_d` | 5.4 | r = 2.700 cylinder on the wrist axis |
| `m3_counterbore_d_body` | 6.0 | r = 3.000 cylinders coaxial with the four Ø3.2 holes |
| `base_plate_thickness` | 10.0 | z = −0.05 to `PLANE` z = 9.95 |
| `base_corner_r` | 10.0 | `TOROIDAL_SURFACE` major 7 + minor 3 at the plate corners |
| `cradle_half_width` | 16.0 | `PLANE` y = 15.782 and −16.218, i.e. ±16.0 about y = −0.218 |
| `wall_thickness` | 2.2 | those faces to `PLANE` y = 17.982 / −18.418 |
| `cradle_top_z` | 38.0 | top of the cradle side walls |
| `m2_clearance_d` / `m2_counterbore_d` | 2.0 / 4.0 | r = 1.000 and r = 2.000 cylinders, axis ±Y |
| `servo_screw_pitch_z` | 20.5 | those holes at z = 14.100 and 34.600 |
| `pivot_z` | 24.35 | midplane of that pair — the gripper servo's own centreline |
| `servo_screw_x_py/ny` | −12.6 / −8.8 | X of the +Y-side and −Y-side pairs (they genuinely differ) |
| `access_bore_d` | 10.0 | r = 5.000 cylinder, axis +X, at (y = 0.132, z = 24.35), 20.2 long |
| `fin_lean_deg` | 20.0 | `PLANE` n = (0.94, 0, −0.342) → exactly 20° |
| fixed gripping face | 0.94x − 0.342z = −48.162 | that plane, area 642 mm² — the largest flat face on the fin |
| `fin_pad_hole_pitch` | 10.0 | five r = 0.750 holes, axis Y, spacing 10.00 along the fin |
| `fin_pad_first_s` | 24.14 | first hole at (−27.464, −24, 50.742), projected onto the fin axis |
| `grip_face_inset` | 5.0 | that hole line is 4.99 mm in from the gripping plane |
| `fixed_finger_length` | 81.03 | fin tip z = 105.375 minus `pivot_z` |
| `fin_width_table` | see source | Y extent of the solid in 5 mm Z bands, sampled by ray-casting the tessellated reference |

## Derived, not measured

Two numbers are **fitted**, because they are not in either file — see NOTES.md.

| parameter | value | how |
|---|---|---|
| `pivot_x` | −25.54 | placed so the two fingertips meet: 82.01 mm from the fixed tip (−12.9, 105.375) at `pivot_z` = 24.35 |
| `mj_closed_lean_deg` | 8.84 | the finger lean that follows from that pivot and the fixed tip position |
| `fin_pivot_to_face` | 15.82 | signed distance from that pivot to the fixed gripping plane |
| `fin_tip_s` | 80.44 | fin tip projected onto the gripping face from the pivot station |
