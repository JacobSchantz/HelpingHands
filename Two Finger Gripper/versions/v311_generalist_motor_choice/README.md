# Generalist Gripper · Base 11: motor choice, RS00 or STS3215 (Gripper 21, no separate Handle)

voice-e82254ec. Jake: *"Add an optional motor variant to the gripper: the gripper base can alternatively be driven by the SO-101
arm's motor, the Feetech STS3215 servo, instead of the RobStride RS00. Make the motor a selectable parameter (motor = RS00 |
STS3215) with the right mount, gear or horn interface and cable routing for each, built on the latest Base … Also record joint
positions from the STS3215 servo while the gripper is used by hand, for data collection."*

Base 11 is Base 10 (`v310_generalist_arm_mount`) with one new switch in `params.json`, **`motor_sts`** (a 0/1 slider on the Tune
panel; the params are numbers only, so it is not a string):

- **`motor_sts 0` = RobStride RS00.** Base 10 exactly, wrist mount and arm included (each print STL has the same triangles as
  Base 10's; checked by rendering both).
- **`motor_sts 1` = Feetech STS3215** (the SO-101 servo). This is what Base 11 exports and shows by default.

**The STS3215** is The Robot Studio's own CAD (SO-ARM100 `STEP/SO100/STS3215_03a.step`, Apache-2.0), measured with OCCT: case
45.4 × 24.8 × 31.8, output axis 10.2 from the near end, round horn Ø20 with 4 × Ø2.5 holes on Ø14 (M3) and an M3 centre screw,
an idler horn on the back, 4 M2 holes in two rails on the front face either side of a 1.1 mm label hump, two 3-pin bus
connectors in a block on the back face. 30 new params in *Motor: Feetech STS3215 (Base 11)*, all on the Tune panel.

- **Horn interface (the pinion).** The same 34-tooth pinion, meshing the right handle-gear as before, but its spigot (Ø19.5)
  sits on the horn's top face and 4 countersunk M3 go down into the horn's 4 holes (SO-101: *"4 M3x6"* into the horn). A
  recess in the spigot clears the horn's centre screw head. Ratio 1:1, so the servo turns 30° for 30° of finger swing.
- **Mount (the base).** The base's underside sits on the servo's two rails, and 4 M2 go down through it into the case (SO-101:
  *"M2x6"* into the case; here M2x8, heads in 2 mm recesses so they stay under the handle-gears). The hump stands up into a
  window cut straight through the base, and the horn turns in the base's centre hole, so the underside stays one flat face on
  the bed: no bridge, no support. The window runs out of the base's lower edge, so the base is a U round the servo's far end.
  The servo's body runs straight down from the pinion (`sts_body_deg` −90), away from the gears: it adds nothing to the width.
- **Cable.** The bus cable plugs into the back face and leaves straight back, away from the base, to the bus adapter
  (`sts_plug_len` 14 mm of plug and bend kept clear of every part at every swing). No reBot wrist mount on this motor: the
  bracket bolts to the RS00's back face, and an STS3215 gripper is hand-held (or goes on an SO-101; that adapter is not drawn).

**Recording by hand: `record_grip.py`.** Torque off, the fingers back-drive the servo and it is read as an encoder through
LeRobot's Feetech bus (the SO-101 one, raw counts, no LeRobot calibration needed): 11.4 counts per finger degree at 34:34.

```bash
conda activate lerobot          # robot_config.md; a native Terminal, as for teleop
python3 record_grip.py --port /dev/tty.usbmodemXXXX --id 1     # close the fingers, Enter, use it; Ctrl+C -> recordings/grip_<time>.csv
python3 record_grip.py --fake --duration 3                     # no hardware: a synthetic open/close
```

Columns `t_s, raw, servo_deg, finger_deg` (each finger's swing from closed, 0–30). `--invert` if opening reads negative,
`--zero <count>` to reuse a closed reading. A new STS3215 is ID 1; the SO-101's gripper motor is ID 6.

Pieces with the STS3215: **7 printed** (2 fingers, 2 handle-gears, pinion, base, top plate) + STS3215 + 4 M3 (horn) + 4 M2
(case) + 3 M3 (pillars) = **19** (Base 10 on the RS00: 11 printed + RS00 + 26 M3).

![servo side](previews/servo_side.png)
![servo iso](previews/servo_iso.png)
![servo seat](previews/servo_seat.png)
![print bed](previews/print_bed.png)

Checks: `python3 export_models.py && python3 genus.py && python3 check_geometry.py` check the motor `params.json` picks. With
the STS3215: Base 9's 50 plus 9 for the servo: the base sits on the rails (pushed 0.5 mm in, it hits); shifted 0.5 mm across,
the hump and horn hit the base (held); the M2 heads sit in their recesses, below everything that turns at 0–30°; the M2s
reach the case; the bus cable's plugs and bend are clear of every part at every swing. The generic drive checks now run on the
servo: the pinion's spigot sits on the horn, nothing that turns hits the base or servo, the horn screws clear the pinion's
holes. 59/59 pass. Genus: pinion 4, base 7. With `motor_sts 0` the checks are Base 10's 71.

## Not verified

No STS3215 was in hand: every number is The Robot Studio's STEP. Its label hump overlaps the horn's rim by 1.1 mm in that STEP,
so the model cuts the hump round the horn (the real case must already clear it). The M2 holes' depth in the case is not known;
M2x8 leaves 4 mm. Back-driving: the SO-101 follower's STS3215 (C001, 1/345) is stiff by hand; its leader arm uses the
C046 (1/147) and C044 (1/191), made to be moved by hand (SO-ARM100 BOM), and those are the ones to buy for a hand-held recorder. No torque, stall,
backlash or reading-rate test: `record_grip.py` ran only with `--fake` (and LeRobot's bus built without a port). The far M2
holes sit 2 mm from the base's edge. Tuning `motor_sts` to 0 in the preview draws the RS00 drive without the wrist mount
(the exported part list is the STS3215's).

Base 10's notes follow.

# Generalist Gripper · Base 10: on the reBot Arm B601-RS (Gripper 21, no separate Handle)

voice-3cd78d20. Jake: *"Make our gripper attach to the Seeed reBot Arm B601-RS … bolts onto the arm's wrist / end-effector flange in
place of the stock reBot gripper … match its bolt pattern and how the stock gripper mounts … prints without supports, with the RS00
cabling routed cleanly."* Then: *"Bring the arm CAD into the repo … so the arm shows in the live preview"* and *"a mount base on the
arm's end flange that takes BOTH … our two-finger gripper and the Aero Hand … one common arm-side flange adapter with swappable
tool-side interfaces."*

Base 10 is Base 9 (`v309_generalist_top_plate`) plus a wrist mount. The gripper itself is unchanged.

**How the stock gripper mounts** (Seeed's STEP files, measured with OCCT; `cad/arm/rebot_b601_rs/interface/`): J6 is an RS00, the same
motor as ours. **Connector A** (`2-M6-ROTOR.step`) is a 35.6 × 6 aluminium disc bolted to J6's output (M3 on the 27 circle). **Connector B**
(`2-M7-STATOR.step`) is a 56.8 × 9.5 cup bolted to the stock gripper motor's *back face* (4 M3 on 38 at 45°). It slips over A and
3 radial M3 at 120° lock it. Base 10 keeps exactly that interface:

- **Hub** (`hub`, twin of Connector A): stays on the arm, bolted to J6's 6 output holes (M3 × 6 in counterbores). It has A's scallops
  for the tool screws' heads, A's 3 relief holes and 3 radial pilots. Seeed's aluminium Connector A fits every tool plate too.
- **Tool plate** (`tool_plate`, twin of Connector B): one per tool. Its socket drops over the hub, and 3 radial M3 × 8 lock it. Its
  floor takes 4 M3 on 38 at 45°, heads in pockets in the socket. **Tool change: loosen 3 screws, lift off, slide the other one on.**
- **Wrist bracket** (`bracket`, gripper only): our motor's axis runs *across* the fingers, so the motor can't sit on J6's axis as the
  stock one does. The bracket is an L. Its **leg** bolts to the RS00's back face (4 M3 × 8, the same 38 circle B uses). Its **foot**
  lies across the J6 axis under the gripper (`mount_gap` 1 mm), and the tool plate screws up into it (4 M3 × 10, self-tapped). The
  fingers point straight out along the roll axis, centred between them and on their mid-plane (`mount_axis_y` 0), like the stock
  fingers. Two 45° gussets join leg and foot.
- **Aero Hand plate** (`aero_plate`): the left Aero Hand's wrist pad has **4 M3 inserts on a 26.9 mm square, i.e. the same 38 circle at
  45°** (its CAD, `third_party/aero_hand/guide/anim41/left_base_link.STL`, inserts at ±13.435). So its plate is the tool plate plus an
  8 mm spacer, with a cable channel (45° roof) from the pad's 15 mm centre hole out to the rim, for the hand's USB and 6 V leads.
  M3 × 14 straight into the hand. Seeed's aluminium Connector B would bolt onto the hand directly too, with no cable channel.
- **RS00 cabling**: the RS00's two connectors (CAN + 48 V in, and out for the daisy chain; measured from Seeed's motor_7 mesh, now on
  the motor model as `motor_conn_*`) point along ±x, clear of the leg (checked). The cable comes off the +x one, is zip-tied through
  two slots in the foot (`tie_*`), then drops past the tool plate to J6, as the stock gripper's cable does. The gripper is the end of
  the chain, as the stock one is.
- **Prints without supports**: bracket foot down (leg holes are teardrops), tool plates tool face down with the socket open on top
  (head pockets run up to the mouth; radial holes are teardrops), hub arm face down. `check_geometry.py` measures every print STL.
- **Arm in the preview**: `exports/parts/arm_*.stl` is Seeed's reBot Arm B601-RS from its URDF (`cad/arm/rebot_b601_rs/`,
  CERN-OHL-W-2.0), posed by `arm_pose.py` so J6's boss top lands on the hub's arm face, stock gripper removed. The Aero Hand's palm
  stands on its plate beside it (`aero_view_x`), the other tool on the rack. The arm doesn't follow the Tune sliders; re-export moves it.

Pieces: **11 printed** (Base 9's 7 + bracket, tool plate, Aero plate, hub) + RS00 + **9 + 6 + 4 + 4 + 3 = 26 M3** for the gripper
on the arm (Base 9's 9; hub to J6 6 × M3×6; tool plate to bracket 4 × M3×10; leg to motor 4 × M3×8; radial 3 × M3×8). The Aero
Hand adds its plate + 4 × M3×14.

![arm](previews/arm_view.png)
![wrist](previews/arm_wrist.png)
![mount side](previews/mount_side.png)
![aero](previews/aero_station.png)
![print bed](previews/print_bed.png)

Checks: `python3 export_models.py && python3 genus.py && python3 check_geometry.py`. Base 9's, plus: the leg seats on the motor's back
face (pushed 0.5 mm in, it hits); the bracket clears the connectors and everything that swings, 0–30°; the tool plate seats on the foot
and the hub on the socket floor (shifted 0.5 mm, held); every screw clears its clearance hole and bites its pilot; the leg screws'
heads and hex key are clear; the tool screws' heads clear the hub; the arm (Seeed's meshes, posed) stays clear of the gripper and
mount and below the hub's arm face (raised 3 mm, it hits); the Aero Hand's 4 inserts lie on the tool screw circle (0.0 mm).
71/71 pass. Genus: bracket 10, tool plate 8, Aero plate 8, hub 13.

## Not verified

No reBot Arm, stock connector or Aero Hand was measured; it all comes from Seeed's and the Aero guide's CAD. Nothing is sliced or
printed. Holding the gripper by the RS00's back face is how the stock gripper hangs too, but here the foot also carries it ~70 mm
across to the J6 axis. Stiffness under the 2.5 kg rated payload isn't computed or tested (`mount_axis_y` −30 halves that reach,
at the cost of the fingers orbiting 30 mm off the roll axis). Radial and tool screws self-tap into print; Seeed's aluminium
Connector A and B are the stronger option if Jake has them. The RS00 connectors' real clocking on our motor (`motor_conn_deg`) is
assumed. Only one arm pose is checked.

Base 9's notes follow.

# Generalist Gripper · Base 9: top plate (Gripper 21, no separate Handle)

voice-d96cd30d. Jake: *"Add a piece on top so everything stays centered: a top plate similar to the bottom base piece, so the
geared handle pieces are captured and supported from both sides (above and below), and their axles are held at both ends so
they stay aligned. Keep it printable without supports, and keep the motor underneath."*

Base 9 is Base 8 (`v308_generalist_handle_gear`) plus a **top plate**:

- **The plate** is a flat 4 mm plate (`top_t`) 0.3 mm (`top_gap`) over the handle-gears, fingers and pinion. Its outline is the
  base's (the hull round both pivots and the pinion; `top_bush_r` 11.5 round each pivot, since any wider its corners reach the
  lower strap slot's keep-out as the handle swings) plus three **pillars** (`pillar_d` 8): two below the pinion
  (`pillar_pin_r`, `pillar_deg`) and one on the centreline above the gears' mesh (`pillar_top_z`, on a strip up the centreline). The pillars stand on the base;
  each foot drops 1.5 mm into a socket in the base top (`pillar_socket`, `pillar_fit` 0.15), so the plate is *located* on the
  base, not just screwed to it, and 3 M3 countersunk screws come up through the base's underside into the pillars (self-tapped).
  The base grows to reach the pillars. The motor stays underneath, unchanged.
- **The axle's top end.** Gripper 21's base hook lies right over the pivot, so the post can't run up through the finger. Instead
  each handle-gear's hub has a **C-shaped groove** round its pivot (`ring_r` 9.5, `ring_w` 2.6, `ring_depth` 2.5), cut down from
  the top face wherever the finger isn't (it stops `ring_wall` 1.5 short of the finger's pocket), and the top plate carries a
  matching **C-shaped ring** that runs in it, `ring_clear` 0.25 narrower each side and shortened by the 30° swing so it never
  reaches the groove's ends. The C is about 250°, open where the finger is. So each handle-gear turns on the base's post below
  and on the plate's ring above: one axis, held at both ends.
- **Captured.** With the plate on, neither a handle-gear nor a finger can lift (Base 8: only gravity held them).
- **A hole over the pinion** (`top_access_clear`) keeps its 3 flange screws reachable with the plate on.
- **Prints top face down** (`exports/print/top_plate.stl`, `previews/top_plate.png`): the plate on the bed, the two rings and three pillars straight up; the pillar pilots are blind,
  1 mm under the bed face. The base's new screw holes are countersunk from the underside (cones open at the bed, 45°).

Pieces: **7 printed** (2 fingers, 2 handle-gears, pinion, base, top plate) + RS00 + **9 M3** (6 + 3) = **17** (Base 8: 13).
17 new params in the *Top plate (Base 9)* group, all on the Tune panel.

Assembly: motor under the base, pinion on the flange, handle-gears on their posts, fingers into the handle-gears (all as
Base 8), then the top plate down onto them: rings into the grooves, pillar feet into their sockets; 3 M3×16 countersunk up
through the base into the pillars.

![top plate](previews/top_plate.png)
![top ring](previews/top_ring.png)
![print bed](previews/print_bed.png)

Checks: `python3 export_models.py && python3 genus.py && python3 check_geometry.py`. Base 8's, plus: nothing that turns touches
the top plate at any swing 0–30° (rings in their grooves, fingers, handle-gears, pinion); lifted 0.5 mm, a handle-gear or a
finger hits the plate; shifted 0.5 mm sideways, each handle-gear hits its ring (left and right); plate and base meet only at
the pillar feet; the plate clears the motor; 50/50 pass; the strap-slot keep-outs and the pinion's screw access include the plate; the top
plate prints without supports; genus: base 9 holes, top plate 1.

## Not verified

Nothing has been sliced or printed. The ring is a printed C in a printed groove, not a full-circle bearing, and it is coaxial
with the post only as well as the pillar sockets locate the plate. The pillar screws self-tap into PLA/PETG; no pull-out test.
M3×16 is computed (6 base + ~10 into the pillar), not tried.

Base 8's notes follow.

# Generalist Gripper · Base 8: handle-gear (Gripper 21, no separate Handle)

voice-1f4d3de1. Jake: *"Base 7 is going in the right direction but not passed. It has two separate handle pieces, which isn't
right. The base and handle are starting to become one piece; go further that way. The part that curls around should be one
piece with the handle. Ditch the separate Handle part entirely: the geared pieces become the handles. Each finger's gear and
handle (with its strap-loop slots) is a single printed part."*

Base 8 is Base 7 (`v307_generalist_printable`) with the Handle part gone:

- **The handle-gear is the handle.** Each side is one print: handle plate, both hooks' feet, the tail that curls round the
  base hook, hub, web and teeth. The parts are now named *Left/Right handle-gear*, and the live preview's mix tile drops the
  Handle picker ("Handle in Base") whenever the chosen Base carries handle-gears. Base 7 in the mix tile was drawn with
  Handle 7's two separate handles on top of its own handle-gears; that was the doubled handle.
- **Two strap-loop slots** per handle-gear (`strap_slots` 2, `strap_rib` 2.5 mm apart; Base 7 had one tunnel). Each is a
  slot cut straight through the part under the strap boss, so it prints as a vertical hole: no bridge, no support. One loop
  per slot wraps the boss and the digit lying on it, so the digit is held in two places. `slots_shift` (3 mm) moves the pair
  toward the top hook so the lower slot's ventral mouth clears the base plate at every swing (centred, the base sat in it).
- Everything else, including the print rules and orientations, is Base 7's. 13 pieces: 6 printed (2 fingers, 2 handle-gears,
  pinion, base) + RS00 + 6 M3.

Checks: `python3 export_models.py && python3 genus.py && python3 check_geometry.py`: 42/42 geometry checks pass (overhang
check on every print STL, strap keep-outs at both slots' mouths at 0–30°), genus 3 per handle-gear (2 slots + post bore).
Nothing has been sliced or printed.

![print bed](previews/print_bed.png)

Base 7's notes follow.

# Generalist Gripper · Base 7: printable (Gripper 21, Handle 7)

voice-fef42307. Jake: *"Copy Base 4 with Handle 7 and simplify significantly, with a focus on 3D printability. The gripper
fingers are pretty good; the other pieces are too complex and not very printable. Every piece should print on an FDM printer
without supports: flat bases, overhangs at 45° or less, no floating features, sensible split lines, and a print orientation
noted for each part. Fewer parts. Keep it parameterized and driven by the single RobStride RS00."* Not built on Base 5 or Base 6.

Base 7 is Base 4 (`v304_generalist_one_piece_drive`) with every printed part redrawn as a flat extrusion. Still parametric
(`params.json`, 102 params; the Tune panel slides them), still one RS00, centred, and the same layout: two handle-gears in the
finger plane, a centred pinion, a base plate.

![print bed](previews/print_bed.png)
![front](previews/front.png)

## The rule

Every printed part is a 2D outline extruded along the finger's thickness (Y), or two of them stacked with the upper one
narrower. So each one lies flat on one face and every wall is vertical. The only sloped faces are the fingers' dorsal taper,
which slopes up and away, and the 45° screw cones. `exports/print/*.stl` are exported lying on the bed in that orientation
(z up), ready to slice. `check_geometry.py` reads each one and fails it if any face above the bed overhangs past 45° or if it
is not one solid sitting on z 0.

## Print orientation

| Part | Bed face | Height | What's above it |
|---|---|---|---|
| Right / left finger (Gripper 21, unchanged) | ventral face (the flat one) | 12 | the taper slopes the top face down to the point; holes and grooves are vertical |
| Right / left handle-gear | the web's underside | 15.2 | the whole outline (plate, strap boss, tail, hub, teeth) runs straight up; the finger pocket is cut down from the top to the web; the strap tunnel and the post bore go straight through |
| Pinion | the teeth's top face (assembled dorsal side) | 20.5 | teeth, then the narrower spigot on top; the screw holes open at the bed into 45° cones |
| Base | the underside (the motor's face) | 6 + 3.1 posts | plate, two pivot posts standing up, countersinks open at the top |

No supports, no brim needed for overhangs, no bridges.

## What changed from Base 4

Base 4's handle-gear was the unprintable part. Its teeth started 2 mm above the web, the handle plate 3.2 mm above it, and the
axle hung under it, so it had no face to sit on that didn't leave something floating. Base 7:

- **Handle-gear = one outline, full height.** The handle plate, strap boss, tail, hub and teeth all run from the web's underside
  to the finger's top face. The teeth are now 15.2 mm wide (Base 4: 8), the pinion's too. **Handle 7's handle is 15.2 mm edge-on
  here, not 12**: the 3.2 mm under the finger is the web plus its fit, the price of a flat bottom. It sticks out on the ventral
  side only; the dorsal face is still flush with the finger.
- **The plate's ends are rounded in plan** (`plate_corner_r` 1.5), not edge-on (Base 4: 3 mm edge-on, which hung over the bed).
- **Pivot posts replace the axles.** A 12 mm post (`post_d`, was `axle_d`) stands up out of the base at each pivot and the
  handle-gear turns on it through a bore in its web. Base 4's axle under the gear and the bushing hole in the base are gone.
- **The hub is a whole disc** (`hub_top` 14 = `hub_r`; Base 4: 0, cut at the pivot). Cut at the pivot, half the bore opened
  under the finger and the post would only bear on one side.
- **Countersunk screws, one type.** The pinion's 3 M3 and the base's 3 M3 are now countersunk (DIN 7991) on 45° cones.
  Base 4's pinion counterbores, printed teeth down, left a flat ledge hanging in the air. Pinion: M3×20 (recess 5 mm, 4.5 mm
  into the flange). Base: M3×10 (4.3 mm into the front ring).
- **`gear_w` is gone**: every gear is the handle-gear's height.

## Piece count

Same as Base 4: **6 printed** (2 fingers, 2 handle-gears, pinion, base) + RS00 + **6 M3 countersunk** = **13**. That's the
floor for this layout while the fingers stay separate yellow prints: the pinion is what lets the motor sit centred, and Base 5
(one gear) and Base 6 (no pinion) are off the table. To go lower, each finger could be printed into its handle-gear: 4 printed
parts, 11 pieces, but one colour per side and no swapping fingers. Not done; Jake's call.

Assembly: motor under the base (3 M3×10 countersunk from the top, dowels locate). Pinion onto the flange through the base
(3 M3×20 countersunk). Drop each handle-gear onto its post. Drop each finger into its handle-gear from above.

## Parts

| Part | Print STL (on the bed) / assembled pose |
|---|---|
| Right / left finger (Gripper 21) | `exports/print/right.stl`, `left.stl` / `exports/parts/...` |
| Right / left handle-gear (Handle 7 + gear) | `right_gear.stl`, `left_gear.stl` |
| Pinion | `pinion.stl` |
| Base | `base.stl` |
| Motor (RS00, not printed) | `motor.stl` |

## Checks (all 42 of 42 pass)

`python3 export_models.py && python3 genus.py && python3 check_geometry.py`. Everything from Base 4, plus:
- every print STL sits on z 0, is one solid and has no face past 45° above the bed (6 parts);
- positive control: the pinion turned spigot-down overhangs ~1350 mm², so the check does catch overhangs;
- each handle-gear turns on its post 0–30° without touching it, and shifted 0.5 mm it hits the post;
- the posts' tops clear the fingers at every swing.

Holes: handle-gear 2 (strap tunnel, post bore), pinion 3, base 6 (motor boss, 3 screws, 2 dowels).

## Not verified

Nothing has been sliced or printed. The overhang check is geometry only: no bridging, warping, elephant's foot, first-layer or
real printer tolerances. The 0.25 mm post clearance and 0.2 mm finger fit are nominal. Each handle-gear bears on its post over
only the web's 3 mm (`web_t`), with its flat underside 0.3 mm over the base; there's no wobble or wear test. Raising `web_t`
lengthens the bearing but makes the handle taller. Base 4's other caveats stand: only gravity and friction keep the fingers in
and the handle-gears on their posts (+y), the left gear has teeth only for 0–30°, there are no swing stops, the 3-bolt joints are
a shear estimate, and the RS00 back face is assumed to be the wrist mount.

---

Base 4's README follows.

# Generalist Gripper · Base 4: one-piece drive (Gripper 21, Handle 7)

voice-b7260e73. Jake: *"Simplify again: there are too many pieces. Focus especially on how the base links to the handle;
that connection has too many parts. Cut the part count wherever possible."*

Base 4 is Base 3 (`v303_generalist_inplane`) with the handle and its side gear printed as one part, and half the motor
screws. Still parametric (`params.json`, 103 params; the Tune panel slides them), still one RobStride RS00, centred.

![front](previews/front.png)
![handle-gear](previews/gear.png)

## Piece count

| | Base 3 | Base 4 |
|---|---|---|
| Fingers | 2 | 2 |
| Handles | 2 | — (in the gears) |
| Side gears | 2 | 2 (each with its handle) |
| Pinion | 1 | 1 |
| Base | 1 | 1 |
| **Printed** | **8** | **6** |
| RS00 motor | 1 | 1 |
| M3 screws | 12 (6 flange, 6 front ring) | **6** (3 + 3) |
| **Total pieces** | **21** | **13** |

Handle-to-base chain. Base 3: finger, handle (tail + key), gear cradle (key notch), gear axle, base bushing.
Base 4: finger, handle-gear, base bushing.

## What changed from Base 3

- **Handle + side gear = one print.** The handle's tail runs straight into the gear hub. The finger's pocket is cut
  through both at once, `fit` off the finger. Gone: the key (`key_deg`, `key_w`, `key_r`), the key notch, the cradle's
  separate fit, and the handle as its own part.
- **The finger drops in from the dorsal side** (+y, moving −y). Its base hook goes between the handle's two feet and its
  base corner into the hub pocket, and it rests on the gear's web. The hooks and the hub drive it both ways. Turned 1°
  either way, the handle-gear hits it (checked).
- **The web is the stop, so Handle 7's stop strip is gone** (`stop_depth`, `stop_width` removed). The handle is exactly the
  finger's 12 mm edge-on: Handle 7's height, `handle_over` 0 (Base 3: 1.5, 15 mm). Plate, feet, strap tunnel and boss are
  Handle 7's.
- **3 bolts, not 6, at each motor joint.** New `motor_out_screws` (3): the pinion bolts through every other hole of the
  RS00's 6-hole output flange. New `motor_front_screws` (3): the base plate uses every other front-ring hole, and the
  two dowels still locate it. Estimate: 14 N·m peak at the 13.5 mm bolt radius is about 350 N of shear per M3. Not tested.
  Slide either one back to 6 to get Base 3's bolting.

Parts: **6 printed** (2 fingers, 2 handle-gears, 1 pinion, 1 base) + the RS00 + **6 M3**.

Assembly: put the motor under the base (3 M3). Bolt the pinion to the flange through the base (3 M3). Drop each
handle-gear's axle into its bushing. Then drop each finger into its handle-gear from above.

## Parts

| Part | STL (assembled pose / print) |
|---|---|
| Right / left finger (Gripper 21) | `exports/parts/right.stl`, `left.stl` / `exports/print/...` |
| Right / left handle-gear (Handle 7 + gear) | `right_gear.stl`, `left_gear.stl` |
| Pinion | `pinion.stl` |
| Base plate | `base.stl` |
| Motor (RS00, not printed) | `motor.stl` |

In the live preview's mix-and-match, the handle-gears count as Base parts (their names start "Right gear" / "Left gear").
Picking another Handle with Base 4 draws that handle over the one already on the gear.

## Checks (all 32 pass)

`python3 export_models.py && python3 genus.py && python3 check_geometry.py`. Everything from Base 3 still passes
(fingers, handle seat and prongs, gear and pinion mesh, strap tunnel keep-outs, bolt access, base/motor clearances), plus:
- the handle-gear clears its seated finger, and the finger drops in from 20 mm above in 0.5 mm steps without touching;
- the finger rests on the web: 0.3 mm lower, it hits;
- turned 1° open or closed, the handle-gear hits the finger, so it drives it both ways;
- handle and gear core overlap, so the print is one solid (each handle-gear is 1 component).

Holes: handle-gear 1 (the strap tunnel), pinion 3, base 8 (2 bushings, the motor boss, 3 screws, 2 dowels).

## Not verified

Nothing has been printed and there is no RS00 in hand. Only friction and gravity keep the finger in its handle-gear
(+y), as in Base 3. The handle-gear is a bigger print with more overhang: the teeth start 2 mm above the web, and the
strap boss stands out from the plate. Print orientation and supports aren't worked out. The 3-bolt joints are a shear
estimate only. Base 3's other caveats stand: the left gear has teeth only for 0–30°, there are no swing stops, nothing
holds the gears down axially, there is no finger pivot pin, and the RS00 back face is assumed to be the wrist mount.

---

Base 3's README follows.

# Generalist Gripper · Version 3.3: in-plane drive (fingers 1.21)

voice-3b311f32. Jake: *"Reduce the handle height again: just barely taller than the gripper fingers themselves. Rework how the
handle attaches to the base and gear system so it attaches much more smoothly. Put the gears in the same plane as the gripper
fingers (move the gears up), with a single motor centered there. The handle wraps around and connects into the gear system."*

3.3 is 3.2 (`v302_generalist_simple`) laid out again. Still parametric (`params.json`, 107 params; the Tune panel slides them),
still separable pieces, still one RobStride RS00.

![front](previews/front.png)
![drive](previews/drive_iso.png)

## What changed from 3.2

- **Handle 15 mm tall** across the finger (3.2: 29; the finger is 12): new `handle_over` (1.5 mm past each face).
- **Strap tunnel instead of strap slots.** A 15 mm plate has no room for a slot beside the finger, so the strap runs
  through a tunnel: a boss on the plate's outer face (where the digit lies) with a 2.5 mm gap under it
  (`strap_slot_width`), open at both faces of the plate. The webbing goes in one face, out the other, and round the digit.
  `slot_gap` is gone. The handle is 4 mm thicker over the 24 mm boss (the digit sits that much further out there).
- **The handle wraps the finger's base.** Its **tail** is a band, `slide_t` thick, that follows the finger's outline
  `tail_gap` off it: from the plate over the base hook's prong, round the hook and under the finger (`tail_top_u`,
  `tail_reach`). A **key** (`key_deg`, `key_w`, `key_r`) sticks straight down out of the tail under the pivot.
- **Gears in the finger plane.** They are centred on the finger's mid-plane below the fingers (3.2: stacked under them).
  Each side gear's hub is a **cradle** cut to the finger and the tail (fit off them), with a notch for the key. The
  finger-and-handle unit drops straight down into it. The key's sides face along the swing, so the gear drives the handle
  both ways with about 1.5 deg of play (without the key it only pushed the handle open). A 3 mm web under the cradle
  reaches in to the pivot, which sits inside the finger's base corner, and a 12 mm axle under it turns in a plain bushing
  in the base. 3.2's cups and drivers are gone.
- **One RS00, centred.** A **pinion** (34 teeth, 1:1, `pinion_teeth`) on the motor's flange sits on the centreline,
  47 mm below the pivots, and meshes the **right** gear only. The right and left gears mesh each other, so the fingers still
  counter-rotate. A pinion meshing both gears would turn them the same way. Each side gear carries teeth only where its
  mates meet it over 0–30 deg (+`gear_extra`), so the left gear never reaches the pinion (checked).
- **Base**: the hull of the motor's disc (centred) and a disc round each bushing. The motor bolts up under its centre.

Parts: **8 printed** (2 fingers, 2 handles, 2 gears, 1 pinion, 1 base; 3.2: 7) + the motor. Screws: only the motor's
(6 M3 flange through the pinion + 6 M3 front ring).

Assembly: motor under the base; the pinion bolted to the flange through the base; each side gear's axle dropped into its
bushing; slide each handle onto its finger across the finger, from the ventral side, as in 2.5; then drop each finger and
handle unit into its gear's cradle from above.

## Parts

| Part | STL (assembled pose / print) |
|---|---|
| Right / left finger (1.21) | `exports/parts/right.stl`, `left.stl` / `exports/print/...` |
| Right / left handle | `right_slide.stl`, `left_slide.stl` |
| Right / left gear | `right_gear.stl`, `left_gear.stl` |
| Pinion | `pinion.stl` |
| Base plate | `base.stl` |
| Motor (RS00, not printed) | `motor.stl` |

## Checks (all 33 pass)

`python3 export_models.py && python3 genus.py && python3 check_geometry.py`: every 2.6 handle check on the new
handle: it seats, slides on across the finger, and is held by both prongs and the stop strip. Plus:
- the side gears mesh 0–30 deg, the pinion meshes the right gear 0–30 deg, and each pair interferes half a tooth off;
- the pinion never touches the left side or the right finger and handle;
- the cradle clears its finger and handle, the unit drops in from above, it rests on the web, and turned 2 deg either way the
  cradle hits the handle;
- the strap tunnel mouths stay clear of everything but their own handle 0–30 deg;
- the six flange bolts can be reached from above the pinion at every swing;
- nothing that swings hits the base or motor, the two sides never collide, and the motor screws and dowels line up.

Holes: handle 1 (the tunnel), gears 0, pinion 6, base 11.

## Not verified

Nothing printed, no RS00 in hand. The cradle is a 0.2 mm fit: the unit sits in it by gravity and friction, and nothing
stops it lifting out upward (+y). Both side gears turn in plain printed bushings, and nothing holds them down
axially. The left gear has teeth only for 0–30 deg, so driving it past that runs it off its teeth. There are no swing
stops; the motor's limits must keep it in range. The strap tunnel (2.5 mm gap for 1.5 mm webbing) is untested with real
webbing. 3.1's caveats stand: no finger pivot pin (the finger is held through its handle), no tooth strength or load
analysis, and the RS00's back face (4 x M3 on 38 mm) is assumed to be the wrist mount.

---

3.2's README follows.

# Generalist Gripper · Version 3.2: simple (handles 2.6 shrunk, fingers 1.21)

voice-e3cd53d6. Jake: *"Simplify the whole 3.1 setup. It has to be much simpler: fewer parts and features, as little as
needed. Nothing should get in the way of the strap-loop slots; keep them completely clear. Shrink the handles part down."*

3.2 is 3.1 (`v301_generalist_base`) with everything that wasn't needed taken out. Still parametric (`params.json`, 99
params; the Tune panel slides them), still separable pieces, still one RobStride RS00 underneath.

