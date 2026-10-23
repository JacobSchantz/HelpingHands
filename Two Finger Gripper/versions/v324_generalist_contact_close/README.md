# Base 23 + Gripper 27 — meeting tips and sourced servo connection

**Base 23 builds on Base 22; Gripper 27 builds on Gripper 26.** Historic versions remain untouched. This remains the compact hand-held **HLS3606M-C001** branch, with no SO-101/Mount 2 bracket or Handle interface.

![Actual closed tips and exploded servo connection](previews/comparison.png)

## Closure and useful stroke

The previous design's middle blade approached first, leaving a **4.78 mm distal gap** despite its nominal 0.2 mm allowance. Simply removing that allowance does not make the ends touch. Gripper 27 retains integral jaw sectors but adds **solid 1.5 mm distal contact noses**, about 3 mm inward from the previous tip, with no extra printed part. Original tip corners are trimmed 0.2 mm behind the new distal contact, so no old tip protrudes beyond it. They are added after lattice/ridge cuts, avoiding a rejected 0.128 mm sliver; minimum plan ligament stays **0.4047 mm**.

Pivot spacing grows slightly **19.6 → 20 mm**. A -0.620189° toe correction leaves 0.6 mm nominal middle-blade clearance; the new contact faces meet at **X=0, Z=61.5..63 mm, jaw=0°**. The tooth phase remains unchanged because its compensating toe rotation is retained. Full jaw bodies have only 3.8e-8 mm³ numerical intersection at closure, below the 1e-4 mm³ STL tolerance. Opening 0.1° releases them by **0.2147 mm**. A deliberately uncommanded -0.1° control intersects the noses and is rejected.

Minimum rear clearance is **1.2291 mm**, over the continuous 0–30° stroke, exceeding the assumed 0.8 mm manufacturing/deflection budget. Two local steel-reinforced 3 mm pivot sleeves remain the only support crossing the 6 mm finger band; projection remains 12.799 mm². First teeth remain 0.8 mm overhead. Centered motor, split-height counter-rotating gears, 30:30:42 teeth and four printed pieces remain. The inherited 43% lower ideal torque multiplication versus Base 21 remains; force/strength is unverified.

`motion_limits.json` is a **design/calibration contract, not executable motor control**. It proposes nominal closure at the manufacturer's neutral 180°/2048 ticks and opening at tick 1805, rounding inward to avoid exceeding 30° (29.9004° at integer ticks). Electronic wrap margin is 158.6426°. Feetech specifies **no mechanical angle limit**, so there is no internal physical end stop to trust. No negative jaw command or extra overtravel is permitted to hide a gap.

CAD contact is not a guarantee of real rigid-tip closure. The assumed print error is ±0.3 mm per side; the two middle blades have 0.6 mm nominal clearance, while the tip faces deliberately have zero nominal gap. Encoder half-step alone reflects about 0.135 mm tip-separation uncertainty; documented servo backlash is up to 0.5° at its output. There is no qualified flexure/contact-force model. Physical assembly needs measured phase/contact teaching with limited force/current and consistent closing direction; never blindly command absolute ticks or compress the tips to conceal tolerance errors. No servo was actuated.

## Hardware facts and discrepancies

The selected hardware is **HLS3606M-C001**, not STS3215. Reproducible `check_hardware.py` reads cylinder axes and depths from the pinned STEP with OpenCascade and compares them analytically to the parametric screw positions. It also reads actual exported head seating faces.

| Connection | Source finding | New design |
| --- | --- | --- |
| Output spline / axial retention | Feetech: 25T / Ø4.95, M2.3×5 center screw. STEP uses smooth Ø4.93 spline envelope and a 3 mm-deep smooth Ø2.3 center bore. | Bought metal plate retained; no printed spline. Original center screw captures a new integral pinion web. |
| Bought rotating plate | Pinned Aero STEP: **eight smooth Ø2 holes on Ø12.007619 PCD**, 2 mm disk; center bore seat grip 1.2 mm. BOM calls for M2×4 plate screws; actual threads are not modeled. | **Two opposed M2×4 screws**, native 45°/225°, replace three. Modeled grip 2.25 mm and engagement 1.75 mm. |
| Case mounting | Manufacturer: **four Ø2.5 case-ear holes**; four M2×6 self-tapping screws enter the printed posts, separate from plate screws. Drawing offsets -8.21/+19.79 mm; STEP -7.96/+19.54, transverse 7 mm. | All four retained. Existing 0.5 mm pilot slots cover the 0.25 mm longitudinal discrepancy; transverse dimension comes from STEP. |
| STS3215 comparison | Four M3 on Ø14 is the other servo's interface. | A deliberate Ø14 PCD control misses the HLS holes by about 0.996 mm and fails. It is not used. |

The four-screw recollection does not match this selected plate STEP; it could refer to the separate four case-ear screws or another supplied plate revision. **Jake's physical plate is not identified by these sources.** No physical fit is declared: verify the actual plate's hole count, PCD and threads before fabrication. Smooth Ø2 CAD cylinders do not prove an M2 thread's minor diameter or pitch. Manufacturer page 7 lists no accessories; obtain/identify the Aero plate separately rather than assume every C001 package includes it.

