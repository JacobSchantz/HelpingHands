#!/usr/bin/env python3
"""print_gen_04.py: the gen_04 first-test-print package.

Exports every printed part of gen_04_index_print.scad in its print
orientation (part="print"), drops it on z = 0, checks each mesh, lays the
parts out on one 256 x 256 plate, and records the print settings read from
Bambu Studio's own X1C profiles:

    python3 print_gen_04.py            # writes print/gen_04/ and its report.md

Mesh checks (numpy only): closed and consistently oriented (every edge
shared by exactly two faces, once each way), one body (no islands), volume,
size, the area resting on the bed, the down-facing area steeper than 45 deg
that is not on the bed (what needs support), and wall thickness: rays cast
inward from points spread over the surface, the distance to the far side.

Not sliced here: on this Mac Bambu Studio's command line (2.04.00.70)
crashes in GUI_App::plater() from PartPlateList::set_shapes for STL and 3MF
input alike, and the CuraEngine inside UltiMaker Cura hangs in dyld before
it prints anything. Slice the plate in the Bambu Studio app (report.md).
"""
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'gen_04_index_print.scad'
OUT = HERE / 'print' / 'gen_04'
SCAD = os.environ.get('OPENSCAD', '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD')
BAMBU_PROFILES = Path.home() / 'Library/Application Support/BambuStudio/system/BBL'

# [piece, count, support, what it is, bodies]
PARTS = [
    ('coupon', 1, False, 'pin and clearance coupon (bar, comb, tab): print and test this first', 3),
    ('proximal', 1, True, 'proximal saddle, top down (supports only under the MCP tab)', 1),
    ('middle', 1, False, 'middle saddle, top down', 1),
    ('distal', 1, False, 'distal saddle with the fingertip cap, top down', 1),
    ('base', 1, True, 'base over the back of the hand, upright (supports under the pad and the post)', 1),
    ('drum', 1, False, 'line drum with knob, lock-hole flange down', 1),
]
BED = 256.0
WALL_MIN = 1.2   # three 0.4 mm lines


def read_stl(path):
    data = path.read_bytes()
    if data[:5] == b'solid' and b'facet' in data[:400]:
        v = [list(map(float, line.split()[1:4])) for line in data.decode().splitlines() if line.strip().startswith('vertex')]
        return np.array(v, dtype=float).reshape(-1, 3, 3)
    n = struct.unpack('<I', data[80:84])[0]
    rec = np.frombuffer(data[84:84 + 50 * n], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    return rec['v'].astype(float)


def write_stl(path, tris):
    tris = np.asarray(tris, dtype=np.float32)
    e1, e2 = tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]
    n = np.cross(e1, e2)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(tris), dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    rec['n'], rec['v'] = n, tris
    path.write_bytes(b'gen_04_index_print'.ljust(80, b' ') + struct.pack('<I', len(tris)) + rec.tobytes())


def export(piece):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'p.stl'
        subprocess.run([SCAD, '--backend', 'Manifold', '--export-format', 'binstl', '-o', str(out),
                        '-D', 'part="print"', '-D', f'piece="{piece}"', str(SOURCE)], capture_output=True, check=True)
        tris = read_stl(out)
    lo = tris.reshape(-1, 3).min(axis=0)
    hi = tris.reshape(-1, 3).max(axis=0)
    return tris - np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])


