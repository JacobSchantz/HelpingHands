"""Score the parametric model against the reference B-rep.

This is the half of the exercise that only a tool with real geometry can do:
the reference STEP and the model are both solids in the same kernel, so
"how close is it?" has a number instead of an opinion.

    .venv/bin/python fidelity_check.py           # print
    .venv/bin/python fidelity_check.py --write   # -> FIDELITY.md

Three comparisons, cheapest first:

1. bounding box and volume;
2. cross-section area and extent at each of the stations the model was built
   from — this is what actually catches a wrong taper;
3. every hole: diameter, axis direction and position, matched nearest-first
   against the reference's, so a bolt pattern that has drifted shows up.
"""

from __future__ import annotations

import sys
from pathlib import Path

from build123d import Compound, GeomType, Plane, import_step
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.TopAbs import TopAbs_REVERSED

import params as P
from fixed_jaw import build_fixed_jaw
from moving_jaw import build_moving_jaw

HERE = Path(__file__).resolve().parent


def _is_bore(face, cyl) -> bool:
    """True when material lies outside the cylinder, i.e. it is a hole.

    Reading the face's TopAbs orientation works on an imported STEP but not
    reliably on a solid this script just built, so ask the geometry instead:
    does the outward normal point back toward the axis?
    """
    centre = face.center()
    axis = cyl.Axis()
    a_pt = axis.Location()
    a_dir = axis.Direction()
    v = (centre.X - a_pt.X(), centre.Y - a_pt.Y(), centre.Z - a_pt.Z())
    d = (a_dir.X(), a_dir.Y(), a_dir.Z())
    t = sum(x * y for x, y in zip(v, d))
    radial = tuple(x - t * y for x, y in zip(v, d))
    try:
        n = face.normal_at(centre)
    except Exception:  # noqa: BLE001 - normal_at can miss on a trimmed face
        return False
    return sum(a * b for a, b in zip(radial, (n.X, n.Y, n.Z))) < 0


def hole_list(solid, min_d=1.0):
    """(diameter, unit axis direction, a point on the axis) for every bore."""
    out = []
    for face in solid.faces():
        if face.geom_type != GeomType.CYLINDER:
            continue
        cyl = BRepAdaptor_Surface(face.wrapped).Cylinder()
        if not _is_bore(face, cyl):
            continue
        if 2 * cyl.Radius() < min_d:
            continue
        d = cyl.Axis().Direction()
        direction = (abs(d.X()), abs(d.Y()), abs(d.Z()))
        bb = face.bounding_box()
        centre = (bb.center().X, bb.center().Y, bb.center().Z)
        out.append((round(2 * cyl.Radius(), 3), direction, centre))
    return out


def match_holes(reference, model, tol=1.5):
    """Pair up holes by diameter and proximity; report what did not pair."""
    unmatched_ref, pairs = [], []
    pool = list(model)
    for d_ref, dir_ref, c_ref in reference:
        best, best_dist = None, 1e9
        for cand in pool:
            d_m, dir_m, c_m = cand
            if abs(d_m - d_ref) > 0.35:
                continue
            if sum((a - b) ** 2 for a, b in zip(dir_ref, dir_m)) > 0.02:
                continue
            dist = sum((a - b) ** 2 for a, b in zip(c_ref, c_m)) ** 0.5
            if dist < best_dist:
                best, best_dist = cand, dist
        if best is not None and best_dist <= tol:
            pool.remove(best)
            pairs.append((d_ref, c_ref, best_dist))
        else:
            unmatched_ref.append((d_ref, c_ref, best_dist if best else None))
    return pairs, unmatched_ref, pool


def section_area(solid, axis: str, value: float):
    normal = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
    origin = tuple(value * c for c in normal)
    section = solid & Plane(origin=origin, z_dir=normal)
    faces = list(section.faces()) if section else []
    if not faces:
        return None, None
    bb = Compound(children=faces).bounding_box()
    return sum(f.area for f in faces), bb