![drive](previews/drive_iso.png)

## What changed from 3.1

- **Arms gone; gear + cup is one part.** 3.1 had an arm per side (channel round the handle, floor plate, hub, hex boss)
  screwed to a separate gear with two M3s. 3.2 merges them into a **driver**: the gear sector with a short **cup** on top
  that the handle plate's low end drops into. The cup is now the handle–base interface (`cup_len` 8, `cup_depth` 5,
  `cup_wall` 2.5). Gone with it: the hex boss/socket, the 4 interface screws, their counterbores and taps, and the
  "Handle-base interface" and "Arm" param groups (16 params).
- **Strap slots completely clear.** 3.1's arm channel and floor ran under the ventral strap slot. Now nothing but the
  handle itself comes within `strap_clear` (3 mm, new param) of either slot or the plate wall beside it, on either face, at
  any swing 0–30 deg. `check_geometry.py` checks exactly that (red boxes in `previews/strap_zones.png`), with a positive
  control (a cup long enough to reach the slots fails it). The cup stops `strap_clear` short of the slots (asserted), and
  the gears sit `strap_clear` below the plate's ventral edge.
- **Handle shrunk.** The plate is 29 mm across the finger (3.1: 37): `slot_wall` 2 (3), `slot_gap` 18 (24). The slots
  are still 3.5 x 21 mm and clear the 12 mm finger by 3 mm each side. Length (67.4 mm, hook to hook) is unchanged:
  it is set by the finger's two hooks.
