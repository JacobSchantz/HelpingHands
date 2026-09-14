# SO-101 gripper — build123d

Parametric model of the SO-101 moving jaw and wrist-roll follower (the body
carrying the fixed jaw), built from the two reference STEP files in
`reference/`.

**Read `NOTES.md` first** — it is the point of this directory. It carries the
bake-off verdict, the measured comparison against the reference, and a plain
list of where the geometry is approximate.

```sh
./build.sh            # measurements, both parts, exports, drawings, fidelity
```

Or one piece at a time, using the venv that is already here:

```sh
.venv/bin/python measure_reference.py --write   # -> MEASUREMENTS.md
.venv/bin/python gripper.py                     # -> export/, render/
.venv/bin/python gripper.py --angle 32          # jaw open
.venv/bin/python fidelity_check.py --write      # -> FIDELITY.md
.venv/bin/python edit_stress.py                 # change a dimension, rebuild
```

Every dimension lives in `params.py`, tagged with where it came from. Change a
number there and rerun; nothing else holds geometry.

| generated | |
|---|---|
| `MEASUREMENTS.md` | what the reference B-rep actually says |
| `FIDELITY.md` | how close this model gets |
| `export/` | STEP and STL for both parts and the closed assembly |
| `render/` | orthographic and isometric drawings |
