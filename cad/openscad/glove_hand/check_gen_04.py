#!/usr/bin/env python3
"""check_gen_04.py: interference, neighbour and tendon numbers for the gen_04 index finger.

Every check is one OpenSCAD intersection of two bodies at one pose
(gen_04_index_print.scad, part="check"), measured from the STL it writes.
In-range poses must come out empty, over a grid of MCP x PIP x DIP poses.
The stop poses go a few degrees past a limit and must NOT be empty: that
proves the stop is real. The neighbours (middle finger and thumb, as skin)
are checked against every printed part over a set of their own poses and
the index's. The tendon numbers come from the file's own path (part="path"),
so this script holds no geometry of its own.

    python3 check_gen_04.py           # prints a markdown report, exit 1 on FAIL
    python3 check_gen_04.py --quick   # fewer poses
"""
import concurrent.futures
import itertools
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'gen_04_index_print.scad'
SCAD = os.environ.get('OPENSCAD', '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD')

# The sampled range: every combination, plus a little hyperextension.
GRID = [list(p) for p in itertools.product([0, 45, 90], [0, 50, 98], [0, 35, 68])] + [[-3, -3, -3]]
QUICK = [[0, 0, 0], [45, 50, 35], [90, 98, 68], [90, 0, 0], [0, 98, 0], [0, 0, 68], [-3, -3, -3]]
PARTS = ['base', 'proximal', 'middle', 'distal', 'drum']
PAIRS = [(a, b) for i, a in enumerate(PARTS) for b in PARTS[i + 1:]] + [('finger', p) for p in PARTS]
# The line against every printed part with the guides left off (only a guide,
# the post or the drum may touch it), and against the finger.
CORD = [('cord', 'printed'), ('cord', 'finger')]
# [name, joint, sign, lo, hi, pair]: the first whole degree at which the pair touches.
STOPS = [
    ('MCP flexion', 0, 1, 90, 115, ('base', 'proximal')),
    ('PIP flexion', 1, 1, 98, 120, ('proximal', 'middle')),
    ('DIP flexion', 2, 1, 68, 90, ('middle', 'distal')),
    ('MCP hyperextension', 0, -1, 0, 15, ('base', 'proximal')),
    ('PIP hyperextension', 1, -1, 0, 15, ('proximal', 'middle')),
    ('DIP hyperextension', 2, -1, 0, 15, ('middle', 'distal')),
]
# The neighbours. The middle finger stays together with the index (splay 0)
# and moves on its own; the thumb sweeps its yaw. Skin, not comfort volume.
INDEX_POSES = [[0, 0, 0], [45, 50, 35], [90, 98, 68], [90, 0, 0], [0, 98, 68]]
MIDDLE_FLEX = [[0, 0, 0], [45, 50, 35], [90, 98, 68], [90, 0, 0], [0, 98, 68]]
THUMB_YAW = [22, 30, 35, 40, 45, 50, 60, 70, 80]
THUMB_INDEX = [[0, 0, 0], [90, 98, 68], [90, 0, 0]]
THUMB_RANGE = (35, 80)          # the documented wearable range: every yaw in it must be clear
THUMB_FLEXED = ([30, 30], 50)   # and a curled thumb inside it


def stl_volume(path):
    data = path.read_bytes()
    if len(data) < 84:
        return 0.0
    if data[:5] == b'solid' and b'facet' in data[:400]:
        nums = [list(map(float, m.split())) for m in re.findall(rb'vertex\s+([^\n]+)', data)]
        tris = [nums[i:i + 3] for i in range(0, len(nums), 3)]
    else:
        n = struct.unpack('<I', data[80:84])[0]
        tris = []
        for i in range(n):
            v = struct.unpack('<12f', data[84 + 50 * i: 84 + 50 * i + 48])
            tris.append([v[3:6], v[6:9], v[9:12]])
    vol = 0.0
    for a, b, c in tris:
        vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6
    return abs(vol)