- **Base: just two discs.** The plate is the hull of a 29 mm disc round the motor (3.1: 31) and a 21 mm disc round the
  left bushing (new `bush_r`). The wrist tab and its 4 holes are gone; the RS00's own back face (4 x M3 on 38 mm) is the
  wrist mount. The whole stack is 6.5 mm shorter (base underside y -31.8; 3.1: -38.3).

Parts: **7 printed** (2 fingers, 2 handles, 2 drivers, 1 base; 3.1: 9) + the motor. Screws: only the motor's (6 M3
flange + 6 M3 front ring; 3.1 also had 4 interface screws).

Assembly: base onto the motor's front ring; right driver bolted to the flange through the base, left driver dropped into
its bushing; each finger, with its handle already on, drops into its driver's cup from above.

## Parts

| Part | STL (assembled pose / print) |
|---|---|
| Right / left finger (1.21) | `exports/parts/right.stl`, `left.stl` / `exports/print/...` |
| Right / left handle (2.6, shrunk) | `right_slide.stl`, `left_slide.stl` |
| Right / left driver (gear + cup) | `right_driver.stl`, `left_driver.stl` |
| Base plate | `base.stl` |
| Motor (RS00, not printed) | `motor.stl` |

## Checks (all pass)

`python3 export_models.py && python3 genus.py && python3 check_geometry.py`: every 2.6 check, plus: gears mesh 0–30 deg
(and interfere half a tooth off); the cup clears its finger and handle, stops the handle sliding out, and lets the
finger-and-handle drop in; **the strap keep-outs are empty of everything but their handle 0–30 deg**; all six flange
bolts can be reached from above the right driver (this is why `cup_len` stops at ~8.5 mm); nothing that swings hits the
base or motor; the sides never collide; motor screws and dowels line up. Holes: driver 6, base 10.

