# Whole-hand direct-contact study

2026-10-23 · voice-3f6ae8e1

Thumb outside one gripper finger, index outside the other; the mechanism sits between them. The inner grasping gap is reserved for objects. No default handles, saddles or straps. This is the human interface, not an Aero Hand robot redesign.

## Shared geometry and acceptance view

voice-550038ca owns CAD, part numbers and catalog. Its Base 21 + Gripper 25 two-pivot design (`v322_generalist_two_pivot_support`) supplies the actual saved meshes. `cad/mobile_gallery/two_pivot_case.js` is the shared contact/motion/pose case used by its acceptance page and this saved-mesh checker. This pass changes no CAD, part versions, motion registry or catalog.

Open `two_pivot_acceptance.html` beside the published gallery's index. It shows the complete skinned hand: wrist, palm, thumb and four fingers. Play animates the mechanism and hand together with the wrist fixed; drag to inspect either side. Choose hand side/length and the other three digits' open/closed curl. Copy fit report includes per-region skin/box intersections and the assumptions. `?angle=15` pauses at a repeatable pose; `&view=palm` selects the opposite camera.

In the regular Live Preview choose **Average human hand → Holding the gripper**. Adjust length, side, pad radius, contact station and **Other digits curl open/closed (%)**. Open/Close animates thumb/index contact and the other three digits together. Keep **Fix wrist through stroke** enabled. Run **Check 13 stroke positions**, then **Copy fit report**. Missing/hidden fingers warn instead of selecting a handle. Hidden physical tool parts still participate in clearance screening.

## Anthropometric and posture assumptions

The existing MIT WebXR generic hand is a complete skin mesh on 25 joints, not contact spheres. Every pose screens all 1,360 skin vertices / 2,314 skin triangles. The viewer uniformly scales wrist-to-middle-tip length: 187.2 mm default; saved checks use 181.1 and 193.3 mm. These reference lengths are documented with the ANSUR II source in `cad/mobile_gallery/reference/human_hand/SOURCE.txt`. The resulting adult hand breadth is about 78 mm: narrow for its length. Uniform scaling preserves that generic shape; it does not independently fit breadth, digit lengths or Jake's hand.

Thumb/index use generic joint limits and local inverse kinematics aimed at actual outer finger surfaces. Contact station follows each finger's local mesh through the stroke, never a handle/cradle. The other digits interpolate from 20% curl open to 80% closed by default; these are adjustable illustrative posture assumptions, not measured natural motion. Thumb/index do not automatically escape a large reach residual. Wrist pose is held after the first available closed-stroke solve; check the displayed contact misses.

## What the collision report measures

Sparse joint/phalanx spheres still guide the IK search and produce the legacy box-overlap depth. After posing, a separate screen evaluates every rendered skin triangle against each conservative world-axis tool box. It reports total intersecting triangles plus wrist, palm and individual-digit regions, identified by dominant skin-bone weights. Triangles spanning region boundaries can count in several regions. Surface intersection catches thin obstacles between vertices; it is not an exact collision test against CAD solids, and can report empty corners of tool boxes. A tool wholly enclosed inside the skin without crossing its surface can be missed. Skin containment, self-collision, soft-tissue compression and continuous motion are not evaluated.

The full skin is diagnostic only: the solver still optimizes sparse envelopes. Therefore a pose may look plausible while the new skin check flags interference, or may have zero flagged skin triangles while missing its contacts. Neither is an acceptance pass. There is no pressure, friction, force, fatigue or comfort model.

## Reproducible screening

`python3 -m unittest Scripts.test_gallery` covers real GLB skin, every named region, a thin obstacle between vertices, a distant negative control, other-digit movement with fixed wrist, outer-surface contact selection, unreachable targets and collision positive controls. The new whole-skin regression was run failing before implementation.

`python3 Scripts/check_human_fit.py --output plans/human_hand_fit.json` screens five geometries (large, compact, Aero-servo, overhead, two-pivot), two lengths, both sides and 13 positions: 260 samples. The two-pivot case uses the same `makeCase` as the acceptance viewer. All contacts are available, but fit remains unresolved: two-pivot worst pad misses range 12.7–17.7 mm across the four hand/side cases, and the larger left hand flags up to 338 skin/box triangles. The saved JSON carries all per-region counts and residuals. The earlier direct-contact table is superseded because unused-digit posture and collision coverage changed.

## Physical review still required

Use a loose, unpowered mock-up. Record hand length/breadth, thumb/index widths, comfortable opposed-pad span and where strain or slipping first occurs. Check rounded outer finger surfaces, pinch/open range, visibility, palm/web/folded-digit clearance, back-driving effort and outward lift to release. Direct contact supports inward squeeze; active opening depends on actual friction and mechanism behavior. Start without added retention; only consider a thin removable friction pad if physical feedback calls for one.

Desktop browser screenshots verify the complete hand renders; phone rendering and physical fit/comfort remain unverified. No printed part or physical acceptance is claimed.
