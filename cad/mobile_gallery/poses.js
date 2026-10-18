export default {
  "_about": "Open/close slider for the gallery. Angles are each jaw's swing in degrees, the same 'angle' the design's .scad uses (0 = closed for gens 3-6). 'exported' is the angle the STLs were exported at. A hinge turns every model whose name matches 'match' about the Y axis through 'pivot' by sign*(angle - exported); a slide moves by dir*(sin(angle) - sin(exported)); a crank turns about 'pivot' by -(asin((2+20 sin(angle) - mid)/radius)) relative to the exported pose. Scripts/check_gripper_closure.py reads this file too.",
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