## Not verified

Nothing printed, no RS00 in hand. The cup is a short (8 mm) 0.2 mm-fit grip: it drives the handle, which drives the
finger through its hooks; no load test. No wrist mount was designed: the RS00 back face is assumed to be it. 3.1's
other caveats stand: no finger pivot pin, nothing holds the left driver down axially, no swing stops.

---

3.1's README follows.

# Generalist Gripper · Version 3.1: base and drive (handles 2.6, fingers 1.21)

voice-5b59d3bf. Jake: *"The black handles extend back behind the yellow fingers, wrap around, and connect into a common
base. A single motor is mounted underneath that base; it spins and drives gears attached to the black handles, which opens
and closes the gripper."* Motor (Jake's correction): the **RobStride RS00**, the gripper motor of Seeed's reBot Arm
B601-RS (its LeRobot follower names the gripper `rs-00`), not the SO-101's STS3215 or the Damiao DM-J4310-2EC.

3.1 is the first 3.x version (gripper plus handles plus base). It is 2.6 (`v206_generalist_single_step`) unchanged, plus
four new kinds of part. Every one is its own module in `gripper.scad`, its own STL, and every dimension is in
`params.json` (112 params; 52 new, in five groups), so the Tune panel slides them.

![drive](previews/drive_iso.png)

