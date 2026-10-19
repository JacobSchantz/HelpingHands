# Generalist Gripper · Generation 5

One shared parametric jaw design, mirrored into one opposing pair, with direct
1:1 jaw gears. ONE servo drives one jaw through ONE plastic adapter; the second
jaw follows through the gear mesh. No crank, yoke, extra links, center pinion,
force pad, sensor, straps or rigid finger cuffs. Generation 4 is preserved.

There are five main displayed parts: hub, left jaw, right jaw, adapter and servo
envelope. Necessary small retention hardware and the real motor mount are not
finished, so this is not a complete bill of materials or a print-ready assembly.
No motor or other hardware was operated.

## One editable jaw and the tooth-phase exception

`jaw(gear_phase)` is the ONLY jaw module. The outline, tip taper, deep finger
channel, tie slots, round pivot bore and rear hex socket share the same source
on both sides. Editing them updates both. There is no left sensor variant or
right-only socket variant. The follower's rear socket is intentionally unused.

The finger bodies and bores are exact mirror images. The only handed exception
is the gear-tooth phase: 0° on the right, half a tooth pitch (7.5°) on the left.
A completely mirrored external gear pair would put tooth material against tooth
material; the timing offset puts one gear's teeth in the other's spaces. Both
fingers retain symmetric installed angles. A center pinion driving two external
gears would turn both the same way, so none is added.

**The two STLs are automatically derived from one source, but they are NOT an
identical part to print twice.** Print/use the correctly indexed left and right
exports. The shared body is reflected for the left, while the tooth timing is
adjusted explicitly. No duplicate hand-edited finger geometry exists.

## Close reference to the actual Generalist imagery

