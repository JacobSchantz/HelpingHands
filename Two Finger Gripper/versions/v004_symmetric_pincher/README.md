# Generalist Gripper · Generation 4

A simpler, centered thumb/index pincher: one opposing pair of mirrored jaws,
one centered servo envelope, one sliding yoke and one crank. Generation 3 is
preserved in `../v003_single_pincher`; no earlier version is replaced.

This is original inspection CAD, not a print-ready or hardware-tested wearable.
No motor or other hardware was operated. The motor, horn, bearings, fasteners,
materials and human fit remain unselected.

## Changes requested for this generation

- Six main displayed bodies instead of Generation 3's twelve: fixed hub, two
  jaws, yoke, crank and ONE servo envelope. Required small hardware is still
  unfinished; six is not a complete assembly bill of materials.
- Identical mirrored jaws and centered fixed hub, yoke and motor volume.
- Continuous curved inner object-contact faces, without a separate black pad,
  sensor block or lightening holes in the contact surface.
- Longitudinal concave channels on the OUTER, human-facing sides, running from
  near the tips toward the pivots. These differ from the inner object-gripping
  faces. They are open channels, not hard finger rings.
- Two radiused zip-tie anchor slots per jaw, through the Y sidewalls near the
  outer spine. The slots do not break the inner gripping face. No purple straps,
  ties, finger cuffs or force sensor are rendered.