## The drive, top to bottom (down the ventral side, -y)

- **Arm** (black, one per finger; `arm()`): the handle's root. A channel wraps the 2.x handle plate's ventral edge for
  `chan_len` (30 mm) from its low end, and a floor plate runs under it to a hub on the finger's pivot. The channel also
  stops the handle sliding back out the way it slid in, which only friction did in 2.5/2.6.
- **The handle-base interface** (`iface_*`): on each pivot axis, a 10 mm hex boss under the arm drops 4 mm into a hex socket
  in the top of that side's gear, held by two M3 screws on a 16 mm circle. This is the one joint every handle version and the
  base share. To fit another 2.x handle, print an arm from that version's handle params (rail, plate thickness, height and
  ends) with this same boss; the gears, base and motor do not change.
- **Gears** (`gear()`): two equal involute spur sectors (34-tooth circle, module 1.60, 20 deg, 8 mm wide, 120 deg of teeth).
  Pitch radius = the pivot half-spacing (27.25 mm), so they mesh on the centreline and the fingers counter-rotate 1:1. The
  left one is half a tooth out of phase. Each has a 35 mm spigot down into the base plate.
- **Base** (`base()`, black): one 6 mm plate across both pivots under the gears, plus a rear tab with four wrist holes.
- **Motor** (`motor()`, reference only): RS00, 57 mm x 51 mm, coaxial with the right pivot under the plate. Its front ring
  (6 x M3 on 50 mm, plus 2 dowels) bolts up to the plate; its output flange (6 x M3 on 27 mm) bolts the right gear's spigot
  through the plate. The left gear turns in its plate hole as a plain bushing and follows through the mesh. So the motor is
  off-centre, under the right finger (a centred motor would need an extra gear that turns the wrong way or an idler).

