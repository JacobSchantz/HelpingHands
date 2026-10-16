# Demo gripper · two jaw pairs, one interface

One CAD project for voice-427220cb, slimmed in voice-a9595f6b: four
interchangeable printed jaws, one shared hub, a handheld pivot insert, and the
SO-101 servo cradle. Seven pieces. There is **no camera on the gripper**: the
robot sees the way a person does, through two stereo cameras at eye height
(`plans/hand_1_0.md`, "Mirror a human"). Yellow A is the broad
Generalist-inspired pinch; teal B is the tapered crow-inspired pinch, with a
rod seat and a gated recess. Both jaws move symmetrically. These are
prototypes, not proven grips.

The slim pass (`plans/demo_gripper_before_after.png`): each jaw is 10 mm deep
behind its gripping face (was 18) and 16 / 22 mm wide (was 24 / 32), with the
outer finger saddle dropped; the digit pad presses straight on the back of the
jaw under the strap. The hub keeps every inherited hole and cheek plane but is
trimmed to a rounded profile. The handheld kit went from about 75 to 43 cm³ of
plastic. The pivot spacing, jaw root, M3 pins, gears, 30-degree stops, horn
pattern and cradle are unchanged, so jaws still swap on the same hub.

**Four fingertip sensors, reserved not designed.** `sensor_pockets=true` cuts
two 12 x 8 x 1.2 mm seats per gripping face (four total) and a lead channel.
It is off by default and nothing is exported with it; the sensor type (most
likely force / touch) is unconfirmed.

The app discovers `export/parts.json` automatically and shows all seven pieces
in its existing Assemble/Explode viewer. A is on the hub; B is parked to the
right as the alternate pair; the arm cradle is parked behind. It is a parts kit,
not two complete grippers. The prior two designs remain available as history.
`part="pair"`, `variant="B"` in OpenSCAD shows B on the SAME hub.
`part="on_arm"` replaces the pivot insert with the cradle. Each moving jaw is
its own STL. `render/` includes both hand poses and B on the arm.

## Print and assemble

Use `jaws_print_ready.zip` for the four jaw STLs already laid on their flat
Y=-5 side, at Z=0. The files in `export/` are positioned for the app assembly;
do not print them all together. Jaw roots, gear sectors and through strap
slots grow vertically in the print orientation; no designed supports or
print-in-place hinges. Inspect the slicer before printing. Start with PLA,
0.2 mm layers, four walls and 35% infill as an untested starting recipe.
One 20 mm hook-and-loop strap per jaw threads through a 22 × 3 mm slot and
wraps the digit on the flat outer face (thumb on the 16 mm jaw, index + middle
on the 22 mm jaw). It is not sized for four fingers. Rounded fabric, fit and actual pressure points need a hand test.

Print one jaw pair first, then the hub and handheld insert.
Lay the hub on its bridge; its 24.5 mm horizontal horn opening may need local
support.
Lay the cradle on its wrist puck; the horn recess and screw access may also
need local support. The insert prints on its outer flange. Only the four jaws
are designed here for straightforward support-free printing.

Hardware (not printed): two M3 pivot bolts with washers/locking nuts, M3 hub
fasteners, and two straps. Trial-fit
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

## Vision and demonstration contract

No camera rides on the gripper, in the hand or on the arm. Vision comes from
two binocular (stereo) cameras at roughly human eye position: worn at eye
height by the demonstrator, mounted at head height on the robot. That matches
how a person sees their own hand, and it removes the camera from the wrist
cable and the payload. Same lens, baseline and jaw pair across demonstration
and robot. A and B are distinct tool IDs, not interchangeable examples.

This change adds no capture software, jaw encoder, IMU or tracker. The jaws
must be visible to the head cameras; real hands can hide them, which is the
same occlusion a person works around by moving their head. Record tool ID,
stereo intrinsics/extrinsics, timestamps, hub pose and measured right-jaw
angle. The left follows with opposite angle. In the shared frame, +Z points to
the tips, X opens the jaws, Y is the pivot axis, and pivots are at X=±12 mm.
At reference Z=52 the bare face separation is
`2*(12 - 11.6*cos(angle) + 52*sin(angle))` (degrees).
Tip Z is 72 for A and 84 for B. Recalibrate SO-101 gripper limits for the
geared transmission; old crow/stock servo limits are not reusable.

No print, ergonomic fit, grasp, force, payload, calibration or data-transfer
result is claimed here. The translucent hand and fabric in renders are
positioning sketches only.

## Reproduce the CAD checks

`python3 cad/openscad/demo_gripper/export.py` generates CAD assets only.
It never invokes an app build, install or deploy. OpenSCAD defaults to the
macOS app executable; override `OPENSCAD` for another installation.
`python3 cad/openscad/demo_gripper/validate.py` requires NumPy and checks
watertight, consistently wound, single-solid meshes; flat jaw bed contact;
both pairs' motion clearance; tooth engagement and stops as positive controls;
fixed-part and insert clearance; and the existing app manifest's seven distinct parts.
The underlying shared modules live in `../hand_gripper/hand_gripper.scad`.
Changes to those modules require rerunning these checks and exports.
