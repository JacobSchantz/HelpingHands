"""Measure the reference SO-101 STEP files as analytic B-rep, not as a mesh.

This is the tool that produced every ``[STEP]`` number in ``params.py``.  It
loads ``reference/Moving_Jaw_SO101.step`` and
``reference/Wrist_Roll_Follower_SO101.step`` through OCCT and interrogates the
*surfaces*: a cylinder reports its exact radius and axis, a plane its exact
normal and offset, a torus its exact fillet radius.  Nothing here is read off a
tessellation, so the numbers are the ones the original CAD author typed.

    ../build123d/.venv/bin/python measure_reference.py          # print
    ../build123d/.venv/bin/python measure_reference.py --write  # -> MEASUREMENTS.md

The reference files are never modified.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from build123d import Compound, GeomType, Plane, import_step
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.TopAbs import TopAbs_REVERSED

HERE = Path(__file__).resolve().parent
REFERENCE = HERE / "reference"
MOVING_JAW = REFERENCE / "Moving_Jaw_SO101.step"
WRIST_ROLL_FOLLOWER = REFERENCE / "Wrist_Roll_Follower_SO101.step"


# --------------------------------------------------------------------------
#  surface interrogation
# --------------------------------------------------------------------------
@dataclass
class Cyl:
    radius: float
    direction: tuple[float, float, float]
    axis_point: tuple[float, float, float]
    concave: bool          # True => material outside the surface, i.e. a hole
    area: float
    bbox: tuple[float, ...]


@dataclass
class Pln:
    normal: tuple[float, float, float]
    offset: float          # n . p, so the plane is  n . x = offset
    area: float


def _round(v, n=3):
    return tuple(round(float(x), n) for x in v)


def cylinders(solid) -> list[Cyl]:
    out = []
    for face in solid.faces():
        if face.geom_type != GeomType.CYLINDER:
            continue
        cyl = BRepAdaptor_Surface(face.wrapped).Cylinder()
        axis = cyl.Axis()
        d, p = axis.Direction(), axis.Location()
        bb = face.bounding_box()
        out.append(
            Cyl(
                radius=cyl.Radius(),
                direction=_round((d.X(), d.Y(), d.Z())),
                axis_point=_round((p.X(), p.Y(), p.Z()), 2),
                concave=face.wrapped.Orientation() == TopAbs_REVERSED,
                area=face.area,
                bbox=(bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z),
            )
        )
    return out


def planes(solid) -> list[Pln]:
    out = []
    for face in solid.faces():
        if face.geom_type != GeomType.PLANE:
            continue
        pl = BRepAdaptor_Surface(face.wrapped).Plane()
        n, p = pl.Axis().Direction(), pl.Location()
        nx, ny, nz = n.X(), n.Y(), n.Z()
        off = nx * p.X() + ny * p.Y() + nz * p.Z()
        if (nx, ny, nz) < (0.0, 0.0, 0.0):       # canonicalise the sign
            nx, ny, nz, off = -nx, -ny, -nz, -off
        out.append(Pln(_round((nx, ny, nz)), round(off, 3), face.area))
    return out


def fillet_radii(solid) -> dict[float, int]:
    """Minor radii of every toroidal face — the original's real fillets."""
    radii: dict[float, int] = defaultdict(int)
    for face in solid.faces():
        if face.geom_type == GeomType.TORUS:
            radii[round(BRepAdaptor_Surface(face.wrapped).Torus().MinorRadius(), 3)] += 1
    return dict(radii)


def stations(solid, axis: str, values) -> list[tuple]:
    """Cross-section extents along one axis — how a tapering blade is measured."""
    normal = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
    rows = []
    for v in values:
        origin = tuple(v * c for c in normal)
        section = solid & Plane(origin=origin, z_dir=normal)
        faces = list(section.faces()) if section else []
        if not faces:
            rows.append((v, None))
            continue
        bb = Compound(children=faces).bounding_box()
        rows.append(
            (v, (round(bb.min.X, 2), round(bb.max.X, 2),
                 round(bb.min.Y, 2), round(bb.max.Y, 2),
                 round(bb.min.Z, 2), round(bb.max.Z, 2)))
        )
    return rows


