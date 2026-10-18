#!/usr/bin/env python3
"""How each gripper generation closes, measured on the meshes the gallery shows.

Uses the hinges in cad/mobile_gallery/poses.js (the same ones the gallery's
Open/Closed slider uses) and the published catalog (~/HelpingHands-tools/
design-gallery, written by Scripts/publish_designs.py). For each design it
swings the jaws shut from fully open until the fingers first touch, then slices
the pair every millimetre along the finger length and reports the gap between
the inner faces. "Good closure" (Jake, voice-b7ae5fc0): the points meet first
and most of the rest of the length touches too.

    check_gripper_closure.py            table for every gripper design
    check_gripper_closure.py --json     the same as JSON
"""
import argparse
import json
import math
from pathlib import Path
import re

import numpy as np

REPO = Path(__file__).resolve().parents[1]
POSES = REPO / 'cad/mobile_gallery/poses.js'
GALLERY = Path.home() / 'HelpingHands-tools/design-gallery'
FINGER = re.compile(r'finger|jaw|tip|thumb|fin-ray|root|contact pad', re.I)
NOT_FINGER = re.compile(r'strap|carrier|adapter|sensor|guide', re.I)
TOUCH_MM = 1.5   # a gap this small or less counts as touching
SKIP_MM = 15     # ignore the pivot/gear region at the root of the fingers


def poses():
    text = POSES.read_text()
    return json.loads(text[text.index('{'):text.rindex('}') + 1])


def stl(path):
    raw = path.read_bytes()
    count = int.from_bytes(raw[80:84], 'little')
    if len(raw) == 84 + 50 * count:
        rows = np.frombuffer(raw, dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]), count=count, offset=84)
        return rows['v'].reshape(-1, 3, 3).astype(float)
    points = [list(map(float, line.split()[1:4])) for line in raw.decode().splitlines() if line.strip().startswith('vertex')]
    return np.array(points, dtype=float).reshape(-1, 3, 3)


def swing(tris, pivot, degrees):
    d = math.radians(degrees)
    out = tris.copy()
    x, z = tris[..., 0] - pivot[0], tris[..., 2] - pivot[2]
    out[..., 0] = pivot[0] + x * math.cos(d) + z * math.sin(d)
    out[..., 2] = pivot[2] - x * math.sin(d) + z * math.cos(d)
    return out


def extent(tris, levels, inner):
    """Per Z level, the innermost X of the cross-section: min for the right jaw, max for the left."""
    best = np.full(len(levels), np.nan)
    for a, b in ((0, 1), (1, 2), (2, 0)):
        p, q = tris[:, a], tris[:, b]
        lo, hi = np.minimum(p[:, 2], q[:, 2]), np.maximum(p[:, 2], q[:, 2])
        for i, z in enumerate(levels):
            hit = (lo <= z) & (hi >= z) & (hi > lo)
            if not hit.any():
                continue
            t = (z - p[hit, 2]) / (q[hit, 2] - p[hit, 2])
            xs = p[hit, 0] + t * (q[hit, 0] - p[hit, 0])
            value = xs.min() if inner == 'min' else xs.max()
            best[i] = value if np.isnan(best[i]) else (min(best[i], value) if inner == 'min' else max(best[i], value))
    return best


def gaps(right, left, rpivot, lpivot, angle, exported):
    r = swing(right, rpivot, angle - exported)
    l = swing(left, lpivot, -(angle - exported))
    top = min(r[..., 2].max(), l[..., 2].max())
    base = max(rpivot[2], lpivot[2]) + SKIP_MM
    levels = np.arange(base, top, 1.0)
    return levels, extent(r, levels, 'min') - extent(l, levels, 'max')


def measure(design_id, pose, catalog):
    design = next((d for d in catalog['designs'] if d['id'] == design_id), None)
    if not design or not design.get('models'):
        return dict(id=design_id, error='not in the published catalog')
    hinges = pose['hinges']
    results = []
    for right_h, left_h in zip(hinges[0::2], hinges[1::2]):
        def jaw(h):
            picked = [m for m in design['models'] if re.search(h['match'], m['name'])
                      and FINGER.search(m['name']) and not NOT_FINGER.search(m['name'])]
            return np.concatenate([stl(GALLERY / m['path']) for m in picked]), [m['name'] for m in picked]
        (right, rnames), (left, lnames) = jaw(right_h), jaw(left_h)
        rp, lp = right_h['pivot'], left_h['pivot']
        def touches(angle):
            return np.nanmin(gaps(right, left, rp, lp, angle, pose['exported'])[1]) <= 0
        # Close from fully open in 1° steps, then back off in 0.25° steps to the first touch.
        closed = None
        angle = pose['max']
        while angle >= pose['min'] - 1e-9:
            if touches(angle):
                closed = angle
                while closed + 0.25 <= pose['max'] and touches(closed + 0.25):
                    closed += 0.25
                break
            angle -= 1
        at = closed if closed is not None else pose['min']
        levels, gap = gaps(right, left, rp, lp, at, pose['exported'])
        valid = ~np.isnan(gap)
        levels, gap = levels[valid], gap[valid]
        first = float(levels[int(np.argmin(gap))])
        length = float(levels[-1] - levels[0]) if len(levels) > 1 else 0
        tip = float(np.min(gap[levels >= levels[-1] - 8]))
        touching = float(np.mean(gap <= TOUCH_MM))
        results.append(dict(
            jaws=rnames + lnames, closes_at_deg=closed, measured_at_deg=at,
            tip_gap_mm=round(max(tip, 0), 1), first_contact_mm_from_tip=round(float(levels[-1]) - first, 1),
            touching_fraction=round(touching, 2), max_gap_mm=round(float(gap.max()), 1), finger_length_mm=round(length),
            profile=[[round(float(z), 0), round(float(g), 1)] for z, g in zip(levels[::5], gap[::5])],
            verdict=('PASS' if tip <= TOUCH_MM and touching >= 0.6 else 'FAIL')))
    return dict(id=design_id, name=design['name'], pairs=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    catalog = json.loads((GALLERY / 'catalog.json').read_text())
    report = [measure(k, v, catalog) for k, v in poses().items() if not k.startswith('_') and not v.get('single_finger')]
    if args.json:
        print(json.dumps(report, indent=1))
        return
    for row in report:
        if 'error' in row:
            print(f"{row['id']}: {row['error']}")
            continue
        for pair in row['pairs']:
            closes = 'never touches' if pair['closes_at_deg'] is None else f"touches at {pair['closes_at_deg']}°"
            print(f"{pair['verdict']}  {row['name']:<6} {row['id']:<44} {closes:<16} tip gap {pair['tip_gap_mm']} mm, "
                  f"first contact {pair['first_contact_mm_from_tip']} mm from tip, "
                  f"{pair['touching_fraction']:.0%} of {pair['finger_length_mm']} mm touching, widest gap {pair['max_gap_mm']} mm")


if __name__ == '__main__':
    main()
