# Robot Glove Hand · generations

One hand that the robot wears and Jake wears: hollow, his fingers inside the
robot's fingers. **Design priority: as little material as possible between
his hand and the object.** Palm and finger pads are ideally a single thin
TPU layer; every cord, servo, and structural part goes on the back and
sides, never under the fingers or palm. Left hand, to match the Aero Hand
(`plans/aero-hand-glove-teaching.md`).

Same rule as `../demo_gripper`: every pass is a new `gen_NN_<label>.scad`;
copy the newest file to the next number and change the copy.

| Gen | File | What | Material |
|---|---|---|---|
| 00 | `gen_00_fit_tray.scad` | Flat-hand outline as a 0.8 mm pad with an 8 mm wall, to check the outline fits | TPU 95A |

## Step 1: outline from a photo

1. Spread the hand fully flat, palm down, on plain white paper. Fingers point
   to the top of the photo, wrist toward the bottom. Put a credit card flat on
   the paper, not touching the hand. Shoot straight down from about 50 cm.
2. `python3 outline_from_photo.py ~/Downloads/<photo>.jpg` writes
   `hand_outline.scad` (mm, wrist at y=0) and `outline_preview.png` (the
   outline drawn back in red over the photo, wrist cut in blue). Check the
   preview before printing.
3. Render or export `gen_00_fit_tray.scad`, then print it flat in TPU. The
   pad is the bed layer, so no supports are needed. Lay the spread hand in it.
   Fingers inside with a little room means the outline is good. Change
   `clearance` (1.5 mm per side) to tighten it.

The card is found as the second-largest dark-on-light blob, and its 85.6 mm
side sets the scale. Pass `--mm-per-px` if there is no card. The wrist cut is
the narrowest row in the bottom 40 % of the hand. `--self-test` runs the
extractor on a synthetic photo with a known scale. Its last run had a 0.17 %
scale error.

**Right now `hand_outline.scad` is a PLACEHOLDER** (a synthetic ~95th
percentile large left hand from `--placeholder`, not Jake's). The SCAD echoes
a NOTE while that is true. Do not print the tray until the photo outline
replaces it.

## Step 2 (not started)

Once the tray fits, build the closed shell around the same outline. It needs
thickness: a side photo of the flat hand, or calipers on each finger at the
knuckles plus palm thickness. After that, build the robot glove around the
shell, with tendons or servos on the back.
