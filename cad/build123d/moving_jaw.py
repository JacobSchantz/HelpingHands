"""The SO-101 moving jaw, parametrically.

Everything the shape depends on lives in ``params.py``.  Nothing here is a
literal dimension; the only numbers in this file are structural (how many
sections a loft needs, which way a hole points).

Run it directly to export the part on its own:

    .venv/bin/python moving_jaw.py
"""

from __future__ import annotations

from build123d import (
    Axis, Circle, Cylinder, GeomType, Location, Plane, Pos, RectangleRounded,
    Polygon, Rectangle, Rot, Solid, chamfer, export_step, export_stl,
    extrude, fillet, loft, mirror,
)

import params as P


# ---------------------------------------------------------------------------
#  the blade's two silhouette curves, as functions of y
# ---------------------------------------------------------------------------
def back_x(y: float) -> float:
    """X of the blade's back (outer) face — two straight tapers and a kink."""
    root_y = P.MJ_BLADE_Y[0]
    if y >= P.MJ_BACK_KINK_Y:
        return P.MJ_BACK_X_AT_ROOT - P.MJ_BACK_SLOPE_1 * (root_y - y)
    x_kink = P.MJ_BACK_X_AT_ROOT - P.MJ_BACK_SLOPE_1 * (root_y - P.MJ_BACK_KINK_Y)
    return x_kink - P.MJ_BACK_SLOPE_2 * (P.MJ_BACK_KINK_Y - y)


def front_x(y: float) -> float:
    """X of the gripping face — a staircase that steps toward the fixed jaw."""
    x = P.MJ_FACE_STEPS[0][1]
    for y_start, face_x in P.MJ_FACE_STEPS:
        if y <= y_start:
            x = face_x
    return x


def half_height(y: float) -> float:
    """Half the blade's Z height, interpolated between measured stations."""
    stations = P.MJ_BLADE_PROFILE
    if y >= stations[0][0]:
        return stations[0][1]
    if y <= stations[-1][0]:
        return stations[-1][1]
    for (y0, h0), (y1, h1) in zip(stations, stations[1:]):
        if y1 <= y <= y0:
            t = (y - y0) / (y1 - y0)
            return h0 + t * (h1 - h0)
    raise AssertionError("unreachable")


def blade_section(y: float, face_x: float, override=None):
    """One cross-section of the blade, as a face sitting in the plane y=const."""
    if override is None:
        x0, x1, h = face_x, back_x(y), half_height(y)
    else:
        x0, x1, h = override
    width, height = x1 - x0, 2 * h
    radius = min(P.MJ_BLADE_CORNER_R, 0.49 * min(width, height))
    plane = Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    return plane * Pos((x0 + x1) / 2, 0) * RectangleRounded(width, height, radius)


def blade() -> Solid:
    """Loft the blade: one segment per step of the gripping face, plus the
    flare where it grows out of the fork."""
    root = loft([
        blade_section(y, x0, override=(x0, x1, h))
        for y, x0, x1, h in P.MJ_ROOT_SECTIONS
    ])

    first_y = P.MJ_ROOT_SECTIONS[-1][0]
    steps = P.MJ_FACE_STEPS
    ends = [y for y, _ in steps[1:]] + [P.MJ_BLADE_PROFILE[-1][0]]
    result = root
    for (y_start, face_x), y_end in zip(steps, ends):
        y_start = min(y_start, first_y)
        if y_start <= y_end:
            continue
        ys = sorted(
            {y_start, y_end}
            | {y for y, _ in P.MJ_BLADE_PROFILE if y_end < y < y_start},
            reverse=True,
        )
        result += loft([blade_section(y, face_x) for y in ys])
    return result


# ---------------------------------------------------------------------------
#  the fork that clamps over the gripper servo horn
# ---------------------------------------------------------------------------
def yoke() -> Solid:
    x_front, _ = P.MJ_PLATE_X
    y_back = P.MJ_PLATE_Y_BACK
    # The plate's +X edge is not a separate dimension: it is the blade's back
    # face carried on past the root, which is why it has the same 6° taper.
    plan = Circle(P.MJ_HUB_D / 2) + fillet(
        Polygon(
            (x_front, 1.0), (x_front, y_back),
            (back_x(y_back), y_back), (back_x(1.0), 1.0),
            align=None,
        ).vertices().filter_by_position(Axis.Y, y_back - 0.1, y_back + 0.1),
        radius=P.MJ_PLATE_CORNER_R,
    )
    block = extrude(plan, amount=P.MJ_FORK_HALF_H, both=True)
    return block - cheek_taper_cut()


