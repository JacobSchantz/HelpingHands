# voice-550038ca — smaller whole gear train

Base25 from24 / Gripper29 from28. See the version README and machine-readable geometry, closure, hardware and gear reports for dimensions, process/load assumptions and limitations.

- `red-test.txt`: old Base24 fails the new gear-size and housing-envelope requirements before implementation.
- `green-tests.txt`: new design, exact unchanged finger-band volume, current report hashes, lineage and publishing checks.
- `comparison.png`: same-scale actual STL top/side views with finger band highlighted.
- `gears.png`: actual gear-only projections, old/new, at15°.
- `closure.png`: original tips closed and full30° opening.
- `whole-hand.json` / `hand-frames.json`: full generic hand, actual selected new design; still fails contact/skin acceptance.25.33/25.34 mm worst contact misses,4/3 collision poses out of13.
- `browser-smoke.json`:13 poses, no browser exceptions, Copy report identifies Base25 design. Screenshots are real browser scenes at0/30°.

Re-render with `cad/blender/.venv/bin/python cad/validation/voice-550038ca-small-drive/render_evidence.py`. Browser smoke requires published gallery served at127.0.0.1:8768; run `node --experimental-websocket cad/validation/voice-550038ca-small-drive/browser_smoke.mjs` on Node20. This creates its own temporary Chrome profile on port9336.

Hand screening: `HAND_CASE_FOLDER='Two Finger Gripper/versions/v326_generalist_small_drive' HAND_CASE_MODULE=small_drive_case.js HAND_CASE_OUT=cad/validation/voice-550038ca-small-drive PYTHONPATH=. cad/blender/.venv/bin/python Scripts/check_contact_hand.py` (expected nonzero: fit is not accepted).

No physical motor actuation, qualified load rating, fatigue/strength test, measured production plate/thread fit, real driver engagement or Jake-hand fit. No SO-101/Mount2 interface claimed.
