#!/usr/bin/env python3
"""Read dimensions out of an AP214 STEP file. No dependencies, stdlib only.

Every number tagged [STEP] in params.scad came from this. STEP carries exact
analytic geometry, so a planar face is a normal plus an offset and a hole is a
cylinder radius plus an axis -- none of it needs tessellating, and none of it
needs a CAD kernel to read. Run it against the reference parts and grep:

    python3 tools/measure_step.py ../build123d/reference/Moving_Jaw_SO101.step
    python3 tools/measure_step.py ../build123d/reference/Wrist_Roll_Follower_SO101.step

    planes     signed normal + offset, grouped -- these are the flat faces,
               so "n=(1,0,0) off=-8.3" is literally the gripping face
    cylinders  radius + axis + location, grouped by radius -- bolt holes,
               counterbores, bores
    bbox       from VERTEX_POINTs only (B-spline control points lie outside
               the solid and would inflate a naive min/max over every point)
"""
import re
import sys
from collections import defaultdict


def load(path):
    txt = open(path).read().split("DATA;", 1)[1].split("ENDSEC;", 1)[0]
    ents = {}
    for stmt in txt.split(";"):
        stmt = stmt.strip()
        if not stmt.startswith("#"):
            continue
        m = re.match(r"#(\d+)\s*=\s*([A-Z_0-9]+)\s*\((.*)\)$", stmt, re.S)
        if m:
            ents[int(m.group(1))] = (m.group(2), m.group(3).replace("\n", ""))
    return ents


def triple(ents, ref):
    """CARTESIAN_POINT / DIRECTION -> (x, y, z)."""
    nums = re.search(r"\(([^()]*)\)\s*$", ents[ref][1]).group(1)
    return tuple(float(v) for v in nums.split(","))


def placement(ents, ref):
    """AXIS2_PLACEMENT_3D -> (location, axis)."""
    refs = [int(v) for v in re.findall(r"#(\d+)", ents[ref][1])]
    loc = triple(ents, refs[0])
    axis = triple(ents, refs[1]) if len(refs) > 1 else (0.0, 0.0, 1.0)
    return loc, axis


def split_args(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def report(path):
    ents = load(path)
    print("=" * 72)
    print(path)
    print("=" * 72)

    verts = []
    for ref, (kind, args) in ents.items():
        if kind == "VERTEX_POINT":
            verts.append(triple(ents, int(re.search(r"#(\d+)", args).group(1))))
    print("\nBOUNDING BOX  (%d vertices)" % len(verts))
    for i, name in enumerate("XYZ"):
        vals = [v[i] for v in verts]
        print("  %s %9.3f .. %9.3f   (%8.3f)"
              % (name, min(vals), max(vals), max(vals) - min(vals)))

    print("\nPLANAR FACES  (normal, offset along it, how many)")
    planes = defaultdict(int)
    for ref, (kind, args) in ents.items():
        if kind != "PLANE":
            continue
        loc, axis = placement(ents, int(re.search(r"#(\d+)", args).group(1)))
        # normalise the sign so mirrored faces group together
        big = max(range(3), key=lambda i: abs(axis[i]))
        sign = -1.0 if axis[big] < 0 else 1.0
        n = tuple(round(sign * a, 3) for a in axis)
        off = sum(loc[i] * n[i] for i in range(3))
        planes[(n, round(off, 3))] += 1
    for (n, off), count in sorted(planes.items(), key=lambda kv: (kv[0][0], kv[1])):
        print("  n=(%6.3f,%6.3f,%6.3f)  off=%9.3f  x%d" % (n[0], n[1], n[2], off, count))

    print("\nCYLINDRICAL FACES  (radius -> axis, location)")
    cyls = defaultdict(list)
    for ref, (kind, args) in ents.items():
        if kind != "CYLINDRICAL_SURFACE":
            continue
        parts = split_args(args)
        radius = float(parts[-1])
        loc, axis = placement(ents, int(re.search(r"#(\d+)", parts[1]).group(1)))
        cyls[round(radius, 4)].append((loc, axis))
    for radius in sorted(cyls):
        print("  R=%7.3f  D=%7.3f  n=%d" % (radius, 2 * radius, len(cyls[radius])))
        seen = set()
        for loc, axis in cyls[radius]:
            key = tuple(round(v, 2) for v in loc) + tuple(round(abs(a), 2) for a in axis)
            if key in seen:
                continue
            seen.add(key)
            print("      at (%8.3f,%8.3f,%8.3f)  axis (%5.2f,%5.2f,%5.2f)"
                  % (loc + axis))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arg in sys.argv[1:]:
        report(arg)
