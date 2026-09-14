"""The SO-101 wrist-roll follower — the gripper body carrying the fixed jaw.

Same rules as ``moving_jaw.py``: every dimension comes from ``params.py``.

    .venv/bin/python fixed_jaw.py
"""

from __future__ import annotations

from build123d import (
    Circle, Plane, Pos, RectangleRounded, Solid, export_step, export_stl,
    extrude, fillet, loft,
)

import params as P
from moving_jaw import _fillet_where_possible


# ---------------------------------------------------------------------------
#  silhouettes
# ---------------------------------------------------------------------------
def wall_front_x(z: float) -> float:
    """X of the body's front face — it leans back as it rises."""
    (z0, x0), (z1, x1) = (P.WR_WALLS_Z[0], 14.93), (P.WR_WALLS_Z[1], 1.67)
    t = (z - z0) / (z1 - z0)
    return x0 + t * (x1 - x0)


def blade_back_x(z: float) -> float:
    """X of the fixed jaw's back face — vertical at the root, then 20° back."""
    return max(P.WR_PLATE_X[0],
               P.WR_BLADE_BACK_X_AT_45 + P.WR_BLADE_BACK_SLOPE * (z - 45.0))


def blade_front_x(z: float) -> float:
    """X of the gripping face — a five-step staircase up the jaw."""
    x = P.WR_FACE_STEPS[0][1]
    for z_start, face_x in P.WR_FACE_STEPS:
        if z >= z_start:
            x = face_x
    return x


def blade_half_width(z: float) -> float:
    stations = P.WR_BLADE_PROFILE
    if z <= stations[0][0]:
        return stations[0][1]
    if z >= stations[-1][0]:
        return stations[-1][1]
    for (z0, w0), (z1, w1) in zip(stations, stations[1:]):
        if z0 <= z <= z1:
            return w0 + (z - z0) / (z1 - z0) * (w1 - w0)
    raise AssertionError("unreachable")


def _section(z: float, x0: float, x1: float, half_y: float, y_centre: float,
             corner_r: float):
    width, height = x1 - x0, 2 * half_y
    radius = min(corner_r, 0.49 * min(width, height))
    return (
        Plane.XY.offset(z)
        * Pos((x0 + x1) / 2, y_centre)
        * RectangleRounded(width, height, radius)
    )


# ---------------------------------------------------------------------------
#  the parts of the body
# ---------------------------------------------------------------------------
def horn_boss() -> Solid:
    z0, z1 = P.WR_BOSS_Z
    return extrude(
        Plane.XY.offset(z0) * Pos(0, P.WR_HORN_CENTRE_Y) * Circle(P.HORN_BOSS_D / 2),
        amount=z1 - z0,
    )


def base_plate() -> Solid:
    z0, z1 = P.WR_PLATE_Z
    x0, x1 = P.WR_PLATE_X
    y0, y1 = P.WR_PLATE_Y
    plan = Pos((x0 + x1) / 2, (y0 + y1) / 2) * RectangleRounded(
        x1 - x0, y1 - y0, P.WR_PLATE_CORNER_R
    )

    ax0, ax1 = P.WR_ARM_X
    ay0, ay1 = P.WR_ARM_Y
    arm_w, arm_h = ax1 - ax0 + 6, ay1 - ay0
    plan += Pos((ax0 - 6 + ax1) / 2, (ay0 + ay1) / 2) * RectangleRounded(
        arm_w, arm_h, min(arm_w, arm_h) / 2 - 0.01
    )

    tx0, tx1 = P.WR_TAB_X
    plan += Pos((tx0 + tx1) / 2, (y1 - 2 + P.WR_TAB_Y_MAX) / 2) * RectangleRounded(
        tx1 - tx0, P.WR_TAB_Y_MAX - y1 + 2, 1.5
    )
    return extrude(Plane.XY.offset(z0) * plan, amount=z1 - z0)


def walls() -> Solid:
    """The box that holds the gripper servo, from the plate up to the blade."""
    z0, z1 = P.WR_WALLS_Z
    y0, y1 = P.WR_WALL_Y
    sections = [
        _section(z, P.WR_PLATE_X[0], wall_front_x(z), (y1 - y0) / 2,
                 (y0 + y1) / 2, P.WR_PLATE_CORNER_R)
        for z in (z0, (z0 + z1) / 2, z1)
    ]
    return loft(sections)


def servo_cavity() -> Solid:
    """The pocket the gripper servo drops into, open toward +X.

    Its side faces are measured — the M2 servo-screw recesses bottom out on
    them.  Its back face is fitted to the reference's cross-section areas
    rather than read off a plane, because the real pocket is not a plain box.
    See NOTES.md.
    """
    z0, z1 = P.WR_WALLS_Z
    y0, y1 = P.WR_CAVITY_Y
    x0 = P.WR_CAVITY_X0
    sections = [
        _section(z, x0, wall_front_x(z) + 10.0, (y1 - y0) / 2, (y0 + y1) / 2, 2.0)
        for z in (z0, z1)
    ]
    return loft(sections)


def blade() -> Solid:
    """Loft the fixed jaw, one segment per step of the gripping face."""
    root_z = P.WR_BLADE_Z[0]
    flare = loft([
        _section(root_z, P.WR_PLATE_X[0], wall_front_x(root_z), 19.36,
                 P.WR_HORN_CENTRE_Y, P.WR_PLATE_CORNER_R),
        _section(root_z + 2, blade_back_x(root_z + 2), blade_front_x(root_z + 2),
                 blade_half_width(root_z + 2), 0.0, P.WR_BLADE_CORNER_R),
    ])

    steps = P.WR_FACE_STEPS
    ends = [z for z, _ in steps[1:]] + [P.WR_BLADE_PROFILE[-1][0]]
    result = flare
    for (z_start, face_x), z_end in zip(steps, ends):
        z_start = max(z_start, root_z + 2)
        if z_start >= z_end:
            continue
        zs = sorted(
            {z_start, z_end}
            | {z for z, _ in P.WR_BLADE_PROFILE if z_start < z < z_end}
        )
        result += loft([
            _section(z, blade_back_x(z), face_x, blade_half_width(z), 0.0,
                     P.WR_BLADE_CORNER_R)
            for z in zs
        ])
    return result


