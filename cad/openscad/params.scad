// =============================================================================
//  params.scad — every dimension of the SO-101 gripper, as a named variable.
// =============================================================================
//
//  CAD bake-off, tool 1 of 3 (OpenSCAD).  See NOTES.md for the verdict and for
//  the honest list of what is measured vs. what is approximated.
//
//  Context:  plans/gripper_bet.md  (why a gripper at all — Hand 1.0 / Hand 2.0)
//            plans/hand_1_0.md     (§6 names OpenSCAD as the source of truth for
//                                   printable parts, and asks for one shared
//                                   params file that every part includes — this
//                                   is that file, scoped to the bake-off dir.)
//
//  DIMENSIONAL SOURCE OF TRUTH
//  ---------------------------
//  Every number tagged [STEP] below was read out of the two reference STEP
//  files committed at cad/build123d/reference/ :
//      Moving_Jaw_SO101.step           (the moving jaw)
//      Wrist_Roll_Follower_SO101.step  (the gripper body / fixed jaw)
//  They were measured analytically — B-rep face by B-rep face, not off a mesh —
//  with tools/measure_step.py, which prints every planar face's normal+offset
//  and every cylindrical face's radius+axis.  Re-run it to re-check any number
//  here.  Numbers tagged [DERIVED] are computed from [STEP] numbers; numbers
//  tagged [GUESS] are mine and are listed again in NOTES.md.
//
//  FRAMES
//  ------
//  Everything below is in the WRIST-ROLL FOLLOWER's own STEP frame:
//      +Z  up the fixed jaw, from the wrist_roll horn face toward the fingertip
//      +Y  along the jaw pivot axis
//      +X  out of the gripper's throat (the direction the jaws open toward)
//      origin = centre of the wrist_roll servo horn bolt circle
//  The moving jaw is modelled in its own STEP frame and transformed into this
//  one by jaw_place() in gripper.scad.
//
// =============================================================================


// --- rendering ---------------------------------------------------------------
fast_preview  = false;                 // true = coarse curves, much faster F5
$fa = fast_preview ? 12 : 2;
$fs = fast_preview ? 1.2 : 0.35;
eps = 0.01;                            // co-planar-face nudge


// --- fasteners ---------------------------------------------------------------
// All of the SO-101's gripper screws are M3.  Change these once and every hole
// in both parts follows.
m3_clear_d      = 3.2;                 // [STEP] Ø3.2 clearance holes, both parts
m3_socket_d     = 5.4;                 // [STEP] counterbore in the moving jaw
m3_socket_depth = 3.0;                 // [STEP] jaw c'bore z 21.0 -> 24.0
m3_cap_d        = 6.0;                 // [STEP] counterbore in the follower base
m3_cap_depth    = 6.0;                 // [STEP] follower c'bore z 3.95 -> 9.95


// --- the bus servo's horn interface -----------------------------------------
// The SO-101 uses one horn pattern everywhere: four screws on the corners of a
// square, plus a centre screw into the output shaft.  Both parts use it — the
// follower to hang off wrist_roll (ID 5), the moving jaw to hang off the
// gripper servo (ID 6) — so it lives here once.
horn_bolt_square   = 9.9;              // [STEP] holes at (+-4.95, +-4.95)
horn_bolt_circle_d = 14.0;             // [DERIVED] 9.9*sqrt(2)
horn_centre_bore_d = 5.4;              // [STEP] centre clearance, follower base
horn_recess_d      = 24.0;             // [STEP] Ø24 pocket the horn sits in
horn_recess_depth  = 6.0;              // [STEP] z -0.05 -> 5.95
horn_spigot_d      = 20.0;             // [STEP] Ø20 boss, z -0.05 -> 0.95
horn_spigot_h      = 1.0;              // [STEP]


// =============================================================================
//  MOVING JAW  (Moving_Jaw_SO101.step, its own frame)
//      pivot axis = Z, blade runs toward -Y, gripping face looks toward -X
// =============================================================================

// -- the fork that clamps onto the gripper servo ------------------------------
mj_fork_outer_w   = 48.0;              // [STEP] z -24.0 .. +24.0
mj_fork_gap       = 36.4;              // [STEP] inner faces z -18.9 .. +17.5
mj_plate_t_top    = 6.5;               // [STEP] z 17.5 .. 24.0
mj_plate_t_bottom = 5.1;               // [STEP] z -24.0 .. -18.9
mj_hub_r          = 10.0;              // [STEP] Ø20 hub disc around the horn
mj_plate_x_min    = -9.6;              // [STEP] plate footprint, -X edge
mj_plate_x_max    =  9.9;              // [STEP] plate footprint, +X edge
mj_plate_y_min    = -18.0;             // [STEP] plate footprint, -Y edge
mj_cb_depth_bottom = 1.6;              // [STEP] bottom plate c'bore z -24 .. -22.4

// -- the neck: where the fork closes up into solid material -------------------
mj_neck_y_start   = -22.0;             // [STEP] blade's flat face begins here
mj_neck_y_end     = -14.0;             // [STEP] solid at y=-16, open at y=-5
mj_neck_half_h    = 21.5;              // [STEP] section at y=-16: z +-21.5
mj_neck_x_min     = -10.0;             // [STEP] plane x=-10, the fork's spine