def scad(args, suffix):
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / f'out.{suffix}'
        run = subprocess.run([SCAD, '--backend', 'Manifold', '-o', str(out), *args, str(SOURCE)],
                             capture_output=True, text=True)
        if suffix == 'echo':
            return out.read_text() if out.exists() else run.stderr
        return stl_volume(out) if out.exists() else 0.0


def overlap(pair, pose, guides=True, extra=()):
    args = ['-D', 'part="check"', '-D', f'pair={json.dumps(list(pair))}', '-D', f'bend={json.dumps(pose)}', *extra]
    if not guides:
        args += ['-D', 'guides=false']
    return scad(args, 'stl')


def stop_angle(joint, sign, lo, hi, pair):
    """Bisect to the first whole degree (between lo and hi) where the pair touches."""
    def touches(a):
        pose = [0, 0, 0]
        pose[joint] = sign * a
        return overlap(pair, pose) >= 0.05
    if touches(lo) or not touches(hi):
        return None
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if touches(mid) else (mid, hi)
    return hi


def path(pose):
    text = scad(['-D', 'part="path"', '-D', f'bend={json.dumps(pose)}'], 'echo')
    m = re.search(r'cord = (\[.*?\]\]), elastic = (\[.*?\]\])', text)
    a = re.search(r'axes = (\[.*?\]\])', text)
    return json.loads(m.group(1)), json.loads(m.group(2)), json.loads(a.group(1))


def length(points):
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def yz(p):
    return (p[1], p[2])


def lever(a, b, c):
    """Distance from axis point c to the line through a and b, in the y-z plane."""
    (ay, az), (by, bz), (cy, cz) = yz(a), yz(b), yz(c)
    dy, dz = by - ay, bz - az
    return abs((ay - cy) * dz - (az - cz) * dy) / math.hypot(dy, dz)


def wrapped(a, b, c, r):
    """Length from a to b in the y-z plane when a circle of radius r round c is in the
    way (the elastic lies on the knuckle): tangent, arc, tangent. Else the chord."""
    if lever(a, b, c) >= r:
        return math.dist(yz(a), yz(b)), False
    da, db = math.dist(yz(a), yz(c)), math.dist(yz(b), yz(c))
    if da <= r or db <= r:
        return math.dist(yz(a), yz(b)), True
    ta, tb = math.sqrt(da * da - r * r), math.sqrt(db * db - r * r)
    ang_a = math.atan2(a[2] - c[2], a[1] - c[1])
    ang_b = math.atan2(b[2] - c[2], b[1] - c[1])
    between = abs((ang_b - ang_a + math.pi) % (2 * math.pi) - math.pi)
    arc = between - math.acos(r / da) - math.acos(r / db)
    return ta + tb + r * max(0.0, arc), True


def scad_value(name):
    m = re.search(rf'^{name}\s*=\s*([^;]+);', SOURCE.read_text(), re.M)
    return json.loads(m.group(1))


def hand_value(name):
    m = re.search(rf'^{name}\s*=\s*([^;]+);', (HERE / 'jake_hand.scad').read_text(), re.M)
    return json.loads(m.group(1))


def tendon(poses):
    """Per pose: line wound in, the line's and the elastic's lever at each joint,
    the elastic's stretch (wrapped over the knuckles where it touches) and
    which knuckles it rests on."""
    t0, t1 = hand_value('hand_finger_base_t')[0], hand_value('hand_finger_tip_t')[0]
    skin = [(t0 + (t1 - t0) * k / 3) / 2 + scad_value('elastic_d') / 2 for k in range(3)]
    rows = {}
    for name, pose in poses.items():
        cord, elastic, axes = path(pose)
        finger = cord[7:]                    # post bottom, then the finger's guides
        # the run that crosses each joint: post->prox[0], prox[1]->mid[0], mid[1]->dist[0]
        cross = [(finger[0], finger[1]), (finger[2], finger[3]), (finger[4], finger[5])]
        cord_arm = [lever(a, b, axes[j]) for j, (a, b) in enumerate(cross)]
        e_cross = [(elastic[1], elastic[2]), (elastic[3], elastic[4]), (elastic[5], elastic[6])]
        e_arm = [lever(a, b, axes[j]) for j, (a, b) in enumerate(e_cross)]
        e_len = length(elastic[:2]) + math.dist(elastic[2], elastic[3]) + math.dist(elastic[4], elastic[5]) \
            + math.dist(elastic[6], elastic[7])
        touching = []
        for j, (a, b) in enumerate(e_cross):
            seg, touch = wrapped(a, b, axes[j], skin[j])
            e_len += seg
            if touch:
                touching.append(['MCP', 'PIP', 'DIP'][j])
        rows[name] = dict(pose=pose, cord=length(finger), cord_arm=cord_arm, e_len=e_len, e_arm=e_arm,
                          touching=touching)
    return rows


