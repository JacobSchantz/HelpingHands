# Thumb/index interface fit study

2026-10-23 · voice-3f6ae8e1 · CAD screening and attachment proposal, awaiting Jake's physical fit.

The gripper sits between the thumb and index. Each digit controls one moving side; opening must pull both sides apart without trapping either digit. This is the human interface, not a redesign of the Aero Hand robot.

## Current attachment interfaces

Handle 1–3 introduced straps, flush loops and the tongue pocket. Handle 4 made dimensions adjustable; Handle 5 spans the original rail, Handle 6 seats in one step, and Handle 7 reduces the proud edge. Those detachable handles fit their matching finger rails. From Base 8 the cradle and gear are one Base part; the Handle picker correctly disappears. Base 19 separates the low cradle from the overhead shaft with a keyed socket, but the cradle remains a Base part. It is not a new shared Handle socket.

Consequently there is no universal current handle-to-base interface. Preserve every existing rail, bore and key; do not advertise Handle 7 as an adapter for the tiny bases or Base 19. A future shared human-contact pad should attach through webbing to existing slots, leaving the mechanical couplings alone. Any rigid cradle/shaft change would require its own Base version. No part geometry changed in this pass, so no part counter was incremented and no shared registry edit was needed.

## Measured screening

`python3 Scripts/check_human_fit.py --output plans/human_hand_fit.json` reads the actual exported STLs and existing viewer motion definitions. At 13 positions including closed and fully open, it raycasts opposing attachment faces halfway down their bounding height, bends the thumb/index, and keeps the wrist at the first solved position. Existing joint limits are generic assumptions, not measured limits for Jake. Two uniformly scaled right hands are tested; the live preview also supports left and custom lengths.

| Geometry | Parts examined | Worst pad miss, 181 / 193 mm hands | Worst box overlap, 181 / 193 mm hands |
| --- | --- | --- | --- |
| Large | Base 11 / Gripper 21 | 34.9 / 25.2 mm | 5.0 / 11.4 mm |
| Compact | Base 12 / Gripper 21 | 25.1 / 36.1 mm | 3.1 / 3.4 mm |
| Aero-servo | Base 18 / Gripper 24 | 13.8 / 14.6 mm | 3.0 / 3.3 mm |
| Overhead | Base 19 / Gripper 22 | 25.7 / 26.5 mm | 6.6 / 6.3 mm |

All four have contact-face ray hits at all 13 positions. None has demonstrated human fit. A ray hit does not prove that the point is on a strap boss rather than a nearby wall; inspect the contact station visually. A miss is a local inverse-kinematics residual, not a proven anatomical impossibility. Box overlap is conservative: rotated parts become world-axis boxes, which can occupy empty space. Conversely the sparse sphere model can miss skin or webbing collisions. All tool meshes, including jaws, cradles, shafts, screws and wrist brackets, participate in the box check; the remote arm reference is omitted. Hidden meshes still participate. The sample grid is not continuous clearance proof. No pressure, force, fatigue, soft-tissue deformation or retention model is present. No electrical actuation or physical test was performed.

Base 19's saved geometry check reserves 8 mm above the 12 mm finger slab for the drive/cable envelope. That is machine-to-machine clearance, not hand clearance: a human digit is thicker than the slab. The results above reinforce the need to check the thumb web, folded middle/ring digits, wrist and release tabs under that stack. They do not justify lowering the overhead drive. Base 18's shorter motor reduces depth, but does not make its scaled cradle a full-size human attachment.

## Attachment proposal for physical fitting

Use two separate, shallow, padded saddles with independently adjustable webbing: a broader thumb saddle and a narrower index saddle. Avoid one loop around index and middle: it couples two joint trajectories and can obstruct the index's opening movement. The middle/ring/little fingers should remain free to rest beside the mechanism. Keep pad and strap out of the thumb/index web and away from flexion creases.

The following are **initial adjustable mock-up assumptions**, not selected print dimensions or anatomical specifications:

