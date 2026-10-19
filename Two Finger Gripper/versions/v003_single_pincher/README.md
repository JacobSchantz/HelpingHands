# Generalist Gripper · Generation 3

One opposing thumb/index pincher, one coupled opening motion and one servo
interface. This is original OpenSCAD geometry for inspection, not a validated
wearable, calibrated force instrument or print-ready package.

The useful earlier gallery designs are Generation 1 (the original
`cad/openscad/demo_gripper/gen_00_slim_two_pairs.scad`) and Generation 2
(`gen_01_finray_tpu.scad`). Those files are preserved. This generation replaces
neither of them. The first, larger rack/rail draft of this version is retained
under `studies/00_parallel_rack`; it is not the current design.

## Reference and design choices

The [official Generalist homepage](https://generalistai.com/) shows tapered
yellow opposing fingers on a compact black central mount. Actual human-operated
footage is in [Generalist's GEN-1.5 jar demonstration](https://generalistai.com/assets/pages/blog/gen-1.5/assets/videos/top_down_human_jar.mp4).
Local reference frames are `references/generalist/human_jar_01.png` and
`human_brush_01.png` in the project root. The box-folding clip is robot-mounted
and is NOT evidence for human attachment.

This design adopts the compact two-finger form, curved taper and lightened
spines. The geared pivots, sensor provision and strap arrangement are our own
mechanical proposals. Images do not establish Generalist's hidden transmission,
sensing, dimensions, materials or attachment details. No proprietary CAD was
copied, and no hardware/CAD licence is claimed for their imagery. No camera is
added: the existing project preference for head-height vision remains intact.

## What moves and what attaches to the hand

Two equal 20-tooth, module-1.2 gears counter-rotate the two jaws. The right/index
pivot is driven through a removable hex adapter; its undrilled flange must be
adapted to the chosen servo horn. The thumb jaw follows through the gear mesh.
There is one degree of freedom, one opposing jaw pair and ONE motor envelope.
These are angular jaws; their contact planes do not stay parallel.

Finger pads press into shallow outer saddles, entering along the open Y axis.
The saddles have flared entrances, no closed ends and no rigid finger rings.
Each jaw has four radiused zip-tie anchor slots. Zip ties attach fabric tabs;
use removable hook-and-loop or similarly releasable soft straps around the
fingers. Do not cinch plastic ties directly on a finger. The purple broken
bands are only soft-strap envelopes, not printable cuffs or proven fit.

The free thumb pivot uses a nominal M3 shoulder-pin clearance. The driven jaw
has a 6 mm front journal in the hub, a rear hex coupling and a separate small
front retainer pilot. The output shaft does not pass through either finger
saddle. Stop tabs meet fixed hub shoulders just beyond the sampled 0–22 degree
range; the overrun checks are at -0.5 and 22.5 degrees. Nothing establishes
stop strength, retention, bearing life or a safe actuator torque.

## Placeholder dimensions, mm

- Pivot spacing: 24; gear pitch radius: 12; tooth face width: 5.
- Rigid jaw thickness along Y: 18; fingertips reach Z=88 before opening.
- Thumb saddle radius: 16; index saddle radius: 13. These are adjustable
  placeholders, not measurements or a claim of anatomical fit.
- Saddle entrance flare: 1.2 over 2.2 depth at each open end.
- Tie slots: approximately 4.8 by 2.8; intended for nominal 3 mm anchor ties.
- Hub cheek inner planes: Y=+/-10; jaw ends: Y=+/-9 (1 mm nominal axial room).
- Free pivot clearance: diameter 3.4; driven front journal/bore: 6/6.4.
- Own hex adapter: 10 across flats, 0.3 nominal socket clearance. This is NOT
  an HLS3606M, STS3215 or other manufacturer's spline/horn specification.
- Motor volume: 36 by 40 by 30, unselected. The depicted body and flange are
  envelopes only; motor retention and the horn fastener pattern are unfinished.
- Local sensor contact patch: 18 by 22; nominal force-cell envelope: diameter
  8 by 4 long; contact face at local X=-10, cell seat at X=-3.

At the reference patch centre Z=50, the nominal opposed face separation is:
`gap_mm = 2 * (12 - 10*cos(angle_deg) + 50*sin(angle_deg))`.
That is 4.00 mm at 0 degrees, 35.88 mm at 18 and 42.92 mm at 22.
The curved tips have a different separation. This is CAD kinematics, not a
measured or calibrated servo reading.

## Backdrive and sensing: what is and is not measured

There is no extra reduction between the servo output and driven jaw, and the
jaw-to-jaw ratio is 1:1. That does NOT make an arbitrary geared servo smoothly
backdrivable. The actual motor is unconfirmed. Its gearbox friction, cogging,
output torque, encoder/readback, power-off behaviour and torque-off mode must
be checked before making a human-operated assembly. No motor or other hardware
was actuated for this design.

The green envelope reserves a real compression sensor behind the floating thumb
contact patch. Intended normal load path: object -> floating contact pad ->
compression cell -> jaw -> pivot/hub. Two shoulder-guide fasteners retain the
pad, with heads recessed 0.6 behind the contact plane. They must allow axial
float rather than clamping the pad rigidly. There is no modelled rigid pad-to-
jaw contact bypass. Sensor mounting, preload, overload protection, guide friction,
wiring and calibration still require a selected part.

This provision measures ONLY local normal contact force on that patch. It does
not measure operator input/backdrive effort, shear, torsion, or contacts on the
other exposed parts of the curved finger. An empty pincher can resist the
operator through motor friction while this object-contact sensor reads zero.
If the desired signal is finger input force, place a separate transducer under
the human saddle or use a selected shaft torque transducer; do not relabel
motor current or this pad signal as that measurement. Motor current is a
model-dependent torque estimate, not an independent contact-force measurement.

Record the selected tool/version, time, actual measured output angle, derived
patch gap and calibrated patch force. Servo selection and the exact desired
force signal remain open; no force accuracy, payload or fit result is claimed.

## Files and checks

`gripper.scad` is self-contained. `part` selects assembly, hub, thumb, index,
sensor_pad or adapter. Component STLs retain their design coordinates; the
assembly STL includes placed parts and hardware/soft-strap envelopes for review.
It is NOT a file to print as one object. Use the coloured PNG previews to see
part roles. No assembly instruction here substitutes for a hardware fit review.

Run `python3 check_geometry.py`. It samples 0–22 degrees every 0.5 degrees for
solid interference and gear overlap, checks the two stop overruns as positive
controls, and checks pad/sensor material clearance. The JSON records exact scope
and limitations. Passing these checks is not a continuous motion proof or a
strength, print, backdrive, human-fit, force or endurance validation.

Next hardware work: confirm motor and horn; choose pivots/bearings and sensor;
complete the motor mount and fastening; verify clearances with coupons; test
power-off motion/strap release without wearing powered hardware; then calibrate
position and sensor response with known loads at the intended contact patch.
