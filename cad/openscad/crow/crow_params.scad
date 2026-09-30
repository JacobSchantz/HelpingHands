// =============================================================================
//  crow_params.scad — the New Caledonian crow beak, as a list of numbers.
// =============================================================================
//
//  A drop-in jaw pair for the SO-101, shaped after the bill of the New
//  Caledonian crow (Corvus moneduloides) — the tool-using crow whose bill is
//  the reason it is usually called the most dexterous beak there is.
//
//  WHAT IS BORROWED FROM THE BIRD, AND WHY IT IS USEFUL HERE
//  ---------------------------------------------------------
//  The NC crow's bill is unusual among corvids in three specific ways, and all
//  three are mechanically interesting for a gripper:
//
//    1. The culmen (the top ridge of the upper mandible) is nearly STRAIGHT,
//       where most crows are decurved.  A straight upper jaw puts the tip where
//       the bird can see it and keeps the contact force pointing down the
//       blade instead of peeling off it.        -> crow_culmen, a straight line.
//
//    2. The lower mandible is UPTURNED toward the tip.  With a straight upper
//       and an upturned lower, the two tips converge nose-up and meet as a
//       forceps rather than a pair of shears.   -> crow_tomium bends toward the
//                                                  upper jaw over its last 20 mm.
//
//    3. The bill is DEEP at the base and strongly compressed side-to-side.
//       Deep base = the load path from the tip is short and stiff.  Compressed
//       = the tip can get into a gap.           -> crow_width, 29.6 mm wide at
//                                                  the root, 3.2 mm at the tip.
//
//  WHAT THIS IS NOT: a scan.  Every number below is drawn, not measured off a
//  specimen — the brief was "that general shape".  The numbers that ARE
//  measured are the ones that make it bolt on, and those all come from
//  ../params.scad, untouched: the wrist_roll horn pattern, the servo cradle,
//  the fork, and the jaw pivot.  Nothing in this file moves an interface.
//
//  FRAME: the wrist-roll follower's frame from ../params.scad.
//      +Z  up the beak, from the horn face toward the tip
//      +X  the direction the jaws open toward (upper jaw is at -X of the
//          contact line, lower jaw at +X)
//      +Y  along the jaw pivot axis
//  In bird terms, -X is "up" (dorsal, toward the culmen) and +Z is "forward".
//
// =============================================================================

include <../params.scad>

// --- envelope ----------------------------------------------------------------
crow_root_z = fj_body_top_z;           // 38.0   blade leaves the servo cradle
crow_tip_z  = fj_top_z;                // 105.4  same reach as the stock gripper
crow_corner_r = 1.2;                   // cross-section corner round


// --- the tomial line: where the two mandibles meet -------------------------
// In a bird the tomia are the opposing edges of the two mandibles.  Here they
// are one shared curve: both jaws are built to it, so at crow_opening = 0 the
// beak closes along its whole length instead of touching at one point.
// Straight at ~5.9 deg for the first 46 mm, then it turns back toward the
// upper jaw — that turn IS the upturned tip.  [z, x]
crow_tomium = [[ 38.000, -15.00],
               [ 50.000, -13.70],
               [ 62.000, -12.40],
               [ 74.000, -11.15],
               [ 84.000, -10.15],      // straight to here: 5.9 deg
               [ 92.000,  -9.90],      // the upturn starts
               [ 98.000, -10.50],
               [102.500, -11.60],
               [105.375, -12.80]];     // ~28 deg of upturn over the last 21 mm     // ~13 deg of upturn over the last 19 mm

function crow_tomium_x(z) = lookup(z, crow_tomium);
function crow_tomium_lean(z) =                    // deg off +Z, toward +X
    atan((crow_tomium_x(min(crow_tip_z, z + 0.5)) -
          crow_tomium_x(max(crow_root_z, z - 0.5))) /
         (min(crow_tip_z, z + 0.5) - max(crow_root_z, z - 0.5)));


