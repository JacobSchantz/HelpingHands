# Gen 15 parts list

Right-hand build. Mirror X in the slicer (or in `gripper.scad`) for a left hand. Sizes are mm.

## Printed (`exports/print/`, already in print orientation)

| File | Qty | Size | Material | How to print |
|---|---|---|---|---|
| `right_finger.stl` (thumb side) | 1 | 30 × 109 × 12 | PETG or PLA+, yellow | Flat. **Supports touching the build plate, under the beak only** (the last ~25 mm thins on both faces). 4 walls, 40 % infill. The tip pad is merged in. |
| `left_finger.stl` (index side) | 1 | 30 × 109 × 12 | same | same |
| `right_carrier.stl` | 1 | 48 × 53 × 21 | PETG, dark | Top face down. No supports: the nut slot is a 7.3 mm bridge. |
| `left_carrier.stl` | 1 | 48 × 53 × 21 | same | same |
| `pivot_plate.stl` | 1 | 74 × 40 × 6 | PETG, dark | Flat, 100 % infill or 6 walls (it carries both pivots). |
| `hand_frame.stl` | 1 | 110 × 117 × 13 | PETG, dark | Top face down, rails up. No supports. |
| `camera_mount.stl` | 1 | 53 × 61 × 14 | PETG, dark | Base down. No supports. |
| `two_material/*` | — | — | yellow + dark TPU | Optional: finger body + 2.5 mm tip pad as two bodies, for a two-material printer. Replaces the two finger files. |

About 150 cm³ of plastic in total. Every part fits a 220 mm bed.

## Hardware

| Item | Qty | Where |
|---|---|---|
| M4 × 16 socket head screw | 2 | Pivots: down through the pivot plate into the carrier's nut |
| M4 nylon-insert lock nut (7 AF × 5) | 2 | Captive in each carrier: slide it into the slot at the back before fitting the finger |
| M4 washer | 4 | One under each screw head, one between each carrier and the pivot plate (that washer sets the 0.8 mm gap) |
| M3 × 22 socket head screw + M3 nut + washer | 4 | Finger to carrier, 2 per side, through the finger's two 3.2 mm holes. The nut goes on the finger's underside. |
| M3 × 5.7 heat-set insert | 4 | In the pivot plate |
| M3 × 8 socket head screw | 4 | Hand frame down into the pivot-plate inserts |
| M3 × 12 screw + nut | 4 | Camera mount to hand frame, nuts under the frame |
| 1/4"-20 × 1/2" screw | 1 | Up through the frame and the camera mount into the camera's tripod thread |
| Insta360 X4 or X5 | 1 | Stands upright in the cradle, lenses facing forward and back |

## Straps (not printed)

| Item | Qty | Where |
|---|---|---|
| 20 mm hook-and-loop strap, ~150 mm | 2 | Thumb (right carrier) and index finger (left carrier). It goes under the digit, up through both 4 × 22 mm slots, and closes over the carrier. |
| 25 mm hook-and-loop strap, ~300 mm | 1 | Wrist, through the frame's two 4 × 22 mm slots |
| 3 mm adhesive foam | — | Under the frame's two rails and the carriers, to taste |

Every strap slot also takes a zip tie up to 5 × 1.5 mm.

## Assembly

1. Press the 4 heat-set inserts into the pivot plate.
2. Slide an M4 nyloc into each carrier's slot, from the back.
3. Bolt each finger under its carrier: 2 × M3 × 22, heads in the carrier's counterbores, nuts under the finger. The carrier's lip locates on the finger's outer edge.
4. Fit each pivot: washer on the carrier, pivot plate, then washer + M4 × 16 down into the nut. Tighten until the finger swings freely with no play. The nylon holds that setting.
5. Bolt the hand frame onto the pivot plate (4 × M3 × 8), and the camera mount onto the frame (4 × M3 × 12).
6. Screw the camera on from underneath (1/4"-20), then fit the straps.
