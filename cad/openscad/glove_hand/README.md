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
| 00 | `gen_00_fit_tray.scad` | Jake's flat spread left hand as a 0.8 mm pad with an 8 mm wall, to check the outline fits | TPU 95A |

## Step 1: outline from a photo

`hand_outline.scad` is **Jake's left hand**, from
`../../glove_hand/refs/jake_left_hand_spread_top.jpg` (spread flat on the
bench, tape measure alongside, shot from eye height at a slant):

    python3 outline_from_photo.py --tape ../../glove_hand/refs/jake_left_hand_spread_top.jpg

It measured 220 mm pinky tip to thumb tip and 170 mm middle tip to wrist
crease. The outline frame has the forearm along -y, wrist cut at y=0, so the
fingers fan out at an angle and the tray is 229 x 183 mm.
`outline_preview.png` is the outline drawn back over the photo in red, wrist
cut in blue. `export/gen_00_fit_tray.stl` is the print.

How `--tape` works: the mm ticks along the tape's left edge are spaced 2.2
px/mm at the top of this photo and 2.9 at the bottom. A pinhole camera
(iPhone 1x focal length, no roll) fitted to that growth comes out 483 mm above
the bench, pitched 13.7 deg, residual 0.002 px/mm. The skin mask (green/blue
< 1.2) is re-projected onto the bench plane lifted 10 mm (where the hand's
outline edge sits), then cut perpendicular to the forearm at its narrowest
point below the palm. A 20 % wrong focal length changes the sizes by under 1 %.
Only the tape's direction is measured; sideways scale comes from the camera
model, so check one width by hand before trusting it to the millimetre.

Print `gen_00_fit_tray.scad` flat in TPU. The pad is the bed layer, so no
supports are needed. Lay the spread hand in it. Fingers inside with a little
room means the outline is good. Change `clearance` (1.5 mm per side) to
tighten it.

Card mode (no `--tape`): white paper and a credit card; the card is the
second-largest dark-on-light blob, its 85.6 mm side sets the scale, and it
assumes the camera is straight above. `--self-test` checks it on a synthetic
photo (0.17 % scale error).

## Step 2 (not started)

Once the tray fits, build the closed shell around the same outline. It needs
thickness: a side photo of the flat hand, or calipers on each finger at the
knuckles plus palm thickness. After that, build the robot glove around the
shell, with tendons or servos on the back.