// --- the culmen: the upper mandible's outer ridge ---------------------------
// The signature feature.  A straight chord from the back of the servo cradle to
// the tip, with ~1 mm of convex bulge — enough to read as a bill and not as a
// wedge, nowhere near the hook a common crow has.  [z, x]
crow_culmen = [[ 38.000, -35.20],
               [ 50.000, -32.10],
               [ 62.000, -28.90],
               [ 74.000, -25.40],
               [ 84.000, -22.20],
               [ 92.000, -19.50],
               [ 98.000, -17.50],
               [102.500, -15.95],
               [105.375, -15.00]];
function crow_culmen_x(z) = lookup(z, crow_culmen);


// --- the gonys: the lower mandible's outer keel -----------------------------
// Steep through the rami (where it leaves the fork), then a long flat run, then
// the gonydeal angle at z=86 where it kicks up to the tip.  [z, x]
crow_lower_root_z = 45.375;            // = jaw y -22, the stock neck/blade join
crow_gonys = [[ 45.375,  12.10],
              [ 52.000,   8.70],
              [ 58.000,   5.40],
              [ 62.000,   3.30],
              [ 70.000,   1.30],
              [ 78.000,  -0.10],
              [ 84.000,  -1.15],       // gonydeal angle: 11.4 deg -> 23.8 deg
              [ 92.000,  -3.30],
              [ 98.000,  -5.90],
              [102.500,  -8.50],
              [105.375, -10.60]];
function crow_gonys_x(z) = lookup(z, crow_gonys);


// --- the commissure: where the lower mandible leaves the tomial line --------
// A beak's mandibles part at the gape.  Ours have to: the lower jaw's neck has
// to clear the fixed jaw's body as it swings.  The lower tomium ramps out from
// the neck and rejoins the shared line at crow_join_z.
crow_join_z  = 62.0;
crow_join_x  = -12.40;                 // = crow_tomium_x(crow_join_z)
crow_lower_tomium = [[45.375, -5.60],  // = jaw-frame x -10, the stock neck face
                     [52.000, -8.60],
                     [58.000, -11.00],
                     [crow_join_z, crow_join_x]];
function crow_lo_tomium_x(z) = (z < crow_join_z) ? lookup(z, crow_lower_tomium)
                                                 : crow_tomium_x(z);


// --- lateral profile: shared, so the two tomia register ---------------------
// One width curve for both mandibles.  In a bird the mandibles are the same
// width where they meet; here that is also what stops the jaws shearing past
// each other.  [z, half_width_in_y]
crow_width = [[ 38.000, 14.80],        // = fj_face_steps[0][2], the body's width
              [ 45.000, 13.00],
              [ 55.000, 10.20],
              [ 62.000,  9.40],
              [ 70.000,  8.30],
              [ 78.000,  7.00],
              [ 84.000,  5.90],
              [ 92.000,  4.40],
              [ 98.000,  3.30],
              [102.500,  2.40],
              [105.375,  1.70]];
function crow_half_y(z) = lookup(z, crow_width);


// --- the tool notch: the crow's actual trick --------------------------------
// NC crows hold a stick in the bill and keep hold of it while probing.  A
// 90-degree V cut into both tomia, on the contact line, does the same job: a
// rod seats on four line contacts instead of skidding on two flat faces, and
// the clamping force is normal to the V, which is the only direction these jaws
// can push.  (A bore down the beak axis would be prettier and useless — these
// jaws cannot squeeze along Z.)
crow_notch_z     = 78.0;               // ~40% up the working length
crow_notch_depth = 4.0;                // per jaw; holds up to ~5.6 mm closed,
                                       // larger rods with the jaws cracked open
crow_notch_len   = 60;                 // through the full width

// What to command to chuck a rod.  Two opposing 90-degree Vs whose apexes are
// s apart hold a circle of radius (s/2 + depth)/sqrt(2), so a rod of diameter d
// needs s = 2*(d*sqrt(2)/4 - depth) of separation at the notch -- scaled out to
// the tip, because crow_opening is measured there.  A Ø6 mm rod comes out at
// 0.72 mm of gape: the beak chucks it essentially shut.
crow_notch_r = sqrt(pow(crow_tomium_x(crow_notch_z) - jaw_pivot_x, 2) +
                    pow(crow_notch_z - jaw_pivot_z, 2));