# --------------------------------------------------------------------------
#  report
# --------------------------------------------------------------------------
def holes_table(solid, min_radius=0.7, min_area=8.0) -> list[str]:
    lines = ["| Ø | axis | axis passes through | through-material | area mm² |",
             "|---|------|---------------------|------------------|----------|"]
    for c in sorted(cylinders(solid), key=lambda c: (-c.radius, c.axis_point)):
        if c.radius < min_radius or c.area < min_area or not c.concave:
            continue
        lines.append(
            f"| {2 * c.radius:.2f} | {c.direction} | {c.axis_point} | "
            f"x {c.bbox[0]:.2f}..{c.bbox[1]:.2f}, y {c.bbox[2]:.2f}..{c.bbox[3]:.2f}, "
            f"z {c.bbox[4]:.2f}..{c.bbox[5]:.2f} | {c.area:.1f} |"
        )
    return lines


def report() -> str:
    out: list[str] = []
    w = out.append
    w("# Reference measurements — SO-101 gripper\n")
    w("Generated by `measure_reference.py` from the two committed STEP files.")
    w("Every number below was read off **analytic B-rep surfaces** (exact radii,")
    w("exact plane normals), never off a tessellation. Re-run the script to")
    w("re-derive any dimension in `params.py`.\n")

    for path, name, ax, vals in [
        (MOVING_JAW, "Moving jaw", "y",
         [-20, -22, -22.5, -23, -24, -25, -26, -28, -30, -32, -34, -36, -40, -44,
          -50, -56, -60, -62, -64, -66, -70, -72, -74, -78, -80, -81]),
        (WRIST_ROLL_FOLLOWER, "Wrist-roll follower (gripper body / fixed jaw)", "z",
         [0.5, 3, 6.5, 10, 12, 18, 26, 34, 38, 40, 42, 45, 55, 60, 65, 70, 75, 80,
          85, 90, 95, 100, 103, 105]),
    ]:
        solid = import_step(str(path))
        bb = solid.bounding_box()
        w(f"\n## {name}\n")
        w(f"`{path.name}`\n")
        w(f"- bounding box: x {bb.min.X:.2f}..{bb.max.X:.2f}, "
          f"y {bb.min.Y:.2f}..{bb.max.Y:.2f}, z {bb.min.Z:.2f}..{bb.max.Z:.2f} mm")
        w(f"- volume: {solid.volume:.0f} mm³")
        w(f"- faces: {len(solid.faces())} "
          f"({sum(1 for f in solid.faces() if f.geom_type == GeomType.BSPLINE)} of them B-spline)")
        rad = fillet_radii(solid)
        w(f"- toroidal fillet radii present: "
          + (", ".join(f"R{r} ×{n}" for r, n in sorted(rad.items())) or "none"))

        w(f"\n### Holes and bores\n")
        out.extend(holes_table(solid))

        w(f"\n### Cross-section stations along {ax.upper()}\n")
        w(f"| {ax} | x min | x max | y min | y max | z min | z max |")
        w("|---|---|---|---|---|---|---|")
        for v, ext in stations(solid, ax, vals):
            if ext is None:
                w(f"| {v} | — | — | — | — | — | — |")
            else:
                w(f"| {v} | " + " | ".join(f"{e:.2f}" for e in ext) + " |")

        w(f"\n### Distinct plane normals (largest faces first)\n")
        by_normal: dict[tuple, list[float]] = defaultdict(list)
        for p in planes(solid):
            by_normal[p.normal].append(p.offset)
        w("| normal | offsets (n·x = offset) |")
        w("|---|---|")
        for n, offs in sorted(by_normal.items(), key=lambda kv: -len(kv[1]))[:12]:
            uniq = sorted(set(offs))
            w(f"| {n} | {', '.join(f'{o:g}' for o in uniq[:12])}"
              + (" …" if len(uniq) > 12 else "") + " |")

    return "\n".join(out) + "\n"


if __name__ == "__main__":
    text = report()
    if "--write" in sys.argv:
        (HERE / "MEASUREMENTS.md").write_text(text)
        print(f"wrote {HERE / 'MEASUREMENTS.md'}")
    else:
        print(text)
