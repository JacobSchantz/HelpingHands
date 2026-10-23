# Direct thumb/index contact study

2026-10-23 · voice-3f6ae8e1 · revised to Jake’s outside-the-fingers clarification.

The thumb rests outside one gripper finger and the index outside the other, directly manipulating the tweezer mechanism. The inner grasping gap is reserved for objects. Large handles, saddles and straps are no longer the proposed default. This is the human hand interface, not an Aero Hand robot redesign.

## Geometry ownership

voice-550038ca owns the new CAD: removing handles, shrinking pivots/hubs where mechanically feasible, reducing the overhead gap and moving the motor to the opposite side above the hand edge. This study changes no CAD, part versions, poses, publisher registry or catalog. It preserves historical Handle/Base versions without requiring their interfaces on the new design. Existing bulky hardware remains visible and participates in clearance screening; selecting finger contacts does not remove that hardware.

The preview identifies “Right finger” and “Left finger” meshes, independent of Base or Handle numbers. Thus new geometry can use the same study when published with those semantic names and its own authored motion. Missing/hidden fingers or a ray that misses the selected station produce an explicit warning; there is no handle/cradle fallback and no claim of universal fit. Coordinate shared catalog edits through the CAD task; this pass needs none.

## Screening of saved meshes

`python3 Scripts/check_human_fit.py --output plans/human_hand_fit.json` reads actual exported STLs and existing motion definitions. At 13 positions, including closed and fully open, it raycasts from outside each finger at mid-thickness. The station is measured from the local finger bounding-box top toward its tip; the ray and its outward normal rotate with that finger. The first surface hit is the intended contact. Thumb/index pads aim at these surfaces with one fixed wrist; the middle finger has no required contact. The solver no longer pulls the palm toward a base plate for this mode.

| Geometry | Parts examined | Worst pad miss, 181 / 193 mm hands | Worst box overlap, 181 / 193 mm hands |
| --- | --- | --- | --- |
| Large | Base 11 / Gripper 21 | 25.4 / 26.9 mm | 12.1 / 4.4 mm |
| Compact | Base 12 / Gripper 21 | 26.2 / 29.2 mm | 12.5 / 11.4 mm |
| Aero-servo | Base 18 / Gripper 24 | 15.6 / 13.2 mm | 4.8 / 2.5 mm |
| Overhead | Base 19 / Gripper 22 | 33.3 / 32.2 mm | 3.2 / 2.3 mm |

All four have outer-surface ray hits at all 13 positions for both hand sizes. None demonstrates human fit. These values replace the earlier attachment/cradle study; do not compare them as a CAD improvement. The new handle-free geometry from voice-550038ca must be screened when available.

A miss is a local inverse-kinematics residual, not proven anatomical impossibility. World-axis boxes conservatively enclose rotated parts and can count empty space as interference; sparse joint/phalanx spheres can also miss real skin collisions. All tool meshes, even hidden ones, participate, including jaws, old cradles, shafts, screws and wrist brackets; remote arm reference meshes do not. Sampling is not continuous clearance proof. The model does not measure pressure, grip force, friction, soft-tissue deformation, fatigue or release. Generic joint limits and uniform hand scaling are adjustable assumptions, not Jake’s measured anatomy. No physical test was performed.

## Direct contact and physical review

Start with the existing outer finger surfaces and minimum added bulk. Assess rounded edges and a broad contact patch before considering a thin removable friction pad. Do not select pad thickness, reshape fingers or create a new Handle from this screening alone: those would need physical feedback and a new version of the changed part.

Direct contact supports inward squeezing. Active opening/back-driving depends on friction and the actual mechanism; this study does not establish it. Check slipping, required opening effort and whether the fingers return as intended without adding retention by default. Release should be possible simply by lifting the digits outward, without threading through a loop. Keep thumb web and folded digits away from hubs, moving shafts and the overhead drive; machine slab clearance alone does not establish hand clearance.

Keep fingertips and working tips visible, with the inner jaw gap available to the object throughout the stroke. Check wrist posture, thumb/index reach and joint trajectory, edge pressure, unintended rubbing, opening effort and outward release using a loose, unpowered mock-up. Record wrist-to-middle-tip length, thumb/index widths, comfortable opposed-pad span and the station of first strain or slip. A thin contact treatment is optional only if that trial shows a need.

## Review in Live Preview

Enable **Average human hand → Holding the gripper**. Try the assemblies above; adjust hand length (140–230 mm), digit pad radius (4–14 mm), side and **Contact down finger (%)** (10–90%). Radius affects the collision/contact model, not displayed skin thickness. Contact station follows the local finger, not a handle. Check the displayed pose: a large residual means the rendered pad may not actually reach the target.

Keep **Fix wrist through stroke** enabled, run **Check 13 stroke positions**, then **Copy fit report**. The report identifies outer-finger contact with no handle/strap assumption. The saved report uses a 50% station and 8 mm pad radius. Existing publication copies the viewer changes; no CAD regeneration is required. Phone rendering and physical comfort remain unverified.