function crow_opening_for_rod(d) =
    max(0, (d / 2 * sqrt(2) - crow_notch_depth) * 2 * crow_tip_arm / crow_notch_r);
crow_rod_d = 6.0;                      // the rod the demo render chucks


// --- the throat: the hook, at the back of the beak (plans/crow_gripper.md D3/D4)
// A U-shaped pocket cut into the UPPER mandible only, opening onto the tomial
// line.  Open, a bar (mug handle, bag strap, cable, drawer pull) slides into it;
// shut, the lower mandible's tomium runs straight across the mouth and the bar
// is enclosed.  Loads toward the culmen (-X) and along the beak (+-Z) are
// carried by the upper mandible's own walls; only a load straight out of the
// mouth (+X) reaches the gate, i.e. the servo.  That is "shut the gate"
// instead of "squeeze hard enough".
//
// Because the throat is a pocket BEHIND the tomial line and not a dip IN it,
// the lower mandible is untouched and the closed-form interference proof below
// still holds unchanged -- material only comes off the fixed jaw.
crow_throat_z     = 67.5;              // centre, along the tomium
crow_throat_d     = 9.0;               // [GUESS] the bar it encloses; mug handles
                                       //         and straps are ~6-10 mm
crow_throat_depth = 9.0;               // how far into the upper mandible, from
                                       // the tomium to the bottom of the U
crow_throat_web_min = 1.5;             // web left between throat and tool notch
crow_throat_wall_min = 3.0;            // wall left behind the U, to the culmen

crow_throat_r = sqrt(pow(crow_tomium_x(crow_throat_z) - jaw_pivot_x, 2) +
                     pow(crow_throat_z - jaw_pivot_z, 2));


// --- jaw command -------------------------------------------------------------
// Same pivot as the stock gripper, so the servo, horn and travel are unchanged.
crow_tip_arm = sqrt(pow(crow_tomium_x(crow_tip_z) - jaw_pivot_x, 2) +
                    pow(crow_tip_z - jaw_pivot_z, 2));
function crow_angle_for(opening) = 2 * asin(min(1, opening / (2 * crow_tip_arm)));
crow_opening     = 0;                  // mm of gape at the tip
crow_opening_max = 50;                 // [GUESS] set by the servo, not the plastic
crow_angle       = crow_angle_for(crow_opening);

// Gape at the tip that swings the gate clear of a bar of diameter d in the
// throat (+1 mm to get it in without rubbing).  Chord at the throat radius,
// scaled out to the tip.
function crow_opening_for_throat(d) = (d + 1.0) * crow_tip_arm / crow_throat_r;


// =============================================================================
//  THE DOCK: one interface, two hosts  (plans/crow_gripper.md section 10)
// =============================================================================
//  The crow is used two ways with the SAME cartridge -- upper mandible body,
//  gripper servo (ID 6), lower mandible, wrist camera:
//      on the arm:  cartridge -> dock -> wrist PUCK -> wrist_roll horn (ID 5)
//      in the hand: cartridge -> dock -> HANDLE (trigger + phone tracker)
//  The puck carries the SO-101's own horn pattern, untouched, so the arm
//  interface still does not move (D1).  What changed is that the cartridge no
//  longer bolts straight to the horn: those four screws sit UNDER the gripper
//  servo, so taking the stock body off means taking the servo out.  A dovetail
//  that slides on and takes one cross-pin is the fix.
//
//  Frame: the cartridge keeps the follower frame from ../params.scad, so every
//  beak number above is unchanged.  The dock plane is the old flange bottom,
//  z = fj_flange_z0.  The puck sits below it; the horn face is dock_lift lower.
crow_mount = "dock";                   // "dock" | "horn" (stock direct bolt)