The designer actively re-viewed these official images during this generation:
`references/generalist/screwhand_1.jpg`, `ziptie_1.jpg`, and the actual human-
operated `human_jar_01.png`, relative to the HelpingHands project root. The
[official human jar clip](https://generalistai.com/assets/pages/blog/gen-1.5/assets/videos/top_down_human_jar.mp4)
is human-operation evidence; the box-folding clip is robot-mounted.

Observed reference features: slender arched yellow fingers, long narrow taper,
small pointed but rounded ends, and compact roots at a black housing. Compared
with Generation 4, this model narrows the body, extends the taper, reduces width
along Y near the tip, replaces the broad paddle end with a small rounded curve,
and removes the tall slider frame. The reference's honeycomb/compliance, black
tip material, hidden drive and sensing are not assumed to be reproduced. Our
direct gears, finger channel and hardware interfaces are original proposals,
not reverse-engineered or copied proprietary CAD.

## Groove, gripping faces and near closure

The OUTER surface is for the human finger. Its continuous lengthwise concave
channel is 5.5 mm deep through the main finger region (Generation 4 was 3 mm).
The nominal channel radius is 8 mm. Near the tapered tip it blends to radius
6 mm and depth 3 mm, preserving side lips and a closed end before the tip.
It runs from near the gear toward the tip; it is not a crosswise finger hole.
All dimensions are placeholders, not a measured thumb/index fit.

The INNER face contacts the object. It is a continuous smooth curve without a
separate pad, sensor or tie hole breaking through it. Two 2.8 by 4.8 mm radiused
slots per jaw pass through Y near the outer spine, for nominal 3 mm anchor ties.
No ties are rendered. Do not cinch bare ties tightly around fingers; use them
as anchors for removable soft tabs with a quick release. Fit is unvalidated.

The jaw width is 18 mm along Y through the main body and tapers to about 8.4 mm
near the tip. The modeled groove is checked against a protected 3 mm band toward
the inner contact profile and 1 mm side-wall bands. These are geometric minimum
clearances, not strength or comfort results. Intentional tie apertures and the
solid final tip are not claimed as uniformly 3 mm thick everywhere.

At zero opening the inward tips have approximately 1.3 mm nominal clearance,
not an ideal zero-gap tweezer. At reference local X=-12.7, Z=60 the gap is
`2*(14.4 - 12.7*cos(a) + 60*sin(a))`: 3.4 mm at 0°, 35.32 mm at 15°.
The actual curved face has varying separation. The rounded tip is not a needle.

## Direct drive, pivots and unfinished retention

Each jaw gear has 24 teeth, module 1.2, pressure angle 20°, pitch radius 14.4 mm,
face width 5 mm. Pivot spacing is 28.8 mm. Equal gears counter-rotate 1:1 from
0–22°. Integral tabs and fixed hub shoulders provide modeled travel stops just
outside that range; their strength is not validated.

Load path: servo output/horn -> plastic adapter -> common rear hex socket in
the right jaw -> right gear -> left gear. There is no added reduction or
intermediate gear. The drive axis is honestly offset to the right jaw's pivot;
the single black motor body is also offset. Centering it with another external
pinion would break the desired opposing motion, and extra idlers would add parts.
The mirrored jaws and compact hub are centered; the complete motor package is
not perfectly bilaterally symmetric.

Both jaws have diameter 3.4 round bores plus the same 6.3 mm-across-flats rear
socket (6 mm nominal adapter, 0.3 mm total flats clearance). The passive jaw
can be inserted between the hub cheeks and retained by a selected shoulder pin
through the front and rear 3.4 mm hub holes. A head/nut or equivalent retention
must capture the pin without clamping the rotating jaw. No shaft enters the
human finger channel. Jaw sides are Y=+/-9; hub cheek inner faces are +/-10,
leaving 1 mm nominal axial room per side.

On the driven side the adapter's 10 mm rear journal runs in the hub's 10.4 mm
bore, and its hex enters the shared jaw socket. It ends 0.3 mm behind the jaw
body so its larger journal does not interfere with the socket mouth. A selected
front rotating shoulder retainer can pass through the front cheek/jaw and engage
the adapter's blind pilot; its head/shoulder must retain the assembly without
clamping the stationary hub. The selected horn/motor mount must retain the rear.
These pins, retainers, bearings/washers and mount fasteners are NOT modeled or
selected. Without them the CAD is not a captive functioning mechanism.

The adapter flange is undrilled and unsplined; its front pilot is 2.5 mm, not a
qualified thread. The ONE motor volume is 36 by 38 by 30 mm with an unselected
shaft envelope. It is not a claimed HLS3606M, STS3215 or other motor's interface.
Actual horn/spline dimensions, fastener locations, torque transfer, bearing fits,
axial stack and case mounting must be completed for the selected hardware.

## Position, backdrive and force remain unvalidated

The ideal right jaw angle follows servo output angle 1:1 and the left follows
oppositely. Actual output readback, zero, backlash and compliance require
measurement. Equal direct gears do NOT make an unknown geared servo smoothly
backdrivable. Gear friction, bearing friction, cogging and power-off/torque-off
behavior remain unknown; no powered human fit test or hardware motion was run.

There is no force sensor in this generation. Object pinch force and operator
input effort are UNMEASURED. Backdrive does not itself provide force sensing;
motor current would be a model-dependent torque estimate. Choose a real sensor
and its load path before reporting measured force. No payload, calibrated force,
safe torque, printability, wear life or comfortable fit is claimed.

## Files and meaningful bounded checks

- `gripper.scad`: self-contained source; `jaw(gear_phase)` is shared.
- `exports/assembly.stl`: assembled inspection mesh, not one printable object.
- `exports/left_jaw.stl`, `right_jaw.stl`: correctly phased raw jaw exports.
- `exports/parts/*.stl`: five design bodies/envelopes at ASSEMBLED world
  coordinates. `viewer_parts.json` provides names, colors and authored explode
  offsets in mm for the existing gallery.
- `previews/`: assembled, centered front, near-closed and channel detail PNGs.
- `python3 check_geometry.py`: samples 45 poses (0–22° every 0.5°), checks
  rigid-part clearance, nominal gear non-overlap, and gear engagement by requiring
  positive overlap with intentional +/-1° follower misphase at EVERY sampled
  pose. Also checks protected groove walls, shared mirrored finger geometry,
  adapter/socket clearance and physical stop overruns. `geometry_checks.json`
  records the exact scope. The phase check is not measured manufactured backlash.
- `python3 export_models.py`: reproducible exports plus closed-edge incidence,
  winding, volume and connected-component checks. Each individual part must be
  one closed connected mesh. Results are `mesh_checks.json` and `export_checks.json`.

These are bounded CAD/topology checks, not a continuous motion proof, tolerance
stack analysis, strength test, fit trial, print test or hardware calibration.