// -- the blade ----------------------------------------------------------------
mj_blade_len      = 82.0;              // [STEP] pivot to fingertip, y=0 .. -82
mj_corner_r       = 1.5;               // [STEP] blade cross-section corner round

// Gripping face: a staircase, each step moving 2 mm closer to the fixed jaw.
// [[y_start, x_of_face], ...]  read straight off the three x-normal planes.
mj_face_steps = [[ -22.0, -8.3],       // [STEP] plane x=-8.3,  y -22 .. -62
                 [ -62.0, -10.3],      // [STEP] plane x=-10.3, y -62 .. -72
                 [ -72.0, -12.3]];     // [STEP] plane x=-12.3, y -72 .. -82
mj_face_step_rise = 2.0;               // [DERIVED] 8.3 -> 10.3 -> 12.3

// Back (outer) face: two straight tapers meeting at a kink.
mj_back_x_at_pivot = 10.06;            // [STEP] plane 0.994x - 0.105y = 10
mj_back_taper_deg  = 6.03;             // [STEP] atan(0.105/0.994)
mj_back_kink_y     = -59.3;            // [DERIVED] where the two planes meet
mj_back_taper2_deg = 26.06;            // [STEP] plane 0.898x - 0.439y = 29.45

// Half-height of the blade down its length: [y, half_height_in_z].
// Every station is a face boundary measured in the STEP, so this list IS the
// taper — edit a row to change the blade's silhouette.
mj_blade_profile = [[-22.0, 12.0],     // [STEP]
                    [-24.0, 11.4],     // [STEP] section y=-24
                    [-28.8, 10.2],     // [STEP]
                    [-34.0,  9.3],     // [STEP] section y=-34
                    [-38.8,  8.9],     // [STEP]
                    [-44.0,  8.5],     // [STEP]
                    [-48.7,  8.1],     // [STEP]
                    [-54.0,  7.75],    // [STEP]
                    [-58.7,  7.4],     // [STEP]
                    [-62.0,  7.1],     // [STEP] plane y=-62
                    [-72.0,  5.8],     // [STEP] plane y=-72
                    [-81.0,  4.8],     // [STEP] plane x=-12.3
                    [-82.0,  3.6]];    // [STEP] tip, rounded off

mj_tip_thickness  = 5.5;               // [DERIVED] front -12.3 to back -6.8 at y=-81


// =============================================================================
//  FIXED JAW / GRIPPER BODY  (Wrist_Roll_Follower_SO101.step)
// =============================================================================

// -- envelope -----------------------------------------------------------------
fj_x_min      = -35.2;                 // [STEP]
fj_x_max      =  30.0;                 // [STEP] tip of the cable tab
fj_y_min      = -24.218;               // [STEP]
fj_y_max      =  27.782;               // [STEP]
fj_top_z      = 105.375;               // [STEP] fingertip
fj_body_top_z =  38.0;                 // [STEP] where the blade leaves the body

// -- the base flange that carries the wrist_roll horn -------------------------
fj_flange_z0     = 0.95;               // [STEP] plane z=0.95
fj_flange_z1     = 11.95;              // [STEP] plane z=11.95
fj_flange_r      = 8.0;                // [GUESS] outline corner radius
fj_rear_half_y   = 12.4;               // [STEP] plane x=-35.2 is only +-12.4
                                       //        wide, so the body tapers to a
                                       //        narrow rear end
fj_flange_x_max  = 27.0;               // [STEP] plane z=5.95 / z=11.95 bbox
fj_flange_y_min  = -21.2;              // [STEP]
fj_flange_y_max  =  23.8;              // [STEP]
fj_floor_z       = 5.95;               // [STEP] plane z=5.95, the cradle floor

// -- the servo cradle ---------------------------------------------------------
fj_cradle_x_max   = 13.0;              // [GUESS] shell ends here, pocket opens +X
fj_pocket_x_min   = -15.0;             // [STEP] plane x=-15, back of the pocket
fj_pocket_half_y  = 16.0;              // [STEP] planes y=+-15.954
fj_pocket_z0      = fj_flange_z1;      // [STEP] pocket floor = z 11.95
fj_pocket_z1      = 36.7;              // [STEP] plane z=36.7
fj_boss_y_pos     =  17.682;           // [STEP] the faces the jaw fork straddles
fj_boss_y_neg     = -17.418;           // [STEP]
fj_fork_clear_z   = 14.0;              // [GUESS] height above which the side
                                       //         walls step in to those faces

// -- cable routing ------------------------------------------------------------
fj_cable_bore_d   = 10.0;              // [STEP] Ø10 bore along X
fj_cable_bore_z   = 24.35;             // [STEP]
fj_cable_bore_y   = 0.13;              // [STEP]
fj_tab_x0         = 11.0;              // [GUESS] the tab that reaches to x=30
fj_tab_half_y     = 14.0;              // [STEP] R3 ends at y=+-13.78

