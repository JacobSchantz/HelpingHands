"""Criterion (2) of the bake-off, as a test instead of an opinion:
how much does it hurt to change a dimension six months from now?

Each case below is an edit the Hand 1.0 design actually calls for (see §2 of
``plans/hand_1_0.md`` — wider pads, a thinner leading edge, a different jaw
opening).  The script changes one parameter, rebuilds, and reports whether the
solid still comes out valid and how long it took.

    .venv/bin/python edit_stress.py
"""

from __future__ import annotations

import importlib
import time

import params as P
import moving_jaw


def rebuild(label: str) -> None:
    importlib.reload(moving_jaw)
    started = time.time()
    try:
        jaw = moving_jaw.build_moving_jaw()
    except Exception as exc:  # noqa: BLE001 - the point is to catch anything
        print(f"{label:48s} FAIL  {type(exc).__name__}: {exc}")
        return
    ok = jaw.is_valid and jaw.volume > 0
    print(f"{label:48s} {'ok  ' if ok else 'BAD '} "
          f"volume {jaw.volume:9.1f} mm³   {time.time() - started:4.1f} s")


def main() -> None:
    rebuild("baseline")

    P.MJ_BLADE_CORNER_R = 3.0
    rebuild("blade corner radius 1.5 -> 3.0 mm")
    P.MJ_BLADE_CORNER_R = 1.5

    P.MJ_BLADE_PROFILE = [(y, h * 1.15) for y, h in P.MJ_BLADE_PROFILE]
    rebuild("gripping pad 15% wider")
    P.MJ_BLADE_PROFILE = [(y, h / 1.15) for y, h in P.MJ_BLADE_PROFILE]

    P.MJ_FACE_STEPS = [(y, x - 2.0) for y, x in P.MJ_FACE_STEPS]
    rebuild("gripping face 2 mm closer to the fixed jaw")
    P.MJ_FACE_STEPS = [(y, x + 2.0) for y, x in P.MJ_FACE_STEPS]

    stretch = 1.12
    P.MJ_BLADE_PROFILE = [(y * stretch, h) for y, h in P.MJ_BLADE_PROFILE]
    P.MJ_FACE_STEPS = [(y * stretch if y < -22 else y, x)
                       for y, x in P.MJ_FACE_STEPS]
    P.MJ_BACK_KINK_Y *= stretch
    P.MJ_VENT_THROUGH_HEIGHT_Y = [y * stretch for y in P.MJ_VENT_THROUGH_HEIGHT_Y]
    P.MJ_VENT_THROUGH_THICKNESS_Y = [y * stretch
                                     for y in P.MJ_VENT_THROUGH_THICKNESS_Y]
    rebuild("blade 12% longer (82 -> 92 mm)")


if __name__ == "__main__":
    main()