def compare(name, reference, model, axis, stations) -> list[str]:
    lines = [f"\n## {name}\n"]
    rb, mb = reference.bounding_box(), model.bounding_box()
    lines += [
        "| | reference | model | Δ |",
        "|---|---|---|---|",
        f"| volume | {reference.volume:.0f} mm³ | {model.volume:.0f} mm³ | "
        f"{100 * (model.volume - reference.volume) / reference.volume:+.1f}% |",
    ]
    for ax in "XYZ":
        r0, r1 = getattr(rb.min, ax), getattr(rb.max, ax)
        m0, m1 = getattr(mb.min, ax), getattr(mb.max, ax)
        lines.append(
            f"| {ax} extent | {r0:.2f} … {r1:.2f} | {m0:.2f} … {m1:.2f} | "
            f"{m0 - r0:+.2f} / {m1 - r1:+.2f} |"
        )

    lines += ["", f"### Cross-sections along {axis.upper()}", "",
              f"| {axis} | ref area | model area | Δ area | Δ extent |",
              "|---|---|---|---|---|"]
    worst = 0.0
    for v in stations:
        ra, rbb = section_area(reference, axis, v)
        ma, mbb = section_area(model, axis, v)
        if ra is None or ma is None:
            lines.append(f"| {v} | {'—' if ra is None else f'{ra:.0f}'} | "
                         f"{'—' if ma is None else f'{ma:.0f}'} | — | — |")
            continue
        d_ext = max(
            abs(getattr(mbb.min, a) - getattr(rbb.min, a))
            for a in "XYZ"
        )
        d_ext = max(d_ext, max(abs(getattr(mbb.max, a) - getattr(rbb.max, a))
                               for a in "XYZ"))
        worst = max(worst, d_ext)
        lines.append(f"| {v} | {ra:.0f} | {ma:.0f} | "
                     f"{100 * (ma - ra) / ra:+.1f}% | {d_ext:.2f} mm |")
    lines.append("")
    lines.append(f"Worst silhouette error at any station: **{worst:.2f} mm**.")

    ref_holes, mod_holes = hole_list(reference), hole_list(model)
    pairs, missing, extra = match_holes(ref_holes, mod_holes)
    lines += ["", "### Holes", "",
              f"- reference has {len(ref_holes)} bores, the model has "
              f"{len(mod_holes)}",
              f"- **{len(pairs)} matched** (same Ø, same axis, within 1.5 mm)"]
    if pairs:
        worst_pair = max(pairs, key=lambda p: p[2])
        lines.append(f"- worst matched-hole position error: "
                     f"{worst_pair[2]:.2f} mm (Ø{worst_pair[0]})")
    if missing:
        lines.append(f"- **{len(missing)} in the reference with no counterpart**: "
                     + ", ".join(f"Ø{d} at ({c[0]:.1f}, {c[1]:.1f}, {c[2]:.1f})"
                                 for d, c, _ in missing[:10])
                     + (" …" if len(missing) > 10 else ""))
    if extra:
        lines.append(f"- {len(extra)} in the model with no counterpart "
                     "(fillet faces and split bores land here)")
    return lines


def report() -> str:
    out = ["# Fidelity — parametric model vs. reference STEP\n",
           "Generated by `fidelity_check.py`. Everything is measured against",
           "the committed reference B-rep, in the same kernel, so these are",
           "real geometric differences and not renderings compared by eye.\n"]

    out += compare(
        "Moving jaw",
        import_step(str(HERE / "reference/Moving_Jaw_SO101.step")),
        build_moving_jaw(),
        "y",
        [-5, -12, -18, -20, -24, -30, -36, -44, -56, -64, -70, -76, -80],
    )
    out += compare(
        "Wrist-roll follower",
        import_step(str(HERE / "reference/Wrist_Roll_Follower_SO101.step")),
        build_fixed_jaw(),
        "z",
        [3, 8, 13, 18, 24, 30, 36, 42, 55, 65, 75, 85, 95, 103],
    )
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    text = report()
    if "--write" in sys.argv:
        (HERE / "FIDELITY.md").write_text(text)
        print(f"wrote {HERE / 'FIDELITY.md'}")
    else:
        print(text)