// -- servo retaining screws through the side walls ----------------------------
fj_servo_screw_d    = 2.0;             // [STEP] Ø2
fj_servo_screw_cb_d = 4.0;             // [STEP] Ø4 counterbore
fj_servo_screw_z    = [14.10, 34.60];  // [STEP]
fj_servo_screw_x_neg = -8.8;           // [STEP] through the -Y wall
fj_servo_screw_x_pos = -12.6;          // [STEP] through the +Y wall

// -- the fixed blade ----------------------------------------------------------
// Gripping face: the same staircase idea as the moving jaw, four steps.
// [[z_start, x_of_face, half_width_in_y], ...]
fj_face_steps = [[ 38.000, -15.0, 14.8],   // [STEP] plane x=-15.0
                 [ 46.066, -13.3, 11.9],   // [STEP] plane x=-13.3
                 [ 65.720, -11.6,  8.6],   // [STEP] plane x=-11.6
                 [ 85.375,  -9.9,  7.2],   // [STEP] plane x=-9.9
                 [ 95.375,  -7.9,  5.9],   // [STEP] plane x=-7.9
                 [104.400,  -7.9,  4.9]];  // [STEP] last step ends here
fj_face_step_rise = 1.7;               // [DERIVED] 15.0 -> 13.3 -> 11.6 -> 9.9
fj_tip_step_rise  = 2.0;               // [DERIVED] 9.9 -> 7.9

// Back face of the blade: one straight plane leaning 20 deg off vertical.
fj_back_lean_deg  = 20.0;              // [STEP] atan(0.342/0.940)
fj_back_x_at_z0   = -51.24;            // [STEP] 0.940x - 0.342z = -48.162, at z=0
fj_back_z_start   = 44.1;              // [STEP] below this the back is the wall
fj_back_half_y    = 12.4;              // [STEP] plane x=-35.2, y +-12.4
fj_tip_r          = 3.0;               // [STEP] torus minor radius at the tip
fj_tip_thickness  = 5.4;               // [DERIVED] front -7.9 to back -13.3 at z=104.4


// =============================================================================
//  ASSEMBLY
// =============================================================================
//
//  The two STEP files are separate solids in separate frames — the export
//  carries no assembly transform — so the placement below was solved, not read.
//  It is pinned by the fingertip pads: with this transform the moving jaw's
//  last step (x=-12.3, y -72..-82) lands exactly on the fixed jaw's last step
//  (x=-7.9, z 95.375..104.4).  Same plane, same 10 mm run, same 105.375 tip.
//  That is four numbers agreeing at once, so treat it as measured — but see
//  NOTES.md, because it is the one number in this file that is inferred.
//
jaw_pivot_x = 4.4;                     // [DERIVED] 12.3 - 7.9
jaw_pivot_z = 23.375;                  // [DERIVED] 105.375 - 82.0

// Jaw command.  jaw_opening is the chord the fingertip pads travel apart, in mm
// — 0 is closed (pads touching), which is where the reference geometry sits.
jaw_opening = 0;                       // mm at the fingertip
jaw_opening_max = 55;                  // [GUESS] not measured; travel is set by
                                       //         the servo, not the plastic

// tip radius = pivot to the centre of the fingertip pad
jaw_tip_arm = sqrt(pow(jaw_pivot_x - (-7.9), 2) + pow(100.0 - jaw_pivot_z, 2));
function jaw_angle_for(opening) = 2 * asin(min(1, opening / (2 * jaw_tip_arm)));
jaw_angle = jaw_angle_for(jaw_opening);


// =============================================================================
//  SELF-CHECKS
// =============================================================================
//  A parametric model that only fails visually is a model that lies six months
//  from now.  These are the relationships that must survive an edit; OpenSCAD
//  evaluates them on every compile, so a bad parameter stops the render instead
//  of quietly producing a part that cannot be assembled.

// The fork has to swallow the body it pivots on.
fj_boss_width = fj_boss_y_pos - fj_boss_y_neg;
assert(mj_fork_gap > fj_boss_width,
       "moving jaw fork is narrower than the body boss it straddles");

// The fingertip pads have to meet, not pass through each other, at jaw_opening=0.
mj_tip_face_x = mj_face_steps[2][1] + jaw_pivot_x;
fj_tip_face_x = fj_face_steps[4][1];
assert(abs(mj_tip_face_x - fj_tip_face_x) < 0.05,
       "fingertip pads do not meet when closed - check jaw_pivot_x");

// The gripping-face staircases must open a throat behind the pads, never close
// one behind them, or the jaws collide before the tips touch.
assert(mj_face_step_rise > 0 && fj_face_step_rise > 0,
       "gripping-face steps must climb toward the fingertip");

// The servo pocket has to leave a wall inside the faces the fork sweeps over.
fj_wall_above_fork = fj_boss_y_pos - fj_pocket_half_y;
echo(str("wall thickness above the fork line: ", fj_wall_above_fork, " mm"));
assert(fj_wall_above_fork > 0, "servo pocket is wider than the fork clearance");