dock_z          = fj_flange_z0;        // 0.95  cartridge sits on this plane
dock_puck_h     = 10.0;                // horn face -> dock plane
dock_puck_d     = 34.0;                // < the cartridge footprint
dock_horn_floor = 4.0;                 // puck floor above the horn recess
dock_head_h     = 2.2;                 // [GUESS] low-head M3 (DIN 7984) c'bore
dock_rail_h     = 6.0;                 // dovetail height
dock_rail_w_top = 26.0;                // wide enough to swallow the horn c'bores
dock_rail_flank = 30.0;                // deg off vertical: a 60 deg dovetail
dock_rail_len   = dock_puck_d;         // along X; open end toward +X
dock_clear      = 0.2;                 // per side, FDM slide fit
dock_pin_d      = 3.2;                 // M3 cross-pin, along Y
dock_pin_x      = 10.0;                // pin position along the rail
dock_y          = -0.22;               // = the stock horn centre's y offset

dock_rail_w_base = dock_rail_w_top - 2 * dock_rail_h * tan(dock_rail_flank);
dock_lift        = dock_puck_h - dock_z;   // how much further out the tip is
dock_pin_z       = dock_z + dock_rail_h / 2;


// =============================================================================
//  THE WRIST CAMERA -- where a crow's eye is
// =============================================================================
//  New Caledonian crows have unusually wide binocular overlap and a straight
//  bill, so the bill tip sits inside the visual field while they work a tool
//  (Troscianko et al. 2012, Nature Communications).  Same idea: the camera
//  rides on the CARTRIDGE, lateral like an eye, toed in so the tip, the throat
//  and the gape are all in frame in both modes.  It is behind the hand's
//  line of sight in handheld mode, so the human arm stays out of the picture.
//  Mounted outside |y| = 24, the lower mandible's fork can never sweep it.
cam_board    = 32.0;                   // [GUESS] common 32x32 mm UVC board
cam_hole_sq  = 28.0;                   // [GUESS] M2 holes on a 28 mm square
cam_lens_d   = 16.0;                   // clearance hole for the lens barrel
cam_fov      = 110.0;                  // [GUESS] diagonal FOV to buy: >= 110
cam_pos      = [-12.0, 36.0, 44.0];    // lens centre, follower frame
cam_mount_screw_x = [-18.0, -4.0];     // M3 into heat-set inserts in the flange's
cam_mount_screw_z = 7.0;               //   +Y face, clear of the dock groove
cam_aim_z    = 82.0;                   // aims at the tomial line here
cam_aim      = [crow_tomium_x(cam_aim_z), 0, cam_aim_z];
cam_toe      = atan2(cam_pos[1] - cam_aim[1], cam_aim[2] - cam_pos[2]);  // about X

// angle off the optical axis to a point, in degrees
function cam_off_axis(p) =
    let(a = cam_aim - cam_pos, b = p - cam_pos,
        c = (a * b) / (norm(a) * norm(b)))
    acos(min(1, c));


// =============================================================================
//  THE HANDLE -- handheld host
// =============================================================================
//  Pistol grip under the dock.  With the culmen up (-X up, bird posture) the
//  grip hangs toward +X and rakes back toward the user (-Z).  The trigger is a
//  back-driven STS3215 read as a LEADER; the cartridge's own ID 6 follows it,
//  so the jaw that touches the object is driven by the same servo, at the
//  same torque limit, as on the arm -- and gripper.pos is recorded from ID 6
//  itself, not from the trigger.  The phone (ARKit pose) clips on the handle
//  only: it never rides on the arm.
handle_head    = [[-20, 20], [-21, 21], [-64, 0]];   // x, y, z, relative to the dock plane
sts_body       = [24.7, 35.0, 45.2];   // [GUESS] STS3215 w x h(shaft) x l, no ears
sts_shaft_from_end = 11.0;             // [GUESS] shaft centre from the body's end
handle_servo_c = [2.35, 0, -26.0];     // pocket centre, relative to the dock plane
grip_len       = 100.0;                // along its axis; adult palm is ~75-95
grip_depth     = 32.0;                 // front to back (Z)
grip_width     = 30.0;                 // side to side (Y)
grip_rake      = 15.0;                 // deg back from +X
grip_front_z   = -30.0;                // front face at the top of the grip
trigger_reach  = 58.0;                 // [GUESS] backstrap -> trigger pad; tune
                                       //         by printing, 55-70 fits most