The compact opposing-finger silhouette is informed by official Generalist
reference frames already saved in `references/generalist/` in the project root:
`human_jar_01.png`, `human_brush_01.png`, `screwhand_1.jpg` and `ziptie_1.jpg`.
The [official human jar demonstration](https://generalistai.com/assets/pages/blog/gen-1.5/assets/videos/top_down_human_jar.mp4)
shows human operation. The box-folding footage is robot-mounted and is not
human-attachment evidence. The transmission and dimensions here are our own
proposal; the footage does not establish Generalist's hidden mechanism or fit.

## Centered drive and real symmetric motion

The servo output axis is on X=0, Z=-30, pointing along Y. An eccentric crank pin
moves in the yoke's horizontal slot. The hub's open-front L guides constrain the
yoke to vertical translation. Two mirrored angled slots in the yoke engage rear
followers integral with the jaws. The jaws pivot on X=+/-16 and counter-rotate
by equal angles. There are no jaw gears, extra links or second motor.

For jaw opening angle `a` (degrees), 0–22:

```
right follower X = 16 - 10*cos(a) - 10*sin(a)
right follower Z = 10*sin(a) - 10*cos(a)
yoke translation t = 2 + 20*sin(a)
right slot: Z - t = X - 18
left slot:  Z - t = -X - 18
crank angle phi = asin((t - 5.746065934)/6)
```

The crank runs about -38.63 to +38.63 degrees, away from its +/-90 degree
vertical-motion dead centers. Both follower slot and crank slot ends retain
clearance throughout the sampled interval. One crank input sets the yoke and
both jaw angles; they are not independently actuated.

The jaws, yoke, fixed hub and motor envelope are bilaterally symmetric in X.
The single eccentric crank pin is an inherently asymmetric internal feature
as it rotates. It is behind the centered assembly, not a fictitious mirrored
second motor. Perfect symmetry is not claimed for every internal moving feature.

## Closure, smooth contact and finger fit

At a=0 the curved tips approach to approximately 1.14 mm nominal clearance;
they do not intersect or form an ideal zero-gap tweezer. The main inner face is
roughly 2–4.4 mm apart in this pose. Larger opening angles increase separation.
At the reference local point X=-14.8, Z=60, the derived gap is
`2*(16 - 14.8*cos(a) + 60*sin(a))`: 2.4 mm at zero and about 34.47 mm at 15 degrees.
The actual curved face has a varying separation. Servo encoder calibration,
backlash and compliance have not been measured.

The outer grooves follow the jaw length. Both use the SAME placeholder radius
10 mm and 3 mm depth, with 18 mm jaw thickness along Y. This deliberately
preserves mirror symmetry; it is not evidence that a thumb and index finger
have identical size. Adjust only after measuring the intended hand. There is
no shaft through either finger channel.

The anchor slots are approximately 2.8 by 4.8 mm for nominal 3 mm ties. They
provide attachment options, not a proven human restraint. Do not cinch bare
zip ties tightly on fingers; use them as anchors for removable soft tabs with
a quick release. No powered fit test has been performed.

## Assembly and unresolved hardware

The jaws have diameter 3.4 through-bores for two unselected pivot pins. The
follower studs are integral CAD features, diameter 3, running in 3.5-wide yoke
slots. Their wear, strength, friction and printing orientation are unvalidated.
The yoke is 4 mm thick at Y=-14. Guide clearance is 0.3 mm to each side and
0.3 mm at the rear. Guides are open at the front so the yoke can be inserted
along Y; it is not trapped behind integral end stops during assembly.

The crank pin also needs a selected removable axial retainer to prevent the
yoke lifting away from the open-front guides. Pivot pins need retention too.
These small hardware parts are NOT included in the six-body viewer. Loading
or backdriving this incomplete assembly is not supported. The hub's integral
stops limit yoke travel just outside the modeled 0–22 degree interval; stop
strength has not been validated.

The centered black servo body is a 36 by 32 by 30 mm envelope, not a selected
motor or mount. The crank has an undrilled/unsplined blank interface and an
unselected 2.5 mm pilot. Its 10 mm rear boss has 0.2 mm nominal radial clearance
in the hub. Actual servo spline/horn geometry, attachment holes, torque transfer,
mounting and retention MUST replace these placeholders. This is not a claimed
HLS3606M, STS3215 or other manufacturer's interface.

## Position, backdrive and force

There is no force transducer in Generation 4: both pinch force and operator
input effort are UNMEASURED. Removing the separate pad simplified this version;
backdrive alone cannot produce a force measurement. Motor current, if available,
is a model-dependent torque estimate, not an independent measured contact force.
If force is required, select a real transducer and define its load path before
adding its geometry or reporting force data.

The yoke has two sliding cam contacts plus guides. Their friction and the
unknown servo gearbox can resist hand operation. A centered layout and absence
of extra gearing do not prove smooth backdrivability. Confirm the actual motor,
output readback, torque-off behavior and power-off resistance before a wearable
build. No load capacity, force accuracy, comfortable fit or safe actuator torque
is claimed.

## Files and verification

- `gripper.scad`: self-contained parametric source, default assembled pose 15°.
- `exports/assembly.stl`: assembled inspection mesh, NOT one printable object.
- `exports/jaw.stl`: common raw jaw; mirror and place for the opposite side.
- `exports/parts/*.stl`: six real design bodies/envelopes at ASSEMBLED world
  coordinates. `viewer_parts.json` supplies names, colors and authored explode
  offsets in mm for the existing gallery's Explode/Assemble control.
- `previews/`: colored assembled, front, closed and finger-channel views.
- `python3 check_geometry.py`: bounded numerical constraints plus exact-solid
  intersections at 45 poses (0–22° every 0.5°), physical stop overrun positive
  controls, mirrored jaw and fixed hub symmetry checks. Hub symmetry subtraction
  accepts only numerical residue below 1e-8 mm³; free-motion checks require
  an empty solid. Results: `geometry_checks.json`.
- `python3 export_models.py`: reproducible STL exports, closed-edge incidence,
  consistent winding and connectivity checks in `mesh_checks.json`. Each
  individual body must be one connected closed mesh. `export_checks.json`
  captures OpenSCAD status.

These checks are sampled CAD/topology checks, not a continuous motion proof,
tolerance analysis, print trial, fatigue test, calibration or hardware validation.
Stop at this generation for review before adding complexity.