Assembly: base onto the motor; gears into their holes (right one bolted to the flange); each arm screwed to its gear; then
each finger, with its handle already on, drops into its arm's channel from above.

## Motor numbers and sources

All from RobStride's RS00 drawing ([Seeed 100083284](https://media-cdn.seeedstudio.com/media/wysiwyg/111-photo/100083284--01.png))
and [RS00.step](https://github.com/RobStride/Product_Information/blob/main/Product%20Literature/CAN2.0/RS00/RS00.step) (bbox
57 x 57 x 51.4): body 57 x 51 +-1, output boss 35 x 1, output 6 x M3 deep 5 on 27 +-0.1, front ring 6 x M3 on 50 +-0.1 at
30 deg, 2 x 3 mm dowels deep 5 at 15 deg, back 4 x M3 deep 4 on 38 +-0.1 at 45 deg. Manual: 5 N m rated, 14 N m peak,
315 rpm no-load, 24-60 V (48 V rated), CAN. Each is a param in the "Motor: RobStride RS00" group.

## Parts

| Part | STL (assembled pose / print) |
|---|---|
| Right / left finger (1.21) | `exports/parts/right.stl`, `left.stl` / `exports/print/...` |
| Right / left handle (2.6) | `right_slide.stl`, `left_slide.stl` |
| Right / left arm | `right_arm.stl`, `left_arm.stl` |
| Right / left gear | `right_gear.stl`, `left_gear.stl` |
| Base plate | `base.stl` |
| Motor (RS00, not printed) | `motor.stl` |

