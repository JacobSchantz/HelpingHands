#!/usr/bin/env python3
"""Measure the SO-101 reference STEP files without a CAD kernel.

Blender cannot read STEP and no OCCT binding is installed on this machine, so
this reads the ISO-10303-21 text directly.  STEP AP214 stores analytic
geometry explicitly -- CARTESIAN_POINT coordinates, CIRCLE radii,
CYLINDRICAL_SURFACE radii and their AXIS2_PLACEMENT_3D frames -- so every
number printed here is read out of the file, not eyeballed off a mesh.

Read-only: it never writes to cad/build123d/reference/.

Usage:  python3 measure_step.py <file.step> [...]
"""
import re
import sys
from collections import defaultdict

ENTITY_RE = re.compile(r"#(\d+)\s*=\s*([A-Z_0-9]+)\s*\((.*)\)\s*;", re.S)


def load(path):
    """Return {id: (TYPE, [args])} for every simple entity in the DATA section."""
    with open(path, "r", errors="replace") as fh:
        text = fh.read()
    text = text.split("DATA;", 1)[1].rsplit("ENDSEC;", 1)[0]
    # STEP statements are ';'-terminated; strings may not contain ';' here.
    out = {}
    for stmt in text.split(";"):
        m = ENTITY_RE.match(stmt.strip() + ";")
        if m:
            out[int(m.group(1))] = (m.group(2), split_args(m.group(3)))
    return out


def split_args(s):
    """Split a STEP argument list on top-level commas."""
    args, depth, cur, in_str = [], 0, [], False
    for ch in s:
        if in_str:
            cur.append(ch)
            if ch == "'":
                in_str = False
            continue
        if ch == "'":
            in_str = True
            cur.append(ch)
        elif ch == "(":
            depth += 1
            cur.append(ch)
        elif ch == ")":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            args.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        args.append("".join(cur).strip())
    return args


def ref(a):
    return int(a[1:]) if a.startswith("#") else None


def point(ents, eid):
    t, a = ents[eid]
    assert t == "CARTESIAN_POINT", t
    return tuple(float(v) for v in split_args(a[1].strip("()")))


def direction(ents, eid):
    t, a = ents[eid]
    return tuple(float(v) for v in split_args(a[1].strip("()")))


def placement(ents, eid):
    """AXIS2_PLACEMENT_3D -> (origin, axis-direction or None)."""
    t, a = ents[eid]
    org = point(ents, ref(a[1]))
    axis = direction(ents, ref(a[2])) if ref(a[2]) else None
    return org, axis


def fmt(v):
    return f"{v:9.3f}"


def report(path):
    ents = load(path)
    print("=" * 78)
    print(path)
    print("=" * 78)

    # --- vertex bounding box: exact B-rep vertices, no tessellation ---------
    verts = [point(ents, ref(a[1])) for t, a in ents.values() if t == "VERTEX_POINT"]
    lo = [min(v[i] for v in verts) for i in range(3)]
    hi = [max(v[i] for v in verts) for i in range(3)]
    print(f"\nvertices: {len(verts)}")
    print("bbox min ", " ".join(fmt(v) for v in lo))
    print("bbox max ", " ".join(fmt(v) for v in hi))
    print("bbox size", " ".join(fmt(hi[i] - lo[i]) for i in range(3)), " (mm)")

    # --- cylinders: holes, bosses, pins, fillet-free round features --------
    cyl = defaultdict(list)
    for t, a in ents.values():
        if t == "CYLINDRICAL_SURFACE":
            org, ax = placement(ents, ref(a[1]))
            cyl[round(float(a[2]), 4)].append((org, ax))
    print(f"\ncylindrical surfaces by radius ({len(cyl)} distinct radii):")
    print("   radius      dia   count   axis dir          example origin")
    for r in sorted(cyl):
        locs, ax = cyl[r], cyl[r][0][1]
        o = locs[0][0]
        axs = " ".join(f"{v:5.2f}" for v in ax) if ax else "    ?"
        print(f"  {r:7.3f}  {2*r:7.3f}   {len(locs):5d}   [{axs}]  "
              f"({o[0]:8.3f},{o[1]:8.3f},{o[2]:8.3f})")

    # --- circles: bolt circles, edge radii, arc features -------------------
    circ = defaultdict(list)
    for t, a in ents.values():
        if t == "CIRCLE":
            org, ax = placement(ents, ref(a[1]))
            circ[round(float(a[2]), 4)].append(org)
    print(f"\ncircle radii ({len(circ)} distinct):")
    for r in sorted(circ):
        print(f"  r={r:7.3f}  d={2*r:7.3f}  n={len(circ[r]):3d}   centres: "
              + "; ".join(f"({p[0]:.2f},{p[1]:.2f},{p[2]:.2f})" for p in circ[r][:4])
              + (" ..." if len(circ[r]) > 4 else ""))

    # --- planes: face positions, useful for wall thickness / plate faces ---
    zs = defaultdict(int)
    for t, a in ents.values():
        if t == "PLANE":
            org, ax = placement(ents, ref(a[1]))
            if ax and abs(abs(ax[2]) - 1.0) < 1e-6:
                zs[round(org[2], 3)] += 1
    if zs:
        print("\nZ-normal plane heights (z: face count):")
        print("  " + "  ".join(f"{z:.2f}:{n}" for z, n in sorted(zs.items())))

    tor = [(round(float(a[2]), 4), round(float(a[3]), 4))
           for t, a in ents.values() if t == "TOROIDAL_SURFACE"]
    if tor:
        print("\ntoroidal surfaces (major, minor) -- fillets/rounds:")
        for major, minor in sorted(set(tor)):
            print(f"  major={major:7.3f}  minor={minor:7.3f}  "
                  f"n={tor.count((major, minor))}")

    con = [(round(float(a[2]), 4), round(float(a[3]), 6))
           for t, a in ents.values() if t == "CONICAL_SURFACE"]
    if con:
        print("\nconical surfaces (radius, half-angle rad / deg) -- chamfers, "
              "countersinks:")
        for r, ang in sorted(set(con)):
            import math
            print(f"  r={r:7.3f}  angle={ang:.6f} rad = {math.degrees(ang):.2f} deg  "
                  f"n={con.count((r, ang))}")

    sph = [round(float(a[2]), 4) for t, a in ents.values()
           if t == "SPHERICAL_SURFACE"]
    if sph:
        print("\nspherical surfaces r: " + ", ".join(f"{r}" for r in sorted(set(sph))))
    print()


if __name__ == "__main__":
    for p in sys.argv[1:]:
        report(p)
