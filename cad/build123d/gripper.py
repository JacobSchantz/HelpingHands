"""The SO-101 gripper assembly, plus every export and drawing this
directory ships.

    .venv/bin/python gripper.py            # STEP + STL + SVG drawings
    .venv/bin/python gripper.py --angle 32 # the same, with the jaw open
"""

from __future__ import annotations

import argparse
from pathlib import Path

from build123d import (
    Axis, Color, Compound, ExportSVG, LineType, Location, Rotation, Solid,
    export_step, export_stl,
)

import params as P
from fixed_jaw import build_fixed_jaw
from moving_jaw import build_moving_jaw

HERE = Path(__file__).resolve().parent
EXPORT = HERE / "export"
RENDER = HERE / "render"


def place_moving_jaw(jaw: Solid, angle_deg: float) -> Solid:
    """Put the moving jaw into the follower's frame, at a given jaw angle.

    The jaw is modelled about its own Z axis; in the body it swings about Y.
    """
    px, py, pz = P.JAW_PIVOT_IN_BODY
    upright = Rotation(-90, 0, 0) * jaw          # jaw +Z -> body +Y
    swung = Rotation(0, angle_deg, 0) * upright  # open about the body's Y
    return Location((px, py, pz)) * swung


def build_assembly(angle_deg: float = P.JAW_ANGLE_DEG) -> Compound:
    body = build_fixed_jaw()
    body.color = Color(0.62, 0.66, 0.72)
    jaw = place_moving_jaw(build_moving_jaw(), angle_deg)
    jaw.label = "moving_jaw"
    jaw.color = Color(0.82, 0.55, 0.35)
    return Compound(label="so101_gripper", children=[body, jaw])


# ---------------------------------------------------------------------------
#  drawings
# ---------------------------------------------------------------------------
VIEWS = {
    "front": ((0, -600, 0), (0, 0, 1)),
    "side": ((600, 0, 0), (0, 0, 1)),
    "iso": ((500, -500, 450), (0, 0, 1)),
}


def draw(shape, name: str, view: str) -> Path | None:
    origin, up = VIEWS[view]
    try:
        visible, hidden = shape.project_to_viewport(origin, viewport_up=up)
    except Exception as exc:  # noqa: BLE001 - OCCT's HLR is fragile
        print(f"  ! hidden-line projection failed for {name}/{view}: {exc}")
        return None
    svg = ExportSVG(scale=6, margin=3)
    svg.add_layer("visible", line_weight=0.35)
    svg.add_layer("hidden", line_weight=0.13, line_type=LineType.DASHED)
    svg.add_shape(visible, layer="visible")
    if view != "iso":
        svg.add_shape(hidden, layer="hidden")
    path = RENDER / f"{name}_{view}.svg"
    svg.write(str(path))
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--angle", type=float, default=P.JAW_ANGLE_DEG,
                    help="jaw angle in degrees; 0 is closed")
    ap.add_argument("--no-drawings", action="store_true")
    args = ap.parse_args()

    EXPORT.mkdir(exist_ok=True)
    RENDER.mkdir(exist_ok=True)

    body = build_fixed_jaw()
    jaw = build_moving_jaw()
    for part, name in ((body, "fixed_jaw"), (jaw, "moving_jaw")):
        export_step(part, str(EXPORT / f"{name}.step"))
        export_stl(part, str(EXPORT / f"{name}.stl"),
                   tolerance=0.03, angular_tolerance=0.25)
        bb = part.bounding_box()
        print(f"{name:12s} volume {part.volume:9.1f} mm³   "
              f"bbox {bb.size.X:6.2f} × {bb.size.Y:6.2f} × {bb.size.Z:6.2f}")

    closed = build_assembly(0.0)
    opened = build_assembly(P.JAW_OPEN_DEG)
    export_step(closed, str(EXPORT / "so101_gripper_closed.step"))
    export_stl(closed, str(EXPORT / "so101_gripper_closed.stl"),
               tolerance=0.03, angular_tolerance=0.25)

    if not args.no_drawings:
        for shape, name in ((jaw, "moving_jaw"), (body, "fixed_jaw")):
            for view in ("front", "side"):
                draw(shape, name, view)
        draw(closed, "gripper_closed", "iso")
        draw(opened, "gripper_open", "iso")
        draw(closed, "gripper_closed", "side")
        print(f"drawings in {RENDER}")


if __name__ == "__main__":
    main()
