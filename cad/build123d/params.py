"""Every dimension of the SO-101 gripper, as a named Python variable.

CAD bake-off, tool 2 of 3 (build123d).  See NOTES.md for the verdict and for
the honest list of what is measured versus what is approximated.

Context
-------
``plans/gripper_bet.md``  — why a gripper at all (Hand 1.0 / Hand 2.0).
``plans/hand_1_0.md``     — §6 provisionally names OpenSCAD as the source of
                            truth for printable parts and flags build123d as
                            "the escape hatch if fillets or precise fits become
                            the blocker".  This directory is that escape hatch
                            being tried on a real part.  §2 is what will
                            actually get edited here: the fingertip geometry,
                            the pad width, the thin leading edge.

Source of every number
----------------------
``[STEP]``    read out of the reference B-rep by ``measure_reference.py``.  Run
              it to re-derive any of them; it reports exact cylinder radii and
              exact plane normals off the analytic surfaces, not off a mesh.
``[DERIVED]`` computed from ``[STEP]`` numbers.
``[ASSUMED]`` mine.  Every one of these is listed again in NOTES.md.

Frames
------
Each part is modelled in its own STEP frame, so a measured number can be typed
in unchanged.  ``gripper.py`` transforms them into one assembly.

Moving jaw frame
    +Z  the pivot axis (the gripper servo's output shaft)
    -Y  out along the blade, toward the fingertip
    -X  the direction the gripping face looks
    origin = centre of the servo horn bolt circle

Wrist-roll follower frame
    +Z  up the fixed jaw, from the wrist_roll horn face toward the fingertip
    +X  toward the back of the body (away from the jaw opening)
    origin = centre of the wrist_roll servo horn bolt circle
"""

# ---------------------------------------------------------------------------
#  fasteners — the SO-101's gripper screws are all M3
# ---------------------------------------------------------------------------
M3_CLEAR_D = 3.2          # [STEP] Ø3.2 clearance holes, both parts
M3_SOCKET_D = 5.4         # [STEP] socket-head counterbore in the moving jaw
M3_CAP_D = 6.0            # [STEP] counterbore in the follower base plate
M2_CLEAR_D = 2.0          # [STEP] servo mounting screws, through the side walls
M2_HEAD_D = 4.0           # [STEP] their head recess

# ---------------------------------------------------------------------------
#  the bus servo horn interface — one pattern, used by both parts
# ---------------------------------------------------------------------------
HORN_BOLT_SQUARE = 9.9    # [STEP] four screws at (±4.95, ±4.95)
HORN_DISC_D = 20.0        # [STEP] Ø20 horn disc
HORN_BOSS_D = 24.0        # [STEP] Ø24 boss/pocket the horn seats in
HORN_CENTRE_BORE_D = 5.4  # [STEP] centre-screw clearance

# ===========================================================================
#  MOVING JAW  (Moving_Jaw_SO101.step)
# ===========================================================================

# -- the fork that clamps over the gripper servo ----------------------------
MJ_FORK_HALF_H = 24.0         # [STEP] outer faces at z = ±24.0
MJ_TOP_PLATE_Z = (17.5, 24.0)       # [STEP] 6.5 thick
MJ_BOTTOM_PLATE_Z = (-24.0, -18.9)  # [STEP] 5.1 thick
MJ_HUB_D = 20.0               # [STEP] Ø20 hub disc around the horn
MJ_HORN_RECESS_DEPTH = 1.5    # [STEP] Ø20 pocket, z 16.0..17.5 and -18.9..-17.4
MJ_PLATE_X = (-10.0, 10.0)    # [STEP] plate footprint in X
MJ_PLATE_Y_BACK = -22.0       # [STEP] plate footprint, -Y edge
MJ_PLATE_CORNER_R = 1.0       # [STEP] R1 vertical round at (-9, -21)
MJ_THROAT_Y = -15.0           # [STEP] the fork is open for y > -15

# counterbores for the four horn screws
MJ_CB_TOP = (21.0, 24.0)      # [STEP] Ø5.4, 3.0 deep, from the outer face
MJ_CB_BOTTOM = (-24.0, -22.4) # [STEP] Ø5.4, 1.6 deep
MJ_CENTRE_HOLE_Z = (-24.0, -20.4)  # [STEP] Ø3.2 centre-screw hole, bottom plate

# lightening pockets through the fork cheeks
MJ_POCKET_D = 8.4             # [STEP] Ø8.4, axis along X
MJ_POCKETS = [                # [STEP] (y, z) of each pocket axis
    (-10.8, 11.8), (-10.8, -13.2),
    (-26.2, 14.9), (-26.2, -14.9),
]

# -- the blade --------------------------------------------------------------
MJ_BLADE_Y = (-22.0, -82.0)   # [STEP] root to fingertip
MJ_TIP_Y = -82.0              # [STEP]

