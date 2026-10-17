# gen_04 print package: checks

Written by `print_gen_04.py`; do not edit by hand. Not sliced (see the script's docstring).

## Meshes (print orientation, on z = 0)

| Part | Count | Prints | Closed + oriented | Bodies | Volume, cm³ | Size x × y × z, mm | On the bed, mm² | Down-facing > 45° off the bed, mm² | Wall 1st / 5th pct / median, mm | Sampled walls under 1.2 mm |
|---|---|---|---|---|---|---|---|---|---|---|
| coupon | 1 | pin and clearance coupon (bar, comb, tab): print and test this first | yes | 3 | 5.7 | 60 × 32 × 8 | 941 | 96 | 0.6 / 0.6 / 8.0 | 5% |
| proximal | 1 | proximal saddle, top down (supports only under the MCP tab) | yes | 1 | 4.0 | 28 × 54 × 26 | 203 | 250 | 1.1 / 1.2 / 2.7 | 5% |
| middle | 1 | middle saddle, top down | yes | 1 | 3.5 | 27 × 33 × 23 | 209 | 139 | 1.0 / 1.2 / 2.9 | 6% |
| distal | 1 | distal saddle with the fingertip cap, top down | yes | 1 | 3.2 | 25 × 32 × 22 | 113 | 72 | 0.5 / 1.3 / 3.0 | 4% |
| base | 1 | base over the back of the hand, upright (supports under the pad and the post) | yes | 1 | 8.3 | 33 × 70 × 50 | 0 | 1403 | 1.0 / 1.6 / 2.4 | 1% |
| drum | 1 | line drum with knob, lock-hole flange down | yes | 1 | 3.3 | 25 × 25 × 11 | 399 | 270 | 1.4 / 1.6 / 5.3 | 0% |

Total 28.0 cm³ of solid, about 36 g of PETG if printed solid (less with infill).

## Settings

| Setting | Value | From |
|---|---|---|
| Printer | Bambu Lab X1 Carbon 0.4 nozzle | Bambu Studio profile |
| Nozzle | 0.4 mm | Bambu Studio profile |
| Process | 0.20mm Standard @BBL X1C | Bambu Studio profile |
| Layer height | 0.2 mm (first 0.2) | Bambu Studio profile |
| Filament | Bambu PETG Basic @BBL X1C | Bambu Studio profile |
| Nozzle temperature | 255 °C (first layer 245) | Bambu Studio profile |
| Bed | Textured PEI 70 °C (first layer 70) | Bambu Studio profile |
| Walls | 3 (profile has 2) | changed: pin bores and lugs want solid walls |
| Infill | 40 % gyroid (profile has 15%) | changed: thin parts, mostly walls anyway |
| Supports | per part, see the table: tree (auto), on build plate only, threshold 30° | changed per part |
| Brim | on for the saddles and the base (narrow tops on the bed) | changed |
