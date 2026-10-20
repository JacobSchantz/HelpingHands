export default {
  "_about": "Open/close slider for the gallery. Angles are each jaw's swing in degrees, the same 'angle' the design's .scad uses (0 = closed for gens 3-17). 'exported' is the angle the STLs were exported at. A hinge turns every model whose name matches 'match' about the Y axis through 'pivot' by sign*(angle - exported); a slide moves by dir*(sin(angle) - sin(exported)) (Base 5's fingers slide: no hinges, a slide per side, dir = gripper.scad pose_dir); a crank turns about 'pivot' by -(asin((2+20 sin(angle) - mid)/radius)) relative to the exported pose. Scripts/check_gripper_closure.py reads this file too, and skips 'single_finger' designs (one moving finger against a fixed thumb, so its hinges are not left/right pairs). Scripts/test_gripper_poses.py checks that every gripper in the catalog has an entry whose hinges match parts, and that each version's gripper.scad 'pivot' and 'angle' still equal the right hinge's pivot X and 'exported'.",
  "two-finger-gripper-v008-pollen-grabette": {"exported": 90, "min": 0, "max": 90, "single_finger": true, "hinges": [
    {"match": "^Grabette finger", "pivot": [0, 0, 0], "sign": 1},
    {"match": "^Gripette finger", "pivot": [320, 0, 0], "sign": 1}]},
  "two-finger-gripper-v314-generalist-sts-arm-mount": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [31.35, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-31.35, 0, 0], "sign": -1}]},
  "two-finger-gripper-v313-generalist-aero-full-hand": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v312-generalist-compact-drive": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [31.35, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-31.35, 0, 0], "sign": -1}]},
  "two-finger-gripper-v311-generalist-motor-choice": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v310-generalist-arm-mount": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v309-generalist-top-plate": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v308-generalist-handle-gear": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v307-generalist-printable": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v305-generalist-single-gear": {"exported": 15, "min": 0, "max": 30, "hinges": [],
    "slides": [{"match": "^Right", "dir": [40, 0, 0]}, {"match": "^Left", "dir": [-40, 0, 0]}]},
  "two-finger-gripper-v304-generalist-one-piece-drive": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v303-generalist-inplane": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v302-generalist-simple": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v301-generalist-base": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v207-generalist-flush-handle": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v206-generalist-single-step": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v205-generalist-spanning-handle": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v204-generalist-parametric": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.1856, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.1856, 0, 0], "sign": -1}]},
  "two-finger-gripper-v203-generalist-tongue-pocket": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.1856, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.1856, 0, 0], "sign": -1}]},
  "two-finger-gripper-v202-generalist-flush-loops": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.1856, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.1856, 0, 0], "sign": -1}]},
  "two-finger-gripper-v201-generalist-strap-loops": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.1856, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.1856, 0, 0], "sign": -1}]},
  "two-finger-gripper-v020-generalist-double-hook": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v019-generalist-wide-beak": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.2512, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.2512, 0, 0], "sign": -1}]},
  "two-finger-gripper-v018-generalist-flat-taper": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.1856, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.1856, 0, 0], "sign": -1}]},
  "two-finger-gripper-v017-generalist-strap-slide": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.1856, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.1856, 0, 0], "sign": -1}]},
  "two-finger-gripper-v016-generalist-rounded-point": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.1856, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.1856, 0, 0], "sign": -1}]},
  "two-finger-gripper-v015-generalist-long-jaw": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.251, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.251, 0, 0], "sign": -1}]},
  "two-finger-gripper-v014-generalist-tip-contact": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.137, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.137, 0, 0], "sign": -1}]},
  "two-finger-gripper-v013-generalist-closed-beak": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.1655, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.1655, 0, 0], "sign": -1}]},
  "two-finger-gripper-v012-generalist-tweezer": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.1, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.1, 0, 0], "sign": -1}]},
  "two-finger-gripper-v011b-generalist-fingers-astra": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.672, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.672, 0, 0], "sign": -1}]},
  "two-finger-gripper-v011-generalist-fingers-opus": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.672, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.672, 0, 0], "sign": -1}]},
  "two-finger-gripper-v010-generalist-fingers-opus": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [27.836, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-27.836, 0, 0], "sign": -1}]},
  "two-finger-gripper-v009-generalist-fingers-sonnet": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [22.377, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-22.377, 0, 0], "sign": -1}]},
  "two-finger-gripper-v007-generalist-fingers": {"exported": 15, "min": 0, "max": 30, "hinges": [
    {"match": "^Right", "pivot": [30.757, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-30.757, 0, 0], "sign": -1}]},
  "two-finger-gripper-v006-dorsal-drive": {"exported": 15, "min": 0, "max": 22, "hinges": [
    {"match": "^Right", "pivot": [14.4, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-14.4, 0, 0], "sign": -1}]},
  "two-finger-gripper-v005-mirrored-gears": {"exported": 15, "min": 0, "max": 22, "hinges": [
    {"match": "^(Right jaw|Plastic horn adapter)", "pivot": [14.4, 0, 0], "sign": 1},
    {"match": "^Left jaw", "pivot": [-14.4, 0, 0], "sign": -1}]},
  "two-finger-gripper-v004-symmetric-pincher": {"exported": 15, "min": 0, "max": 22, "hinges": [
    {"match": "^Right", "pivot": [16, 0, 0], "sign": 1},
    {"match": "^Left", "pivot": [-16, 0, 0], "sign": -1}],
    "slides": [{"match": "yoke", "dir": [0, 0, 20]}],
    "cranks": [{"match": "servo crank", "pivot": [0, -20, -30], "radius": 6, "mid": 5.746}]},
  "two-finger-gripper-v003-single-pincher": {"exported": 18, "min": 0, "max": 22, "hinges": [
    {"match": "^(Index|Undrilled)", "pivot": [12, 0, 0], "sign": 1},
    {"match": "^(Thumb|Floating|Compression|Front pad|Rear pad)", "pivot": [-12, 0, 0], "sign": -1}]},
  "demo-gripper-gen-01": {"exported": 0, "min": 0, "max": 30, "hinges": [
    {"match": "^Right (fin-ray|root)", "pivot": [12, 0, 0], "sign": 1},
    {"match": "^Left (fin-ray|root)", "pivot": [-12, 0, 0], "sign": -1}]},
  "demo-gripper-gen-00": {"exported": 0, "min": 0, "max": 30, "hinges": [
    {"match": "^A · right", "pivot": [12, 0, 0], "sign": 1},
    {"match": "^A · left", "pivot": [-12, 0, 0], "sign": -1},
    {"match": "^B · right", "pivot": [152, 0, 0], "sign": 1},
    {"match": "^B · left", "pivot": [128, 0, 0], "sign": -1}]}
}
