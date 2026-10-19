# HelpingHands agent conventions

## Gripper design versions

- **1.x — gripper only.** The old "Gen N" numbering maps to 1.N (e.g. Gen 16 = 1.16, `Two Finger Gripper/versions/v016_generalist_rounded_point`).
- **2.x — gripper plus handles** (strap-loop attachment). 2.1 builds on 1.17.
- Each time Jake asks for a change to the gripper design, make a new version (bump the minor number within its line) instead of editing the current one in place.
- Existing `versions/vNNN_*` folders still use the old Gen numbering; workers may rename them to the new scheme as part of their pebble.