def cheek_taper_cut() -> Solid:
    """The cheeks' outer faces slope in toward the back of the fork.

    Swept as one profile so the taper is a single curve to edit, not two
    mirrored chamfers that have to be kept in step.
    """
    reach = P.MJ_PLATE_X[1] - P.MJ_PLATE_X[0] + 4
    y_first, h_first = P.MJ_CHEEK_TAPER[0]
    y_last, h_last = P.MJ_CHEEK_TAPER[-1]
    far = P.MJ_FORK_HALF_H + 6
    pts = [(y, h) for y, h in P.MJ_CHEEK_TAPER]
    upper = (
        [(y_first + 1, h_first), *pts, (y_last - 1, h_last)]
        + [(y_last - 1, far), (y_first + 1, far)]
    )
    profile = Plane(origin=(0, 0, 0),
                    x_dir=(0, 1, 0), z_dir=(1, 0, 0)) * Polygon(*upper, align=None)
    wedge = extrude(profile, amount=reach, both=True)
    return wedge + wedge.mirror(Plane.XY)


def throat_cut() -> Solid:
    """The gap between the fork's cheeks, where the servo and its horn sit."""
    z0, z1 = P.MJ_BOTTOM_PLATE_Z[1], P.MJ_TOP_PLATE_Z[0]
    x0, x1 = P.MJ_PLATE_X
    depth = P.MJ_HUB_D  # runs out past the +Y end of the plate
    plan = Pos((x0 + x1) / 2, (P.MJ_THROAT_Y + depth) / 2) * RectangleRounded(
        (x1 - x0) + 4, depth - P.MJ_THROAT_Y, P.MJ_PLATE_CORNER_R * 3
    )
    return extrude(Plane.XY.offset(z0) * plan, amount=z1 - z0)


def horn_recesses() -> list[Solid]:
    """Ø20 pockets in the cheeks' inner faces, clearing the horn disc."""
    out = []
    for z_face, direction in (
        (P.MJ_TOP_PLATE_Z[0], +1),
        (P.MJ_BOTTOM_PLATE_Z[1], -1),
    ):
        pocket = extrude(
            Plane.XY.offset(z_face) * Circle(P.MJ_HUB_D / 2),
            amount=direction * P.MJ_HORN_RECESS_DEPTH,
        )
        out.append(pocket)
    return out


# ---------------------------------------------------------------------------
#  holes
# ---------------------------------------------------------------------------
def horn_screw_holes() -> list[Solid]:
    """Four M3 through-holes with a counterbore on each outer face."""
    s = P.HORN_BOLT_SQUARE / 2
    cuts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            at = Pos(sx * s, sy * s)
            for (z0, z1), (cb0, cb1) in (
                (P.MJ_TOP_PLATE_Z, P.MJ_CB_TOP),
                (P.MJ_BOTTOM_PLATE_Z, P.MJ_CB_BOTTOM),
            ):
                cuts.append(
                    extrude(Plane.XY.offset(z0) * at * Circle(P.M3_CLEAR_D / 2),
                            amount=z1 - z0)
                )
                cuts.append(
                    extrude(Plane.XY.offset(cb0) * at * Circle(P.M3_SOCKET_D / 2),
                            amount=cb1 - cb0)
                )
    z0, z1 = P.MJ_CENTRE_HOLE_Z
    cuts.append(extrude(Plane.XY.offset(z0) * Circle(P.M3_CLEAR_D / 2), amount=z1 - z0))
    return cuts


