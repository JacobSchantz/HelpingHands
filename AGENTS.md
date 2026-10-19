# HelpingHands agent conventions

## Gripper design versions

- **1.x — gripper only.** The old "Gen N" numbering maps to 1.N (e.g. Gen 16 = 1.16, `Two Finger Gripper/versions/v016_generalist_rounded_point`).
- **2.x — gripper plus handles** (strap-loop attachment). 2.1 builds on 1.17.
- **3.x — gripper plus handles plus base** (the base/drive assembly: common base the handles plug into, single motor underneath, gear linkage to the handles). Any 2.x handle must fit the base through the shared handle–base interface.
- Each time Jake asks for a change to the gripper design, make a new version (bump the minor number within its line) instead of editing the current one in place.
- Existing `versions/vNNN_*` folders still use the old Gen numbering; workers may rename them to the new scheme as part of their pebble.
- **From 2.4 on, a version is its `params.json`.** `v204_generalist_parametric` names every dimension there (finger outline,
  solid, handles, tongue/pocket). To make the next version, copy the latest parametric folder, change values in `params.json`
  only, run `python3 export_models.py && python3 genus.py && python3 check_geometry.py`, and add it to
  `Scripts/publish_designs.py` (generations) and `cad/mobile_gallery/poses.js` (pivot: `ECHO: pivot` from
  `part="viewer_right"`). Add a new parameter to `params.json` (with its doc and slider range) rather than a literal in
  `gripper.scad`. Jake tunes these live in the preview's Tune panel and pastes the copied JSON into a pebble.
