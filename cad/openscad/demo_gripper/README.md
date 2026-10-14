# Demo gripper · two jaw pairs, one interface

One CAD project for voice-427220cb: four interchangeable printed jaws, with one
shared hub, camera bracket, handheld pivot insert, and SO-101 servo cradle.
Yellow A is the broad Generalist-inspired pinch; teal B is the tapered
crow-inspired pinch, with a rod seat and a gated recess. Both jaws move
symmetrically, including B: this deliberately replaces the old crow's fixed
upper jaw and separate dovetail mount. These are prototypes, not proven grips.

The app discovers `export/parts.json` automatically and shows all eight pieces
in its existing Assemble/Explode viewer. A is on the hub; B is parked to the
right as the alternate pair; the arm cradle is parked behind. It is a parts kit,
not two complete grippers. The prior two designs remain available as history.
`part="pair"`, `variant="B"` in OpenSCAD shows B on the SAME hub and camera.
`part="on_arm"` replaces the pivot insert with the cradle. Each moving jaw is
its own STL. `render/` includes both hand poses and B on the arm.

## Print and assemble

Use `jaws_print_ready.zip` for the four jaw STLs already laid on their flat
Y=-5 side, at Z=0. The files in `export/` are positioned for the app assembly;
do not print them all together. Jaw roots, gear sectors and through strap
slots grow vertically in the print orientation; no designed supports or
print-in-place hinges. Inspect the slicer before printing. Start with PLA,
0.2 mm layers, four walls and 35% infill as an untested starting recipe.
The narrower thumb saddle and wider index/middle saddle replace hard sleeves.
One 20 mm hook-and-loop strap per jaw threads through a 22 × 3 mm slot and
wraps the digit on the outside. The saddle is 2.5 mm deep. It is not sized for
four fingers. Rounded fabric, fit and actual pressure points need a hand test.

Print one jaw pair first, then the hub, camera bracket and handheld insert.
Lay the hub on its bridge; its 24.5 mm horizontal horn opening may need local
support. The angled camera bracket needs slicer-selected support.
Lay the cradle on its wrist puck; the horn recess and screw access may also
need local support. The insert prints on its outer flange. Only the four jaws
are designed here for straightforward support-free printing.

Hardware (not printed): two M3 pivot bolts with washers/locking nuts, M3 hub /
camera fasteners, two straps, camera board and M2 camera fasteners. Trial-fit
bolt lengths with the washer stack; never clamp a moving jaw solid. Use smooth
shanks at the pivots. The handheld insert seats in the large horn opening and
is keyed by the +X bridge screw; it adds a second bearing for the driven jaw.
The jaws have 0.4 mm axial clearance per cheek and a nominal 0.8 mm closed
face gap. Add approximately 0.5 mm compliant grip tape per face and check
compression/closed calibration before testing paper. Tape is consumable,
not included in the CAD exports; do not infer paper grip from bare CAD.

For the arm, remove the insert and the driven pivot bolt, bolt the shared
cradle to the hub and wrist, fit the servo, then attach its horn to the right
jaw. Four M3 holes on a 9.9 mm square and the 24 × 6 mm wrist horn recess are
inherited from the repository's SO-101 interface. The 45.2 × 24.7 × 35 mm
servo case, shaft location, screw locations, and horn stack remain UNMEASURED
assumptions inherited from the earlier design. Measure your servo and horn
before printing the cradle; this is an adaptation design, not a verified fit.
The two 30-degree jaw stops and straight-flank gears are retained. Root fill
was extended to 10.35 mm radius here because faceting left some original
half-phase teeth disconnected; every exported piece is checked as one solid.
No load rating or gear lifetime is established.

## Camera and demonstration contract

The camera is raised and moved forward from the earlier design: ray tests
found its rearward position hid open jaw tips behind their gripping faces.
The same physical camera bracket stays on the hub when moving between hand
and arm; do not re-mount the board. Board center is (0,65,20) mm, aimed at
(0,0,60), with a 32 mm board and 28 mm mounting-hole square. These camera
sizes are assumptions. Use the same lens, focus, resolution, jaw pair, tape
and angle zero for a matched hand/robot pilot. A and B are distinct tool IDs,
not interchangeable training examples with identical contact geometry.

The camera bracket is an RGB mounting interface, not a tracking system.
This change adds no capture software, jaw encoder, IMU or phone tracker.
Follow the QC/retargeting workflow in `plans/handheld_gripper.md`; its rigid
phone mount and trigger-servo assumptions do NOT hold for this direct pinch.
A calibrated external pose tracker / visual pose pipeline and synchronized
jaw-angle measurement must be supplied before collecting training episodes.
Do not silently substitute RGB for measured pose or command for measured angle.
An unpowered servo is not assumed easy to back-drive; free-hand mode removes it.

Record tool ID, camera intrinsics, camera-to-hub transform, hub-to-wrist
transform, timestamps, measured hub pose and measured right-jaw angle. The
left follows with opposite angle. In the shared frame, +Z points to the tips,
X opens the jaws, Y is the pivot axis, and pivots are at X=±12 mm. At reference
Z=52 the bare face separation is
`2*(12 - 11.6*cos(angle) + 52*sin(angle))` (degrees).
Tip Z is 72 for A and 84 for B; use each tool's own fingertip transform and
pad thickness when retargeting. Recalibrate SO-101 gripper limits for the new
geared transmission; old crow/stock servo limits are not reusable.

Before a dataset pilot: measure servo fit and mass; check full travel under
hand force and then limited servo torque; check camera visibility with real
hands, straps and objects; calibrate intrinsics/extrinsics and measured angle;
run the same small pick/place task handheld and on the arm, comparing tracking
loss, timing, endpoint error and success. No print, ergonomic fit, grasp,
force, payload, camera calibration or data-transfer result is claimed here.
The translucent hand and fabric in renders are positioning sketches only.

## Reproduce the CAD checks

`python3 cad/openscad/demo_gripper/export.py` generates CAD assets only.
It never invokes an app build, install or deploy. OpenSCAD defaults to the
macOS app executable; override `OPENSCAD` for another installation.
`python3 cad/openscad/demo_gripper/validate.py` requires NumPy and checks
watertight, consistently wound, single-solid meshes; flat jaw bed contact;
both pairs' motion clearance; tooth engagement and stops as positive controls;
fixed-part and insert clearance; and the existing app manifest's eight distinct parts.
`python3 cad/openscad/demo_gripper/check_camera.py` tests unobstructed rays to
both tips at 0, 14 and 29.5 degrees, for both tools, bare and with the schematic
hand/straps or arm cradle. It assumes at least 70 degrees usable field in BOTH
image axes after cropping. That is a lens requirement, not a calibrated camera
claim. Real hands, wiring, straps and objects can introduce additional occlusion.
The underlying shared modules live in `../hand_gripper/hand_gripper.scad`.
Changes to those modules require rerunning these checks and exports.
