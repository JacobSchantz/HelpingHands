// =============================================================================
//  gripper.scad — the SO-101 gripper assembly: fixed jaw + moving jaw.
// =============================================================================
//  This is the file to open.  Set `jaw_opening` (mm at the fingertip) in
//  params.scad, or override it here, and the moving jaw swings on the measured
//  pivot.  `part` picks what gets rendered, so one file drives every export:
//
//      openscad -D 'part="assembly"'   -o gripper_assembly.stl gripper.scad
//      openscad -D 'part="fixed_jaw"'  -o fixed_jaw.stl        gripper.scad
//      openscad -D 'part="moving_jaw"' -o moving_jaw.stl       gripper.scad
//
//  Why this part: it is the end effector plans/hand_1_0.md is about to replace.
//  Hand 1.0 keeps the wrist_roll horn interface and the servo cradle and throws
//  away the jaws — so the interesting edits are mj_blade_profile /
//  mj_face_steps / fj_face_steps, and every one of those is a list in
//  params.scad rather than a shape buried in this file.  See plans/gripper_bet.md
//  for why the gripper matters at all, and NOTES.md for the bake-off verdict.
// =============================================================================

include <params.scad>
use <fixed_jaw.scad>
use <moving_jaw.scad>

part = "assembly";      // "assembly" | "fixed_jaw" | "moving_jaw" | "open"

// Moving-jaw frame -> follower frame, with the jaw swung open by jaw_angle.
//   jaw +Z (pivot axis)   -> follower +Y
//   jaw -Y (down the blade) -> follower +Z
module jaw_place(angle = jaw_angle) {
    translate([jaw_pivot_x, 0, jaw_pivot_z])
        rotate([0, angle, 0])
            rotate([-90, 0, 0])
                children();
}

module gripper_assembly(angle = jaw_angle) {
    color("#7f8c9b") fixed_jaw();
    color("#c96a3f") jaw_place(angle) moving_jaw();
}

if      (part == "assembly")   gripper_assembly();
else if (part == "open")       gripper_assembly(jaw_angle_for(jaw_opening_max));
else if (part == "fixed_jaw")  fixed_jaw();
else if (part == "moving_jaw") moving_jaw();