def mesh_check(tris, seed=4):
    v = tris.reshape(-1, 3)
    key = np.round(v / 1e-4).astype(np.int64)
    uniq, idx = np.unique(key, axis=0, return_inverse=True)
    faces = idx.reshape(-1, 3)
    faces = faces[(faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])]
    directed = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    d_keys, d_counts = np.unique(directed, axis=0, return_counts=True)
    undirected = np.sort(directed, axis=1)
    u_keys, u_counts = np.unique(undirected, axis=0, return_counts=True)
    closed = bool(np.all(u_counts == 2))
    oriented = bool(np.all(d_counts == 1)) and closed
    # bodies: union-find over vertices joined by faces
    parent = np.arange(len(uniq))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for f in faces:
        ra, rb, rc = find(f[0]), find(f[1]), find(f[2])
        parent[rb] = ra
        parent[rc] = ra
    bodies = len({find(a) for a in np.unique(faces)})
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    cross = np.cross(b - a, c - a)
    area = np.linalg.norm(cross, axis=1) / 2
    normal = cross / np.maximum(2 * area[:, None], 1e-12)
    volume = float(np.sum(np.einsum('ij,ij->i', a, np.cross(b, c))) / 6)
    zmin = tris[:, :, 2].min(axis=1)
    on_bed = (tris[:, :, 2].max(axis=1) < 0.01) & (normal[:, 2] < -0.99)
    steep = (normal[:, 2] < -math.cos(math.radians(45))) & ~on_bed & (zmin > 0.2)
    thickness = wall_thickness(tris, normal, area, seed)
    return dict(closed=closed, oriented=oriented, bodies=bodies, volume=volume,
                size=(tris.reshape(-1, 3).max(axis=0) - tris.reshape(-1, 3).min(axis=0)).tolist(),
                bed=float(area[on_bed].sum()), overhang=float(area[steep].sum()), thickness=thickness,
                triangles=len(tris))


def wall_thickness(tris, normal, area, seed, samples=4000):
    """Inward ray from points spread over the surface (by area) to the nearest
    other face: the wall's thickness there. Möller-Trumbore, in chunks."""
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(tris), size=samples, p=area / area.sum())
    r1, r2 = rng.random(samples), rng.random(samples)
    s = np.sqrt(r1)
    pts = (tris[pick, 0] * (1 - s)[:, None] + tris[pick, 1] * (s * (1 - r2))[:, None] + tris[pick, 2] * (s * r2)[:, None])
    dirs = -normal[pick]
    pts = pts + dirs * 1e-3
    v0, e1, e2 = tris[:, 0], tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]
    best = np.full(samples, np.inf)
    for i in range(0, samples, 64):
        o, d = pts[i:i + 64, None, :], dirs[i:i + 64, None, :]
        p = np.cross(d, e2[None])
        det = np.einsum('ijk,ijk->ij', np.broadcast_to(e1[None], p.shape), p)
        ok = np.abs(det) > 1e-12
        inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
        t = o - v0[None]
        u = np.einsum('ijk,ijk->ij', t, p) * inv
        q = np.cross(t, np.broadcast_to(e1[None], t.shape))
        w = np.einsum('ijk,ijk->ij', np.broadcast_to(d, q.shape), q) * inv
        dist = np.einsum('ijk,ijk->ij', np.broadcast_to(e2[None], q.shape), q) * inv
        hit = ok & (u >= 0) & (w >= 0) & (u + w <= 1) & (dist > 1e-3)
        best[i:i + 64] = np.where(hit, dist, np.inf).min(axis=1)
    best = best[np.isfinite(best)]
    return dict(p1=float(np.percentile(best, 1)), p5=float(np.percentile(best, 5)), median=float(np.median(best)),
                under=float(np.mean(best < WALL_MIN)))


def layout(meshes):
    """Shelf-pack the parts' footprints on the bed, 6 mm apart."""
    placed, x, y, row = [], 8.0, 8.0, 0.0
    for name, tris in meshes:
        lo, hi = tris.reshape(-1, 3).min(axis=0), tris.reshape(-1, 3).max(axis=0)
        w, d = hi[0] - lo[0], hi[1] - lo[1]
        if x + w > BED - 8:
            x, y, row = 8.0, y + row + 6, 0.0
        placed.append((name, tris + np.array([x - lo[0], y - lo[1], 0])))
        x, row = x + w + 6, max(row, d)
    if y + row > BED - 8:
        raise SystemExit('parts do not fit on one plate')
    return placed


def bambu_profile(kind, name):
    d = json.loads((BAMBU_PROFILES / kind / f'{name}.json').read_text())
    if d.get('inherits'):
        base = bambu_profile(kind, d['inherits'])
        base.update(d)
        d = base
    return d


def first(v):
    return v[0] if isinstance(v, list) else v


