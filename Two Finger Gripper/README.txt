DUAL PARALLEL GRIPPERS — ORIGINAL PARAMETRIC CONCEPT

Latest user architecture (2026-10-17): two independent parallel-jaw grippers on
one support. Each gripper has one servo, two translating jaws and its own position
and force signals. Four jaw elements and two servos total. Optional synchronization
is a command relationship; the moving mechanisms are not mechanically linked.

CURRENT: versions/v002_two_parallel_modules/gripper.scad
PREVIEW: versions/v002_two_parallel_modules/previews/two_independent_grippers.png
CHECKS:  versions/v002_two_parallel_modules/geometry_checks.json

This is a geometry and load-path study, not a finished wearable or print package.
Human finger-pocket mapping is deliberately deferred until the user clarifies
how two grippers are operated. No four-pocket human interface is assumed.
No hardware, motor, printer, watcher or deployment was operated.

VERSION HISTORY
v001_motor_force_layout: rotating thumb/index concept superseded before CAD.
v002_two_parallel_modules: two independent guide-rod/rack-and-pinion modules.
The earlier three-finger snapshot remains in the separate Three Finger Gripper
folder and is explicitly marked stopped.

WHAT IS CONNECTED
Each servo's output shaft/horn fastens to a 20-tooth, module-1.5 pinion. The pinion
engages one upper and one lower rack. Each rack is rigidly attached to one jaw
carriage. Two parallel rods constrain each carriage to X translation, so the
contact-pad faces stay parallel rather than moving through arcs.

The displayed modules have 24 mm and 58 mm pad gaps. Each supports a modeled
8–70 mm opening. Center collars stop closing at 8 mm; outer collars stop opening
at 70 mm. Repositionable fixture holes provide grasp-station separations of
100, 120, 140, 160 or 180 mm. The display uses 140 mm.

The pinion pitch radius is 15 mm. Relative to the 8 mm opening:
  gap_mm = 8 + 30 * shaft_angle_radians
The 62 mm opening range therefore requires about 118.4 degrees of shaft rotation.
This is a derived kinematic relationship, not a calibrated hardware measurement.

POSITION AND FORCE
A magnet on each output shaft and a fixed encoder-board envelope provide a
direct shaft-position sensing layout. The actual encoder and its magnet gap,
mounting, wiring, resolution and calibration are not selected.

Each of four contact pads has a separate green sensor envelope between pad and
jaw backbone. The intended load path is object -> pad -> load cell -> backbone
-> carriage -> guides/frame. There is no rigid backbone contact behind the pad
that bypasses the sensor. These blocks must be replaced by selected load cells
with correct fixed/live mounting lands, fasteners and protection from side loads.
Normal pad force is intended to be measured; friction, axial force and torque on
a long object are not measured by these single-axis sensor envelopes.

Record at least time, module ID, measured gap, left pad force and right pad force.
Do not add both opposed pad readings and label that sum as the one-side grip
force. Preserve individual readings; their mean is meaningful for balanced loads.
Servo current, if available, is an additional torque estimate rather than an
independent measurement of object contact force.

MOTOR / HUMAN-OPERATION DECISIONS STILL OPEN
Servo bodies, flanges, output horns and bolt patterns are generic placeholders.
No specific actuator, encoder, bearing or load cell is selected. A geared servo
must not be assumed smooth to backdrive. Actuator choice, transmission friction,
manual disconnection or torque-limited control must be resolved before attaching
human finger pockets. Smooth insertion geometry, emergency release and any
human-use mode are not completed or claimed by this version.

VALIDATION BOUNDARY
Run python3 versions/v002_two_parallel_modules/check_geometry.py.
The report tests every 1 mm gap from 8 through 70 mm for frame/carriage clearance,
opposed carriage clearance, rack/pinion material overlap and encoder-board
clearance. It also tests closing and opening stops separately beyond their limits.
This sampled sweep does not establish continuous collision freedom, strength,
friction, accuracy, grip capacity, comfort, printability, or electrical safety.

The source is self-contained OpenSCAD; all geometry is original. The assembly STL
contains multiple placed parts for inspection and is not a merged printable part.
No upstream CAD was copied. No commits were made.
