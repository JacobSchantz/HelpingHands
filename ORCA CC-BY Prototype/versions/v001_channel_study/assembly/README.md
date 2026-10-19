# ORCA index assembly and central-channel study

**ORCA Hand hardware — Copyright (c) 2026 ORCA Dexterity, Inc.**
Original geometry and this geometry study: **CC BY 4.0**.
[Source repository](https://github.com/orcahand/orcahand_hardware) ·
[License](../upstream/LICENSE) ·
[Source manifest](../manifest.json).

The manufacturing files are pinned to
`37b71dc03d3f11e48b920cbf54562b33c025bc8c`. Original STL/STEP files remain
unchanged in `../upstream/`. Changes here are assembled placement, an enlarged
copy, and a configurable longitudinal subtraction. This is an independent
prototype, with no implied ORCA endorsement.

## Open in OpenSCAD

- [original_index.scad](original_index.scad): the three original right-index
  printed parts in a neutral assembled pose. Optional joint-angle, axis and
  exploded-view controls are for geometric inspection.
- [wearable_channel_concept.scad](wearable_channel_concept.scad): defaults to
  **2× enlargement with a 24 mm wide × 22 mm deep elliptical through-channel**.
  These channel dimensions are provisional; Jake's finger width and thickness
  have not been supplied. `enlargement` controls X/Y, `longitudinal_scale`
  controls Z independently, and both default to 2. `part` selects one component;
  `view` selects the carve, original, comparison or removed material.
- [index_2x_carved_concept.stl](export/index_2x_carved_concept.stl): the first
  default subtraction exported by OpenSCAD. **Inspection artifact only; it
  contains disconnected fragments and is not a functional printable glove.**

Width is the lateral Y dimension. Depth is X, across the palmar/dorsal profile.
The neutral finger points in +Z. Channel dimensions are final millimeters,
independent of the scale controls. The source shapes and their built-in holes
scale with the parts. No skin, palm, pins, bearings or tendons are added here.

## Placement evidence

Analytic cylindrical faces in the current STEP parts establish these axes:

| Part | CAD feature | Axis origin (mm) | Axis direction |
| --- | --- | --- | --- |
| I-AP-R | MCP bearing seats, radius 4.1 | (0, 0, 0) | Y |
| I-PP | MCP shaft hole, radius 2 | (0, 0, 0) | Y |
| I-PP | PIP bearing seats, radius 4.125 | (1.5, 0, 37) | Y |
| I-IP | PIP shaft hole, radius 2 | (0, 0, 0) | Y |

The assembly uses AP rotated +90° about Y, PP untransformed, and IP translated
by (1.5, 0, 37). This makes the mating axes coincide. The AP's carpal-axis
center (18.75, 0, 1) becomes (1, 0, −18.75), pointing toward the palm.

The relative AP/PP rotation and PIP displacement agree with the official
[v2 right-hand URDF](https://github.com/orcahand/orcahand_description/blob/b9b349a21ee0238c62b6cf92ae7597027867adf8/v2/models/urdf/orcahand_right.urdf).
That visualization's AP mesh offset and MCP joint translation differ by
0.400968 mm. The manufacturing assembly here uses the current STEP's
coincident bearing axes, rather than transferring that visualization offset.
The retained URDF is reference evidence; its separate
[MIT notice](source/DESCRIPTION_LICENSE_MIT.txt) does not relicense the
manufacturing CAD. Full-hand simulation geometry is handled separately in
`../full_hand/`.

The [official v2 assembly video](https://www.youtube.com/watch?v=TgIz7HiyaoU)
and pinned [assembly addendum](../upstream/orca_v2/base/ASSEMBLY_ADDENDUM.md)
describe the physical assembly. The addendum specifies PTFE in the wide AP
hole pair, trimmed about 1 mm proud on both sides. The retained
[AP routing image](source/ap-ptfe-1.png) is from that same hardware commit.
The video itself was not successfully retrieved for visual review here.

At the neutral pose, Boolean intersection of every pair of the three original
printed parts is **0 mm³**. This establishes a non-overlapping CAD placement,
not validated assembly fit, full-range motion, tendon routing or force output.

## What the first carve actually does

The straight channel was subtracted from each component in the assembled,
uniformly doubled pose. No loose fragments were removed or hidden.

| Part | Material removed | Disconnected solids remaining |
| --- | ---: | ---: |
| AP | 23.5% | 4 |
| PP | 43.3% | 4 |
| IP | 72.0% | 6 |

The cut crosses central webs, tendon-guide features and the region traversed
by the joint shafts. The resulting parts do not retain their original
mechanical function. A shaft spanning the finger cavity would also obstruct a
wearer's finger; a usable exoskeleton would need a different joint/retention
arrangement. That redesign has not been performed.

Uniform 2× scaling moves the PIP from **37 mm to 74 mm** along Z from the MCP,
and doubles the original approximately 82 mm MCP-to-tip extent. It therefore
does not establish alignment with a human finger. Independent longitudinal
scaling is provided for later exploration; nonuniform scaling also changes
joint and hardware-hole shapes and is not a fit solution by itself.

[cut_audit.json](cut_audit.json) contains the exact material volumes and
component counts. [original_index.png](render/original_index.png) and
[index_2x_carved_concept.png](render/index_2x_carved_concept.png) were rendered
in OpenSCAD and visually inspected. The cut study has not been sliced,
printed, worn or mechanically tested.

Run `uv run audit.py` from this folder to reproduce the source-integrity,
neutral-intersection and default-cut checks. The script inspects the mesh
geometry and does not alter upstream files.