# Gripping face: a staircase, each step 2 mm closer to the fixed jaw.
# (y_at_which_the_step_starts, x_of_the_face)
MJ_FACE_STEPS = [             # [STEP] planes x = -8.3, -10.3, -12.3
    (-22.0, -8.30),
    (-62.0, -10.30),
    (-72.0, -12.30),
]
MJ_FACE_STEP_RISE = 2.0       # [DERIVED] 8.3 -> 10.3 -> 12.3

# Back face: two straight tapers meeting at a kink.
MJ_BACK_X_AT_ROOT = 7.72      # [STEP] section y = -22
MJ_BACK_SLOPE_1 = 0.1056      # [STEP] plane normal (0.994, -0.105, 0) -> 6.03°
MJ_BACK_SLOPE_2 = 0.4889      # [STEP] plane normal (0.898, -0.439, 0) -> 26.06°
MJ_BACK_KINK_Y = -59.3        # [DERIVED] where the two planes intersect

# Blade half-height in Z, station by station.  Every row is a measured
# cross-section, so this list *is* the blade's silhouette — edit a row and the
# loft follows.  (The taper is convex, not straight; a two-point taper misses
# the middle of the blade by ~0.4 mm.)
MJ_BLADE_PROFILE = [          # [STEP] (y, half_height)
    (-22.5, 12.92), (-23.0, 12.18), (-24.0, 11.33), (-25.0, 10.88),
    (-26.0, 10.64), (-28.0, 10.22), (-30.0, 9.87), (-32.0, 9.57),
    (-34.0, 9.31), (-36.0, 9.08), (-40.0, 8.70), (-44.0, 8.38),
    (-50.0, 7.97), (-56.0, 7.58), (-60.0, 7.28), (-62.0, 7.11),
    (-66.0, 6.71), (-70.0, 6.19), (-72.0, 5.85), (-74.0, 5.43),
    (-78.0, 4.19), (-80.0, 3.13), (-81.0, 2.28), (-81.8, 1.40),
    # The reference tip closes at y = -82.0.  Lofting all the way to a 0.8 mm
    # half-height there produces a degenerate solid that OCCT still reports as
    # valid (its volume comes back negative), so the loft stops 0.2 mm short
    # and the tip is finished with a fillet.  See NOTES.md.
]
MJ_BLADE_CORNER_R = 1.5       # [ASSUMED] section corner round; the original
                              # blends these with B-splines, not arcs

# The fork's outer cheeks are not flat slabs — they slope inward toward the
# back, and then flare sharply into the blade.  These two rows are the flare,
# measured; the loft starts here so the blade grows out of the fork instead of
# stepping off it.  (y, x_front, x_back, half_height)
MJ_ROOT_SECTIONS = [          # [STEP]
    (-22.0, -9.00, 7.72, 18.34),
    (-22.2, -8.30, 7.70, 13.62),
]
MJ_CHEEK_TAPER = [            # [STEP] (y, half_height) of the cheeks' outer face
    (-9.5, 24.00), (-15.0, 21.91), (-21.0, 20.07), (-22.0, 18.34),
]

# Small Ø1.5 holes marching down the blade, alternating between "through the
# thickness, normal to the back face" and "through the height, normal to the
# top face".  Purpose is not determinable from the geometry alone — they are
# reproduced because they are there, and because they are a good test of
# whether a tool can put a hole normal to a tapering face.
MJ_VENT_D = 1.5               # [STEP]
MJ_VENT_BACK_OFFSET = 5.03    # [DERIVED] vertical holes sit this far in from
                              # the back face, at every station
MJ_VENT_THROUGH_HEIGHT_Y = [  # [STEP] holes along Z
    -18.89, -28.83, -38.78, -48.72, -58.66,
]
MJ_VENT_THROUGH_THICKNESS_Y = [  # [STEP] holes along the back-face normal
    -23.72, -33.72, -43.72, -53.72, -61.49, -71.52,
]

# ===========================================================================
#  WRIST-ROLL FOLLOWER  —  the gripper body, carrying the fixed jaw
#  (Wrist_Roll_Follower_SO101.step)
# ===========================================================================

# -- the horn boss under the base plate -------------------------------------
WR_HORN_CENTRE_Y = -0.218     # [STEP] the bolt circle is off-centre in Y
WR_BOSS_Z = (0.0, 5.95)       # [STEP] Ø24 boss, 5.95 tall
WR_DISC_RECESS_Z = (0.0, 0.95)      # [STEP] Ø20 pocket the horn disc drops into
WR_SCREW_CLEAR_Z = (0.95, 3.95)     # [STEP] Ø3.2 through the plate
WR_SCREW_CB_Z = (3.95, 9.95)        # [STEP] Ø6 counterbore from above
WR_CENTRE_BORE_Z = (0.95, 9.95)     # [STEP] Ø5.4 centre-screw clearance