def cheek_pockets() -> list[Solid]:
    """Ø8.4 lightening pockets straight through the fork cheeks."""
    x0, x1 = P.MJ_PLATE_X
    return [
        Plane(origin=(x0 - 1, y, z), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
        * extrude(Circle(P.MJ_POCKET_D / 2), amount=(x1 - x0) + 2)
        for y, z in P.MJ_POCKETS
    ]


def vent_holes() -> list[Solid]:
    """The Ø1.5 pattern marching down the blade.

    Half of them go through the blade's height; the others go through its
    thickness, drilled *normal to the back face* — which is what a tapering
    face makes awkward in a tool without real surface normals.
    """
    r = P.MJ_VENT_D / 2
    cuts = []

    for y in P.MJ_VENT_THROUGH_HEIGHT_Y:
        x = back_x(y) - P.MJ_VENT_BACK_OFFSET
        # far enough to break out of the fork as well as the blade: the first
        # of these holes sits under the fork's cheek, not the blade
        h = P.MJ_FORK_HALF_H + 2
        cuts.append(
            extrude(Plane.XY.offset(-h) * Pos(x, y) * Circle(r), amount=2 * h)
        )

    for y in P.MJ_VENT_THROUGH_THICKNESS_Y:
        slope = P.MJ_BACK_SLOPE_1 if y >= P.MJ_BACK_KINK_Y else P.MJ_BACK_SLOPE_2
        # outward normal of the back face, in the XY plane
        nx, ny = 1.0, -slope
        norm = (nx**2 + ny**2) ** 0.5
        nx, ny = nx / norm, ny / norm
        length = (back_x(y) - front_x(y)) + 6
        start = (back_x(y) + 3 * nx, y + 3 * ny, 0)
        plane = Plane(origin=start, x_dir=(0, 0, 1), z_dir=(-nx, -ny, 0))
        cuts.append(extrude(plane * Circle(r), amount=length))

    return cuts


# ---------------------------------------------------------------------------
#  assembly of the part
# ---------------------------------------------------------------------------
def _fillet_where_possible(part, edges, radii):
    """Try each radius in turn; keep the part unchanged if none of them take.

    OCCT will refuse (and occasionally abort the process) on a radius that
    does not fit, and the radius that fits depends on parameters the user is
    expected to change — so the model must not die when someone widens the
    blade.
    """
    if not edges:
        return part
    for radius in radii:
        try:
            candidate = fillet(edges, radius=radius)
        except Exception:  # noqa: BLE001 - OCCT raises bare failures here
            continue
        # A fillet that "succeeds" but leaves an invalid shell will crash the
        # hidden-line renderer several steps later, so check here.
        if candidate.is_valid:
            return candidate
    return part


def build_moving_jaw(*, fillets: bool = True) -> Solid:
    part = yoke() - throat_cut()
    for pocket in horn_recesses():
        part -= pocket

    part += blade()

    if fillets:
        # Real B-rep fillets, on edges that only exist after the boolean:
        # where the lofted blade meets the fork, and along the two steps in
        # the gripping face.  Radii are capped by what the geometry allows.
        part = _fillet_where_possible(
            part,
            [e for e in part.edges()
             if abs(e.center().Y - P.MJ_ROOT_SECTIONS[0][0]) < 0.3
             and e.length > 2 and abs(e.center().Z) < 20],
            (1.2, 0.8, 0.5),
        )
        for y_step, _ in P.MJ_FACE_STEPS[1:]:
            part = _fillet_where_possible(
                part,
                [e for e in part.edges()
                 if abs(e.center().Y - y_step) < 0.3 and e.center().X < -7],
                (0.8, 0.5, 0.3),
            )

    for cut in horn_screw_holes() + cheek_pockets() + vent_holes():
        part -= cut

    if fillets:
        # round the fingertip
        tip = [e for e in part.edges()
               if abs(e.center().Y - P.MJ_BLADE_PROFILE[-1][0]) < 0.4]
        if tip:
            try:
                part = fillet(tip, radius=1.0)
            except Exception:      # noqa: BLE001 - tip radius is cosmetic
                pass

    part.label = "moving_jaw"
    return part


if __name__ == "__main__":
    jaw = build_moving_jaw()
    print("volume", round(jaw.volume, 1), "bbox", jaw.bounding_box())
    export_step(jaw, "export/moving_jaw.step")
    export_stl(jaw, "export/moving_jaw.stl", tolerance=0.03, angular_tolerance=0.25)
