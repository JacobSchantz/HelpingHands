# Gen 16 parts list

Right-hand build. Mirror X in the slicer (or in `gripper.scad`) for a left hand. Sizes are mm.
Three printed parts, two pivot screws, one camera screw. No wrist or forearm attachment.

## Printed (`exports/print/`, already in print orientation)

| File | Qty | Size | Material | How to print |
|---|---|---|---|---|
| `right_finger.stl` (finger + thumb side pad) | 1 | 57 × 116 × 21 | PETG or PLA+, yellow | Side pad's top face down. **Supports touching the build plate, under the beak only.** 4 walls, 40 % infill. The tip pad is merged in. |
| `left_finger.stl` (finger + index side pad) | 1 | 57 × 116 × 21 | same | same |
| `pivot_plate.stl` (pivots + camera cradle) | 1 | 74 × 62 × 20 | PETG, dark | Flat, cradle up. No supports. 6 walls (it carries both pivots). |
| `two_material/*` | — | — | yellow + dark TPU | Optional: finger body + 2.5 mm tip pad as two bodies, for a two-material printer. Replaces the two finger files. |

About 92 cm³ of plastic. Every part fits a 220 mm bed.

## Hardware

| Item | Qty | Where |
|---|---|---|
| M4 × 16 socket head screw | 2 | Pivots: down through the pivot plate into the nut in the finger's side pad |
| M4 nylon-insert lock nut (7 AF × 5) | 2 | Captive in each side pad: slide it into the slot at the back |
| M4 washer | 4 | One under each screw head, one between each side pad and the plate (sets the 0.8 mm gap) |
| 1/4"-20 × 3/8" button head screw | 1 | Up through the plate's counterbore into the camera's tripod thread |
| Insta360 X4 or X5 | 1 | Stands upright in the cradle, lenses facing forward and back |

## Straps (not modelled)

| Item | Qty | Where |
|---|---|---|
| 20 mm hook-and-loop strap ~150 mm, or a zip tie up to 5 × 1.5 | 2 | One per side pad: under the thumb (right) or index finger (left), up through the pad's 4 × 22 mm slot, closed over the pad |

## Assembly

1. Slide an M4 nyloc into each side pad's slot.
2. Fit each pivot: washer on the side pad, pivot plate, washer, then M4 × 16 down into the nut. Tighten until the finger swings freely with no play.
3. Screw the camera on from underneath (1/4"-20).
4. Thumb under the right pad, index finger under the left, strap each one.