# -- the base plate ---------------------------------------------------------
WR_PLATE_Z = (5.95, 11.95)    # [STEP] 6.0 thick
WR_PLATE_X = (-35.2, 12.0)    # [STEP] main body footprint
WR_PLATE_Y = (-24.22, 23.78)  # [STEP]
WR_PLATE_CORNER_R = 6.0       # [ASSUMED] the original blends these corners
WR_PLATE_EDGE_R = 3.0         # [STEP] R3 rounds on the plate's free edges
WR_ARM_X = (12.0, 30.0)       # [STEP] the arm reaching out to +X
WR_ARM_Y = (-14.0, 14.0)      # [STEP] 28 wide, matching the R3 edge length
WR_TAB_X = (2.0, 10.0)        # [STEP] small tab at +Y carrying two Ø3.2 holes
WR_TAB_Y_MAX = 27.78          # [STEP]
WR_TAB_HOLES_X = (4.39, 7.81) # [STEP] Ø3.2, axis Z, y = 24.58
WR_TAB_HOLE_Y = 24.58         # [STEP]

# -- the walls that box in the gripper servo --------------------------------
WR_WALLS_Z = (11.95, 38.0)    # [STEP] side walls run from the plate to the
                              # blade root
WR_WALL_Y = (-24.22, 23.78)   # [STEP] outer faces
WR_WALL_T = 3.5               # [ASSUMED] wall thickness
WR_CAVITY_Y = (-16.22, 15.78)  # [STEP] inner faces, fixed by how deep the M2
                               # servo-screw recesses go into the side walls
WR_CAVITY_X0 = -26.0          # [FITTED] back of the pocket.  Chosen so the
                              # model's cross-section area matches the
                              # reference's at z = 13, 20, 24 and 32 to within
                              # ~3%; it is not a face I could read directly.
WR_SERVO_SCREWS = [           # [STEP] (x, z, y_side) M2 servo mounting screws
    (-12.6, 14.1, +1), (-12.6, 34.6, +1),
    (-8.8, 14.1, -1), (-8.8, 34.6, -1),
]
WR_SIDE_SCREWS_X = (-5.0, 3.1)  # [STEP] Ø3.2 through the -Y wall
WR_SIDE_SCREWS_Z = 24.35        # [STEP]
WR_BORE_D = 10.0              # [STEP] Ø10 bore straight through the body
WR_BORE_Z = 24.35             # [STEP]
WR_BORE_X = (-35.2, -15.0)    # [STEP]

# -- the fixed jaw blade ----------------------------------------------------
WR_BLADE_Z = (38.0, 105.375)  # [STEP] root to fingertip
WR_BLADE_BACK_X_AT_45 = -34.87  # [STEP]
WR_BLADE_BACK_SLOPE = 0.3638    # [STEP] plane normal (0.94, 0, -0.342) -> 20°

# Gripping face: a staircase again, this time five steps up the jaw.
WR_FACE_STEPS = [             # [STEP] (z_at_which_the_step_starts, x_of_face)
    (38.0, -15.00),
    (55.0, -13.30),
    (70.0, -11.60),
    (88.0, -9.90),
    (98.0, -7.90),
]

# Blade half-width in Y, station by station.
WR_BLADE_PROFILE = [          # [STEP] (z, half_width)
    (40.0, 14.73), (42.0, 13.63), (45.0, 12.28), (55.0, 9.82),
    (60.0, 9.17), (65.0, 8.69), (70.0, 8.31), (75.0, 7.96),
    (80.0, 7.62), (85.0, 7.22), (90.0, 6.70), (95.0, 5.97),
    (100.0, 4.74), (103.0, 3.41), (105.0, 1.42), (105.375, 0.80),
]
WR_BLADE_CORNER_R = 1.5       # [ASSUMED] as for the moving jaw

WR_VENT_D = 1.5               # [STEP] the same Ø1.5 pattern as the moving jaw
WR_VENT_Z = [50.74, 60.14, 69.54, 78.93, 88.33]  # [STEP] holes along Y

# ===========================================================================
#  ASSEMBLY
# ===========================================================================
# Where the moving jaw's pivot sits in the follower's frame, and how far it
# swings.  Nothing in either STEP file says how the two parts mate — they are
# two separate solids with no assembly constraints — so this is reasoned, not
# measured, and NOTES.md says why it is probably not the whole story.
#   x: set so the two gripping faces meet when the jaw is closed
#      (moving-jaw face sits 8.3 mm from its pivot; fixed-jaw face is at -15.0)
#   y, z: the Ø10 bore's axis, which is the only feature at the right height
JAW_PIVOT_IN_BODY = (-6.7, 0.13, 24.35)  # [DERIVED + ASSUMED]
JAW_OPEN_DEG = 32.0                      # [ASSUMED] travel, closed to open
JAW_ANGLE_DEG = 0.0                      # closed; set to JAW_OPEN_DEG to open

# ===========================================================================
#  PRINT / FIT allowances — the numbers Hand 1.0 will actually edit
# ===========================================================================
FIT_CLEARANCE = 0.2           # [ASSUMED] added to every bore for an FDM fit
WALL_MIN = 1.6                # [ASSUMED] four perimeters at 0.4 mm