## Checks (all pass)

`python3 export_models.py && python3 genus.py && python3 check_geometry.py`: every 2.6 check, plus: the gears mesh without
touching at every degree 0-30 (and do touch when one is turned half a tooth); the arm clears its finger and handle, stops
the handle sliding out, and lets the finger-and-handle unit drop in; the hex boss clears its socket and drives the gear
(turned 10 deg it hits); nothing that swings hits the base or motor, and the two sides never meet, 0-30 deg; the motor's
screws and dowels line up with the gear and base holes. Hole counts: arm 2, gear 6, base 14.
`live_render.py` renders all ten parts for the Tune panel (~0.2 s); bad combinations show the assert's message.

## Not verified

Nothing printed, and no RS00 in hand: the numbers are the drawing's. The second dowel is assumed opposite the first.
Solids only: no tooth strength, loads or motor torque. The fingers have no pivot pin; each is held to its arm only through
its handle (hooks + channel), and the finger can still slide out dorsally against friction. Nothing holds the left gear
down axially, and its bushing is printed plastic. No swing stops: the motor's limits must keep it in 0-30 deg. The wrist
holes are placeholders; the B601 wrist connector is not measured.

---

2.6's README follows.

# Generalist Gripper · Version 2.6: single step (fingers 1.21)

voice-72840084. Jake (on 1.20 + 2.5): *"Extend the black piece where my finger rests all the way up to where the profile
starts to go out again. Where it goes out again, make it more of a single jump out: no double indent, just out and then
back in."*

