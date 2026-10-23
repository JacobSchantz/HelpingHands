# Unpublished four-post cap candidate — rejected by CAD tests

This preserves the edits already underway when Jake redirected voice-550038ca to validation first. It builds on **Base 20 / Gripper 25**. “Base 21” in the copied export labels was provisional and is superseded by the actual two-pivot Base 21 in versions/v322_generalist_two_pivot_support. This rejected study is not a version. Gripper 25 is unchanged byte for byte in the part meshes. No registry, picker, publisher or pose-map change was made.

The draft removes the cap's inherited pinion disc/access opening, hulls only its four supports, reduces fastening pillars from 8 to 6 mm, moves them to Z=-34 mm, and removes duplicated post segments. These are preserved edits, not an accepted design. Two pivots and two fastening pillars remain; the test contract does not require exactly four pegs.

**Reject this candidate:** live 121-pose testing detects pinion/base interference (up to 186.78 mm³), base/plate-screw interference, and blocked plate/center driver paths. No further geometry changes were made after that evidence. The smaller outline alone is insufficient. Do not print or substitute this for the published Base 20.

Evidence and runnable acceptance tests: `../../../cad/validation/voice-550038ca/README.md`. It includes the actual top/side comparison and explains what remains unverified. No physical strength, ergonomics, motor actuation, human-fit or assembly claim is made. Bought HLS3606M-C001 hardware, reference license and original source provenance are retained in `reference/`.

To reproduce the preserved mesh exports: `python3 export_models.py`. To run the original detailed checker: `../../../cad/blender/.venv/bin/python check_geometry.py` (expected failure). `genus.py` passes for all seven printed parts; watertight geometry does not excuse motion/assembly interference.
