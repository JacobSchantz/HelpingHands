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


// --- jaw command -------------------------------------------------------------
// Same pivot as the stock gripper, so the servo, horn and travel are unchanged.
crow_tip_arm = sqrt(pow(crow_tomium_x(crow_tip_z) - jaw_pivot_x, 2) +
                    pow(crow_tip_z - jaw_pivot_z, 2));
function crow_angle_for(opening) = 2 * asin(min(1, opening / (2 * crow_tip_arm)));
crow_opening     = 0;                  // mm of gape at the tip
crow_opening_max = 50;                 // [GUESS] set by the servo, not the plastic
crow_angle       = crow_angle_for(crow_opening);


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

echo(str("crow beak: reach ", crow_tip_z, " mm, tip arm ", crow_tip_arm,
         " mm, gape at max = ", crow_angle_for(crow_opening_max), " deg"));
echo(str("upper tip thickness ", crow_upper_tip_t,
         " mm, lower tip thickness ", crow_lower_tip_t, " mm"));
echo(str("tool notch: holds Ø5.66 mm shut; Ø6 needs ", crow_opening_for_rod(6.0),
         " mm of gape, Ø10 needs ", crow_opening_for_rod(10.0), " mm"));