# ---------------------------------------------------------------------------
#  holes
# ---------------------------------------------------------------------------
def horn_holes() -> list[Solid]:
    cy = P.WR_HORN_CENTRE_Y
    s = P.HORN_BOLT_SQUARE / 2
    cuts = [
        extrude(Plane.XY.offset(P.WR_DISC_RECESS_Z[0]) * Pos(0, cy)
                * Circle(P.HORN_DISC_D / 2),
                amount=P.WR_DISC_RECESS_Z[1] - P.WR_DISC_RECESS_Z[0]),
        extrude(Plane.XY.offset(P.WR_CENTRE_BORE_Z[0]) * Pos(0, cy)
                * Circle(P.HORN_CENTRE_BORE_D / 2),
                amount=P.WR_CENTRE_BORE_Z[1] - P.WR_CENTRE_BORE_Z[0]),
    ]
    for sx in (-1, 1):
        for sy in (-1, 1):
            at = Pos(sx * s, cy + sy * s)
            cuts.append(extrude(
                Plane.XY.offset(P.WR_SCREW_CLEAR_Z[0]) * at * Circle(P.M3_CLEAR_D / 2),
                amount=P.WR_SCREW_CLEAR_Z[1] - P.WR_SCREW_CLEAR_Z[0]))
            cuts.append(extrude(
                Plane.XY.offset(P.WR_SCREW_CB_Z[0]) * at * Circle(P.M3_CAP_D / 2),
                amount=P.WR_SCREW_CB_Z[1] - P.WR_SCREW_CB_Z[0]))
    return cuts


def servo_screw_holes() -> list[Solid]:
    """M2 screws into the servo's own mounting holes, through the side walls."""
    y0, y1 = P.WR_WALL_Y
    cuts = []
    for x, z, side in P.WR_SERVO_SCREWS:
        y_outer = y1 if side > 0 else y0
        plane = Plane(origin=(x, y_outer, z), x_dir=(1, 0, 0),
                      z_dir=(0, side, 0))
        cuts.append(extrude(plane * Circle(P.M2_HEAD_D / 2), amount=-5.8))
        cuts.append(extrude(plane * Circle(P.M2_CLEAR_D / 2), amount=-12.0))
    return cuts


def side_and_body_holes() -> list[Solid]:
    cuts = []
    y0, _ = P.WR_WALL_Y
    for x in P.WR_SIDE_SCREWS_X:
        plane = Plane(origin=(x, y0, P.WR_SIDE_SCREWS_Z), x_dir=(1, 0, 0),
                      z_dir=(0, -1, 0))
        cuts.append(extrude(plane * Circle(P.M3_CLEAR_D / 2), amount=-4.0))

    bx0, bx1 = P.WR_BORE_X
    plane = Plane(origin=(bx0 - 1, P.WR_HORN_CENTRE_Y, P.WR_BORE_Z),
                  x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    cuts.append(extrude(plane * Circle(P.WR_BORE_D / 2), amount=bx1 - bx0 + 1))

    for x in P.WR_TAB_HOLES_X:
        cuts.append(extrude(
            Plane.XY.offset(P.WR_PLATE_Z[0]) * Pos(x, P.WR_TAB_HOLE_Y)
            * Circle(P.M3_CLEAR_D / 2),
            amount=P.WR_PLATE_Z[1] - P.WR_PLATE_Z[0]))
    return cuts


def blade_vent_holes() -> list[Solid]:
    cuts = []
    for z in P.WR_VENT_Z:
        x = blade_back_x(z) + 5.32
        w = blade_half_width(z) + 2
        plane = Plane(origin=(x, -w, z), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
        cuts.append(extrude(plane * Circle(P.WR_VENT_D / 2), amount=2 * w))
    return cuts


# ---------------------------------------------------------------------------
def build_fixed_jaw(*, fillets: bool = True) -> Solid:
    part = horn_boss() + base_plate() + walls()
    part -= servo_cavity()
    part += blade()

    for cut in (horn_holes() + servo_screw_holes() + side_and_body_holes()
                + blade_vent_holes()):
        part -= cut

    if fillets:
        # Filleting after the holes, not before: one of the Ø1.5 holes lands
        # a third of a millimetre from a step, and a fillet that swallows a
        # hole leaves an invalid shell.
        part = _fillet_where_possible(
            part,
            [e for e in part.edges()
             if abs(e.center().Z - P.WR_PLATE_Z[1]) < 0.2 and e.length > 4],
            (2.0, 1.2, 0.6),
        )
        for z_step, _ in P.WR_FACE_STEPS[1:]:
            part = _fillet_where_possible(
                part,
                [e for e in part.edges()
                 if abs(e.center().Z - z_step) < 0.3 and e.center().X > -14],
                (0.8, 0.5, 0.3),
            )

    part.label = "fixed_jaw"
    return part


if __name__ == "__main__":
    jaw = build_fixed_jaw()
    print("volume", round(jaw.volume, 1), "bbox", jaw.bounding_box())
    export_step(jaw, "export/fixed_jaw.step")
    export_stl(jaw, "export/fixed_jaw.stl", tolerance=0.03, angular_tolerance=0.25)