trigger_travel = 28.0;                 // deg of lever for full open -> shut

phone          = [71.6, 147.6, 7.8];   // [GUESS] short x long x thick, landscape
phone_gap      = 4.0;                  // head top -> phone edge
phone_z        = -44.0;                // phone back (camera side), rel. dock plane
phone_cam      = [14.0, 18.0];         // [GUESS] rear lens centre from the
                                       //  phone's top edge / +Y end
phone_window   = 40.0;                 // square window for the camera bump


// =============================================================================
//  SELF-CHECKS
// =============================================================================
//  NOTES.md section 5 says the thing this model was missing is an interference
//  test.  The two checks below are that test, done in closed form rather than
//  by eye, plus the usual can-it-be-assembled ones.

// (1) The gape has to open, not scissor.  The moving jaw turns about the pivot,
// so a point only moves along its own circle about that pivot.  If the radius
// from the pivot grows strictly along the tomial line, the rotated lower tomium
// is everywhere inside the fixed one and the jaws cannot touch except at 0.
// That is a stronger statement than "it looked fine in the preview".
function crow_pivot_r(p) = sqrt(pow(p[1] - jaw_pivot_x, 2) +
                                pow(p[0] - jaw_pivot_z, 2));
function crow_r_climbs(t) =
    len([for (i = [0 : len(t) - 2]) if (crow_pivot_r(t[i + 1]) <= crow_pivot_r(t[i])) 1]) == 0;

assert(crow_r_climbs(crow_tomium),
       "tomial line doubles back toward the pivot - the jaws will collide as they open");
assert(crow_r_climbs(concat(crow_lower_tomium, [for (p = crow_tomium) if (p[0] > crow_join_z) p])),
       "lower mandible's ramus doubles back toward the pivot");

// (2) At closed, the lower mandible must sit on the +X side of the upper's face
// everywhere, or the two solids overlap before the servo has done anything.
assert(len([for (p = crow_lower_tomium) if (crow_lo_tomium_x(p[0]) < crow_tomium_x(p[0]) - 0.001) 1]) == 0,
       "lower mandible cuts through the upper at crow_opening = 0");

// (3) Both mandibles have to survive the printer and the notch.
crow_upper_tip_t = crow_tomium_x(crow_tip_z) - crow_culmen_x(crow_tip_z);
crow_lower_tip_t = crow_gonys_x(crow_tip_z) - crow_tomium_x(crow_tip_z);
crow_tip_min_t = 2.0;                  // three 0.4 mm perimeters plus a core
assert(crow_upper_tip_t > crow_tip_min_t && crow_lower_tip_t > crow_tip_min_t,
       "beak tip is thinner than crow_tip_min_t - it will not print");
assert(crow_culmen_x(crow_notch_z) + crow_notch_depth < crow_tomium_x(crow_notch_z) - 1.5,
       "tool notch is deeper than the upper mandible is thick at crow_notch_z");
assert(crow_half_y(crow_notch_z) * 2 > crow_notch_depth * 2 + 2.0,
       "tool notch is wider than the beak at crow_notch_z");

// (4) The mandibles taper monotonically - a beak that gets fatter toward the
// tip is a beak that was typed wrong.
function crow_thins(f) =
    len([for (i = [0 : len(crow_width) - 2])
         if (crow_width[i + 1][1] > crow_width[i][1]) 1]) == 0;
assert(crow_thins(0), "crow_width must narrow from root to tip");

