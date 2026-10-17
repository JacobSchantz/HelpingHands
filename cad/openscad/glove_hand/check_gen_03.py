#!/usr/bin/env python3
"""check_gen_03.py: interference and tendon numbers for the gen_03 index finger.

Every check is one OpenSCAD intersection of two bodies at one pose
(gen_03_index_finger.scad, part="check"), measured from the STL it writes.
In-range poses must come out empty. The stop poses go a few degrees past a
limit and must NOT be empty: that proves the stop is real. The tendon numbers
(excursion, lever arm, elastic stretch) come from the file's own path
(part="path"), so this script holds no geometry of its own.

    python3 check_gen_03.py           # prints a markdown report
    python3 check_gen_03.py --quick   # straight and full curl only
"""
import concurrent.futures
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
SOURCE = HERE / 'gen_03_index_finger.scad'
SCAD = os.environ.get('OPENSCAD', '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD')

IN_RANGE = {
    'straight': [0, 0, 0],
    'half curl': [45, 55, 35],
    'full curl': [90, 98, 68],
    'MCP only': [90, 0, 0],
    'PIP only': [0, 98, 0],
    'DIP only': [0, 0, 68],
}
PARTS = ['base', 'proximal', 'middle', 'distal']
PAIRS = [(a, b) for i, a in enumerate(PARTS) for b in PARTS[i + 1:]] + [('finger', p) for p in PARTS + ['spool']]
# The line against every printed part with the guides left off (only a guide
# may touch it), and against the finger.
CORD = [('cord', 'printed'), ('cord', 'finger')]
# Where each stop really is: the first whole degree at which the pair touches,
# searched between the limit's lower and upper bound. [name, joint, sign, lo, hi, pair]
STOPS = [
    ('PIP flexion', 1, 1, 95, 115, ('proximal', 'middle')),
    ('DIP flexion', 2, 1, 65, 90, ('middle', 'distal')),
    ('PIP hyperextension', 1, -1, 0, 15, ('proximal', 'middle')),
    ('DIP hyperextension', 2, -1, 0, 15, ('middle', 'distal')),
    ('MCP hyperextension', 0, -1, 0, 15, ('base', 'proximal')),
]
# The neighbours in the photo pose, then spread until they clear: [variable, values].
NEIGHBOURS = [('middle_finger', 'middle_splay', [0, -4, -8, -12, -16, -20]),
              ('thumb', 'thumb_yaw', [22, 30, 40, 50, 60, 70])]


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
    cord, elastic = json.loads(m.group(1)), json.loads(m.group(2))
    return cord, elastic


def length(points):
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def tendon_table(poses):
    rows = []
    base = None
    for name, pose in poses.items():
        cord, elastic = path(pose)
        if base is None:
            base = (length(cord), length(elastic))
        rows.append((name, pose, base[0] - length(cord), length(elastic) - base[1]))
    return rows


def main(argv):
    poses = {k: IN_RANGE[k] for k in ('straight', 'full curl')} if '--quick' in argv else IN_RANGE
    jobs = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        for name, pose in poses.items():
            for pair in PAIRS:
                jobs[('range', name, pair)] = pool.submit(overlap, pair, pose)
            for pair in CORD:
                jobs[('cord', name, pair)] = pool.submit(overlap, pair, pose, False)
        stops = {name: pool.submit(stop_angle, *spec) for name, *spec in STOPS}
        clear = {(body, v): pool.submit(overlap, (body, 'printed'), [0, 0, 0], True, ('-D', f'{var}={v}'))
                 for body, var, values in NEIGHBOURS for v in values}
        tendon = pool.submit(tendon_table, {'straight': [0, 0, 0], **{k: v for k, v in IN_RANGE.items() if k != 'straight'}})
        results = {k: f.result() for k, f in jobs.items()}
        stops = {k: f.result() for k, f in stops.items()}
        clear = {k: f.result() for k, f in clear.items()}

    ok = True
    print('## Interference (mm³ of overlap; in range must be 0)\n')
    print('| Pose | ' + ' | '.join(f'{a} × {b}' for a, b in PAIRS + CORD) + ' |')
    print('|---|' + '---|' * len(PAIRS + CORD))
    for name in poses:
        cells = []
        for pair in PAIRS + CORD:
            v = results[('cord' if pair in CORD else 'range', name, pair)]
            ok &= v < 0.05
            cells.append('0' if v < 0.05 else f'**{v:.1f}**')
        print(f'| {name} {poses[name]} | ' + ' | '.join(cells) + ' |')
    print('\n## Stops: the first degree where the parts touch\n')
    print('| Stop | Pair | Touches at |')
    print('|---|---|---|')
    for name, joint, sign, lo, hi, pair in STOPS:
        angle = stops[name]
        ok &= angle is not None
        print(f'| {name} | {pair[0]} × {pair[1]} | {f"{angle} deg" if angle is not None else "**no stop in range**"} |')
    print('\n## Neighbours (straight finger; information)\n')
    for body, var, values in NEIGHBOURS:
        cells = ', '.join(f'{v}: {clear[(body, v)]:.0f}' for v in values)
        print(f'- {body} × printed parts, mm³ at {var} = {cells}')
    print('\n## Tendon\n')
    print('| Pose | Line wound in, mm | Spool turn (r = 9), deg | Elastic stretch, mm |')
    print('|---|---|---|---|')
    for name, pose, wound, stretch in tendon.result():
        print(f'| {name} {pose} | {wound:.1f} | {math.degrees(wound / 9):.0f} | {stretch:.1f} |')
    print(f'\n{"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