def main(argv):
    quick = '--quick' in argv
    poses = {str(p): p for p in (QUICK if quick else GRID)}
    jobs, stops, mid, thumb = {}, {}, {}, {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        for name, pose in poses.items():
            for pair in PAIRS:
                jobs[('range', name, pair)] = pool.submit(overlap, pair, pose)
            for pair in CORD:
                jobs[('cord', name, pair)] = pool.submit(overlap, pair, pose, False)
        stops = {name: pool.submit(stop_angle, *spec) for name, *spec in STOPS}
        for ip in INDEX_POSES:
            for mf in MIDDLE_FLEX:
                for body in ('printed', 'cord'):
                    mid[(str(ip), str(mf), body)] = pool.submit(
                        overlap, ('middle_finger', body), ip, True, ('-D', f'middle_flex={json.dumps(mf)}'))
        for ip in THUMB_INDEX:
            for yaw in THUMB_YAW:
                for body in ('printed', 'cord'):
                    thumb[(str(ip), yaw, body)] = pool.submit(
                        overlap, ('thumb', body), ip, True, ('-D', f'thumb_yaw={yaw}'))
        flexed = {str(ip): pool.submit(overlap, ('thumb', 'printed'), ip, True,
                                       ('-D', f'thumb_yaw={THUMB_FLEXED[1]}', '-D', f'thumb_flex={json.dumps(THUMB_FLEXED[0])}'))
                  for ip in THUMB_INDEX}
        named = {'straight': [0, 0, 0], 'half curl': [45, 50, 35], 'full curl': [90, 98, 68],
                 'MCP only': [90, 0, 0], 'PIP only': [0, 98, 0], 'DIP only': [0, 0, 68],
                 'at the stops': [95, 101, 70]}
        tendon_job = pool.submit(tendon, named)
        results = {k: f.result() for k, f in jobs.items()}
        stops = {k: f.result() for k, f in stops.items()}
        mid = {k: f.result() for k, f in mid.items()}
        thumb = {k: f.result() for k, f in thumb.items()}
        flexed = {k: f.result() for k, f in flexed.items()}

    ok = True
    print(f'## Interference over {len(poses)} poses (mm³ of overlap; must be 0)\n')
    print('Poses are [MCP, PIP, DIP]: every combination of MCP 0/45/90, PIP 0/50/98 and DIP 0/35/68, '
          'plus 3° of hyperextension at all three. The cord columns leave the guides off, so only the '
          'post and the drum may touch it.\n' if not quick else '')
    cols = PAIRS + CORD
    print('| Pose | ' + ' | '.join(f'{a} × {b}' for a, b in cols) + ' |')
    print('|---|' + '---|' * len(cols))
    for name in poses:
        cells = []
        for pair in cols:
            v = results[('cord' if pair in CORD else 'range', name, pair)]
            ok &= v < 0.05
            cells.append('0' if v < 0.05 else f'**{v:.1f}**')
        print(f'| {name} | ' + ' | '.join(cells) + ' |')

    print('\n## Stops: the first degree where the parts touch\n')
    print('| Stop | Pair | Touches at |')
    print('|---|---|---|')
    for name, joint, sign, lo, hi, pair in STOPS:
        angle = stops[name]
        ok &= angle is not None
        print(f'| {name} | {pair[0]} × {pair[1]} | {f"{angle}°" if angle is not None else "**no stop in range**"} |')

    print('\n## Middle finger (skin, fingers together: splay 0), mm³\n')
    print('Rows: the index pose. Columns: the middle finger\'s own pose. Each cell is printed parts / line.\n')
    print('| Index \\ middle | ' + ' | '.join(str(m) for m in MIDDLE_FLEX) + ' |')
    print('|---|' + '---|' * len(MIDDLE_FLEX))
    for ip in INDEX_POSES:
        cells = []
        for mf in MIDDLE_FLEX:
            a, b = mid[(str(ip), str(mf), 'printed')], mid[(str(ip), str(mf), 'cord')]
            ok &= a < 0.05 and b < 0.05
            cells.append(f'{a:.0f} / {b:.0f}' if a >= 0.05 or b >= 0.05 else '0')
        print(f'| {ip} | ' + ' | '.join(cells) + ' |')

    print('\n## Thumb (skin), mm³ against printed parts / line, by thumb yaw\n')
    print(f'The documented wearable range is thumb yaw {THUMB_RANGE[0]} to {THUMB_RANGE[1]}° '
          '(0 = along the index, the fingers-together photo is 22, the spread photo about 70). '
          'Every cell in it must be 0.\n')
    print('| Index pose | ' + ' | '.join(f'{y}°' for y in THUMB_YAW) + ' |')
    print('|---|' + '---|' * len(THUMB_YAW))
    for ip in THUMB_INDEX:
        cells = []
        for yaw in THUMB_YAW:
            a, b = thumb[(str(ip), yaw, 'printed')], thumb[(str(ip), yaw, 'cord')]
            if THUMB_RANGE[0] <= yaw <= THUMB_RANGE[1]:
                ok &= a < 0.05 and b < 0.05
            cells.append(f'{a:.0f} / {b:.0f}' if a >= 0.05 or b >= 0.05 else '0')
        print(f'| {ip} | ' + ' | '.join(cells) + ' |')
    for ip, v in flexed.items():
        ok &= v < 0.05
        print(f'\nThumb curled {THUMB_FLEXED[0]} at yaw {THUMB_FLEXED[1]}, index {ip}: {v:.0f} mm³', end='')
    print()

    rows = tendon_job.result()
    drum_r = scad_value('drum_r') + scad_value('cord_d') / 2
    base = rows['straight']
    cut = base['e_len'] / 1.15
    print('\n## Line and elastic\n')
    print(f'Line on the drum at r = {drum_r:g} mm. The lock has {scad_value("lock_n")} holes, '
          f'{360 / scad_value("lock_n"):.0f}° = {math.radians(360 / scad_value("lock_n")) * drum_r:.1f} mm of line a step. '
          f'Elastic: free run {base["e_len"]:.0f} mm at straight. Cut it to {cut:.0f} mm between knots '
          '(15 % pre-stretch) and the strain is:\n')
    print('| Pose | Line wound in, mm | Drum turn | Line lever MCP / PIP / DIP, mm | Elastic lever MCP / PIP / DIP, mm '
          '| Elastic stretch, mm | Elastic strain | Elastic lies on |')
    print('|---|---|---|---|---|---|---|---|')
    for name, r in rows.items():
        wound = base['cord'] - r['cord']
        print(f'| {name} {r["pose"]} | {wound:.1f} | {math.degrees(wound / drum_r):.0f}° | '
              + ' / '.join(f'{x:.1f}' for x in r['cord_arm']) + ' | '
              + ' / '.join(f'{x:.1f}' for x in r['e_arm']) + f' | {r["e_len"] - base["e_len"]:.1f} | '
              f'{r["e_len"] / cut - 1:.0%} | {", ".join(r["touching"]) or "nothing"} |')
    full = base['cord'] - rows['at the stops']['cord']
    ok &= math.degrees(full / drum_r) < 360
    print(f'\nAll three stops reached: {full:.1f} mm of line, {math.degrees(full / drum_r):.0f}° of the drum '
          '(must be under one turn so the line stays in one layer).')
    print(f'\n{"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