def settings():
    """The print settings, read from Bambu Studio's X1C 0.4 / 0.20 Standard /
    Bambu PETG Basic profiles where they exist there: [setting, value, source]."""
    try:
        m = bambu_profile('machine', 'Bambu Lab X1 Carbon 0.4 nozzle')
        p = bambu_profile('process', '0.20mm Standard @BBL X1C')
        f = bambu_profile('filament', 'Bambu PETG Basic @BBL X1C')
    except FileNotFoundError:
        return []
    prof = 'Bambu Studio profile'
    return [
        ('Printer', m['name'], prof), ('Nozzle', f'{first(m["nozzle_diameter"])} mm', prof),
        ('Process', p['name'], prof), ('Layer height', f'{p["layer_height"]} mm (first {p["initial_layer_print_height"]})', prof),
        ('Filament', f['name'], prof),
        ('Nozzle temperature', f'{first(f["nozzle_temperature"])} °C (first layer {first(f["nozzle_temperature_initial_layer"])})', prof),
        ('Bed', f'Textured PEI {first(f["textured_plate_temp"])} °C (first layer {first(f["textured_plate_temp_initial_layer"])})', prof),
        ('Walls', '3 (profile has ' + str(p['wall_loops']) + ')', 'changed: pin bores and lugs want solid walls'),
        ('Infill', '40 % gyroid (profile has ' + p['sparse_infill_density'] + ')', 'changed: thin parts, mostly walls anyway'),
        ('Supports', 'per part, see the table: tree (auto), on build plate only, threshold 30°', 'changed per part'),
        ('Brim', 'on for the saddles and the base (narrow tops on the bed)', 'changed'),
    ]


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    meshes, report = [], {}
    for name, count, support, what, bodies in PARTS:
        tris = export(name)
        write_stl(OUT / f'gen_04_{name}.stl', tris)
        meshes.append((name, tris))
        report[name] = mesh_check(tris)
        print(f'{name}: {report[name]}', file=sys.stderr)
    plate = layout(meshes)
    write_stl(OUT / 'gen_04_plate.stl', np.concatenate([t for _, t in plate]))
    write_report(report, settings())
    ok = all(report[n]['closed'] and report[n]['oriented'] and report[n]['bodies'] == b for n, *_, b in PARTS)
    print('PASS' if ok else 'FAIL')
    return 0 if ok else 1


def write_report(report, conf):
    lines = ['# gen_04 print package: checks\n',
             'Written by `print_gen_04.py`; do not edit by hand. Not sliced (see the script\'s docstring).\n',
             '## Meshes (print orientation, on z = 0)\n',
             '| Part | Count | Prints | Closed + oriented | Bodies | Volume, cm³ | Size x × y × z, mm | On the bed, mm² '
             '| Down-facing > 45° off the bed, mm² | Wall 1st / 5th pct / median, mm | Sampled walls under 1.2 mm |',
             '|---|---|---|---|---|---|---|---|---|---|---|']
    for name, count, support, what, bodies in PARTS:
        r = report[name]
        t = r['thickness']
        lines.append(f'| {name} | {count} | {what} | {"yes" if r["closed"] and r["oriented"] else "**NO**"} | '
                     f'{r["bodies"] if r["bodies"] == bodies else "**" + str(r["bodies"]) + "**"} | {r["volume"] / 1000:.1f} | '
                     + ' × '.join(f'{v:.0f}' for v in r['size']) + f' | {r["bed"]:.0f} | {r["overhang"]:.0f} | '
                     f'{t["p1"]:.1f} / {t["p5"]:.1f} / {t["median"]:.1f} | {t["under"]:.0%} |')
    total = sum(report[n]['volume'] for n, *_ in PARTS) / 1000
    lines.append(f'\nTotal {total:.1f} cm³ of solid, about {total * 1.27:.0f} g of PETG if printed solid (less with infill).')
    if conf:
        lines += ['\n## Settings\n', '| Setting | Value | From |', '|---|---|---|']
        lines += [f'| {a} | {b} | {c} |' for a, b, c in conf]
    (OUT / 'report.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