### Center screw: corrected modeled bottoming

The original flat plate seat at Y=13.8 mm with a nominal 5 mm under-head screw projected to Y=18.8; the source STEP bore floor is Y=18.0, an **0.8 mm bottoming discrepancy**. Base 23 integrates a **1 mm capture web into the existing pinion**, moving the head seat to Y=12.8. The screw tip ends at Y=17.8, leaving **0.2 mm modeled floor clearance and 2.8 mm engagement**. No washer or separate mounting adapter is added. The web has Ø2.6 clearance and the existing Ø5.3 head/driver well.

This resolves the nominal STEP stack; it does not prove a production screw's length/head tolerances or actual blind thread depth. The original manufacturer screw designation is the source for M2.3×5; the supplied screw must be measured. The full screw thread is intentionally omitted from collision probes where it engages the output; exported head/seat geometry and analytical engagement are checked separately.

## Parts, assembly and load path

Four actual print solids: two integral jaw/gears, pinion, overhead base. Purchased parts: motor, metal plate, two plate screws, one center screw, four case screws, two M2×25 pivot bolts, two washers, two nuts. **19 total**, versus 20 in Base 22 and 22 in Base 21. All physical items appear in the preview manifest and assembly; cable/driver reserves are not counted as parts.

Seat the motor on the four case-ear posts. Position the bought plate on its output, place the pinion and loosely install the two opposed M2×4 screws. Fit the original center screw through the pinion's access well; its head now bears on the integral web, clamping pinion and plate together. Verify full seating and no screw bottoming before tightening the plate screws. Install the integral jaws in the exported phase over their sleeves, then the same local pivot washers/bolts/nuts. The center tool path remains accessible through the pinion after assembly.

Drive load goes from bought spline plate through two opposed M2 screws and the clamped pinion flange to the right sector, then the lower sector pair. The center screw provides axial capture. Jaw retention remains 0.75 mm radial washer overlap, 0.2 mm lower clearance, 0.5 mm endplay, 1.6 mm nut engagement. No slipping hex coupling remains.

All CAD shaft/tool probes pass. Two case-ear locations still need a 10° driver shaft tilt in the source geometry; the source guide calls the case screws flanged Torx, so previous assumptions of PH0 engagement are not relied on. **Real drive engagement, tool handles and supplied head dimensions remain unverified.** Four case screws are retained because deleting them would need a separately justified housing load path. Printed bearing walls remain 0.4 mm; crushing, locking, neck/tooth strength, tip loading, resin tolerances, wear and actual cable bend need physical tests.

## Verification and whole hand

Run `python3 export_models.py`, `../../../cad/build123d/.venv/bin/python check_hardware.py`, then `../../../cad/blender/.venv/bin/python check_geometry.py`, `check_closure.py`, `genus.py`. Four prints are watertight single bodies; genus is 33/33/3/3. All 121 motion poses ×78 body pairs, tool paths, 726 outside contact approaches, retention and wrong-phase controls pass without body-pair exclusions. Body collision screening is sampled; rear-outline and swept vertex extrema are continuous.

**Whole-hand acceptance still FAILS.** The shared narrow WebXR right hands at 181.1/193.3 mm miss outside contacts by up to **26.59/35.31 mm**, with actual skin vertices inside jaw solids at **2/13 poses each**. This is not ergonomic acceptance. Conservative full-part boxes affect the IK cost for integral jaw/gears; a solver miss does not prove anatomical impossibility. Vertex sampling can miss crossings and does not model pressure. No physical fit or human trial was performed.

Open `contact_acceptance.html` from the published gallery for complete-hand motion and Copy fit report. This uses unchanged `human_hand.js`; `contact_case.js` is the shared case/pose/contact owner for hand-study voice-3f6ae8e1. Jaw axes ±10 X, export 15°, stroke 0–30°, right +1/left -1; rotor axis [0,0,-21.8174242293], ratio -30/42. Actual in-band triangles supply contact rays; all physical meshes remain complete in collision checks. No other pebble, anatomy solver or historical design was edited.

## Primary sources

- [Feetech C001 specification](https://www.feetechrc.com/Data/feetechrc/upload/file/20240807/6385862508379674057566108.pdf), edition A/0, 2024-04-22, pages 4/6/7; unchanged local `reference/HLS3606M-C001.pdf`.
- [Pinned Aero BOM](https://raw.githubusercontent.com/Chestnut-Robotics/aero-hand-open/7bb2f23485a7d440960c21046da642de132b7745/hardware/Assembly/BOM.csv) and local `third_party/aero_hand/guide/aero_guide_original.pdf`, printed pages 31/36: spool uses three plate screws; motor-frame case screws are separate.
- [Pinned Aero STEP](https://github.com/Chestnut-Robotics/aero-hand-open/blob/7bb2f23485a7d440960c21046da642de132b7745/hardware/CAD/Aero_Hand_Open_Left.stp), extracted servo 304 / aluminum plate 248; exact local STEP hashes in `reference/provenance.json`. CAD licensing remains CC BY-NC-SA 4.0.
