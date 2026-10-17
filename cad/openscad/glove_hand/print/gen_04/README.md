# gen_04 index finger: first test print

This is a first test print, to check the fit and the motion of ONE index finger, worked by hand. It is not a glove yet, and nothing in it is proven until it's printed (see "What this print has to tell us"). Rebuild everything with:

    python3 ../../print_gen_04.py      # STLs in print orientation, mesh checks -> report.md
    python3 ../../check_gen_04.py      # interference, stops, neighbours, line and elastic

## Files

| File | Count | How it prints |
|---|---|---|
| `gen_04_coupon.stl` | 1 | Flat. **Print this first, on its own** (about 15 min). |
| `gen_04_proximal.stl` | 1 | Flat top down. Supports (tree, build plate only) only under the MCP tab. |
| `gen_04_middle.stl` | 1 | Flat top down. No supports. |
| `gen_04_distal.stl` | 1 | Flat top down. No supports. |
| `gen_04_base.stl` | 1 | Upright as exported. Supports (tree, build plate only) under the pad and the post. |
| `gen_04_drum.stl` | 1 | Lock-hole flange down. No supports. |
| `gen_04_plate.stl` | | All six laid out on one 256 × 256 bed (X1C). |

The STLs are gitignored like every generation's. On another checkout, run `print_gen_04.py`.

## Settings

These start from your Bambu Studio profiles: **Bambu Lab X1 Carbon 0.4 nozzle**, **0.20mm Standard @BBL X1C**, **Bambu PETG Basic @BBL X1C** (255 °C, textured PEI at 70 °C). Changes from the profile: 3 walls, 40 % gyroid infill, a brim on the saddles and the base, and supports per part as in the table above. The full table is in `report.md`.

Not sliced here. Bambu Studio's command line crashes on this Mac, and Cura's engine hangs. Load `gen_04_plate.stl` in the Bambu Studio app. Check that the saddles lie on their flat tops, and that the slicer's support preview only shows supports where the table says. If it puts supports anywhere else on the middle saddle, distal saddle or drum, tell me: they were designed not to need any.

PLA+ (what's loaded now) will work for a fit test. PETG is the choice for the real thing because it's less brittle at the pins.

## Parts list (besides the prints)

| Item | Count | For |
|---|---|---|
| M3 × 6 screw + M3 washer | 1 | MCP pivot. Threads into the base plate's 2.5 mm hole; the head holds the tab. |
| M3 × 20 screw + M3 nyloc nut | 1 | Drum axle. The nut sits in the hex pocket on the cheek. |
| 1.75 mm filament offcuts | 2 × 6 mm, 1 × 15 mm | PIP and DIP pins, drum lock pin. |
| 1 mm braided line (PE fishing braid, about 50 lb) | 300 mm | The flexion line. |
| 2 mm round elastic cord | 250 mm | The return. Cut 121 mm between knots. |
| 10 mm hook-and-loop strap | 150 mm | Proximal saddle. |
| 20 mm hook-and-loop strap | 300 mm | Palm. |
| Drill bits 1.8 and 2.0 mm (by hand), 2.5 mm | | Clean the pin bores and the M3 tap hole. |

## Step 0: the coupon

- **Bar:** 7 horizontal holes, from left 1.7 / 1.8 / 1.9 / 2.0 / 2.1 / 2.5 / 3.3 mm. The notch count on top is the hole number. Find the hole that 1.75 filament presses into firmly; that sets `pin_fix` (now 1.8). Find the one it turns freely in without rattling; that sets `pin_run` (now 2.0). An M3 screw should self-tap the 2.5 hole and pass freely through the 3.3.
- **Comb:** 3 slots for the 2 mm tab, with 0.2 / 0.3 / 0.4 mm clearance a side (1 to 3 notches). The tightest slot the tab slides in without binding sets `lug_c` (now 0.3).

If anything differs, change those values at the top of `gen_04_index_print.scad` and re-run both scripts before you print the rest.

## Assembly

1. Remove the supports. Ream the pin bores by hand with the 1.8 drill (fork plates) and the 2.0 drill (lugs).
2. **PIP:** slide the middle saddle's fork over the proximal saddle's lug. The lug goes between the fork's two plates, on the thumb side. Push a 6 mm filament pin in from outside, flush. Do the **DIP** the same way (distal fork over the middle lug). Each should swing freely from straight to its stop: about 100° at the PIP, 71° at the DIP.
3. **MCP:** put the proximal saddle's tab on the outside of the base's plate, M3 × 6 + washer through the tab into the plate. Snug it, but the tab must still swing. Range: straight to 95° (the tail lands on the block), and about 4° of hyperextension.
4. **Drum:** M3 × 20 through the drum, knob side out, into the cheek, with the nyloc in the hex pocket. Leave a little friction.
5. **Line:** tie a double overhand stopper in one end. Thread the other end from the knot pocket at the fingertip end of the distal saddle's guide, back toward the hand through the distal guide, the middle saddle's two guides and the proximal's two guides (all on the thumb side, below the joints). Then under the MCP, round the back and bottom of the post behind the knuckle, up to the front of the drum. Go through the hole in the knob next to the core and knot it in the countersink on the knob's face. With the finger straight, take up the slack, then lock: push the 15 mm pin through the cheek into whichever drum hole lines up.
   **Turning:** turn the knob so its top rolls toward your wrist to wind the line in and curl the finger. Turn the other way and the elastic opens it.
6. **Elastic:** knot one end and pull it into the countersink on top of the distal saddle. Thread back through the distal, middle and proximal top channels, then the eyelet over the knuckle. Tie it round the anchor post at the back under its head, with 121 mm between the knots.
7. **Straps:** the 10 mm strap goes through the proximal saddle's slot, under your finger and over the saddle. The 20 mm strap goes through the base's ulnar slot, round your palm and back over the base, onto itself.

## The first fit and motion test (unpowered, bounded)

**On the bench, no hand:**
1. Move each joint through its range by hand. Note where each stop lands (phone protractor): about 95 / 100 / 71°.
2. Turn the knob in 20° clicks. Note the joint order and how many clicks to full curl. The prediction is about 15 clicks; the line arms say the PIP and DIP close before the MCP.
3. Let go. The elastic should bring it back straight. Note any joint that doesn't.
4. With a luggage or spring scale on the line at the drum, note the pull to start curling and the pull at full curl.

**On your hand** (left index), with the drum unlocked, for 5 minutes at most:
1. Thumb out at least 35° from the index (an L shape), fingers together. Strap the palm, then the proximal saddle.
2. At rest, nothing should press on a knuckle, and your middle finger should move freely beside it.
3. Make a slow fist on your own. Stop at the first pinch or press, and note how far each joint got.
4. Turn the knob slowly with your other hand. Stop at any pressure or pain. Don't lock it curled.
5. Take it off and photograph any red marks.

**Stop at once on pain, numbness or a sharp press:** pull the lock pin and the elastic opens it.

## What this print has to tell us

Pin, tab and bolt fit; line friction in the guides; the pull force needed; whether the elastic opens it reliably; whether one strap keeps the saddles in place; comfort and pressure points; and whether the joint order matches the prediction. None of that is shown by the checks. They only show the geometry doesn't collide in the model, which uses `jake_hand.scad` with its GUESSED thicknesses.