2.6 is 2.5 (`v205_generalist_spanning_handle`) with the top hook moved up. Its fingers are **1.21** (gripper only = the
`right`/`left` finger STLs here; there is no separate 1.21 folder). Side by side, same camera: `previews/compare_v205.png`.

## What changed from 2.5

- **The outer edge runs straight up to where it used to go out** (1.21). 1.20's edge had the top hook notch at u 28.4, a
  ramp back in, a ~1 mm dip from u 36 to 56, then the blade-root S-curve climbing out: two indents. Now the edge is one
  straight line from the base hook to the top notch at u 54 (new param `top_notch_u`, replacing `top_hook_mirror_u`).
- **One step out.** At u 54 the mirrored J-hook curls out to its crest (6.6 mm out, same hook as 2.5), and the edge stays
  out there, nearly level (sags 0.3 mm), until the beak's outer edge comes back up to it at about u 77; then the beak
  carries on and rounds back in to the point. New param `top_step_back` (0) lets the back of the step dip and rejoin
  the edge sooner if the shoulder is too bulky. Ahead of the hook the finger is up to ~3 mm wider outboard than 1.20.
- **The handle is longer** (2.6). Same plate, feet, strap slots, stop strip and slide-in across the finger as 2.5, but
  floor to floor + `span_over` it is now **67.4 mm** (2.5: 41.8). The strap slots stay centred on it.

## Parts

| Part | STL (assembled pose / print) |
|---|---|
| Right finger (1.21) | `exports/parts/right.stl` / `exports/print/right.stl` |
| Left finger (mirror) | `exports/parts/left.stl` / `exports/print/left.stl` |
| Right handle | `exports/parts/right_slide.stl` / `exports/print/right_slide.stl` |
| Left handle | `exports/parts/left_slide.stl` / `exports/print/left_slide.stl` |

## Checks (all pass)

`python3 export_models.py && python3 genus.py && python3 check_geometry.py`: every 2.5 check (meshes watertight, 33
finger holes + 2 handle holes, fingers never collide 1-30 deg, point-only contact, taper, handle seats, slides in across the
finger without touching, held by both prongs, both floors and the stop strip).

## Not verified

Nothing printed. The wider shoulder ahead of the top hook isn't checked against a hand or anything the finger closes on.
2.5's caveats stand: only friction stops the handle sliding back out the way it came, the 0.2 mm fit is nominal, and
the prongs haven't been pull-tested.

---

2.5's README follows.

# Generalist Gripper · Version 2.5: spanning handle

voice-56f9d73f. Jake: *"Bring the handles down further, and make the handle piece extend higher up, so it spans between the
gripper's bottom and top hooks and slides in to be captured by both."*

2.5 is 2.4 (`v204_generalist_parametric`: every dimension in `params.json`, the Tune panel) on 1.20's fingers
(`v020_generalist_double_hook`: 1.19's wide beak, 1.18's flat-bottom taper, and a top hook mirroring the base J-hook).
The finger STL is byte-identical to 1.20's.

## What changed from 2.4

- **1.20's fingers.** `trace_photo.py` gains 1.20's `top_hook()`. `params.json` takes 1.19/1.20's values:
  `outer_lean_deg` 15, `outer_start_handle` 0.50, `outer_end_handle` 0.25, `outer_bow` 0.20, `tip_thick` 2.4, and
  `contact_back` 0.0005 (calibration). New outline param `top_hook_mirror_u` (8.5) slides the top hook along the edge.
- **One handle spans both hooks.** The black plate (3.5 mm, 37 mm across, two strap slots, as 2.2-2.4) now runs the whole
  straight outer edge, from the base notch floor to the top notch floor plus `span_over` (1 mm) at each end: 41.8 mm long
  (2.4: 28). That's lower at the bottom (its foot now reaches the base notch's floor, 2.4 stopped 0.8 mm short) and 13.8 mm
  higher at the top. The finger outline grown by `fit` trims each end into a foot that fills one notch.
  `slide_len` and `slide_u0` are gone: the plate's length follows the hooks.
- **It slides in across the finger.** The two hooks face each other, so nothing can slide in along the edge any more. So 2.3's
  tongue and keyhole pocket are gone (with their 10 params), and the hooks do their job: both hold the handle along the edge
  and against outboard pull. The handle slides on across the finger's thickness from the flat (ventral) side, like 1.20's
  blank. With no pocket, the finger no longer breaks into 4 honeycomb holes.
- **A stop strip.** New `stop_depth` (1.5) and `stop_width` (2): a strip on the plate's inboard face, along its ventral side.
  It trails the slide-in, and when the handle is home it butts against the ventral face, so the handle can't slide on
  through. `stop_depth` 0 removes it. In 1.20, only friction held the blank.

## Parts

| Part | STL (assembled pose / print) |
|---|---|
| Right finger | `exports/parts/right.stl` / `exports/print/right.stl` |
| Left finger (mirror) | `exports/parts/left.stl` / `exports/print/left.stl` |
| Right handle | `exports/parts/right_slide.stl` / `exports/print/right_slide.stl` |
| Left handle | `exports/parts/left_slide.stl` / `exports/print/left_slide.stl` |

`gripper.scad` `part=` adds `handle_sliding` (with `handle_slide` = mm still to go). Print the fingers flat on the ventral face.

## Checks (all pass)

`python3 export_models.py && python3 genus.py && python3 check_geometry.py`: every 2.4 / 1.20 finger check, plus:

- the seated handle clears the finger;
- it slides in from 26 mm out on the ventral side, in 1 mm steps, without touching;
- pushed 0.5 mm outboard it hits both prongs, toward either hook that notch's floor, and on through, the stop strip
  hits the ventral face;
- the finger has 33 through-holes (1.20's) and the handle has 2.

`live_render.py` with no overrides reproduces the exported STLs, and with `top_hook_mirror_u` changed it re-traces (~1 s).

## Not verified

Nothing has been printed. Only friction keeps the handle from sliding back out the way it came in. The 0.2 mm fit is
nominal, and the prongs (1.19 base-hook size, about 2.2 mm deep) haven't been pull-tested.