// (5) The throat: it has to sit on the part of the tomium the gate closes
// (above the commissure), leave a web to the tool notch, and leave a wall.
crow_throat_lo = crow_throat_z - crow_throat_d / 2;
crow_throat_hi = crow_throat_z + crow_throat_d / 2;
assert(crow_throat_lo >= crow_join_z + 0.5,
       "throat mouth runs below the commissure - the lower mandible cannot close it");
assert((crow_notch_z - crow_notch_depth) - crow_throat_hi >= crow_throat_web_min,
       "throat runs into the tool notch");
assert((crow_tomium_x(crow_throat_z) - crow_throat_depth) - crow_culmen_x(crow_throat_z)
           >= crow_throat_wall_min,
       "throat is deeper than the upper mandible can carry");
assert(crow_throat_depth >= crow_throat_d / 2,
       "throat is shallower than a half-circle - it is a notch, not a hook");

// (6) The dock: the rail must swallow the horn screw heads, and the servo
// pocket must keep a floor over the groove.
assert(dock_rail_w_base / 2 > horn_bolt_square / 2 + m3_cap_d / 2,
       "dovetail base is narrower than the horn screw counterbores it covers");
assert(fj_pocket_z0 - (dock_z + dock_rail_h + dock_clear) >= 3.0,
       "dock groove leaves less than 3 mm of floor under the gripper servo");
assert(dock_puck_h - horn_recess_depth >= dock_horn_floor,
       "puck is too thin to floor the horn recess");

// (7) Framing: the tip (shut and fully open) and the throat must all be inside
// the camera's field.  Cheap to get wrong, cheap to check -- hand_1_0.md 3.
crow_open_tip = [jaw_pivot_x + (crow_tomium_x(crow_tip_z) - jaw_pivot_x) * cos(crow_angle_for(crow_opening_max))
                              + (crow_tip_z - jaw_pivot_z) * sin(crow_angle_for(crow_opening_max)),
                 0,
                 jaw_pivot_z - (crow_tomium_x(crow_tip_z) - jaw_pivot_x) * sin(crow_angle_for(crow_opening_max))
                              + (crow_tip_z - jaw_pivot_z) * cos(crow_angle_for(crow_opening_max))];
cam_tip_deg    = cam_off_axis([crow_tomium_x(crow_tip_z), 0, crow_tip_z]);
cam_throat_deg = cam_off_axis([crow_tomium_x(crow_throat_z), 0, crow_throat_z]);
cam_open_deg   = cam_off_axis(crow_open_tip);
assert(max(cam_tip_deg, cam_throat_deg, cam_open_deg) < cam_fov / 2 - 5,
       "wrist camera cannot see the tip, the throat and the open gape at once");
assert(abs(cam_pos[1]) - cam_board / 2 * cos(cam_toe) > mj_fork_outer_w / 2,
       "camera board is inside the lower mandible fork's sweep");

echo(str("crow beak: reach ", crow_tip_z, " mm, tip arm ", crow_tip_arm,
         " mm, gape at max = ", crow_angle_for(crow_opening_max), " deg"));
echo(str("upper tip thickness ", crow_upper_tip_t,
         " mm, lower tip thickness ", crow_lower_tip_t, " mm"));
echo(str("tool notch: holds Ø5.66 mm shut; Ø6 needs ", crow_opening_for_rod(6.0),
         " mm of gape, Ø10 needs ", crow_opening_for_rod(10.0), " mm"));
echo(str("throat: encloses Ø", crow_throat_d, " mm at z ", crow_throat_z,
         ", lever ", crow_tip_arm / crow_throat_r, "x the tip's force; gate clears it at ",
         crow_opening_for_throat(crow_throat_d), " mm of gape"));
echo(str("dock: tip is ", crow_tip_z + dock_lift, " mm from the wrist_roll horn face (",
         crow_tip_z, " + ", dock_lift, " mm of puck)"));
echo(str("camera: off-axis tip ", cam_tip_deg, " deg, throat ", cam_throat_deg,
         " deg, open tip ", cam_open_deg, " deg, of ", cam_fov / 2, " available"));