| Feature | Thumb start | Index start | Adjustment to try |
| --- | --- | --- | --- |
| Contact footprint | 24 × 28 mm | 18 × 25 mm | ±6 mm in each direction |
| Soft pad | 3 mm | 3 mm | 2–5 mm; inspect edge pressure |
| Shallow saddle concavity radius | 12 mm | 9 mm | ±4 mm; open sides, no rigid closed ring |
| Loop webbing | Match existing slot, nominal 20 mm on large cradle | Match existing slot | Measure each version; do not scale webbing with the jaw |
| Contact station | 50% down attachment | 50% down attachment | Preview 10–90%, then measure the actual boss |
| Pad yaw relative to cradle | 0° | 0° | Try ±20° in a loose mock-up before fixing it |

Use the same soft pad/webbing concept across full-size cradles. Strap length and pad position adapt without modifying the load-carrying interface. Let soft webbing accommodate small digit rotations instead of forcing both fingers to follow the gear axes exactly. A rigid swivel is deferred until a mock-up shows that webbing cannot accommodate the trajectory.

Retention must permit active opening but release without operating the gripper: use a loose, peel-open loop with a visible pull tab on the outward side of each digit, accessible to the other hand. Avoid a closed printed ring or self-tightening routing. Verify the strap cannot feed into gears, keyed sockets or shaft retainers at either endpoint. Padding spreads contact over the saddle; comfort and allowable tension require actual use, not a calculated pressure from an unknown force.

| Geometry | Integration proposal | Current limit |
| --- | --- | --- |
| Large / compact | Webbing-mounted saddles on existing integral strap bosses; try separate station/yaw for thumb and index | Fixed-wrist full stroke currently misses contacts; pad offset/stroke may need adjustment |
| Aero-servo Base 18 | Dedicated cradle-sized carrier with a full-size digit pad; retain its actual gear/bore dimensions | No validated attachment to the miniature slots; Handle 7 is not compatible; new Base/Handle design requires fit dimensions |
| Overhead Base 19 | Saddles on low strap cradles, with release tabs facing outboard and webbing kept below shafts | Thumb/index envelope must clear overhead servo, rails and cable throughout stroke; 8 mm slab clearance is insufficient evidence |

Keep fingertips and the object-facing jaw tips visible from the head-height cameras described in `handheld_gripper.md`. The saddle should not extend toward the working tips merely to improve reach. For the self-building demo, the same robot jaw geometry must remain available when the human straps are removed; pads should be removable without disassembling the drive.

## Review in the live preview

Turn on **Average human hand → Holding the gripper**. Choose the Base/Gripper pair above. Hand length (140–230 mm), digit radius (4–14 mm) and contact station (10–90%) are explicit exploratory inputs; radius affects the collision/contact model, not the displayed skin mesh. Length scales the whole generic hand, not individual digit proportions. Thumb and index drive opposing sides. The middle digit no longer has a required second contact.

Keep **Fix wrist through stroke** checked; Open/Close now exposes changing reach instead of moving the whole hand to hide it. **Check 13 stroke positions** starts from closed, fixes the wrist and records residuals/box overlap. **Copy fit report** includes assumptions and per-position values. A missing attachment yields a warning rather than substituting the jaw edge. The existing catalog publication path copies these viewer changes; no CAD regeneration is required.

For physical fitting, record Jake's wrist-to-middle-tip length, thumb/index widths where each loop rests, comfortable opposed-pad span at rest and at maximum opening, and a photo from above/side with a ruler. Fit a loose saddle mock-up with the drive unpowered. Move slowly from closed to open and back; note the angle of first strain, slip, pressure edge or interference. Check that each loop peels open at both endpoints without moving a joint or reaching through the mechanism. Use the smallest comfortable stroke until the full stroke is demonstrated. These measurements determine the first printable saddle version; this pass provides the assessment tool and proposal, not a print-ready or comfort-qualified attachment.
